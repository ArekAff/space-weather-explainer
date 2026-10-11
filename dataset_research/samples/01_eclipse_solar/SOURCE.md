# 01 – Solar eclipses in irradiance and PV generation

**Business use (primary case):** a PV owner, O&M firm or trader sees output far below the forecast. The platform recognises the eclipse signature, matches it to the eclipse catalogue and ENTSO-E guidance, and labels it "external, no dispatch". Without that, it would raise a fault alarm. The same pattern applies to curtailment, Saharan dust and snow. KPIs: false dispatches avoided, lost MWh attributed by cause, imbalance cost explained.

This is the closest match to the motivating example: sunlight data with a dip that only an
astronomical explanation can account for.

## Files

| File | What | Resolution | Source / retrieval |
|---|---|---|---|
| `energy_charts_DE_2015-03-19_to_21_15min.csv` | Germany: solar, load, onshore wind [MW] | 15 min, UTC | Energy-Charts API `https://api.energy-charts.info/public_power?country=de&start=2015-03-19&end=2015-03-21`, retrieved 2026-10-10 |
| `energy_charts_DE_ES_PL_solar_2026-08-11_to_13_15min.csv` | Solar generation in Germany, Spain, Poland [MW] | 15 min, UTC | same API, `country=de/es/pl`, 2026-08-11..13 |
| `zurich_irradiance_and_load_2015-03-13_to_27_15min.csv` | Zurich global irradiance `StrGlo [W/m2]`, temperature, pressure, plus city electricity use | hourly weather interpolated to 15 min, UTC | Darts dataset `ElectricityConsumptionZurichDataset` (GitHub `unit8co/darts`), originally Open Data Zürich (ewz consumption, UGZ station Stampfenbachstrasse) |
| `plot_eclipse_examples.png` | Figure, made by `scripts/make_sample_plots.py` | | |

Notes
* Energy-Charts data are free for non-commercial / journalistic use with the credit **"Energy-Charts / Fraunhofer ISE"**.
  The underlying numbers come from ENTSO-E and TSOs.
* Spain's `es_solar_MW` is not zero at night because it includes concentrated solar power, which has thermal storage.
* The Zurich weather data are hourly values that Darts interpolated to 15 min, so the eclipse dip is smeared
  and shows at the 09:00 UTC point. For research-grade work use 1-min stations: BSRN, NREL MIDC,
  DWD 10-min stations, or Open Data Zürich directly.

## The events (ground truth with expert explanation)

| Event | What the data show | Expert explanation / source |
|---|---|---|
| Partial solar eclipse, 20 Mar 2015 | German PV falls from 13.2 GW (08:30 UTC) to 6.2 GW (09:30 UTC), then recovers to 18.9 GW by 10:45 UTC. Zurich irradiance dips to ~215 W/m² against ~530 W/m² the day before. | ENTSO-E *Solar Eclipse Impact Analysis* (Feb 2015): Germany eclipse 08:33–10:52 UTC, expected PV reduction in Germany 16.9 GW under clear sky, gradients down to −273 MW/min and up to +361 MW/min. EclipseWise local circumstances: Bern 08:24–10:44 UTC, max 09:32, magnitude 0.751, obscuration 69.6 %; Warsaw 08:47–11:07 UTC, max 09:57, obscuration 66.2 %. |
| Total eclipse over N. Spain, 12 Aug 2026 (at sunset) | Spain solar at 18:00 UTC is 4.97 GW against 9.08 GW (day before) and 6.78 GW (day after). Germany at 18:00 UTC is 0.12 GW against 1.85 / 1.50 GW. Poland shows almost nothing, because the sun had nearly set. | ENTSO-E press release (7 Aug 2026): eclipse window 19:15–21:30 CEST, up to 9.7 GW PV reduction in Europe under clear sky, Spain and Germany most affected. Wikipedia: greatest eclipse 17:47 UTC; totality in Spain ~20:27–20:33 local; Warsaw max coverage 81.7 % at 20:02 local, about sunset. |

This explains the Polish case: an eclipse that happens at sunset produces almost no PV anomaly.
The system has to reason about the eclipse together with the solar elevation, not just flag the date.

## Where the knowledge lives (open)
* NASA Eclipse Web Site (F. Espenak): five-millennium catalogue of eclipses and local circumstances. It works as a
  machine-readable "known event" list. https://eclipse.gsfc.nasa.gov/
* EclipseWise city tables (Espenak), e.g. https://business.eclipsewise.com/oh/oh-tables/ec2015-Tab02a.pdf
* ENTSO-E 2015 report: https://eepublicdownloads.entsoe.eu/clean-documents/Publications/SOC/150219_Solar_Eclipse_Impact_Analysis_Final.pdf
* IEA PVPS Task 14 report on the 2015 eclipse in Germany: https://apvi.org.au/wp-content/uploads/2016/08/PVPS-_T14-06_2016_EuropeanSolarEclipse2015inGermany.pdf
* ENTSO-E 2026 press release: https://www.entsoe.eu/news/2026/08/07/transmission-system-operators-prepare-for-solar-eclipse-to-ensure-secure-system-operation/
* Solar-geometry knowledge (sun position, clear-sky models) is implemented in `pvlib` (open source) and explained in
  Stull, *Practical Meteorology* (free, Creative Commons), chapter on solar radiation.

## How to get more
`scripts/fetch_official_data.py energy_charts --country de --start 2015-03-01 --end 2015-03-31`.
The Energy-Charts API covers many European countries from 2015 at 15-min or hourly resolution.
