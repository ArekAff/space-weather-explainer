"""Shared pieces for the historical series (GFZ Kp/Hp30, OMNI2): table schema, file ingestion, coverage report.

Historical tables live in `normalized/<dataset>/<YYYY-MM>.parquet` like the live ones, but are never mixed with
the NOAA live archive. `time_utc` is always the START of the averaging interval (3 h for Kp, 30 min for Hp30, 1 h
for OMNI2, the UT day for daily indices). A re-pull adds a new version when value, unit or status changed, so the
move from `pre` to `def` is kept as history.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from swx_ingest.store import FetchError, RawArchive, SeriesStore, utc_now, write_parquet_atomic

log = logging.getLogger(__name__)

HISTORY_COLUMNS = [
    "time_utc",
    "quantity",
    "qualifier",
    "value",
    "unit",
    "version",
    "source",
    "product",
    "status",
    "status_basis",  # why the status is what it is (source flag, documented span, or "no status in source")
    "retrieved_at",
    "source_file",
]
COMPARE = ("value", "unit", "status")
STATUSES = {"realtime", "pre", "def", "provisional"}
GAP_COLUMNS = ["quantity", "start_utc", "end_utc", "missing_steps"]
COVERAGE_COLUMNS = [
    "quantity",
    "first_utc",
    "last_utc",
    "rows",
    "nan_rows",
    "gap_runs",
    "longest_gap_steps",
    "status_counts",
]


def history_store(root: Path, dataset: str) -> SeriesStore:
    return SeriesStore(root, dataset, HISTORY_COLUMNS, COMPARE)


def finish_rows(
    rows: pd.DataFrame, source: str, product: str, retrieved_at: datetime, source_file: str
) -> pd.DataFrame:
    """Add provenance columns and check the status vocabulary. `rows` already has time, quantity, value, unit,
    status and status_basis."""
    bad = set(rows["status"].unique()) - STATUSES
    if bad:
        raise ValueError(f"unknown status values {bad}")
    out = rows.copy()
    if "qualifier" not in out:
        out["qualifier"] = ""
    out["version"] = 0
    out["source"] = source
    out["product"] = product
    out["retrieved_at"] = pd.Timestamp(retrieved_at)
    out["source_file"] = source_file
    return out[HISTORY_COLUMNS]


def mask_fill(values: pd.Series, fill: float, label: str) -> pd.Series:
    """Replace a documented fill value with NaN and log how many were replaced."""
    hit = values == fill
    if hit.any():
        log.info("%s: %d fill values (%s) set to NaN", label, int(hit.sum()), fill)
    return values.mask(hit)


@dataclass
class FileResult:
    name: str
    ok: bool
    changed: bool = False
    rows_added: int = 0
    detail: str = ""


class NormalizedState:
    """Which version of each raw file has been fully normalised, in `raw/<source>/normalized.json`.

    The key is the file's SHA-256 plus, where status rules come from another document, that document's SHA-256. It
    is written only after the last table write for a file, so a run killed halfway re-normalises that file next time
    instead of skipping it as unchanged.
    """

    def __init__(self, root: Path, source: str) -> None:
        self.path = root / "raw" / source / "normalized.json"
        self.done: dict[str, str] = json.loads(self.path.read_text()) if self.path.exists() else {}

    def is_done(self, name: str, key: str) -> bool:
        return self.done.get(name) == key

    def mark(self, name: str, key: str) -> None:
        self.done[name] = key
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.done, indent=2, sort_keys=True))
        os.replace(tmp, self.path)


def ingest_file(
    root: Path,
    raw: RawArchive,
    state: NormalizedState,
    source: str,
    name: str,
    url: str,
    licence: str,
    fetcher: Callable[[str], bytes],
    to_rows: Callable[[bytes, datetime, str], dict[str, pd.DataFrame]],
    rules_key: str = "",
    force: bool = False,
) -> FileResult:
    """Fetch one file, archive it raw, normalise it into one or more datasets.

    `to_rows(content, fetched_at, raw_path)` returns {dataset: rows}. A file is skipped when this exact content (and
    `rules_key`, the hash of whatever sets its status) was already normalised completely, unless `force`.
    """
    fetched_at = utc_now()
    try:
        content = fetcher(url)
    except FetchError as exc:
        log.error("%s: %s", name, exc)
        return FileResult(name, ok=False, detail=str(exc))
    rec = raw.save(source, name, url, content, fetched_at, licence)
    raw.flush()  # persist provenance before the slow normalising step
    key = f"{rec.sha256}:{rules_key}" if rules_key else rec.sha256
    if not force and state.is_done(name, key):
        return FileResult(name, ok=True, changed=rec.changed)
    raw_path = rec.path or raw.last_path(source, name) or ""
    try:
        tables = to_rows(content, fetched_at, raw_path)
    except (ValueError, KeyError, IndexError) as exc:
        log.error("%s: parse failed: %s", name, exc)
        return FileResult(name, ok=False, changed=rec.changed, detail=f"parse failed: {exc}")
    added = sum(history_store(root, ds).add(rows) for ds, rows in tables.items())
    state.mark(name, key)
    log.info("%s: %d rows added", name, added)
    return FileResult(name, ok=True, changed=rec.changed, rows_added=added)


def latest_values(df: pd.DataFrame) -> pd.DataFrame:
    """Latest version of each (time_utc, quantity, qualifier)."""
    if df.empty:
        return df
    return df.sort_values("version").groupby(["time_utc", "quantity", "qualifier"], as_index=False).tail(1)


def coverage(
    frames: Iterable[pd.DataFrame],
    step: pd.Timedelta,
    step_by_quantity: dict[str, pd.Timedelta] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-quantity coverage and gap list from an iterable of table chunks (e.g. one month each).

    Uses the latest version of each key. A gap is a stretch between two valid values longer than `step`; values that
    are NaN count as missing. `step_by_quantity` overrides `step` (e.g. daily Ap in a 3-hourly table). Gaps are only counted between a quantity's first and last valid value. Each chunk must
    hold every version of its keys (true for monthly files).
    """
    valid_times: dict[str, list[np.ndarray]] = defaultdict(list)
    rows: dict[str, int] = defaultdict(int)
    nans: dict[str, int] = defaultdict(int)
    statuses: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for df in frames:
        if df.empty:
            continue
        df = latest_values(df)
        for q, part in df.groupby("quantity"):
            rows[q] += len(part)
            ok = part["value"].notna()
            nans[q] += int((~ok).sum())
            for k, v in part["status"].value_counts().items():
                statuses[q][k] += int(v)
            valid_times[q].append(part.loc[ok, "time_utc"].to_numpy(dtype="datetime64[ns]"))
    cov_rows, gap_rows = [], []
    for q in sorted(rows):
        step_ns = np.timedelta64((step_by_quantity or {}).get(q, step).value, "ns")
        status_counts = ";".join(f"{k}={v}" for k, v in sorted(statuses[q].items()))
        t = (
            np.sort(np.concatenate(valid_times[q]))
            if valid_times[q]
            else np.array([], dtype="datetime64[ns]")
        )
        if len(t) == 0:
            cov_rows.append([q, pd.NaT, pd.NaT, rows[q], nans[q], 0, 0, status_counts])
            continue
        d = np.diff(t)
        idx = np.nonzero(d > step_ns)[0]
        missing = (d[idx] // step_ns - 1).astype(int)
        for i, n in zip(idx, missing, strict=True):
            gap_rows.append(
                [q, pd.Timestamp(t[i] + step_ns, tz="UTC"), pd.Timestamp(t[i + 1], tz="UTC"), int(n)]
            )
        cov_rows.append(
            [
                q,
                pd.Timestamp(t[0], tz="UTC"),
                pd.Timestamp(t[-1], tz="UTC"),
                rows[q],
                nans[q],
                len(idx),
                int(missing.max()) if len(idx) else 0,
                status_counts,
            ]
        )
    return pd.DataFrame(cov_rows, columns=COVERAGE_COLUMNS), pd.DataFrame(gap_rows, columns=GAP_COLUMNS)


def write_coverage(
    root: Path,
    source: str,
    dataset: str,
    step: pd.Timedelta,
    step_by_quantity: dict[str, pd.Timedelta] | None = None,
) -> pd.DataFrame:
    """Rebuild `raw/<source>/<dataset>_coverage.csv` and `<dataset>_gaps.parquet`; return the coverage table."""
    store = history_store(root, dataset)
    cols = ["time_utc", "quantity", "qualifier", "value", "version", "status"]
    chunks = (pd.read_parquet(store.dir / f"{m}.parquet", columns=cols) for m in store.months())
    cov, gaps = coverage(chunks, step, step_by_quantity)
    out = root / "raw" / source
    out.mkdir(parents=True, exist_ok=True)
    cov.to_csv(out / f"{dataset}_coverage.csv", index=False)
    write_parquet_atomic(gaps, out / f"{dataset}_gaps.parquet")
    return cov


def setup_logging(root: Path, log_name: str, verbose: bool) -> None:
    (root / "logs").mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.FileHandler(root / "logs" / log_name, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ]
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fmt.converter = time.gmtime  # log times in UTC
    for h in handlers:
        h.setFormatter(fmt)
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, handlers=handlers, force=True)


def print_results(results: list[FileResult]) -> None:
    print(f"{'file':40} {'ok':3} {'changed':7} rows_added")
    for r in results:
        print(f"{r.name:40} {'y' if r.ok else 'N':3} {'y' if r.changed else '-':7} {r.rows_added} {r.detail}")


def print_coverage(dataset: str, cov: pd.DataFrame) -> None:
    print(f"\n{dataset}")
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(cov.to_string(index=False))
