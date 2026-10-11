# 09 – River levels and flows in Poland, September 2024 flood (IMGW)

**Business use:** insurers and reinsurers, municipalities, Wody Polskie and logistics firms. Analog search ("this rise looks like the start of 1997/2024"), linked to IMGW warnings, gives early exposure estimates and supports claims triage. The September 2024 flood produced over 131,000 claims and PLN 2.13 bn of settled claims (KNF, as of 30 Jun 2025). Detecting a gauge failure during an event is also a sellable feature.

## File
`imgw_hydro_daily_HY2024_odra_nysa_flood.csv` holds the daily mean water level [cm] and discharge [m³/s] for the
whole **hydrological year 2024** (1 Nov 2023 – 31 Oct 2024) at six gauges:

| Column prefix | Gauge (IMGW code) | River |
|---|---|---|
| `klodzko` | KŁODZKO (150160180) | Nysa Kłodzka |
| `nysa` | NYSA (150170060) | Nysa Kłodzka |
| `glucholazy` | GŁUCHOŁAZY (150170070) | Biała Głuchołaska |
| `opole_groszowice` | OPOLE-GROSZOWICE (150170290) | Odra |
| `raciborz_miedonia` | RACIBÓRZ-MIEDONIA (150180060) | Odra |
| `brzeg_dolny` | BRZEG DOLNY (151160170) | Odra |

Source: IMGW-PIB public data, `https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_hydrologiczne/dobowe/2024/codz_2024.zip`
(the format is described in `CODZ_publiczne_format.txt` in the same folder). Retrieved 2026-10-10. Empty cell = no data.

**Required attribution (IMGW regulations § 5):** "Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki
Wodnej – Państwowy Instytut Badawczy". Because this file is a processed extract, also add: "Dane Instytutu Meteorologii
i Gospodarki Wodnej – Państwowego Instytutu Badawczego zostały przetworzone".

## What the data show (`plot_flood_wave_sep2024.png`)
* The flood wave travels downstream. Daily mean peaks: Kłodzko 669 cm (15 Sep), Nysa 616 cm (16 Sep),
  Racibórz-Miedonia 793 cm (17 Sep), Opole 660 cm (18 Sep), Brzeg Dolny 946 cm (20 Sep).
  Similarity search should find the *same shape shifted in time* along the river.
* **Daily means hide the peak.** IMGW reported an instantaneous 798 cm at Kłodzko, ~143 cm above the 1997 record
  (655 cm), and said the automatic sensor there was damaged by the water (Rzeczpospolita, 16 Sep 2024).
* **Missing data are an event too.** The Głuchołazy series stops on 15 Sep 2024 at 432 cm, during the flood, when the
  town was flooded and IMGW reported damage to its measuring infrastructure. A good system should explain a gap, not
  only a spike.

## Knowledge sources
* IMGW-PIB reports and communiqués on the September 2024 flood (Genoa low "Boris", record rainfall in the Sudetes),
  the monthly *Biuletyn Monitoringu Klimatu Polski* and the annual *Klimat Polski* reports (free PDFs)
* Wody Polskie reports on reservoir operations (Nysa, Otmuchów, Racibórz Dolny dry polder)
* Comparisons with the 1997 "Millennium flood" and 2010 floods. There is a lot of Polish scientific literature;
  search *Bibliografia Geografii Polskiej*, *BazTech*, *Biblioteka Nauki*, *CEON* (all free, on your SGH list)
* Copernicus EMS rapid-mapping activations (satellite flood maps)

More data: all ~900 gauges since 1951 (daily) in the same IMGW folder; 10-min operational data via the IMGW API
(current only); synoptic weather data since 1951 (`dane_meteorologiczne`).
