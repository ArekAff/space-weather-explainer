# code/platform/: the explanation system (package `swx_platform`)

Turns the data store into cited explanations and evaluates them. Reads only `normalized/`, `corpus/` and (evaluation
only) `answer_key/` from the data store in `code/CLAUDE.md`. Never calls a data source over the network.

Design references: `docs/metodologia/z_czym_porownac.md` (variants and metrics), `docs/metodologia/zestaw_zdarzen_zasady.md`
(event set and answer key), `docs/rag/projekt_korpusu_rag.md` (corpus, time cut-off, metadata, citations),
`dataset_research/space_weather_decision/README.md` (what the first experiments showed).

## Pipeline

```
moment (detected or user-marked, with t0)
  → detect / describe   (series state at t0)
  → analogues           (similar past situations + what followed)
  → catalogue links     (variants B, C)
  → retrieval           (variant C)
  → explanation         (LLM, Polish, every claim cited)
  → evaluation          (against the answer key; never fed back)
```

- **One pipeline, three variants.** A, B and C are one code path with a knowledge-access setting, not three programs.
  Anything that differs between variants other than knowledge access is a bug in the experiment.
- **One gate for time.** All reads go through a single access layer that takes `as_of=t0` and applies the cut-off:
  `issued_at <= t0` for texts, `submissionTime <= t0` for DONKI entries, no retrospective DONKI notes in the main mode.
  Retrieval, catalogue lookups and analogue search must not bypass it. Test it with a planted future document.
- **Answer key isolation.** Only `evaluation/` may import the answer-key loader. Add a test that fails if any other
  module imports it.

## Component notes

- Detection: the baseline from the research is robust z ≥ 3 on log(ap+1) against the median and IQR of the previous
  27 days. For space weather "anomaly" mostly means "storm", so the added value is quiet-time anomalies,
  data-quality flags and later forecast misses.
- Analogues: the windows' continuation must end before t0. Use driver features (solar wind, Bz, CME speed, shock flag
  from DONKI IPS), not Kp shape alone. Benchmark to beat: climatology by onset level + shock flag (Brier skill 0.131).
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

- Event set: `docs/metodologia/zestaw_zdarzen_ewaluacja.csv` (v2: 157 events, 88 DEV / 69 TEST, `zbior` = DEV/TEST, `t0_utc`,
  `okres_korpusu`). Develop on DEV. TEST runs once, at the end, with Arek's go-ahead.
- Accuracy: cause class accuracy and F1 (CME / high-speed stream / radiation / not space weather) against
  Richardson–Cane; onset time error against SSC; effect agreement against TEC/ROTI and orbit decay; share of jamming
  cases correctly called "not space weather". The 7 storms marked SPORNE are reported separately or excluded, and the
  run says which.
- Documentation: share of claims with a citation, share of citations that support their claim (manual sample or LLM
  judge with manual checks), hallucination rate.
- Statistics: paired tests on the same events (McNemar for accuracy, Wilcoxon for ratings).
- Every run writes to `runs/<timestamp>_<variant>/`: config, git commit, model ID, prompt version, seed, per-event
  outputs, metrics. Results go into the thesis only from runs on frozen data.
