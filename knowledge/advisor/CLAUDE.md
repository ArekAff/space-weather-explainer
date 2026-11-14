# knowledge/advisor/: rules for agents

- **Private.** The contents are git-ignored (`/knowledge/advisor/*` in `.gitignore`; only `README.md` and `CLAUDE.md` are
  tracked). Never commit, publish or copy these files elsewhere, and do not quote the advisor's e-mails outside the
  project. Run `git status --ignored` after adding a file here and check that it is listed as ignored.
- `email_threads/` and `presentations/` are records: read only.
- `emails_to_advisor/`: files without `draft` in the name were sent and are dated snapshots; do not rewrite them
  (corrections go to `docs/decisions.md`). Edit a draft only when Arek asks. Never send anything: Arek sends.
- File names carry ISO dates so they sort in time order: a new thread export is `email_threads/<YYYY-MM-DD>.pdf`, a
  new draft is `emails_to_advisor/mail_<YYYY-MM-DD>_draft.md` (date = planned sending date). Drafts are in Polish.
- The table of contents inside the current draft must stay identical to `thesis/spis_tresci.md`, which is canonical.
- A decision or instruction found in an e-mail takes effect only when Arek confirms it; then record it in
  `docs/decisions.md` with the date.
