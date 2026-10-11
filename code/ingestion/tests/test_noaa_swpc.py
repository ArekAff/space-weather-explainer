"""Offline tests for the NOAA SWPC live collector. Fixtures in tests/fixtures/noaa_swpc/ copy the SWPC file
shapes with synthetic values; no test touches the network."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from swx_ingest.sources import noaa_swpc as n
from swx_ingest.store import RawArchive

FIX = Path(__file__).parent / "fixtures" / "noaa_swpc"
SHORT = "propagated-solar-wind-1-hour.json"
LONG = "propagated-solar-wind.json"


class FakeServer:
    """Serves fixture files by URL basename; `files` can be overridden per test."""

    def __init__(self) -> None:
        self.files = {p.name: p.read_bytes() for p in FIX.iterdir()}
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        name = url.rsplit("/", 1)[-1]
        self.calls.append(name)
        if name not in self.files:
            raise n.FetchError(f"{url}: HTTP Error 404")
        return self.files[name]


def run(root: Path, server: FakeServer, products=None) -> list[n.Result]:
    return n.Collector(root, base_url="https://example.invalid/", fetcher=server).run(products or n.PRODUCTS)


def table(root: Path, dataset: str) -> pd.DataFrame:
    files = sorted((root / "normalized" / dataset).glob("*.parquet"))
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def by_name(name: str) -> n.Product:
    return next(p for p in n.PRODUCTS if p.name == name)


def test_parse_both_json_shapes():
    lol = n.parse_json_table((FIX / "plasma-2-hour.json").read_bytes())
    lod = n.parse_json_table((FIX / "planetary_k_index_1m.json").read_bytes())
    assert list(lol.columns) == ["time_tag", "density", "speed", "temperature"]
    assert {"time_tag", "estimated_kp"} <= set(lod.columns)


def test_times_are_tz_aware_utc_for_all_tag_formats():
    t = n.parse_time(pd.Series(["2026-10-11 15:00:00.000", "2026-10-11T15:00:00", "2026-10-11T15:00:00Z"]))
    assert str(t.dt.tz) == "UTC"
    assert t.nunique() == 1


def test_first_run_stores_rows_with_contract_columns(tmp_path):
    results = run(tmp_path, FakeServer())
    df = table(tmp_path, "noaa_swpc_solar_wind")
    for col in ["time_utc", "quantity", "value", "unit", "source", "status", "retrieved_at", "source_file"]:
        assert col in df.columns
    assert (df["status"] == "realtime").all()
    assert len(df) == 55  # 5 minutes x (10 values + propagation delay)
    assert df["value"].isna().sum() == 1  # source null kept as NaN
    assert str(df["time_utc"].dt.tz) == "UTC"
    # 7-day files are absent in the fixtures, so first-run backfill attempts are logged as failures
    assert any(r.file == "propagated-solar-wind.json" and not r.ok for r in results)


def test_rerun_with_same_bytes_adds_nothing(tmp_path):
    server = FakeServer()
    run(tmp_path, server)
    before = table(tmp_path, "noaa_swpc_solar_wind")
    manifest_before = len(pd.read_parquet(tmp_path / "raw" / "manifest.parquet"))
    results = run(tmp_path, server)
    after = table(tmp_path, "noaa_swpc_solar_wind")
    assert len(after) == len(before)
    assert len(pd.read_parquet(tmp_path / "raw" / "manifest.parquet")) == manifest_before
    assert all(not r.changed for r in results if r.ok)


def test_overlapping_fetch_dedupes_and_changed_value_is_new_version(tmp_path):
    server = FakeServer()
    run(tmp_path, server, (by_name("solar_wind"),))
    rows = json.loads(server.files[SHORT])
    rows[1][1] = 999.9  # revised speed at minute 0
    rows.append(
        ["2026-10-11T15:05:00Z", 545, 0.8, 66000, 5, -1, 1, 5.3, -543, 10, -38, "2026-10-11T15:47:00Z"]
    )
    server.files[SHORT] = json.dumps(rows).encode()
    run(tmp_path, server, (by_name("solar_wind"),))
    df = table(tmp_path, "noaa_swpc_solar_wind")
    assert not df.duplicated(subset=n.KEY + ["version"]).any()
    assert len(df) == 55 + 1 + 11
    speed0 = df[(df.quantity == "speed") & (df.time_utc == pd.Timestamp("2026-10-11 15:00", tz="UTC"))]
    assert sorted(speed0["version"]) == [1, 2]
    assert sorted(speed0["value"]) == [544.2, 999.9]  # old value kept, never overwritten


def test_short_file_gap_triggers_long_fetch_and_logs_lost_interval(tmp_path):
    server = FakeServer()
    run(tmp_path, server, (by_name("solar_wind"),))
    later = json.loads(server.files[SHORT])[:1] + [
        ["2026-10-20T10:00:00Z", 500, 5, 90000, 1, 1, 1, 2, -500, 0, 0, "2026-10-20T10:45:00Z"]
    ]
    server.files[SHORT] = json.dumps(later).encode()
    server.files[LONG] = json.dumps(later).encode()  # 7-day file no longer reaches back
    server.calls.clear()
    run(tmp_path, server, (by_name("solar_wind"),))
    assert LONG in server.calls
    gaps = pd.read_csv(tmp_path / "raw" / "noaa_swpc" / "gap_log.csv")
    lost = gaps[gaps.kind == "lost_before_coverage"]
    assert len(lost) == 1 and lost.iloc[0]["dataset"] == "noaa_swpc_solar_wind"


def test_spacecraft_and_qualifiers_kept(tmp_path):
    run(tmp_path, FakeServer(), (by_name("rtsw_wind"), by_name("goes_integral_protons")))
    rtsw = table(tmp_path, "noaa_swpc_rtsw_wind")
    assert set(rtsw["spacecraft"]) == {"SOLAR1", "ACE"}
    assert not rtsw.duplicated(subset=n.KEY).any()
    prot = table(tmp_path, "noaa_swpc_goes_integral_protons")
    assert prot["qualifier"].str.contains("energy=>=10 MeV").any()
    assert (prot["unit"] == "pfu").all()


def test_text_product_indexed_by_issue_time_and_saved_once(tmp_path):
    server = FakeServer()
    p = (by_name("forecast_3day"),)
    run(tmp_path, server, p)
    run(tmp_path, server, p)
    idx = pd.read_parquet(tmp_path / "raw" / "noaa_swpc" / "text_index.parquet")
    assert len(idx) == 1
    assert idx.iloc[0]["issued_at"] == pd.Timestamp("2026-10-11 12:30", tz="UTC")


def test_forecasts_are_not_normalised(tmp_path):
    run(tmp_path, FakeServer())
    normalized = {p.name for p in (tmp_path / "normalized").iterdir()}
    assert not any("forecast" in d for d in normalized)


def test_fetch_failure_is_logged_and_run_continues(tmp_path):
    results = run(tmp_path, FakeServer())
    gaps = pd.read_csv(tmp_path / "raw" / "noaa_swpc" / "gap_log.csv")
    assert (gaps.kind == "fetch_failed").any()  # e.g. alerts.json has no fixture
    assert any(r.ok for r in results)


def test_raw_archive_is_gzipped_and_hashed(tmp_path):
    import gzip
    import hashlib

    run(tmp_path, FakeServer(), (by_name("kp_3h"),))
    m = pd.read_parquet(tmp_path / "raw" / "manifest.parquet")
    row = m.iloc[0]
    data = gzip.decompress((tmp_path / row["path"]).read_bytes())
    assert hashlib.sha256(data).hexdigest() == row["sha256"]
    assert data == (FIX / "noaa-planetary-k-index.json").read_bytes()


def test_raw_archive_unchanged_detection(tmp_path):
    a = RawArchive(tmp_path)
    t = n.utc_now()
    assert a.save("s", "f.json", "u", b"x", t, "l").changed
    assert not a.save("s", "f.json", "u", b"x", t, "l").changed
    a.flush()
    assert not RawArchive(tmp_path).save("s", "f.json", "u", b"x", t, "l").changed


@pytest.mark.parametrize(
    "text,expected",
    [
        (":Issued: 2026 Oct 11 0030 UTC\n", "2026-10-11 00:30"),
        (":Issued: 2026 Oct  1 1230 UTC\n", "2026-10-01 12:30"),
    ],
)
def test_parse_issued(text, expected):
    assert n.parse_issued(text) == pd.Timestamp(expected, tz="UTC").to_pydatetime()


def test_rtsw_fill_values_become_nan_and_units_are_known(tmp_path, caplog):
    run(tmp_path, FakeServer(), (by_name("rtsw_wind"), by_name("kp_3h")))
    rtsw = table(tmp_path, "noaa_swpc_rtsw_wind")
    flag = rtsw[rtsw.quantity == "max_data_flag"]
    assert flag["value"].isna().sum() == 2  # the -9999 minute, both spacecraft
    assert (rtsw["value"].dropna() > -9999).all()
    units = dict(zip(rtsw.quantity, rtsw.unit))
    assert units["proton_vx_gsm"] == "km/s" and units["max_data_flag"] == "flag"
    kp = table(tmp_path, "noaa_swpc_kp_3h")
    assert set(kp.unit[kp.quantity == "Kp"]) == {"Kp"}
    assert "no unit known" not in caplog.text


def test_unit_for_patterns():
    assert n.unit_for("alpha_temperature") == "K"
    assert n.unit_for("theta_gse") == "deg"
    assert n.unit_for("bz_gsm") == "nT"
    assert n.unit_for("something_new") is None


def test_propagation_delay_stored_in_minutes(tmp_path):
    run(tmp_path, FakeServer(), (by_name("solar_wind"),))
    df = table(tmp_path, "noaa_swpc_solar_wind")
    delay = df[df.quantity == "propagated_time_tag_delay_min"]
    assert len(delay) == 5 and (delay["value"] == 42.0).all() and (delay["unit"] == "min").all()


def test_hourly_ace_gap_logged_once(tmp_path):
    server = FakeServer()
    run(tmp_path, server, (by_name("ace_swepam_1h"),))
    run(tmp_path, server, (by_name("ace_swepam_1h"),))
    gaps = pd.read_csv(tmp_path / "raw" / "noaa_swpc" / "gap_log.csv")
    no_data = gaps[(gaps.kind == "no_data") & (gaps.dataset == "noaa_swpc_ace_swepam_1h")]
    assert len(no_data) == 1
    df = table(tmp_path, "noaa_swpc_ace_swepam_1h")
    assert set(df.unit[df.quantity == "dens"]) == {"cm^-3"}


def test_long_history_files_are_fetched_at_most_every_6_hours(tmp_path):
    server = FakeServer()
    products = (by_name("rtsw_wind"), by_name("kp_1m"))
    run(tmp_path, server, products)
    server.calls.clear()
    run(tmp_path, server, products)
    assert server.calls == ["planetary_k_index_1m.json"]  # rtsw skipped, kp_1m fetched every run
    state_path = tmp_path / "raw" / "noaa_swpc" / "state.json"
    state = json.loads(state_path.read_text())
    state["fetched_at:rtsw_wind"] = "2026-01-01T00:00:00+00:00"  # pretend the last fetch was long ago
    state_path.write_text(json.dumps(state))
    server.calls.clear()
    run(tmp_path, server, products)
    assert "rtsw_wind_1m.json" in server.calls
