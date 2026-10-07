# docs/: how each session was planned

This folder is the working record of how the project was run, one session
at a time. Nothing here is needed to run the code.

## The loop

Session prompts are in [sessions/](sessions/) and commit messages in
[commits/](commits/) (D92.2).

1. The owner plans each session in a planning chat and writes its prompt,
   `sessions/session-NN.md` in [sessions/](sessions/). The prompt says
   exactly what the session may do.
2. Claude Code (Anthropic's AI coding tool) carries out that one session,
   under the standing rules in [../CLAUDE.md](../CLAUDE.md), and saves its
   real printed output in [../notes/](../notes/README.md).
3. The owner reviews the result and commits it by hand. The commit message
   is saved as `commits/commit-NN.txt` in [commits/](commits/).

A suffix such as `03b`, `34a` or `98b` marks a session that was split or
re-run.

## Other files

- [PROJECT-INSTRUCTIONS.md](PROJECT-INSTRUCTIONS.md): the planning guide,
  the operating rules for the planning chat. Claude Code does not follow
  it. It was moved here from the repository root by DECISIONS D91.3.
- [HANDOVER-richer-features.md](HANDOVER-richer-features.md): a handover
  note written on 9 September 2026, just after session 30, for a new
  planning chat starting the richer-features phase. It carries the plan
  and reasoning of that time; its own text says the project's files win
  wherever they disagree with it.

These files are part of the record and are not edited after the fact.
