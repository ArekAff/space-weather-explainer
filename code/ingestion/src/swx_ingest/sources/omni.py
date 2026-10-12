"""NASA OMNI2 hourly solar wind, IMF and indices from SPDF yearly files (`omni2_YYYY.dat`, 1963 to now).

Yearly files (2.9 MB each) rather than `omni2_all_years.dat` (184 MB): a re-pull then archives only the years
that changed. Format and fill values: `omni2.text` in the same SPDF directory. Each row is one hour;
`time_utc` = START of the hour (HAPI shows the same values at the HH:30 midpoint).

Quantities go to `normalized/omni2_hourly/`. Kp, sunspot number, ap and F10.7 (words 39, 40, 50, 51) are left out
on purpose: GFZ is their primary source (`gfz_kp`). Fill values (runs of 9s, per word) become NaN.

Status. OMNI2 marks no status per value. The page https://omniweb.gsfc.nasa.gov/html/ow_data.html lists date
spans for final, provisional and quick-look Dst and AE/AL/AU, and for definitive PC(N). It is fetched and archived
on every run, and its spans set the status: final/definitive -> `def`, provisional -> `provisional`, quick look or
after the last span -> `realtime`. IMF, plasma and proton values have no status anywhere, so they are `def` with
`status_basis` saying so; re-pull before the freeze to catch late revisions.

Run: `cd code; uv run swx-omni` (all years) or `--from-year 2025`. Not scheduled.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime
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
from swx_ingest.store import FetchError, RawArchive, StoreLock, data_dir, http_get, utc_now

log = logging.getLogger(__name__)

SOURCE = "omni"
DATASET = "omni2_hourly"
BASE_URL = "https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/"
SPANS_URL = "https://omniweb.gsfc.nasa.gov/html/ow_data.html"
FIRST_YEAR = 1963
LICENCE = (
    "NASA SPDF, public; acknowledge SPDF/OMNIWeb and cite OMNI (King & Papitashvili, doi:10.48322/1shr-ht18). "
    "Dst/AE from WDC Kyoto, PC(N) from DTU"
)
USER_AGENT = "swx_ingest/0.1 (academic research collector, SGH master's thesis)"
N_WORDS = 55
NO_STATUS = "no status in OMNI2; treated as final, re-pull before freeze"


@dataclass(frozen=True)
class Word:
    """One OMNI2 word (1-based position in omni2.text), its fill value and status group."""

    pos: int
    name: str
    unit: str
    fill: float | None
    group: str  # "imf", "plasma", "dst", "ae", "pcn", "protons"


WORDS: tuple[Word, ...] = (
    Word(5, "imf_spacecraft_id", "id", 99, "imf"),
    Word(6, "plasma_spacecraft_id", "id", 99, "plasma"),
    Word(7, "imf_n_points", "count", 999, "imf"),
    Word(8, "plasma_n_points", "count", 999, "plasma"),
    Word(9, "b_mag_avg", "nT", 999.9, "imf"),
    Word(10, "b_vector_mag", "nT", 999.9, "imf"),
    Word(11, "b_lat_gse", "deg", 999.9, "imf"),
    Word(12, "b_lon_gse", "deg", 999.9, "imf"),
    Word(13, "bx_gse", "nT", 999.9, "imf"),
    Word(14, "by_gse", "nT", 999.9, "imf"),
    Word(15, "bz_gse", "nT", 999.9, "imf"),
    Word(16, "by_gsm", "nT", 999.9, "imf"),
    Word(17, "bz_gsm", "nT", 999.9, "imf"),
    Word(18, "sigma_b_mag", "nT", 999.9, "imf"),
    Word(19, "sigma_b_vector", "nT", 999.9, "imf"),
    Word(20, "sigma_bx", "nT", 999.9, "imf"),
    Word(21, "sigma_by", "nT", 999.9, "imf"),
    Word(22, "sigma_bz", "nT", 999.9, "imf"),
    Word(23, "proton_temperature", "K", 9999999.0, "plasma"),
    Word(24, "proton_density", "cm^-3", 999.9, "plasma"),
    Word(25, "flow_speed", "km/s", 9999.0, "plasma"),
    Word(26, "flow_lon", "deg", 999.9, "plasma"),
    Word(27, "flow_lat", "deg", 999.9, "plasma"),
    Word(28, "alpha_proton_ratio", "ratio", 9.999, "plasma"),
    Word(29, "flow_pressure", "nPa", 99.99, "plasma"),
    Word(30, "sigma_temperature", "K", 9999999.0, "plasma"),
    Word(31, "sigma_density", "cm^-3", 999.9, "plasma"),
    Word(32, "sigma_speed", "km/s", 9999.0, "plasma"),
    Word(33, "sigma_flow_lon", "deg", 999.9, "plasma"),
    Word(34, "sigma_flow_lat", "deg", 999.9, "plasma"),
    Word(35, "sigma_alpha_proton_ratio", "ratio", 9.999, "plasma"),
    Word(36, "electric_field", "mV/m", 999.99, "plasma"),
    Word(37, "plasma_beta", "ratio", 999.99, "plasma"),
    Word(38, "alfven_mach", "ratio", 999.9, "plasma"),
    Word(41, "dst", "nT", 99999, "dst"),
    Word(42, "ae", "nT", 9999, "ae"),
    Word(43, "proton_flux_gt1mev", "cm^-2 s^-1 sr^-1", 999999.99, "protons"),
    Word(44, "proton_flux_gt2mev", "cm^-2 s^-1 sr^-1", 99999.99, "protons"),
    Word(45, "proton_flux_gt4mev", "cm^-2 s^-1 sr^-1", 99999.99, "protons"),
    Word(46, "proton_flux_gt10mev", "cm^-2 s^-1 sr^-1", 99999.99, "protons"),
    Word(47, "proton_flux_gt30mev", "cm^-2 s^-1 sr^-1", 99999.99, "protons"),
    Word(48, "proton_flux_gt60mev", "cm^-2 s^-1 sr^-1", 99999.99, "protons"),
    # 0 = no proton data or all contaminated; kept as a value, not a fill (omni2.text note ***).
    Word(49, "proton_contamination_flag", "flag", None, "protons"),
    Word(52, "pcn", "index", 999.9, "pcn"),
    Word(53, "al", "nT", 99999, "ae"),
    Word(54, "au", "nT", 99999, "ae"),
    Word(55, "magnetosonic_mach", "ratio", 99.9, "plasma"),
)


# --------------------------------------------------------------------------- status spans

SPAN_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*\(\s*\d+\)\s*-\s*(\d{4}-\d{2}-\d{2})\s*\(\s*\d+\)\s+([^\n]+)")


@dataclass(frozen=True)
class Span:
    start: date
    end: date
    label: str


def parse_spans(html: bytes) -> list[Span]:
    """Read the "YYYY-MM-DD (DDD) - YYYY-MM-DD (DDD)   Parameters" table from ow_data.html."""
    text = re.sub(r"<[^>]*>", "", html.decode("utf-8", errors="replace")).replace("&nbsp;", " ")
    spans = [
        Span(date.fromisoformat(a), date.fromisoformat(b), label.strip())
        for a, b, label in SPAN_RE.findall(text)
    ]
    if not spans:
        raise ValueError("no time-span table found in ow_data.html")
    return spans


@dataclass(frozen=True)
class StatusRule:
    """Last day of each status for one group; days after `provisional_end` are `realtime`."""

    def_end: date
    provisional_end: date | None
    basis: str


def _find(spans: list[Span], pattern: str) -> Span:
    hits = [s for s in spans if re.search(pattern, s.label, re.IGNORECASE)]
    if len(hits) != 1:
        raise ValueError(f"expected one span matching {pattern!r}, found {[s.label for s in hits]}")
    return hits[0]


def status_rules(spans: list[Span]) -> dict[str, StatusRule]:
    """Status rule per group from the ow_data.html spans. Fails loudly if the page wording changed."""
    dst_final = _find(spans, r"^Dst Final")
    dst_prov = _find(spans, r"^Provisional Dst")
    dst_ql = _find(spans, r"^Quick Look Dst")
    ae_final = _find(spans, r"^AE, AL, ?AU-index$")
    ae_prov = _find(spans, r"^Provisional AE")
    ae_ql = _find(spans, r"^Quick look AE")
    pcn_def = _find(spans, r"^PCN index \(Definitive\)")
    return {
        "dst": StatusRule(
            dst_final.end,
            dst_prov.end,
            f"ow_data.html: final to {dst_final.end}, provisional to {dst_prov.end}, quick look to {dst_ql.end}",
        ),
        # 1988-07 to 1989-12 has no AE in OMNI (only fills); provisional starts 1990.
        "ae": StatusRule(
            ae_final.end,
            ae_prov.end,
            f"ow_data.html: final to {ae_final.end}, provisional to {ae_prov.end}, quick look to {ae_ql.end}",
        ),
        "pcn": StatusRule(
            pcn_def.end, date.max, f"ow_data.html: definitive to {pcn_def.end}, later provisional"
        ),
    }


def assign_status(times: pd.Series, group: str, rules: dict[str, StatusRule]) -> tuple[np.ndarray, str]:
    if group not in rules:
        return np.full(len(times), "def", dtype=object), NO_STATUS
    rule = rules[group]
    day = times.dt.date
    status = np.where(day <= rule.def_end, "def", "realtime").astype(object)
    if rule.provisional_end is not None:
        status[((day > rule.def_end) & (day <= rule.provisional_end)).to_numpy()] = "provisional"
    return status, rule.basis


# --------------------------------------------------------------------------- yearly files


def parse_year_file(
    content: bytes, fetched_at: datetime, source_file: str, rules: dict[str, StatusRule], name: str
) -> pd.DataFrame:
    """Parse one omni2_YYYY.dat into long rows for dataset `omni2_hourly`.

    The current year's file is padded with fill lines up to 31 Dec; hours after `fetched_at` are dropped, so the
    table never holds rows for times that had not happened when it was fetched.
    """
    rows = [line.split() for line in content.decode("ascii").splitlines() if line.strip()]
    bad = next((r for r in rows if len(r) != N_WORDS), None)
    if bad is not None or not rows:
        raise ValueError(f"{name}: expected {N_WORDS} words per line, got {bad}")
    a = np.array(rows, dtype=object)
    year, doy, hour = (a[:, i].astype(int) for i in range(3))
    times = pd.Series(
        pd.to_datetime([f"{y}-01-01" for y in year], utc=True)
        + pd.to_timedelta(doy - 1, unit="D")
        + pd.to_timedelta(hour, unit="h")
    )
    past = (times <= pd.Timestamp(fetched_at)).to_numpy()
    if not past.all():
        log.info("%s: %d hours after the fetch time dropped", name, int((~past).sum()))
        a, times = a[past], times[past].reset_index(drop=True)
    frames = []
    for w in WORDS:
        values = pd.Series(a[:, w.pos - 1].astype(float))
        if w.fill is not None:
            values = mask_fill(values, float(w.fill), f"{name} {w.name}")
        status, basis = assign_status(times, w.group, rules)
        frames.append(
            pd.DataFrame(
                {
                    "time_utc": times,
                    "quantity": w.name,
                    "value": values,
                    "unit": w.unit,
                    "status": status,
                    "status_basis": basis,
                }
            )
        )
    return finish_rows(pd.concat(frames, ignore_index=True), SOURCE, name, fetched_at, source_file)


def fetch(url: str) -> bytes:
    return http_get(url, USER_AGENT, timeout_s=120.0)


def run(
    root: Path,
    years: range,
    fetcher=fetch,
    base_url: str = BASE_URL,
    spans_url: str = SPANS_URL,
    force: bool = False,
    pause_s: float = 1.0,
) -> list[FileResult]:
    """Fetch the status page, then each year file. A year is re-normalised when its bytes or the spans page changed."""
    raw = RawArchive(root)
    state = NormalizedState(root, SOURCE)
    fetched_at = utc_now()
    try:
        page = fetcher(spans_url)
    except FetchError as exc:
        log.error("status page: %s", exc)
        return [FileResult("ow_data.html", ok=False, detail=str(exc))]
    rec = raw.save(SOURCE, "ow_data.html", spans_url, page, fetched_at, LICENCE)
    raw.flush()
    rules = status_rules(parse_spans(page))
    results = [FileResult("ow_data.html", ok=True, changed=rec.changed)]
    for y in years:
        name = f"omni2_{y}.dat"
        results.append(
            ingest_file(
                root,
                raw,
                state,
                SOURCE,
                name,
                base_url + name,
                LICENCE,
                fetcher,
                lambda c, t, p, n=name: {DATASET: parse_year_file(c, t, p, rules, n)},
                rules_key=rec.sha256,
                force=force,
            )
        )
        time.sleep(pause_s)
    raw.flush()
    return results


def main(argv: list[str] | None = None) -> int:
    """Entry point `swx-omni`. Exit code 1 if any download or parse failed."""
    ap = argparse.ArgumentParser(description="Download OMNI2 hourly yearly files once.")
    ap.add_argument("--from-year", type=int, default=FIRST_YEAR)
    ap.add_argument("--to-year", type=int, default=datetime.now(UTC).year)
    ap.add_argument("--force", action="store_true", help="re-normalise even when a file is unchanged")
    ap.add_argument("--data-dir", type=Path, help="override SWX_DATA_DIR")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    root = args.data_dir.resolve() if args.data_dir else data_dir()
    setup_logging(root, "omni.log", args.verbose)
    log.info(
        "OMNI run start, data dir %s (pid %d), years %d-%d", root, os.getpid(), args.from_year, args.to_year
    )
    with StoreLock(root / "raw" / SOURCE / ".lock", stale_after_s=6 * 3600):
        results = run(root, range(args.from_year, args.to_year + 1), force=args.force)
        print_results(results)
        print_coverage(DATASET, write_coverage(root, SOURCE, DATASET, pd.Timedelta(hours=1)))
    failed = [r for r in results if not r.ok]
    log.info("OMNI run end: %d files, %d failed", len(results), len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
