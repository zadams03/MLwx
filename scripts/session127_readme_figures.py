"""Session 127: the figures for README.md and RESULTS.md (DECISIONS D121.5).

Offline. Python standard library only. It reads committed result files only,
checks each input's SHA-256 before reading it, draws recorded values and
recorded margins, averages nothing across airports, and writes new files only:
it refuses to overwrite a figure that exists. Nothing is fitted, scored or
fetched, and nothing is run from other scripts.

Figures (written into the folder given to --draw):
  stagec_gain.svg         (a) how much lower the corrected forecast's error is
                          than raw GFS, per cent, at each of the six new
                          airports, both held-out years, hourly curve and
                          daily maximum. Input: the raw GFS half of
                          session 107's verdicts file. Gate: each value at 2
                          decimals equals F150.2; KORD, second look, at 3
                          decimals equals SPEC 9.5.
  how_it_works.svg        (b) a diagram with no numbers.
  lock_then_look.svg      (c) how each claim was tested: rules written down,
                          one look, the verdict; with dates held as constants
                          (checked against the record entries by
                          tests/test_session127_figures.py).
  compare_hourly.svg      (d) the curve against each other forecast, hourly.
  compare_dailymax.svg    (e) the same, daily maximum. Inputs: the files under
                          data/processed/session114_comparisons/ and
                          data/processed/session112_analysis/ from which
                          ANALYSIS.md's Tables 2a and 2b are rendered. Gate:
                          every plotted pair, rounded as in the tables, equals
                          the table's cell.

Modes (one per run):
  --gate             check every input and every gate; print PASS or FAIL per
                     figure; write nothing.
  --draw OUTDIR      run the gate, then write the five figures into OUTDIR
                     (created if needed). Refuses if any figure exists.

Run: .venv/bin/python -B scripts/session127_readme_figures.py --gate
No em-dashes in any text here (D76.6).
"""

import csv
import hashlib
import html
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# ---------------------------------------------------------------- inputs (SHA-256 held as constants, D98.2)

INPUTS = {
    # F150.4
    "data/processed/session107_claim_verdicts.csv":
        "0a9c1dc80a1e052c5b98a117b6c42cbd9811c160a944be959dca0e4575e319da",
    # session 112's analyse_meta.txt records the first two
    "data/processed/session112_analysis/hourly_headline.csv":
        "db080daad9aa71bdec82e569d7360530f99de4680cee58ae8b9d39bd7814dfe2",
    "data/processed/session112_analysis/dailymax_headline.csv":
        "da9ee0c200bed601758900c07a9a2c5e6507c9e4845f74a175fe9a279e7f9c63",
    "data/processed/session112_analysis/hourly_curve_skill.csv":
        "222a7e89bc60727362b2272a2450db0561dbe37d518364d8b705fa46f5a53ab5",
    "data/processed/session112_analysis/dailymax_curve_skill.csv":
        "2c23a87a633bd4431629ca66a45fc53bf3c2dd00922026ac4a6b5b9282a5cae6",
    "data/processed/session114_comparisons/hourly_aifs.csv":
        "ca659a814e1499f269662b1d238657c8d50a05614b7c705bee9d4e176e935b2f",
    "data/processed/session114_comparisons/hourly_aifs_skill.csv":
        "3019549cb16ca7e0ab64d06069752c915874cc04b5c5d904349fb217312021c4",
    "data/processed/session114_comparisons/hourly_aifs_dm.csv":
        "b459e613f3017602c8ca39ddecb763e0adac92db3846b848693bbebc8a4c4d40",
    "data/processed/session114_comparisons/hourly_ifs.csv":
        "a499e177661cec8911da291cdc5432e128a5b254ab4c5730c6ecd9e3f4f71b47",
    "data/processed/session114_comparisons/hourly_ifs_skill.csv":
        "49cb62a943a64b4dd92b99f8ce073a33795e9eee806b7500322b6c3c3dd7c906",
    "data/processed/session114_comparisons/hourly_ifs_dm.csv":
        "e45d2e796d5846f79b3a19da2edff0f1fc08c9a51e5297972aeec9d220f1df5a",
    "data/processed/session114_comparisons/hourly_nbm.csv":
        "cb984a00e4f65c0dfd86314089310669694e2921f2ff845aa624edbc229cb85a",
    "data/processed/session114_comparisons/hourly_nbm_skill.csv":
        "bffe494e499cabdb62ba92a3c05178ebb830b631cdae8f576b04cc67989d279e",
    "data/processed/session114_comparisons/hourly_nbm_dm.csv":
        "8f5df210ecbb211086edca3da7b93e9ec6ea643ef6ea45955e2a66c475003c78",
    "data/processed/session114_comparisons/hourly_nbs.csv":
        "d86bf0d4d4414fdcf6f1a2bae9ba62e48193323bb662cce0c64a18c806e7fafd",
    "data/processed/session114_comparisons/hourly_nbs_skill.csv":
        "32f4f176251034159355a018a1aa7ed2e837dbbde6239ee6e60349a68aa8c178",
    "data/processed/session114_comparisons/hourly_nbs_dm.csv":
        "9a552baa83babee35fe4bd8db935c7c050014295aa4627e7fc29186e411551e8",
    "data/processed/session114_comparisons/hourly_mav.csv":
        "a0263639a9ebc0e5d61deb15a7881cc6ecda0a36eb78c746f55b219fd642a18e",
    "data/processed/session114_comparisons/hourly_mav_skill.csv":
        "af319b7d058f7e796f99e6b5d75c21a9ee98d43a00d51909c4b3e342a5875906",
    "data/processed/session114_comparisons/hourly_mav_dm.csv":
        "4fa638b0db741b5584868091b6aa30922afddeeb3e37990e74bdfc8c759c40f6",
    "data/processed/session114_comparisons/dailymax_aifs.csv":
        "96ddc753e0d873e763daf48526d452439e4bfa830fc42707da801a8f100ae761",
    "data/processed/session114_comparisons/dailymax_aifs_skill.csv":
        "14bd518bcd43c04afecd112c61b29506a43ded1b525b630e4210493f38a39f09",
    "data/processed/session114_comparisons/dailymax_aifs_dm.csv":
        "b5efa509171527bd758586cbfcdc064158ca4e7f78aa17589294c025f754feb8",
    "data/processed/session114_comparisons/dailymax_ifs.csv":
        "e10964942c5ecbb3f5ea5edd96cab4f55c35f5afdf7a6f4d47232119482ce06a",
    "data/processed/session114_comparisons/dailymax_ifs_skill.csv":
        "be6e3d3a947cd0252811ca7f35d89db643dea0bff56182053eb44ad7f82bcb1f",
    "data/processed/session114_comparisons/dailymax_ifs_dm.csv":
        "64e9f04af2a9ba440827db0e7b7f58353095b2b688dd5fe4202e2604fce124df",
    "data/processed/session114_comparisons/dailymax_nbm.csv":
        "8b0498e22af665dbcf3569c187d1eca515b9b2e7089bb0d4f6c88a70c07f441d",
    "data/processed/session114_comparisons/dailymax_nbm_skill.csv":
        "058547986cb536707eafef42bd314811f341467cdd623943aa917f1ea88bb372",
    "data/processed/session114_comparisons/dailymax_nbm_dm.csv":
        "cc4503a6264685a14fbeb04b61d521ae3a5d5ef23c2d2c0f44c03934ab7d7201",
    "data/processed/session114_comparisons/dailymax_nbs.csv":
        "ff77d31a78018a7f5ad6bf2a28ba71906329976267e484e7588331744da16eda",
    "data/processed/session114_comparisons/dailymax_nbs_skill.csv":
        "eaaa53c75fe29821788d585f3ab5332e46bcef9bfe50c2c91e6b0bd064bd2286",
    "data/processed/session114_comparisons/dailymax_nbs_dm.csv":
        "d185bb4d481a568612d6589813cce148ebfdc295dbb3f12d11566b88377224ce",
    "data/processed/session114_comparisons/dailymax_mav.csv":
        "a9bd5ba3c4bbfefd8b94b3590e5add69dac61bceb80252d519eeaef09d5f1a1d",
    "data/processed/session114_comparisons/dailymax_mav_skill.csv":
        "5532552c60437ee17c251e2a251e5f5911e5664fd61a74712de214ad3fcd1f99",
    "data/processed/session114_comparisons/dailymax_mav_dm.csv":
        "a9c58df58ca1b912440e8f09153c31784662c341b67e010fb75423c1779ba559",
}

VERDICTS = "data/processed/session107_claim_verdicts.csv"
S112 = "data/processed/session112_analysis/"
S114 = "data/processed/session114_comparisons/"

# ---------------------------------------------------------------- recorded values used only to check what is read

CLAIM = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]    # order of F150.2 and ANALYSIS.md Table 2a
DEV = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO"]      # order of ANALYSIS.md Table 2a
NAMES = {
    "EDDM": "Munich", "KORD": "Chicago O'Hare", "CYYZ": "Toronto Pearson", "ZGSZ": "Shenzhen",
    "ZUCK": "Chongqing", "NZWN": "Wellington", "EGLC": "London City", "LFPG": "Paris CDG",
    "KDSM": "Des Moines", "YSDU": "Dubbo", "KRNO": "Reno", "KSFO": "San Francisco",
}

# F150.2: margin over raw GFS in per cent at 2 decimals (look A, look B).
F150_2_RAW = {
    "hourly": {
        "EDDM": ("24.83", "26.96"), "KORD": ("14.39", "8.22"), "CYYZ": ("22.04", "23.48"),
        "ZGSZ": ("21.63", "23.09"), "ZUCK": ("23.91", "27.07"), "NZWN": ("31.71", "32.99"),
    },
    "daily": {
        "EDDM": ("29.14", "31.44"), "KORD": ("9.32", "2.59"), "CYYZ": ("23.19", "21.22"),
        "ZGSZ": ("40.31", "39.63"), "ZUCK": ("14.84", "14.14"), "NZWN": ("55.74", "57.21"),
    },
}
# SPEC 9.5: the smallest margin, KORD, look B, per cent at 3 decimals.
SPEC_9_5_SMALLEST = {"hourly": "8.216", "daily": "2.589"}

# ANALYSIS.md Table 2a and Table 2b, row by row: curve, raw GFS, linear MOS, AIFS, NBM grid, NBS, MAV, ECMWF IFS.
TABLE_2A = {
    "EDDM": ('1.33', '1.79', '1.43', '1.21 / 1.28', '-', '-', '-', '1.42 / 1.33 *'),
    "KORD": ('1.19', '1.34', '1.22', '1.12 / 1.26 *', '1.05 / 1.16 *', '1.06 / 1.21 *', '1.36 / 1.21 *', '1.39 / 1.18 *'),
    "CYYZ": ('1.14', '1.47', '1.20', '1.17 / 1.18', '1.05 / 1.12 *', '1.07 / 1.15 *', '-', '1.35 / 1.14 *'),
    "ZGSZ": ('0.90', '1.16', '0.94', '0.96 / 0.89', '-', '-', '-', '1.31 / 0.89 *'),
    "ZUCK": ('1.09', '1.46', '1.17', '1.06 / 1.10', '-', '-', '-', '1.32 / 1.10 *'),
    "NZWN": ('0.79', '1.16', '0.83', '1.06 / 0.79 *', '-', '-', '-', '0.94 / 0.78 *'),
    "EGLC": ('0.84', '1.04', '0.85', '1.13 / 0.87 *', '-', '-', '-', '1.17 / 0.83 *'),
    "LFPG": ('0.95', '1.23', '1.00', '1.11 / 0.95 *', '-', '-', '-', '1.28 / 0.96 *'),
    "KDSM": ('1.30', '1.88', '1.43', '1.08 / 1.35 *', '1.21 / 1.27 *', '1.16 / 1.32 *', '1.45 / 1.32 *', '1.50 / 1.30 *'),
    "YSDU": ('1.23', '1.52', '1.32', '1.12 / 1.19 *', '-', '-', '-', '1.34 / 1.24 *'),
    "KRNO": ('1.21', '2.22', '1.41', '1.60 / 1.10 *', '1.44 / 1.19 *', '1.17 / 1.22 *', '1.16 / 1.23 *', '2.20 / 1.21 *'),
    "KSFO": ('1.00', '1.29', '1.14', '0.94 / 0.96', '1.40 / 0.99 *', '0.92 / 1.01 *', '1.06 / 1.01 *', '1.30 / 1.00 *'),
}
TABLE_2B = {
    "EDDM": ('1.25', '1.79', '1.37', '1.21 / 1.12', '-', '-', '-', '1.42 / 1.25 *'),
    "KORD": ('1.09', '1.16', '1.10', '1.43 / 1.12 *', '1.14 / 1.09', '1.12 / 1.09', '1.47 / 1.09 *', '1.38 / 1.09 *'),
    "CYYZ": ('1.04', '1.34', '1.13', '1.39 / 1.08 *', '1.21 / 1.04 *', '1.16 / 1.04', '-', '1.46 / 1.04 *'),
    "ZGSZ": ('0.91', '1.52', '1.07', '1.23 / 0.92 *', '-', '-', '-', '1.65 / 0.91 *'),
    "ZUCK": ('1.17', '1.37', '1.30', '1.32 / 1.20', '-', '-', '-', '1.50 / 1.17 *'),
    "NZWN": ('0.74', '1.70', '0.83', '1.80 / 0.72 *', '-', '-', '-', '1.48 / 0.74 *'),
    "EGLC": ('0.84', '0.95', '0.89', '0.98 / 0.91', '-', '-', '-', '1.04 / 0.84 *'),
    "LFPG": ('0.96', '1.20', '1.05', '1.45 / 0.91 *', '-', '-', '-', '1.23 / 0.96 *'),
    "KDSM": ('1.22', '1.73', '1.46', '1.43 / 1.24 *', '1.30 / 1.22', '1.23 / 1.22', '1.57 / 1.22 *', '1.41 / 1.22 *'),
    "YSDU": ('1.03', '1.09', '1.11', '1.48 / 0.97 *', '-', '-', '-', '1.61 / 1.03 *'),
    "KRNO": ('0.95', '1.55', '0.99', '1.40 / 0.82 *', '0.93 / 0.95', '0.97 / 0.95', '1.12 / 0.95 *', '2.44 / 0.95 *'),
    "KSFO": ('1.21', '1.66', '1.39', '1.45 / 1.17 *', '1.87 / 1.21 *', '1.19 / 1.21', '1.41 / 1.21 *', '1.57 / 1.21 *'),
}
TABLES = {"hourly": TABLE_2A, "dailymax": TABLE_2B}
TABLE_COL = {"aifs": 3, "nbm": 4, "nbs": 5, "mav": 6, "ifs": 7}   # index into a table row
TABLE_COL_CURVE, TABLE_COL_RAW = 0, 1

# Dates drawn in lock_then_look.svg. Each is checked against the record entry that gives it
# by tests/test_session127_figures.py (a script never searches DECISIONS text, D98.2).
DATES = {
    "train_before": "2024-08-01",     # D100.3(c): trained on rows valid before 2024-08-01T00:00 UTC
    "look_a": ("2024-08-01", "2025-07-31"),   # D100.4: cycles 2024-08-01T00 to 2025-07-31T18
    "look_b": ("2025-08-01", "2026-07-31"),   # D100.4: cycles 2025-08-01T00 to 2026-07-31T18
    "claim_rules": "2026-10-11",      # D100's section heading
    "claim_look": "2026-10-11",       # F150.4: run 2026-10-11
    "live_first_cycle": "2026-10-12", # D105.5(d): the 12 airports start at 2026-10-12 12z
    "live_rules": "2026-10-14",       # D105's section heading
    "live_end": "2027-07-31",         # D105.5(e): to 2027-07-31 18z
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def plain_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


# ---------------------------------------------------------------- alt text (one sentence each, for README)

ALT = {
    "stagec_gain.svg": "Bar chart: at each of six new airports, in both held-out years, how many per cent lower the "
                       "corrected forecast's error is than raw GFS, for the hourly curve and for the daily maximum, "
                       "with the smallest margin (Chicago O'Hare, second year) marked.",
    "how_it_works.svg": "Diagram of five steps: the GFS forecast for the airport, the features read from it, one model "
                        "per airport, run time and forecast hour, the running correction for drifting bias, and the "
                        "corrected hourly curve with the day's maximum read off it.",
    "lock_then_look.svg": "Two timelines, one for the six-airport claim and one for the live forward test, each going "
                          "from rules written down, to one look at years the model never saw, to a verdict, with the "
                          "dates; the claim passed and the live test is not yet scored.",
    "compare_hourly.svg": "Dot plot: at each airport where the other forecast exists, by how many per cent the "
                          "curve's hourly error is lower or higher than raw GFS, AIFS, ECMWF IFS, the NBM grid, NBS "
                          "and MAV, with 95% ranges.",
    "compare_dailymax.svg": "Dot plot: at each airport where the other forecast exists, by how many per cent the "
                            "curve's daily-maximum error is lower or higher than raw GFS, AIFS, ECMWF IFS, the NBM "
                            "grid, NBS and MAV, with 95% ranges.",
}
FIGURES = list(ALT)

# ---------------------------------------------------------------- style: one look for every figure

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK = "#1a1a1a"
MUTED = "#4d4d4d"
GRID = "#d9d9d9"
BAND = "#f3f4f6"
PAPER = "#ffffff"
BLUE = "#0072B2"       # Okabe-Ito blue: the curve is better
SKY = "#8fc3e6"
VERMILION = "#D55E00"  # Okabe-Ito vermillion: the other forecast is better; also the "smallest" mark
WIDTH = 800


def n(x):
    return f"{x:.2f}"


def esc(s):
    return html.escape(s, quote=False)


def svg_open(width, height, title, desc, extra_defs=""):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" font-family="{FONT}">',
        f'<title id="title">{esc(title)}</title>',
        f'<desc id="desc">{esc(desc)}</desc>',
        f'<defs>{extra_defs}</defs>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{PAPER}"/>',
    ]


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal"):
    return (f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}" font-weight="{weight}">{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke=GRID, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def finish(parts):
    parts.append("</svg>")
    s = "\n".join(parts) + "\n"
    if chr(0x2014) in s:
        raise SystemExit("STOP: em-dash in figure text")
    return s


# ---------------------------------------------------------------- reading inputs

def read_checked(rel):
    if rel not in INPUTS:
        raise SystemExit(f"STOP: {rel} is not a declared input")
    data = (ROOT / rel).read_bytes()
    found = hashlib.sha256(data).hexdigest()
    if found != INPUTS[rel]:
        raise SystemExit(f"STOP: {rel} SHA-256 {found}, expected {INPUTS[rel]}")
    return data.decode("utf-8")


def read_table(rel):
    return list(csv.DictReader(io.StringIO(read_checked(rel))))


def only(rows, **kw):
    hit = [r for r in rows if all(r[k] == v for k, v in kw.items())]
    if len(hit) != 1:
        raise SystemExit(f"STOP: expected one row for {kw}, found {len(hit)}")
    return hit[0]


# ---------------------------------------------------------------- figure (a): the gain over raw GFS

def load_gain():
    """{(output, icao, look): margin_pct} from the raw GFS half; gated against F150.2 and SPEC 9.5."""
    rows = read_table(VERDICTS)
    out = {}
    for r in rows:
        if r["half"] != "raw_gfs":
            continue
        out[(r["output"], r["icao"], r["look"])] = float(r["margin_pct"])
    if len(out) != 24:
        raise SystemExit(f"STOP: expected 24 raw GFS halves, found {len(out)}")
    for output, per in F150_2_RAW.items():
        for ic, (a, b) in per.items():
            for look, want in (("A", a), ("B", b)):
                got = f"{out[(output, ic, look)]:.2f}"
                if got != want:
                    raise SystemExit(f"STOP: {output} {ic} look {look}: {got} differs from F150.2 {want}")
    for output, want in SPEC_9_5_SMALLEST.items():
        got = f"{out[(output, 'KORD', 'B')]:.3f}"
        if got != want:
            raise SystemExit(f"STOP: {output} KORD look B: {got} differs from SPEC 9.5 {want}")
        smallest = min(out[(output, ic, lk)] for ic in CLAIM for lk in "AB")
        if smallest != out[(output, "KORD", "B")]:
            raise SystemExit(f"STOP: the smallest {output} margin is not KORD, look B")
    # the claim as counted from the file: PASS in both looks, both halves, per airport and output
    passes = {}
    for r in rows:
        passes.setdefault((r["output"], r["icao"]), []).append(r["verdict"] == "PASS" and r["look_pass"] == "true")
    claim = {o: sum(all(passes[(o, ic)]) for ic in CLAIM) for o in ("hourly", "daily")}
    if claim != {"hourly": 6, "daily": 6}:
        raise SystemExit(f"STOP: claim count {claim}, expected 6 and 6")
    return out


def fig_gain(v):
    left, right = 175, 70
    xmax = 60.0
    scale = (WIDTH - left - right) / xmax
    bar_h, pitch = 13, 40
    top_panel = (132, 462)
    height = 800
    desc_parts = []
    for output, label in (("hourly", "hourly curve"), ("daily", "daily maximum")):
        desc_parts.append(label + ": " + "; ".join(
            f"{ic} {v[(output, ic, 'A')]:.2f} and {v[(output, ic, 'B')]:.2f}" for ic in CLAIM))
    desc = ("Per cent by which the corrected forecast's mean absolute error is lower than raw GFS, first value "
            "2024-25 and second value 2025-26. " + ". ".join(desc_parts) + ".")
    defs = (f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="6" height="6" fill="{SKY}"/><line x1="0" y1="0" x2="0" y2="6" stroke="{BLUE}" '
            f'stroke-width="2.4"/></pattern>')
    out = svg_open(WIDTH, height, "How much lower the error is than raw GFS", desc, defs)
    out.append(text(20, 30, "How much lower the corrected forecast's error is than raw GFS", size=17, weight="bold"))
    out.append(text(20, 52, "Six new airports, two held-out years. A longer bar is a bigger improvement.", size=12,
                    fill=MUTED))
    # legend
    out.append(f'<rect x="20" y="66" width="16" height="12" fill="{BLUE}"/>')
    out.append(text(42, 76, "first year (2024-25)", size=12))
    out.append(f'<rect x="200" y="66" width="16" height="12" fill="url(#hatch)" stroke="{BLUE}" stroke-width="1"/>')
    out.append(text(222, 76, "second year (2025-26)", size=12))
    out.append(f'<rect x="400" y="64" width="22" height="16" fill="none" stroke="{VERMILION}" stroke-width="2" '
               f'stroke-dasharray="4 2"/>')
    out.append(text(430, 76, "smallest margin in the panel", size=12))
    out.append(text(20, 98, "Error means mean absolute error: the average size of the miss in degrees. "
                    "Per cent lower = 100 x (1 - corrected error / raw GFS error).", size=11, fill=MUTED))
    for (output, title), top in zip((("hourly", "Hourly curve, 3 to 48 hours ahead"),
                                     ("daily", "Daily maximum temperature")), top_panel):
        out.append(text(20, top - 8, title, size=14, weight="bold"))
        ph = pitch * len(CLAIM)
        for tick in range(0, 61, 10):
            x = left + tick * scale
            out.append(line(x, top, x, top + ph))
            out.append(text(x, top + ph + 16, f"{tick}", size=11, anchor="middle", fill=MUTED))
        out.append(line(left, top, left, top + ph, stroke=INK, width=1))
        out.append(text(left + (WIDTH - left - right) / 2, top + ph + 34, "per cent lower than raw GFS",
                        size=11, anchor="middle", fill=MUTED))
        smallest = min(v[(output, ic, lk)] for ic in CLAIM for lk in "AB")
        for i, ic in enumerate(CLAIM):
            y0 = top + i * pitch + 5
            out.append(text(left - 10, y0 + bar_h + 5, f"{NAMES[ic]} ({ic})", size=12, anchor="end"))
            for j, look in enumerate("AB"):
                val = v[(output, ic, look)]
                y = y0 + j * (bar_h + 3)
                w = val * scale
                fill = BLUE if look == "A" else "url(#hatch)"
                out.append(f'<rect x="{n(left)}" y="{n(y)}" width="{n(w)}" height="{bar_h}" fill="{fill}" '
                           f'stroke="{BLUE}" stroke-width="1"/>')
                is_small = val == smallest
                if is_small:
                    out.append(f'<rect x="{n(left - 3)}" y="{n(y - 3)}" width="{n(w + 6)}" height="{bar_h + 6}" '
                               f'fill="none" stroke="{VERMILION}" stroke-width="2" stroke-dasharray="4 2"/>')
                label = f"{val:.1f}" + ("  smallest" if is_small else "")
                out.append(text(left + w + 8 if not is_small else left + w + 10, y + bar_h - 2, label, size=11.5,
                                weight="bold" if is_small else "normal"))
    out.append(text(20, 776, "Hourly: every hour from 3 to 48 hours ahead. Daily maximum: the day's highest value "
                    "on the curve. All data is GFS version 16.", size=11, fill=MUTED))
    out.append(text(20, 792, "Against persistence (repeating the latest observed value for that hour of "
                    "the day) the margins were larger in every case.", size=11, fill=MUTED))
    return finish(out)


# ---------------------------------------------------------------- figure (b): how it works (no numbers drawn as results)

def fig_how():
    height = 640
    out = svg_open(WIDTH, height, "How the corrected forecast is made", ALT["how_it_works.svg"])
    out.append(text(20, 30, "How a corrected forecast is made", size=17, weight="bold"))
    out.append(text(20, 52, "The same five steps run at every airport, for every GFS forecast.", size=12, fill=MUTED))
    steps = [
        ("GFS forecast for the airport",
         ["GFS is the US national weather model. Four times a day we take its forecast",
          "for the spot where the airport is."]),
        ("Features read from that forecast",
         ["Temperature, cloud, wind, moisture, how fast the air cools with height,",
          "sunshine and pressure change, and the time of year."]),
        ("One model per airport, run time and forecast hour",
         ["Each model has learned, from past forecasts and what was then observed,",
          "how GFS is usually wrong at that airport. It predicts that error."]),
        ("A running correction for drifting bias",
         ["A running average of the model's recent misses is added, so the forecast",
          "follows slow shifts in GFS's bias. It uses only misses already observed."]),
        ("The corrected hourly curve",
         ["A corrected temperature for every hour from 3 to 48 hours ahead.",
          "Each day's highest value on the curve is the daily maximum."]),
    ]
    x0, bw, bh, gap, y = 20, 760, 84, 28, 74
    for i, (head, body) in enumerate(steps):
        last = i == len(steps) - 1
        fill = "#e8f1f8" if last else BAND
        out.append(f'<rect x="{x0}" y="{n(y)}" width="{bw}" height="{bh}" rx="8" fill="{fill}" '
                   f'stroke="{BLUE if last else MUTED}" stroke-width="{2 if last else 1}"/>')
        out.append(f'<circle cx="{x0 + 34}" cy="{n(y + bh / 2)}" r="16" fill="{BLUE}"/>')
        out.append(text(x0 + 34, y + bh / 2 + 5, str(i + 1), size=15, anchor="middle", fill="#ffffff", weight="bold"))
        out.append(text(x0 + 68, y + 30, head, size=15, weight="bold"))
        for k, ln in enumerate(body):
            out.append(text(x0 + 68, y + 52 + k * 18, ln, size=12.5, fill=INK))
        if not last:
            ax = x0 + 34
            out.append(line(ax, y + bh + 2, ax, y + bh + gap - 8, stroke=MUTED, width=2))
            out.append(f'<polygon points="{ax - 6},{n(y + bh + gap - 10)} {ax + 6},{n(y + bh + gap - 10)} '
                       f'{ax},{n(y + bh + gap - 2)}" fill="{MUTED}"/>')
        y += bh + gap
    out.append(text(20, height - 14, "The models are trained once on past years and then frozen; only the running "
                    "correction in step 4 keeps updating.", size=11, fill=MUTED))
    return finish(out)


# ---------------------------------------------------------------- figure (c): rules, one look, verdict

def fig_lock(v):
    height = 472
    small = {o: min(v[(o, ic, lk)] for ic in CLAIM for lk in "AB") for o in ("hourly", "daily")}
    d = DATES
    out = svg_open(WIDTH, height, "How each claim was tested", ALT["lock_then_look.svg"])
    out.append(text(20, 30, "How each claim was tested", size=17, weight="bold"))
    out.append(text(20, 52, "Rules first, then one look at years the model never saw, then the verdict.", size=12,
                    fill=MUTED))
    lanes = [
        ("The six-airport claim (finished)", 84, [
            ("1. Rules written down", plain_date(d["claim_rules"]),
             ["Method, settings and pass rule", "fixed in writing. Models trained", "only on data before "
              + plain_date(d["train_before"]) + ",", "then frozen."], False),
            ("2. One look at unseen years", "run once on " + plain_date(d["claim_look"]),
             ["Year 1: " + plain_date(d["look_a"][0]) + " to " + plain_date(d["look_a"][1]),
              "Year 2: " + plain_date(d["look_b"][0]) + " to " + plain_date(d["look_b"][1]),
              "The models had never seen them."], False),
            ("3. The verdict", "passed",
             ["Passed at 6 of 6 airports, hourly", "and daily maximum, in both years.",
              f"Smallest margins: +{small['hourly']:.1f}% hourly,", f"+{small['daily']:.1f}% daily (Chicago, year 2)."], True),
        ]),
        ("The live forward test, 49 airports (running)", 270, [
            ("1. Rules written down", plain_date(d["live_rules"]),
             ["Test fixed in writing before any", "forecast is scored. Forecasts have", "been logged since "
              + plain_date(d["live_first_cycle"]) + ",", "each written once, never edited."], False),
            ("2. One look per period, later", "after each period ends",
             ["The test covers forecasts up to", plain_date(d["live_end"]) + ". Each period is", "scored once, only after it",
              "has ended."], False),
            ("3. The verdict", "not yet scored",
             ["No accuracy figure is shown for", "the live tool until this look", "has been run."], False),
        ]),
    ]
    bw, bh, gap = 236, 150, 26
    for title, top, boxes in lanes:
        out.append(text(20, top, title, size=14, weight="bold"))
        for i, (head, date, body, done) in enumerate(boxes):
            x = 20 + i * (bw + gap)
            y = top + 12
            out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{BAND}" '
                       f'stroke="{BLUE if done else MUTED}" stroke-width="{2 if done else 1}"'
                       f'{"" if done or i < 2 else " stroke-dasharray=" + chr(34) + "6 4" + chr(34)}/>')
            out.append(text(x + 14, y + 26, head, size=13.5, weight="bold"))
            out.append(text(x + 14, y + 46, date, size=12.5, fill=BLUE if done else INK, weight="bold"))
            for k, ln in enumerate(body):
                out.append(text(x + 14, y + 70 + k * 17, ln, size=12))
            if i < 2:
                ax = x + bw + 2
                out.append(line(ax, y + bh / 2, ax + gap - 10, y + bh / 2, stroke=MUTED, width=2))
                out.append(f'<polygon points="{ax + gap - 11},{n(y + bh / 2 - 6)} {ax + gap - 11},{n(y + bh / 2 + 6)} '
                           f'{ax + gap - 3},{n(y + bh / 2)}" fill="{MUTED}"/>')
    out.append(text(20, height - 14, "Time runs left to right. Dates are those in the project's public, "
                    "timestamped record.", size=11, fill=MUTED))
    return finish(out)


# ---------------------------------------------------------------- figures (d) and (e): the curve against other forecasts

SOURCES = [
    ("raw", "Raw GFS", "the model itself"),
    ("aifs", "AIFS", "ECMWF AI model"),
    ("ifs", "ECMWF IFS", "ECMWF main model"),
    ("nbm", "NBM grid", "US blend, grid"),
    ("nbs", "NBS", "US blend, station"),
    ("mav", "MAV", "GFS station guidance"),
]


def load_comparison(out):
    """{source: {icao: dict(comp, curve, skill, lo, hi, reject)}} for output 'hourly' or 'dailymax'.
    Gate: every plotted pair, rounded as in ANALYSIS.md's table, equals the table's cell."""
    table = TABLES[out]
    data = {}
    head = read_table(f"{S112}{out}_headline.csv")
    rskill = read_table(f"{S112}{out}_curve_skill.csv")
    raw = {}
    for ic in CLAIM + DEV:
        c = float(only(head, icao=ic, period="all", forecast="curve")["mae"])
        r = float(only(head, icao=ic, period="all", forecast="raw_gfs")["mae"])
        s = only(rskill, icao=ic, period="all", reference="raw_gfs")
        if f"{c:.2f}" != table[ic][TABLE_COL_CURVE] or f"{r:.2f}" != table[ic][TABLE_COL_RAW]:
            raise SystemExit(f"STOP: {out} {ic} raw GFS pair {c:.2f}, {r:.2f} differs from the table "
                             f"{table[ic][TABLE_COL_CURVE]}, {table[ic][TABLE_COL_RAW]}")
        skill = float(s["skill"])
        if abs(skill - (1 - c / r)) > 1e-9:
            raise SystemExit(f"STOP: {out} {ic} raw GFS skill is not 1 - curve / raw")
        raw[ic] = dict(comp=r, curve=c, skill=skill, lo=float(s["lo"]), hi=float(s["hi"]), reject=None)
    data["raw"] = raw
    for src in ("aifs", "ifs", "nbm", "nbs", "mav"):
        h = read_table(f"{S114}{out}_{src}.csv")
        sk = read_table(f"{S114}{out}_{src}_skill.csv")
        dm = read_table(f"{S114}{out}_{src}_dm.csv")
        have = {r["icao"] for r in h}
        want = {ic for ic in CLAIM + DEV if table[ic][TABLE_COL[src]] != "-"}
        if have != want:
            raise SystemExit(f"STOP: {out} {src}: airports in the file {sorted(have)} differ from the table "
                             f"{sorted(want)}")
        per = {}
        for ic in sorted(have):
            comp = float(only(h, icao=ic, test_year="all", forecast="comp")["mae"])
            curve = float(only(h, icao=ic, test_year="all", forecast="curve")["mae"])
            reject = only(dm, icao=ic)["bh_reject_q005"] == "True"
            cell = f"{comp:.2f} / {curve:.2f}" + (" *" if reject else "")
            if cell != table[ic][TABLE_COL[src]]:
                raise SystemExit(f"STOP: {out} {src} {ic}: cell '{cell}' differs from the table "
                                 f"'{table[ic][TABLE_COL[src]]}'")
            s = only(sk, icao=ic, test_year="all", a="curve", b="comp")
            skill = float(s["skill_a_vs_b"])
            if abs(skill - (1 - curve / comp)) > 1e-9:
                raise SystemExit(f"STOP: {out} {src} {ic}: skill is not 1 - curve / competitor")
            per[ic] = dict(comp=comp, curve=curve, skill=skill, lo=float(s["lo"]), hi=float(s["hi"]), reject=reject)
        data[src] = per
    return data


def pc(x):
    return f"{100 * x:+.1f}"


def fig_compare(out_name, data, title, subtitle, notes, tick_values, lo_axis, hi_axis, desc_head):
    col0, colw = 156, 105
    ncol = len(SOURCES)
    row_h = 30
    header_top = 140
    rows_top = header_top + 52
    claim_y = rows_top
    dev_y = claim_y + 22 + row_h * 6 + 14
    axis_y = dev_y + 22 + row_h * 6 + 6
    height = axis_y + 38 + 18 * len(notes) + 16
    desc_items = []
    for key, name, _ in SOURCES:
        desc_items.append(name + ": " + ", ".join(f"{ic} {pc(d['skill'])}" for ic, d in data[key].items()))
    desc = desc_head + " " + "; ".join(desc_items) + "."
    out = svg_open(WIDTH, height, title, desc)
    out.append(text(20, 30, title, size=17, weight="bold"))
    for k, ln in enumerate(subtitle):
        out.append(text(20, 52 + k * 17, ln, size=12, fill=MUTED))
    # legend (two rows)
    ly = 96
    out.append(f'<circle cx="28" cy="{ly - 4}" r="4.5" fill="{BLUE}" stroke="{BLUE}" stroke-width="1.5"/>')
    out.append(text(40, ly, "filled dot: a formal test finds a real difference", size=11.5))
    out.append(f'<circle cx="400" cy="{ly - 4}" r="4.5" fill="{PAPER}" stroke="{BLUE}" stroke-width="1.5"/>')
    out.append(text(412, ly, "hollow dot: not clearly different", size=11.5))
    ly2 = ly + 20
    out.append(f'<polygon points="28,{ly2 - 9} 34,{ly2 - 4} 28,{ly2 + 1} 22,{ly2 - 4}" fill="{BLUE}"/>')
    out.append(text(40, ly2, "diamond: raw GFS, no formal test was run on it", size=11.5))
    out.append(line(388, ly2 - 4, 412, ly2 - 4, stroke=MUTED, width=2))
    out.append(text(418, ly2, "bar: the 95% range", size=11.5))
    xs = lambda i, val: col0 + i * colw + 8 + (val - lo_axis) / (hi_axis - lo_axis) * (colw - 16)

    # column headings
    for i, (key, name, sub) in enumerate(SOURCES):
        cx = col0 + i * colw + colw / 2
        out.append(text(cx, header_top, name, size=13, anchor="middle", weight="bold"))
        out.append(text(cx, header_top + 15, sub, size=11, anchor="middle", fill=MUTED))
        out.append(text(xs(i, 0) - 4, header_top + 32, "other", size=11, anchor="end", fill=VERMILION, weight="bold"))
        out.append(text(xs(i, 0) + 4, header_top + 32, "curve", size=11, anchor="start", fill=BLUE, weight="bold"))

    groups = [("New airports (never used to choose settings)", CLAIM, claim_y),
              ("Development airports (used to choose settings, so their figures flatter the curve a little)", DEV, dev_y)]
    for gname, ics, gy in groups:
        out.append(f'<rect x="10" y="{gy - 6}" width="{WIDTH - 20}" height="20" fill="{BAND}"/>')
        out.append(text(20, gy + 9, gname, size=12, weight="bold"))
        for r_i, ic in enumerate(ics):
            cy = gy + 22 + r_i * row_h + 14
            out.append(text(col0 - 10, cy + 4, f"{NAMES[ic]} ({ic})", size=12, anchor="end"))
            for i, (key, name, _) in enumerate(SOURCES):
                d = data[key].get(ic)
                if d is None:
                    out.append(text(xs(i, 0), cy + 4, "n/a", size=11, anchor="middle", fill=MUTED))
                    continue
                out.append(line(xs(i, 0), cy - 12, xs(i, 0), cy + 12, stroke=GRID, width=1))
                colour = BLUE if d["skill"] > 0 else VERMILION
                x1, x2, xm = xs(i, 100 * d["lo"]), xs(i, 100 * d["hi"]), xs(i, 100 * d["skill"])
                out.append(line(x1, cy - 3, x2, cy - 3, stroke=colour, width=2))
                out.append(line(x1, cy - 7, x1, cy + 1, stroke=colour, width=1.5))
                out.append(line(x2, cy - 7, x2, cy + 1, stroke=colour, width=1.5))
                if key == "raw":
                    out.append(f'<polygon points="{n(xm)},{n(cy - 9)} {n(xm + 6)},{n(cy - 3)} {n(xm)},{n(cy + 3)} '
                               f'{n(xm - 6)},{n(cy - 3)}" fill="{colour}"/>')
                else:
                    fill = colour if d["reject"] else PAPER
                    out.append(f'<circle cx="{n(xm)}" cy="{n(cy - 3)}" r="4.5" fill="{fill}" stroke="{colour}" '
                               f'stroke-width="1.8"/>')
                out.append(text(xm, cy + 11, pc(d["skill"]), size=10.5, anchor="middle"))
    # axes: tick labels under the last row of each column
    for i, _ in enumerate(SOURCES):
        out.append(line(xs(i, lo_axis), axis_y - 8, xs(i, hi_axis), axis_y - 8, stroke=MUTED, width=1))
        for t in tick_values:
            out.append(line(xs(i, t), axis_y - 8, xs(i, t), axis_y - 4, stroke=MUTED, width=1))
            out.append(text(xs(i, t), axis_y + 8, f"{t:+d}" if t else "0", size=10.5, anchor="middle", fill=MUTED))
    out.append(text(col0 + ncol * colw / 2, axis_y + 24, "per cent by which the curve's error is lower (right) or higher "
                    "(left) than the other forecast's", size=11.5, anchor="middle", fill=MUTED))
    for k, ln in enumerate(notes):
        out.append(text(20, axis_y + 46 + k * 17, ln, size=11, fill=MUTED))
    return finish(out)


def axis_for(data):
    lo = min(100 * d["lo"] for per in data.values() for d in per.values())
    hi = max(100 * d["hi"] for per in data.values() for d in per.values())
    import math
    return 5 * math.floor(lo / 5), 5 * math.ceil(hi / 5)


NOTES_COMMON = [
    "Each forecast is compared with the curve only on the hours (or days) where both exist, so the curve's error differs a little "
    "between columns.",
    "At the development airports AIFS and the NBM grid were read at GFS's grid point, not at the airport itself.",
    "Descriptive, on years already used (2023-24 to 2025-26, depending on the source). Nothing is averaged across airports.",
]
NOTES_DAILY = NOTES_COMMON + [
    "AIFS's daily maximum is the highest of its 6-hourly values and ECMWF IFS's the highest of its 3-hourly values, so "
    "each can miss the true peak.",
]


def fig_hourly(data):
    lo, hi = axis_for(data)
    return fig_compare(
        "compare_hourly.svg", data, "Hourly: the curve against other forecasts",
        ["Right of the line, the curve's error is lower. Left of the line, the other forecast's error is lower.",
         "One dot per airport and forecast, with the 95% range. Every hour from 3 to 48 hours ahead."],
        NOTES_COMMON, [t for t in range(-200, 201, 25) if lo <= t <= hi], lo, hi,
        "Per cent by which the curve's hourly error is lower (positive) or higher (negative) than each other forecast's.")


def fig_daily(data):
    lo, hi = axis_for(data)
    return fig_compare(
        "compare_dailymax.svg", data, "Daily maximum: the curve against other forecasts",
        ["Right of the line, the curve's error is lower. Left of the line, the other forecast's error is lower.",
         "One dot per airport and forecast, with the 95% range. Each day's highest temperature."],
        NOTES_DAILY, [t for t in range(-200, 201, 25) if lo <= t <= hi], lo, hi,
        "Per cent by which the curve's daily-maximum error is lower (positive) or higher (negative) than each other "
        "forecast's.")


# ---------------------------------------------------------------- gate and draw

def build_all():
    """Read every input, run every gate, return {figure name: svg text}."""
    v = load_gain()
    hourly = load_comparison("hourly")
    daily = load_comparison("dailymax")
    return {
        "stagec_gain.svg": fig_gain(v),
        "how_it_works.svg": fig_how(),
        "lock_then_look.svg": fig_lock(v),
        "compare_hourly.svg": fig_hourly(hourly),
        "compare_dailymax.svg": fig_daily(daily),
    }, (v, hourly, daily)


def report_gates(extra):
    v, hourly, daily = extra
    print(f"inputs: {len(INPUTS)} files, each SHA-256 equal to its constant")
    print("gate (a) stagec_gain.svg: 24 margins over raw GFS equal F150.2 at 2 decimals; KORD look B equals SPEC 9.5 "
          "at 3 decimals (hourly 8.216, daily 2.589) and is the smallest; the claim counts 6 and 6 from the file: PASS")
    print("gate (b) how_it_works.svg: no data values drawn: PASS")
    print("gate (c) lock_then_look.svg: dates held as constants " + ", ".join(f"{k}={v_}" for k, v_ in DATES.items())
          + "; the smallest margins drawn come from gate (a): PASS (dates are checked against the entries by the test)")
    for tag, data, table, fig in (("d", hourly, TABLE_2A, "compare_hourly.svg"), ("e", daily, TABLE_2B,
                                                                                   "compare_dailymax.svg")):
        cells = sum(len(per) for per in data.values())
        print(f"gate ({tag}) {fig}: {cells} plotted pairs (raw GFS, AIFS, ECMWF IFS, NBM grid, NBS, MAV); every "
              f"pair at 2 decimals, and the formal-test star, equals the table's cell; each skill equals 1 - curve / "
              f"other forecast: PASS")


def main(argv):
    if len(argv) >= 1 and argv[0] == "--gate" and len(argv) == 1:
        figs, extra = build_all()
        report_gates(extra)
        for name, svg in figs.items():
            print(f"{name}: {len(svg.encode('utf-8'))} bytes, SHA-256 {hashlib.sha256(svg.encode('utf-8')).hexdigest()} "
                  f"(not written)")
        print("alt text:")
        for name, alt in ALT.items():
            print(f"  {name}: {alt}")
        print("--gate: PASS")
        return 0
    if len(argv) == 2 and argv[0] == "--draw":
        outdir = Path(argv[1]).resolve()
        for name in FIGURES:
            if (outdir / name).exists():
                print(f"STOP: {outdir / name} exists; figures are written once")
                return 2
        figs, extra = build_all()
        report_gates(extra)
        outdir.mkdir(parents=True, exist_ok=True)
        for name in FIGURES:
            svg = figs[name]
            with open(outdir / name, "x", encoding="utf-8", newline="\n") as f:
                f.write(svg)
            print(f"wrote {outdir / name}: {len(svg.encode('utf-8'))} bytes, "
                  f"SHA-256 {hashlib.sha256(svg.encode('utf-8')).hexdigest()}")
        print("--draw: PASS")
        return 0
    print("usage: session127_readme_figures.py --gate | --draw OUTDIR")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
