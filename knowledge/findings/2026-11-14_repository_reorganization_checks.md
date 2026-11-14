# Only four things in this repo depend on file paths, and all still work after the reorganization

- Date: 2026-11-14
- Found by: agent, while reorganizing the repository by function
- Status: current

## What was checked and how

- Windows Task Scheduler listed with `Get-ScheduledTask` (all non-Microsoft tasks).
- `grep` over the repo for every moved folder name; the scripts in `code/ingestion/scripts/`; `store.py`.
- User and machine environment variables for `SWX_DATA_DIR`.
- `Test-Path C:\Users\areka\magisterka`.
- Event-set build run into a copy before and after the move; `uv run pytest`; log of the scheduled run.

## Result

- The only scheduled automation is the task "NOAA SWPC live collector" in `\space-weather-explainer\`. It stores
  the absolute path `...\magisterka\code\ingestion\scripts\noaa_live_task.cmd`. The script changes to `code/` and
  runs `uv run --frozen --quiet swx-noaa-live`.
- `SWX_DATA_DIR` is not set, so the data store is `<repo>/data`, computed from the position of
  `code/ingestion/src/swx_ingest/store.py` (four folders below the repo root).
- `evaluation/event_set/zestaw_zdarzen_build.py` finds its inputs next to itself and `data/normalized/gfz_kp` two
  folders up.
- There is no second copy of the project at `C:\Users\areka\magisterka` (the path does not exist).
- After the move: the scheduled run of 13:37 UTC ended with 9 files and 0 failures; 34 tests passed; the build
  reproduced `zestaw_zdarzen_ewaluacja.csv` exactly (ignoring CRLF/LF); `rtgms_parse.py` reproduced
  `rtgms_alarmy_2026.csv`; `zestaw_zdarzen_xlsx.py` ran (158 events).
- `openpyxl` is not installed in `code/.venv`, so the XLSX script needs `uv run --with openpyxl`.
- The working-tree copy of the event CSV has LF line endings while the build writes CRLF on Windows; compare
  rebuilds with line endings ignored.
- The GitHub repository `ArekAff/space-weather-explainer` is public (`gh repo view`, 2026-11-14).
- `git log --all --name-only` lists no path under `thesis`, `praca_magisterska`, `email_promotor`, `maile_surma`
  or `advisor`, and no `.pdf`, `.pptx` or `.tex` file: nothing private was ever committed or pushed. `origin/main`
  is 7 commits behind the local `main`.

## What it means for the project

`code/` and `data/` were left where they are, so nothing had to be re-registered. The rule is in the root
`CLAUDE.md` ("Paths that automation depends on"); the layout decision is in `docs/decisions.md` (2026-11-14).
Untested: a fresh clone on another machine.
