# docs/: rules for agents

- Treat the copied documents (`email_promotor/`, `zrodla_danych/`, `metodologia/`, `rag/`, `obszar_biznesowy/`) as
  dated snapshots. Do not rewrite them. When something in them turns out wrong or changes, add an entry to
  `decisions.md` that names the file and the superseded statement.
- `decisions.md` and `open_questions.md` are the living files. Append to them and keep entries short and dated.
  Only Arek makes decisions; an agent may record a decision Arek stated, quoting him, or propose one in
  `open_questions.md`.
- `data_gathering_plan.md` is living too: when a fetcher works, update that source's entry (endpoint tested, cadence,
  row count, quirks).
- Thesis-facing text (anything Arek may paste into the thesis or an e-mail to the advisor) is written in Polish.
  Everything aimed at agents is in English.
- New documents: put them in the matching subfolder, add a row to the table in `README.md`, and keep file names in
  lower_snake_case.
