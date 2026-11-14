# space-weather-explainer: daily space-weather early warning; classic LLM with RAG vs a decision model

SGH master's thesis (Analiza danych – Big Data) by Arek (Arkadiusz Affek), advisor Prof. Surma.
Working title (PL, proposed 2026-11-13): „Wczesne ostrzeganie o zagrożeniach pogody kosmicznej dla systemów
satelitarnych: analiza porównawcza modelu językowego z RAG i modelu decyzyjnego”.

The platform monitors the space-weather situation (not the satellites) with real-time data analysis. Once a day it
issues an early warning: the most probable incident type, from a predefined catalogue modelled on cybersecurity
incident taxonomies, that the situation could cause for satellites and GNSS positioning. Users: precision GNSS
positioning (mainly precision agriculture in Poland) and satellite operators. In Polish thesis text say „analiza
danych czasu rzeczywistego”, never „szereg czasowy” (advisor).

## Research design (do not change without Arek's explicit OK)

Research question (2026-11-13): picking the most probable incident type from the catalogue, how do a classic LLM
with RAG and a decision model of the "System One" kind compare on cost, quality and time? Simple comparison, no
hybrid approaches (advisor). Same events in every scenario:

| Scenario | Gets | Decides | Role |
|---|---|---|---|
| A | Numeric data + detected anomalies; analogues on numeric features only | Classic LLM | Baseline |
| C | A + DONKI catalogues (structured fields incl. SEP; shock, CME speed and driver type also filter analogues) + RAG over expert texts, with citations | Classic LLM | The platform |
| C-decision | Same knowledge as C | Decision model (e.g. Jev, TypeSafe AI; need not be Jev) | Does the decision model improve the platform? |

Variant B is dropped (advisor, 2026-11-13). Whether optional D (NOAA forecaster text) stays is open.

Invariants. Breaking one silently invalidates the thesis:
1. **The answer key never reaches the system.** Richardson–Cane ICME list, SSC list (ISGI/Ebre), NOAA proton-event
   list (NGDC), effect data (IGS TEC/ROTI, EPN, orbital elements), GUGiK notices about specific jamming cases, and
   case-study papers about test events are used only by evaluation code.
2. **Shock-arrival feature comes from DONKI IPS real-time alerts** (notifications, by `messageIssueTime`), never from
   SSC (SSC is answer key). IPS catalogue entries usually appear after t0.
3. **Time cut-off.** A document or catalogue entry is visible for event *e* only if `issued_at <= t0(e)`. Publication
   time counts, not the period described. Date-only timestamps count as 23:59 UTC. This applies to catalogues in C
   and C-decision too (DONKI `submissionTime`), not only to RAG.
4. **DONKI notes before 06/2020 were added retroactively**: mark `is_retrospective = true`; excluded in the main mode.
5. **DEV/TEST split.** TEST = events from 2025-01-01, except the May 2026 rtgms.pl jamming episodes (J132–J139),
   which are DEV (62 of 158 in TEST, 96 in DEV). Tune prompts, thresholds and retrieval on DEV only;
   run TEST once at the end. Report C separately per corpus period (before 06/2020, to 02/2024, from 03/2024) and for
   events after the LLM's training cut-off.
6. **Provenance on every value**: `source`, `status` (`realtime`/`pre`/`def`/`provisional`), `retrieved_at`. Raw
   downloads are immutable and stored with SHA-256.
7. **Data freeze**: test events up to 2026-12-31; final re-pull of all catalogues in Feb 2027 (GFZ definitive values).
   Thesis numbers are computed only on the frozen version.

Facts that bite: NOAA live JSON files keep only 1–7 days, so the live collector is the most urgent code (every day
without it is lost for good). NOAA Forecast Discussion exists only from 03/2024. Kp is written in thirds
(5- = 4.67, 5o = 5.00, 5+ = 5.33); G1..G5 = Kp 5..9. NOAA Kp and GFZ Kp disagree at thresholds; store which one.
Kp saturates at 9o, so rank extremes with Hp30. GFZ revises preliminary values monthly.

Implementation status: `code/ingestion/CLAUDE.md` (Status section); collection checklist: `docs/data_gathering_plan.md`.

Full rationale: `docs/README.md` (index), decisions in `docs/decisions.md`, unresolved items in `docs/open_questions.md`.

## Repository map

| Path | What it is | Agents may |
|---|---|---|
| `code/` | All application code (see `code/CLAUDE.md`) | Create and edit |
| `code/ingestion/` | Data ingestion pipeline: collectors, raw archive, normalised tables, corpus | Create and edit |
| `code/platform/` | The system: detection, analogues, catalogues, RAG, incident-type decision, evaluation | Create and edit |
| `data/` | Data store written by the collectors (git-ignored; contract in `code/CLAUDE.md`) | Write only through `code/ingestion` |
| `evaluation/` | What the system is scored against: evaluation event set, its rules, inputs and build scripts (see `evaluation/CLAUDE.md`) | Read; change only when Arek asks |
| `thesis/` | Thesis text (Polish), private and git-ignored: table of contents, its sources, LaTeX drafts in `thesis/latex/` (see `thesis/CLAUDE.md`) | Edit only when Arek asks; never commit or publish |
| `docs/` | Project knowledge: decision log, open questions, plans, dated reference documents (mostly Polish) | Read; append to `decisions.md` / `open_questions.md` |
| `knowledge/` | What the thesis rests on (see `knowledge/CLAUDE.md`): `advisor/` private correspondence, `sources/` article PDFs with `sources_index.md`, `findings/` dated notes on what was found out | Add findings and index rows; `advisor/` and the PDFs are git-ignored and read only |
| `dataset_research/` | Exploratory research from Oct 2026 (domain choice, sanity checks, first downloads) | Read only |
| `dataset_research/space_weather_decision/` | GO decision report, catalogues downloaded 2026-10-10, backtests | Read only; `data/MANIFEST_D*.md` give provenance |
| `README.md` | The map of the repo for people | Keep it in step with this table |

Each folder type follows published conventions (sources and deliberate exceptions: `docs/repository_conventions.md`).
New files follow them: lower_snake_case names, ISO dates (`YYYY-MM-DD`) in dated file names, a `README.md` row for
every new file in a top-level folder.

Paths that automation depends on (do not move or rename without re-registering the task and re-running the checks in
`code/ingestion/CLAUDE.md`): `code/ingestion/scripts/noaa_live_task.cmd` (absolute path stored in Windows Task
Scheduler), the depth of `code/ingestion/src/swx_ingest/store.py` below the repo root (default data dir), `data/`,
and the depth of `evaluation/event_set/` (the build script finds `data/normalized/gfz_kp` two levels up).

Key numbers from `dataset_research/space_weather_decision/README.md` that the code should reproduce or beat:
100 % of G3+ storms 2010–2026 have a catalogued cause (random windows 32 %); Kp-only analogues add no skill over
climatology by onset level (Brier skill 0.095); adding a shock flag gives 0.131 (measured with SSC, now answer key;
re-measure with DONKI IPS). Analogues must use driver features, not Kp shape alone: solar wind in every variant;
shock (DONKI IPS), CME speed and driver type only in C and C-decision.

## How to work here

- **Context first.** This file plus the `CLAUDE.md` of the folder you touch are loaded automatically. Then read only
  the doc that matches the task (`docs/README.md` says which). Do not bulk-read `dataset_research/`.
- **Teach the domain, skip the RAG basics.** Arek is strong in RAG and multi-agent systems and new to time series and
  space weather. When a choice rests on physics or time-series methodology (leakage, skill scores, resampling,
  storm definitions), explain it in 1–3 sentences with a source. Don't explain embeddings, chunking or agents.
- **Plan, then build in small verified steps.** For anything beyond a small fix, state the plan first. Run the tests
  or the script and show the evidence. Say plainly what you did not verify.
- **Stop and ask** before touching an invariant above, adding a data source, changing the event set, or doing anything
  that costs money or is hard to undo (bulk downloads of many GB, deleting data, publishing anything).
- **Record what you find.** Before the final message, write anything a later session would have to rediscover
  into `knowledge/findings/` (one dated note, template in its `README.md`). Knowledge must not get lost (Arek).
- **Never invent** URLs, endpoints, dataset IDs, numbers or citations. Mark anything not tried as "untested".
- **Language.** Code, comments, commit messages, logs and these CLAUDE.md files: English. Anything for the advisor or
  the thesis text: Polish. End-user explanations from the platform: Polish, with quoted sources in the original
  language (usually English).
- **What may be public.** The GitHub repo is public. Code and project docs may be pushed; the thesis text
  (`thesis/`), advisor correspondence (`knowledge/advisor/`) and article files (`knowledge/sources/`) may not
  (Arek, 2026-11-14). They are git-ignored: never force-add them, and do not copy thesis passages, chapter text
  or the table of contents into a tracked file.
- **Secrets.** Never write credentials into the repo. Earthdata uses `C:\Users\areka\_netrc`; other keys come from
  environment variables. Space-Track data may not be redistributed: keep raw TLEs out of anything shared.
- **Python 3.14 only, and uv only inside `code/`** (Arek, 2026-11-14). The repo root holds no `pyproject.toml`,
  lockfile or virtual environment: never run `uv init`, `uv add` or `uv sync` outside `code/`. The pin is enforced
  through `code/.python-version` and `requires-python` (details in `code/CLAUDE.md`).
- **Machine.** Windows laptop, repo inside OneDrive. Use `pathlib`, no hard-coded separators. Long-running jobs run
  via Windows Task Scheduler. If OneDrive sync interferes with data files, point `SWX_DATA_DIR` at a
  non-synced folder (see `code/CLAUDE.md`).

## Keeping these instruction files current

Full guide: `docs/claude_md_guide.md`. Short version, which every agent follows:
- **Update in the same change** as the code or decision that made the text stale. A stale CLAUDE.md is worse than none.
- **Put each fact in exactly one place**, the most specific file that covers it: root = cross-cutting rules and the
  research design; `code/CLAUDE.md` = shared code conventions; `code/<part>/CLAUDE.md` = that part only. Link to
  `docs/` rather than copying long content.
- **Triggers:** a new command, dependency or layout → update the matching file. Arek decides something → one dated
  entry in `docs/decisions.md`, then fix every line it affects. Arek corrects an agent, or the same mistake happens
  twice → add a one-line rule where it would have prevented it. An open question gets answered → move it from
  `docs/open_questions.md` to `docs/decisions.md`.
- **The "Research design" section changes only with Arek's explicit OK.** Propose the edit in chat instead.
- **Style:** imperative, specific, checkable ("Store timestamps as tz-aware UTC"), not vague ("handle time well"). No
  history or narration here; history lives in `docs/decisions.md` and git.
- **Size:** keep this file under 200 lines and each subfolder file under 150. When a file grows past that, move detail
  into `docs/` and link to it.
- **Report it.** When you change any CLAUDE.md, say which lines changed in your final message to Arek.
