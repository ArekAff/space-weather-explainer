# code/platform/: the early-warning system (package `swx_platform`)

Turns the data store into a daily early warning (the most probable incident type from the catalogue, decision
2026-11-13) and evaluates the scenarios. Reads only `normalized/`, `corpus/` and (evaluation
only) `answer_key/` from the data store in `code/CLAUDE.md`. Never calls a data source over the network.

Design references: `docs/metodologia/z_czym_porownac.md` (variants and metrics), `docs/metodologia/zestaw_zdarzen_zasady.md`
(event set and answer key), `docs/rag/projekt_korpusu_rag.md` (corpus, time cut-off, metadata, citations),
`dataset_research/space_weather_decision/README.md` (what the first experiments showed).

## Pipeline

```
moment (detected or user-marked, with t0)
  → detect / describe   (series state at t0)
  → analogues           (similar past situations + what followed)
  → catalogue links     (C, C-decision)
  → retrieval           (C, C-decision)
  → decision            (incident type from the catalogue: classic LLM in A and C, decision model in C-decision)
  → evaluation          (against the answer key; never fed back)
```

- **One pipeline, three scenarios.** A, C and C-decision are one code path with a knowledge-access setting and a
  decider setting (classic LLM or decision model), not three programs. Anything else that differs between scenarios
  is a bug in the experiment. Variant B was dropped on 2026-11-13.
- **One gate for time.** All reads go through a single access layer that takes `as_of=t0` and applies the cut-off:
  `issued_at <= t0` for texts, `submissionTime <= t0` for DONKI entries, no retrospective DONKI notes in the main mode.
  Retrieval, catalogue lookups and analogue search must not bypass it. Test it with a planted future document.
- **Answer key isolation.** Only `evaluation/` may import the answer-key loader. Add a test that fails if any other
  module imports it.

## Data available (audit 2026-10-12)

- `normalized/gfz_kp` (Kp and ap 3-hourly, Ap, `sn`, `f107_obs`, `f107_adj` daily; from 1932), `gfz_hp30` (from 1985),
  `omni2_hourly` (47 quantities from 1963, incl. `dst`, `ae`/`al`/`au`, `pcn`), `noaa_swpc_*` (live, `realtime`,
  from 2026-10-04). Read the latest `version` per key; `status_basis` says why a value has its status.
- OMNI2 lags 2–4 weeks. Where it has no data, take solar wind from `noaa_swpc_solar_wind` and record per feature
  which source it came from. Proton flux: OMNI2 ends 2020-03-04 and NOAA live starts 2026-10-04 (open question).
- Event set: only `id`, `t0_utc` and `stacja` may reach the system; `zbior` and `okres_korpusu` only select and group
  runs. Every other column is answer key or describes what happened after t0.
- DONKI catalogue entries arrive late (05/2024 IPS: median 77 h after the shock; 2012 entries: 1.2–11 years later),
  so under the gate C sees almost no catalogue for P1 events. C's shock flag comes from IPS alerts (notifications,
  gated on `messageIssueTime`; decision 2026-10-12).
- Coverage of the 72 h before t0: Kp and Hp30 complete for all 157 v2 events, solar wind at least 90 % for 146 (checked before B161 was added). The
  readiness audit lists the 11 others: https://claude.ai/code/artifact/86adc040-9fb4-46d0-8978-736e84f031b2

## Component notes

- Detection: the baseline from the research is robust z ≥ 3 on log(ap+1) against the median and IQR of the previous
  27 days. For space weather "anomaly" mostly means "storm", so the added value is quiet-time anomalies,
  data-quality flags and later forecast misses.
- Analogues: the windows' continuation must end before t0. Use driver features, not Kp shape alone. Variant A matches
  on numeric features only (Kp/Hp30, solar wind speed, density, Bz; a shock detected from these numbers is numeric).
  C and C-decision add DONKI filters (shock from IPS alerts, CME speed, driver type) through the time gate. Benchmarks: A, climatology
  by onset level (Brier skill 0.095); C and C-decision, climatology by level + shock flag (0.131 with SSC; re-measure with IPS).
  Report skill scores against climatology and persistence, never raw accuracy.
- Retrieval: chunk along product sections (Forecast Discussion and RSGA sections, one DONKI notification per chunk,
  review papers by subsection with page). Mask background chunks that mention the tested event (date within ±3 days,
  storm name, NOAA region number, DONKI ID) and count masked chunks per event. Queries in English, multilingual
  embeddings.
- Explanation: written in Polish; quotes stay in the original. Citation format:
  `[NOAA SWPC, Forecast Discussion, 2024-05-10 12:30 UTC, sekcja Geospace]` plus the URL. A claim without a citation is
  allowed only in variant A and must be marked as inference.
- LLM calls: model ID and prompt version come from config and are saved with every output. Cache responses by
  (model, prompt version, input hash) so reruns are cheap and reproducible.

## Evaluation rules

- Criteria (advisor, 2026-11-13): quality (correct incident type), cost and time per daily analysis. How each is
  scored, and whether the explanation text stays, is open (`docs/open_questions.md`); the metrics below predate that
  decision and still apply to cause and effect keys.

- Event set: `docs/metodologia/zestaw_zdarzen_ewaluacja.csv` (v3: 158 events, 96 DEV / 62 TEST; May 2026 jamming J132–J139 are DEV, `zbior` = DEV/TEST, `t0_utc`,
  `okres_korpusu`). Develop on DEV. TEST runs once, at the end, with Arek's go-ahead.
- Accuracy: cause class accuracy and F1 (CME / high-speed stream / radiation / not space weather) against
  Richardson–Cane; onset time error against SSC; effect agreement against TEC/ROTI and orbit decay; share of jamming
  cases correctly called "not space weather". The 7 storms marked SPORNE are reported separately or excluded, and the
  run says which.
- Documentation: share of claims with a citation, share of citations that support their claim (manual sample or LLM
  judge with manual checks), hallucination rate.
- Statistics: paired tests on the same events (McNemar for accuracy, Wilcoxon for ratings).
- Every run writes to `runs/<timestamp>_<scenario>/`: config, git commit, model ID, prompt version, seed, per-event
  outputs, metrics. Results go into the thesis only from runs on frozen data.
