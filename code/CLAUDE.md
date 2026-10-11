# code/: shared conventions for all application code

Two parts with one contract between them:
- `ingestion/`: the only code that talks to the network. Fetches, archives raw responses, builds normalised
  tables and the text corpus. See `ingestion/CLAUDE.md`.
- `platform/`: the system itself. Reads only what ingestion wrote, never the network. See `platform/CLAUDE.md`.

`ingestion/` holds the NOAA SWPC live collector (since 2026-10-11); `platform/` has no code yet. Follow the layout
below and update this file if you have to deviate.

## Layout

```
code/
  pyproject.toml            # uv workspace root (members: ingestion; add platform when it starts)
  .python-version           # 3.14, repeated here because uv stops looking at the workspace root
  ingestion/
    pyproject.toml          # package swx_ingest
    src/swx_ingest/
    tests/
  platform/
    pyproject.toml          # package swx_platform
    src/swx_platform/
    tests/
```

- Package names are `swx_ingest` and `swx_platform`. Never name an importable package `platform` or `code`: both
  shadow Python standard-library modules.
- The repo-root `pyproject.toml` and `main.py` are Arek's stub from `uv init`; leave them alone. The workspace root is
  `code/pyproject.toml`.
- The two packages share no code at first. If shared types become necessary, propose a third member (`swx_common`)
  instead of importing across parts.

## Tooling

- **Python 3.14 only.** The repo-root `.python-version` says `3.14` and every `pyproject.toml` in the repo (root,
  `code/`, each member) sets `requires-python = ">=3.14,<3.15"`, so uv refuses any other interpreter. Install it with
  `uv python install 3.14`. Don't run project code with a system Python or another version, and don't change the pin
  without Arek. Why 3.14 and not 3.15: see `docs/decisions.md` (2026-10-11).
- Packages via `uv` (`uv sync`, `uv run pytest`, `uv add <pkg>`). Before adding a dependency, check it ships wheels
  for CPython 3.14 on Windows.
- Lint and format with `ruff` (`uv run ruff check --fix` and `uv run ruff format`); tests with `pytest`.
- Add a dependency only when it earns its place, and say why in the commit. Prefer pandas + pyarrow (Parquet) and
  DuckDB for queries. These are already used in `dataset_research/` scripts.
- Commands, run from `code/`: `uv sync` (creates `code/.venv`), `uv run pytest`, `uv run ruff check --fix`,
  `uv run ruff format`. Run `uv run python --version` after `uv sync`; a 3.10 venv means the pin was not picked up.

## Data store (the contract between the two parts)

Root directory: env var `SWX_DATA_DIR`, default `<repo>/data/` (git-ignored). Layout:

| Path | Written by | Read by | Content |
|---|---|---|---|
| `raw/<source>/<file>/` | ingestion | ingestion | Byte-for-byte responses, gzipped, `<fetched_at_utc>_<file>.gz`, with SHA-256 in `raw/manifest.parquet`; per-source gap log and state files sit in `raw/<source>/` |
| `normalized/<dataset>/` | ingestion | platform | Parquet tables, one file per month (`YYYY-MM.parquet`), one row per (time, quantity, qualifier, version), with provenance columns |
| `logs/` | ingestion | Arek | Run logs, e.g. `noaa_live.log` (UTC timestamps) |
| `corpus/` | ingestion | platform | Expert texts and chunks with metadata from `docs/rag/projekt_korpusu_rag.md` §4 |
| `answer_key/` | ingestion | platform evaluation only | Richardson–Cane, SSC, TEC/ROTI, orbits, jamming cases |
| `runs/` | platform | platform, Arek | Evaluation runs: config, model ID, prompt version, outputs, metrics |
| `freeze/<date>/` | ingestion | everyone | Frozen copies used for thesis numbers |

Required columns in every normalised table: `time_utc`, `quantity`, `value`, `unit`, `source`, `status`,
`retrieved_at`, `source_file`. Text documents also carry `issued_at`, `issued_precision`, `is_retrospective`.
Changing a column or path is a contract change: update this table, both parts, and their tests in the same change.

## Rules for all code

- Time: every timestamp is a tz-aware UTC `datetime` or `pandas.Timestamp`. Convert at the boundary where data enters.
  Never use naive datetimes or local time.
- Leakage: any function that answers "what was known at time t" takes an explicit `as_of` argument. No default value,
  no "now".
- Missing values: convert source fill values (OMNI 9999.9 and similar, GFZ -1) to NaN at ingestion and log how many.
- Determinism: seed every random choice (the event set used seed 2026) and write the seed into run metadata.
- Config through environment variables or a typed settings object. No paths, keys or model IDs in code.
- Logging through `logging`, not `print`, in library code. Scripts may print summaries.
- Tests: unit tests never touch the network. Store small recorded responses in `tests/fixtures/`. Every rule in the
  root "Research design" section that code enforces gets a test that fails if the rule is broken.
- Type hints on public functions; docstrings say units and time conventions.
- Commits: small, one concern each, message in English, imperative mood (e.g. `ingestion: add NOAA plasma collector`).
