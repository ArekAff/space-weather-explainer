# knowledge/: rules for agents

Arek's rule (2026-11-14): knowledge must not get lost. This folder is where it is kept.

- **Record findings in the same session.** When work turns up something a later session would have to rediscover
  (a source checked, an endpoint tested, a claim verified or refuted, a dead end, a number measured), write a note
  in `findings/` before the final message: `findings/<YYYY-MM-DD>_<topic>.md`, using the template in
  `findings/README.md`, and add a row to the index there. One finding per note; say what was checked and how, and
  mark anything not verified as "untested".
- Findings are evidence, not decisions. A decision still needs Arek and goes to `docs/decisions.md`, linking the
  note. Standing rules go to the matching `CLAUDE.md`. Do not rewrite an old note: add a new one that says it
  supersedes the old one, and mark the old row in the index.
- **Sources.** Every file in `sources/` has a row in `sources/sources_index.md`, and a row may exist without a file
  (source known, PDF not saved). Fill the row only from the document itself or its publisher page: never invent
  authors, years, DOIs, page numbers or quotes. File names: `<year>_<first_author>_<short_title>.pdf`, lower case,
  no spaces, no Polish letters.
- **Copyright and privacy.** The GitHub repo is public. Files in `sources/` and everything in `advisor/` are
  git-ignored on purpose; never force-add them, and never paste long passages of an article into a tracked file.
  Short quotes with the citation are fine. After adding files, check `git status --ignored`.
- **Answer key.** A paper that is a case study of a TEST event is answer key (root `CLAUDE.md`, invariant 1): set
  the "answer key" column in the index to yes, and never put such a paper into the RAG corpus.
- **Corpus.** Saving a PDF here does not put it into the RAG corpus. The corpus is built by `code/ingestion` under
  the rules in `docs/rag/projekt_korpusu_rag.md` (licence, time cut-off).
- `advisor/` has its own rules in `advisor/CLAUDE.md`.
- Language: notes and the index in English; quotes in the original language; anything meant for the thesis text
  goes to `thesis/` in Polish.
