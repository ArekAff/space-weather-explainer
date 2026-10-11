@echo off
rem One NOAA SWPC live collection run, for Windows Task Scheduler (see code/ingestion/CLAUDE.md).
rem Output goes to <data dir>/logs/noaa_live.log; the exit code is 1 if any fetch failed.
cd /d "%~dp0..\.."
uv run --frozen --quiet swx-noaa-live
