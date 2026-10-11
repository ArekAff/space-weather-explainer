"""Data store helpers shared by all sources: location, lock, raw archive and manifest.

Layout and contract: see `code/CLAUDE.md` ("Data store"). All timestamps are tz-aware UTC.
"""

from __future__ import annotations

import gzip
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

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

    A lock older than `stale_after_s` is treated as left over from a crash and removed.
    """

    def __init__(self, path: Path, stale_after_s: float = 2 * 3600) -> None:
        self.path = path
        self.stale_after_s = stale_after_s

    def __enter__(self) -> StoreLock:  # noqa: PYI034
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and time.time() - self.path.stat().st_mtime > self.stale_after_s:
            log.warning("Removing stale lock %s", self.path)
            self.path.unlink(missing_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(f"Another run holds the lock {self.path}") from exc
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

    Call `flush()` once at the end of a run to persist new manifest rows.
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
        if not self._new_rows:
            return
        new = pd.DataFrame(self._new_rows, columns=MANIFEST_COLUMNS)
        frames = [f for f in (self._manifest, new) if len(f)]
        self._manifest = pd.concat(frames, ignore_index=True)
        self._manifest["fetched_at"] = pd.to_datetime(self._manifest["fetched_at"], utc=True)
        write_parquet_atomic(self._manifest, self.manifest_path)
        self._new_rows = []
