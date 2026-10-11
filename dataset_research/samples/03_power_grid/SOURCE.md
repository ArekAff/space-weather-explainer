# 03 – Power grid operation

**Business use:** post-incident analysis for TSOs, generators and traders ("what happened at 12:33 and has it happened before?"), and data-quality alerts for anyone consuming grid data. The PSE file is the Polish 15-min data that the primary PV business case runs on. Since 14 Jun 2024 Polish imbalances are settled per 15 min, so unexplained deviations cost money.

## Files

| File | What | Source |
|---|---|---|
| `energy_charts_ES_2025-04-27_to_29_iberian_blackout_15min.csv` | Spain: load, solar, nuclear, onshore wind, gas, reservoir hydro, cross-border trade [MW], 15 min, UTC | Energy-Charts API `public_power?country=es&start=2025-04-27&end=2025-04-29` (credit "Energy-Charts / Fraunhofer ISE"; data from ENTSO-E / Red Eléctrica), retrieved 2026-10-10 |
| `pse_PL_demand_pv_wind_2026-08-11_to_13_15min.csv` | Poland: demand, PV, wind [MW], 15 min; the timestamp is the **end** of the interval in UTC | PSE API v2 `https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date eq 'YYYY-MM-DD'` (report "Praca KSE – wielkości podstawowe"), retrieved 2026-10-10 |
| `plot_iberian_blackout.png` | Figure | |

## Events
**28 Apr 2025, Iberian blackout.** At 12:33 CEST (10:33 UTC) the Iberian peninsula lost synchronism with the
continental grid and collapsed. In the data, nuclear drops from 3.4 GW to 0 and stays at 0 for more than a day,
gas and hydro collapse and then ramp up overnight during restoration, and the *load* series becomes missing.
The solar series keeps ~5 GW after the collapse, which is physically implausible for a black system and is most
likely an artefact of the reporting chain. It is a good example of data-quality anomalies the system must also
recognise and explain.

Expert explanation: the ENTSO-E Expert Panel final report (March 2026, ~440 pages) describes the voltage-control
and reactive-power deficiencies, the rapid chain of generation disconnections (e.g. 727 MW at 12:33:16 in
Badajoz), the loss of synchronism at 12:33:19, and 22 recommendations. Portal:
https://www.entsoe.eu/publications/blackout/9-may-2025-iberian-blackout/

**12 Aug 2026, eclipse at sunset (Poland).** The PSE data show almost no PV effect because the maximum in Warsaw
(81.7 % coverage at 20:02 local) coincided with sunset. It is a negative example: an event happened, but no
anomaly should be flagged.

## Other well-documented grid events (all with free ENTSO-E reports)
* 8 Jan 2021 Continental Europe system split (frequency deviation, ENTSO-E final report)
* 24 Jul 2021 France–Iberian separation
* 4 Nov 2006 European disturbance (UCTE final report)
* Eclipses 2015, 2022, 2026; COVID-19 lockdown load drop (Mar–Apr 2020); holidays; big TV events

## Polish-specific sources
* PSE "Raporty" (API v2 from 14 Jun 2024; historical CSV reports for earlier years at https://www.pse.pl/raporty-historyczne)
* URE and ARE annual reports; PSE "Raport z funkcjonowania KSE"
* SGH access: *IEA Electricity Information Statistics* (login) for monthly national statistics
