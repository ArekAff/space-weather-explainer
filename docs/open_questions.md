# Open questions

Items that agents must not treat as settled. When one is answered, move it to `decisions.md` with the date and the
answer. Grouped by where the answer will come from.

## Answered by trying it (first download)

- Resolved 2026-10-12: GFZ's complete Hp30 file (Hpo V3.0) starts 1985-01-01, and the store holds it from there.
- Resolved 2026-10-12: notifications, weekly reports included, go back to 2010-04-05 with `messageIssueTime` to the
  minute. All 8 event types carry `submissionTime` and `versionId`; the API serves only the latest version. Entries
  arrive late (2012 entries 1.2–11 years after the event; 05/2024 IPS entries a median 77 h after the shock).
- Resolved 2026-10-12 for the text products: RSGA (1996, 2026), SGAS (2010) and Forecast Discussion (2026) start with
  `:Issued: YYYY Mon DD HHMM UTC`. The Weekly is PDF; check its issue date when extracting.
- Is pre-1996 RSGA only scanned PDF (needs OCR)? The NCEI files are PDF (1980 sample); OCR need still untested.
- Resolved 2026-10-11 (accounts thread): IGS final ROTI maps (`IGS0OPSFIN_..._ROT.INX.gz`) sit next to the GIM files
  in `gnss/products/ionex/YYYY/DDD/` on CDDIS.
- Resolved 2026-10-12: no. OMNI2 proton flux ends 2020-03-04, so variant A has no proton numbers from 2020-03 until
  the live collector's GOES data start on 2026-10-04 (see the question under "Arek decides").

## Arek decides

- Kp history from 1957 (as in the e-mail) or from 1932? If 1957 stays, the thesis needs one sentence of justification
  (e.g. alignment with OMNI from 1963).
- Definition of t0 in the main mode. Default: the moment the platform first detects the anomaly (first Kp/Hp30
  threshold crossing); for storms in the event set, onset + 3 h.
- Where the NOAA collector runs: the laptop via Task Scheduler (default; the 7-day buffer covers short gaps) or an
  always-on machine for full continuity of alerts and texts.
- Use of the 7 storms marked SPORNE (catalogues disagree): score against Richardson–Cane, or exclude them and say so.
- Which LLM and embedding model to use, and whether to pin their versions for the whole evaluation.
- Resolved 2026-10-12 (Arek): B's shock flag comes from DONKI IPS alerts; see `decisions.md`.
- Whether variant A needs >10 MeV proton flux for 2020-03 – 2026-10 (TEST radiation storms such as 2026-01-19). No
  source tested yet; the GOES archive at NCEI is the likely candidate.

## Advisor (Prof. Surma) or outside parties

- Data freeze date (default 2026-12-31).
- E-mail to CCMC about using DONKI for validation (recommended by CCMC policy).
- E-mail to GUGiK / IŁ-PIB only if the rtgms.pl web archive (`/monitoring-medium`, `/monitoring-low`) is not enough or cannot be exported.

## Evaluation event set: known gaps

- 3 jamming entries from 2026 are periods, not single days; exact days and hours must be read from rtgms.pl.
- The GUGiK notice about Siedlce on 2026-06-30 could not be found again; marked "to confirm".
- Effect sources for the 03/2015 and 09/2017 storms came from memory and are unverified; check before citing.
- One TEST storm (2026-08-18) falls after the end of the Richardson–Cane list, so its cause key rests on DONKI
  (weakened key).
- The G3 storm of 2026-10-10 (GFZ nowcast Kp 7+ at 15:00 UTC) is missing: the build read Kp only to 2026-10-09.
  Rebuilding with `normalized/gfz_kp` adds it to TEST and fills Kp for J160. Approved by Arek 2026-10-12; the
  event-set thread runs it.
- Resolved 2026-10-11: the 3 period entries were replaced by 29 rtgms.pl episodes (J132–J160); see `decisions.md`.
- Time zone of rtgms.pl times (UTC or Polish time) is unconfirmed; it shifts t0 of J132–J160 by up to 2 h. Kp is
  checked from alarm start minus 2 h, so the Kp-based labels do not depend on it.
- J155 (BRWO 2026-08-23 19:17–19:25) has exactly the same clock times as WIKO 2026-07-18; possible transcription slip.
- J160 (BRWO 2026-10-10) has no Kp yet (Kp data end 2026-10-09); rerun the build after the next Kp download.
- Resolved 2026-10-11 (Arek): rtgms.pl shows Polish local time (CEST = UTC+2 for all alarms in 05–10/2026). J132–J160
  are now in UTC; the new column `poczatek_rtgms_pl` keeps the time shown on the site. IDs and DEV/TEST are unchanged;
  Kp changed in 10 episodes but none reached 5-. J140/J141 start 32 min after the DONKI shock at 12:06 UTC, which their
  key now notes.
- Resolved 2026-10-11 (Arek): J155 (BRWO 2026-08-23) and J151 (WIKO 2026-07-18) are correct readings, not a
  transcription slip.
- Resolved 2026-10-12 (rebuild, Arek: yes): J160 now has Kp 4- (12–15 UT, preliminary). Its alarm ended 1 h 44 min
  before the DONKI shock at 14:33 UTC, so its key stays "not space weather".
- B161 (G3, 2026-10-10): Kp is preliminary and the Kp data end with the 2026-10-10 21:00 bin, so the storm's end (at
  least 2026-10-11 00:00) and level are provisional. Rerun the build after the next GFZ download. Its cause key is
  CME from DONKI only (weakened), because the Richardson–Cane and ISGI SSC lists do not reach October 2026.
- The NOAA proton-event list ends on 2026-07-30, but DONKI has a GOES proton event on 2026-09-05. No event in the set
  has it in its window; re-download the NOAA list before the next rebuild.
- 2026-10-17, RINEX test of J140/J141 (rtgms.pl alarm 2026-06-05 12:38–12:45 UTC at BRWO and WIKO): ASG-EUPOS
  RINEX 3.02 at 30 s from POZGEO D (BRWO, WIKO and REDZ as a control, 11:00–16:00 GPS time) has C/N0 (S) observables
  for GPS, GLONASS, Galileo (E6 empty) and BeiDou. In the alarm window the per-band median C/N0 drops by less than
  1 dB-Hz (as in the hour before), tracked satellites and loss-of-lock flags match the hour before, and ROTI (elevation >= 30 deg) stays at
  0.03–0.08 TECU/min. Neither jamming strong enough to show in 30 s data nor ionospheric irregularities are visible.
  Only trace: a common ~0.7 dB-Hz drop in L5/E5a and E5b at all three stations at 12:38:30 GPS time (the only such
  epoch in those bands in 5 h; similar common drops occur in other bands at other times). Open: whether POZGEO D
  offers 1 s data for June 2026, since short bursts between 30 s epochs are not excluded. If not, the system would get
  no RINEX symptom for this alarm. Keys unchanged. Analysis: Claude project files, `metodologia/rinex_test`.
- Resolved 2026-10-17: POZGEO D does give 1 s data (at most 14 400 epochs per order). In 1 s files (BRWO, WIKO, WLAD,
  12:15–13:15 GPS time) the J140/J141 alarm shows as a common C/N0 drop in the L5/E5a band at about 12:37:40–12:38:40
  GPS time: ~1 dB-Hz at BRWO (16 of 17 satellites), ~0.5 dB-Hz at WIKO, weaker in E5b, nothing unusual in L1, L2 or B3,
  quiet ROTI, no extra loss of lock. It is the lowest L5 moment in each file (also at REDZ in the 30 s data). Reading:
  RF interference in the L5 band, not the ionosphere; key unchanged. The symptom is weak and lasts ~1 min (the rtgms.pl
  alarm lasts 7 min), so it needs 1 s data and a statistic over all satellites of a band. WLAD (Leica) records C/N0
  in whole dB-Hz and has gaps, so it does not help.
- 2026-10-17, POZGEO D archive depth: a 1 s order for BRWO on 2025-01-01 12:00-13:05 GPS time (3900 epochs) came
  back with no missing epochs and the same C/N0 (S) observables as in 2026. So 1 s data reach at least January 2025,
  which covers all of TEST and all rtgms.pl alarms. Years before 2025 (DEV storms) are untested. The order list for
  the 27 remaining rtgms.pl alarms (1 s, two stations) and the 13 TEST G3+ storms (BRWO, 30 s) is in the Claude
  project files, `metodologia/rinex_test/zamowienia_pozgeo_d.md`.
- 2026-10-24, RINEX for the rtgms.pl alarms: all 27 POZGEO D orders are on the laptop (plus Order_2.zip for
  J140/J141). Every zip has BRWO and WIKO, nav files and order summaries, correct CRCs and all epochs without gaps.
  To re-order: J132 (came as RINEX 2.11, which the script cannot read) and J144, J146, J147, J148, J149 (their
  30-min windows end 2-9 min before the alarm starts). Intervals are mixed: 1 s (J133, J134, J136-J138, J140, J141),
  2 s (J135), 5 s (J139, J142-J160). J140's 1 s data thinned to 2 s and 5 s give the same L5 result (BRWO dip
  1.0-1.1 dB-Hz, lowest 20 s block z = -4.8), so 5 s is enough for this kind of symptom. Details: Claude project
  files, `metodologia/rinex_test/kontrola_zamowien_alarmy.md`.
- Resolved 2026-10-24: after two rounds of re-orders (J132, J144, J146-J149) the RINEX set for all 29 rtgms.pl
  alarms is complete and correct: 27 zips plus Order_2.zip, all RINEX 3, BRWO and WIKO, correct CRCs, all epochs,
  no gaps. Every window starts at least 30 min before its alarm (J140/J141: 23 min) and covers the alarm start.
  Intervals: 1 s (J133, J134, J136-J138, J140, J141), 2 s (J132, J135, J144, J146-J149), 5 s (the rest).

## After the 2026-11-13 advisor meeting (Arek decides unless noted)

- Does optional variant D (NOAA forecaster text) stay, or is it dropped with B under "simple thesis, no hybrids"?
- Output of each scenario: only the incident type (with probability), or also the cited Polish explanation for A and
  C? The decision model returns choices with probabilities, not text.
- How "quality" is scored: accuracy/F1 of the chosen incident type against an answer key. The 158-event set has cause
  and effect keys, not catalogue incident types; decide whether to map events to catalogue types or build a new set.
- How "cost" (API cost per run, tokens) and "time" (latency per daily analysis) are measured, and on which hardware.
- Daily cadence vs event-based t0: is the evaluation one analysis per day (t0 = fixed daily time) or per event?
- Which decision model if not Jev, and which classic LLM (extends the existing LLM question above).
- Incident types without a confirmed source (draft types 1.3, 1.4, 3.2, 3.3, 4.1 and class 5 "GNSS satellites"):
  keep searching or drop.
- Table of contents v2 (`praca_magisterska/spis_tresci.md`), name "model decyzyjny": TypeSafe asks to call Jev a
  "System One model", not a "decision model" (blog post 2026-11-03,
  https://typesafe.ai/blog/dont-call-it-a-decision-model). The title and ToC 3.3, 4.3, 5.4 say "model decyzyjny".
  Keep, rename, or explain in 3.3? Possibly a question for the advisor.
