# 04 – Numenta Anomaly Benchmark, "realKnownCause" subset

**Business use:** demand planning and operations (ride-hailing, retail, transport). The question is whether a demand drop or spike is explained by a holiday, weather or a public event, or is a real problem. The failure series represent IT/industrial monitoring, where the platform would match alerts against past incidents and runbooks.

## Files
| File | What |
|---|---|
| `nyc_taxi.csv` | NYC taxi passengers per 30 min, 1 Jul 2014 – 31 Jan 2015 (10,320 points) |
| `machine_temperature_system_failure.csv` | Temperature of an industrial machine component (5 min); planned shutdown, then a failure precursor, then catastrophic failure |
| `ambient_temperature_system_failure.csv` | Office ambient temperature (hourly), with system failures |
| `ec2_request_latency_system_failure.csv` | AWS server metric that ends with a documented AWS API failure |
| `nab_anomaly_windows_realKnownCause.json` | Official NAB anomaly windows for these files |
| `NAB_LICENSE_AGPL-3.0.txt` | Licence of the NAB repository |
| `matrix_profile_top_discords.csv` | Output of the unsupervised discord demo (below) |
| `plot_nyc_taxi.png` | Figure |

Source: https://github.com/numenta/NAB (`data/realKnownCause`, `labels/combined_windows.json`). The raw taxi trips come
from the NYC Taxi & Limousine Commission open data. Citation: Lavin & Ahmad (2015), *Evaluating Real-time Anomaly
Detection Algorithms – the Numenta Anomaly Benchmark*, arXiv:1510.03336.

## The five NYC taxi anomalies and their explanations
| NAB window | Cause (NAB README) | Date / open knowledge |
|---|---|---|
| 30 Oct – 3 Nov 2014 | NYC Marathon | 2 Nov 2014 (Wikipedia "2014 New York City Marathon") |
| 25 – 29 Nov 2014 | Thanksgiving | 27 Nov 2014 |
| 23 – 27 Dec 2014 | Christmas | 25 Dec 2014 |
| 29 Dec 2014 – 3 Jan 2015 | New Year | 1 Jan 2015 |
| 24 – 29 Jan 2015 | Snow storm | January 2015 North American blizzard ("Juno"); NYC travel ban 26–27 Jan |

## Proof-of-concept: matrix-profile discords (no labels used)
A one-day window (m = 48) gives these top discords: 27 Jan 2015 (blizzard), 2 Nov 2014 (marathon), 25 Jan 2015
(blizzard onset), 31 Dec 2014 (New Year), **3 Jul 2014** and 24 Dec 2014 (Christmas).
Five of the six fall inside labelled windows, covering 4 of the 5 events (Thanksgiving is not among the top 6). The
sixth, the day window from 3 Jul 07:00 into **Independence Day**, is *not* labelled in NAB but is obviously
explainable by a holiday calendar. This shows why knowledge grounding adds value on top of benchmark
labels.

Caveat for the thesis: Wu & Keogh (2021) criticise NAB and other benchmarks (trivial anomalies, mislabelling,
run-to-failure bias). Cite and discuss it: *Current Time Series Anomaly Detection Benchmarks are Flawed and are
Creating the Illusion of Progress*, arXiv:2009.13807.
