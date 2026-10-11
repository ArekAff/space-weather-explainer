# 07 – Global pressure wave from the Hunga Tonga–Hunga Ha'apai eruption (15 Jan 2022)

**Business use:** sensor-network operators (weather stations, IoT, industrial pressure sensors) must tell a sensor fault from a real but remote cause. Here a simultaneous jump across stations explained by an eruption means "do not replace the sensor".

## File
`iem_asos_1min_DSM_pressure_2022-01-15_hunga_tonga.csv` holds 1-minute station pressure (inHg; × 33.8639 = hPa)
at Des Moines airport (DSM, Iowa, USA), 15 Jan 12:00 – 16 Jan 11:59 UTC.
Retrieved 2026-10-10 from the Iowa Environmental Mesonet ASOS 1-minute service:
`https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py?station=DSM&vars=pres1&sts=...&ets=...&sample=1min&what=view&tz=UTC`
(ASOS data from NOAA/FAA are public domain; credit the Iowa Environmental Mesonet).

## What it shows
After subtracting a 2-hour running mean (`plot_hunga_tonga_pressure.png`):
* **~14:00 UTC, 15 Jan:** +0.6 hPa then −0.5 hPa. This is the Lamb wave arriving on the direct path,
  ~9.75 h after the eruption (~04:15 UTC), from ~10,850 km away. That implies ≈ 309 m/s.
* **~06:55 UTC, 16 Jan:** a −0.9 hPa excursion followed by a rise. This is the wave arriving the *long way around*
  the globe (~29,200 km, ≈ 304 m/s).

Nothing in local weather explains these blips. Only volcanology and atmospheric-wave physics (Lamb waves travel at
~310–320 m/s) does, which makes this a textbook "anomaly that needs expert knowledge".

## Knowledge sources (open)
* Matoza et al. (2022) *Science* 377, "Atmospheric waves and global seismoacoustic observations of the January 2022
  Hunga eruption, Tonga"
* Wright et al. (2022) *Nature* 609, "Surface-to-space atmospheric waves from Hunga Tonga–Hunga Ha'apai eruption"
  (pressure data on Zenodo, record 6575810)
* University of Reading dataset of ~50 UK/Irish barographs at 1 min (doi:10.17864/1947.000359)
* Smithsonian Global Volcanism Program weekly reports (eruption catalogue for the "known events" list)

Polish angle: IMGW synoptic stations report pressure hourly, which is too coarse. Amateur or Netatmo networks and
1-min research stations show the wave over Poland in the evening of 15 Jan 2022.
