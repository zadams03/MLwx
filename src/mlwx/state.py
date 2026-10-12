"""The tracker state file (DECISIONS D103.6, Step 7 of session 109).

One file, state/tracker_<model>.json, updated each run. Each cell (airport, cycle hour, lead) holds b, the
valid time of the last error applied (so no error is used twice, and none out of order) and the
number of errors applied. A cell that is not in the file starts at b = 0 (D97.7, D103.6). The file
also lists the cycles that issued nothing, with the reason, and the last run. It is replaced
atomically: a temporary name, then os.replace. The log is the record; this file is a cache of
where the tracker had got to.
"""

import datetime as dt
import json
import os
from pathlib import Path

from .tracker import Cell

TIME_FORMAT = "%Y-%m-%dT%H:%MZ"
STATE_VERSION = 1
MAX_STOPS = 100


def iso(t):
    return None if t is None else t.strftime(TIME_FORMAT)


def parse(s):
    return None if s is None else dt.datetime.strptime(s, TIME_FORMAT)


def state_path(root, model):
    return Path(root) / "state" / f"tracker_{model}.json"


def cell_key(icao, cycle_hour, lead):
    return f"{icao}|{cycle_hour:02d}|{lead}"


class State:
    def __init__(self, model):
        self.model = model
        self.cells = {}          # key -> Cell
        self.stops = []          # [{"cycle": iso, "reason": str, "at": iso}]
        self.last_cycle = None   # the newest cycle issued
        self.last_run = None     # {"at": iso, "status": str}

    def cell(self, icao, cycle_hour, lead):
        key = cell_key(icao, cycle_hour, lead)
        if key not in self.cells:
            self.cells[key] = Cell()
        return self.cells[key]

    def stopped(self):
        return {parse(s["cycle"]) for s in self.stops}

    def add_stop(self, cycle, reason, at):
        self.stops.append({"cycle": iso(cycle), "reason": reason, "at": iso(at)})
        self.stops = self.stops[-MAX_STOPS:]

    def to_json(self):
        return {"version": STATE_VERSION, "model": self.model, "last_cycle": iso(self.last_cycle),
                "last_run": self.last_run, "stops": self.stops,
                "cells": {k: {"b": c.b, "last_valid": iso(c.last_valid), "n": c.n}
                          for k, c in sorted(self.cells.items())}}

    @classmethod
    def from_json(cls, d):
        if d.get("version") != STATE_VERSION:
            raise ValueError(f"state file version {d.get('version')} is not {STATE_VERSION}")
        s = cls(d["model"])
        s.last_cycle = parse(d["last_cycle"])
        s.last_run = d.get("last_run")
        s.stops = list(d.get("stops", []))
        s.cells = {k: Cell(b=v["b"], last_valid=parse(v["last_valid"]), n=v["n"]) for k, v in d["cells"].items()}
        return s


def load_state(root, model):
    """The state, or a fresh one (every tracker at b = 0) if there is no file."""
    p = state_path(root, model)
    if not p.exists():
        return State(model)
    s = State.from_json(json.loads(p.read_text()))
    if s.model != model:
        raise ValueError(f"{p} is for model {s.model}, not {model}")
    return s


def save_state(root, state):
    p = state_path(root, state.model)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(state.to_json(), indent=1, sort_keys=True) + "\n")
    os.replace(tmp, p)
