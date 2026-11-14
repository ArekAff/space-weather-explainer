# space-weather-explainer

Master's thesis project (SGH, Analiza danych – Big Data; advisor Prof. Surma). A platform that watches the
space-weather situation with real-time data analysis and once a day issues an early warning: the most probable
incident type for satellites and GNSS positioning. The thesis compares a classic LLM with RAG against a decision
model on cost, quality and time.

## Where things are

| Folder | What you do there | Start with |
|---|---|---|
| `code/` | Write and run code: data collectors (`ingestion/`) and the platform itself (`platform/`) | `code/README.md` |
| `data/` | Nothing by hand. The collectors write here (not in git, about 180 MB) | `code/CLAUDE.md`, "Data store" |
| `evaluation/` | Look up or rebuild what the system is scored against: the 158 evaluation events and their answer key | `evaluation/README.md` |
| `thesis/` | Write the thesis: table of contents, its sources, LaTeX drafts (private, not in git) | `thesis/README.md` |
| `docs/` | Check what was decided, what is open, and the design documents (methodology, data sources, RAG corpus) | `docs/README.md` |
| `knowledge/` | Keep what the thesis rests on: advisor e-mails (`advisor/`, private), article PDFs to read and cite (`sources/`), dated notes on what was found out (`findings/`) | `knowledge/README.md` |
| `dataset_research/` | Look back at the October 2026 research that led to the topic (archive, read only) | `dataset_research/README.md` |

Root files: `CLAUDE.md` holds the research design and the rules for AI agents; every folder above has its own
`CLAUDE.md` with the rules for that folder. There is no Python project in the root: `uv` is used only inside
`code/`.

## Everyday commands

Run from `code/` (Python 3.14 through `uv`):

```
uv sync                 # create the environment
uv run pytest           # tests
uv run swx-noaa-live    # one NOAA live collection run (also runs every 30 min from Windows Task Scheduler)
uv run swx-gfz          # re-pull GFZ Kp and Hp30 history
uv run swx-omni         # re-pull OMNI2 hourly history
```

The scheduled task is "NOAA SWPC live collector" in the Task Scheduler folder `\space-weather-explainer\`. Its log is
`data/logs/noaa_live.log`. Do not move `code/` or `data/` without reading "Paths that automation depends on" in
`CLAUDE.md`.

## Rules worth knowing before you change anything

- The answer key (everything in `evaluation/` except event `id`, `t0_utc` and `stacja`) must never reach the system.
- Tune on DEV events only; the TEST events run once, at the end.
- Anything found out while working is written down in `knowledge/findings/`, so it is not lost.
- Decisions are logged in `docs/decisions.md`; open points are in `docs/open_questions.md`.
- Why each folder is laid out the way it is, with sources: `docs/repository_conventions.md`.
