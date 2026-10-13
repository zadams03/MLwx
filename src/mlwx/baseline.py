"""The baseline: one LightGBM model per airport, cycle hour and lead (DECISIONS D88.4, SPEC 9.3).

SPEC 8's recipe B+D,L,R,T with section 8's settings and column order, unchanged. Ported from
scripts/session97_stagec_cv.py (fit_predict) and scripts/session62_reserved_confirm.py
(LGB_PARAMS, G14: `lgb.LGBMRegressor(**LGB_PARAMS).fit(x, y)`, no other fit arguments), the
reference, never edited. The target is the residual obs - temp (G20); the forecast is temp
plus the model's output.

Product models (D103.5) are fitted once on every complete-case row valid up to 2026-07-31
and then frozen: v1 does no retraining. They are saved outside the repo as one file per
airport and cycle hour (46 models, leads 3 to 48), with a manifest of (file, SHA-256) and one
SHA-256 over the manifest. That SHA-256 is held here as MANIFEST_SHA256 (D98.2), checked by a
test, and cited by every log row (D103.5, D103.8).
"""

import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np

from . import features

# D21.4 / D48.6: locked LightGBM settings, identical to every modelling script in the project
# (scripts/session62_reserved_confirm.py l.131-146). Never tuned per set or fold.
LGB_PARAMS = dict(
    objective="regression_l1",
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=15,
    min_child_samples=40,
    subsample=1.0,
    colsample_bytree=1.0,
    reg_alpha=0.0,
    reg_lambda=0.0,
    random_state=42,
    n_jobs=1,
    deterministic=True,
    force_row_wise=True,
    verbose=-1,
)

# The SHA-256 over the product models' manifest (D103.5, D98.2). Session 109's 12 airports (F152):
# 16485f384c81094247ec745550ad04982e8c3adb255147546bf1190f498641ef. Session 110's combined set of 49
# airports (D104.9, F153), in ../MLwx-live-build/models-49/:
MANIFEST_SHA256 = "484590bf6c877bb153446dc87f57c0f00270ad689066ea1791a60cea71baeea4"

MANIFEST_NAME = "manifest.txt"


def fit(train):
    """train: list of (x, temp, obs) in ascending time. Returns the fitted model."""
    x = np.array([r[0] for r in train], dtype=float)
    y = np.array([r[2] - r[1] for r in train], dtype=float)
    m = lgb.LGBMRegressor(**LGB_PARAMS)
    m.fit(x, y)
    return m


def predict(model, rows):
    """rows: list of (x, temp, ...). Returns temp plus the model's output for each."""
    pred = model.predict(np.array([r[0] for r in rows], dtype=float))
    return [r[1] + float(pred[i]) for i, r in enumerate(rows)]


def fit_predict(train, test):
    """As scripts/session97_stagec_cv.py fit_predict. train, test: lists of (x, temp, obs)."""
    return predict(fit(train), test)


# ------------------------------------------------------------------ the product model files

def pack_name(model_name, icao, cycle_hour):
    return f"{model_name}_{icao}_{cycle_hour:02d}z.json.gz"


def pack_bytes(icao, cycle_hour, models):
    """models: {lead: fitted LGBMRegressor}. Equal models give equal bytes: sorted keys, a zero
    gzip timestamp, no file name."""
    body = {"airport": icao, "cycle_hour": cycle_hour, "features": features.G15,
            "models": {str(n): m.booster_.model_to_string() for n, m in sorted(models.items())}}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return gzip.compress(raw, compresslevel=9, mtime=0)


def manifest_text(entries):
    """entries: {file name: sha256}. One line per file, sorted by name: 'sha256  file'."""
    return "".join(f"{sha}  {name}\n" for name, sha in sorted(entries.items()))


def manifest_sha256(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


class ModelSet:
    """The frozen product models of one weather model, loaded from a folder after checking it
    against its manifest (and the manifest against MANIFEST_SHA256 when that is set)."""

    def __init__(self, folder, model_name="gfs", expected_manifest_sha=None):
        self.folder = Path(folder)
        self.model_name = model_name
        text = (self.folder / MANIFEST_NAME).read_text()
        self.manifest_sha = manifest_sha256(text)
        want = expected_manifest_sha if expected_manifest_sha is not None else MANIFEST_SHA256
        if want is not None and self.manifest_sha != want:
            raise ValueError(f"the models' manifest SHA-256 {self.manifest_sha} is not the recorded {want}")
        self.entries = {}
        for line in text.splitlines():
            sha, name = line.split("  ", 1)
            self.entries[name] = sha
        self._boosters = {}

    def _pack(self, icao, cycle_hour):
        key = (icao, cycle_hour)
        if key not in self._boosters:
            name = pack_name(self.model_name, icao, cycle_hour)
            if name not in self.entries:
                raise KeyError(f"no models for {icao} {cycle_hour:02d}z in the manifest")
            data = (self.folder / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != self.entries[name]:
                raise ValueError(f"{name}: SHA-256 differs from the manifest")
            body = json.loads(gzip.decompress(data).decode("ascii"))
            if body["features"] != features.G15 or body["airport"] != icao or body["cycle_hour"] != cycle_hour:
                raise ValueError(f"{name}: not the expected airport, cycle hour or feature list")
            self._boosters[key] = {int(n): lgb.Booster(model_str=s) for n, s in body["models"].items()}
        return self._boosters[key]

    def baseline(self, icao, cycle_hour, lead, x, temp):
        """The baseline forecast: temp plus the model's output for the nine inputs x."""
        b = self._pack(icao, cycle_hour)[lead]
        return temp + float(b.predict(np.array([x], dtype=float))[0])

    def check_all(self):
        """SHA-256 of every file against the manifest. Returns the number of files."""
        for name, sha in self.entries.items():
            if hashlib.sha256((self.folder / name).read_bytes()).hexdigest() != sha:
                raise ValueError(f"{name}: SHA-256 differs from the manifest")
        return len(self.entries)


def training_rows(table_files):
    """The complete-case rows of one airport, by (cycle hour, lead), each in ascending cycle time:
    {(h, n): [(cycle, x, temp, obs)]}. table_files: [(path, station, leads)]."""
    cells = {}
    for path, station, leads in table_files:
        from .tables import read_table_rows
        for cycle, valid, h, n, complete, obs, temp, x in read_table_rows(path, station, leads):
            if complete:
                cells.setdefault((h, n), []).append((cycle, x, temp, obs))
    for rows in cells.values():
        rows.sort(key=lambda r: r[0])
    return cells


LAST_TRAIN_VALID = dt.datetime(2026, 7, 31, 23, 0)     # D103.5: every complete-case row valid up to 2026-07-31
