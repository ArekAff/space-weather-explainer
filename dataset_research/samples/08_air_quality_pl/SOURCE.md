# 08 – Air quality in Poland (GIOŚ)

**Business use (mostly public sector):** cities and voivodeships must inform the public about exceedances and justify measures such as anti-smog rules. Building and HVAC operators and health apps want to know the cause and expected duration. The platform separates a short fireworks spike from a multi-day heating-smog episode and cites the reason.

## File
`gios_pm_hourly_waw_krk_2024-12-28_to_2025-01-04.csv` has hourly PM2.5 and PM10 [µg/m³] at
Warszawa, Al. Niepodległości (station 530, sensors 3585/3584) and Kraków, Al. Krasińskiego (station 400,
sensors 2752/2750). Times are **CET** (UTC+1); the value stamped HH:00 is the mean of the preceding hour.
Retrieved 2026-10-10 from the GIOŚ API v1:
`https://api.gios.gov.pl/pjp-api/v1/rest/archivalData/getDataBySensor/{sensorId}?dateFrom=YYYY-MM-DD HH:MM&dateTo=...`
(at most 366 days per request; station list `/v1/rest/station/findAll`, sensors `/v1/rest/station/sensors/{stationId}`).
Documentation: https://api.gios.gov.pl/pjp-api/swagger-ui/. Data: Państwowy Monitoring Środowiska, GIOŚ.
Raw automatic data are not fully verified; GIOŚ publishes the verified annual data in its "Bank danych pomiarowych".

## Two kinds of anomaly, two explanations
| Pattern | Example in file | Explanation |
|---|---|---|
| 1-hour spike right after midnight, in both cities | Warsaw PM2.5 65.7 µg/m³ at 01:00 on 1 Jan 2025 (≈ 2× surrounding hours) | New Year's fireworks |
| Multi-hour build-up, evening maximum, slow decay | Kraków PM2.5 ~90 µg/m³ on the evening of 29 Dec 2024 | Winter smog: domestic solid-fuel heating plus a temperature inversion and low wind. Kraków's basin location makes it worse. |
| Sharp drop on 2 Jan 2025 | Both cities fall below 10 µg/m³ | Change of air mass, wind and precipitation (check IMGW synoptic data) |

Knowledge sources: GIOŚ annual "Ocena jakości powietrza w strefach w Polsce" reports, the EEA "Air quality in Europe"
reports (free), WHO 2021 air-quality guidelines, IMGW meteorological data and bulletins for the meteorological
context, and Polish research in *Biblioteka Nauki* / *BazTech* (both free, on your SGH list).

Other events worth adding: Saharan dust episodes, smoke from Canadian wildfires transported over Europe (e.g. early June 2025), and COVID-19 lockdown NO₂ drops (spring 2020).
