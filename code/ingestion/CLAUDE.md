# code/ingestion/: data ingestion pipeline (package `swx_ingest`)

Fetches every source, archives raw responses unchanged, and writes normalised tables, the text corpus and the answer
key into the data store described in `code/CLAUDE.md`. This is the only part allowed to use the network.

Source of truth for what to fetch: `docs/data_gathering_plan.md` (English summary of the project's plan) and
`docs/zrodla_danych/` (access table, download notes, accounts). Already downloaded once:
`dataset_research/space_weather_decision/data/` with provenance in `MANIFEST_D1.md` and `MANIFEST_D2.md`. Reuse
the request patterns from there; do not copy those files into the store without recording them in the manifest.

## Build order

1. **NOAA SWPC live collector** (`sources/noaa_swpc.py`, built 2026-10-11). Most urgent: the live files keep 1–7 days,
   so a missed day is gone for good. Runs unattended every 30 min (Windows Task Scheduler) and backfills from the 7-day
   files after the laptop was off. RTSW 1-min files keep only ~24 h, so their minute data survive only daily runs.
2. Historical series: GFZ Kp/ap/Ap since 1932 with status, full Hp30, OMNI2 hourly since 1963.
3. DONKI events (CME, FLR, SEP, HSS, MPC, IPS, GST) as raw JSON, in windows of at most 60 days.
4. Corpus: NOAA SWPC texts from the NCEI archive, DONKI notifications and notes, open review papers.
5. Answer key: Richardson–Cane, SSC, NOAA 3-day forecasts, IGS TEC (final), Space-Track history, jamming cases,
   ASG-EUPOS RINEX (Polish stations).
6. Freeze job: re-pull all catalogues, write `freeze/<date>/` with a manifest.

## Status (checked 2026-10-11 20:42 UTC)

Update this section whenever a build-order step starts or finishes, or the collector's health changes.
- Step 1 done: `sources/noaa_swpc.py` plus 18 unit tests (tests not re-run in this check). Store contents verified:
  8 normalised tables, all `status = realtime`, all required provenance columns present; 49 raw files in
  `raw/manifest.parquet`; 3 text issues indexed (3-day forecast and discussion issued 2026-10-11 12:30 UTC).
  Coverage starts: solar_wind, kp_3h and GOES protons 2026-10-04 (7-day backfill), ACE 1h 2026-09-11,
  RTSW 2026-10-10 17:38, kp_1m 2026-10-11 11:39. Gap log holds only source-side `no_data` intervals and the two
  404s from the retired `products/solar-wind/*` files.
- Scheduler not yet confirmed: the log shows manual runs 17:40–17:47 and 20:22–20:35 UTC (none in between) and one
  run at 20:37 UTC, which matches the 30-min task slots (:07 and :37 local time). Confirm with steady runs in
  `data/logs/noaa_live.log`; if they stop after a day, check the trigger's repetition duration.
- Deliberate deviation from the Polish plan: one 30-min cadence for all products instead of 5 min for wind and alerts.
  No data is lost because every short file covers more than 30 min.
- Steps 2–6 not started: `noaa_swpc.py` is the only source module. Next: step 2 (GFZ, Hp30, OMNI2).
- Data store is inside OneDrive (`<repo>/data`, 3.6 MB so far). Move `SWX_DATA_DIR` out if sync locks files.

## NOAA collector rules

Endpoints are the `PRODUCTS` list in `sources/noaa_swpc.py`; tested results are in `docs/data_gathering_plan.md`.
Run once: `cd code; uv run swx-noaa-live` (exit code 1 if any fetch failed). Task Scheduler: register with
`ingestion/scripts/register_noaa_task.ps1`, which runs `ingestion/scripts/noaa_live_task.cmd`.
- Save every response raw (gzipped), named with the UTC fetch time, plus SHA-256. If the hash equals the previous
  one, write only a log line.
- Each product family has one table (the short and 7-day files feed the same table). Rows are keyed by
  (`time_utc`, quantity, `qualifier`); a later fetch adds a version only when the value changed and never overwrites.
  `source_file` is the raw archive path. RTSW has rows for several spacecraft per minute (seen 2026-10-11: SOLAR1
  active, ACE, IMAP), so `spacecraft` and `active` are kept and the spacecraft is part of `qualifier`.
- Treat RTSW `-9999` as a fill value (NaN). `products/solar-wind/*` no longer exists (404 on 2026-10-11); solar wind
  comes from `products/geospace/propagated-solar-wind*.json`, whose arrival-at-Earth time is stored as
  `propagated_time_tag_delay_min`.
- Text products (`3-day-forecast.txt`, `discussion.txt` and similar): parse `:Issued:` into `issued_at` in
  `raw/noaa_swpc/text_index.parquet`. Save only when the content changes. Forecasts (texts and the Kp forecast) are
  answer-key material: archive them raw, never under `normalized/` or `corpus/`.
- Gap log `raw/noaa_swpc/gap_log.csv`: kinds `fetch_failed`, `parse_failed`, `no_data` (interval missing in the
  source) and `lost_before_coverage` (collector off longer than the file keeps). The 7-day file is fetched when the
  short file does not reach back to the last stored time, when nothing is stored, and once a day.
- Files whose history far exceeds the run interval (RTSW ~24 h, ACE 1h ~30 days, GOES 1-day) are fetched at most
  every 6 h (`min_interval_h` on the product), so runs do not re-archive near-identical multi-MB copies.
- Status of everything from this collector is `realtime`. Never merge it into the historical GFZ/OMNI tables.

## Source-specific gotchas

- GFZ: values go nowcast → `pre` → `def` about monthly; store `status`. The merged Kp file in
  `dataset_research/.../results/` uses CelesTrak before 2025-07-20 (no status, Kp rounded to 0.1); replace that part
  with GFZ data. The Hp30 API returns no status, so record the Hpo version (currently V3.0).
- Hp30 start (1985 or 1995) and Kp start (1932 or 1957) are open questions: see `docs/open_questions.md`.
- OMNI: fill values are runs of 9s (999.9, 9999.99 and so on), per `omni2.text`. Dst from 2021 is provisional; AE has no
  status. Store flags. HAPI parameters must stay in the documented order, or the server returns error 1411.
- DONKI: records carry `versionId` and get revised; keep every version. Store `submissionTime` (it drives the time
  cut-off). Entries before 06/2020 are retrospective. Bulk CME pulls are large (10,266 CMEs for 2010–2026).
- NOAA proton events (NGDC list): current to 2026-07-30, has known date typos (see the manifest). The correction in
  `docs/zrodla_danych/weryfikacja_maila.md` claiming the list ends in 2011 is wrong (see `docs/decisions.md`).
- NCEI texts: parse issue time from headers. Date-only means 23:59 UTC. Old RSGA (before 1996) may need OCR; test a
  sample before committing to it.
- ASG-EUPOS RINEX (https://system.asgeupos.pl/) is answer key only (`answer_key/`). Account requirement and archive
  depth are untested; check before writing the fetcher.
- IGS TEC needs NASA Earthdata (`_netrc`); use the final product, not rapid. Space-Track needs an account, and its
  data must not be redistributed.
- SSC and the Belsk magnetometer are CC BY-NC 4.0. Fine for the thesis; keep the attribution in the manifest.

## Code rules for this part

- Every fetcher is idempotent and resumable: re-running a day must not duplicate rows.
- Be polite: set a descriptive User-Agent, back off on errors (exponential, capped), never hammer an endpoint in tests.
- One module per source (`sources/noaa_swpc.py`, `sources/gfz.py` and so on), sharing one raw-archive writer and one
  manifest writer.
- Answer-key sources write only under `answer_key/`. A test should assert that no answer-key dataset appears under
  `normalized/` or `corpus/`.
- Each source gets a short entry in `docs/data_gathering_plan.md` once it works: endpoint, cadence, row count, quirks.
