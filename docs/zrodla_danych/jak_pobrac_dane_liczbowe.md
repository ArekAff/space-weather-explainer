# Numeric data (section 5a of the email): what each source is for and how to download it

Written 11 Oct 2026. The details come from the access table [dostep_do_zrodel_danych.xlsx](dostep_do_zrodel_danych.xlsx) and my own knowledge of these services. These sites can't be reached from the cloud session. The GFZ JSON API and the OMNI HAPI request were already used on your laptop to download the data in `dataset_research\space_weather_decision\data` (see the manifests there). The rest is untested, so try each command once before you rely on it.

**Already on your laptop:** CelesTrak daily Kp/Ap/sunspots/F10.7 1957–2025 in `dataset_research\samples\02_space_weather\`, and a merged file up to 2026-10-09 in `space_weather_decision\results\`.

## How the three sources fit together

| Source | What it tells the platform | Role | Period | Live? |
|---|---|---|---|---|
| GFZ Potsdam Kp / ap / Ap / Hp30 | How strong the geomagnetic disturbance is at Earth (storm level G1–G5) | The main time series: detecting storms and anomalies, finding similar past situations, "what happened next", labels | Kp since 1932 (the email uses 1957–2026), Hp30 since 1995 | Yes (nowcast, values marked preliminary) |
| NOAA SWPC | The same storm level live, the solar wind measured at L1 about 30–60 min before it reaches Earth, alerts and 3-day forecasts | Live feed ("real time") and the official forecast to compare against | Live files cover only the last 1–7 days | Yes |
| NASA OMNI | Solar wind speed, density and magnetic field (Bz) arriving at Earth, the **cause** of a storm | Extra features for finding similar situations in history | 1963 to about a week ago | No (several days' delay) |

In short:
- **GFZ** tells you **what happened** at Earth.
- **OMNI** tells you **why** it happened (history).
- **NOAA** provides both **right now**.

Kp on its own did not predict the course of a storm better than simple climatology. Information about the cause (solar wind, shock) is what improved the forecast. That's why you need OMNI for history and NOAA for live use.

## 1. GFZ Potsdam (no registration, CC BY 4.0)

**The whole history in one file** (Kp, ap, Ap, sunspot number and F10.7 since 1932, updated daily):
```
https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt
```
Hp30/Hp60 (Hpo V3.0 from 1985): the download page is https://kp.gfz.de/en/hp30-hp60 (complete-series files).

**JSON API** (any time range and index):
```python
import requests, pandas as pd
r = requests.get("https://kp.gfz.de/app/json/", params={
    "start": "1957-10-01T00:00:00Z", "end": "2026-10-10T00:00:00Z",
    "index": "Kp",          # also: ap, Ap, Hp30, ap30, Hp60, SN, Fadj ...
    "status": "def"})      # "def" = definitive only; omit it to include preliminary values
d = r.json()
kp = pd.Series(d["Kp"], index=pd.to_datetime(d["datetime"]))
```
GFZ also publishes a ready Python client (`getKpindex`) on the same site. For live use, poll the API every 3 h (Hp30 every 30 min). Save the `status` field, because preliminary values are corrected later.

**Alternative long daily file (CelesTrak, 1957 to today):** https://celestrak.org/SpaceData/SW-All.csv. It includes the sunspot number and F10.7, which give the solar-cycle phase.

If a long API range is refused, request one year at a time.

## 2. NOAA SWPC (no registration or key, public domain)

Live files (overwritten all the time, they **do not keep history**):
```
https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json     # Kp, last 7 days
https://services.swpc.noaa.gov/json/planetary_k_index_1m.json           # estimated Kp, every minute
https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json    # solar wind speed and density at L1
https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json       # magnetic field (Bz) at L1
https://services.swpc.noaa.gov/text/3-day-forecast.txt                  # official 3-day forecast
```
```python
import requests, pandas as pd
rows = requests.get("https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json").json()
sw = pd.DataFrame(rows[1:], columns=rows[0])   # the first row holds the column names
```
**What you need to do:** run a small collector (cron or a scheduled task) that downloads these files every few minutes and appends them to your own database. Without that, the platform has no history of the live data.

**History of forecasts and reports:** NCEI archive at https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/. 3-day forecasts start in 03/2022. The RSGA reports, with forecast Ap, go back to 1966. Bulk download with `wget -r`.

## 3. NASA OMNI (no registration; cite DOI 10.48322/1shr-ht18)

**Easiest option, the whole history as text files** (one file per year, or all years in one):
```
https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_2024.dat
https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_all_years.dat
```
The column layout is in `omni2.text` in the same folder. Missing values are written as 9s (e.g. 999.9).

**HAPI** (any time range, returns CSV):
```python
# pip install hapiclient
from hapiclient import hapi
server = "https://cdaweb.gsfc.nasa.gov/hapi"
data, meta = hapi(server, "OMNI2_H0_MRG1HR", "", "1963-01-01T00:00:00Z", "2026-10-01T00:00:00Z")
# the empty string fetches all parameters; the list of names is in meta (or /hapi/info?id=OMNI2_H0_MRG1HR)
```
Request that has already worked (one year at a time; keep the parameters in this order, otherwise HAPI returns error 1411):
```
https://cdaweb.gsfc.nasa.gov/hapi/data?id=OMNI2_H0_MRG1HR&parameters=ABS_B1800,BZ_GSM1800,N1800,V1800,Pressure1800,R1800,F10_INDEX1800,KP1800,DST1800,AE1800&time.min=2024-01-01T00:00:00Z&time.max=2025-01-01T00:00:00Z&format=csv
```
1-minute data since 1981: dataset `OMNI_HRO_1MIN` on the same server. It is large, so download it only for storm windows. OMNI arrives with a delay of several days, so in live mode the same quantities come from NOAA SWPC (point 2).

Rough sizes: Kp since 1932 is about 280k rows, Hp30 since 1985 about 720k rows, and OMNI hourly about 560k rows. All of it fits in a few CSV or Parquet files on a laptop.

## Suggested order of work

1. Download the full GFZ file (Kp since 1932) and OMNI `omni2_all_years.dat` once, and load both into one table indexed by time (every 3 h; OMNI hourly values averaged to 3-hour bins).
2. Add Hp30 for the storms you want to look at in detail.
3. Start the NOAA collector so the platform builds up its own live archive from today.
4. Keep a `source` and `status` (preliminary or definitive) column for every value, and refresh the last few weeks after GFZ corrects them.
