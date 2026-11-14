# knowledge/: what the thesis rests on

The material the project learns from, kept in one place so that nothing gets lost between sessions.

| Folder | What goes in | In git? |
|---|---|---|
| `advisor/` | Everything exchanged with the advisor: e-mail threads (PDF), e-mails to the advisor, the presentation | No (private); only its `README.md` and `CLAUDE.md` |
| `sources/` | PDF exports of articles, reports and other sources to read and cite, plus `sources_index.md`, the list of them | Only `sources_index.md` and `README.md`; the files stay on the laptop and in OneDrive (publishers' copyright, public repo) |
| `findings/` | What agents and Arek found out while working: one dated note per finding, listed in `findings/README.md` | Yes |

How this differs from `docs/`: `docs/` holds what the project decided and designed (decision log, open questions,
plans). `knowledge/` holds the inputs to those decisions: what the advisor said, what the literature says, what was
found by checking. A finding that leads to a decision is recorded here first, then the decision goes to
`docs/decisions.md` with a link back.

## Adding something

- **An e-mail from the advisor:** save the PDF export as `advisor/email_threads/<YYYY-MM-DD>.pdf`.
- **An article:** save the PDF as `sources/<year>_<first_author>_<short_title>.pdf` and add one row to
  `sources/sources_index.md`.
- **A finding:** new file `findings/<YYYY-MM-DD>_<topic>.md` from the template in `findings/README.md`, plus one row
  in the index there.
