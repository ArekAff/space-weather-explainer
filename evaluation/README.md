# evaluation/: what the system is scored against

The evaluation events and their answer key. Nothing here is input for the platform except three columns of the
event table (`id`, `t0_utc`, `stacja`); everything else is used only by evaluation code.

## event_set/

| File | What it is |
|---|---|
| `zestaw_zdarzen_zasady.md` | Start here (PL): how the 158 events were chosen, DEV/TEST split, answer key, t0 |
| `data_dictionary.md` | What every column of the table means and which columns the system may see |
| `zestaw_zdarzen_ewaluacja.csv` | The event table (v3: 158 events, 96 DEV / 62 TEST). The file code reads |
| `zestaw_zdarzen_ewaluacja.xlsx` | The same table formatted for reading, with a sources sheet |
| `zestaw_zdarzen_build.py` | Builds the CSV from the catalogues in `dataset_research/space_weather_decision` |
| `zestaw_zdarzen_xlsx.py` | Turns the CSV into the XLSX (needs `openpyxl`) |
| `rtgms_alarmy_2026_surowe.txt` | rtgms.pl alarms for WIKO and BRWO as Arek copied them by hand (Polish time) |
| `rtgms_parse.py` | Turns the raw alarm text into the CSV below |
| `rtgms_alarmy_2026.csv` | 78 alarm windows with UTC times; input of the build |
| `donki_flr_mx_2026-05_2026-10.csv` | DONKI M/X flares, to check an alarm against solar radio bursts; input of the build |
| `donki_uzupelnienie_2026-10.json` | DONKI entries of 9–11 Oct 2026 missing from the 10 Oct catalogues; input of the build |

## Rebuild the event set

From `code/` (so the project's Python environment is used):

```
uv run python ../evaluation/event_set/zestaw_zdarzen_build.py ../dataset_research/space_weather_decision ../evaluation/event_set
uv run --with openpyxl python ../evaluation/event_set/zestaw_zdarzen_xlsx.py ../evaluation/event_set/zestaw_zdarzen_ewaluacja.csv ../evaluation/event_set/zestaw_zdarzen_ewaluacja.xlsx
uv run python ../evaluation/event_set/rtgms_parse.py ../evaluation/event_set/rtgms_alarmy_2026_surowe.txt ../evaluation/event_set/rtgms_alarmy_2026.csv
```

The build keeps existing event IDs when the output file already exists, so always point it at the current CSV.
It also reads `data/normalized/gfz_kp` (found two folders above `event_set/`) and the input files next to it.

## Where the rest of the answer key is

- Catalogues downloaded on 2026-10-10 (Richardson–Cane, SSC, NOAA proton events, DONKI):
  `dataset_research/space_weather_decision/data/`, provenance in `MANIFEST_D1.md` and `MANIFEST_D2.md`.
- Answer-key datasets fetched by the ingestion code will go to `data/answer_key/` (not built yet).
