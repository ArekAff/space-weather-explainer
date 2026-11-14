# docs/: rules for agents

- Treat the copied documents (`zrodla_danych/`, `metodologia/`, `rag/`, `obszar_biznesowy/`) as dated snapshots. Do
  not rewrite them, not even to fix a path that moved. When something in them turns out wrong or changes, add an
  entry to `decisions.md` that names the file and the superseded statement.
- `decisions.md` and `open_questions.md` are the living files. Append to them and keep entries short and dated.
  Only Arek makes decisions; an agent may record a decision Arek stated, quoting him, or propose one in
  `open_questions.md`. Do not edit old entries; paths in entries before 2026-11-14 follow the mapping in the
  2026-11-14 entry.
- `data_gathering_plan.md` is living too: when a fetcher works, update that source's entry (endpoint tested, cadence,
  row count, quirks).
- This folder holds text about the project only. Data and scripts for the event set go to `evaluation/`, thesis
  text to `thesis/`, anything sent to or received from the advisor to `knowledge/advisor/`, articles to `knowledge/sources/`, findings
  to `knowledge/findings/`, code to `code/`.
- `docs/` is pushed to the public GitHub repo. Do not copy thesis text, the table of contents or advisor e-mails
  into it; refer to the private file by path (`thesis/...`, `knowledge/advisor/...`).
- Thesis-facing text (anything Arek may paste into the thesis or an e-mail to the advisor) is written in Polish.
  Everything aimed at agents is in English.
- New documents: put them in the matching subfolder, add a row to the table in `README.md`, and keep file names in
  lower_snake_case.
