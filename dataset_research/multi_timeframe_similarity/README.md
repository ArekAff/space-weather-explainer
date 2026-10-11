# Feature: multi-timeframe similarity search and "what happened after"

*Assessment prepared 10 Oct 2026. Reference: https://github.com/bitsofchris/time-series-AI (MIT licence, last commit
26 Mar 2025).*

## 1. What the reference repository does

`time-series-rag/` is a prototype called "Time Series RAG for Trading":

| Step | Implementation in the repo |
|---|---|
| Data | Stock OHLCV from yfinance per **symbol** and **timeframe** (1d, 1h), stored in TimescaleDB (`raw_price_data`, `normalized_price_data`) |
| Windows | Sliding windows of 20 bars, stride 10, with 4 features per bar (open, high, low, close) |
| Normalisation | z-score or min-max computed **over all windows of a symbol together** (not per window) |
| "Embedding" | The normalised window flattened to an 80-number vector (no learned model) |
| Vector store | LanceDB table with `symbol, timeframe, window_start, window_end, vector, metadata` |
| Search | Nearest neighbours (L2) to the most recent window of a symbol; optionally exclude the same symbol |
| UI | Streamlit pages "Find similar windows" and "Similar to recent", with Plotly charts |
| Roadmap only (not built) | Timeframe-agnostic matching, statistics of **what happened after** a pattern, backtesting, learned embeddings |

The "RAG" in its name means retrieval of similar windows. There is no text knowledge and no generation step.

## 2. What we take, and what we change for the platform

| Topic | Reference repo | Our platform |
|---|---|---|
| Entities | stock symbol | country × production type, river gauge, weather/air station, sensor, Wikipedia article … |
| Bars | OHLC candles | **[mean, min, max, last]** per bar: the physical analogue of OHLC, computed from the finer data |
| Timeframes | stored separately per fetch | the **same series** re-sampled to several bar sizes (e.g. 15 min → 1 h → 1 day → 1 week); with TimescaleDB *continuous aggregates* this is automatic |
| Normalisation | global per symbol, which in effect is a *level* search | two modes. **shape** (z-score inside each window) is scale-free and makes cross-timeframe and cross-entity matching meaningful. **level** keeps magnitude (storm strength). Plus an **amplitude filter** so a 3-cm wiggle cannot match a 3-m flood rise |
| Trivial matches | only the exact query window is excluded | overlapping windows of the same entity are excluded, plus non-maximum suppression (one hit per region) |
| After the match | not implemented | **"what happened after"**: the next H bars of every analogue, expressed relative to its window, plus summary statistics (an analogue forecast) |
| Seasonality | not needed for prices | essential. Search on **residuals** (actual ÷ clear-sky or forecast, anomaly vs. climatology), otherwise the hits are just "sunny days" or "Mondays" |
| Explanation | none | every hit carries (entity, timeframe, start, end), which is joined to the event catalogue and expert texts → cited explanation |
| Evaluation | visual | retrieval precision against event lists (below) |

The prototype is in `scripts/multi_timeframe_search.py`. Its `MultiTimeframeIndex` builds windows at several
timeframes, searches with NumPy, and can store the same vectors in **LanceDB** (`to_lancedb()`), the vector DB of
the reference repo; this was tested. Run `python scripts/multi_timeframe_search.py` to reproduce every result and
figure in this folder.

## 3. Results on our data (all reproducible)

| Demo | Data / index | Query ("something identified") | Result | Lesson |
|---|---|---|---|---|
| Storm analogues (`space_weather_analogues.*`) | Kp 3-h 1957–2025; 132,043 windows over 3 h / 1 D / 3 D bars | 48 h up to 21:00 UT on 10 May 2024 (Gannon storm already at Kp 8+) | **10 of 10** analogues are storms with Kp ≥ 7 (1961, 1963, 1989, 1976 …). The analogues' median peak in the next 24 h is **Kp 7.3**; the real storm reached **Kp 9** | Analogues give a *distribution* of outcomes, but an extreme event is underestimated. The knowledge layer (CME reports, NOAA alerts) must correct it |
| Same shape at other scales (`space_weather_cross_timeframe.*`) | same, shape mode, 1 D / 3 D bars | same | Matches are moderately active multi-week periods | Storms are a short-time-scale phenomenon, so cross-timeframe matching adds little here |
| Demand anomaly (`nyc_taxi_blizzard_matches.*`) | NYC taxi 30-min; 3,836 windows over 30 min / 2 h bars | blizzard day 26–27 Jan 2015 | **7 of 10** hits fall on NAB anomaly windows or US federal holidays (Christmas Eve, MLK Day, Thanksgiving eve, Labor Day, 4 July, New Year, 26 Dec). The other 3 are holiday-season weekends | Disruptions look like holidays, so calendar knowledge is needed to tell "blizzard" from "holiday" |
| Flood analogues (`hydro_flood_analogues.*`) | 6 IMGW gauges, daily; amplitude-aware shape | Kłodzko 9–14 Sep 2024 (start of the rise) | Top 5 = **the same flood at the other gauges** (Głuchołazy, Nysa, Racibórz, Brzeg Dolny, Opole: the wave travelling downstream), then the Dec 2023 high water | Cross-entity search works. "What happened after" spans from a small peak to +20 window-SDs, which is the risk distribution an insurer wants. Without the amplitude filter a 3-cm bump at Opole ranked #2 |
| Lockdown analogues (`load_lockdown_analogues.*`) | Zürich business electricity 2015–2022; 14,338 windows over 1 h / 1 D / 7 D bars | 28 days around the 16 Mar 2020 lockdown | Top hits = **Christmas/New Year periods** and **February school-holiday weeks** | Lockdown looked like a holiday period. But all analogues recovered while the lockdown persisted, so outcome statistics must be checked against knowledge (news, regulations) |
| Eclipse morning (`pv_eclipse_day_matches.*`) | Zürich irradiance ÷ clear-sky proxy, hourly 2015–2022 | 20 Mar 2015 07–14 UTC | Hits are ordinary mornings with clouds or fog (2018-06-14, 2020-05-16, 2015-03-17 …) | **Shape alone cannot tell an eclipse from a cloud.** The eclipse catalogue (knowledge) is what identifies it. This is the core argument for the knowledge-grounded platform |
| Multi-scale ECG (`ecg_*_scale_matches.*`) | MIT-BIH record 100; 0.7-s "beat" bars and 6.4-s "rhythm" bars | first atrial premature ('A') beat | Precision@5 = **0.2 at beat scale** (random 0.006), **0.4 at rhythm scale** (random 0.058); precision@20 = 0.05 / 0.10 | The larger timeframe helps (premature timing is a rhythm feature), but generic windows are weak. ECG needs beat-aligned windows and RR-interval features |

## 4. Which datasets suit this feature

Criteria: a base resolution fine enough for ≥ 3 meaningful timeframes; long history (many windows); many entities to
search across; events to evaluate retrieval; a "what happened after" question with business value.

| Dataset | Base resolution / history | Natural timeframes (bars) | Entities to search across | "What happened after" (business question) | Pre-processing | Suitability |
|---|---|---|---|---|---|---|
| **Energy-Charts / ENTSO-E PV & load** | 15 min since 2015 (~385k points per series) | 15 min · 1 h · 1 D · 1 W | ~40 countries × production types; ENTSO-E also per generating unit | After a deviation starts, how long does it last and how many MWh are lost? (re-hedge, dispatch decision) | residual vs. forecast / clear-sky; calendar | ★★★★★ |
| **PSE (Poland)** | 15 min; API from 14 Jun 2024, older reports as CSV | 15 min · 1 h · 1 D | system demand, PV, wind, generation groups | Curtailment onset → expected duration and lost energy | as above | ★★★★☆ (shorter API history) |
| **IMGW hydrology** | daily since 1951, ~900 gauges (10-min only for current data) | 1 D · 3 D · 1 W (+10 min if collected going forward) | ~900 gauges, upstream → downstream | After a rise: expected peak and timing downstream (insurer exposure, municipal warning) | amplitude-aware shape | ★★★★★ (demo confirms) |
| **IMGW meteorology / ERA5** | hourly since 1951 (IMGW), hourly since 1940 (ERA5) | 1 h · 1 D · 1 W | stations / grid points | Persistence of a heat wave or cold spell (load, PV, health) | anomaly vs. climatology | ★★★★☆ |
| **GIOŚ air quality** | hourly, ~2000 →, hundreds of sensors | 1 h · 1 D · 1 W | sensors / cities | Will this smog episode last 3 more days? (alerts) | anomaly vs. seasonal profile | ★★★★☆ |
| **Ground irradiance (BSRN 1-min, DWD 10-min)** | 1–10 min, decades | 1 min · 15 min · 1 h · 1 D | stations | Short-term PV ramps; dust/fog episode duration | ÷ clear-sky (pvlib) | ★★★★☆ (demo: needs knowledge to separate causes) |
| **Space weather (GFZ Kp/Hp30, OMNI 1-min)** | 30 min–3 h since 1932; OMNI 1 min | 1 min · 30 min · 3 h · 1 D · 27 D (solar rotation) | indices, solar-wind parameters | Storm onset → peak Kp and duration (analogue forecasting for GNSS users) | level mode | ★★★★☆ (within-timeframe strong; cross-timeframe weak) |
| **Wikipedia page views** | daily since Jul 2015 (hourly in dumps) | 1 h · 1 D · 1 W | millions of articles × languages | Attention decay after a spike (media, support load) | log, shape | ★★★★☆ |
| **NYC taxi / mobility** | 30 min (NAB); raw trips by zone | 30 min · 2 h · 1 D | taxi zones (raw TLC) | Recovery after a disruption | weekly profile | ★★★★☆ (demo confirms) |
| **Seismic waveforms** | 20–100 Hz continuous | seconds → minutes → hours | thousands of stations | Aftershock activity | band-pass | ★★★★☆ technically, weak business case |
| **Kepler/TESS light curves** | 2–30 min | minutes → days | ~200k stars | Repeating transits | detrend | ★★★★☆ technically, no business case |
| **MIT-BIH / PTB-XL ECG** | 360–500 Hz | beat · rhythm · trend | 48 records / 21.8k ECGs | Does ectopy turn into runs? | beat alignment, RR features | ★★★☆☆ (demo: generic windows weak) |
| **NAB / UCR / TSB-UAD** | various, single series | 2 | few | — | — | ★★★☆☆ (tests only) |

**Recommendation:** implement the feature on the primary business case (PV and load residuals from
Energy-Charts / ENTSO-E / PSE: 15 min → 1 h → 1 day → 1 week, entities = countries/production types, later the
customer's PV parks). Use **IMGW hydrology** as the second showcase, because cross-gauge analogues demonstrate the
idea best. Keep **Kp** as a clean, label-rich test bed.

## 5. How the feature fits the platform ("research workbench")

1. A user (or a detector) **marks a moment**: an anomaly, or any hand-picked window.
2. The platform searches it **at several timeframes** (the same series at coarser and finer bars) and **across
   entities** (other countries, gauges, stations).
3. For each analogue it shows **what happened after** (fan chart of continuations, distribution of peak and duration).
4. Each analogue is **joined to the event catalogue and expert texts**, so the user sees *why* it happened then (eclipse,
   curtailment, holiday, CME, flood warning) with citations.
5. The user can **confirm or relabel** a match, which grows the labelled event catalogue for evaluation and later
   training.

Suggested stack (same as the reference repo, so it is easy to cite and reuse): TimescaleDB (raw data plus continuous
aggregates for the timeframes) → window builder → LanceDB (vectors + metadata filters) → Streamlit/Plotly UI. Add an
event-catalogue table and a document index (RAG) for the explanations. Learned embeddings (e.g. TS2Vec, or time-series
foundation models such as MOMENT or Chronos) are a later upgrade to the flattened-window vectors used here.

Files in this folder: `*.png` (query, top analogues, continuation in orange), `*.csv` (hits with distances, labels,
outcomes) and `demo_summary.json` (numbers quoted above).
