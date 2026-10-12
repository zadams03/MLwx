"""The four-point extraction arithmetic and the feature builder (DECISIONS D82.4, D88.5).

Ported from scripts/session96_stagec_table.py (make_row, r_inputs, r_raw, r_value,
t_inputs, t_value) and scripts/session91_grib_pull.py (bilinear_stored, derive),
which are the reference and are never edited. Same arithmetic, same rounding
order (SPEC 8.8 G4, G6, G7), same empty reasons, same column order (G15).

Inputs are the raw values at an airport's four grid points, one list of four
per (forecast hour, field), as the adapter or a pull extract holds them. A
feature that cannot be built is None with a reason, never filled (SPEC 2.2).
"""

import datetime as dt
import math

# The nine model inputs, SPEC 8.8 G15, in the record's order. Column order changes the fit.
G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
       "pressure_tendency_3h_hpa"]
GRIB_COLS = ["temp", "temperature_grib_c", "t2m_raw", "cloud_cover", "wind_speed_10m", "dew_point_2m", "t850",
             "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
             "pressure_tendency_3h_hpa", "season_sin", "season_cos", "tmax2m_c", "tmin2m_c"]
OK_STATUSES = ("ok", "ok (whole file)")

# The pull field each instantaneous column needs, at the row's own lead.
INST_NEEDS = {"temp": ["t2m"], "temperature_grib_c": ["t2m"], "t2m_raw": ["t2m"], "cloud_cover": ["tcdc"],
              "wind_speed_10m": ["u10", "v10"], "dew_point_2m": ["d2m"], "t850": ["t850"],
              "dewpoint_depression_t2m_floored": ["t2m", "d2m"], "lapse_rate_t2_t850": ["t2m", "t850"],
              "tmax2m_c": ["tmax2m"], "tmin2m_c": ["tmin2m"], "season_sin": [], "season_cos": []}
PLACEHOLDER = 0.0     # given to the arithmetic for an input whose output is not used; never reaches a row


def window_start(lead):
    """The 6-hour DSWRF average reset mark before a forecast hour."""
    return 6 * ((lead - 1) // 6)


def year_fraction(d):
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


# ------------------------------------------------------------------ bilinear on the four stored values

def bilinear_stored(points, lat, lon, vals):
    """The record's bilinear (SPEC 8.8 G6) on the 4 stored values, with the 4 points'
    (lat, lon) and the position used. Same arithmetic and term order as the pull's."""
    lats = sorted(set(round(q[0], 6) for q in points))
    lons = sorted(set(round(q[1], 6) for q in points))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        raise ValueError("unexpected neighbour layout")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(q[0], 6), round(q[1], 6)): v for q, v in zip(points, vals)}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    return ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
            + dlat * (1 - dlon) * v10 + dlat * dlon * v11)


def airport_values(airport, raw, status=None):
    """Bilinear value of every (forecast hour, field) in raw for one airport. raw maps
    (fh, field) to the airport's 4 raw values. A key whose status is given and is not ok
    is left out."""
    out = {}
    for key, four in raw.items():
        if status is not None and status.get(key) not in OK_STATUSES:
            continue
        v4 = [float(x) for x in four]
        if not all(math.isfinite(x) for x in v4):
            raise ValueError(f"non-finite stored value at {key}")
        out[key] = bilinear_stored(airport.point_list, airport.lat, airport.lon, v4)
    return out


# ------------------------------------------------------------------ R and T (D88.5(b), (c))

def r_inputs(n):
    """The forecast hours whose DSWRF average R at lead n needs, or None when R does not
    exist (leads 0 and 1). W = 6 x floor((n-1)/6)."""
    if n < 2:
        return None
    w = window_start(n)
    if n - w >= 2:
        return [n] if n - 2 == w else [n, n - 2]
    return [n, w, w - 1]


def r_raw(n, a):
    """D88.5(b), unrounded. a maps forecast hour to A(hour), the GFS average over (W, hour]."""
    w = window_start(n)
    if n - w >= 2:
        if n - 2 == w:
            return a[n]                                   # R = A(N) at leads 2, 8, 14, 20
        return ((n - w) * a[n] - (n - 2 - w) * a[n - 2]) / 2
    return (a[n] + 6 * a[w] - 5 * a[w - 1]) / 2          # N - W = 1: leads 7, 13, 19


def r_value(n, a):
    """R as stored: rounded to 3 decimals, as the record stores dswrf_2h_wm2."""
    return round(r_raw(n, a), 3)


def t_inputs(n):
    """The forecast hours T at lead n needs, or None (leads 0 to 2)."""
    return None if n < 3 else [n, n - 3]


def t_value(n, p):
    """D88.5(c): sea level pressure at n minus that at n-3, in hPa, from the two rounded
    pressures, as the record does. p maps forecast hour to PRMSL in Pa."""
    msl = round(p[n] / 100.0, 3)
    m3 = round(p[n - 3] / 100.0, 3)
    return round(msl - m3, 3)


# ------------------------------------------------------------------ one row

def instant_columns(corr, got):
    """The instantaneous columns, with the record's rounding order (SPEC 8.8 G4, G7). got holds
    the bilinear values (or the placeholder) under t2m, tcdc, u10, v10, t850, d2m. Returns the
    values session 91's derive gives for the same columns."""
    tg = round((got["t2m"] - 273.15) + corr, 3)
    cc = round(got["tcdc"], 3)
    ws = round(((got["u10"] ** 2 + got["v10"] ** 2) ** 0.5) * 3.6, 3)
    t2m_raw = round(tg - corr, 3)
    lapse = round(t2m_raw - (got["t850"] - 273.15), 3)
    dd = round(t2m_raw - (got["d2m"] - 273.15), 3)
    return {"temperature_grib_c": tg, "cloud_cover": cc, "wind_speed_10m": ws,
            "dewpoint_depression_t2m_floored": max(dd, 0.0), "lapse_rate_t2_t850": lapse}


def build_row(airport, cycle, n, in_plan, val, stat):
    """Every feature column of one row (session 96's make_row, without the observation).

    in_plan: the forecast hours available for this cycle. val: {(fh, field): bilinear value}.
    stat: {(fh, field): status}. A field the caller does not hold (for example the 2 m
    maximum in a live cycle) is simply absent from stat, and its columns are empty with the
    reason "not fetched".

    Returns (out, reason, used): out maps each GRIB column to a value or None, reason maps
    an empty column to why, used is the set of (fh, field) read."""
    valid = cycle + dt.timedelta(hours=n)
    used, reason, out = set(), {}, {}

    def need(fields_at):
        for fh, fname in fields_at:
            if fh not in in_plan:
                return "outside pull window"
        for fh, fname in fields_at:
            if (fh, fname) not in stat:
                return "not fetched"
        for fh, fname in fields_at:
            if stat[(fh, fname)] == "absent by design":
                return "absent by design"
        for fh, fname in fields_at:
            if stat[(fh, fname)] not in OK_STATUSES:
                return "message not ok"
        return None

    got = {fname: val.get((n, fname), PLACEHOLDER) for fname in ("t2m", "tcdc", "u10", "v10", "t850", "d2m")}
    der = instant_columns(airport.correction_c, got)
    corr = airport.correction_c
    for col, fields in INST_NEEDS.items():
        why = need([(n, f) for f in fields])
        if why:
            reason[col] = why
            out[col] = None
            continue
        used.update((n, f) for f in fields)
        if col in ("temp", "temperature_grib_c"):
            out[col] = der["temperature_grib_c"]
        elif col == "t2m_raw":
            out[col] = round(der["temperature_grib_c"] - corr, 3)          # SPEC 8.8 G4
        elif col in ("cloud_cover", "wind_speed_10m", "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850"):
            out[col] = der[col]
        elif col == "dew_point_2m":
            out[col] = round(val[(n, "d2m")] - 273.15, 3)                    # SPEC 8.8 G7
        elif col == "t850":
            out[col] = round(val[(n, "t850")] - 273.15, 3)                   # SPEC 8.8 G7
        elif col in ("tmax2m_c", "tmin2m_c"):
            out[col] = round(val[(n, col[:6])] - 273.15, 3)                  # D88.5(e), no constant
        elif col == "season_sin":
            out[col] = math.sin(2 * math.pi * year_fraction(valid.date()))
        elif col == "season_cos":
            out[col] = math.cos(2 * math.pi * year_fraction(valid.date()))
    leads = r_inputs(n)
    why = "lead too short" if leads is None else need([(fh, "dswrf") for fh in leads])
    if why:
        reason["dswrf_2h_wm2"], out["dswrf_2h_wm2"] = why, None
    else:
        used.update((fh, "dswrf") for fh in leads)
        out["dswrf_2h_wm2"] = r_value(n, {fh: val[(fh, "dswrf")] for fh in leads})
    leads = t_inputs(n)
    why = "lead too short" if leads is None else need([(fh, "prmsl") for fh in leads])
    if why:
        reason["pressure_tendency_3h_hpa"], out["pressure_tendency_3h_hpa"] = why, None
    else:
        used.update((fh, "prmsl") for fh in leads)
        out["pressure_tendency_3h_hpa"] = t_value(n, {fh: val[(fh, "prmsl")] for fh in leads})
    for col in GRIB_COLS:
        if out[col] is not None and not math.isfinite(out[col]):
            raise ValueError(f"non-finite {col} at {airport.icao} {cycle} f{n:03d}")
    return out, reason, used


def feature_vector(out):
    """The nine model inputs in G15 order, or None if any is empty."""
    x = [out[c] for c in G15]
    return None if any(v is None for v in x) else x
