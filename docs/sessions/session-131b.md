# Session 131b: the live tool's models move to a private repository

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
The 49-airport product models are today a public Release asset of
MLwx-live (D105.2). This session changes the live workflow template so
the models are downloaded from a private repository with a read-only
token, and writes the owner's steps. The models themselves do not
change: same file, same SHA-256, same `MODELS_TAG`. Recommended model:
Sonnet.

## Read first

- STATUS.md in full; SPEC section 2; the live DECISIONS.md (D125 and
  F174 only).
- Archived, by line range: D103.5, D105.2, D105.9, F152.5.
- `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`,
  `tests/test_live_template.py` in full.

## Rules for this session

- Only the template, its README, its tests and the record change. No
  file under `src/` (D125.4's pinned files above all), `scripts/` or
  `data/` changes. No network.
- No logged value changes: the models are byte-identical, so D105.5(k)
  is not engaged beyond the redeploy D125.8 already records.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
deploy/mlwx-live/.github/workflows/live.yml, deploy/mlwx-live/README.md,
tests/test_live_template.py, notes/session-131b-output.txt.

## Steps

**Step 1. Start checks.** HEAD is session 131's commit (its title starts
"Session 131:"); the tree is clean apart from this prompt. Tests: 395 OK
(1 skipped). Stop if any check fails.

**Step 2. Record D126.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-14: Session 131b decision: F174 accepted, and the product models moved to a private repository (owner, planning chat)

**D126. Owner decisions, planning chat (after session 131's commit): F174 accepted; the live tool's product models are kept in a private repository from the next redeploy; and Live index changes.** Written at the start of session 131b, before any other edit. No 2026-27 value has been read or scored.

- **D126.1 F174 accepted,** with its readings.
- **D126.2 Why (owner).** The models are the working product; the code, the record, the log and the page stay public. Public signals checked by the planning chat on 2026-11-14: `gfs-models-49` downloaded 2 times and `gfs-models-12` once (the live workflow's own fetches), no forks, no stars, one unique visitor (the owner) to MLwx in 14 days. Stage B's frozen models (`data/models/session81/`) stay in MLwx: they are part of D73's pre-registered test.
- **D126.3 How.** A private repository, `zadams03/MLwx-models`, holds the same `gfs-models.tar` as a Release with the same tag, `gfs-models-49`; its SHA-256 must equal D105.2's (`e30f8fb99e275fd410bcc37a41686deb26bf61ccb658cb0acbb419da9769f284`) before it is used. MLwx-live's workflow downloads it with a fine-grained token, read-only on that one repository's contents, stored as the secret `MODELS_TOKEN`, under a new cache key, so the first run after the redeploy proves the private route. The models' own manifest check in the code (D103.5) is unchanged. After one green run on the private route, the owner deletes the public Releases `gfs-models-49` and `gfs-models-12` from MLwx-live and the old cache entries. MLwx-live's fork pull request workflows are set to need the owner's approval for every outside contributor, so no outside workflow can read the cache.
- **D126.4 The redeploy.** One redeploy covers D125.8 and D126.3: `MLWX_COMMIT` is session 131's commit (the runner reads no model path that changes here), `MODELS_TAG` stays `gfs-models-49`.
- **D126.5 Live index.** Removed (archived): D125 and F174, which are settled (D125's rulings are carried in STATUS and by their tests). Added: D126 and F175 (F175 when it is written). After session 131b: D93, D103, D105, D118, D126, F175.
```

**Step 3. The template.** In `live.yml`: add `MODELS_REPO:
zadams03/MLwx-models` to `env`; a step before the cache restore that
fails with a plain message if `secrets.MODELS_TOKEN` is empty; the
cache key becomes `gfs-models-private-${{ env.MODELS_TAG }}`; the
download step uses `GH_TOKEN: ${{ secrets.MODELS_TOKEN }}` and
`--repo "$MODELS_REPO"`, and after `tar -xf` nothing else changes.
Update the header comment (item 3). README: where the models live and
why, in plain words.

**Step 4. Tests.** In `tests/test_live_template.py`: the download step
names `MODELS_REPO` and `secrets.MODELS_TOKEN`, not `GITHUB_REPOSITORY`
or `github.token`; the cache key contains `private`; the empty-secret
check step exists and comes before the cache step; the two
`SET-AT-DEPLOY` lines are unchanged. All tests pass.

**Step 5. The owner's steps,** written into the output file in this
order, plain and exact:
1. Create the private repository `zadams03/MLwx-models` (no README).
2. Get the tar: `gh release download gfs-models-49 --repo
   zadams03/MLwx-live --pattern gfs-models.tar`; check `shasum -a 256
   gfs-models.tar` equals D126.3's value.
3. `gh release create gfs-models-49 gfs-models.tar --repo
   zadams03/MLwx-models --title "Frozen GFS product models, 49 airports"
   --notes "Same file as MLwx-live's former public Release (DECISIONS
   D105.2, D126)."`; check the asset's SHA-256 by downloading it again.
4. Create a fine-grained personal access token: only
   `zadams03/MLwx-models`, permission Contents: Read-only, an expiry
   date the owner chooses (and a reminder to renew it before then).
5. In MLwx-live: Settings, Secrets and variables, Actions, new
   repository secret `MODELS_TOKEN` with that token.
6. In MLwx-live: Settings, Actions, General, fork pull request
   workflows: require approval for all outside collaborators.
7. Redeploy MLwx-live's workflow from the template, with `MLWX_COMMIT`
   session 131's 40-character commit and `MODELS_TAG` `gfs-models-49`;
   copy the template's `.gitignore` and README; commit and push.
8. Run the workflow by hand once, not between :35 and :55 past the
   hour. It must be green, its log must show the download from
   `zadams03/MLwx-models`, and the runner must start.
9. Only then: delete the Releases `gfs-models-49` and `gfs-models-12`
   from MLwx-live (and their tags if asked), and under MLwx-live's
   Actions, Caches, delete the entries named `gfs-models-gfs-models-...`.
10. Copy session 131's three MOSMIX files into `zadams03/MLwx-mosmix`,
    push, run it by hand once.
11. Tell the planning chat: the commit of MLwx-live's redeploy, the time
    of the green run, and whether every step went as written.

**Step 6. Final checks.** Tests all OK; no file outside the scope list
changed; no file under `src/` changed; 0 em-dashes in added lines.

## End of session (CLAUDE.md)

1. **F175**, at most about 25 lines: the template's changes, the tests,
   the owner's steps in brief, every check with PASS or FAIL.
2. **Overwrite STATUS.md:** the redeploy and the models' move wait for
   the owner (D126.3, D126.4); the rest as session 131 left it. End
   with: `**Next planning session:** Review session 131b and commit; the
   owner moves the models, redeploys MLwx-live and updates MLwx-mosmix;
   the planning chat records the redeploy and syncs Project knowledge
   (D118.8); then session 132 (D125.9).`
3. **Archive step:** make D126.5's index changes, add F175, then
   `python3 scripts/archive_decisions.py --apply --session 131b`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a short summary; report it in chat. Then
   stop and wait for review. Do not commit.
