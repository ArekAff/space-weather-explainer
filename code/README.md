# code/: all application code

A `uv` workspace (Python 3.14). Run every command from this folder.

| Path | What it is |
|---|---|
| `ingestion/` | Package `swx_ingest`: the only code that talks to the network. Collectors for NOAA SWPC live data, GFZ Kp/Hp30 and OMNI2; raw archive; normalised tables |
| `ingestion/src/swx_ingest/sources/` | One module per data source |
| `ingestion/tests/` | Unit tests with recorded responses in `tests/fixtures/` (no network) |
| `ingestion/scripts/` | Windows Task Scheduler wrapper for the NOAA collector and the script that registers it |
| `platform/` | Package `swx_platform`: the early-warning system and its evaluation. No code yet; the design is in `platform/CLAUDE.md` |
| `pyproject.toml`, `uv.lock` | Workspace definition and locked dependencies |

```
uv sync                 # create .venv
uv run pytest           # tests
uv run ruff check --fix # lint
uv run ruff format      # format
uv run swx-noaa-live    # one NOAA live run; log in ../data/logs/noaa_live.log
uv run swx-gfz          # GFZ history
uv run swx-omni         # OMNI2 history
```

The collectors write to `../data/` unless the environment variable `SWX_DATA_DIR` points elsewhere. Conventions,
the data-store layout and the rules for each part are in `CLAUDE.md`, `ingestion/CLAUDE.md` and `platform/CLAUDE.md`.

The scripts that build the evaluation event set are not here: they live next to their data in
`../evaluation/event_set/`.
