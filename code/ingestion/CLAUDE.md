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
2. **Historical series** (`sources/gfz.py`, `sources/omni.py`, built 2026-10-11): GFZ Kp/ap/Ap since 1932 with
   status, full Hp30, OMNI2 hourly since 1963. Run by hand monthly and before the freeze; not scheduled.
3. DONKI events (CME, FLR, SEP, HSS, MPC, IPS, GST) as raw JSON, in windows of at most 60 days.
4. Corpus: NOAA SWPC texts from the NCEI archive, DONKI notifications and notes, open review papers.
5. Answer key: Richardson–Cane, SSC, NOAA 3-day forecasts, IGS TEC (final), Space-Track history, jamming cases,
   ASG-EUPOS RINEX (Polish stations).
6. Freeze job: re-pull all catalogues, write `freeze/<date>/` with a manifest.

## Status (checked 2026-10-12 00:30 UTC)

Update this section whenever a build-order step starts or finishes, or the collector's health changes.
- Step 1 done: `sources/noaa_swpc.py`. Scheduled every 30 min since 2026-10-11 20:37 UTC: 9 runs to 00:37 on 10-12
  (past midnight too), 0 failed fetches; gap log holds only source-side `no_data` intervals and the two 404s from the retired
  `products/solar-wind/*` files. Coverage starts: solar_wind, kp_3h and GOES protons 2026-10-04 (7-day backfill),
  ACE 1h 2026-09-11, RTSW 2026-10-10 17:38, kp_1m 2026-10-11 11:39.
- Step 2 done 2026-10-11/12: `gfz_kp` 1932-01-01 to 2026-10-10 (692,340 rows; Kp `def` to 2026-09-30),
  `gfz_hp30` 1985-01-01 to 2026-10-10 (1,464,768 rows), no gaps in Kp, ap or Hp30; `omni2_hourly` 1963 to
  2026-10-11 (26,276,760 rows, 47 quantities; field to 09-18, plasma to 09-29, Dst to 10-05). GFZ Kp matches the
  2026-10-10 JSON pull (0 of 3,728 slots differ). 34 unit tests pass (NOAA included).
- Raw manifest: 142 files, every one on disk with SHA-256 (checked after the OMNI pull, which ran alongside the NOAA
  task). Data store 133 MB in OneDrive (`<repo>/data`). Move `SWX_DATA_DIR` out if sync locks files.
- Steps 3–6 not started. Suggested order (audit default, Arek can change it): step 5's answer-key lists (cheap,
  unblocks scoring), then step 3 (DONKI events and notifications, every version), then step 4 (NCEI texts). Audit:
  https://claude.ai/code/artifact/86adc040-9fb4-46d0-8978-736e84f031b2
- Deliberate deviation from the Polish plan: one 30-min cadence for all products instead of 5 min for wind and alerts.
  No data is lost because every short file covers more than 30 min.

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

## Historical series rules (GFZ, OMNI2)

Run: `cd code; uv run swx-gfz` (whole Kp file, 5.5 MB, and Hp30 file, 44 MB) and `uv run swx-omni` (yearly files,
`--from-year`/`--to-year`). Each prints per-file results and a coverage table; exit code 1 if anything failed.
- Tables `normalized/gfz_kp`, `normalized/gfz_hp30`, `normalized/omni2_hourly` add a `status_basis` column. A re-pull
  adds a version when value, unit or status changed, so `pre` → `def` stays visible as history.
- Status: GFZ Kp/ap/Ap from the file's D flag (D>=1 `def`), SN `def` only for D=2. F10.7 and Hp30 have no status in
  the source: `provisional`. OMNI Dst, AE/AL/AU and PC(N) take status from the date spans on
  `omniweb.gsfc.nasa.gov/html/ow_data.html` (archived each run; parsing fails loudly if its wording changes). OMNI
  IMF, plasma and protons have no status anywhere: stored as `def`, with that said in `status_basis`.
- OMNI words 39, 40, 50, 51 (Kp, sunspot number, ap, F10.7) are not stored: GFZ is their primary source.
- `raw/<source>/normalized.json` records which file version (plus the spans-page hash for OMNI) was fully
  normalised. Only those files are skipped, so a stopped run resumes correctly.
- Coverage and gap lists are rebuilt on every run: `raw/<source>/<dataset>_coverage.csv` and `<dataset>_gaps.parquet`.
- All fetches use certifi's CA bundle: the laptop's Windows store lacked the root for kp.gfz.de on 2026-10-11.

## Source-specific gotchas

- GFZ: values go nowcast → `pre` → `def` about monthly. Use `gfz_kp`, not the merged Kp file in
  `dataset_research/.../results/` (CelesTrak before 2025-07-20, no status, Kp rounded to 0.1). Hp30 has no status,
  so `status_basis` records the Hpo version (V3.0 on 2026-10-11).
- The store keeps each series from its file start (Kp 1932, Hp30 1985, OMNI 1963). Which start the analysis uses
  (Hp30 1985 or 1995, Kp 1932 or 1957) is an open question: see `docs/open_questions.md`.
- OMNI: fill values are runs of 9s per word (999.9, 9999.99 and so on), per `omni2.text`; word 49 (proton flag) uses 0
  for "no data" and is kept as a value. OMNI2 lags 2–4 weeks (current end per quantity in
  `raw/omni/omni2_hourly_coverage.csv`) and its proton flux ends 2020-03-04. 1-min data: HAPI `OMNI_HRO_1MIN` (1981
  to 2026-09-30 on 2026-10-11, with SYM-H and AE). HAPI parameters must stay in the documented order, or the server
  returns error 1411.
- DONKI: all 8 event types (CME, FLR, SEP, HSS, MPC, IPS, GST, RBE) carry `submissionTime` and `versionId` (checked
  2026-10-11). The API returns only the latest version, so archive every pull to keep revisions. Entries arrive late:
  2012 entries were submitted 1.2–11 years after the event, 05/2024 IPS entries a median 77 h after the shock.
  `get/notifications?type=all` reaches back to 2010-04-05, weekly reports included, with `messageIssueTime` to the
  minute; alerts are on time (IPS alert 25 min after the 2024-05-10 shock) and are B's shock-flag source. Windows of at most 60 days. Bulk CME
  pulls are large (10,266 CMEs for 2010–2026).
- NOAA proton events (NGDC list): current to 2026-07-30, has known date typos (see the manifest). The correction in
  `docs/zrodla_danych/weryfikacja_maila.md` claiming the list ends in 2011 is wrong (see `docs/decisions.md`).
- NCEI texts: `www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/<product>/<YYYY>/<MM>/`, updated
  daily (discussion from 2024, RSGA from 1966, SGAS from 1996, 3-day and geomagnetic forecasts from 2022); The Weekly
  is under `weekly_reports/PRFs_of_SGD/` from 1997. Text files start with `:Issued: YYYY Mon DD HHMM UTC` (checked
  1996–2026). The Weekly and RSGA before 1996 are PDF: test text extraction (and OCR) on a sample first.
  Date-only means 23:59 UTC.
- ASG-EUPOS RINEX (https://system.asgeupos.pl/) has two roles (`docs/decisions.md`, event set v2): signal-quality
  symptoms at the station (C/N0, observation counts) are input for jamming cases; ROTI and position error are answer
  key (`answer_key/`). Keep them in separate datasets. Account activation and archive depth are still unchecked.
- rtgms.pl monitoring pages are a JavaScript app (plain HTTP gets the same 43.9 KB shell for both), so alarms are
  copied by hand into `docs/metodologia/rtgms_alarmy_2026.csv`. Retention is unknown.
- IGS TEC needs NASA Earthdata (`_netrc`, works since 2026-10-11); use the final product, not rapid. Final GIM and ROTI
  maps (`IGS0OPSFIN_..._GIM.INX.gz`, `..._ROT.INX.gz`) are in `gnss/products/ionex/YYYY/DDD/`. Space-Track works
  too; its data must not be redistributed (under 30 requests a minute, 300 an hour).
- SSC and the Belsk magnetometer are CC BY-NC 4.0. Fine for the thesis; keep the attribution in the manifest.

## Code rules for this part

- Every fetcher is idempotent and resumable: re-running a day must not duplicate rows.
- Be polite: set a descriptive User-Agent, back off on errors (exponential, capped), never hammer an endpoint in tests.
- One module per source (`sources/noaa_swpc.py`, `sources/gfz.py` and so on), sharing `store.py` (`http_get`,
  `RawArchive`, `SeriesStore`). `RawArchive.flush` merges into `raw/manifest.parquet` under `raw/.manifest.lock`, so
  collectors for different sources may run at the same time.
- Answer-key sources write only under `answer_key/`. A test should assert that no answer-key dataset appears under
  `normalized/` or `corpus/`.
- Each source gets a short entry in `docs/data_gathering_plan.md` once it works: endpoint, cadence, row count, quirks.
