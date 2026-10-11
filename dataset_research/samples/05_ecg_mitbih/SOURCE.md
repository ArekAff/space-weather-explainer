# 05 – ECG with cardiologist annotations (MIT-BIH Arrhythmia Database)

**Business use:** triage support for Holter/ECG review (cardiology clinics, Holter labs). Similar-beat retrieval plus textbook explanations could cut review time. Note that a real product is a medical device under EU MDR, so this domain is best kept as a research example in a business-focused thesis.

## Files
| File | What |
|---|---|
| `mitdb_record_100/100.dat, 100.hea, 100.atr` | Full record 100 in WFDB format: 30 min, 2 leads (MLII, V5), 360 Hz, with reference beat annotations |
| `mitdb_100_annotations.csv` | All 2,274 annotations as a table (sample, time_s, symbol). Counts: 2,239 N (normal), 33 A (atrial premature), 1 V (premature ventricular), 1 rhythm marker |
| `mitdb_100_first5min_mV.csv` | First 5 minutes of the signal in mV, easy to open without the `wfdb` library |
| `MBA_ECG805_data.out` | ECG series from the TSB-UAD benchmark (value, label). 20,200 of 230,400 points are labelled anomalous. TSB-UAD documents that the ECG anomalies are premature ventricular contractions. |
| `plot_ecg_record100.png` | Figure |

Sources
* Record 100 is mirrored in the `wfdb-python` repository (`sample-data/`). The original is PhysioNet
  https://physionet.org/content/mitdb/1.0.0/ (48 records, 360 Hz, ~110,000 beat labels, each record annotated
  independently by two or more cardiologists; **Open Data Commons Attribution 1.0**). Cite Moody & Mark (2001),
  *IEEE Eng. Med. Biol.* 20(3):45–50, and Goldberger et al. (2000) PhysioNet.
* TSB-UAD: https://github.com/TheDatumOrg/TSB-UAD (Apache-2.0), Paparrizos et al., PVLDB 2022.

## Why it fits the project
* Labels are *expert* (cardiologist) judgements, and each label maps to textbook knowledge. An 'A' beat comes early,
  with an abnormal or hidden P wave and a narrow QRS. A 'V' beat is wide and bizarre, has no preceding P wave and is
  followed by a compensatory pause.
* The data have a strong periodic structure, so they suit similarity search: "find beats that look like this one"
  is a classic matrix-profile and DTW use case.
* Open explanation sources: LITFL ECG Library (CC BY-NC-SA 4.0), ECGpedia, the PhysioNet database directory
  (it describes the rhythm of each record), and the AHA/ESC guidelines (free to read).

## More data on PhysioNet (all open)
MIT-BIH Supraventricular Arrhythmia DB, Long-Term AF DB, PTB-XL (~21,800 12-lead ECGs with diagnostic statements:
text plus signal pairs), INCART, sleep-apnea databases.
