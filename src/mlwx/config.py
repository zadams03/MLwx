"""Per-weather-model settings (DECISIONS D103.3, D103.4).

One WeatherModel per model: its data source, field map (each GRIB message's
identity keys), cycle hours, leads, grid and GFS version table. v1 has only
`gfs`. The 12 airports come from data/gfs_airports.csv (D103.4): the six
development airports and the six claim airports, each with its four grid
points around the position used (D82.4), the elevation constant (SPEC 7.2)
and its time zone.

Everything here is a fixed fact of the build, not a runtime choice. The tests
check data/gfs_airports.csv against the committed files it was built from.
"""

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Field:
    """One GRIB message the adapter reads. ident is the GRIB2 identity:
    (discipline, parameterCategory, parameterNumber, typeOfFirstFixedSurface,
    level). live says whether the live adapter fetches it (the baseline's
    features need only the eight record fields; the 2 m maximum and minimum
    are kept in the pull for later daily-maximum work, D88.5(e))."""
    name: str
    var: str
    level: str
    kind: str        # "instant", "avg", "max" or "min"
    ident: tuple
    live: bool


@dataclass(frozen=True)
class Airport:
    station: str            # IEM id, also the table's station column
    icao: str
    role: str               # "development" or "claim"
    time_zone: str
    lat: float              # the position used (SPEC 3.4 grid point, or IEM's position)
    lon: float
    correction_c: float     # elevation constant, degrees C (SPEC 5.2, 7.2)
    indices: tuple          # grid index of each of the 4 points, in eccodes order
    points: tuple           # ((lat, lon), ...) of the 4 points, same order
    weights: tuple          # bilinear weights, same order (reference; the arithmetic recomputes them)

    @property
    def point_list(self):
        return list(self.points)


@dataclass(frozen=True)
class WeatherModel:
    name: str
    bucket: str
    cycle_hours: tuple
    first_cycle: dt.datetime          # the first run of the version the models were trained on
    first_lead: int                   # first forecast hour fetched (the analysis)
    last_lead: int
    curve_first_lead: int             # leads below this are in the past when a run arrives (D88.6)
    arrival_hours: int                # a run is taken to arrive this long after its start (D98.10(b))
    fields: tuple
    grid: dict                        # the grid geometry every message must have
    versions: tuple                   # ((first cycle, label), ...), ascending
    airports_file: str

    def version_of(self, cycle):
        """The GFS version label of a cycle, from the version table (D103.10). Until a
        DECISIONS entry records the first operational v17 cycle, every cycle is v16."""
        label = None
        for first, v in self.versions:
            if cycle >= first:
                label = v
        if label is None:
            raise ValueError(f"cycle {cycle} is before the first entry of {self.name}'s version table")
        return label

    def live_fields(self):
        return tuple(f for f in self.fields if f.live)

    def file_url(self, cycle, fh):
        return (f"{self.bucket}/gfs.{cycle:%Y%m%d}/{cycle:%H}/atmos/"
                f"gfs.t{cycle:%H}z.pgrb2.0p25.f{fh:03d}")


# The ten fields of the pull (session 91; identities from session86_forward_build.py l.373-389; TMAX and
# TMIN are parameter numbers 4 and 5 of the same category as TMP).
GFS_FIELDS = (
    Field("t2m", "TMP", "2 m above ground", "instant", (0, 0, 0, 103, 2), True),
    Field("tcdc", "TCDC", "entire atmosphere", "instant", (0, 6, 1, 10, 0), True),
    Field("u10", "UGRD", "10 m above ground", "instant", (0, 2, 2, 103, 10), True),
    Field("v10", "VGRD", "10 m above ground", "instant", (0, 2, 3, 103, 10), True),
    Field("d2m", "DPT", "2 m above ground", "instant", (0, 0, 6, 103, 2), True),
    Field("t850", "TMP", "850 mb", "instant", (0, 0, 0, 100, 850), True),
    Field("dswrf", "DSWRF", "surface", "avg", (0, 4, 192, 1, 0), True),
    Field("prmsl", "PRMSL", "mean sea level", "instant", (0, 3, 1, 101, 0), True),
    Field("tmax2m", "TMAX", "2 m above ground", "max", (0, 0, 4, 103, 2), False),
    Field("tmin2m", "TMIN", "2 m above ground", "min", (0, 0, 5, 103, 2), False),
)

GFS = WeatherModel(
    name="gfs",
    bucket="https://noaa-gfs-bdp-pds.s3.amazonaws.com",
    cycle_hours=(0, 6, 12, 18),
    first_cycle=dt.datetime(2021, 3, 22, 12),       # the first GFS v16 run (D84.2, D95.5)
    first_lead=0,
    last_lead=48,
    curve_first_lead=3,
    arrival_hours=4,
    fields=GFS_FIELDS,
    grid={"Ni": 1440, "Nj": 721, "lat_first": 90.0, "lon_first": 0.0, "lat_last": -90.0, "lon_last": 359.75,
          "di": 0.25, "dj": 0.25},
    # D103.10: v16 until the first operational v17 cycle is recorded in a DECISIONS entry.
    versions=((dt.datetime(2021, 3, 22, 12), "v16"),),
    airports_file="gfs_airports.csv",
)

MODELS = {"gfs": GFS}


def get_model(name):
    if name not in MODELS:
        raise KeyError(f"unknown weather model {name!r}; known: {sorted(MODELS)}")
    return MODELS[name]


def load_airports(model):
    """The model's airports, in file order (development airports, then claim airports)."""
    out = []
    with open(DATA / model.airports_file, newline="") as f:
        for r in csv.DictReader(f):
            out.append(Airport(
                station=r["station"], icao=r["icao"], role=r["role"], time_zone=r["time_zone"],
                lat=float(r["lat"]), lon=float(r["lon"]), correction_c=float(r["correction_c"]),
                indices=tuple(int(r[f"p{k}_index"]) for k in (1, 2, 3, 4)),
                points=tuple((float(r[f"p{k}_lat"]), float(r[f"p{k}_lon"])) for k in (1, 2, 3, 4)),
                weights=tuple(float(r[f"p{k}_weight"]) for k in (1, 2, 3, 4))))
    if len({a.icao for a in out}) != len(out):
        raise ValueError("an airport appears twice")
    return out
