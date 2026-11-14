# Decision log

Newest at the bottom. One entry per decision: date, decision, why, and which files it affects. A later entry wins over
an earlier one and over any snapshot document in `docs/`. Only Arek decides; agents record what he decided.

## 2026-10-10

- **Domain: space weather (GO).** Best technical fit among candidates; 100 % of G3+ storms 2010–2026 link to a
  catalogued cause. Source: `dataset_research/space_weather_decision/README.md`.

## 2026-10-11

- **Users: GNSS precision positioning (mainly precision agriculture) and satellite operators.** Power grids stay as
  motivation only. Gap: no open satellite-anomaly data, so satellite effects are checked on orbit decay (Space-Track,
  CelesTrak). Source: `obszar_biznesowy/porownanie_obszarow.md`.
- **Research question and variants A (numeric only), B (plus catalogues, optional), C (plus RAG with citations)**, as
  sent to Prof. Surma. Optional D = NOAA forecaster text (from 03/2024). Source: `email_promotor/odpowiedz_prof_surma_final.txt`.
- **Richardson–Cane ICME list and SSC list are answer key only** and never enter the system.
- **Shock-arrival feature comes from DONKI IPS, not SSC.** Supersedes the e-mail, which used SSC for both.
  Affects: `email_promotor/odpowiedz_prof_surma_final.txt` §4b (SSC paragraph), `rag/projekt_korpusu_rag.md` §2.
- **Time cut-off: a document or catalogue entry is visible only if `issued_at <= t0`.** Also applies to catalogues
  in B and C. Date-only timestamps count as 23:59 UTC. Source: `rag/projekt_korpusu_rag.md` §3.
- **DONKI notes before 06/2020 are retrospective** and excluded in the main mode.
- **Evaluation event set: 131 events 04/2010–10/2026; TEST = events from 2025-01-01 (43), DEV = 88.** Corpus periods:
  before 06/2020, 06/2020–02/2024, from 03/2024. Source: `metodologia/zestaw_zdarzen_zasady.md`.
- **Data freeze 2026-12-31 for test events; final catalogue re-pull in Feb 2027.** Proposed default in the data
  gathering plan; will change if the advisor sets another date.
- **Correction: the NGDC proton-event list is current (to 2026-07-30).** The link in the advisor e-mail is correct.
  Supersedes `zrodla_danych/weryfikacja_maila.md` §1.5, which said the table ends in 03/2011.
- **The NOAA live collector is the most urgent piece of code** (live files keep only 1–7 days).
- **Repository conventions for agents:** CLAUDE.md files in English, `code/ingestion` and `code/platform` as separate
  packages (`swx_ingest`, `swx_platform`), data store outside git under `MAGISTERKA_DATA_DIR`. Defaults chosen when the
  CLAUDE.md files were created; Arek can override them.
- **Python 3.14 for all project code (Arek asked to leave 3.10 for the newest recommended version).** 3.10 reaches end
  of life in Oct 2026. 3.15 had only just been released (scheduled 2026-10-09), and big binary packages (torch for
  embeddings, and others) usually take months to ship wheels for a new version. 3.14 (Oct 2025) is supported by
  numpy, pandas, pyarrow, duckdb, scipy, scikit-learn and torch. Enforced with `.python-version` = `3.14` and
  `requires-python = ">=3.14,<3.15"` in every `pyproject.toml`. Revisit 3.15 after the thesis data freeze, not before.
  Affects: `.python-version`, `pyproject.toml`, `CLAUDE.md`, `code/CLAUDE.md`.
- **Project name is `space-weather-explainer` everywhere (Arek).** GitHub repo `ArekAff/space-weather-explainer`
  (private); a fresh clone gets that folder name, so tracked files must not say "magisterka". The data-dir env var
  is now `SWX_DATA_DIR` (was `MAGISTERKA_DATA_DIR`) and the scheduled task lives under `\space-weather-explainer\`.
  The local working folder on Arek's laptop may keep its old name. Affects: `pyproject.toml`, `CLAUDE.md`,
  `code/CLAUDE.md`, `code/ingestion` (store, collector, register script), `docs/claude_md_guide.md`.
- **ASG-EUPOS RINEX added as an effect (answer-key) source.** Arek: „tak” to adding https://system.asgeupos.pl/ for
  measuring impact. Uses: ROTI and position error at Polish stations during G3+ storms; C/N0 and observation-count
  drops on jamming days, cross-checked with rtgms.pl. Account requirement and archive depth untested. Affects:
  `data_gathering_plan.md`, `code/ingestion/CLAUDE.md`.
- **Evaluation event set v2: 157 events.** Arek sent rtgms.pl Monitoring Low alarm lists for stations WIKO (Wicko)
  and BRWO (Braniewo), 05–10/2026. 29 jamming episodes were added as J132–J160 (episode = alarms at one station with
  gaps < 6 h; default chosen by the event-set thread, Arek can override). The three 2026 period placeholders J121,
  J126, J128 were removed; their IDs are retired and all other IDs are unchanged (IDs are keyed on category + start +
  station). The rtgms.pl label and band are answer key; the system gets only the symptom (station, time, RINEX signal
  quality). Supersedes the "131 events" entry above. Affects: `metodologia/zestaw_zdarzen_*`, `metodologia/rtgms_*`.
- **DEV/TEST exception (Arek, decision card): the May 2026 rtgms.pl jamming episodes (J132–J139, BRWO) are DEV.**
  Without them DEV has no station-level jamming case for building the RINEX-symptom input. The split stays
  time-ordered inside 2026 (May DEV, June–October TEST). Totals: DEV 96, TEST 61. Supersedes "TEST = events from
  2025-01-01 (43), DEV = 88" for these events. Affects: `CLAUDE.md` invariant 5 (numbers and exception),
  `metodologia/zestaw_zdarzen_zasady.md`, `metodologia/zestaw_zdarzen_build.py`.
- **Variant B's proton events are DONKI SEP entries; the NOAA (NGDC) proton-event list is answer key only (Arek's
  OK, decision card).** The NGDC list is compiled after the fact and has no issue time, so it could not pass the time
  cut-off. DONKI SEP and the NGDC list both derive from GOES >10 MeV flux, so B's input and the radiation key are not
  fully independent; say so in the thesis. Affects: `CLAUDE.md` (variant B row, invariant 1).
- **Analogue features follow knowledge access (Arek's OK, decision card).** A matches on numeric features only
  (Kp/Hp30, solar wind; a shock detected from those numbers is numeric). B and C add DONKI filters through the time
  gate: shock (IPS), CME speed, driver type. The GO report already labels the shock flag as knowledge (§4.3). Its
  0.131 benchmark used SSC, now answer key, so re-measure it with DONKI IPS; A's benchmark is climatology by onset
  level (0.095). Affects: `CLAUDE.md` (variant rows A and B, key numbers), `code/platform/CLAUDE.md` (analogues).

## 2026-10-12

- **B's shock flag comes from DONKI's real-time IPS alerts (notifications, gated on `messageIssueTime`), not from IPS
  catalogue entries (Arek: "on time").** The readiness audit found IPS entries appear a median 77 h after the shock
  (05/2024; the 2024-05-10 shock 4.3 days later) and years later before 2020, so the time gate hides them at t0; the
  alert for the 2024-05-10 shock came 25 min after it. Catalogue entries stay usable through the gate on
  `submissionTime`. Affects: `CLAUDE.md` invariant 2, `code/platform/CLAUDE.md`, `code/ingestion/CLAUDE.md`.
- **Rebuild the event set with `normalized/gfz_kp` (Arek: yes).** Adds the missing G3 storm of 2026-10-10 to TEST
  and fills Kp for J160. Run by the event-set thread, which keeps both copies of the set in sync.
- **Event set v3: 158 events, DEV 96, TEST 62 (rebuild above).** B161 is the G3 storm with onset 2026-10-10 15:00 UTC
  (Kp 7+), in TEST. It is found in GFZ Kp with the storm list's own rules (bins with Kp ≥ 5- merged when ≤ 24 h apart;
  end = last bin + 3 h). The samples (G1–G2, quiet days, shocks without a storm) stay frozen on data up to 2026-10-09,
  so newer Kp only adds G3+ storms and no other event changed (default chosen by the event-set thread; Arek can
  override). The DONKI entries for 9–11 Oct came from the DONKI API on 2026-10-12 and are in
  `metodologia/donki_uzupelnienie_2026-10.json`, because the catalogues end on 2026-10-09. Supersedes the 157-event
  totals above. Affects: `CLAUDE.md` invariant 5 (TEST 61 → 62), `metodologia/zestaw_zdarzen_*`.

## 2026-10-24

- **The measured effect of the 13 TEST G3+ storms in the answer key is ROTI only (Arek, decision card).** ROTI comes
  from BRWO RINEX 3.04 at 30 s (POZGEO D, 12 h before each storm to at least 6 h after it), computed with the same
  ROT/ROTI functions as the rtgms.pl alarm symptoms (GPS L1/L2 and Galileo E1/E5a, 5-min window, elevation >= 30 deg).
  Position error is not computed and stays an expected effect: single-frequency positions from the broadcast
  ephemerides would only show metre-level errors, and PPP would need IGS products, a new data source. Results in the
  Claude project files: `metodologia/rinex_test/burze_roti.md`. Affects: `metodologia/zestaw_zdarzen_zasady.md`
  (measured effect).

## 2026-11-13 (meeting with Prof. Surma; recorded from Arek's meeting notes and replies)

- **Business problem reversed: monitor the space-weather situation, not the satellites.** Once a day the platform
  analyses the current situation and issues an early warning: what could happen to satellites and to GNSS positioning,
  as the most probable incident type from a predefined catalogue. Supersedes the framing "explain a single incident a
  user reports" in `email_promotor/odpowiedz_prof_surma_final.txt` §1–3 and the presentation.
- **Terminology (advisor): "analiza danych czasu rzeczywistego", not "szereg czasowy"/"szeregi czasowe"** in the
  thesis and in anything sent to the advisor.
- **Variants: A and C stay, B is dropped (advisor: "warianty a, c super, bez B").** Third scenario (Arek): C with a
  decision model of the "System One" kind instead of the classic LLM; the comparison shows how much the decision model
  improves the platform. The decision model does not have to be Jev (TypeSafe AI, launched 2026-09-15); Jev is the
  example. Scenarios: A = numeric data + classic LLM; C = data + DONKI catalogues + RAG + classic LLM; C-decision =
  same knowledge as C, the decision model picks the incident type. Supersedes the variant list of 2026-10-11 (B, D).
- **Comparison criteria: cost, quality, time. Simple thesis, no hybrid approaches** (advisor).
- **Incident catalogue in the style of cybersecurity incident taxonomies** (class → type → indicators), covering
  GNSS positioning, satellites in orbit and their combination (Arek). Working draft (6 classes, 16 types, sources):
  Claude doc "Materiały dla promotora na 20.11", https://claude.ai/artifact/Du7BQy5kG4i5y9ecmM6WBU. Only types
  confirmed by a cited paper go to the advisor (Arek: "if anything is not confirmed drop it").
- **Space debris and space situational awareness (SSA) are covered in the theory chapter** (advisor).
- **Working title (proposal sent to the advisor):** „Wczesne ostrzeganie o zagrożeniach pogody kosmicznej dla systemów
  satelitarnych: analiza porównawcza modelu językowego z RAG i modelu decyzyjnego”. Supersedes the title of 2026-10-11.
- **Milestones (advisor).** By 2026-11-20: title and table of contents, papers showing space weather affects
  satellites and positioning, draft incident-category list (e-mail draft:
  `email_promotor/mail_2026-11-20_draft.md`). By January 2027: PoC of both
  approaches, data sources connected, first comparative results on simple data with the category list; a working
  environment, not a finished system.
- Affects: `CLAUDE.md` (title, summary, research design), `code/platform/CLAUDE.md` (pipeline, variants, evaluation),
  `docs/README.md`, `open_questions.md`. Snapshot docs that still describe B or the old framing:
  `email_promotor/odpowiedz_prof_surma_final.txt`, `metodologia/z_czym_porownac.md`, `rag/projekt_korpusu_rag.md`,
  `maile_surma/Prezentacja_temat_pracy.pptx`.

## 2026-11-13 (table of contents as a thesis resource; Arek, in the Claude project)

- **The table of contents is a thesis resource in its own folder**: `praca_magisterska/spis_tresci.md` (canonical,
  working version 2). The copy in `email_promotor/mail_2026-11-20_draft.md` is kept identical.
- **Its structure and wording follow real works, not an invented style** (Arek: "dont make up any styles of the spis
  tresci look at highly remarked papers on similar topic and base the style and phrasing of the spis tresci on
  them"). The SGH thesis requirements, the theses and papers that were opened, and the source of every change from
  version 1 are in `praca_magisterska/spis_tresci_wzorce.md`.
- **The comparison criteria (koszt, jakość, czas) are described in 5.5**, in the comparison-environment chapter next
  to the scenarios, not in theory chapter 3 as in version 1 (Arek, decision card 2026-11-13: "Move to 5.5 (as
  saved)"). Rejected: criteria in chapter 3 plus a measures section in chapter 5; criteria only in chapter 3.
- **Chapter 4 gets a data-processing subsection**: new 4.2 „Przetwarzanie danych czasu rzeczywistego”, so the chapter
  title's "analiza danych czasu rzeczywistego" has a subsection of its own; the knowledge section becomes 4.3 and the
  test-event section 4.4 (Arek, 2026-11-13: "lets add it"). Wording: the heading „Przetwarzanie danych” from a
  reference thesis plus the advisor's term from the chapter title.
- The rest of version 2 is a proposal until Arek confirms it; its open points are in `open_questions.md`.
