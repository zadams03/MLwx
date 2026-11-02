# notes/: what each session actually printed

This folder holds the saved, real output of the sessions, so every number in the record can
be traced to what a script printed.

- **Session output:** `session-NN-output.txt` and similar names (for example
  `session-07-check-output.txt` or `session-50-e1-experiment-output.txt`). Each finding in
  DECISIONS.md names the file that holds its full output. The prompt for session NN is
  `session-NN.md` in [../docs/sessions/](../docs/sessions/).
- **Audit reports:** `audit-session-*.md`, the four audit reports written in sessions 66 to
  68b and triaged in the record.
- **Health check registers:** `session-120-register.csv` and `session-121-register.csv`, one
  row per item checked by the project health check's two audits.
- **Other records** that the record names, such as `session-34-archive-manifest.md`.

Some scripts write their output files here, and the record cites these files by path, so the
folder and its file names stay as they are. These files are part of the record and are not
edited after the fact.

Some files contain file paths from the author's own machine.

## Where these facts come from

"D" and "F" numbers are entries in [../DECISIONS.md](../DECISIONS.md) or its
[archive](../DECISIONS-archive.md).

| fact in this file | where it is recorded |
|---|---|
| The audit reports were triaged | D62 |
| The health check registers | D114.7 |
| The archive manifest | D46 |
| The folder and its file names stay as they are, because the record cites them by path | D91.2 |
| Some files contain file paths from the author's machine | F126.2 |
