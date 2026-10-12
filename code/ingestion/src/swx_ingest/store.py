"""Data store helpers shared by all sources: location, lock, raw archive and manifest.

Layout and contract: see `code/CLAUDE.md` ("Data store"). All timestamps are tz-aware UTC.
"""

from __future__ import annotations

import gzip
import hashlib
import logging
import os
import ssl
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import certifi
import pandas as pd

log = logging.getLogger(__name__)

MANIFEST_COLUMNS = [
    "fetched_at",
    "source",
    "name",
    "url",
    "path",
    "sha256",
    "bytes",
    "licence",
]


def data_dir() -> Path:
    """Root of the data store: `SWX_DATA_DIR`, else `<repo>/data/`."""
    env = os.environ.get("SWX_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # store.py -> swx_ingest -> src -> ingestion -> code -> <repo>
    return Path(__file__).resolve().parents[4] / "data"


def utc_now() -> datetime:
    return datetime.now(UTC)


def stamp(t: datetime) -> str:
    """Compact UTC stamp for file names, e.g. 20261011T173000Z."""
    return t.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def write_parquet_atomic(df: pd.DataFrame, path: Path) -> None:
    """Write via a temporary file and rename, so a crash never leaves a half-written table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


class StoreLock:
    """Exclusive lock file so two collector runs never write at the same time.

    A lock older than `stale_after_s` is treated as left over from a crash and removed. With `wait_s` > 0 a held
    lock is retried until that many seconds have passed.
    """

    def __init__(self, path: Path, stale_after_s: float = 2 * 3600, wait_s: float = 0.0) -> None:
        self.path = path
        self.stale_after_s = stale_after_s
        self.wait_s = wait_s

    def __enter__(self) -> StoreLock:  # noqa: PYI034
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.wait_s
        while True:
            if self.path.exists() and time.time() - self.path.stat().st_mtime > self.stale_after_s:
                log.warning("Removing stale lock %s", self.path)
                self.path.unlink(missing_ok=True)
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError as exc:
                if time.monotonic() >= deadline:
                    raise RuntimeError(f"Another run holds the lock {self.path}") from exc
                time.sleep(0.2)
        with os.fdopen(fd, "w") as f:
            f.write(f"pid={os.getpid()} started={utc_now().isoformat()}\n")
        return self

    def __exit__(self, *exc: object) -> None:
        self.path.unlink(missing_ok=True)


@dataclass
class RawRecord:
    """Result of archiving one response. `changed` is False when the bytes equal the last archived copy."""

    changed: bool
    sha256: str
    path: str | None  # relative to the data store root; None when unchanged


class RawArchive:
    """Writes byte-for-byte responses (gzipped) to `raw/<source>/<name>/` and keeps `raw/manifest.parquet`.

    Call `flush()` to persist new manifest rows (at the end of a run, or after each large file).
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.manifest_path = root / "raw" / "manifest.parquet"
        if self.manifest_path.exists():
            self._manifest = pd.read_parquet(self.manifest_path)
        else:
            self._manifest = pd.DataFrame(columns=MANIFEST_COLUMNS)
        self._new_rows: list[dict] = []
        self._last_hash: dict[tuple[str, str], str] = {}
        if len(self._manifest):
            last = self._manifest.sort_values("fetched_at").groupby(["source", "name"]).tail(1)
            self._last_hash = {(r.source, r.name): r.sha256 for r in last.itertuples()}

    def last_sha256(self, source: str, name: str) -> str | None:
        return self._last_hash.get((source, name))

    def last_path(self, source: str, name: str) -> str | None:
        """Archive path of the most recent saved copy of (source, name), or None."""
        for row in reversed(self._new_rows):
            if row["source"] == source and row["name"] == name:
                return row["path"]
        m = self._manifest
        hit = m[(m["source"] == source) & (m["name"] == name)]
        return str(hit.sort_values("fetched_at")["path"].iloc[-1]) if len(hit) else None

    def save(
        self, source: str, name: str, url: str, content: bytes, fetched_at: datetime, licence: str
    ) -> RawRecord:
        """Archive `content` unless it is identical to the previous copy of the same (source, name)."""
        sha = hashlib.sha256(content).hexdigest()
        if self._last_hash.get((source, name)) == sha:
            log.info("%s/%s unchanged (sha256 %s), not archived", source, name, sha[:12])
            return RawRecord(changed=False, sha256=sha, path=None)
        rel = Path("raw") / source / name.replace(".", "_") / f"{stamp(fetched_at)}_{name}.gz"
        dest = self.root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".tmp")
        with gzip.open(tmp, "wb") as f:
            f.write(content)
        os.replace(tmp, dest)
        self._last_hash[(source, name)] = sha
        self._new_rows.append(
            {
                "fetched_at": fetched_at,
                "source": source,
                "name": name,
                "url": url,
                "path": rel.as_posix(),
                "sha256": sha,
                "bytes": len(content),
                "licence": licence,
            }
        )
        return RawRecord(changed=True, sha256=sha, path=rel.as_posix())

    def flush(self) -> None:
        """Append this archive's new rows to `raw/manifest.parquet`.

        Several collectors share the manifest (the NOAA task can run during a history pull), so the file is re-read
        under a short lock and only new rows are appended; rows written by other runs in the meantime survive.
        """
        if not self._new_rows:
            return
        new = pd.DataFrame(self._new_rows, columns=MANIFEST_COLUMNS)
        with StoreLock(self.root / "raw" / ".manifest.lock", stale_after_s=600, wait_s=120):
            if self.manifest_path.exists():
                current = pd.read_parquet(self.manifest_path)
                new = new[~new["path"].isin(current["path"])]
            else:
                current = pd.DataFrame(columns=MANIFEST_COLUMNS)
            merged = pd.concat([f for f in (current, new) if len(f)], ignore_index=True)
            merged["fetched_at"] = pd.to_datetime(merged["fetched_at"], utc=True)
            write_parquet_atomic(merged, self.manifest_path)
        self._manifest = merged
        self._new_rows = []


# --------------------------------------------------------------------------- fetching


class FetchError(RuntimeError):
    pass


# Mozilla's CA bundle instead of the Windows store: on 2026-10-11 the Windows store on the laptop lacked the root
# for kp.gfz.de (CERTIFICATE_VERIFY_FAILED), while curl and certifi verified it.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def http_get(url: str, user_agent: str, attempts: int = 3, timeout_s: float = 60.0) -> bytes:
    """GET with a descriptive User-Agent and capped exponential back-off (5 s, 10 s, ... max 30 s).

    4xx errors are not retried. Raises `FetchError` after the last attempt.
    """
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout_s, context=_SSL_CONTEXT) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and 400 <= exc.code < 500:
                break  # a 404 will not fix itself
            if i < attempts - 1:
                time.sleep(min(30.0, 5.0 * 2**i))
    raise FetchError(f"{url}: {last}")


# --------------------------------------------------------------------------- normalised store

KEY = ["time_utc", "quantity", "qualifier"]


def _same(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a == b) | (a.isna() & b.isna())


def merge_versions(
    existing: pd.DataFrame,
    new: pd.DataFrame,
    columns: Sequence[str],
    compare: Sequence[str] = ("value", "unit"),
) -> pd.DataFrame:
    """Return only the rows of `new` that are new keys or differ in any `compare` column, with versions set.

    Existing rows are never modified: a change is a new version (latest + 1). Keys are (time_utc, quantity,
    qualifier).
    """
    if new.empty:
        return new
    if existing.empty:
        return new.assign(version=1)
    latest = existing.sort_values("version").groupby(KEY, as_index=False).tail(1)
    old = {c: f"_old_{c}" for c in [*compare, "version"]}
    latest = latest[KEY + list(old)].rename(columns=old)
    m = new.drop(columns="version").merge(latest, on=KEY, how="left")
    is_new = m["_old_version"].isna()
    same = pd.Series(True, index=m.index)
    for c in compare:
        same &= _same(m[c], m[old[c]])
    m = m[is_new | ~same].copy()
    m["version"] = m["_old_version"].fillna(0).astype(int) + 1
    return m[list(columns)]


class SeriesStore:
    """Monthly Parquet files per dataset under `normalized/<dataset>/<YYYY-MM>.parquet`.

    `columns` is the table schema; `compare` lists the columns whose change creates a new version.
    """

    def __init__(
        self,
        root: Path,
        dataset: str,
        columns: Sequence[str],
        compare: Sequence[str] = ("value", "unit"),
    ) -> None:
        self.dir = root / "normalized" / dataset
        self.columns = list(columns)
        self.compare = tuple(compare)

    def _path(self, month: str) -> Path:
        return self.dir / f"{month}.parquet"

    def read_month(self, month: str) -> pd.DataFrame:
        p = self._path(month)
        return pd.read_parquet(p) if p.exists() else pd.DataFrame(columns=self.columns)

    def months(self) -> list[str]:
        return sorted(p.stem for p in self.dir.glob("*.parquet")) if self.dir.exists() else []

    def read_all(self) -> pd.DataFrame:
        frames = [f for f in (self.read_month(m) for m in self.months()) if len(f)]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=self.columns)

    def last_time(self) -> pd.Timestamp | None:
        for month in reversed(self.months()):
            df = self.read_month(month)
            if len(df):
                return pd.Timestamp(df["time_utc"].max())
        return None

    def times_since(self, since: pd.Timestamp) -> pd.Series:
        frames = [self.read_month(m) for m in self.months() if m >= since.strftime("%Y-%m")]
        frames = [f for f in frames if len(f)]
        if not frames:
            return pd.Series([], dtype="datetime64[ns, UTC]")
        t = pd.concat(frames)["time_utc"]
        return pd.Series(sorted(t[t >= since].unique()))

    def add(self, rows: pd.DataFrame) -> int:
        """Merge rows into the store; returns how many rows (new keys or new versions) were written."""
        if rows.empty:
            return 0
        written = 0
        months = rows["time_utc"].dt.strftime("%Y-%m")
        for month, part in rows.groupby(months):
            existing = self.read_month(month)
            add = merge_versions(existing, part, self.columns, self.compare)
            if add.empty:
                continue
            out = pd.concat([f for f in (existing, add) if len(f)], ignore_index=True)
            out = out.sort_values(KEY + ["version"], ignore_index=True)
            write_parquet_atomic(out, self._path(month))
            written += len(add)
        return written
