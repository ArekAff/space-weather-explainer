# space-weather-explainer: real-time space-weather platform with cited, expert-grounded explanations

SGH master's thesis (Analiza danych – Big Data) by Arek (Arkadiusz Affek), advisor Prof. Surma.
Working title (PL): „Platforma analizy szeregów czasowych w czasie rzeczywistym z objaśnieniami opartymi na wiedzy
eksperckiej (RAG) na przykładzie wpływu pogody kosmicznej na pozycjonowanie GNSS i pracę satelitów”.

The platform watches space-weather time series, detects unusual moments (or takes a moment the user marks), finds
similar past situations and what followed, links the moment to catalogued causes, retrieves expert texts from that
time (RAG), and writes an explanation in which every claim cites a source. Users: precision GNSS positioning
(mainly precision agriculture in Poland) and satellite operators.

## Research design (do not change without Arek's explicit OK)

Research question: does real-time data analysis plus expert knowledge (catalogues and RAG) give more accurate and
better documented explanations than numeric data alone? Same events, variants differ only in knowledge access:

| Variant | Gets | Role |
|---|---|---|
| A | Numeric series + detected anomalies only | Baseline from the research question |
| B | A + event catalogues (DONKI structured fields, proton events) | Separates the catalogue effect from RAG |
| C | B + RAG over expert texts, with citations | The platform |
| D (optional) | NOAA forecaster's own text | External ceiling, only from 03/2024 |

Invariants. Breaking one silently invalidates the thesis:
1. **The answer key never reaches the system.** Richardson–Cane ICME list, SSC list (ISGI/Ebre), effect data (IGS
   TEC/ROTI, EPN, orbital elements), GUGiK notices about specific jamming cases, and case-study papers about test
   events are used only by evaluation code.
2. **Shock-arrival feature comes from DONKI IPS**, never from SSC (SSC is answer key).
3. **Time cut-off.** A document or catalogue entry is visible for event *e* only if `issued_at <= t0(e)`. Publication
   time counts, not the period described. Date-only timestamps count as 23:59 UTC. This applies to catalogues in B
   and C too (DONKI `submissionTime`), not only to RAG.
4. **DONKI notes before 06/2020 were added retroactively**: mark `is_retrospective = true`; excluded in the main mode.
5. **DEV/TEST split.** TEST = events from 2025-01-01 (43 of 131). Tune prompts, thresholds and retrieval on DEV only;
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

Full rationale: `docs/README.md` (index), decisions in `docs/decisions.md`, unresolved items in `docs/open_questions.md`.

## Repository map

| Path | What it is | Agents may |
|---|---|---|
| `code/` | All application code (see `code/CLAUDE.md`) | Create and edit |
| `code/ingestion/` | Data ingestion pipeline: collectors, raw archive, normalised tables, corpus | Create and edit |
| `code/platform/` | The system: detection, analogues, catalogues, RAG, explanations, evaluation | Create and edit |
| `docs/` | Reference documents copied from the Claude project (mostly Polish) plus decision log | Read; append to `decisions.md` / `open_questions.md` |
| `dataset_research/` | Exploratory research from Oct 2026 (domain choice, sanity checks, first downloads) | Read only |
| `dataset_research/space_weather_decision/` | GO decision report, catalogues downloaded 2026-10-10, backtests | Read only; `data/MANIFEST_D*.md` give provenance |
| `maile_surma/` | Advisor e-mails (PDF) | Read only |
| `README.md`, `main.py`, `pyproject.toml` | Arek's root files (uv project stub) | Do not edit unless Arek asks |

Key numbers from `dataset_research/space_weather_decision/README.md` that the code should reproduce or beat:
100 % of G3+ storms 2010–2026 have a catalogued cause (random windows 32 %); Kp-only analogues add no skill over
climatology by onset level (Brier skill 0.095); adding a shock flag gives 0.131. Analogues must use driver features
(solar wind, CME speed, shock), not Kp shape alone.

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
- **Never invent** URLs, endpoints, dataset IDs, numbers or citations. Mark anything not tried as "untested".
- **Language.** Code, comments, commit messages, logs and these CLAUDE.md files: English. Anything for the advisor or
  the thesis text: Polish. End-user explanations from the platform: Polish, with quoted sources in the original
  language (usually English).
- **Secrets.** Never write credentials into the repo. Earthdata uses `C:\Users\areka\_netrc`; other keys come from
  environment variables. Space-Track data may not be redistributed: keep raw TLEs out of anything shared.
- **Python 3.14 only**, enforced through `.python-version` and `requires-python` (details in `code/CLAUDE.md`).
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
