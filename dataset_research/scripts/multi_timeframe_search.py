"""
Multi-timeframe similarity search ("time-series RAG") – prototype for the thesis platform.

Idea taken from github.com/bitsofchris/time-series-AI (MIT): cut a series into windows, turn every window
into a vector, store the vectors with metadata and retrieve nearest neighbours. Extended here with the three
things the platform needs and that the reference repo only lists on its roadmap:

  1. MULTI-TIMEFRAME: the same series is re-sampled into several bar sizes (e.g. 15 min -> 1 h -> 1 day -> 1 week).
     Every bar keeps 4 aggregates [mean, min, max, last] (the physical analogue of OHLC candles), and every
     window has the same number of bars, so a pattern can be matched at another time scale.
  2. "WHAT HAPPENED AFTER": for each match we return the next H bars, plus simple statistics over all matches
     (analogue forecasting / outcome analysis).
  3. GROUNDING HOOK: every match carries (entity, timeframe, start, end), so it can be joined with an event
     catalogue (eclipses, storms, floods, holidays, curtailment days...) to explain it.

Two normalisations:
  * "shape": z-score inside each window, so the search is scale-free. This is what makes cross-timeframe and
    cross-entity matching meaningful.
  * "level": one global z-score per entity and timeframe, so magnitude matters (e.g. storm strength). The
    reference repo normalises globally, which effectively makes it a level search.

Backends: exact NumPy search (default) or LanceDB (same vector DB as the reference repo) via `to_lancedb()`.

Run all demos:   python scripts/multi_timeframe_search.py
Needs:           pip install pandas numpy matplotlib wfdb   (lancedb optional)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

AGG = ["mean", "min", "max", "last"]
ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples"
OUT = ROOT / "multi_timeframe_similarity"


# ----------------------------------------------------------------------------- engine
def to_bars(s: pd.Series, rule: str) -> pd.DataFrame:
    """Resample a regular series into bars with [mean, min, max, last]. Empty bars stay NaN (gaps are kept)."""
    r = s.resample(rule, label="left", closed="left")
    return pd.DataFrame({"mean": r.mean(), "min": r.min(), "max": r.max(), "last": r.last()})


@dataclass
class MultiTimeframeIndex:
    window_bars: int = 32
    mode: str = "shape"                       # "shape" or "level"
    vectors: list = field(default_factory=list)
    meta: list = field(default_factory=list)
    bars: dict = field(default_factory=dict)  # (entity, timeframe) -> bar DataFrame (for outcomes / plots)

    def add(self, entity: str, series: pd.Series, timeframes: dict[str, int]):
        """timeframes: {pandas rule: stride in bars}, e.g. {"1h": 4, "1D": 1}."""
        for rule, stride in timeframes.items():
            b = to_bars(series.dropna(), rule)
            self.bars[(entity, rule)] = b
            X = b[AGG].to_numpy(float)
            if self.mode == "level":
                mu, sd = np.nanmean(X), np.nanstd(X) or 1.0
                X = (X - mu) / sd
            n = self.window_bars
            for i in range(0, len(X) - n + 1, stride):
                w = X[i:i + n]
                if np.isnan(w).any():
                    continue
                raw_sd = float(b[AGG].to_numpy(float)[i:i + n].std())   # amplitude in original units
                if self.mode == "shape":
                    sd = w.std()
                    if sd == 0:
                        continue
                    w = (w - w.mean()) / sd
                self.vectors.append(w.astype(np.float32).ravel())
                self.meta.append((entity, rule, b.index[i], b.index[i + n - 1], i, raw_sd))
        return self

    def finalize(self):
        self.V = np.vstack(self.vectors)
        self.M = pd.DataFrame(self.meta, columns=["entity", "timeframe", "start", "end", "bar_pos", "raw_sd"])
        self.M["end_excl"] = [self.bars[(e, tf)].index[p + self.window_bars - 1] + pd.tseries.frequencies.to_offset(tf)
                              for e, tf, p in zip(self.M.entity, self.M.timeframe, self.M.bar_pos)]
        return self

    def query_vector(self, entity, timeframe, start):
        m = self.M[(self.M.entity == entity) & (self.M.timeframe == timeframe)]
        j = (m.start - pd.Timestamp(start)).abs().idxmin()
        return j, self.V[j]

    def search(self, qid: int, k=10, timeframes=None, entities=None, exclude_overlap=True, min_amplitude_ratio=None):
        """Nearest windows to window `qid`. Overlapping windows of the same entity are excluded, and
        non-maximum suppression keeps one hit per (entity, timeframe, region).
        min_amplitude_ratio: in shape mode, drop windows whose raw amplitude is below this fraction of the
        query's amplitude, so a 3-cm wiggle cannot match a 3-m flood rise ("amplitude-aware shape search")."""
        d = np.sqrt(((self.V - self.V[qid]) ** 2).mean(axis=1))
        res = self.M.assign(distance=d)
        if min_amplitude_ratio:
            res = res[res.raw_sd >= min_amplitude_ratio * self.M.loc[qid, "raw_sd"]]
        if timeframes:
            res = res[res.timeframe.isin(timeframes)]
        if entities:
            res = res[res.entity.isin(entities)]
        q = self.M.loc[qid]
        if exclude_overlap:
            same = res.entity == q.entity
            overlap = (res.start < q.end_excl) & (res.end_excl > q.start)
            res = res[~(same & overlap)]
        res = res.sort_values("distance")
        kept = []
        for idx, r in res.iterrows():
            if any(r.entity == o.entity and r.timeframe == o.timeframe and r.start < o.end_excl and r.end_excl > o.start
                   for o in kept):
                continue
            kept.append(r)
            if len(kept) == k:
                break
        return pd.DataFrame(kept)

    def window_values(self, entity, timeframe, pos, n_after=0, col="mean"):
        b = self.bars[(entity, timeframe)]
        return b[col].iloc[pos:pos + self.window_bars + n_after].to_numpy(float)

    def to_lancedb(self, uri: str, table="windows"):
        """Store the index in LanceDB (the vector DB used by the reference repo)."""
        import lancedb
        db = lancedb.connect(uri)
        df = self.M[["entity", "timeframe", "start", "end", "bar_pos"]].copy()
        df["vector"] = list(self.V)
        return db.create_table(table, data=df, mode="overwrite")


def outcome_stats(idx: MultiTimeframeIndex, hits: pd.DataFrame, horizon: int, col="max"):
    """'What happened after': for each hit, the next `horizon` bars, expressed relative to the window
    (z-scored with the window's own mean/sd), so different scales/entities are comparable."""
    rows, paths = [], []
    for _, h in hits.iterrows():
        v = idx.window_values(h.entity, h.timeframe, h.bar_pos, horizon, col)
        w, after = v[:idx.window_bars], v[idx.window_bars:]
        sd = np.nanstd(w) or 1.0
        rel = (after - np.nanmean(w)) / sd
        paths.append(rel)
        rows.append({"entity": h.entity, "timeframe": h.timeframe, "start": h.start, "end": h.end,
                     "distance": round(h.distance, 3), "next_peak_raw": np.nanmax(after) if len(after) else np.nan,
                     "next_peak_in_window_sd": np.nanmax(rel) if len(rel) else np.nan})
    return pd.DataFrame(rows), paths


# ----------------------------------------------------------------------------- plotting
def plot_query_and_hits(idx, qid, hits, horizon, title, path, col="mean", n=6, ylab=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    q = idx.M.loc[qid]
    fig, axes = plt.subplots(1 + min(n, len(hits)), 1, figsize=(8, 1.35 * (1 + min(n, len(hits))) + 0.6), sharex=False)
    rows = [(q, "#0b0b0b", "QUERY")] + [(h, "#2a78d6", f"#{i+1}") for i, (_, h) in enumerate(hits.head(n).iterrows())]
    for ax, (r, c, lab) in zip(axes, rows):
        v = idx.window_values(r.entity, r.timeframe, r.bar_pos, horizon, col)
        x = np.arange(len(v))
        ax.plot(x[:idx.window_bars], v[:idx.window_bars], color=c, lw=1.6)
        ax.plot(x[idx.window_bars - 1:], v[idx.window_bars - 1:], color="#eb6834", lw=1.2, ls="--")
        ax.axvline(idx.window_bars - 0.5, color="#c3c2b7", lw=0.8)
        dist = "" if lab == "QUERY" else f"  d={r.distance:.2f}"
        fmt = "%H:%M:%S.%f" if pd.Timedelta(r.timeframe) < pd.Timedelta("1min") else "%Y-%m-%d %H:%M"
        t0, t1 = pd.Timestamp(r.start).strftime(fmt), pd.Timestamp(r.end).strftime(fmt)
        if fmt.startswith("%H"):
            t0, t1 = t0[:-3], t1[:-3]
        ax.set_title(f"{lab}  {r.entity} | bars={r.timeframe} | {t0} → {t1}{dist}",
                     fontsize=7.5, loc="left", color="#0b0b0b")
        ax.tick_params(labelsize=6.5)
        ax.grid(color="#e6e5e0", lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].text(1.0, 1.25, "solid = matched window, dashed orange = what happened after", transform=axes[0].transAxes,
                 ha="right", fontsize=7, color="#52514e")
    axes[-1].set_xlabel("bar index (window, then continuation)", fontsize=7)
    fig.suptitle(title, fontsize=9.5, fontweight="bold", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- demos
def demo_space_weather():
    """Storm analogues: query = the 2 days up to Gannon storm onset; outcome = max Kp in the next 24 h."""
    sw = pd.read_csv(SAMPLES / "02_space_weather/celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv", parse_dates=["date"])
    kc = [c for c in sw.columns if c.startswith("kp_") and c.endswith("UT")]
    long = sw.melt(id_vars="date", value_vars=kc, var_name="slot", value_name="kp")
    long["t"] = long.date + pd.to_timedelta(long.slot.str[3:5].astype(int), unit="h")
    kp = long.set_index("t").kp.sort_index()
    idx = MultiTimeframeIndex(window_bars=16, mode="level").add("Kp", kp, {"3h": 2, "1D": 1, "3D": 1}).finalize()
    qid, _ = idx.query_vector("Kp", "3h", "2024-05-09 00:00")   # 16 bars = 48 h ending 10 May 21:00
    hits = idx.search(qid, k=10, timeframes=["3h"])
    stats, _ = outcome_stats(idx, hits, horizon=8, col="max")
    stats["window_max_kp"] = [idx.window_values(h.entity, h.timeframe, h.bar_pos, 0, "max").max() for _, h in hits.iterrows()]
    actual = idx.window_values("Kp", "3h", idx.M.loc[qid].bar_pos, 8, "max")[16:].max()
    stats.to_csv(OUT / "space_weather_analogues.csv", index=False)
    plot_query_and_hits(idx, qid, hits, 8, "Space weather: analogues of the Gannon-storm onset (3-h Kp bars, level mode)",
                        OUT / "space_weather_analogues.png", col="max")
    # cross-timeframe, shape mode: does the same shape exist at daily / 3-day scale?
    idx2 = MultiTimeframeIndex(window_bars=16, mode="shape").add("Kp", kp, {"3h": 2, "1D": 1, "3D": 1}).finalize()
    q2, _ = idx2.query_vector("Kp", "3h", "2024-05-09 00:00")
    cross = idx2.search(q2, k=6, timeframes=["1D", "3D"], min_amplitude_ratio=0.5)
    cross.drop(columns=["bar_pos"]).to_csv(OUT / "space_weather_cross_timeframe.csv", index=False)
    plot_query_and_hits(idx2, q2, cross, 4, "Space weather: same shape at daily / 3-day scale (shape mode)",
                        OUT / "space_weather_cross_timeframe.png", col="max")
    return {"windows_indexed": len(idx.M), "hits_with_storm_in_window_(Kp>=7)": int((stats.window_max_kp >= 7).sum()),
            "hits": len(stats), "median_next24h_maxKp_of_analogues": float(stats.next_peak_raw.median()),
            "actual_next24h_maxKp": float(actual)}


def demo_nyc_taxi():
    """Demand anomalies: query = blizzard day; check which hits fall on NAB-labelled or holiday windows."""
    import json
    s = pd.read_csv(SAMPLES / "04_nab_known_causes/nyc_taxi.csv", parse_dates=["timestamp"]).set_index("timestamp").value
    labels = json.load(open(SAMPLES / "04_nab_known_causes/nab_anomaly_windows_realKnownCause.json"))["realKnownCause/nyc_taxi.csv"]
    # NAB windows + US federal holidays in the period (Independence Day, Labor Day, Columbus Day, Veterans Day,
    # Thanksgiving, Christmas, New Year, Martin Luther King Jr. Day), each as the calendar day.
    fed = ["2014-07-04", "2014-09-01", "2014-10-13", "2014-11-11", "2014-11-27", "2014-12-25", "2015-01-01", "2015-01-19"]
    labels = [(pd.Timestamp(a), pd.Timestamp(b)) for a, b in labels] + [(pd.Timestamp(d), pd.Timestamp(d) + pd.Timedelta("1D")) for d in fed]
    idx = MultiTimeframeIndex(window_bars=48, mode="shape").add("NYC taxi", s, {"30min": 4, "2h": 2}).finalize()
    qid, _ = idx.query_vector("NYC taxi", "30min", "2015-01-26 06:00")
    hits = idx.search(qid, k=10)
    hits["on_labelled_or_holiday"] = [any(h.start < b and h.end_excl > a for a, b in labels) for _, h in hits.iterrows()]
    hits.drop(columns=["bar_pos"]).to_csv(OUT / "nyc_taxi_blizzard_matches.csv", index=False)
    plot_query_and_hits(idx, qid, hits, 12, "NYC taxi: windows most similar to the blizzard day (30-min and 2-h bars, shape mode)",
                        OUT / "nyc_taxi_blizzard_matches.png")
    return {"windows_indexed": len(idx.M), "hits_on_labelled_or_holiday": int(hits.on_labelled_or_holiday.sum()), "hits": len(hits)}


def demo_hydro():
    """Flood analogues across gauges: query = Kłodzko rising limb; outcome = what the river did next."""
    h = pd.read_csv(SAMPLES / "09_hydrology_pl/imgw_hydro_daily_HY2024_odra_nysa_flood.csv", parse_dates=["date"]).set_index("date")
    idx = MultiTimeframeIndex(window_bars=6, mode="shape")
    for g in ["klodzko", "nysa", "glucholazy", "opole_groszowice", "raciborz_miedonia", "brzeg_dolny"]:
        idx.add(g, h[f"{g}_level_cm"].asfreq("1D"), {"1D": 1})
    idx.finalize()
    qid, _ = idx.query_vector("klodzko", "1D", "2024-09-09")     # 9..14 Sep: the rise begins
    hits = idx.search(qid, k=8, min_amplitude_ratio=0.25)
    stats, _ = outcome_stats(idx, hits, horizon=6, col="max")
    stats.to_csv(OUT / "hydro_flood_analogues.csv", index=False)
    plot_query_and_hits(idx, qid, hits, 6, "IMGW gauges: analogues of the Kłodzko rise (daily bars, shape mode, all gauges)",
                        OUT / "hydro_flood_analogues.png")
    return {"windows_indexed": len(idx.M), "top_hits": hits[["entity", "start"]].astype(str).values.tolist()[:5]}


def demo_ecg():
    """Multi-scale: beat scale (~0.7 s) vs rhythm scale (~6.4 s). Label check: do hits contain 'A' beats?"""
    import wfdb
    rec = wfdb.rdrecord(str(SAMPLES / "05_ecg_mitbih/mitdb_record_100/100"))
    ann = wfdb.rdann(str(SAMPLES / "05_ecg_mitbih/mitdb_record_100/100"), "atr")
    fs = rec.fs
    t = pd.date_range("2000-01-01", periods=rec.sig_len, freq=pd.Timedelta(seconds=1 / fs))
    s = pd.Series(rec.p_signal[:, 0], index=t)
    a_times = t[[smp for smp, sym in zip(ann.sample, ann.symbol) if sym == "A"]]
    res = {}
    for name, rule, stride, k in [("beat", f"{int(round(4000/fs*1000))}us", 2, 20), ("rhythm", "100ms", 1, 20)]:
        idx = MultiTimeframeIndex(window_bars=64, mode="shape").add("ECG100", s, {rule: stride}).finalize()
        win = idx.window_bars * pd.Timedelta(rule)
        qid, _ = idx.query_vector("ECG100", rule, a_times[0] - win / 2)
        hits = idx.search(qid, k=k)
        centre = hits.start + win / 2
        tol = win / 4
        hit_a = [any(abs(c - a) <= tol for a in a_times) for c in centre]
        prior = len(a_times) * 2 * tol / (t[-1] - t[0])
        res[name] = {"window": str(win), "precision@20": round(float(np.mean(hit_a)), 2), "random_baseline": round(float(prior), 3)}
        hits.assign(contains_A_beat=hit_a).drop(columns=["bar_pos"]).to_csv(OUT / f"ecg_{name}_scale_matches.csv", index=False)
        plot_query_and_hits(idx, qid, hits, 0, f"ECG record 100: {name} scale ({win.total_seconds():.1f} s windows), query = first 'A' beat",
                            OUT / f"ecg_{name}_scale_matches.png", n=5)
    return res


def demo_load_lockdown():
    """Electricity demand (Zürich, business customers NE7): query = first lockdown weeks 2020 at daily bars;
    cross-timeframe search at hourly bars; outcome = recovery."""
    z = pd.read_csv(SAMPLES / "13_long_energy_series/zurich_electricity_weather_2015-2022_15min.csv.gz",
                    parse_dates=["Timestamp"]).set_index("Timestamp")
    s = z["Value_NE7"]
    idx = MultiTimeframeIndex(window_bars=28, mode="shape").add("Zurich NE7", s, {"1h": 6, "1D": 1, "7D": 1}).finalize()
    qid, _ = idx.query_vector("Zurich NE7", "1D", "2020-03-02")   # 28 days incl. 16 Mar 2020 lockdown
    hits = idx.search(qid, k=8, timeframes=["1D"])
    stats, _ = outcome_stats(idx, hits, horizon=28, col="mean")
    stats.to_csv(OUT / "load_lockdown_analogues.csv", index=False)
    plot_query_and_hits(idx, qid, hits, 28, "Zürich business electricity use: analogues of March 2020 (daily bars, shape mode)",
                        OUT / "load_lockdown_analogues.png")
    return {"windows_indexed": len(idx.M), "top_hits": hits[["timeframe", "start"]].astype(str).values.tolist()[:6]}


def demo_pv_residual():
    """Solar: raw irradiance is dominated by the daily cycle, so search on the residual = measured / clear-sky
    proxy (31-day rolling max for the same hour). Query = Zürich, 20 Mar 2015 (eclipse morning)."""
    z = pd.read_csv(SAMPLES / "13_long_energy_series/zurich_electricity_weather_2015-2022_15min.csv.gz",
                    parse_dates=["Timestamp"]).set_index("Timestamp")
    g = z["StrGlo [W/m2]"].resample("1h").mean()
    clear = g.groupby(g.index.hour).transform(lambda x: x.rolling(31, min_periods=10, center=True).max())
    ratio = (g / clear).where(clear > 150).clip(0, 1.2)            # daytime hours with enough sun
    daytime = ratio.where((ratio.index.hour >= 7) & (ratio.index.hour <= 14))
    idx = MultiTimeframeIndex(window_bars=8, mode="level").add("Zurich irradiance ratio", daytime, {"1h": 1}).finalize()
    qid, _ = idx.query_vector("Zurich irradiance ratio", "1h", "2015-03-20 07:00")
    hits = idx.search(qid, k=10)
    hits.drop(columns=["bar_pos"]).to_csv(OUT / "pv_eclipse_day_matches.csv", index=False)
    plot_query_and_hits(idx, qid, hits, 0, "Zürich irradiance / clear-sky proxy: mornings most similar to the 2015 eclipse",
                        OUT / "pv_eclipse_day_matches.png", n=5)
    try:  # same index in LanceDB, as in the reference repo (needs a local disk that supports atomic rename)
        import tempfile
        try:
            tbl = idx.to_lancedb(str(ROOT / "lancedb_store"), "pv_windows")
        except NotImplementedError:
            tbl = idx.to_lancedb(tempfile.mkdtemp(), "pv_windows")
        lance_top = tbl.search(idx.V[qid]).limit(3).to_pandas()[["entity", "timeframe", "start"]].astype(str).values.tolist()
    except Exception as ex:  # lancedb not installed
        lance_top = f"LanceDB not used ({ex.__class__.__name__})"
    return {"windows_indexed": len(idx.M), "top_hits": hits[["start", "distance"]].astype(str).values.tolist()[:5],
            "lancedb_top3": lance_top}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    import json
    summary = {}
    for name, fn in [("space_weather", demo_space_weather), ("nyc_taxi", demo_nyc_taxi), ("hydro", demo_hydro),
                     ("ecg", demo_ecg), ("load_lockdown", demo_load_lockdown), ("pv_residual", demo_pv_residual)]:
        print(f"== {name}")
        summary[name] = fn()
        print(json.dumps(summary[name], indent=1, default=str))
    json.dump(summary, open(OUT / "demo_summary.json", "w"), indent=1, default=str)
