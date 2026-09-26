# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 26 September 2026, after session 76b._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (D59.2). F109
stands.**

**A sixth airport, San Francisco International (KSFO), was opened by D67**
under the frozen B+D,L,R,T recipe, with two pre-registered looks (2024-25
and 2025-26). Session 76 verified it, pulled its data and built its
tables (F116). Its GRIB-vs-Open-Meteo reproduction gate **failed**
(F116.5: mean diff −3.326 °C, seasonal). That result stands.

**Session 76b diagnosed the gate failure (D68, F117). It decided nothing.**
- **A. Pipeline: PASS.** Session 76's own code, pointed at RNO, rebuilds
  RNO's record exactly (0 differing rows in 32 field comparisons).
- **B. The four 0.25° points:** two sea points to the west (weight 0.375)
  and two land points to the east (0.625). In summer the sea points run
  much colder; July's four-point spread is 6.90 °C against a 6.05 °C gap.
  Even the warmest land point stays 3.6–4.0 °C below Open-Meteo from April
  to September.
- **C. Open-Meteo's product:** its documentation marks `temperature_2m` as
  coming from the high-resolution 0.11° GFS product, not GFS025. The
  Previous Runs API documents no 0.25°-only GFS option, so no comparison
  pull was made.
- Per F117.5, the evidence meets both of D68.2's "explains the gap" tests
  as written. The owner decides.

Session 76b used SHA-verified cached copies of session 76's GRIB messages,
because session 76 kept none (owner-approved amendment, F117.1).

No model has been fit at KSFO. Its held-out years (2024-08-01..2026-07-31)
have been read for counts and timestamps only.

---

## Open questions (live)

- **Q34 (F116, D68, F117).** KSFO's reproduction gate failed. The owner
  decides using D68.2's pre-registered reading and F117's evidence.
- **Q30 (open).** The owner's order (D66.1): Q33 (done, F115); a further
  airport under the frozen recipe (now KSFO, D67; waiting on Q34); then a
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
  (D66.2, D67.8). As of 2026-09-25 (planning-chat research) no Service
  Change Notice was listed; the earliest possible go-live is late October
  2026.
- **SPEC wording about KSFO and airport counts (session 76 consistency
  items 1–4).** Left for the owner:
  1. SPEC 3.4's note "All five network codes are now verified" does not
     count KSFO's `CA_ASOS`.
  2. SPEC 3.4's note "DSM's is the closest of the five": the count is now
     six (the claim still holds).
  3. SPEC 7.3 says the GRIB temperature matched Open-Meteo "at every
     airport" once corrected. That is scoped to section 7's five airports,
     but a reader may set it against KSFO's failed gate.
  4. SPEC 3.3 lists KSFO's "GRIB elevation constant" among its verified
     facts; the gate that checks it failed. SPEC 3.4 and 6 say so; SPEC 1
     and 3.3 do not.
- **For the lock, if KSFO proceeds.** Raw GFS at KSFO is heavily biased
  relative to Open-Meteo, so beating raw is expected to be easy;
  persistence is the binding part of the bar. State this in the lock's
  expectations. The bias against observations is first measured in
  rehearsal.

---

## Next

**Next planning session: review session 76b; the owner decides Q34 using
D68.2.** If KSFO proceeds, draft session 77: rehearsal on the 2022-23 and
2023-24 folds, the band per D67.5, and the lock, including SPEC 5.2's KSFO
constant and a KSFO-specific held-out guard. If KSFO stops, choose the next
airport under D67.2. After the airport work, hold the roadmap planning
session. Roadmap inputs: P1–P3, Q30 (2026-27, pooling), Q32, SPEC 5.4,
RESULTS §7 terrain descriptor, SPEC stages 4–6, GFS v17 (D66.2, D67.8).
