# thesis/: rules for agents

- **Private.** The GitHub repo is public and the thesis must not be (Arek, 2026-11-14). The contents are
  git-ignored (`/thesis/*` in `.gitignore`; only `README.md` and `CLAUDE.md` are tracked). Never force-add them,
  and do not copy the table of contents, chapter text or draft passages into a tracked file (`docs/`, `code/`,
  any `CLAUDE.md` or `README.md`): refer to the file by path instead. Check `git status --ignored` after adding
  a file here.
- Everything here is thesis text: write it in Polish. Say „analiza danych czasu rzeczywistego”, never „szereg
  czasowy” (advisor).
- `spis_tresci.md` is the canonical table of contents. Change it only when Arek asks, keep the copy in the current
  advisor e-mail draft (`knowledge/advisor/emails_to_advisor/`) identical, and record in `spis_tresci_wzorce.md` which opened
  source each change follows.
- **Never invent structure or wording** (Arek, 2026-11-13). Base headings and phrasing on works that were actually
  opened and read; what has no source stays unchanged or goes to `docs/open_questions.md`.
- **Never invent citations, numbers or URLs.** Thesis numbers come only from runs on frozen data (root `CLAUDE.md`,
  invariant 7). Mark anything not checked against the original as „do sprawdzenia”.
- LaTeX lives only in `latex/`. Arek writes the thesis; draft or edit `.tex` files only when he asks, in small
  pieces he can review. Do not choose a template, class or bibliography style for him: propose it.
- New thesis knowledge (literature notes, formal requirements, figure plans) goes here as lower_snake_case `.md`
  files, with a row in `README.md`. Project decisions still go to `docs/decisions.md`.
