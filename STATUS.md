# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 25 September 2026, after session 76._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (D59.2). F109
stands.**

**A sixth airport, San Francisco International (KSFO), was opened by D67**
under the frozen B+D,L,R,T recipe, with two pre-registered looks (2024-25
and 2025-26). Session 76 verified it on contact, pulled all its data, and
built its feature table and paired observations (F116):
- IEM code `SFO`; target hour 20:00 UTC, lead 26 (as RNO); routine report
  at `:56`, a 4-minute pairing offset; elevation constant +0.6944 °C.
- 1,955 of 1,956 feature days (2022-11-30 lost upstream, as at RNO);
  1,953 of 1,956 days paired.
- **The GRIB-vs-Open-Meteo reproduction gate FAILED** (before
  2024-08-01): mean |diff| 3.395 °C, mean diff −3.326 °C, against < 1.0.
  The gap is seasonal (about −0.2 to −0.8 °C in winter, −4 to −6 °C
  from April to September). The pipeline was checked against RNO's record
  and is not the cause. A coastal land/sea effect is likely but untested.
- Per the session prompt, the session stopped after the gate. The
  constant and pipeline were not changed. Step 5.5 (feature sanity) was
  not run.

No model has been fit at KSFO. Its held-out years (2024-08-01..2026-07-31)
have been read for counts and timestamps only.

---

## Open questions (live)

- **Q34 (new, F116).** KSFO's reproduction gate failed. Options: stop KSFO
  and pick another airport under D67.2's offset rule; go ahead with the
  recipe unchanged, with the gate failure as a caveat; or first
  investigate descriptively (for example the land mask of the four GRIB
  points), before 2024-08-01 only. The owner decides.
- **Q30 (open).** The owner's order (D66.1): Q33 (done, F115); a further
  airport under the frozen recipe (now KSFO, D67; blocked on Q34); then a
  dedicated roadmap planning session. Pooling is deferred. The 2026-27
  forward test is deferred until the GFS v17 date is known (D66.2, D67.8).
  If a 2026-27 test is ever pre-registered, it must name the two tracked
  DSM files for 2026-08-05..2026-08-15 (D62.7, A67-15).
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82) changes the owner's intentions for future terrain-hard airports
  generally.

No other open question is live.

---

## Carried items

- **GFS v17.** Re-check the NWS notice list at each planning session
  (D66.2, D67.8). As of 2026-09-25 (planning-chat research, not checked by
  session 76) no Service Change Notice was listed; the earliest possible
  go-live is late October 2026.
- **SPEC 3.4 note "All five network codes are now verified"** does not yet
  count KSFO's `CA_ASOS` (verified in session 76). Left for the owner
  (session 76 consistency check).

---

## Next

**Next planning session: review session 76 (F116), then decide Q34.** If
KSFO goes ahead, draft session 77 as D67 plans: KSFO rehearsal on the
2022-23 and 2023-24 folds, the column-order band per D67.5, and the lock,
including SPEC 5.2's KSFO constant and a KSFO-specific held-out guard for
session 78. If KSFO stops, choose the next airport under D67.2. After the
airport work, hold the roadmap planning session. Roadmap inputs: P1–P3,
Q30 (2026-27, pooling), Q32, SPEC 5.4, RESULTS §7 terrain descriptor,
SPEC stages 4–6, GFS v17 (D66.2, D67.8).
