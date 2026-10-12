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
