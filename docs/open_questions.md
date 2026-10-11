# Open questions

Items that agents must not treat as settled. When one is answered, move it to `decisions.md` with the date and the
answer. Grouped by where the answer will come from.

## Answered by trying it (first download)

- Hp30 start: 1985 (Hpo V3.0, as in the advisor e-mail) or 1995 (access table)? Check on the GFZ site.
- Does the DONKI API return archived notifications and weekly reports, and from what date? Which entry types carry
  `submissionTime`?
- Format of issue-time headers in SGAS, RSGA and The Weekly across 1996–2026.
- Is pre-1996 RSGA only scanned PDF (needs OCR)? Test a sample.
- Does IGS publish ROTI maps for Europe on CDDIS, or must ROTI be computed from TEC or RINEX? Check after creating the
  Earthdata account.
- Every NOAA live endpoint in `data_gathering_plan.md` is untested.

## Arek decides

- Kp history from 1957 (as in the e-mail) or from 1932? If 1957 stays, the thesis needs one sentence of justification
  (e.g. alignment with OMNI from 1963).
- Definition of t0 in the main mode. Default: the moment the platform first detects the anomaly (first Kp/Hp30
  threshold crossing); for storms in the event set, onset + 3 h.
- Where the NOAA collector runs: the laptop via Task Scheduler (default; the 7-day buffer covers short gaps) or an
  always-on machine for full continuity of alerts and texts.
- Use of the 7 storms marked SPORNE (catalogues disagree): score against Richardson–Cane, or exclude them and say so.
- Which LLM and embedding model to use, and whether to pin their versions for the whole evaluation.

## Advisor (Prof. Surma) or outside parties

- Data freeze date (default 2026-12-31).
- E-mail to CCMC about using DONKI for validation (recommended by CCMC policy).
- E-mail to GUGiK / IŁ-PIB asking for the RTGMS interference archive.

## Evaluation event set: known gaps

- 3 jamming entries from 2026 are periods, not single days; exact days and hours must be read from rtgms.pl.
- The GUGiK notice about Siedlce on 2026-06-30 could not be found again; marked "to confirm".
- Effect sources for the 03/2015 and 09/2017 storms came from memory and are unverified; check before citing.
- One TEST storm (2026-08-18) falls after the end of the Richardson–Cane list, so its cause key rests on DONKI
  (weakened key).
