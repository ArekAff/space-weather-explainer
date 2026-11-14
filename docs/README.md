# docs/: project knowledge for the thesis and for agents

What was decided, what is still open, and the reference documents behind the design. The folders `metodologia/`,
`rag/`, `zrodla_danych/` and `obszar_biznesowy/` were copied on 2026-10-11 from the shared folder of the thesis Claude
project and keep its folder names, so the relative links inside those documents still work. Originals are in Polish
unless noted. Later corrections live in `decisions.md`, which wins over any older document.

Since 2026-11-14 three things that used to sit here have their own top-level folders: the evaluation event set
(`../evaluation/event_set/`), the thesis text (`../thesis/`) and the advisor correspondence (`../knowledge/advisor/`, next to article PDFs in
`../knowledge/sources/` and dated findings in `../knowledge/findings/`).
Entries in `decisions.md` written before that date use the old paths; the mapping is in its 2026-11-14 entry.

## Read this when...

Paths without `../` are inside `docs/`.

| Task | Read |
|---|---|
| Understand the thesis concept as of 2026-11-13 (scenarios, incident catalogue, title, milestones) | `decisions.md`, entry 2026-11-13; draft catalogue and papers: https://claude.ai/artifact/Du7BQy5kG4i5y9ecmM6WBU |
| Know what is decided / still open | `decisions.md`, `open_questions.md` |
| Decide what to compare and how to score explanations | `metodologia/z_czym_porownac.md` (PL) |
| Build the RAG corpus: sources, exclusions, time cut-off, metadata, licences | `rag/projekt_korpusu_rag.md` (PL) |
| Write a fetcher or the NOAA collector | `data_gathering_plan.md` (EN), then `zrodla_danych/jak_pobrac_dane_liczbowe.md` (EN) |
| Check access, licence and terms of a source | `zrodla_danych/dostep_do_zrodel_danych.xlsx` |
| Set up Earthdata / Space-Track / the CCMC e-mail | `zrodla_danych/konta_do_zalozenia.md` (EN) |
| See which advisor-email claims were checked | `zrodla_danych/weryfikacja_maila.md` (PL; one correction there is wrong, see `decisions.md`) |
| Recall why GNSS + satellites were chosen | `obszar_biznesowy/porownanie_obszarow.md` (PL) |
| Maintain the CLAUDE.md files | `claude_md_guide.md` |
| See which published conventions each folder type follows, and where the repo differs on purpose | `repository_conventions.md` |
| Work with the evaluation events, DEV/TEST split, answer key, t0, or rebuild the event set | `../evaluation/README.md` |
| Find an article to cite, or see what earlier sessions found out | `../knowledge/README.md` |
| Use or change the thesis table of contents, or write LaTeX | `../thesis/README.md` |
| Understand the original concept as sent to the advisor (Oct 2026; B and the framing are superseded), find the diagrams or the current e-mail draft | `../knowledge/advisor/README.md` |

## Not copied here

- Arek's learning plan (space weather and time series, 10 weeks):
  https://claude.ai/code/artifact/d279770b-1c5e-4c0c-9096-93c07ac135cf. It is for Arek, not a spec for code.
- The Polish original of the data gathering plan:
  https://claude.ai/code/artifact/ad0e1d0b-0b53-40b8-ad0b-c979d30f1962. `data_gathering_plan.md` is its English summary.
- The exploratory research and first downloads stay in `../dataset_research/` (read only).
- RINEX tests and alarm checks (`metodologia/rinex_test/...`) exist only in the shared folder of the Claude project.
