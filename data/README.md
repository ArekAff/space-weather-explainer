# data/: the data store

Written by the collectors in `code/ingestion`. Nothing here is edited by hand, and nothing except this file is in
git. The location can be moved with the environment variable `SWX_DATA_DIR`; this folder is the default.

| Folder | Content | Rule |
|---|---|---|
| `raw/` | Every downloaded response, byte for byte, gzipped, with SHA-256 in `raw/manifest.parquet` | Immutable: never edit, overwrite or delete |
| `normalized/` | Parquet tables built from `raw/`, one file per month, every value with its source and status | Rebuilt only by the collectors; a changed value becomes a new version |
| `logs/` | Run logs, e.g. `noaa_live.log` (UTC) | Read to check the collectors |
| `corpus/`, `answer_key/`, `runs/`, `freeze/` | Planned: expert texts, answer-key datasets, evaluation runs, frozen copies for thesis numbers | Not built yet |

The full contract (file naming, required columns, who writes and reads what) is in `code/CLAUDE.md`, section
"Data store". Coverage and health of each dataset are in `code/ingestion/CLAUDE.md`, section "Status".

Back-up note: the raw NOAA live files cannot be downloaded again (the source keeps only 1–7 days), so this folder
must not be deleted or excluded from OneDrive sync without a copy elsewhere.
