# 13 – Long energy series (for multi-timeframe similarity search)

**Business use:** the history needed to find analogues ("when did demand or solar behave like this before, and what
happened next?") for the primary PV/energy business case. The short event samples in folders 01 and 03 are too short
for that.

## Files (gzip-compressed CSV; `pandas.read_csv` opens them directly)
| File | What | Source |
|---|---|---|
| `zurich_electricity_weather_2015-2022_15min.csv.gz` | City of Zürich electricity use, 15 min, 2015-01-01 → 2022-08-31, UTC. `Value_NE5` = households & SMEs (low voltage) and `Value_NE7` = business & services (medium voltage), in kWh per 15 min. Plus weather from station Zch_Stampfenbachstrasse (hourly, interpolated to 15 min): global irradiance `StrGlo [W/m2]`, temperature, humidity, pressure, wind, rain duration | Darts `ElectricityConsumptionZurichDataset` (github.com/unit8co/darts, Apache-2.0), built from Open Data Zürich (ewz electricity, UGZ meteo) |
| `spain_energy_entsoe_2015-2018_hourly.csv.gz` | Spain, hourly 2015–2018: generation by type (incl. `generation solar`), load, TSO forecasts, day-ahead and actual prices | Darts `EnergyDataset`, originally the Kaggle dataset "Hourly energy demand generation and weather" compiled from ENTSO-E and Red Eléctrica |

## Events inside (for evaluation)
* 20 Mar 2015 partial solar eclipse (both files; visible in Zürich irradiance and in Spanish solar on a cloudy day)
* 16 Mar 2020 Swiss COVID-19 "extraordinary situation" (lockdown): business electricity use drops 10–15 %
* Christmas / New Year and school holidays every year; Easter; summer holidays
* Heat waves (e.g. summer 2015, 2018, 2019, 2022) in temperature and load

Used by `scripts/multi_timeframe_search.py` (demos "lockdown analogues" and "eclipse morning").
