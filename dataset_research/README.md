# Data for a knowledge-grounded time-series anomaly & similarity search platform

*Research notes for the master's thesis, prepared 10 Oct 2026 (updated with the business-case view).*

**Requirement:** the platform must **solve a business problem for a paying user**. It is not enough to show that
anomalies can be found and explained. Every dataset below is therefore judged first by *which costly decision the
explanation supports, and for whom*, and only then by size, openness and knowledge.

The technical goal is unchanged: open time-series data whose interesting moments (anomalies, hand-picked moments,
recurring patterns) can be **explained by open expert knowledge** such as reports, catalogues and textbooks. The solar
eclipse in sunlight data is the model case. Stock data are excluded.

> **Update (10 Oct 2026): space weather chosen for a decision check.** The sanity check against all planned features,
> the extended search for data sources and ground truth, and the business-case decision are in
> [`space_weather_decision/README.md`](space_weather_decision/README.md). The result is a **GO**:
> * **Fit:** the best of all candidates; 100 % of G3+ storms since 2010 can be linked to a catalogued cause.
> * **Business case for the thesis:** the problem is costly, affects many groups (GNSS/RTK users, satellite operators,
>   grids, aviation) and recurs about 7 times a year at G3+ level.
> * **Poland:** ASG-EUPOS has about 48 k accounts, and grid failures rise after storms.

---

## 1. The business problem the platform solves

**Problem.** Organisations that monitor time series (PV farms, grid and trading desks, insurers, GNSS-dependent
operations, cities) are not short of *alerts*. They are short of *explanations*. For every deviation an analyst must
answer one question: **"Is this a fault I must act on, or an external event I should note, claim or forecast around?"**
Answering it by hand is slow, and both kinds of mistake cost money:

| Mistake | Typical cost |
|---|---|
| Treating an external event as a fault | Unnecessary technician dispatch, alarm fatigue, wrong maintenance decisions |
| Treating a fault as an external event | Lost production, missed warranty or insurance claims, a growing fault |
| Not knowing the cause in time | Imbalance costs, missed curtailment compensation, slow claims handling, poor customer communication |

**What the platform delivers** (one workflow, reusable across domains):

```
detect deviation → retrieve the most similar past moments → match known events (catalogues) and expert texts
→ explanation with citations → impact in MWh / PLN / claims → recommended action
```

**How value is measured** (KPIs to use in the thesis):
* share of alerts explained automatically, and correctly (vs. a ground-truth event list)
* time-to-explanation per alert (minutes saved by analysts)
* false-dispatch rate, i.e. site visits avoided because the cause was external
* lost energy or loss value attributed by cause (MWh and PLN per cause)
* in insurance: claims triaged per day, and events detected before claims arrive

**Business-model hint for an SGH thesis:** sell it as B2B SaaS priced per monitored asset (per MW of PV, per gauge or
region, per fleet). Public data, as in this folder, is used to **build and prove** the product. In deployment the
customer's own data (inverter/SCADA, claims, telemetry) is added on top of the same knowledge layer.

---

## 2. Short answer: recommended business case and data

### Primary business case: explainable PV performance monitoring and lost-energy attribution in Poland
**Customer:** owners and O&M operators of PV farms, aggregators and balance-responsible parties (trading desks), DSOs.
**Question answered:** *Why did my PV output deviate from expectation in this 15-minute interval, and what should I do?*
Typical causes are a grid-operator curtailment, an eclipse, Saharan dust, snow or soiling, an inverter or grid fault,
or a forecast error.

Why the business case is strong now:
* Poland had **27.9 GW** of PV installed at the end of July 2026 (PSE data via Gramwzielone.pl).
* In **June 2026 PSE curtailed 246.9 GWh of PV output (14.2 % of potential PV production) on 26 days** through
  non-market redispatch (Forum Energii analysis, GLOBEnergia, 9 Jul 2026). Owners need to tell curtailment from
  their own faults, for reporting, compensation claims and O&M.
* Since **14 June 2024 Poland settles imbalances in 15-minute periods** (balancing-market reform), so unexplained
  forecast deviations translate directly into imbalance costs.
* External events move whole fleets at once. On 30 Mar 2024 Saharan dust cut PV in Baden-Württemberg to 1.6 GW
  against a 3.5 GW forecast (TransnetBW via Clean Energy Wire). The 12 Aug 2026 eclipse could remove up to 9.7 GW of
  European PV (ENTSO-E). The 2015 eclipse cut German PV by ~7 GW in one hour (sample 01).

The open data are enough to build and evaluate it. They are 15-min generation, load and PV at national level
(Energy-Charts, ENTSO-E, PSE: samples 01 and 03), weather and irradiance (IMGW, ERA5, ground stations), and an event
catalogue built from eclipses, PSE notices and market messages, holidays and storms. The knowledge comes from reports
by ENTSO-E, PSE and Forum Energii, IEA PVPS and the meteorological literature. This is the direct business version of
your eclipse example.

### Second case to show the method generalises (pick one)
* **Insurance and flood risk (Poland):** analog search ("this hydrograph looks like 1997/2010/2024") plus
  explanation from IMGW warnings, for early exposure estimates and claims triage. The September 2024 flood alone
  produced **over 131,000 insurance claims and PLN 2.13 bn of settled claims** (KNF report, as of 30 Jun 2025).
  Data: IMGW hydro and meteo (sample 09).
* **Space weather for GNSS/HF-dependent operations** (precision agriculture, surveying, drones, aviation, satellite
  operators): "is my RTK/GNSS problem caused by a geomagnetic storm, and how bad were similar storms?" Agricultural
  economists estimated **~$500 million** in losses to US farmers when GNSS-guided tractors could not operate during
  the May 2024 storm (UCAR/CPAESS). Data: GFZ/CelesTrak (sample 02), with Wikipedia page views as a demand signal
  (sample 06).

The other domains are useful for research but are weaker as a *business* case for a master's thesis (§3). The
benchmarks (NAB, UCR, TSB-UAD; folders 04 and 11) are only for reporting comparable detection metrics.

---

## 3. Business case per data domain

Strength = how convincing the business case is for a thesis prototype (paying customer, money at stake, explanation
changes a decision, data available to prove it).

| Domain (samples) | Business problem / decision | Who pays | What the platform adds | Evidence of value | Strength |
|---|---|---|---|---|---|
| **PV and grid, PL/EU** (01, 03) | Fault or external cause of a PV deviation; curtailment attribution; forecast correction | PV owners and O&M, aggregators and traders, DSOs | Cause per interval (curtailment, eclipse, dust, weather, fault) with sources; lost MWh by cause | 27.9 GW PV in PL; 14.2 % PV curtailed in Jun 2026; 15-min imbalance settlement | ★★★★★ |
| **Power-system incidents** (03) | Fast post-incident analysis ("what happened at 12:33?") | TSOs, large generators, regulators | Timeline, similar past incidents, report retrieval | Iberian blackout 28 Apr 2025, ENTSO-E 440-page final report | ★★★☆☆ (few customers) |
| **Hydrology and flood, PL** (09) | Early flood exposure; claims triage; detecting gauge failures | Insurers and reinsurers, municipalities, Wody Polskie, logistics | Analog hydrographs, explanation from IMGW warnings, data-gap alerts | 131k claims, PLN 2.13 bn settled after Sep 2024 | ★★★★☆ |
| **Space weather** (02, 06) | Is a GNSS/HF/satellite problem external, and how severe will it get? | Precision-ag and RTK providers, drone and survey firms, airlines, satellite operators, parametric insurers | Storm detection plus "most similar past storms" and their documented impacts | ~$500 M est. farm losses, May 2024 | ★★★★☆ |
| **Air quality, PL** (08) | Explain exceedances (fireworks, heating smog, transport, dust) for alerts and policy | Cities and voivodeships (B2G), building/HVAC operators, health apps | Cause attribution per episode, similar past episodes | Legal duty to inform the public; Kraków/Warsaw smog | ★★★☆☆ (mostly public sector) |
| **Demand and attention** (04, 06) | Why did demand spike or drop (holiday, weather, event)? | Retail, ride-hailing, media, ad planning | Calendar, weather and news grounding of demand anomalies | NYC taxi: holidays, the marathon and a blizzard explain all labelled anomalies | ★★★☆☆ (knowledge mostly news) |
| **IT/industrial monitoring** (04) | Root-cause analysis of alerts (AIOps, predictive maintenance) | IT operations, manufacturers | Similar past incidents + runbooks | Large market, but the knowledge (runbooks, logs) is private | ★★★☆☆ for a thesis |
| **ECG** (05) | Triage of Holter recordings | Cardiology clinics, Holter labs | Similar-beat retrieval + textbook explanation | Cardiologist time | ★★☆☆☆ (medical-device regulation) |

---

## 4. Feature: multi-timeframe similarity search and "what happened after"

Inspired by github.com/bitsofchris/time-series-AI, a "time-series RAG" prototype for stock charts (windows →
vectors → LanceDB → Streamlit). The platform adds what that repo only plans:
* the **same series at several timeframes**: 15 min → 1 h → 1 day → 1 week bars with [mean, min, max, last], the
  physical analogue of OHLC candles;
* search **across entities**: countries, gauges, stations;
* the **continuation of every analogue** ("what happened after"), as an analogue forecast;
* a **join to the event catalogue**, so each match is explained.

A working prototype is `scripts/multi_timeframe_search.py` (NumPy search, optional LanceDB as in the reference repo).
The full assessment is in **`multi_timeframe_similarity/README.md`**. Results on our data:
* **Floods:** the Kłodzko rise of 9–14 Sep 2024 finds the same flood at the other 5 gauges first (the wave
  travelling downstream). The spread of what happened after is the risk distribution an insurer needs.
* **Storms:** all 10 nearest analogues of the Gannon-storm onset (1957–2025) are Kp ≥ 7 storms. Their median next-24 h
  peak (Kp 7.3) underestimates the real Kp 9, so the knowledge layer must correct analogue forecasts for extreme
  events.
* **Demand:** 7 of 10 analogues of the NYC blizzard day fall on labelled anomalies or federal holidays. The March 2020
  lockdown in Zürich load data is most similar to Christmas and school-holiday periods, but unlike them it did not
  recover.
* **Solar:** the 2015 eclipse morning is most similar to ordinary cloudy mornings. Shape alone cannot identify the
  cause; the eclipse catalogue can. This is the core argument for knowledge grounding.

**Best data for this feature:**
* PV and load residuals from Energy-Charts / ENTSO-E / PSE (★★★★★) and IMGW hydrology (★★★★★)
* then IMGW meteorology, GIOŚ, ground irradiance, space weather, Wikipedia and NYC mobility (★★★★☆)

The catalogue has a new column, *Multi-timeframe similarity suitability*.

## 5. Selection criteria (business first)

| Criterion | Why it matters |
|---|---|
| **A paying user's decision depends on the explanation** | Without it the platform is a study, not a product (the requirement above) |
| Money or risk attached to the anomalies (MWh, PLN, claims, downtime) | Lets the thesis quantify value |
| Enough data (long, high-frequency, many series) | Similarity search needs many candidate windows; detectors need history |
| Many **dateable, documented** events | Ground truth the system must find *and explain* |
| Explanations in **open, citable** text or catalogues | They feed the knowledge layer (event catalogue + RAG) |
| Recurring shapes | "Find similar moments" is only meaningful if patterns repeat |
| Easy, stable access; Polish relevance | Feasible for a thesis; fits SGH and the Polish market |

The full catalogue (21 datasets) is in **`dataset_catalog.xlsx`**. The *Datasets* sheet now starts with *Business
problem*, *Who pays* and a *Business-case strength* score, which carries double weight in the ranking by default; you
can change the yellow weights. Other sheets: *Events (ground truth)*, *Knowledge sources* and *SGH library databases*.
A CSV copy is `dataset_catalog.csv`.

---

## 6. What is in this folder

Every sample is real data retrieved on 10 Oct 2026. Each folder has a `SOURCE.md` covering provenance, licence,
fields, the business use, the documented events and where their explanations live, plus a figure made by
`scripts/make_sample_plots.py`. Samples from official APIs were read in the browser on your computer and checked
byte-for-byte (SHA-256) against the source response.

| Folder | Data | Business question it demonstrates |
|---|---|---|
| `01_eclipse_solar` | German PV 19–21 Mar 2015; Zürich irradiance; DE/ES/PL PV 11–13 Aug 2026 | "Is this PV drop a fault?" It is not: an eclipse, ~7 GW in one hour inside ENTSO-E's forecast window. In 2026 Spain is hit at sunset while Poland is not (no false alarm should be raised) |
| `02_space_weather` | Daily Kp/Ap/sunspots/F10.7 1957–2025; Hp30 during the 2024 storm | "How bad can this storm get?" The 10 most similar historical storms are retrieved automatically, each with a documented history |
| `03_power_grid` | Spain during the 28 Apr 2025 blackout; PSE Poland demand/PV/wind | Incident timeline, and a **data-quality** anomaly (missing load, implausible solar values) that must not be mistaken for real behaviour |
| `04_nab_known_causes` | NAB NYC taxi + 3 IT/industrial failure series | Demand anomalies explained by holidays and weather. Matrix-profile discords: 5 of the top 6 fall in labelled windows (4 of 5 events; Thanksgiving missed). The 6th is 3–4 Jul (Independence Day), which NAB did not label but a holiday calendar explains |
| `05_ecg_mitbih` | MIT-BIH record 100 + annotations; TSB-UAD ECG | Expert labels plus textbook explanations; triage use case |
| `06_wikipedia_pageviews` | "Aurora" (en) / "Zorza polarna" (pl) page views 2024 | Public attention spikes on exactly the storm days in 02, a proxy for customer impact and support load |
| `07_atmosphere_pressure_wave` | 1-min pressure, Des Moines, 15–16 Jan 2022 | A sensor anomaly with a remote cause (Hunga Tonga eruption): "not a sensor fault" |
| `08_air_quality_pl` | PM2.5/PM10 Warsaw & Kraków around New Year 2025 | Two causes, two responses: a 1-h fireworks spike vs. a multi-hour heating smog |
| `09_hydrology_pl` | 6 IMGW gauges, hydrological year 2024 | The flood wave travels downstream (analog search, early warning for insurers). The daily mean hides the 798 cm peak. A gauge fails during the flood |
| `11_benchmarks_ucr_tsb` | UCR anomaly #135 | Standard benchmark for detector metrics |
| `13_long_energy_series` | Zürich electricity + weather 2015–2022 (15 min); Spain generation/load 2015–2018 (hourly) | Long history for analogue search: "when did demand or solar behave like this before, and what happened next?" |
| `multi_timeframe_similarity` | Results of the multi-timeframe search demos (figures, CSV, summary) | The research-workbench feature (§4) on real data |

Scripts:
* `scripts/make_sample_plots.py` rebuilds all figures and the two demos (`pip install pandas numpy matplotlib wfdb stumpy`).
* `scripts/multi_timeframe_search.py` runs the multi-timeframe similarity engine and its six demos (§4); LanceDB is optional.
* `scripts/fetch_official_data.py` downloads more data from Energy-Charts, GFZ, Wikimedia, IEM, GIOŚ, IMGW and PSE.
  The endpoints were checked on 10 Oct 2026, but the script has not yet been run against them, so start with a small request.

---

## 7. The knowledge layer

1. **Structured event catalogues** (dated, machine-readable) are the most reliable layer for business use, because
   every explanation is traceable. Examples:
   * eclipses: NASA eclipse catalogue
   * storms: NOAA/GFZ storm lists
   * grid: ENTSO-E incident reports; outage and unavailability messages with stated reasons (REMIT "UMMs", e.g. on the
     ENTSO-E Transparency Platform and PSE's UMM page); PSE "Komunikaty OSP" notices
   * curtailment: Forum Energii monthly analyses
   * holidays: `python-holidays`
   * floods: IMGW warnings and flood chronology
   * earthquakes and volcanoes: USGS / Smithsonian GVP
   * insurance: KNF catastrophe reports
2. **Unstructured expert text** (reports, textbooks, OA papers) is searched by retrieval (RAG) to write the
   explanation and to cover events that are in no catalogue.

Design points for the thesis:
* Recent work shows that "just add RAG" does not automatically improve detection: ATSADBench (2026) found RAG gave
  little gain. Use knowledge for **explanation, attribution and verification**, and evaluate it separately: "did the
  system name the right cause and cite the right source?"
* **Licences matter for a commercial product.** For a product (not only a thesis), prefer public-domain (NASA, NOAA,
  USGS), CC0 (Wikimedia page views) and CC BY (EEA, C3S, many OA papers). Some sources need care:
  * Non-commercial only: Energy-Charts data (non-commercial and journalistic use), LITFL and Stull (CC BY-NC-SA).
  * IMGW: free, but requires an exact attribution text, and some uses (e.g. agriculture support, water planning)
    need a paid contract under its regulations.
  * OpenStax *Astronomy 2e* forbids ingestion into generative-AI products without permission.
  * Full-text databases behind the SGH login are for reading, not bulk indexing.
  * For a commercial PV product, ENTSO-E or PSE data (or the customer's own data) are safer than Energy-Charts.
  * I am not a lawyer, so check each licence before any commercial use.
* **Data caveats are part of the value.** Aggregation hides peaks (Kłodzko), sensors fail during extreme events
  (Głuchołazy), and published series contain artefacts (Spanish solar during the blackout). Telling "the asset
  misbehaved" from "the data misbehaved" is itself a selling point.

---

## 8. How to prove the business value with public data (suggested thesis evaluation)

1. Build an **event table** for the primary case: eclipses, curtailment days, dust episodes, holidays, storms and grid
   incidents for 2024–2026. A seed list is in the *Events* sheet.
2. Run the detector on 15-min PV/load series (PSE, Energy-Charts, ENTSO-E) and let the platform explain each
   deviation.
3. Report the share of deviations explained correctly, time-to-explanation, false-dispatch reduction (simulated) and
   MWh/PLN attributed per cause. Prices come from PSE's RCE and imbalance reports.
4. Compare against a baseline with no knowledge layer (detector only), and against an LLM without retrieval.

---

## 9. How your SGH library list helps

Details are in the sheet *SGH library databases*. In short:
* **Free and directly useful:** DOAJ, Taylor & Francis OA Books, Otwórz Książkę, Biblioteka Nauki, BazTech,
  Bibliografia Geografii Polskiej, CEON/**RepOD** (Polish open research data), EU Bookshop (JRC PV and EEA reports),
  Eurostat, Portal GUS, HighWire, DART-Europe, and the Biuro Analiz Sejmowych / OSW / PISM analyses.
* **For the business part:** IEA Electricity Information, OECD iLibrary, Eurostat energy statistics (market sizing),
  EUR-Lex (balancing and network codes, REMIT), and Puls Biznesu / Presseurop (market and press context).
* **With login, for reading and citing:** ScienceDirect (*Solar Energy*, *Journal of Hydrology*, *Atmospheric
  Environment*, *Pattern Recognition*), Wiley (AGU *Space Weather*), Springer Link (Aggarwal *Outlier Analysis*),
  Oxford Academic, and Scopus / Web of Science for the systematic review.
* **Not useful here:** the finance, company and law databases (LSEG, Orbis, EMIS, CEIC, Passport, Ceduła GPW, Lex,
  Legalis, tax databases). Orbis or EMIS could help only to size the market of PV owners/O&M firms in Poland.

---

## 10. Methods and related work to read first

* Similarity search / matrix profile: Yeh et al. 2016; Law 2019 (*STUMPY*, JOSS); Mueen's MASS; Rakthanmanon et al.
  2012 (UCR Suite). Tutorials: https://stumpy.readthedocs.io
* Evaluation and benchmark critique: Wu & Keogh 2021 (arXiv:2009.13807); Paparrizos et al. 2022 (TSB-UAD);
  Lavin & Ahmad 2015 (NAB).
* Time series + text / LLMs: Time-MMD (arXiv:2406.08627); Context is Key (arXiv:2410.18959); MTBench
  (arXiv:2503.16858); AXIS (arXiv:2509.24378); ATSADBench (arXiv:2601.12448).
* Background: Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (free online, otexts.com/fpp3).

---

## 11. Open questions

1. Is the **PV/energy** business case acceptable as the primary one, or does your supervisor prefer another sector
   (insurance/flood, GNSS/space weather, public sector air quality)?
2. Polish or English for the thesis and the platform?
3. Will explanations be generated by an LLM with retrieval? If so, the next step is a licence-clean corpus and the
   event catalogue for the chosen case.
4. Real-time monitoring (APIs, alerts) or historical analysis and backtesting only?

---

## Sources
* PV in Poland 27.9 GW (PSE data, end Jul 2026): https://www.gramwzielone.pl/?p=20377240
* PV curtailment June 2026 (Forum Energii via GLOBEnergia): https://globenergia.pl/rekordowy-czerwiec-fotowoltaika-byla-ograniczana-przez-ponad-jedna-trzecia-miesiaca/
* Polish balancing-market reform, 15-min settlement from 14 Jun 2024 (Clyde & Co): https://www.clydeco.com/en/insights/2024/03/balancing-market-reform-electricity
* Saharan dust and PV, 30 Mar 2024 (Clean Energy Wire): https://www.cleanenergywire.org/news/saharan-dust-cuts-solar-power-output-germany
* KNF catastrophe losses 2024 / flood claims (XPRIMM): https://www.xprimm.com/POLAND-Catastrophic-losses-in-2024-cost-the-insurance-sector-three-times-more-than-a-year-before-articol-24-23790.htm
* GNSS disruption and farm losses, May 2024 storm (UCAR CPAESS): https://cpaess.ucar.edu/news/nasa-jack-eddy-fellow-quantifies-gps-disruption-2024-solar-storm
* ENTSO-E, *Solar Eclipse Impact Analysis* (2015): https://eepublicdownloads.entsoe.eu/clean-documents/Publications/SOC/150219_Solar_Eclipse_Impact_Analysis_Final.pdf
* ENTSO-E press release on the 12 Aug 2026 eclipse: https://www.entsoe.eu/news/2026/08/07/transmission-system-operators-prepare-for-solar-eclipse-to-ensure-secure-system-operation/
* EclipseWise city tables for 20 Mar 2015: https://business.eclipsewise.com/oh/oh-tables/ec2015-Tab02a.pdf
* Solar eclipse of 12 Aug 2026 (Wikipedia): https://en.wikipedia.org/wiki/Solar_eclipse_of_August_12,_2026
* ENTSO-E Iberian blackout portal: https://www.entsoe.eu/publications/blackout/9-may-2025-iberian-blackout/ and the final report summary: https://www.pv-magazine.com/2026/03/23/entso-e-report-finds-systemic-failures-behind-2025-iberian-blackout/
* NOAA SWPC, G5 conditions observed (10 May 2024): https://www.spaceweather.gov/news/g5-conditions-observed
* GFZ Kp index (CC BY 4.0): https://kp.gfz.de/
* Rzeczpospolita, Kłodzko 798 cm and damaged sensor (16 Sep 2024): https://www.rp.pl/kleski-zywiolowe/art41133291-powodz-w-polsce-nysa-w-klodzku-miala-prawie-8-metrow-czujnik-sie-zepsul
* IMGW public data and terms: https://danepubliczne.imgw.pl/
* GIOŚ API notice: https://www.gov.pl/web/gios/korzystasz-z-danych-gios-o-jakosci-powietrza-za-posrednictwem-uslug-api-sprawdz-wazne-zmiany
* MIT-BIH Arrhythmia Database: https://physionet.org/content/mitdb/1.0.0/
* NAB: https://github.com/numenta/NAB ; Wu & Keogh: https://arxiv.org/abs/2009.13807
* Time-MMD: https://arxiv.org/abs/2406.08627 ; Context is Key: https://arxiv.org/abs/2410.18959 ; AXIS: https://arxiv.org/abs/2509.24378 ; ATSADBench: https://arxiv.org/abs/2601.12448
* Reference repository for the similarity feature: https://github.com/bitsofchris/time-series-AI (MIT licence)
* Energy-Charts terms: https://energy-charts.info/llms.txt ; OpenStax licence and AI clause: https://openstax.org/books/astronomy-2e/pages/preface ; LITFL licence: https://litfl.com/ecg-library/
