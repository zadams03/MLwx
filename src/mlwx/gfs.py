"""The GFS adapter: byte-range fetch and the message guard (DECISIONS D82.4, D103.7, D103.10).

Ported from scripts/session91_grib_pull.py (find_range, parse_idx, selector,
expected_steps, check_message), which is the reference and is never edited.
For one cycle it reads each needed GRIB2 message from the public bucket by
byte range, checks it, and keeps only the raw value at each airport's four
grid points. No global field is kept.

The guard (D103.10). Before any value is used, every message's identity keys
(discipline, category, number, surface type, level), step type and step
range, run date and time, full validity date and hour, grid type and grid
geometry are checked against the model's field map, and the four values at
every airport must be finite. Any mismatch, missing field or missing value
raises GuardStop: the cycle issues nothing (D103.7). A network problem, a
short or broken body or a file not there yet raises FetchError: the cycle
issues nothing now, and the runner may try again (runner.py).

Not ported: session 94's whole-file fallback (D86.2), which recovered 27 archived files
whose .idx files were wrong. A live cycle with a bad .idx simply issues nothing.
"""

import datetime as dt
import math
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import eccodes as ec

RETRIES = 5                 # retries after the first try (as the pull)
USER_AGENT = "MLwx-live/1.0"
STEP_WORD = {"avg": "ave", "max": "max", "min": "min"}
GEOM_KEYS = (("Ni", "Ni"), ("Nj", "Nj"), ("lat_first", "latitudeOfFirstGridPointInDegrees"),
             ("lon_first", "longitudeOfFirstGridPointInDegrees"), ("lat_last", "latitudeOfLastGridPointInDegrees"),
             ("lon_last", "longitudeOfLastGridPointInDegrees"), ("di", "iDirectionIncrementInDegrees"),
             ("dj", "jDirectionIncrementInDegrees"))

_ec_lock = threading.Lock()


class GuardStop(Exception):
    """A message or the grid failed the guard, or a field is missing. The cycle issues nothing."""


class FetchError(Exception):
    """A network, HTTP or body problem. The cycle issues nothing now; it may be tried again."""


# ------------------------------------------------------------------ the request plan

def window_start(fh):
    """The 6-hour reset mark before a forecast hour, for averages, maxima and minima
    (session91_grib_pull.py window_start)."""
    return 6 * ((fh - 1) // 6)


def selector(kind, fh):
    """The .idx step text of a field at a forecast hour. None means absent by design:
    GFS gives no average, maximum or minimum at f000."""
    if kind == "instant":
        return "anl" if fh == 0 else f"{fh} hour fcst"
    if fh == 0:
        return None
    return f"{window_start(fh)}-{fh} hour {STEP_WORD[kind]} fcst"


def expected_steps(kind, fh):
    """(stepType, startStep, endStep) the decoded message must carry."""
    if kind == "instant":
        return ("instant", fh, fh)
    return (kind, window_start(fh), fh)


def parse_idx(text):
    rows = []
    for line in text.strip().splitlines():
        p = line.split(":")
        rows.append({"offset": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5], "line": line})
    return rows


def find_range(rows, var, level, step, cycle):
    """Exactly one .idx line, with the run stamp checked. Returns (byte range, expected
    length or None, the line). Raises GuardStop if the line is not there once."""
    hits = [i for i, r in enumerate(rows) if r["var"] == var and r["level"] == level and r["step"] == step]
    if len(hits) != 1:
        raise GuardStop(f"expected 1 idx line for {var}:{level}:{step}, found {len(hits)}")
    i = hits[0]
    if rows[i]["d"] != f"d={cycle:%Y%m%d%H}":
        raise GuardStop(f"idx run stamp {rows[i]['d']} does not match the run")
    start = rows[i]["offset"]
    if i + 1 < len(rows):
        return f"{start}-{rows[i + 1]['offset'] - 1}", rows[i + 1]["offset"] - start, rows[i]["line"]
    return f"{start}-", None, rows[i]["line"]


# ------------------------------------------------------------------ the guard

def msg_geometry(gid):
    return {k: (ec.codes_get_long(gid, key) if k in ("Ni", "Nj") else ec.codes_get_double(gid, key))
            for k, key in GEOM_KEYS}


def check_message(gid, field, fh, cycle, airports, geom):
    """The per-message guard (session 91's check_message). Returns the 4 values per
    airport, read by grid index, in airport order. Raises GuardStop on any mismatch."""
    try:
        valid = cycle + dt.timedelta(hours=fh)
        steps = expected_steps(field.kind, fh)
        got = (tuple(ec.codes_get_long(gid, k) for k in ("discipline", "parameterCategory", "parameterNumber",
                                                         "typeOfFirstFixedSurface", "level"))
               + (ec.codes_get_string(gid, "stepType"), ec.codes_get_long(gid, "startStep"),
                  ec.codes_get_long(gid, "endStep")))
        if got != tuple(field.ident) + steps:
            raise GuardStop(f"{field.name} f{fh:03d}: identity {got} != expected {tuple(field.ident) + steps}")
        if (ec.codes_get_long(gid, "dataDate") != int(f"{cycle:%Y%m%d}")
                or ec.codes_get_long(gid, "dataTime") != cycle.hour * 100):
            raise GuardStop(f"{field.name} f{fh:03d}: run date or time mismatch")
        vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
        if vd != int(f"{valid:%Y%m%d}") or vt != valid.hour * 100:
            raise GuardStop(f"{field.name} f{fh:03d}: validity {vd} {vt:04d} != expected {valid:%Y%m%d %H%M}")
        g = msg_geometry(gid)
        if g != geom or ec.codes_get_string(gid, "gridType") != "regular_ll":
            raise GuardStop(f"{field.name} f{fh:03d}: grid {g} differs from the config's {geom}")
        values = ec.codes_get_values(gid)
        missing = ec.codes_get_double(gid, "missingValue")
        bitmap = ec.codes_get_long(gid, "bitmapPresent")
        out = []
        for a in airports:
            for i in a.indices:
                v = float(values[i])
                if not math.isfinite(v) or (bitmap and v == missing):
                    raise GuardStop(f"{field.name} f{fh:03d}: missing or non-finite value at grid index {i} ({a.icao})")
                out.append(v)
        return out
    except GuardStop:
        raise
    except Exception as e:  # noqa: BLE001  (an eccodes error on a message is a guard failure)
        raise GuardStop(f"{field.name} f{fh:03d}: the message could not be read: {e!r}") from e


# ------------------------------------------------------------------ HTTP

class Http:
    """Standard-library HTTP with the pull's retry policy: network errors, 429, 5xx, a
    short body and a broken GRIB body are retried with a growing wait; a 404 is a
    FetchError at once (a file that is not there yet). Anything else is a FetchError."""

    def __init__(self, sleep=time.sleep, timeout=120, retries=RETRIES):
        self.sleep = sleep
        self.timeout = timeout
        self.retries = retries
        self.requests = 0
        self.bytes = 0
        self._lock = threading.Lock()

    def get(self, url, kind="idx", byte_range=None, expected_len=None):
        headers = {"User-Agent": USER_AGENT}
        if byte_range:
            headers["Range"] = f"bytes={byte_range}"
        last = None
        for attempt in range(self.retries + 1):
            if attempt:
                self.sleep(2.0 * 2 ** (attempt - 1))
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    status = r.status
                    body = r.read()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise FetchError(f"{url}: HTTP 404") from e
                if e.code == 429 or 500 <= e.code <= 599:
                    last = f"HTTP {e.code}"
                    continue
                raise FetchError(f"{url} {byte_range or ''}: HTTP {e.code}") from e
            except (urllib.error.URLError, OSError, ValueError) as e:
                last = f"network error {e!r}"
                continue
            except Exception as e:  # noqa: BLE001  (for example http.client.IncompleteRead)
                last = f"read error {e!r}"
                continue
            if status != (206 if byte_range else 200):
                raise FetchError(f"{url} {byte_range or ''}: HTTP {status}")
            if expected_len is not None and len(body) != expected_len:
                last = f"short body {len(body)} of {expected_len} bytes"
                continue
            if kind == "message" and (body[:4] != b"GRIB" or body[-4:] != b"7777"):
                last = "broken body (no GRIB or 7777 marker)"
                continue
            with self._lock:
                self.requests += 1
                self.bytes += len(body)
            return body
        raise FetchError(f"{url} {byte_range or ''}: failed after {self.retries} retries: {last}")


# ------------------------------------------------------------------ one file, one cycle

def fetch_file(http, model, airports, cycle, fh):
    """One GRIB file: its .idx, then each live field's message, checked, and the 4 values
    per airport. Returns ({(fh, field): values}, {(fh, field): status})."""
    url = model.file_url(cycle, fh)
    try:
        rows = parse_idx(http.get(url + ".idx", "idx").decode("ascii"))
    except (ValueError, IndexError, UnicodeDecodeError) as e:
        raise GuardStop(f"unreadable idx for f{fh:03d}: {e!r}") from e
    values, status = {}, {}
    for f in model.live_fields():
        step = selector(f.kind, fh)
        if step is None:
            status[(fh, f.name)] = "absent by design"
            continue
        rng, exp, _ = find_range(rows, f.var, f.level, step, cycle)
        data = http.get(url, "message", rng, exp)
        with _ec_lock:
            try:
                gid = ec.codes_new_from_message(data)
            except Exception as e:  # noqa: BLE001
                raise GuardStop(f"{f.name} f{fh:03d}: the message could not be opened: {e!r}") from e
            try:
                values[(fh, f.name)] = check_message(gid, f, fh, cycle, airports, model.grid)
            finally:
                ec.codes_release(gid)
        status[(fh, f.name)] = "ok"
    return values, status


class CycleValues:
    """The raw values of one cycle: values[(fh, field)] is a list of 4 floats per airport,
    in airport order; status[(fh, field)] is "ok" or "absent by design"."""

    def __init__(self, cycle, airports, values, status):
        self.cycle = cycle
        self.icaos = [a.icao for a in airports]
        self.values = values
        self.status = status

    def point_values(self, icao, fh, field):
        k = self.icaos.index(icao)
        return self.values[(fh, field)][4 * k:4 * k + 4]

    def airport_view(self, icao):
        """({(fh, field): value}, status) for one airport, ready for the features module
        (the bilinear step needs the airport; see features.airport_values)."""
        k = self.icaos.index(icao)
        return {key: v[4 * k:4 * k + 4] for key, v in self.values.items()}


def fetch_cycle(model, airports, cycle, http=None, workers=8, hours=None):
    """Every file of one cycle, forecast hours 0 to the model's last lead. Raises GuardStop or
    FetchError; on either, nothing is returned (the cycle issues nothing)."""
    http = http or Http()
    hours = list(hours if hours is not None else range(model.first_lead, model.last_lead + 1))
    values, status = {}, {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fetch_file, http, model, airports, cycle, fh) for fh in hours]
        errors = []
        for fut in futs:
            try:
                v, s = fut.result()
                values.update(v)
                status.update(s)
            except (GuardStop, FetchError) as e:
                errors.append(e)
        if errors:
            # a guard failure outranks a fetch error: it will not go away by trying again
            guard = [e for e in errors if isinstance(e, GuardStop)]
            raise (guard or errors)[0]
    return CycleValues(cycle, airports, values, status)
