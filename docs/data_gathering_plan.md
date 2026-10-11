# Data gathering plan (English working summary)

Summary of the Polish plan written on 2026-10-11 ("Plan pozyskania danych – platforma pogody kosmicznej",
https://claude.ai/code/artifact/ad0e1d0b-0b53-40b8-ad0b-c979d30f1962). This file is a living document. When a
fetcher works, update its row: endpoint tested (date), cadence, row count, quirks.

## Roles

Each source has one main role. Answer-key sources never reach the system (see root `CLAUDE.md`, invariant 1).

| Role | Purpose | Sources |
|---|---|---|
| Input | Time series, event detection, analogue search, live mode | GFZ Kp/ap/Ap/Hp30, NOAA SWPC live, NASA OMNI (history), DONKI (cause chain) |
| Knowledge base | Texts that variant C retrieves and cites | NOAA SWPC texts in NCEI, DONKI notes and reports, review papers |
| Answer key | True cause, timing and effect; forecast baseline | Richardson–Cane, SSC, NOAA proton events, NOAA forecasts, IGS TEC, orbital data, GUGiK jamming cases |

Periods: analogue history Kp from 1957 (or 1932), OMNI from 1963. Test events: all G3+ storms since 2010 plus samples
(see the event set). Live mode: from collector start to the data freeze (default 2026-12-31; final pull Feb 2027).

## Already on the laptop (downloaded 2026-10-10)

In `dataset_research/space_weather_decision/data/` unless noted; provenance in `MANIFEST_D1.md` and `MANIFEST_D2.md`.

| File | Range | Rows | Notes |
|---|---|---|---|
| `results/kp_ap_Ap_SN_F107_daily_1957-10-01_to_2026-10-09_merged.csv.gz` | 1957-10-01 – 2026-10-09 | 25,211 | CelesTrak to 2025-07-20 (Kp rounded to 0.1, no status), then GFZ |
| `gfz_kp_ap_Ap_SN_F107_daily_2025-07-01_to_2026-10-09.csv` | 2025-07-01 – 2026-10-09 | 466 | Definitive to 2026-09-30, preliminary 1–9 Oct; SN preliminary from 2026-04-01 |
| `gfz_Hp30_selected_storms.csv` | 6 storm windows 2003–2026 | 1,104 | Plus May 2024 window in `samples/`; API gives no status for Hp30 |
| `omni_hourly_2024-05-08_to_2024-05-15_gannon.csv` | 8–15 May 2024 | 192 | One storm only; Dst 2021–2026 provisional |
| `donki_gst_2010-01-01_to_2026-10-09.csv` | 2010-04-05 – 2026-10-04 | 201 | Storms with links; no note text |
| `donki_cme_linked_to_gst.csv` | 2010–2026 | 148 | Only CMEs linked to storms (10,266 fetched) |
| `donki_ips_earth_2010-01-01_to_2026-10-09.csv` | 2010-04-05 – 2026-10-09 | 683 | Shocks at Earth (the shock feature) |
| `richardson_cane_icme_1996_to_2026.csv` | 1996-05-27 – 2026-07-03 | 644 | Answer key; last rows with provisional Dst |
| `isgi_ssc_1957_to_2026.csv` | 1957-01-02 – 2026-08-11 | 1,806 | Answer key; definitive to 2022, preliminary 2023–2026 |
| `noaa_sep_events_1976_to_2026.csv` | 1976-04-30 – 2026-07-30 | 320 | From NGDC; known date typos (see manifest) |
| `intermagnet_BEL_1min_2024-05-10T12_to_2024-05-11T12.csv` | 10–11 May 2024, 1 min | 1,440 | Belsk, definitive |

Nothing yet for: full Hp30, full OMNI, the NOAA live collector, NOAA forecasts and texts from NCEI, DONKI notes and
reports, DONKI SEP/FLR/HSS events, review papers, IGS TEC maps, orbital data, jamming cases.

## Source cards

Only NASA Earthdata (TEC on CDDIS) and Space-Track (historical orbits) need accounts; both are free. Licences are in
`zrodla_danych/dostep_do_zrodel_danych.xlsx`.

### Input

| Source | Range needed | Resolution | Access | Missing | Preliminary vs final |
|---|---|---|---|---|---|
| GFZ Kp, ap, Ap | 1957 (or 1932) – freeze | 3 h (Ap daily) | `Kp_ap_Ap_SN_F107_since_1932.txt` or JSON API | GFZ version with status (and 1932–1957 if extended) | nowcast → `pre` → `def` monthly; store status; re-pull before freeze |
| GFZ Hp30 | 1985 (or 1995) – freeze | 30 min | Full Hpo series files on kp.gfz.de or API | Full series (~720k rows) | API gives no status; record Hpo version (V3.0) |
| NOAA SWPC live | Collector start – freeze | 1 min (wind, estimated Kp), 3 h (Kp), 5 min (GOES protons) | services.swpc.noaa.gov | Everything; files keep 1–7 days | All `realtime`; evaluate live mode on what was known then |
| NASA OMNI | 1963 – ~1 week before freeze; 1 min only for test-storm windows | 1 h (OMNI2), 1 min (HRO, from 1981) | `omni2_all_years.dat` on SPDF or HAPI | Whole history | Dst from 2021 provisional, AE without status; store flags |
| NASA DONKI events | 2010 – freeze | Events | `ccmc.gsfc.nasa.gov/DONKI-API/get/...`, windows ≤ 60 days | All CMEs raw, FLR, SEP, HSS, MPC | Records have `versionId` and get revised; re-pull at freeze |

### Knowledge base (RAG)

| Source | Range | Unit | Access | Missing | Note |
|---|---|---|---|---|---|
| NOAA SWPC texts (NCEI) | ≥ 2010 – freeze; ideally from 1996 | Document with issue date and time | HTTPS directories under ngdc.noaa.gov/stp/space-weather/swpc-products/ (wget) | RSGA (from 1966), SGAS and event reports (from 1996), The Weekly (from 1997), Forecast Discussion (from 03/2024) | Final at issue; the issue time drives the cut-off |
| DONKI notes and reports | 2010 – freeze | Note, report | Same API (`note` field; notification types to check) | All note text | `versionId` as above |
| Review papers | n/a | Paper section | PDF via DOI (Temmer 2021, Richardson 2018), CC BY 4.0 | All | n/a |

### Answer key and baseline

| Source | Checks | Range | Access | Missing | Note |
|---|---|---|---|---|---|
| Richardson–Cane ICME | Cause: CME or fast wind | 2010 – freeze (have from 1996) | HTML page | Re-pull at freeze | Provisional Dst flagged P/Q; list updated with delay |
| SSC list (Ebre/ISGI) | Shock arrival time | 2010 – freeze | Yearly files at obsebre.es | Have 1957 – 2026-08-11 | Definitive to 2022 |
| NOAA proton events | Radiation storms (operators) | 2010 – freeze | NGDC table | Have to 2026-07-30 | Preliminary list with date typos |
| NOAA forecasts (3-day, RSGA) | Does the platform beat NOAA | 3-day from 03/2022, geomagnetic from 11/2022, RSGA predicted Ap from 1966 | NCEI, like texts | All | Final at issue |
| IGS TEC maps (IONEX) | Effect on GNSS | Test-storm windows ±3 days plus quiet days, 2010 – freeze | CDDIS, Earthdata account | All | Use final product (~2 weeks delay), not rapid |
| Starlink orbits | Effect on satellites: faster decay | 01–03/2022, 04–06/2024, plus G3+ storms since 2020 | Space-Track `gp_history`, account; no redistribution. CelesTrak SupGP is current only | All | Elements get overwritten; take history from Space-Track |
| Jamming cases (GUGiK, rtgms.pl) | Counter-examples "not space weather" | 2024 – freeze | Manual from geoportal.gov.pl; e-mail GUGiK / IŁ-PIB for RTGMS data | All | n/a |

Optional: Belsk (local storm picture, BGS HAPI, test-storm windows) and EPN observations (own RINEX processing, a lot
of work). Neither is in the final advisor e-mail.

## NOAA live files: polling and archiving

Start the collector as soon as possible. The 7-day files are a buffer: if the collector runs again within 7 days, full
minute data can be recovered.

Tested 2026-10-11 on the laptop (collector `code/ingestion/src/swx_ingest/sources/noaa_swpc.py`, run every 30 min).
Rows and coverage are from the first run.

| File (services.swpc.noaa.gov) | Content | Keeps | Result 2026-10-11 |
|---|---|---|---|
| `/products/solar-wind/plasma-*.json`, `mag-*.json` | Solar wind, 1 min | n/a | **404, directory removed.** Replaced by the propagated files below |
| `/products/geospace/propagated-solar-wind-1-hour.json`, `propagated-solar-wind.json` | Plasma + field at L1, 1 min, plus estimated arrival time at Earth | 1 h / 7 days | OK: 110,220 rows (7 days, 11 quantities) |
| `/json/rtsw/rtsw_wind_1m.json`, `rtsw_mag_1m.json` | RTSW 1 min per spacecraft (SOLAR1 active; ACE, IMAP) with quality flags | ~24 h | OK: 105,212 and 74,860 rows. `-9999` is a fill value. One HTTP 502 on a manual retry |
| `/json/ace/swepam/ace_swepam_1h.json`, `/json/ace/mag/ace_mag_1h.json` | ACE plasma and field, hourly | ~30 days, hours missing | OK: 2,492 and 8,593 rows; hourly gaps logged |
| `/json/planetary_k_index_1m.json` | Estimated Kp, 1 min | ~6 h | OK: 723 rows |
| `/products/noaa-planetary-k-index.json` | Kp every 3 h | 7 days | OK: 183 rows. Now a list of objects (no header row); Kp as decimal thirds |
| `/json/goes/primary/integral-protons-1-day.json`, `-7-day.json` | GOES integral protons, 5 min, per energy channel | 1 / 7 days | OK: 16,080 rows; source gap 2026-10-06 17:25–17:45 |
| `/products/noaa-planetary-k-index-forecast.json` | Kp forecast | n/a | OK, raw only (answer key) |
| `/products/alerts.json`, `/products/noaa-scales.json` | Alerts; current G/S/R | few days / current | OK, raw only |
| `/text/3-day-forecast.txt`, `/text/3-day-geomag-forecast.txt`, `/text/discussion.txt` | Forecasts and forecaster discussion | current issue | OK, raw only, indexed by `:Issued:` |

Archiving rules:
1. Save every response unchanged (raw, compressed) with the UTC fetch time in the name and its SHA-256. If the hash
   equals the previous one, write only a log entry.
2. Build a separate normalised table: one row per timestamp and quantity, columns `time_tag`, `fetched_at`,
   `source_file`, `spacecraft` (DSCOVR or ACE, from the RTSW source field), `status = realtime`. Unique key
   `time_tag` + quantity + file; a newer fetch of the same timestamp adds a version and never overwrites.
3. For texts, store the issue time from the header (`:Issued:`) and the fetch time.
4. Keep a gap log: every failed fetch and every interval without data. Once a day compare the archive with the 7-day
   files and backfill missing minutes.
5. Never mix this archive with historical data: NOAA live values are preliminary. Use GFZ `def` and OMNI for history
   and the answer key; use the NOAA archive to evaluate live mode.
6. Where to run: a Windows Task Scheduler job on the laptop is enough if the laptop is on at least every few days.
   An always-on machine is better for continuous alerts and texts. Texts and alerts can be recovered from NCEI later;
   live minute data cannot.

## Rules for all sources

- **Role separation.** Richardson–Cane and SSC are answer key only. The shock feature comes from DONKI IPS.
- **Time separation.** Every knowledge-base document has an issue time; RAG sees only documents issued before t0.
- **Value status.** Every numeric value has `source`, `status` (`realtime`, `pre`, `def`, `provisional`) and
  `retrieved_at`, plus manifests (URL, fetch time, SHA-256, licence) as in D1/D2.
- **Freeze.** On the freeze date re-pull all catalogues (GFZ, DONKI, Richardson–Cane, SSC, SEP) and store their
  versions. Thesis results use only the frozen version.
- **Licences.** Space-Track forbids redistribution: raw elements stay out of thesis appendices, only derived results.
  SSC and Belsk are CC BY-NC 4.0. Send CCMC a short e-mail about using DONKI for validation.

## Collection checklist

Order: first what cannot be recovered later (NOAA live), then what the test event set needs.

Now
- [x] Start the NOAA SWPC collector; check every URL on first fetch (scheduled every 30 min since 2026-10-11)
- [ ] Create NASA Earthdata (CDDIS) and Space-Track accounts
- [ ] E-mail CCMC about using DONKI for validation
- [ ] E-mail GUGiK / IŁ-PIB about the RTGMS interference archive

Historical series (input)
- [ ] GFZ full Kp/ap/Ap since 1932 with status; replace the CelesTrak part of the merged file
- [ ] Full Hp30 from GFZ; settle the start year (1985 or 1995)
- [ ] OMNI2 hourly 1963–today (`omni2_all_years.dat`)
- [ ] All DONKI CME, FLR, SEP, HSS and MPC 2010–today as raw JSON (60-day windows)

Test event set
- [x] G3+ storms since 2010, G1–G2 sample and quiet days (done: `metodologia/zestaw_zdarzen_ewaluacja.csv`)
- [ ] OMNI 1-min (HRO) for those storm windows

Knowledge base (RAG)
- [ ] NOAA texts from NCEI: RSGA, SGAS, event reports, The Weekly, Forecast Discussion; test whether old RSGA needs OCR
- [ ] DONKI notes (`note` field) and reports, if the API serves them
- [ ] Temmer 2021 and Richardson 2018
- [ ] Give every document an issue time

Answer key
- [ ] NCEI archived 3-day forecasts (from 03/2022) and RSGA predicted Ap
- [ ] IGS TEC maps (final) for test-storm windows and quiet days
- [ ] Space-Track Starlink element history for 2022, 2024 and G3+ storms since 2020
- [ ] Jamming cases from geoportal.gov.pl and rtgms.pl

At the end
- [ ] On the freeze date re-pull GFZ, DONKI, Richardson–Cane, SSC and the SEP list; write manifests with SHA-256
- [ ] Review the NOAA collector gap log and describe gaps in the thesis
