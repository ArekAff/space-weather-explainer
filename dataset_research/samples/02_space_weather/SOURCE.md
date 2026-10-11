# 02 – Space weather (geomagnetic indices, sunspots, solar radio flux)

**Business use:** operators that depend on GNSS, HF radio or satellites (precision agriculture and RTK networks, surveying and drones, airlines, satellite operators, parametric insurers) need to know whether a problem is caused by space weather and how bad it may get. During the May 2024 storm, agricultural economists estimated ~$500 M of losses to US farmers whose GNSS-guided machinery could not work (UCAR/CPAESS). The similarity search below answers "how severe were the most similar past storms?".

## Files

| File | What | Resolution / span | Source |
|---|---|---|---|
| `celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv` | 8 × 3-hourly Kp, Kp sum, 8 × ap, daily Ap, international sunspot number (ISN), F10.7 solar flux (adjusted and observed) | daily rows, 1957-10-01 → 2025-07-20 (24,765 days) | CelesTrak `SW-All.txt` (T.S. Kelso), as bundled in the PyPI package `spaceweather` 0.4.2. Kp/ap are from GFZ Potsdam (CC BY 4.0), ISN from SILSO, F10.7 from NRCan. |
| `gfz_Hp30_2024-05-07_to_14_gannon_storm.csv` | Hp30, GFZ's open-ended 30-min Kp-like index | 30 min, 7–14 May 2024 | GFZ Kp/Hpo API `https://kp.gfz.de/app/json/?start=...&end=...&index=Hp30&status=def`, retrieved 2026-10-10. Licence CC BY 4.0 ("GFZ Potsdam"). |
| `similarity_search_gannon_top10.csv` | Output of the query-by-example demo (see below) | | made by `scripts/make_sample_plots.py` |
| `plot_space_weather.png` | Figure | | |

Kp values are written in decimal thirds: 7.7 = 7+ (7.667), 8.3 = 8+ … The CelesTrak file stores Kp×10.

## Events and their expert explanations

| Moment in data | Explanation | Open source |
|---|---|---|
| 10–11 May 2024, Hp30 reaches 11.33 and daily Ap is 271 (second-highest day since 1957) | "Gannon" storm, a series of CMEs from active region 13664. NOAA observed G5 (extreme) at 22:54 UTC on 10 May. | NOAA SWPC news item; GFZ paper by Yamazaki et al. 2024 (ESS Open Archive, doi:10.22541/essoar.171838396.68563140/v1) |
| 13 Mar 1989, Ap 246 | Storm that caused the Hydro-Québec blackout | NOAA / NASA educational pages; many open papers in *Space Weather* (AGU, open access) |
| 29–31 Oct 2003, Ap 204 | "Halloween storms" | NOAA SWPC service assessment (free PDF) |
| 13 Nov 1960, Ap 280 (highest day in file) | Great storm of solar cycle 19 | literature (JSTOR / Wiley via SGH) |
| ~11-year oscillation in ISN | Solar (Schwabe) cycle | SILSO; OpenStax *Astronomy 2e*, ch. 15 (but see its AI-use restriction in the report) |
| 27-day recurrences | Solar rotation, recurrent coronal-hole high-speed streams | NOAA SWPC "Space Weather Scales" and education pages |

## Proof-of-concept: "find moments similar to this one"
`similarity_search_demo()` slides the 3-day Kp pattern starting 2024-05-10 12:00 UTC over all 198,000
3-hourly values since 1957. It uses STUMPY's MASS with non-normalised Euclidean distance, so magnitude matters.
The ten nearest non-overlapping windows are all severe-to-extreme historical storms (max Kp between 7+ and 9):
12 Nov 1960, 31 Mar–1 Apr 1960, 4–5 Jun 1991, 6 Oct 1960, 16 Aug 1959, 4 Aug 1972, 20 Oct 1989,
28 Oct 1991, 14 May 1969 and 13 Jul 1982. Each can be looked up in storm catalogues and the literature
(e.g. the August 1972 and October 1989 storms are widely studied). This is exactly the
retrieve-similar-then-explain loop the system needs. The famous 13 Mar 1989 and Oct 2003 storms are *not*
in the top 10, because their 3-day shape differs. That is a good thesis discussion point about
window length and distance choice (z-normalised vs raw, DTW).

## More data
* GFZ: Kp since 1932, open-ended Hp30/Hp60 indices (CC BY 4.0), https://kp.gfz.de/
* NASA OMNIWeb: solar wind and IMF, hourly since 1963 and 1-/5-min since 1981 (public domain)
* NOAA SWPC JSON feeds (real time) and GOES X-ray flux (solar flares)
* Kyoto WDC Dst index; SuperMAG magnetometers (free registration)
* Natural pairing: magnetometer and ionosphere data plus power-grid GIC reports.
