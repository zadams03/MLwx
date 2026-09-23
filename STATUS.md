# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 64._

---

## Where the project is right now

**The single authorized reserved-year confirmation of the locked final
feature set (D58: B + D, L, R, T) has been run, once, and PASSES the
frozen bar at all five airports (F109).** Session 64's Step 1 gate
(re-running `preflight()`) matched session 61's own grid and session 62's
own preflight output to the fourth decimal at all five airports before
`--confirm` was run. `--confirm` then ran cleanly, once — no guard trip,
no crash.

**Reserved-year result (2024-08-01..2025-07-31), per airport (raw GFS
MAE / persistence MAE / B MAE / B+D,L,R,T MAE):**

```
station  raw     persist  B       B+DLRT   vs_raw    vs_persist  vs_B
EGLC     1.2362  2.2259   1.0861  1.0008   +19.04%   +55.04%     +7.85%
LFPG     1.4091  2.5233   1.3285  1.2369   +12.22%   +50.98%     +6.89%
DSM      1.7043  4.1081   1.4402  1.4123   +17.13%   +65.62%     +1.94%
YSDU     1.4897  2.5775   1.3030  1.2643   +15.13%   +50.95%     +2.97%
RNO      1.6135  2.7563   1.4272  1.2742   +21.03%   +53.77%     +10.72%
```

**Bar verdict: PASS at all five airports, beating both raw GFS and
persistence, no exception.** Secondary read: B+D,L,R,T beats plain B on
airport-averaged MAE (1.2377 vs 1.3170, +6.02%). D58 item 7 pre-registered
only that per-airport variation was expected, especially at DSM — not a
ranking: DSM's small margin (+1.94%) is consistent with that expectation;
RNO's own margin (+10.72%) was not pre-registered and is descriptive only.
Full detail, per-rung row counts, the day-set-mismatch note (EGLC/YSDU,
verdict-irrelevant, same F93 pattern), and the D58 item 8 honesty caveat
are in DECISIONS F109.

**This was THE single authorized look at the reserved year for this
feature set (D51). It is now spent and will not be repeated.** The look
does not re-open, re-score, or change any prior verdict — the minimal
method's own airport results (F16/F30/F47/F64/F82), the 5-feature GRIB
sealed test (F94), and the multi-year backtest (F96) all stand exactly as
reported. This confirmation is a separate, additional result for a richer,
selected feature set on a separate held-out year.

**No code, script, `SPEC.md`, or `RESULTS.md` was modified this session.**
`scripts/session62_reserved_confirm.py` remains frozen, unchanged since
F107's documented pre-look wiring — `git diff HEAD` against it was empty
both before and after this session. Nothing was committed.

---

## Next

**Next planning session: owner review of F109 and the verdict.** The
confirmation result (bar PASS at all five airports, secondary read
confirmed, DSM's small margin consistent with D58 item 7's own
pre-registered expectation) is ready for the owner's review. Open
decisions for that session: whether/how to fold B+D,L,R,T into `SPEC.md`
as a third proven method alongside the minimal method (sections 1–6) and
the 5-feature GRIB method (section 7); whether/how to update `RESULTS.md`
to cover it; and the archive pass for D52–D58/F106–F108, which per this
session's own scope stayed live and untouched pending that review.

---

## Open questions (live)

- **Q30 (its richer-features branch is resolved; the question itself stays
  open because its other two branches remain the owner's choice).** The
  owner picked its first branch — more airports, "ramp up difficulty" — and
  Reno's own five steps are finished, ending in a failure under the
  existing recipe. The richer-features branch of that intent has now
  reached its answer (the 5-feature GRIB recipe passes at all five
  airports, F94), and its documentation follow-up (SPEC/RESULTS fold-in,
  archive pass) is done. **Q30's other two branches — a further airport,
  and a second test year (the remaining half of the F30/F48 caveat) — and
  stage 3 (pooling) remain fully open and are the owner's choice**,
  unaffected by how the richer-features branch resolved, and unaffected by
  the feature-selection programme's own now-complete confirmation (F109).
- **Q32 (effectively answered by events, left on record rather than
  formally closed).** Session 27 asked whether Reno's rehearsal loss should
  change anything about locking/testing Reno; the session-28 and session-29
  prompts both instructed proceeding regardless, and that is what happened
  — Reno was locked unmodified (D44) and tested unmodified (F82), and it
  failed. The owner has still not been asked, in so many words, whether a
  failed sealed test (as opposed to just a negative rehearsal) changes their
  intentions for future terrain-hard airports generally — though the
  richer-features branch is the owner's first practical answer for Reno
  specifically.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
