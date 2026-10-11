# Decision log

Newest at the bottom. One entry per decision: date, decision, why, and which files it affects. A later entry wins over
an earlier one and over any snapshot document in `docs/`. Only Arek decides; agents record what he decided.

## 2026-10-10

- **Domain: space weather (GO).** Best technical fit among candidates; 100 % of G3+ storms 2010–2026 link to a
  catalogued cause. Source: `dataset_research/space_weather_decision/README.md`.

## 2026-10-11

- **Users: GNSS precision positioning (mainly precision agriculture) and satellite operators.** Power grids stay as
  motivation only. Gap: no open satellite-anomaly data, so satellite effects are checked on orbit decay (Space-Track,
  CelesTrak). Source: `obszar_biznesowy/porownanie_obszarow.md`.
- **Research question and variants A (numeric only), B (plus catalogues, optional), C (plus RAG with citations)**, as
  sent to Prof. Surma. Optional D = NOAA forecaster text (from 03/2024). Source: `email_promotor/odpowiedz_prof_surma_final.txt`.
- **Richardson–Cane ICME list and SSC list are answer key only** and never enter the system.
- **Shock-arrival feature comes from DONKI IPS, not SSC.** Supersedes the e-mail, which used SSC for both.
  Affects: `email_promotor/odpowiedz_prof_surma_final.txt` §4b (SSC paragraph), `rag/projekt_korpusu_rag.md` §2.
- **Time cut-off: a document or catalogue entry is visible only if `issued_at <= t0`.** Also applies to catalogues
  in B and C. Date-only timestamps count as 23:59 UTC. Source: `rag/projekt_korpusu_rag.md` §3.
- **DONKI notes before 06/2020 are retrospective** and excluded in the main mode.
- **Evaluation event set: 131 events 04/2010–10/2026; TEST = events from 2025-01-01 (43), DEV = 88.** Corpus periods:
  before 06/2020, 06/2020–02/2024, from 03/2024. Source: `metodologia/zestaw_zdarzen_zasady.md`.
- **Data freeze 2026-12-31 for test events; final catalogue re-pull in Feb 2027.** Proposed default in the data
  gathering plan; will change if the advisor sets another date.
- **Correction: the NGDC proton-event list is current (to 2026-07-30).** The link in the advisor e-mail is correct.
  Supersedes `zrodla_danych/weryfikacja_maila.md` §1.5, which said the table ends in 03/2011.
- **The NOAA live collector is the most urgent piece of code** (live files keep only 1–7 days).
- **Repository conventions for agents:** CLAUDE.md files in English, `code/ingestion` and `code/platform` as separate
  packages (`swx_ingest`, `swx_platform`), data store outside git under `MAGISTERKA_DATA_DIR`. Defaults chosen when the
  CLAUDE.md files were created; Arek can override them.
- **Python 3.14 for all project code (Arek asked to leave 3.10 for the newest recommended version).** 3.10 reaches end
  of life in Oct 2026. 3.15 had only just been released (scheduled 2026-10-09), and big binary packages (torch for
  embeddings, and others) usually take months to ship wheels for a new version. 3.14 (Oct 2025) is supported by
  numpy, pandas, pyarrow, duckdb, scipy, scikit-learn and torch. Enforced with `.python-version` = `3.14` and
  `requires-python = ">=3.14,<3.15"` in every `pyproject.toml`. Revisit 3.15 after the thesis data freeze, not before.
  Affects: `.python-version`, `pyproject.toml`, `CLAUDE.md`, `code/CLAUDE.md`.
- **Project name is `space-weather-explainer` everywhere (Arek).** GitHub repo `ArekAff/space-weather-explainer`
  (private); a fresh clone gets that folder name, so tracked files must not say "magisterka". The data-dir env var
  is now `SWX_DATA_DIR` (was `MAGISTERKA_DATA_DIR`) and the scheduled task lives under `\space-weather-explainer\`.
  The local working folder on Arek's laptop may keep its old name. Affects: `pyproject.toml`, `CLAUDE.md`,
  `code/CLAUDE.md`, `code/ingestion` (store, collector, register script), `docs/claude_md_guide.md`.
