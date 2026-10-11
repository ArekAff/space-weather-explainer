# How the CLAUDE.md files in this repo work, and how to keep them useful

For Arek and for any agent that edits a CLAUDE.md. Based on Anthropic's Claude Code memory documentation
(https://code.claude.com/docs/en/memory) and common practice, checked 2026-10-11.

## How Claude Code loads them

- `CLAUDE.md` files in the directory where a session starts, and in every directory above it, load at launch.
  Start sessions at the repo root (`magisterka/`) so the root file always loads.
- A `CLAUDE.md` in a subdirectory loads on demand, the first time the agent reads or edits a file in that
  subdirectory. So `code/ingestion/CLAUDE.md` costs nothing while the agent works on the platform.
- Files are concatenated, not overridden. Instructions that contradict each other make the agent pick one arbitrarily,
  so each fact lives in one file only.
- `@path/to/file` inside a CLAUDE.md imports that file at launch. Imports organise text but don't save context.
  This repo deliberately uses plain backticked paths instead, so `docs/` files load only when an agent opens them.
- `CLAUDE.local.md` (git-ignored) holds personal, uncommitted notes and loads after `CLAUDE.md` in the same folder.
- `.claude/rules/*.md` with a `paths:` front-matter loads only for matching files. Use it if a rule applies to one file
  type across many folders (e.g. all notebooks). Folder-specific rules belong in that folder's CLAUDE.md.
- CLAUDE.md is guidance, not enforcement. Anything that must never happen (e.g. committing `_netrc`) also needs a
  technical guard: `.gitignore`, a test, or a hook.

## What goes where

| File | Holds | Size budget |
|---|---|---|
| `CLAUDE.md` (root) | What the project is, research design and invariants, repo map, how agents work, update rules | < 200 lines |
| `code/CLAUDE.md` | Layout, tooling and commands, the data-store contract, rules for all code | < 150 |
| `code/ingestion/CLAUDE.md` | Build order, collector rules, per-source gotchas | < 150 |
| `code/platform/CLAUDE.md` | Pipeline, variant and time-gate rules, component notes, evaluation rules | < 150 |
| `docs/CLAUDE.md` | How to treat snapshots vs living docs | < 50 |
| `docs/*.md` | Long reference material, decisions, open questions | No limit; linked, not loaded |

Include what an agent cannot work out from the code: commands, conventions that differ from defaults, the research
rules, data quirks, things that went wrong before. Leave out what it can infer, standard language conventions,
long tutorials, file-by-file descriptions and anything that changes weekly.

## When to update (the protocol)

| Event | Action |
|---|---|
| New command, dependency, folder or file convention | Update the most specific CLAUDE.md in the same commit |
| Arek makes a decision | Dated entry in `docs/decisions.md`; then fix every CLAUDE.md line it affects |
| An open question is answered | Move it from `docs/open_questions.md` to `docs/decisions.md` |
| Arek corrects an agent, or the same mistake happens twice | Add a one-line rule to the file whose scope would have prevented it |
| A source endpoint is tested | Update its entry in `docs/data_gathering_plan.md` |
| A fact in a CLAUDE.md turns out wrong | Edit it in place (no "UPDATE:" notes); log it in `decisions.md` if it was a decision |
| A file passes its size budget | Move detail into `docs/` and replace it with a link |
| Milestone (first collector running, first end-to-end explanation, before the TEST run, before writing chapters) | Review all CLAUDE.md files for stale or conflicting lines |

Guard rails:
- The root "Research design" section changes only with Arek's explicit OK. Agents propose; Arek approves.
- Write rules as imperatives that can be checked. Prefer "Store timestamps as tz-aware UTC" to "be careful with time".
- Say why when the reason isn't obvious. A rule with its reason gets applied correctly in new situations.
- Don't add emphasis inflation (ALL CAPS, "CRITICAL" everywhere). Bold is reserved for the few invariants.
- No secrets, personal data or credentials in any CLAUDE.md.
- Every agent that changed a CLAUDE.md says so, line by line, in its final message.

## Periodic audit (5 minutes, at each milestone)

1. Run a session at the repo root and ask: "Read every CLAUDE.md and docs/decisions.md. List contradictions, stale
   statements and rules that no longer match the code." Claude Code's `/doctor prompt-audit` (if available in your
   version) does a similar check.
2. Delete what is no longer true. Shorten what grew.
3. Check that commands in `code/CLAUDE.md` still run.
