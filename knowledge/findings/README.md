# knowledge/findings/: what was found out, and when

One short dated note per finding, written by an agent or by Arek, so that a later session does not have to find
it out again. Newest at the bottom of the index.

## Index

| Date | Note | Finding in one line | Status |
|---|---|---|---|
| 2026-11-14 | `2026-11-14_repository_reorganization_checks.md` | What depends on file paths in this repo, and what was verified after the reorganization | current |

## Template

File name: `<YYYY-MM-DD>_<topic_in_snake_case>.md`.

```
# <Finding in one sentence>

- Date: YYYY-MM-DD
- Found by: <agent or Arek>, while <task>
- Status: current | superseded by <file>

## What was checked and how
Commands run, pages opened (with URL and date), files read.

## Result
The facts, with numbers. Mark anything not verified as "untested".

## What it means for the project
Which decision, document or code it affects; link to `docs/decisions.md` if a decision followed.
```

## Earlier findings recorded elsewhere

Before this folder existed, findings were written into other documents. They stay there:
`docs/zrodla_danych/weryfikacja_maila.md` (advisor-e-mail claims checked), `docs/data_gathering_plan.md` (endpoints
tested), `code/ingestion/CLAUDE.md` ("Status" and "Source-specific gotchas"),
`dataset_research/space_weather_decision/README.md` (sanity checks and backtests), and the "Resolved" items in
`docs/open_questions.md`.
