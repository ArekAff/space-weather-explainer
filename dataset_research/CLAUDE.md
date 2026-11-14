# dataset_research/: rules for agents

Archive of the exploratory research of October 2026 that led to the topic. Read only.

- Do not edit, move, rename or delete anything here. `evaluation/event_set/zestaw_zdarzen_build.py` reads
  `space_weather_decision/results/` and `space_weather_decision/data/` by file name, and the manifests record
  provenance by path.
- Do not bulk-read this folder. Start from `README.md` (domain comparison) or `space_weather_decision/README.md`
  (GO decision, sanity checks, backtests) and open only what the task needs.
- `space_weather_decision/data/` holds answer-key catalogues (Richardson–Cane, SSC, NOAA proton events): evaluation
  only, never input for the system (root `CLAUDE.md`, invariant 1). The data files are git-ignored; provenance is in
  `MANIFEST_D1.md` and `MANIFEST_D2.md`.
- The Kp file in `space_weather_decision/results/` is a merged, rounded series without status. New code uses
  `data/normalized/gfz_kp` instead (`code/ingestion/CLAUDE.md`).
- Scripts here are research one-offs, not project code: reuse their request patterns in `code/ingestion`, do not
  import them. `samples/` keeps only `SOURCE.md` notes in git; the data is re-fetched with `scripts/`.
- New research does not go here. Put new documents in `docs/` and new code in `code/`.
