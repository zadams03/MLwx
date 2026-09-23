# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 65._

---

## Where the project is right now

**The project now has three independently-tested, proven methods for
correcting GFS's local bias at an airport, and the feature-selection
programme that produced the third one is closed.**

1. **The minimal method** (SPEC sections 1–6) — three features, Open-Meteo
   source. Passes at four of five airports; fails at Reno. Results:
   EGLC/LFPG/DSM/YSDU F16/F30/F47/F64 (PASS), RNO F82 (FAIL).
2. **The richer 5-feature GRIB method** (SPEC section 7, "act two" in
   RESULTS.md) — five features, GFS GRIB source. Passes at all five
   airports, including Reno. Result: F94.
3. **The selected-features GRIB method** (SPEC section 8, new this
   session, "act three" in RESULTS.md) — the 5-feature baseline (`B`) plus
   four selected features (moisture, lapse rate, shortwave radiation,
   pressure tendency — `B+D,L,R,T`), chosen by a staged feature-selection
   programme (DECISIONS D51–D59) and confirmed once on a separate reserved
   year (2024-08-01..2025-07-31). Passes at all five airports, including
   Reno. Result: F109. Secondary read: beats plain `B` on airport-averaged
   MAE (1.2377 vs 1.3170, +6.02%). This is now the project's **default
   recipe** for future airport or pooling work (DECISIONS D59.3).

**None of the three methods erases any other** (DECISIONS D48.13, D59.3);
all three results stand as reported, each with its own required caveats
(SPEC 7.5, SPEC 8.6/DECISIONS D59.3).

**The feature-selection programme is closed (DECISIONS D59.2).** No
further feature family, variant, or combination will be tested under it.
The reserved year is spent for this programme and will not be reused for
any verdict; the in-code reserved-year guard stays in place, untouched, as
a permanent tripwire.

**No untouched held-out year now remains at any of the five airports.**
The 2025-26 year is spent (F94, the richer method's sealed test) and the
2024-25 year is spent (F109, the selected-features confirmation). A
further independent test now needs either a new airport (never scored on
either year) or a live, forward-looking year not yet elapsed — 2026-27
(2026-08-01..2027-07-31) — which session 65's own Step 0 check confirmed
has not yet had any row scored anywhere under `data/processed/`
(DECISIONS D59.5).

**Documentation only this session.** `SPEC.md` §8 and `RESULTS.md` §6 now
carry the selected-features method (DECISIONS D59, F110); F97–F109/D52–D58
are archived to `DECISIONS-archive.md` (D51, F96 stay live). Nothing was
committed.

---

## Open questions (live)

- **Q30 (open; its options changed this session, per D59.5, now that no
  untouched held-out year remains).** The owner previously picked its
  first branch — more airports, "ramp up difficulty" — and both the
  richer-features branch (F94) and the selected-features branch (F109)
  of that programme are now complete and documented. **Q30's three
  branches — a further airport, a second test year (now only possible as
  a forward-looking 2026-27 test or a weaker reuse rule), or pooling
  (SPEC stage 3) — remain fully open and are the owner's choice**
  (DECISIONS D59.5). See "Next," below, for the planning-chat
  recommendation on record.
- **Q32 (effectively answered by events, left on record rather than
  formally closed; unchanged this session).** Session 27 asked whether
  Reno's rehearsal loss should change anything about locking/testing
  Reno; the session-28 and session-29 prompts both instructed proceeding
  regardless, and that is what happened — Reno was locked unmodified
  (D44) and tested unmodified (F82), and it failed. The owner has still
  not been asked, in so many words, whether a failed sealed test (as
  opposed to just a negative rehearsal) changes their intentions for
  future terrain-hard airports generally — though both the richer-
  features result (F94) and the selected-features result (F109) are now
  the owner's practical answers for Reno specifically.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.

---

## Next

Q30's three branches, per DECISIONS D59.5:
- **A further airport**, run under the frozen `B+D,L,R,T` recipe — the
  cheapest genuinely out-of-sample test available now, per D32 a harder
  type (coastal, tropical, or mountainous).
- **A second test year** — now only possible as (i) a live, forward-
  looking pre-registered test on 2026-27, scored once after the year
  ends, or (ii) a written rule for reusing an already-seen year (weaker
  evidence).
- **Pooling** (SPEC stage 3) — the largest build; previously judged
  premature with only five locations.

**Planning-chat recommendation on record (DECISIONS D59.5, not a
decision — the owner has not chosen):** open a further airport under the
frozen `B+D,L,R,T` recipe now, and in parallel pre-register 2026-27 as a
forward-looking test year (a small documentation step); defer pooling.

**Next planning session: the owner chooses a Q30 branch (DECISIONS D59.5;
recommendation on record above).**
