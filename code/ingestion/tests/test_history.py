"""Offline tests for the historical GFZ and OMNI2 collectors. Fixtures are short excerpts of the real files
(fetched 2026-10-11); no test touches the network."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from swx_ingest.history import HISTORY_COLUMNS, coverage, history_store
from swx_ingest.sources import gfz, omni
from swx_ingest.store import FetchError, RawArchive, SeriesStore, utc_now

FIX = Path(__file__).parent / "fixtures"
REQUIRED = {"time_utc", "quantity", "value", "unit", "source", "status", "retrieved_at", "source_file"}


class FakeServer:
    def __init__(self, folder: Path) -> None:
        self.files = {p.name: p.read_bytes() for p in folder.iterdir()}
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        name = url.rsplit("/", 1)[-1]
        self.calls.append(name)
        if name not in self.files:
            raise FetchError(f"{url}: HTTP Error 404")
        return self.files[name]


def table(root: Path, dataset: str) -> pd.DataFrame:
    return history_store(root, dataset).read_all()


def kp_at(df: pd.DataFrame, quantity: str, t: str) -> pd.Series:
    hit = df[(df["quantity"] == quantity) & (df["time_utc"] == pd.Timestamp(t, tz="UTC"))]
    assert len(hit) == 1
    return hit.iloc[0]


# --------------------------------------------------------------------------- GFZ


def test_gfz_kp_parsing_times_status_and_fills(tmp_path):
    results = gfz.run(tmp_path, ["kp"], fetcher=FakeServer(FIX / "gfz"), base_url="https://example.invalid/")
    assert all(r.ok for r in results)
    df = table(tmp_path, "gfz_kp")
    assert REQUIRED <= set(df.columns)
    assert str(df["time_utc"].dt.tz) == "UTC"
    # 3-hourly Kp: slot 6 (15:00) of 2026-10-10 is 7.333 (7-), preliminary because D=0
    row = kp_at(df, "kp", "2026-10-10 15:00")
    assert row["value"] == pytest.approx(7.333) and row["status"] == "pre"
    # D=1: Kp definitive, SN still preliminary
    assert kp_at(df, "kp", "2026-09-30 00:00")["status"] == "def"
    assert kp_at(df, "sn", "2026-09-30 00:00")["status"] == "pre"
    # D=2: both definitive
    assert kp_at(df, "sn", "2025-06-30 00:00")["status"] == "def"
    # F10.7 has no status in the source and -1.0 before 1947 is missing data
    f107 = kp_at(df, "f107_obs", "1932-01-01 00:00")
    assert pd.isna(f107["value"]) and f107["status"] == "provisional"
    assert kp_at(df, "Ap", "2026-10-10 00:00")["value"] == 53
    assert set(df["status"]) <= {"pre", "def", "provisional"}


def test_gfz_hp30_records_version_and_missing(tmp_path):
    gfz.run(tmp_path, ["hp30"], fetcher=FakeServer(FIX / "gfz"), base_url="https://example.invalid/")
    df = table(tmp_path, "gfz_hp30")
    assert set(df["quantity"]) == {"hp30", "ap30"}
    assert (df["status"] == "provisional").all()
    assert df["status_basis"].str.startswith("Hpo V3.0").all()
    assert kp_at(df, "hp30", "1985-01-01 00:30")["value"] == pytest.approx(3.333)
    assert pd.isna(kp_at(df, "hp30", "1985-01-01 03:00")["value"])  # -1.000 fill


def test_rerun_unchanged_adds_nothing_and_status_change_is_new_version(tmp_path):
    server = FakeServer(FIX / "gfz")
    gfz.run(tmp_path, ["kp"], fetcher=server, base_url="https://example.invalid/")
    n1 = len(table(tmp_path, "gfz_kp"))
    again = gfz.run(tmp_path, ["kp"], fetcher=server, base_url="https://example.invalid/")
    assert not again[0].changed and again[0].rows_added == 0
    # GFZ finalises 2026-10-01: same values, D flips 0 -> 2
    text = server.files[gfz.KP_FILE].decode()
    old = next(line for line in text.splitlines() if line.startswith("2026 10 01"))
    server.files[gfz.KP_FILE] = text.replace(old, old[:-1] + "2").encode()
    third = gfz.run(tmp_path, ["kp"], fetcher=server, base_url="https://example.invalid/")
    df = table(tmp_path, "gfz_kp")
    assert third[0].rows_added == 8 + 8 + 2  # kp and ap slots, Ap and SN; F10.7 has no status to change
    hist = df[(df["quantity"] == "kp") & (df["time_utc"] == pd.Timestamp("2026-10-01 18:00", tz="UTC"))]
    assert list(hist.sort_values("version")["status"]) == ["pre", "def"]
    assert len(df) == n1 + 18
    assert not df.duplicated(subset=["time_utc", "quantity", "qualifier", "version"]).any()


def test_raw_file_archived_with_hash(tmp_path):
    gfz.run(tmp_path, ["kp"], fetcher=FakeServer(FIX / "gfz"), base_url="https://example.invalid/")
    m = pd.read_parquet(tmp_path / "raw" / "manifest.parquet")
    assert list(m["name"]) == [gfz.KP_FILE]
    assert len(m["sha256"].iloc[0]) == 64
    assert (tmp_path / m["path"].iloc[0]).exists()
    assert (table(tmp_path, "gfz_kp")["source_file"] == m["path"].iloc[0]).all()


def test_failed_fetch_is_reported(tmp_path):
    res = gfz.run(tmp_path, ["kp"], fetcher=FakeServer(FIX / "omni"), base_url="https://example.invalid/")
    assert not res[0].ok and "404" in res[0].detail


# --------------------------------------------------------------------------- OMNI


def run_omni(root: Path, server: FakeServer | None = None, **kw):
    server = server or FakeServer(FIX / "omni")
    return omni.run(
        root,
        range(2026, 2027),
        fetcher=server,
        base_url="https://example.invalid/",
        spans_url="https://example.invalid/ow_data.html",
        pause_s=0,
        **kw,
    )


def test_omni_spans_parsed_into_status_rules():
    rules = omni.status_rules(omni.parse_spans((FIX / "omni" / "ow_data.html").read_bytes()))
    assert str(rules["dst"].def_end) == "2020-12-31"
    assert str(rules["dst"].provisional_end) == "2026-07-31"
    assert str(rules["ae"].def_end) == "1988-06-30"
    assert str(rules["pcn"].def_end) == "2024-12-31"


def test_omni_spans_fail_loudly_when_page_changes():
    with pytest.raises(ValueError):
        omni.status_rules(
            omni.parse_spans(b"<pre>1963-01-01 (001) - 2020-12-31 (366)   Something else</pre>")
        )


def test_omni_rows_times_fills_and_status(tmp_path):
    results = run_omni(tmp_path)
    assert all(r.ok for r in results)
    df = table(tmp_path, omni.DATASET)
    assert REQUIRED <= set(df.columns) and list(df.columns) == HISTORY_COLUMNS
    # day 1 hour 1 = 2026-01-01 01:00 (start of the hour)
    assert kp_at(df, "flow_speed", "2026-01-01 01:00")["value"] == 476
    assert kp_at(df, "dst", "2026-01-01 01:00")["status"] == "provisional"
    # day 213 = 2026-08-01, after the provisional span: quick look
    assert kp_at(df, "dst", "2026-08-01 00:00")["status"] == "realtime"
    assert kp_at(df, "ae", "2026-01-01 00:00")["status"] == "realtime"
    assert kp_at(df, "pcn", "2026-01-01 00:00")["status"] == "provisional"
    assert kp_at(df, "bz_gsm", "2026-01-01 00:00")["status"] == "def"
    # 2026-10-05 13:00: every plasma/IMF word is a fill, but Dst is present (-24)
    assert pd.isna(kp_at(df, "flow_speed", "2026-10-05 13:00")["value"])
    assert pd.isna(kp_at(df, "proton_flux_gt10mev", "2026-10-05 13:00")["value"])
    assert kp_at(df, "dst", "2026-10-05 13:00")["value"] == -24
    # GFZ-sourced indices are deliberately not duplicated from OMNI
    assert not {"kp", "ap", "f107", "sn"} & set(df["quantity"])


def test_omni_drops_hours_after_the_fetch_time():
    rules = omni.status_rules(omni.parse_spans((FIX / "omni" / "ow_data.html").read_bytes()))
    content = (FIX / "omni" / "omni2_2026.dat").read_bytes()
    fetched = pd.Timestamp("2026-08-01 00:00", tz="UTC")  # before the 2026-10-05 13:00 line
    df = omni.parse_year_file(content, fetched, "x", rules, "omni2_2026.dat")
    assert df["time_utc"].max() == fetched
    assert (df["time_utc"] <= fetched).all()


def test_omni_rerun_skips_unchanged_years(tmp_path):
    server = FakeServer(FIX / "omni")
    run_omni(tmp_path, server)
    second = run_omni(tmp_path, server)
    assert [r.changed for r in second] == [False, False]
    assert sum(r.rows_added for r in second) == 0


def test_omni_wrong_word_count_is_a_parse_failure(tmp_path):
    server = FakeServer(FIX / "omni")
    server.files["omni2_2026.dat"] = b"2026   1  0 2623 51\n"
    res = run_omni(tmp_path, server)
    assert not res[1].ok and "parse failed" in res[1].detail


def test_omni_spans_change_renormalises_unchanged_years(tmp_path):
    server = FakeServer(FIX / "omni")
    run_omni(tmp_path, server)
    html = server.files["ow_data.html"].decode()
    old = "2026-07-31 (212)   Provisional Dst"
    assert old in html
    server.files["ow_data.html"] = html.replace(old, "2025-12-31 (365)   Provisional Dst").encode()
    res = run_omni(tmp_path, server)
    assert res[0].changed and not res[1].changed and res[1].rows_added > 0
    df = table(tmp_path, omni.DATASET)
    hist = df[(df["quantity"] == "dst") & (df["time_utc"] == pd.Timestamp("2026-01-01 00:00", tz="UTC"))]
    assert list(hist.sort_values("version")["status"]) == ["provisional", "realtime"]


# --------------------------------------------------------------------------- shared


def test_interrupted_normalisation_is_redone(tmp_path, monkeypatch):
    server = FakeServer(FIX / "gfz")
    gfz.run(tmp_path / "clean", ["kp"], fetcher=server, base_url="https://example.invalid/")
    n_full = len(table(tmp_path / "clean", "gfz_kp"))
    real_add = SeriesStore.add

    def killed_halfway(self, rows):
        real_add(self, rows.iloc[: len(rows) // 2])
        raise KeyboardInterrupt  # the run is stopped during the table writes

    monkeypatch.setattr(SeriesStore, "add", killed_halfway)
    with pytest.raises(KeyboardInterrupt):
        gfz.run(tmp_path / "x", ["kp"], fetcher=server, base_url="https://example.invalid/")
    monkeypatch.setattr(SeriesStore, "add", real_add)
    res = gfz.run(tmp_path / "x", ["kp"], fetcher=server, base_url="https://example.invalid/")
    assert not res[0].changed  # same bytes as the archived copy ...
    assert res[0].rows_added == n_full - n_full // 2  # ... but normalising is finished, not skipped
    assert len(table(tmp_path / "x", "gfz_kp")) == n_full


def test_manifest_keeps_rows_from_concurrent_archives(tmp_path):
    # e.g. the NOAA task runs while a history pull is going: both write raw/manifest.parquet
    noaa, history = RawArchive(tmp_path), RawArchive(tmp_path)
    t = utc_now()
    noaa.save("noaa_swpc", "a.json", "https://example.invalid/a", b"1", t, "PD")
    history.save("omni", "b.dat", "https://example.invalid/b", b"2", t, "PD")
    history.flush()
    noaa.flush()
    history.save("omni", "c.dat", "https://example.invalid/c", b"3", t, "PD")
    history.flush()
    m = pd.read_parquet(tmp_path / "raw" / "manifest.parquet")
    assert sorted(m["name"]) == ["a.json", "b.dat", "c.dat"]
    assert not (tmp_path / "raw" / ".manifest.lock").exists()


def test_coverage_finds_gaps_and_nan():
    t = pd.to_datetime(
        ["2020-01-01 00:00", "2020-01-01 01:00", "2020-01-01 02:00", "2020-01-01 05:00"], utc=True
    )
    df = pd.DataFrame(
        {
            "time_utc": t,
            "quantity": "x",
            "qualifier": "",
            "value": [1.0, float("nan"), 2.0, 3.0],
            "version": 1,
            "status": "def",
        }
    )
    cov, gaps = coverage([df], pd.Timedelta(hours=1))
    row = cov.iloc[0]
    assert row["rows"] == 4 and row["nan_rows"] == 1 and row["gap_runs"] == 2
    assert list(gaps["missing_steps"]) == [1, 2]
    assert gaps["start_utc"].iloc[1] == pd.Timestamp("2020-01-01 03:00", tz="UTC")
