# Data dictionary: zestaw_zdarzen_ewaluacja.csv

One row per evaluation event (v3: 158 events). Descriptions are translated from the `COLS` list in
`zestaw_zdarzen_xlsx.py` (the "Legenda" sheet of the XLSX); that list is the source, so change it there first and
then here. How the events were chosen: `zestaw_zdarzen_zasady.md`. All times are UTC unless the name says otherwise.

"Use" says who may read the column: **system** = may be given to the platform; **grouping** = only selects and
groups runs; **key** = answer key or knowledge from after t0, for evaluation code only.

| Column | Use | Meaning |
|---|---|---|
| `id` | system | Stable event ID. B = storm, Q = quiet day, F = shock/impulse without a storm, J = GNSS jamming |
| `t0_utc` | system | The moment at which the system must explain the event. Storms: start + 3 h (first available Kp value). Knowledge cut-off: `issued_at <= t0` |
| `stacja` | system | ASG-EUPOS station code for rtgms.pl events (WIKO = Wicko, BRWO = Braniewo); empty otherwise |
| `zbior` | grouping | DEV = tuning of prompts and thresholds; TEST = held out, scored once (events from 2025-01-01). Exception: rtgms.pl alarms of May 2026 (J132–J139) are DEV |
| `okres_korpusu` | grouping | Corpus period: P1 before 06/2020 (DONKI notes retrospective), P2 06/2020–02/2024, P3 from 03/2024 (Forecast Discussion). Report scenario C per period |
| `kategoria` | key | Event type (storm G1–G5, quiet day, impulse/shock without a storm, GNSS jamming) |
| `poczatek_utc` | key | Storms: start of the first 3-h interval with Kp ≥ 5-. Quiet days: 00:00. Impulses: SSC/SI time. rtgms.pl alarms: start of the first alarm of the episode, converted from Polish time |
| `poczatek_rtgms_pl` | key | rtgms.pl alarms only: start as the site shows it (Polish time, UTC+2 in summer), to find the alarm on rtgms.pl. Part of the ID key |
| `szczyt_utc` | key | 3-h interval with the maximum Kp |
| `koniec_utc` | key | End of the Kp ≥ 5- episode (impulses: +48 h) |
| `kp_max` | key | Maximum Kp in the window (GFZ), in thirds (e.g. `7+`) |
| `kp_wstepne` | key | `tak` = the window contains preliminary GFZ Kp values (from 2026-10-01). Rebuild after definitive values are published and re-check Kp and level |
| `poziom` | key | NOAA G scale (Kp 5 = G1 … 9o = G5) |
| `klucz_przyczyna` | key | The correct answer for cause classification |
| `klucz_zrodlo` | key | Source of the cause key. Richardson-Cane = independent key; „tylko DONKI” = key that depends on the input of C (weakened) |
| `moment_klucz` | key | Shock time key: SSC from the ISGI list; if missing, the disturbance time from the Richardson–Cane list |
| `rc_icme` | key | Richardson–Cane ICME covering the storm peak (or partly in the window), with Dst minimum |
| `ssc_isgi` | key | The chosen shock: the last SSC before start + 3 h, otherwise the first after |
| `ssc_inne_w_oknie` | key | Other SSC/SI in the window [start − 24 h, peak + 3 h] |
| `donki_gst` | key | DONKI storm entries starting in [start − 12 h, end] |
| `donki_cme` | key | CMEs linked to the GST entry: start time, speed, source location, active region |
| `donki_hss` | key | High-speed streams linked to the GST entry |
| `donki_ips` | key | DONKI interplanetary shocks at Earth in [start − 24 h, peak + 3 h] |
| `donki_klasa` | key | DONKI driver class: CME / HSS/CIR / mixed / none |
| `spe` | key | Largest NOAA proton event (>10 MeV ≥ 10 pfu) in [start − 72 h, end], with S level |
| `skutek_gnss` | key | Documented effect on GNSS (if any) and the effect expected from the NOAA scale |
| `skutek_satelity` | key | Documented effect on satellites (if any) and the effect expected from the NOAA G and S scales |
| `skutek_zrodlo` | key | Source of the effect: publication or notice |
| `skutek_status` | key | „udokumentowane” or „oczekiwane wg skali”; „DO SPRAWDZENIA” = source given from model knowledge, check before citing |
| `pomiar_skutku` | key | Which data would verify the effect |
| `noaa_forecast_discussion` | key | Whether a NOAA forecaster text exists for the event (from 03/2024; optional variant D) |
| `wymuszone` | key | Event added by hand, outside the random sampling |
| `uwagi` | key | Notes |
| `wersja` | key | When the event was added (set version). IDs are stable; IDs of removed events (J121, J126, J128) are not reused |

The `donki_*` columns show what the DONKI catalogue says today. In scenarios C and C-decision the system reads DONKI
itself through the time gate (`submissionTime <= t0`), never from these columns.
