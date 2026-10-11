# 06 – Wikipedia page views (attention time series)

**Business use:** attention data as a proxy for customer impact. For example, support-ticket or website-traffic spikes during a storm, or for media and e-commerce explaining traffic anomalies with news. It also shows cross-domain grounding: the platform can explain one company's anomaly with a physical event observed elsewhere.

## File
`wikipedia_pageviews_aurora_2024-04_to_11.csv` gives daily views by human users of en:"Aurora" and pl:"Zorza polarna",
1 Apr – 30 Nov 2024.
Retrieved 2026-10-10 from the Wikimedia REST API:
`https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/user/{article}/daily/{start}/{end}`
(data available from 1 Jul 2015; Wikimedia analytics data are released under CC0).

## What it shows
| Peak | Views | Explanation |
|---|---|---|
| 11 May 2024 | 341,117 (en), 20,795 (pl) | Auroras visible across Europe and the US during the G5 "Gannon" storm (see sample 02, Ap = 271) |
| 11 Oct 2024 | 122,024 (en) | Severe (G4) storm of 10–11 Oct 2024 (daily Ap 97 and 116) |
| 12–13 Aug 2024 | ~7,700 (en), ~2,700 (pl) | Geomagnetic storm of 12 Aug 2024 (Ap ≈ 127) |

`plot_aurora_pageviews_vs_ap.png` puts the two series side by side, for **cross-domain grounding**. A spike in
human attention is explained by a physical time series, and both are explained by NOAA/GFZ storm reports.

## Why it is useful
* Every article is its own knowledge base. The revision history, the "In the news" archive and the *Portal:Current
  events* daily pages give dated text describing what happened. That is ideal for a retrieval-augmented explainer.
* It provides millions of series (one per article and language), daily since 2015 or hourly from dumps.
* It is not financial data, and it is fully open.
