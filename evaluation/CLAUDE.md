# evaluation/: rules for agents

Human overview and commands: `README.md` here. Rules of the set (PL): `event_set/zestaw_zdarzen_zasady.md`.

- **Answer key.** From `event_set/zestaw_zdarzen_ewaluacja.csv` only `id`, `t0_utc` and `stacja` may reach the
  system; `zbior` and `okres_korpusu` only select and group runs. Every other column and every other file in this
  folder is for evaluation code only (root `CLAUDE.md`, invariant 1). Never copy these files into `data/normalized/`
  or `data/corpus/`, and never put them in prompts or retrieval indexes.
- `event_set/data_dictionary.md` describes every column. The column list in `zestaw_zdarzen_xlsx.py` (`COLS`) is its
  source: when a column is added or its meaning changes, update `COLS` first, then the dictionary.
- **Do not change the event set without Arek's explicit OK**: not the CSV, not the rules, not the sampling seed
  (2026), not the DEV/TEST rule. A change gets a dated entry in `docs/decisions.md` and new counts in the root
  `CLAUDE.md` (invariant 5) and `code/platform/CLAUDE.md`.
- **IDs are stable.** Always run the build with the current CSV as output so IDs are kept; IDs of removed events
  (J121, J126, J128) are never reused. Never edit the CSV by hand: change the inputs or the script and rebuild.
- **Check a rebuild.** Build into a copy first and diff against the current CSV (ignore CRLF/LF). On 2026-11-14 the
  build reproduced the CSV exactly.
- **Keep the folder depth.** `zestaw_zdarzen_build.py` finds its inputs next to itself and `data/normalized/gfz_kp`
  two levels up. If the folder moves, pass the gfz_kp folder as the fourth argument or fix `GFZ_KP` in the script.
- `rtgms_alarmy_2026_surowe.txt` is Arek's manual reading: do not edit it. Arek appends new alarms, then
  `rtgms_parse.py` rebuilds the CSV.
- The scripts here are small one-off builders that live next to their data. Application code (collectors, the
  platform, evaluation) belongs in `code/`.
- The XLSX is generated from the CSV; regenerate it after every rebuild (`openpyxl` is not a project dependency:
  use `uv run --with openpyxl`).
- Text and column names in this folder are Polish (thesis-facing). Keep file names unchanged: the rules document,
  the XLSX sources sheet and `docs/decisions.md` refer to them.
