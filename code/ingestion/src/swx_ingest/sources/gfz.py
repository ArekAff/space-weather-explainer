"""GFZ Potsdam geomagnetic indices: Kp/ap/Ap (+ SN, F10.7) since 1932 and the full Hp30/ap30 series.

Both come as complete text files that GFZ rewrites daily, so each run downloads the whole file (5.5 MB and 44 MB on
2026-10-11), archives it raw when the bytes changed, and merges it into:

- `normalized/gfz_kp/`: `kp`, `ap` (3-hourly, `time_utc` = interval start) and `Ap`, `sn`, `f107_obs`,
  `f107_adj` (daily, `time_utc` = 00:00 of the UT day).
- `normalized/gfz_hp30/`: `hp30`, `ap30` (30-min, `time_utc` = interval start).

Status. The Kp file's D column: D=0 Kp and SN preliminary, D=1 Kp definitive and SN preliminary, D=2 both
definitive (format file Kp_ap_Ap_SN_F107_format.txt). Kp, ap and Ap take `def` for D>=1, else `pre`; SN takes `def`
only for D=2. F10.7 and Hp30 carry no status in the source, so they are stored as `provisional` with that reason in
`status_basis`; Hp30 also records the Hpo version from the file header. Missing data (-1) becomes NaN.

Run: `cd code; uv run swx-gfz` (both files). Not scheduled: run it monthly and before the freeze.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from swx_ingest.history import (
    FileResult,
    NormalizedState,
    finish_rows,
    ingest_file,
    mask_fill,
    print_coverage,
    print_results,
    setup_logging,
    write_coverage,
)
from swx_ingest.store import RawArchive, StoreLock, data_dir, http_get

log = logging.getLogger(__name__)

SOURCE = "gfz"
BASE_URL = "https://kp.gfz.de/app/files/"
KP_FILE = "Kp_ap_Ap_SN_F107_since_1932.txt"
HP30_FILE = "Hp30_ap30_complete_series.txt"
LICENCE_KP = (
    "CC BY 4.0 (Kp, ap, Ap, F10.7); sunspot number CC BY-NC 4.0 (WDC-SILSO). Cite Matzka et al. 2021, "
    "doi:10.1029/2020SW002641"
)
LICENCE_HP30 = "CC BY 4.0. Cite Yamazaki et al. 2024 (doi:10.22541/essoar.171838396.68563140/v1) and doi:10.5880/Hpo.0003"
USER_AGENT = "swx_ingest/0.1 (academic research collector, SGH master's thesis)"
NO_STATUS = "no status in source"


def fetch(url: str) -> bytes:
    return http_get(url, USER_AGENT, timeout_s=300.0)


def _data_lines(text: str) -> list[list[str]]:
    return [line.split() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def parse_kp_file(content: bytes, fetched_at: datetime, source_file: str) -> dict[str, pd.DataFrame]:
    """Parse Kp_ap_Ap_SN_F107_since_1932.txt into long rows for dataset `gfz_kp`."""
    rows = _data_lines(content.decode("ascii"))
    if not rows or any(len(r) != 28 for r in rows):
        bad = next((r for r in rows if len(r) != 28), None)
        raise ValueError(f"{KP_FILE}: expected 28 fields per line, got {bad}")
    a = np.array(rows, dtype=object)
    day = pd.to_datetime(
        pd.DataFrame({"year": a[:, 0].astype(int), "month": a[:, 1].astype(int), "day": a[:, 2].astype(int)}),
        utc=True,
    )
    d = a[:, 27].astype(int)
    kp_status = np.where(d >= 1, "def", "pre")
    kp_basis = np.where(d >= 1, "D>=1 (Kp definitive)", "D=0 (Kp preliminary)")
    sn_status = np.where(d == 2, "def", "pre")
    sn_basis = np.where(d == 2, "D=2 (SN definitive)", "D<2 (SN preliminary)")
    frames = []
    for i in range(8):
        t = day + pd.Timedelta(hours=3 * i)
        for q, col, unit in (("kp", 7 + i, "Kp"), ("ap", 15 + i, "ap")):
            frames.append(
                pd.DataFrame(
                    {
                        "time_utc": t,
                        "quantity": q,
                        "value": mask_fill(pd.Series(a[:, col].astype(float)), -1.0, f"{KP_FILE} {q}"),
                        "unit": unit,
                        "status": kp_status,
                        "status_basis": kp_basis,
                    }
                )
            )
    daily = (
        ("Ap", 23, "Ap", kp_status, kp_basis),
        ("sn", 24, "SN", sn_status, sn_basis),
        ("f107_obs", 25, "sfu", "provisional", NO_STATUS),
        ("f107_adj", 26, "sfu", "provisional", NO_STATUS),
    )
    for q, col, unit, status, basis in daily:
        frames.append(
            pd.DataFrame(
                {
                    "time_utc": day,
                    "quantity": q,
                    "value": mask_fill(pd.Series(a[:, col].astype(float)), -1.0, f"{KP_FILE} {q}"),
                    "unit": unit,
                    "status": status,
                    "status_basis": basis,
                }
            )
        )
    out = pd.concat(frames, ignore_index=True)
    return {"gfz_kp": finish_rows(out, SOURCE, KP_FILE, fetched_at, source_file)}


HPO_VERSION_RE = re.compile(r"Hpo index\.\s*V\.\s*([\d.]+)")


def parse_hp30_file(content: bytes, fetched_at: datetime, source_file: str) -> dict[str, pd.DataFrame]:
    """Parse Hp30_ap30_complete_series.txt into long rows for dataset `gfz_hp30`."""
    text = content.decode("ascii")
    m = HPO_VERSION_RE.search(text)
    if not m:
        raise ValueError(f"{HP30_FILE}: Hpo version not found in header")
    basis = f"Hpo V{m.group(1)}; {NO_STATUS} (D always 0)"
    rows = _data_lines(text)
    if not rows or any(len(r) != 10 for r in rows):
        bad = next((r for r in rows if len(r) != 10), None)
        raise ValueError(f"{HP30_FILE}: expected 10 fields per line, got {bad}")
    a = np.array(rows, dtype=object)
    day = pd.to_datetime(
        pd.DataFrame({"year": a[:, 0].astype(int), "month": a[:, 1].astype(int), "day": a[:, 2].astype(int)}),
        utc=True,
    )
    t = day + pd.to_timedelta(a[:, 3].astype(float), unit="h")
    frames = [
        pd.DataFrame(
            {
                "time_utc": t,
                "quantity": q,
                "value": mask_fill(pd.Series(a[:, col].astype(float)), -1.0, f"{HP30_FILE} {q}"),
                "unit": unit,
                "status": "provisional",
                "status_basis": basis,
            }
        )
        for q, col, unit in (("hp30", 7, "Hp30"), ("ap30", 8, "ap30"))
    ]
    out = pd.concat(frames, ignore_index=True)
    return {"gfz_hp30": finish_rows(out, SOURCE, HP30_FILE, fetched_at, source_file)}


DAILY = {q: pd.Timedelta(days=1) for q in ("Ap", "sn", "f107_obs", "f107_adj")}
FILES = {
    "kp": (KP_FILE, LICENCE_KP, parse_kp_file, "gfz_kp", pd.Timedelta(hours=3)),
    "hp30": (HP30_FILE, LICENCE_HP30, parse_hp30_file, "gfz_hp30", pd.Timedelta(minutes=30)),
}


def run(
    root: Path, which: list[str], fetcher=fetch, base_url: str = BASE_URL, force: bool = False
) -> list[FileResult]:
    raw = RawArchive(root)
    state = NormalizedState(root, SOURCE)
    results = []
    for key in which:
        name, licence, parser, _, _ = FILES[key]
        results.append(
            ingest_file(
                root, raw, state, SOURCE, name, base_url + name, licence, fetcher, parser, force=force
            )
        )
    raw.flush()
    return results


def main(argv: list[str] | None = None) -> int:
    """Entry point `swx-gfz`. Exit code 1 if any download or parse failed."""
    ap = argparse.ArgumentParser(description="Download GFZ Kp (since 1932) and Hp30 (full series) once.")
    ap.add_argument("--only", choices=sorted(FILES), action="append", help="limit to one file (repeatable)")
    ap.add_argument("--force", action="store_true", help="re-normalise even when the file is unchanged")
    ap.add_argument("--data-dir", type=Path, help="override SWX_DATA_DIR")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    root = args.data_dir.resolve() if args.data_dir else data_dir()
    setup_logging(root, "gfz.log", args.verbose)
    which = args.only or list(FILES)
    log.info("GFZ run start, data dir %s (pid %d), files %s", root, os.getpid(), which)
    with StoreLock(root / "raw" / SOURCE / ".lock", stale_after_s=6 * 3600):
        results = run(root, which, force=args.force)
        print_results(results)
        for key in which:
            _, _, _, dataset, step = FILES[key]
            print_coverage(dataset, write_coverage(root, SOURCE, dataset, step, DAILY))
    failed = [r for r in results if not r.ok]
    log.info("GFZ run end: %d files, %d failed", len(results), len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
