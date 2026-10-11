# docs/: reference documents for the thesis and for agents

Most files were copied on 2026-10-11 from the shared folder of the thesis Claude project, which agents on this
laptop cannot reach. Folder names match that shared folder, so the relative links inside the documents still work.
Originals are in Polish unless noted. Later corrections live in `decisions.md`, which wins over any older document.

## Read this when...

| Task | Read |
|---|---|
| Understand the thesis concept, data and variants as sent to the advisor | `email_promotor/odpowiedz_prof_surma_final.txt` (PL) |
| Decide what to compare and how to score explanations | `metodologia/z_czym_porownac.md` (PL) |
| Work with the evaluation events, DEV/TEST split, answer key, t0 | `metodologia/zestaw_zdarzen_zasady.md` (PL), `metodologia/zestaw_zdarzen_ewaluacja.csv` |
| Rebuild the event set | `metodologia/zestaw_zdarzen_build.py` (args: path to `dataset_research/space_weather_decision`, output folder) |
| Build the RAG corpus: sources, exclusions, time cut-off, metadata, licences | `rag/projekt_korpusu_rag.md` (PL) |
| Write a fetcher or the NOAA collector | `data_gathering_plan.md` (EN), then `zrodla_danych/jak_pobrac_dane_liczbowe.md` (EN) |
| Check access, licence and terms of a source | `zrodla_danych/dostep_do_zrodel_danych.xlsx` |
| Set up Earthdata / Space-Track / the CCMC e-mail | `zrodla_danych/konta_do_zalozenia.md` (EN) |
| See which advisor-email claims were checked | `zrodla_danych/weryfikacja_maila.md` (PL; one correction there is wrong, see `decisions.md`) |
| Recall why GNSS + satellites were chosen | `obszar_biznesowy/porownanie_obszarow.md` (PL) |
| Know what is decided / still open | `decisions.md`, `open_questions.md` |
| Maintain the CLAUDE.md files | `claude_md_guide.md` |

Diagrams sent to the advisor: `email_promotor/diagram1_pogoda_kosmiczna.png` (space-weather chain),
`email_promotor/diagram2_koncepcja_platformy.png` (platform concept).

## Not copied here

- Arek's learning plan (space weather and time series, 10 weeks):
  https://claude.ai/code/artifact/d279770b-1c5e-4c0c-9096-93c07ac135cf. It is for Arek, not a spec for code.
- The Polish original of the data gathering plan:
  https://claude.ai/code/artifact/ad0e1d0b-0b53-40b8-ad0b-c979d30f1962. `data_gathering_plan.md` is its English summary.
- The exploratory research and first downloads stay in `../dataset_research/` (read only).
