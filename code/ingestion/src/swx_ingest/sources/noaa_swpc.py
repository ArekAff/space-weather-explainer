"""NOAA SWPC live collector.

The live files on services.swpc.noaa.gov keep only 1-7 days, so this collector runs unattended (Windows Task
Scheduler) and archives every response. Each run:

1. fetches every product in `PRODUCTS`; for series that have a 7-day file it fetches the short file, and the 7-day
   file when the short one does not reach back to the last stored minute, when nothing is stored yet, or once a day;
2. archives each response raw (gzipped, SHA-256 in `raw/manifest.parquet`), skipping bytes identical to the last copy;
3. normalises numeric series into `normalized/noaa_swpc_<dataset>/<YYYY-MM>.parquet`, one row per
   (time_utc, quantity, qualifier, version); a later fetch adds a version only when the value changed;
4. indexes text products by their `:Issued:` time in `raw/noaa_swpc/text_index.parquet`;
5. appends failed fetches and intervals without data to `raw/noaa_swpc/gap_log.csv`.

Everything from this collector has `status = realtime` and must never be merged into GFZ/OMNI history tables.
Forecast products (Kp forecast, 3-day forecasts) are answer key / baseline material, so they are archived raw only.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from swx_ingest.store import RawArchive, StoreLock, data_dir, utc_now, write_parquet_atomic

log = logging.getLogger(__name__)

SOURCE = "noaa_swpc"
BASE_URL = "https://services.swpc.noaa.gov/"
LICENCE = "US Government work, public domain (NOAA SWPC)"
USER_AGENT = "swx_ingest/0.1 (academic research collector, SGH master's thesis)"
STATUS = "realtime"
LONG_REFRESH = timedelta(hours=24)

NORMALIZED_COLUMNS = [
    "time_utc",
    "quantity",
    "qualifier",
    "value",
    "unit",
    "version",
    "spacecraft",
    "source",
    "product",
    "status",
    "retrieved_at",
    "source_file",
]
KEY = ["time_utc", "quantity", "qualifier"]
GAP_COLUMNS = ["logged_at", "kind", "dataset", "start_utc", "end_utc", "detail"]

# Units by field name. Exact names first, then name patterns; anything else gets unit "" and a warning.
UNITS = {
    "kp": "Kp",
    "kp_index": "Kp",
    "estimated_kp": "Kp",
    "a_running": "a",
    "station_count": "count",
    "sample_size": "count",
    "flux": "pfu",
    "active": "flag",
    "manual_mode": "flag",
    "overall_quality": "flag",
    "dsflag": "flag",
    "numpts": "count",
    "dens": "cm^-3",
    "range": "setting",
    "scale": "setting",
    "sensitivity": "setting",
}
UNIT_PATTERNS = (
    (re.compile(r"_flag$"), "flag"),
    (re.compile(r"_sample_size$"), "count"),
    (re.compile(r"(speed|_v[xyz]_gs[em])$"), "km/s"),
    (re.compile(r"density$"), "cm^-3"),
    (re.compile(r"temperature$"), "K"),
    (re.compile(r"_delay_min$"), "min"),
    (re.compile(r"^v[xyz]$"), "km/s"),
    (re.compile(r"^((theta|phi|lon|lat)_gs[em]|gs[em]_(lat|lon))$"), "deg"),
    (re.compile(r"^(b[xyzt](_gs[em])?|gs[em]_b[xyz])$"), "nT"),
)
# RTSW marks missing values with -9999 (seen in max_data_flag on 2026-10-11); no real quantity here is that low.
FILL_THRESHOLD = -9999.0


def unit_for(field: str) -> str | None:
    """Unit for a SWPC field name, or None if unknown."""
    key = field.lower()
    if key in UNITS:
        return UNITS[key]
    for pattern, unit in UNIT_PATTERNS:
        if pattern.search(key):
            return unit
    return None


@dataclass(frozen=True)
class Product:
    """One live file. `kind` is "series" (normalised), "raw" (archived only) or "text" (archived and indexed)."""

    name: str
    path: str
    kind: str
    long_path: str | None = None
    cadence_min: int = 1
    qualifiers: tuple[str, ...] = ()
    spacecraft_field: str | None = None
    time_fields: tuple[str, ...] = ()  # extra timestamps, stored as minutes after time_tag

    @property
    def dataset(self) -> str:
        return f"{SOURCE}_{self.name}"


PRODUCTS: tuple[Product, ...] = (
    # products/solar-wind/* (plasma/mag 2-hour and 7-day) returned 404 on 2026-10-11; the propagated file below
    # holds the same plasma and field values for 7 days, plus the estimated arrival time at Earth.
    Product(
        "solar_wind",
        "products/geospace/propagated-solar-wind-1-hour.json",
        "series",
        long_path="products/geospace/propagated-solar-wind.json",
        time_fields=("propagated_time_tag",),
    ),
    Product("ace_swepam_1h", "json/ace/swepam/ace_swepam_1h.json", "series", cadence_min=60),
    Product("ace_mag_1h", "json/ace/mag/ace_mag_1h.json", "series", cadence_min=60),
    Product("rtsw_wind", "json/rtsw/rtsw_wind_1m.json", "series", spacecraft_field="source"),
    Product("rtsw_mag", "json/rtsw/rtsw_mag_1m.json", "series", spacecraft_field="source"),
    Product("kp_1m", "json/planetary_k_index_1m.json", "series"),
    Product("kp_3h", "products/noaa-planetary-k-index.json", "series", cadence_min=180),
    Product(
        "goes_integral_protons",
        "json/goes/primary/integral-protons-1-day.json",
        "series",
        long_path="json/goes/primary/integral-protons-7-day.json",
        cadence_min=5,
        qualifiers=("satellite", "energy"),
    ),
    Product("kp_forecast", "products/noaa-planetary-k-index-forecast.json", "raw"),
    Product("alerts", "products/alerts.json", "raw"),
    Product("scales", "products/noaa-scales.json", "raw"),
    Product("forecast_3day", "text/3-day-forecast.txt", "text"),
    Product("geomag_forecast_3day", "text/3-day-geomag-forecast.txt", "text"),
    Product("discussion", "text/discussion.txt", "text"),
)


# --------------------------------------------------------------------------- fetching


class FetchError(RuntimeError):
    pass


def fetch(url: str, attempts: int = 3, timeout_s: float = 60.0) -> bytes:
    """GET with a descriptive User-Agent and capped exponential back-off (5 s, 10 s, ... max 30 s)."""
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and 400 <= exc.code < 500:
                break  # a 404 will not fix itself
            if i < attempts - 1:
                time.sleep(min(30.0, 5.0 * 2**i))
    raise FetchError(f"{url}: {last}")


# --------------------------------------------------------------------------- parsing


def parse_json_table(content: bytes) -> pd.DataFrame:
    """Parse a SWPC JSON product into a DataFrame of strings/numbers.

    Handles both shapes SWPC uses: a list of lists whose first row is the header, and a list of objects.
    """
    data = json.loads(content)
    if not isinstance(data, list):
        raise TypeError(f"expected a JSON list, got {type(data).__name__}")
    if not data:
        return pd.DataFrame()
    if isinstance(data[0], list):
        header, rows = data[0], data[1:]
        return pd.DataFrame(rows, columns=header)
    if isinstance(data[0], dict):
        return pd.DataFrame(data)
    raise ValueError("unrecognised JSON table shape")


def parse_time(series: pd.Series) -> pd.Series:
    """SWPC time tags are UTC with or without a trailing Z ("2026-10-11 17:00:00.000", "2026-10-11T17:00:00Z")."""
    return pd.to_datetime(
        series.astype(str).str.replace("T", " ").str.rstrip("Z"), utc=True, format="mixed", errors="coerce"
    )


def _numeric(col: pd.Series) -> pd.Series | None:
    """Return the column as float if every non-null value is numeric (bools become 0/1), else None."""
    present = col.dropna()
    if present.empty:
        return pd.to_numeric(col, errors="coerce").astype(float)
    if present.map(lambda v: isinstance(v, bool)).all():
        return col.map(lambda v: float(v) if isinstance(v, bool) else math.nan)
    conv = pd.to_numeric(col, errors="coerce")
    if conv[present.index].isna().any():
        return None
    return conv.astype(float)


def normalize(
    table: pd.DataFrame, product: Product, retrieved_at: datetime, source_file: str
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Turn a parsed product table into long rows with provenance. Returns (rows, null counts per quantity).

    Source nulls become NaN rows, so "served but empty" stays distinguishable from "never fetched".
    """
    if table.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS), {}
    if "time_tag" not in table.columns:
        raise ValueError(f"{product.name}: no time_tag column in {list(table.columns)}")
    times = parse_time(table["time_tag"])
    meta = {"time_tag", *product.qualifiers}
    if product.spacecraft_field:
        meta.add(product.spacecraft_field)
    spacecraft = (
        table[product.spacecraft_field].astype("string")
        if product.spacecraft_field and product.spacecraft_field in table.columns
        else pd.Series(pd.NA, index=table.index, dtype="string")
    )
    qual_parts = ["spacecraft=" + spacecraft.fillna("")] if product.spacecraft_field else []
    for q in product.qualifiers:
        if q in table.columns:
            qual_parts.append(f"{q}=" + table[q].astype(str))
    qualifier = (
        pd.concat(qual_parts, axis=1).agg(";".join, axis=1)
        if qual_parts
        else pd.Series("", index=table.index)
    )
    frames, nulls = [], {}
    table = table.copy()
    for col in product.time_fields:
        if col in table.columns:
            later = parse_time(table[col])
            table[f"{col}_delay_min"] = (later - times).dt.total_seconds() / 60.0
            meta.add(col)
    for col in table.columns:
        if col in meta:
            continue
        values = _numeric(table[col])
        if values is None:
            log.debug("%s: skipping non-numeric field %s", product.name, col)
            continue
        unit = unit_for(col)
        if unit is None:
            log.warning("%s: no unit known for field %s", product.name, col)
        fills = values <= FILL_THRESHOLD
        if fills.any():
            log.info(
                "%s: %d fill values (<= %s) in %s set to NaN", product.name, fills.sum(), FILL_THRESHOLD, col
            )
            values = values.mask(fills)
        nulls[col] = int(values.isna().sum())
        frames.append(
            pd.DataFrame(
                {
                    "time_utc": times,
                    "quantity": col,
                    "qualifier": qualifier,
                    "value": values,
                    "unit": unit or "",
                    "spacecraft": spacecraft,
                }
            )
        )
    if not frames:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS), nulls
    out = pd.concat(frames, ignore_index=True)
    out = out.dropna(subset=["time_utc"]).drop_duplicates(subset=KEY, keep="last")
    out["version"] = 0
    out["source"] = SOURCE
    out["product"] = product.name
    out["status"] = STATUS
    out["retrieved_at"] = pd.Timestamp(retrieved_at)
    out["source_file"] = source_file
    return out[NORMALIZED_COLUMNS], nulls


ISSUED_RE = re.compile(r":Issued:\s*(\d{4}\s+\w{3}\s+\d{1,2}\s+\d{4})\s*UTC")


def parse_issued(text: str) -> datetime | None:
    """Parse ':Issued: 2026 Oct 11 1230 UTC' into a UTC datetime (minute precision)."""
    m = ISSUED_RE.search(text)
    if not m:
        return None
    return datetime.strptime(" ".join(m.group(1).split()), "%Y %b %d %H%M").replace(tzinfo=UTC)


# --------------------------------------------------------------------------- normalised store


def _same(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a == b) | (a.isna() & b.isna())


def merge_versions(existing: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Return only the rows of `new` that are new keys or changed values, with their version numbers set.

    Existing rows are never modified: a changed value is a new version (latest + 1).
    """
    if new.empty:
        return new
    if existing.empty:
        return new.assign(version=1)
    latest = existing.sort_values("version").groupby(KEY, as_index=False).tail(1)
    latest = latest[KEY + ["value", "unit", "version"]].rename(
        columns={"value": "_old_value", "unit": "_old_unit", "version": "_old_version"}
    )
    m = new.drop(columns="version").merge(latest, on=KEY, how="left")
    is_new = m["_old_version"].isna()
    changed = ~is_new & ~(_same(m["value"], m["_old_value"]) & (m["unit"] == m["_old_unit"]))
    m = m[is_new | changed].copy()
    m["version"] = m["_old_version"].fillna(0).astype(int) + 1
    return m[NORMALIZED_COLUMNS]


class SeriesStore:
    """Monthly Parquet files per dataset under `normalized/<dataset>/<YYYY-MM>.parquet`."""

    def __init__(self, root: Path, dataset: str) -> None:
        self.dir = root / "normalized" / dataset

    def _path(self, month: str) -> Path:
        return self.dir / f"{month}.parquet"

    def read_month(self, month: str) -> pd.DataFrame:
        p = self._path(month)
        return pd.read_parquet(p) if p.exists() else pd.DataFrame(columns=NORMALIZED_COLUMNS)

    def months(self) -> list[str]:
        return sorted(p.stem for p in self.dir.glob("*.parquet")) if self.dir.exists() else []

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
            add = merge_versions(existing, part)
            if add.empty:
                continue
            out = pd.concat([f for f in (existing, add) if len(f)], ignore_index=True)
            out = out.sort_values(KEY + ["version"], ignore_index=True)
            write_parquet_atomic(out, self._path(month))
            written += len(add)
        return written


# --------------------------------------------------------------------------- gap log


class GapLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        if path.exists():
            self.df = pd.read_csv(path, dtype=str, keep_default_na=False)
        else:
            self.df = pd.DataFrame(columns=GAP_COLUMNS)
        self._seen = set(zip(self.df["kind"], self.df["dataset"], self.df["start_utc"], self.df["end_utc"]))
        self._new: list[dict] = []

    def add(self, kind: str, dataset: str, start: str = "", end: str = "", detail: str = "") -> None:
        key = (kind, dataset, start, end)
        if kind in ("no_data", "lost_before_coverage") and key in self._seen:
            return
        self._seen.add(key)
        self._new.append(
            {
                "logged_at": utc_now().isoformat(timespec="seconds"),
                "kind": kind,
                "dataset": dataset,
                "start_utc": start,
                "end_utc": end,
                "detail": detail,
            }
        )
        log.warning("gap log: %s %s %s %s %s", kind, dataset, start, end, detail)

    def flush(self) -> None:
        if not self._new:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        new = pd.DataFrame(self._new, columns=GAP_COLUMNS)
        new.to_csv(self.path, mode="a", header=not self.path.exists(), index=False)
        self._new = []


def _iso(t: pd.Timestamp) -> str:
    return pd.Timestamp(t).isoformat()


def find_gaps(times: pd.Series, cadence_min: int) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Intervals where consecutive stored times are further apart than 3 cadences (at least 5 min)."""
    if len(times) < 2:
        return []
    t = pd.Series(sorted(times)).reset_index(drop=True)
    limit = pd.Timedelta(minutes=max(5, 3 * cadence_min))
    d = t.diff()
    idx = d[d > limit].index
    return [(t[i - 1], t[i]) for i in idx]


# --------------------------------------------------------------------------- run


@dataclass
class Result:
    product: str
    file: str
    ok: bool
    changed: bool = False
    rows_added: int = 0
    detail: str = ""


class Collector:
    def __init__(self, root: Path, base_url: str = BASE_URL, fetcher=fetch) -> None:
        self.root = root
        self.base_url = base_url
        self.fetcher = fetcher
        self.raw = RawArchive(root)
        self.gaps = GapLog(root / "raw" / SOURCE / "gap_log.csv")
        self.state_path = root / "raw" / SOURCE / "state.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.text_index_path = root / "raw" / SOURCE / "text_index.parquet"
        self.results: list[Result] = []

    def _get(self, product: Product, path: str) -> tuple[bytes, datetime, str] | None:
        url = self.base_url + path
        fetched_at = utc_now()
        file = path.rsplit("/", 1)[-1]
        try:
            content = self.fetcher(url)
        except FetchError as exc:
            self.gaps.add(
                "fetch_failed", product.dataset, fetched_at.isoformat(timespec="seconds"), "", str(exc)
            )
            self.results.append(Result(product.name, file, ok=False, detail=str(exc)))
            return None
        return content, fetched_at, url

    def _archive(self, product: Product, path: str) -> tuple[bytes, datetime, str | None] | None:
        got = self._get(product, path)
        if got is None:
            return None
        content, fetched_at, url = got
        file = path.rsplit("/", 1)[-1]
        rec = self.raw.save(SOURCE, file, url, content, fetched_at, LICENCE)
        self.results.append(Result(product.name, file, ok=True, changed=rec.changed))
        return content, fetched_at, rec.path

    def _ingest_series(self, product: Product, path: str, store: SeriesStore) -> pd.DataFrame | None:
        got = self._archive(product, path)
        if got is None:
            return None
        content, fetched_at, raw_path = got
        try:
            table = parse_json_table(content)
            rows, nulls = normalize(table, product, fetched_at, raw_path or "")
        except (ValueError, TypeError, KeyError) as exc:
            self.gaps.add(
                "parse_failed",
                product.dataset,
                fetched_at.isoformat(timespec="seconds"),
                "",
                f"{path}: {exc}",
            )
            self.results[-1].ok = False
            self.results[-1].detail = f"parse failed: {exc}"
            return None
        if raw_path is None:
            return rows  # identical bytes: nothing new to store, but the coverage still counts
        n_null = sum(nulls.values())
        if n_null:
            log.info("%s: %d null values from source stored as NaN (%s)", path, n_null, nulls)
        self.results[-1].rows_added = store.add(rows)
        return rows

    def run_series(self, product: Product) -> None:
        store = SeriesStore(self.root, product.dataset)
        last_before = store.last_time()
        short = self._ingest_series(product, product.path, store)
        coverage = short
        if product.long_path:
            long_key = f"long_fetched_at:{product.name}"
            last_long = self.state.get(long_key)
            reason = None
            if last_before is None:
                reason = "nothing stored yet"
            elif short is None or short.empty:
                reason = "short file unavailable"
            elif short["time_utc"].min() > last_before + pd.Timedelta(minutes=product.cadence_min):
                reason = "short file does not reach back to the last stored time"
            elif last_long is None or utc_now() - datetime.fromisoformat(last_long) > LONG_REFRESH:
                reason = "daily refresh"
            if reason:
                log.info("%s: fetching %s (%s)", product.name, product.long_path, reason)
                long = self._ingest_series(product, product.long_path, store)
                if long is not None:
                    self.state[long_key] = utc_now().isoformat(timespec="seconds")
                    coverage = long
        self._check_gaps(product, store, last_before, coverage)

    def _check_gaps(
        self,
        product: Product,
        store: SeriesStore,
        last_before: pd.Timestamp | None,
        coverage: pd.DataFrame | None,
    ) -> None:
        if coverage is None or coverage.empty:
            return
        first = coverage["time_utc"].min()
        step = pd.Timedelta(minutes=max(5, 3 * product.cadence_min))
        if last_before is not None and first - last_before > step:
            self.gaps.add(
                "lost_before_coverage",
                product.dataset,
                _iso(last_before),
                _iso(first),
                "collector was off longer than the live file keeps data",
            )
        for a, b in find_gaps(store.times_since(first), product.cadence_min):
            self.gaps.add("no_data", product.dataset, _iso(a), _iso(b), "no rows in source for this interval")

    def run_text(self, product: Product) -> None:
        got = self._archive(product, product.path)
        if got is None or got[2] is None:
            return
        content, fetched_at, raw_path = got
        issued = parse_issued(content.decode("utf-8", errors="replace"))
        if issued is None:
            log.warning("%s: no ':Issued:' line found", product.path)
        row = pd.DataFrame(
            [
                {
                    "product": product.name,
                    "issued_at": pd.Timestamp(issued) if issued else pd.NaT,
                    "issued_precision": "minute" if issued else "",
                    "fetched_at": pd.Timestamp(fetched_at),
                    "sha256": self.raw.last_sha256(SOURCE, product.path.rsplit("/", 1)[-1]),
                    "path": raw_path,
                }
            ]
        )
        old = pd.read_parquet(self.text_index_path) if self.text_index_path.exists() else None
        out = pd.concat([old, row], ignore_index=True) if old is not None and len(old) else row
        out["issued_at"] = pd.to_datetime(out["issued_at"], utc=True)
        write_parquet_atomic(out, self.text_index_path)

    def run(self, products: tuple[Product, ...] = PRODUCTS) -> list[Result]:
        for product in products:
            if product.kind == "series":
                self.run_series(product)
            elif product.kind == "text":
                self.run_text(product)
            else:
                self._archive(product, product.path)
        self.raw.flush()
        self.gaps.flush()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, indent=2))
        return self.results


def _setup_logging(root: Path, verbose: bool) -> None:
    (root / "logs").mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.FileHandler(root / "logs" / "noaa_live.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ]
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fmt.converter = time.gmtime  # log times in UTC
    for h in handlers:
        h.setFormatter(fmt)
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, handlers=handlers, force=True)


def main(argv: list[str] | None = None) -> int:
    """Entry point `swx-noaa-live`: one collection run. Exit code 1 if any fetch or parse failed."""
    ap = argparse.ArgumentParser(description="Fetch and archive NOAA SWPC live products once.")
    ap.add_argument("--data-dir", type=Path, help="override MAGISTERKA_DATA_DIR")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    root = args.data_dir.resolve() if args.data_dir else data_dir()
    _setup_logging(root, args.verbose)
    log.info("NOAA SWPC run start, data dir %s (pid %d)", root, os.getpid())
    with StoreLock(root / "raw" / SOURCE / ".lock"):
        results = Collector(root).run()
    print(f"{'product':24} {'file':40} {'ok':3} {'changed':7} rows_added")
    for r in results:
        print(
            f"{r.product:24} {r.file:40} {'y' if r.ok else 'N':3} {'y' if r.changed else '-':7} "
            f"{r.rows_added} {r.detail}"
        )
    failed = [r for r in results if not r.ok]
    log.info("NOAA SWPC run end: %d files, %d failed", len(results), len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
