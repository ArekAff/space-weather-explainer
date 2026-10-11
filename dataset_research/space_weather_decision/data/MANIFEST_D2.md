# MANIFEST_D2 - space-weather event lists and storm time series (fetch batch D2)

Prepared 2026-10-10. All data were read in the user's built-in browser (fetch() from a page on the data host's origin), converted to CSV in the browser, transferred in chunks, re-joined in the container and saved only after the container SHA-256 equalled the SHA-256 computed in the browser. All files are ASCII, comma-separated, LF line endings, one header row, final newline. Empty field = missing / not given in the source.

| # | File | Rows x cols | First - last timestamp | SHA-256 | Status |
|---|------|-------------|------------------------|---------|--------|
| 1 | richardson_cane_icme_1996_to_2026.csv | 644 x 24 | 1996-05-27 15:00 - 2026-07-03 11:00 (disturbance_time) | e6845455f2b70322b6949f4299cd55ec1b15f71f3542b7e23d42aa784eaf130b | OK |
| 2 | isgi_ssc_1957_to_2026.csv | 1806 x 13 | 1957-01-02 09:06 - 2026-08-11 11:26 | d94aed6b6b277db7aa09e7cfd7b76f8f97bb00228322081f8e7428a51ef4ef65 | OK |
| 3 | omni_hourly_2024-05-08_to_2024-05-15_gannon.csv | 192 x 11 | 2024-05-08 00:30 - 2024-05-15 23:30 | 8741104bfc629c758f3022b01a3d3226f2518b0846ef4125b73c83df5975bb2e | OK |
| 4 | noaa_sep_events_1976_to_2026.csv | 320 x 12 | 1976-04-30 21:20 - 2026-07-30 18:45 (start_time) | ed50881dcf59001c61dbd3282575f017d7c0333744ad807483c4a119054423c7 | OK |
| 5 | intermagnet_BEL_1min_2024-05-10T12_to_2024-05-11T12.csv | 1440 x 6 | 2024-05-10 12:00 - 2024-05-11 11:59 | 1f7fa7fc11d42200de03fc78f7ec279550b74e3985c3940086712cda34a8331e | OK (completed in a second browser session, 21:02-21:06Z) |

---

## 1. richardson_cane_icme_1996_to_2026.csv - Richardson & Cane near-Earth ICME list

- URL: https://izw1.caltech.edu/ACE/ASC/DATA/level3/icmetable2.htm
- Retrieved: 2026-10-10T15:54:48Z; re-fetched 2026-10-10T15:59:35Z after the browser tab was closed externally - both fetches gave a byte-identical CSV (same SHA-256).
- Page states "Revised July 23, 2026" (HTTP Last-Modified not exposed). Catalog DOI: 10.7910/DVN/C2MHTH.
- Terms: no licence on the page; it asks users to "include the DOI when referring to the catalog in a publication".
- Columns: disturbance_time, disturbance_flag, icme_start, icme_end, comp_start, comp_end, mc_start, mc_end, bde, bif, qual, qual_flag, dv, dv_flag, v_icme, v_max, b_mean, mc, mc_flag, dst_min_nT, dst_flag, v_transit, lasco_cme, lasco_cme_time.
  - disturbance_time, icme_start, icme_end converted from "YYYY/MM/DD HHMM" to "YYYY-MM-DD HH:MM" (all 644 rows converted; one source date had a 1-digit day, 2024/09/4).
  - disturbance_flag = letter that followed the disturbance time in brackets (footnote a): A = shock time at ACE (27 rows), W = shock at Wind (4), S = possible shock from SOHO Shockspotter (4); empty = SSC/SI time or estimated arrival.
  - Letter flags were split off into separate columns so the value columns stay clean: qual_flag W = weak ICME signatures (49); dv_flag S = forward fast shock reported (164) plus one "Wv" (1998-05-04, as in source); mc_flag H = Huttunen et al. cloud not in Lepping list (14); dst_flag P = provisional (114), Q = quick-look (8), empty = final.
  - comp_start/comp_end and mc_start/mc_end are hours relative to the ICME start/end (text as given, incl. "ns", "nc", "(2 MCs)"). mc_start/mc_end were added because the table has them.
  - lasco_cme = associated CME text as given (may list several CMEs, codes H/D/W/?, "dg" = LASCO data gap, brackets = solar event without coronagraph coverage, "(p)" = multiple candidates). lasco_cme_time = ISO time of the first CME listed, only when unambiguous (344 rows); left empty for "dg", "...", bracketed or day-only entries.
  - "..." = no data/not applicable in the source; kept as text.
- Caveats: 30 repeated header rows and 18 empty spacer rows removed; 11 rows had an extra empty 19th cell (dropped). All rows split cleanly, so no raw_row column was needed. In 2 rows the disturbance time is after icme_start (2007-01-14, 2011-10-07), as in the source. Recent Dst values are provisional/quick-look and the list is "updated frequently" (2026 rows may change).

## 2. isgi_ssc_1957_to_2026.csv - ISGI storm sudden commencements / sudden impulses

- ISGI page https://isgi.unistra.fr/events_sc.php holds no data in its source. ISGI's own routes were not usable under the rules: https://isgi.unistra.fr/data_download.php is a 2-step form that requires an e-mail address, and the web service (https://isgi.unistra.fr/ws?user=...&index=SC, documented at https://isgi.unistra.fr/ws_documentation.php) needs a user name issued by ISGI.
- Source used: the ISGI SC page names Observatori de l'Ebre (Spain) as the ISGI Collaborating Institute that produces the list and links to http://www.obsebre.es/en/variations/rapid, which publishes the annual SC lists:
  - https://www.obsebre.es/php/geomagnetisme/vrapides/ssc_YYYY_d.html for 1957-1967 (Mayaud series, definitive)
  - https://www.obsebre.es/php/geomagnetisme/vrapides/ssc_YYYY_d.txt for 1968-2022 (definitive)
  - https://www.obsebre.es/php/geomagnetisme/vrapides/ssc_YYYY_p.txt for 2023-2026 (preliminary)
- Retrieved: 70 files, 2026-10-10T16:05:40Z-16:06:36Z; re-fetched 16:22:57Z-16:23:52Z after the browser pane was closed externally (byte-identical CSV). ssc_2026_p.txt Last-Modified: Mon, 21 Sep 2026 09:10:13 GMT.
- Licence/terms: the Ebre page says use is "subject to compliance with the CC BY-NC 4.0 license"; the ISGI SC page shows the CC BY-NC 4.0 badge. ISGI policy (https://isgi.unistra.fr/policy.php): data must "not [be] used for commercial gain". Users should acknowledge the collaborating institute, ISGI, INTERMAGNET and the observatories, and offer co-authorship when making substantial use.
- Size rule: the full list from 1869 is clearly above 100 KB as CSV (1869-1918 alone has 1045 events; 1957-2026 is already 131 KB), so 1957 onward was kept.
- Columns: datetime_utc, type, minute_decimal, duration_min, amplitude_nT, amplitude_ANS, rise_time_min_by_station, amplitude_nT_by_station, quality_codes, stations, appreciations, status, raw_line.
  - datetime_utc "YYYY-MM-DD HH:MM". Where the source gives a decimal minute (1995-2015), the minute is truncated and the original decimal is kept in minute_decimal (for example 40.1 means 19:40:06).
  - type: SSC / SI / SI- (negative impulse), as given; only the 2006+ lists give it (343 rows: SSC 268, SI 62, SI- 13). Empty before 2006 (the Mayaud 1868-1967 list is described as SSC-only; the 1968-2005 lists give no per-event type).
  - Formats differ by era (all as given, nothing recomputed). 1957-67: duration_min, amplitude_nT = AT (collection T, nT), amplitude_ANS = normalised amplitude, quality_codes = N T S codes. 1968-1994: duration_min, amplitude_nT (mean of 5 low-latitude observatories), quality_codes (5-digit code split into space-separated digits; "-" = no record), appreciations = collaborating-observatory counts A/B/C/si/sfe as given. 1994 is fixed-width and parsed by column position into "A:n B:n C:n -:n si:n time_dif:(hhmm-hhmm)". 1995-2004: duration_min, amplitude_nT, quality_codes, stations. 2005+: per-station rise times, amplitudes and quality codes plus stations (same order).
  - status: definitive (1957-2022) or preliminary (2023-2026).
  - raw_line: filled for 1 row only (1996-11-11 15:26), where the source prints the amplitude as "09 4". amplitude_nT is left empty and the full source line is kept.
- Caveats: per-year footnotes in the source (for example times based on only 4 observatories) are not carried into the CSV. Preliminary 2023-2026 lists can change. The site returned HTTP 429 (rate limit) to parallel requests, so files were fetched one at a time.

## 3. omni_hourly_2024-05-08_to_2024-05-15_gannon.csv - NASA OMNI hourly, May 2024 storm

- Info: https://cdaweb.gsfc.nasa.gov/hapi/info?id=OMNI2_H0_MRG1HR (HAPI 2.0; dataset stopDate 2026-10-05T13:00Z)
- Data: https://cdaweb.gsfc.nasa.gov/hapi/data?id=OMNI2_H0_MRG1HR&parameters=ABS_B1800,BZ_GSM1800,N1800,V1800,Pressure1800,R1800,F10_INDEX1800,KP1800,DST1800,AE1800&time.min=2024-05-08T00:00:00Z&time.max=2024-05-16T00:00:00Z&format=csv (the same URL with &include=header was used to confirm column order; data lines identical). The first attempt listed the parameters in a different order and got HAPI error 1411 "Parameter out of order".
- Retrieved: 2026-10-10T16:27:48Z
- Terms: the HAPI response has no licence text. The CDAWeb dataset notes give DOI 10.48322/1shr-ht18 (OMNI, J.H. King and N. Papitashvili, ADNET/NASA GSFC); cite the DOI / OMNIWeb.
- Columns (units): datetime_utc; B_mag_avg_nT = ABS_B1800 (field magnitude average, nT); Bz_GSM_nT = BZ_GSM1800; flow_speed_km_s = V1800; proton_density_per_cc = N1800 ("ion number density"); flow_pressure_nPa = Pressure1800; Kp_x10 = KP1800 (Kp*10, e.g. 87 = 8+ and 90 = 9o); Dst_nT = DST1800; AE_nT = AE1800; sunspot_number_daily = R1800 (daily SILSO V2); F10_7_sfu = F10_INDEX1800 (daily, 10^-22 W m^-2 Hz^-1).
- Fill values (999.9, 9999.0, 99.99, 99, 99999, 9999, 999 per /info) are written as empty fields. Only 2024-05-09 18:30 had fills (speed, density, pressure).
- Caveats: timestamps are hour midpoints (HH:30) as served, so each value is the HH:00-HH:59 average. Kp, sunspot number and F10.7 repeat over 3 h or 1 day. The /info says Dst for 2021-2026 is provisional. AE in 2024 is present, but its status is not stated (the description lists provisional AE only to 2020). Minimum Dst is -406 nT at 2024-05-11 02:30; Kp*10 reaches 90.

## 4. noaa_sep_events_1976_to_2026.csv - NOAA/SWPC solar proton events affecting the Earth environment

- Checked https://umbra.nascom.nasa.gov/SEP/ ("Preliminary Listing 1976 - present"; HTTP Last-Modified Mon, 26 Feb 2018 18:13:15 GMT; no update date in the text). It stops abruptly at 2014-02-25 (last row truncated), so it was not used.
- Used the NGDC copy, which is more complete and current: https://www.ngdc.noaa.gov/stp/space-weather/interplanetary-data/solar-proton-events/SEP%20page%20code.html (title "NOAA Space Weather Prediction Center - Solar Proton Events Affecting the Earth Environment 1976 - Present"; HTTP Last-Modified Mon, 03 Aug 2026 21:53:01 GMT; no explicit update date in the text).
- Retrieved: 2026-10-10T16:33:38Z
- Terms: the page states no licence or terms. It credits CDAW (CME movies), LASP SWx TREC (flux plots) and LMSAL (flare links), and gives SWPC contacts.
- Event definition (page note): >10 MeV integral 5-min GOES fluxes in pfu. Start = first of 3 consecutive points >= 10 pfu. Fluxes from different GOES detectors are not cross-normalised.
- Columns: start_time, max_time (ISO from "YYYY MM/DD HHMM"); peak_pfu_gt10MeV (thousands separators removed); flare_importance and flare_max_time (split from "Flare Maximum": class/optical part and ISO time, year taken from the event, Dec->Jan handled); location; active_region; type_II_radio; type_IV_radio; cme_linear_speed_km_s; cme_info; cdaw_cme_ref.
  - cme_info = free-text note in the "Imagery/Misc" column (link labels such as C2/X-Ray/Flux Plot removed; a stray literal "a>" HTML artefact removed in 4 cells).
  - cdaw_cme_ref = CME identifier taken from the CDAW link in that column: the "title" value (date.time.PA;V=speed), the .yht file name, or "movie date YYYYMMDD".
  - "N/A" in the source is written as empty.
- Caveats (source values kept as given): max_time before start_time on 2014-02-25; max 1990-09-19 for the 1990-03-19 event and 2025-01-25 for the 2025-01-04 event (likely source typos); flare 1989-06-15 listed for the 1989-08-15 event. In 11 rows the listed flare maximum is after the event start (for example 1989-03-10 with an 03/17 flare). Three flare times are kept raw because they are not in M/D HHMM form: "0411 1353", "06/14", "09/1858". A few cdaw_cme_ref values look inconsistent with the event date (for example 2001-10-19 and 2012-09-01), and in places the CDAW speed differs from the linear-speed column. The largest events are 43,500 pfu (1991-03-23), 42,200 (1989-10-19) and 37,000 (2026-01-18).

## 5. intermagnet_BEL_1min_2024-05-10T12_to_2024-05-11T12.csv - INTERMAGNET Belsk (BEL) definitive 1-min data, 10-11 May 2024

- HAPI server: https://imag-data.bgs.ac.uk/GIN_V1/hapi (HAPI 3.1, id "INTERMAGNET", contact e_ginman@bgs.ac.uk). Catalog: https://imag-data.bgs.ac.uk/GIN_V1/hapi/catalog lists bel/{definitive,quasi-def,adjusted,reported,best-avail}/PT1M/{native,xyzf,hdzf,diff}.
- Chosen dataset: bel/definitive/PT1M/xyzf (definitive data cover 1993-01-01 to 2025-12-31T23:59Z; modificationDate 2026-04-14T03:30:33Z; timeStampLocation begin; fill 99999.0). The native orientation for this window is XYZ (checked with bel/definitive/PT1M/native).
- Data URL: https://imag-data.bgs.ac.uk/GIN_V1/hapi/data?dataset=bel/definitive/PT1M/xyzf&start=2024-05-10T12:00:00Z&stop=2024-05-11T12:00:00Z&format=csv. First retrieved 2026-10-10T16:37:28Z; re-fetched 2026-10-10T21:02:09Z (the /info modificationDate was still 2026-04-14T03:30:33Z). Both fetches gave the same CSV (same SHA-256). 1440 rows, no fills, no gaps (continuous 1-min steps).
- Time range: 2024-05-10 12:00 to 2024-05-11 11:59 UTC. The HAPI stop time is exclusive, and each timestamp marks the start of its minute (timeStampLocation begin).
- Terms/acknowledgement given by the service: "citation" : "https://intermagnet.org/data_conditions.html". The /hapi/about response also includes x_warnings: "Some institutes choose to embargo their data for a short time. For more information see https://imag-data.bgs.ac.uk/GIN_V1/index.jsp#embargo_data_plots".
- INTERMAGNET conditions of use (https://intermagnet.org/data_conditions.html, read 2026-10-10 ~21:05Z): unless otherwise noted, the data are "licensed under a Creative Commons Attribution-NonCommercial 4.0 International License".
  - Use is non-commercial. Commercial use, sale or bulk redistribution to third parties needs written permission from the institute that runs the observatory.
  - The preferred acknowledgement is to cite the relevant DOIs. Definitive INTERMAGNET data from 2013 onward are published with DOIs; the DOI for the 2024 definitive data was not looked up here.
  - Where no DOI is available, use the page's "Suggested Acknowledgement Text (template 2)". It names the observatory (Belsk) and its operating institute and thanks INTERMAGNET. The page also asks that a citation reference be sent to the INTERMAGNET Secretary.
  - BEL is not in the page's list of institutes with different licence conditions (only BCMT is listed). It is also not in the table of observatories with data embargoes.
- CSV columns: datetime_utc ("YYYY-MM-DD HH:MM"), X_nT, Y_nT, Z_nT, H_nT, F_nT, all rounded to 0.1 nT.
  - X, Y and Z come from the source, which already has 0.1 nT resolution.
  - H_nT = sqrt(X^2+Y^2), computed from the unrounded source values and then rounded.
  - F_nT is the observatory's independent scalar field, rounded half away from zero with exact decimal arithmetic. It is an extra column beyond the requested X/Y/Z/H.
  - Fill value 99999.0 would be written as empty; none occur.
- Transfer: CSV of 80,678 chars, 7 chunks. The first session was interrupted after chunks 00-02 because the user's computer went offline. In the second session, the re-fetch reproduced the same browser hash, and the existing part00-02 files matched the new chunk hashes byte for byte, so they were reused. Chunks 03-06 were then transferred and each was verified. The full-file container SHA-256 equals the browser SHA-256, and pandas loads the file as 1440 x 6 with no missing values.
- Notes from the browser-side data: the SSC step at Belsk is between 17:06 and 17:08 UT on 10 May (H 19021.1 -> 19229.1 nT). Minimum H was 18211.0 nT at 22:16 UT, and the largest 1-min |dH| was 248.5 nT at 22:37 UT.
