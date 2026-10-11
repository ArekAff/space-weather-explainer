# 11 – Anomaly-detection benchmarks for evaluation

**Business use:** none directly. These benchmarks prove the detection component is competitive, which a buyer may ask for.

## Files
| File | What |
|---|---|
| `135_UCR_Anomaly_InternalBleeding16_TRAIN.csv / _TEST.csv` | Series #135 of the UCR Time Series Anomaly Archive (KDD Cup 2021). Arterial blood pressure in an animal internal-bleeding experiment. Exactly one anomaly in the test part, at indices 4187–4198 (`is_anomaly` = 1). |
| `plot_ucr_135.png` | Figure |

Source: copied from the `aeon` toolkit (`aeon/datasets/data/KDD-TSAD_135`, BSD-3 code licence). The full archive
(250 series, one anomaly each, many with a short provenance note) is distributed by E. Keogh's group (UCR).
Cite Wu & Keogh, *IEEE TKDE* 2021 / arXiv:2009.13807.
The ECG series from **TSB-UAD** is in folder 05.

## Role in the thesis
These are *not* the main knowledge-grounded data (most series have no external text). They are the standard way to:
* check that the detection or similarity component is competitive (UCR archive, TSB-UAD, NAB);
* report metrics comparable with the literature (VUS-PR, range-F1, UCR "one-anomaly" accuracy).

Larger collections: TSB-UAD (public part: ~1,980 real series from 18 datasets), TimeEval (HPI Potsdam), the UCR Time Series Classification Archive
(128 datasets; for similarity search and motif evaluation), and the Monash forecasting archive.
