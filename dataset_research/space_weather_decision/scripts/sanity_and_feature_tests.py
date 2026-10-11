"""
Space weather: data sanity checks and feature tests for the thesis platform.

Checks the space-weather data against the platform idea: anomaly detection, hand-picked moments, similarity
search over several timeframes with "what happened after", and explanations grounded in expert knowledge.
Every number quoted in ../README.md is written to ../results/results.json.

Run:   python space_weather_decision/scripts/sanity_and_feature_tests.py
Needs: pandas, numpy, matplotlib, scipy (stumpy optional, for the matrix-profile detector)

Inputs
  ../../samples/02_space_weather/celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv  (Kp/ap/Ap, SN, F10.7)
  ../../samples/02_space_weather/gfz_Hp30_2024-05-07_to_14_gannon_storm.csv
  ../../samples/06_wikipedia_pageviews/wikipedia_pageviews_aurora_2024-04_to_11.csv
  ../data/*.csv  (GFZ extension to 2026-10-09, Hp30 storms, DONKI, Richardson & Cane, ISGI/Ebre SSC,
                  NOAA SEP list, OMNI, INTERMAGNET Belsk)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view

HERE = Path(__file__).resolve().parent
SWD = HERE.parent
ROOT = SWD.parent
DATA, RES, FIG = SWD / "data", SWD / "results", SWD / "figures"
RES.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SAMPLE = ROOT / "samples" / "02_space_weather"

C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e6e5e0", "#c3c2b7"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlelocation": "left"})

R: dict = {}
SLOTS = ["00", "03", "06", "09", "12", "15", "18", "21"]
KPC, APC = [f"kp_{s}UT" for s in SLOTS], [f"ap_{s}UT" for s in SLOTS]
# Kp in thirds (0o, 0+, 1-, 1o, ... 9-, 9o) -> ap, Bartels' standard conversion table
KP2AP = np.array([0, 2, 3, 4, 5, 6, 7, 9, 12, 15, 18, 22, 27, 32, 39, 48, 56, 67, 80, 94, 111, 132, 154, 179, 207,
                  236, 300, 400])
G1, G2, G3, G4, G5 = 14, 17, 20, 23, 27          # NOAA G-scale thresholds in Kp thirds: 5-, 6-, 7-, 8-, 9o
BANDS = {"G1": (14, 16), "G2": (17, 19), "G3": (20, 22), "G4": (23, 26), "G5": (27, 27)}  # G4 = Kp 8 incl. 9-
NOAA_PER_CYCLE = {"G1": (1700, 900), "G2": (600, 360), "G3": (200, 130), "G4": (100, 60), "G5": (4, 4)}
H3 = pd.Timedelta(hours=3)


def style(ax):
    ax.grid(color=GRID, lw=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def kp_label(k3: int) -> str:
    n = int(round(k3 / 3))
    return f"{n}{ {-1: '-', 0: 'o', 1: '+'}[int(k3) - 3 * n] }"


def g_level(k3: int) -> str:
    for g, (lo, hi) in BANDS.items():
        if lo <= k3 <= hi:
            return g
    return "below G1"


def to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s.astype(str).str.replace("Z", "", regex=False), errors="coerce")


def any_in(sorted_times: np.ndarray, lo, hi) -> np.ndarray:
    """For each [lo, hi] interval: is there at least one time in sorted_times inside it?"""
    a = np.searchsorted(sorted_times, np.asarray(lo, dtype="datetime64[ns]"), side="left")
    b = np.searchsorted(sorted_times, np.asarray(hi, dtype="datetime64[ns]"), side="right")
    return b > a


def r3(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 3)


def jdefault(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


# ============================================================================ 1. load, integrity, merge
ctk = pd.read_csv(SAMPLE / "celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv", parse_dates=["date"])
ctk = ctk.rename(columns={"ap_daily": "Ap", "sunspot_number_isn": "SN", "f107_observed": "F107_obs",
                          "f107_adjusted": "F107_adj"})
gfz = pd.read_csv(DATA / "gfz_kp_ap_Ap_SN_F107_daily_2025-07-01_to_2026-10-09.csv", parse_dates=["date"])


def integrity(df: pd.DataFrame, rounded: bool) -> dict:
    o = {"first": str(df.date.min().date()), "last": str(df.date.max().date()), "days": int(len(df))}
    full = pd.date_range(df.date.min(), df.date.max(), freq="D")
    o["missing_days"] = int(len(full.difference(df.date)))
    o["duplicate_days"] = int(df.date.duplicated().sum())
    K, A = df[KPC].to_numpy(float), df[APC].to_numpy(float)
    o["kp_missing"], o["ap_missing"] = int(np.isnan(K).sum()), int(np.isnan(A).sum())
    k3 = np.rint(K * 3)
    o["kp_values_off_thirds_grid"] = int((np.abs(K * 3 - k3) > (0.11 if rounded else 0.01)).sum())
    ok = ~np.isnan(k3) & ~np.isnan(A)
    o["kp_ap_pairs_checked"] = int(ok.sum())
    o["kp_ap_mismatches"] = int((KP2AP[k3[ok].astype(int)] != A[ok]).sum())
    o["Ap_vs_mean_of_8_ap_mismatches"] = int((np.abs(df.Ap.to_numpy(float) - A.mean(axis=1)) > 0.5 + 1e-9).sum())
    sn = pd.to_numeric(df.SN, errors="coerce")
    o["SN_missing"] = int((sn.isna() | (sn < 0)).sum())
    for c in ["F107_obs", "F107_adj"]:
        v = pd.to_numeric(df[c], errors="coerce")
        o[f"{c}_missing"] = int((v.isna() | (v <= 0)).sum())
    if "kp_sum" in df:
        o["kp_sum_mismatches"] = int((np.abs(df.kp_sum.to_numpy(float) - k3.sum(axis=1) / 3) > 0.051).sum())
    return o


R["integrity_celestrak"] = integrity(ctk, rounded=True)
R["integrity_gfz_extension"] = integrity(gfz, rounded=False)
R["gfz_extension_status_days"] = gfz.kp_status.value_counts().to_dict()

ov = ctk[ctk.date >= "2025-07-01"].merge(gfz, on="date", suffixes=("_c", "_g"))
k3c = np.rint(ov[[c + "_c" for c in KPC]].to_numpy(float) * 3)
k3g = np.rint(ov[[c + "_g" for c in KPC]].to_numpy(float) * 3)
dk3 = (k3c - k3g)[k3c != k3g]
R["overlap_celestrak_vs_gfz"] = {
    "days": int(len(ov)), "kp_intervals_different": int((k3c != k3g).sum()), "kp_intervals": int(k3c.size),
    "kp_differences_of_one_third": int((np.abs(dk3) == 1).sum()), "kp_preliminary_higher": int((dk3 > 0).sum()),
    "kp_preliminary_lower": int((dk3 < 0).sum()),
    "ap_values_different": int((ov[[c + "_c" for c in APC]].to_numpy() != ov[[c + "_g" for c in APC]].to_numpy()).sum()),
    "Ap_days_different": int((ov.Ap_c != ov.Ap_g).sum()), "SN_days_different": int((ov.SN_c != ov.SN_g).sum()),
    "F107_obs_max_abs_diff": r3((ov.F107_obs_c - ov.F107_obs_g).abs().max()),
    "F107_adj_max_abs_diff": r3((ov.F107_adj_c - ov.F107_adj_g).abs().max())}

cols = ["date"] + KPC + APC + ["Ap", "SN", "F107_obs", "F107_adj"]
d = pd.concat([ctk.loc[ctk.date < "2025-07-01", cols].assign(source="CelesTrak SW-All"),
               gfz[cols].assign(source="GFZ API")], ignore_index=True)
for c in ["F107_obs", "F107_adj"]:
    d[c] = pd.to_numeric(d[c], errors="coerce").where(lambda v: v > 0)
d["SN"] = pd.to_numeric(d.SN, errors="coerce").where(lambda v: v >= 0)
assert d.date.is_monotonic_increasing and not d[KPC].isna().any().any()
K3D = np.rint(d[KPC].to_numpy(float) * 3).astype(int)          # (days, 8)
k3 = K3D.ravel()
ap3 = d[APC].to_numpy(float).ravel()
t3 = (d.date.to_numpy()[:, None] + np.array([np.timedelta64(3 * i, "h") for i in range(8)])).ravel()
kpf = (k3 / 3).astype(np.float32)
N = len(k3)
dmax = K3D.max(axis=1)                                          # daily max Kp (thirds)
years_covered = (d.date.iloc[-1] - d.date.iloc[0]).days / 365.25 + 1 / 365.25
R["merged_series"] = {"first": str(d.date.iloc[0].date()), "last": str(d.date.iloc[-1].date()), "days": int(len(d)),
                      "three_hour_values": int(N), "years": round(years_covered, 2)}
d.to_csv(RES / "kp_ap_Ap_SN_F107_daily_1957-10-01_to_2026-10-09_merged.csv.gz", index=False, compression="gzip")

# ============================================================================ 2. physical sanity checks
doy = d.date.dt.dayofyear.to_numpy()
r_au = 1 - 0.01671 * np.cos(2 * np.pi * (doy - 4) / 365.256)          # Earth-Sun distance (AU), approx.
ratio = (d.F107_adj / d.F107_obs).to_numpy()
m = np.isfinite(ratio)
res_ = ratio[m] - r_au[m] ** 2
R["f107_adjusted_vs_observed"] = {
    "days": int(m.sum()), "corr_ratio_vs_r2": r3(np.corrcoef(ratio[m], r_au[m] ** 2)[0, 1]),
    "median_abs_residual": r3(np.median(np.abs(res_))), "share_within_0.005": r3((np.abs(res_) < 0.005).mean()),
    "ratio_p1": r3(np.percentile(ratio[m], 1)), "ratio_p99": r3(np.percentile(ratio[m], 99))}

mon = d.set_index("date")[["SN", "F107_adj", "Ap"]].resample("MS").mean()
R["sn_vs_f107_monthly_corr"] = r3(mon.SN.corr(mon.F107_adj))
w13 = np.r_[0.5, np.ones(11), 0.5] / 12
mon["SN_13m"] = mon.SN.rolling(13, center=True).apply(lambda x: float((x * w13).sum()), raw=True)


def extrema(s: pd.Series, find_max: bool, sep=84, thr=None):
    v = s.dropna()
    order = v.sort_values(ascending=not find_max).index
    keep = []
    for t in order:
        if thr is not None and ((find_max and v[t] < thr) or (not find_max and v[t] > thr)):
            break
        if all(abs((t - k).days) > sep * 30.4 for k in keep):
            keep.append(t)
    return sorted(keep)


sn_max = extrema(mon.SN_13m, True, thr=80)
sn_min = extrema(mon.SN_13m, False, thr=40)
R["solar_cycle_maxima_13m_smoothed_SN"] = [(t.strftime("%Y-%m"), round(mon.SN_13m[t], 1)) for t in sn_max]
R["solar_cycle_minima_13m_smoothed_SN"] = [(t.strftime("%Y-%m"), round(mon.SN_13m[t], 1)) for t in sn_min]

yr = d.assign(y=d.date.dt.year).groupby("y").agg(Ap=("Ap", "mean"), SN=("SN", "mean"), n=("Ap", "size"))
yr = yr[yr.n > 300]
cyc_rows = []
bounds = [pd.Timestamp("1954-04-01")] + sn_min + [pd.Timestamp("2031-01-01")]
for a, b in zip(bounds[:-1], bounds[1:]):
    ys = yr[(yr.index >= a.year + 1) & (yr.index <= b.year - 1)]
    mx = [t for t in sn_max if a < t < b]
    if len(ys) < 4 or not mx:
        continue
    cyc_rows.append({"cycle_from": a.strftime("%Y-%m"), "SN_max": mx[0].strftime("%Y-%m"),
                     "year_of_max_annual_Ap": int(ys.Ap.idxmax()), "max_annual_Ap": round(ys.Ap.max(), 1),
                     "lag_years_after_SN_max": round(ys.Ap.idxmax() + 0.5 - (mx[0].year + mx[0].month / 12), 1)})
R["geomagnetic_activity_peak_vs_SN_max"] = cyc_rows


def declining(ts: pd.Timestamp) -> bool:
    prev_max = [t for t in sn_max if t <= ts]
    if not prev_max:
        return False
    nxt_min = [t for t in sn_min if t > prev_max[-1]]
    return bool(nxt_min) and ts < nxt_min[0] or (not nxt_min and ts > prev_max[-1])


# semiannual (equinoctial) effect
mo = pd.DatetimeIndex(t3).month.to_numpy()
rate = np.bincount(mo[k3 >= G1], minlength=13)[1:] / np.bincount(mo, minlength=13)[1:]
R["semiannual"] = {"G1plus_share_of_3h_intervals_by_month": [round(float(x), 4) for x in rate],
                   "equinox_over_solstice_ratio": r3(rate[[2, 3, 8, 9]].mean() / rate[[0, 5, 6, 11]].mean())}

# 27-day recurrence
x_ap = np.log1p(d.Ap.to_numpy(float))
anom = x_ap - pd.Series(x_ap).rolling(81, center=True, min_periods=41).mean().to_numpy()


def acf(v, lags):
    out = []
    for L in lags:
        a_, b_ = v[:-L], v[L:]
        mm = np.isfinite(a_) & np.isfinite(b_)
        out.append(np.corrcoef(a_[mm], b_[mm])[0, 1])
    return np.array(out)


LAGS = np.arange(1, 61)
AC = acf(anom, LAGS)
sel = (LAGS >= 20) & (LAGS <= 35)
R["recurrence_27d"] = {"acf_lag27": r3(AC[LAGS == 27][0]), "best_lag_20_35": int(LAGS[sel][np.argmax(AC[sel])]),
                       "acf_best": r3(AC[sel].max()), "acf_lag13": r3(AC[LAGS == 13][0]), "acf_lag20": r3(AC[LAGS == 20][0])}
yac = []
for y_, g in d.assign(an=anom).groupby(d.date.dt.year):
    if len(g) > 300:
        v = g.an.to_numpy()
        yac.append((int(y_), float(acf(v, [27])[0]), declining(pd.Timestamp(f"{y_}-07-01"))))
yac = pd.DataFrame(yac, columns=["year", "acf27", "declining"])
R["recurrence_27d"]["top5_years"] = [(int(a_), round(b_, 2)) for a_, b_ in yac.nlargest(5, "acf27")[["year", "acf27"]].to_numpy()]
R["recurrence_27d"]["mean_acf27_declining_phase_years"] = r3(yac[yac.declining].acf27.mean())
R["recurrence_27d"]["mean_acf27_other_years"] = r3(yac[~yac.declining].acf27.mean())

# ============================================================================ 3. storm events from Kp
idx = np.flatnonzero(k3 >= G1)
br = np.flatnonzero(np.diff(idx) > 8)                     # >= 24 h without G1 starts a new event
starts, ends = np.r_[idx[0], idx[br + 1]], np.r_[idx[br], idx[-1]]
ev = []
for s, e in zip(starts, ends):
    p = s + int(np.argmax(k3[s:e + 1]))
    ev.append((s, e, p, int(k3[p]), int((k3[s:e + 1] >= G1).sum())))
ev = pd.DataFrame(ev, columns=["i_onset", "i_end", "i_peak", "peak_k3", "n_G1_intervals"])
ev["onset"], ev["peak_time"] = t3[ev.i_onset], t3[ev.i_peak]
ev["end"] = pd.to_datetime(t3[ev.i_end]) + H3
ev["onset_k3"] = k3[ev.i_onset]
ev["peak_kp"] = ev.peak_k3.map(kp_label)
ev["level"] = ev.peak_k3.map(g_level)

# G-scale climatology vs NOAA's published numbers
cyc = years_covered / 11
gs = []
for g, (lo, hi) in BANDS.items():
    inb = (k3 >= lo) & (k3 <= hi)
    gs.append({"level": g, "noaa_events_per_cycle": NOAA_PER_CYCLE[g][0], "noaa_days_per_cycle": NOAA_PER_CYCLE[g][1],
               "data_3h_intervals_per_cycle": round(inb.sum() / cyc), "data_days_with_level_per_cycle":
                   round(((K3D >= lo) & (K3D <= hi)).any(axis=1).sum() / cyc),
               "data_days_peaking_at_level_per_cycle": round(((dmax >= lo) & (dmax <= hi)).sum() / cyc),
               "data_storm_events_peaking_at_level_per_cycle": round(((ev.peak_k3 >= lo) & (ev.peak_k3 <= hi)).sum() / cyc, 1)})
gs = pd.DataFrame(gs)
old = (d.date <= "2008-12-31").to_numpy()                       # cycles 19-23 only (stronger cycles)
cyc_old = ((d.date[old].iloc[-1] - d.date.iloc[0]).days + 1) / 365.25 / 11
gs["data_days_with_level_per_cycle_1957_2008"] = [round(((K3D[old] >= lo) & (K3D[old] <= hi)).any(axis=1).sum() / cyc_old)
                                                  for lo, hi in BANDS.values()]
gs["data_3h_intervals_per_cycle_1957_2008"] = [round(((K3D[old] >= lo) & (K3D[old] <= hi)).sum() / cyc_old)
                                               for lo, hi in BANDS.values()]
gs.to_csv(RES / "gscale_frequency_vs_noaa.csv", index=False)
R["gscale_vs_noaa"] = gs.to_dict("records")
R["gscale_cycles_covered"] = round(cyc, 2)

top = d.nlargest(15, "Ap")[["date", "Ap"]].assign(max_kp=lambda x: [kp_label(dmax[i]) for i in x.index])
R["top15_days_by_Ap"] = [(str(r.date.date()), int(r.Ap), r.max_kp) for r in top.itertuples()]
R["events"] = {"G1plus_events": int(len(ev)), **{f"{g}_peak_events": int((ev.level == g).sum()) for g in BANDS}}
ev_years = ev[ev.peak_k3 >= G3].onset.dt.year.value_counts()
R["storm_frequency_1957_2026"] = {                               # how often the problem occurs
    "days_per_year_G1plus": round(float((dmax >= G1).sum() / years_covered), 1),
    "days_per_year_G3plus": round(float((dmax >= G3).sum() / years_covered), 1),
    "storm_events_per_year_G3plus": round(float((ev.peak_k3 >= G3).sum() / years_covered), 1),
    "storm_events_per_year_G4plus": round(float((ev.peak_k3 >= G4).sum() / years_covered), 1),
    "calendar_years_1958_2025_without_G3plus_storm": int(sum(ev_years.get(y, 0) == 0 for y in range(1958, 2026))),
    "max_G3plus_storms_in_one_year": int(ev_years.max()), "year_of_max": int(ev_years.idxmax())}

# ============================================================================ 4. catalogues and knowledge links
ssc = pd.read_csv(DATA / "isgi_ssc_1957_to_2026.csv")
ssc["t"] = pd.to_datetime(ssc.datetime_utc)
ssc = ssc[ssc.type.fillna("SSC") != "SI-"].sort_values("t")
SSC_T = ssc.t.to_numpy()
icme = pd.read_csv(DATA / "richardson_cane_icme_1996_to_2026.csv")
for c in ["disturbance_time", "icme_start", "icme_end"]:
    icme[c] = pd.to_datetime(icme[c], errors="coerce")
icme["t0"] = icme.disturbance_time.fillna(icme.icme_start)
icme["dst"] = pd.to_numeric(icme.dst_min_nT, errors="coerce")
gst = pd.read_csv(DATA / "donki_gst_2010-01-01_to_2026-10-09.csv")
gst["t"] = to_dt(gst.start_time)
gst = gst.sort_values("t").reset_index(drop=True)
ips = pd.read_csv(DATA / "donki_ips_earth_2010-01-01_to_2026-10-09.csv")
ips["t"] = to_dt(ips.event_time)
IPS_T = np.sort(ips.t.to_numpy())
cme = pd.read_csv(DATA / "donki_cme_linked_to_gst.csv")
cme["t"] = to_dt(cme.start_time)
SSC_END, ICME_START, ICME_END = pd.Timestamp("2026-08-31"), pd.Timestamp("1996-05-27"), pd.Timestamp("2026-07-15")
DONKI_START, DONKI_END = pd.Timestamp("2010-04-01"), pd.Timestamp("2026-10-04")

on, pk, en = ev.onset.to_numpy(), ev.peak_time.to_numpy(), ev.end.to_numpy()
ev["ssc"] = any_in(SSC_T, on - np.timedelta64(24, "h"), pk + np.timedelta64(3, "h"))
ev["ips_donki"] = any_in(IPS_T, on - np.timedelta64(24, "h"), pk + np.timedelta64(3, "h"))
ic_lo = (icme.t0 - pd.Timedelta(hours=3)).to_numpy()
ic_hi = (icme.icme_end + pd.Timedelta(hours=6)).to_numpy()
ev["icme"] = [bool(((ic_lo <= p + np.timedelta64(3, "h")) & (ic_hi >= o)).any()) for o, p in zip(on, pk)]
gt = gst.t.to_numpy()
links = {"gst": [], "gst_ids": [], "cme": [], "hss": [], "ips": []}
for o, e_ in zip(on, en):
    j = np.flatnonzero((gt >= o - np.timedelta64(12, "h")) & (gt <= e_ + np.timedelta64(12, "h")))
    g_ = gst.iloc[j]
    links["gst"].append(len(j) > 0)
    links["gst_ids"].append(";".join(g_.gst_id.astype(str)))
    for k_, col in [("cme", "linked_cme"), ("hss", "linked_hss"), ("ips", "linked_ips")]:
        links[k_].append(bool(g_[col].notna().any()))
ev["donki_gst"], ev["donki_gst_ids"] = links["gst"], links["gst_ids"]
ev["gst_linked_cme"], ev["gst_linked_hss"], ev["gst_linked_ips"] = links["cme"], links["hss"], links["ips"]
ev["in_ssc_period"] = ev.onset <= SSC_END
ev["in_icme_period"] = (ev.onset >= ICME_START) & (ev.onset <= ICME_END)
ev["in_donki_period"] = (ev.onset >= DONKI_START) & (ev.onset <= DONKI_END)


def share(mask, col):
    sub = ev[mask]
    return None if len(sub) == 0 else round(100 * sub[col].mean(), 1)


cov = []
for name, lv in [("G2", (17, 19)), ("G3", (20, 22)), ("G4", (23, 26)), ("G5", (27, 27)), ("G3+", (20, 27))]:
    L = (ev.peak_k3 >= lv[0]) & (ev.peak_k3 <= lv[1])
    dn = L & ev.in_donki_period
    sub = ev[dn]
    any_cause = (sub.gst_linked_cme | sub.gst_linked_hss | sub.gst_linked_ips | sub.icme | sub.ssc | sub.ips_donki)
    cov.append({"level": name,
                "n_1957_2026": int((L & ev.in_ssc_period).sum()), "pct_with_SSC_1957_2026": share(L & ev.in_ssc_period, "ssc"),
                "n_1996_2026": int((L & ev.in_icme_period).sum()), "pct_with_ICME_1996_2026": share(L & ev.in_icme_period, "icme"),
                "n_2010_2026": int(dn.sum()), "pct_DONKI_GST": share(dn, "donki_gst"),
                "pct_GST_linked_CME": share(dn, "gst_linked_cme"), "pct_GST_linked_HSS": share(dn, "gst_linked_hss"),
                "pct_GST_linked_IPS": share(dn, "gst_linked_ips"), "pct_DONKI_IPS_at_Earth": share(dn, "ips_donki"),
                "pct_any_cause_evidence_2010_2026": None if len(sub) == 0 else round(100 * any_cause.mean(), 1)})
cov = pd.DataFrame(cov)
cov.to_csv(RES / "knowledge_link_coverage.csv", index=False)
R["knowledge_link_coverage"] = cov.to_dict("records")
R["knowledge_link_windows"] = {"DONKI storm record": "storm start in [onset-12h, end+12h]",
                               "SSC and DONKI shock at Earth": "in [onset-24h, peak+3h]",
                               "ICME": "[disturbance-3h, ICME end+6h] overlaps [onset, peak+3h]"}


def cause_flags(on_, pk_, en_):
    """Same matching rules as above, for arbitrary windows (used for the chance level)."""
    on_, pk_, en_ = (np.asarray(x, "datetime64[ns]") for x in (on_, pk_, en_))
    f = {"ssc": any_in(SSC_T, on_ - np.timedelta64(24, "h"), pk_ + np.timedelta64(3, "h")),
         "ips": any_in(IPS_T, on_ - np.timedelta64(24, "h"), pk_ + np.timedelta64(3, "h")),
         "icme": np.array([bool(((ic_lo <= p + np.timedelta64(3, "h")) & (ic_hi >= o)).any()) for o, p in zip(on_, pk_)])}
    lk = {"cme": [], "hss": [], "ipsl": []}
    for o, e_ in zip(on_, en_):
        g_ = gst.iloc[np.flatnonzero((gt >= o - np.timedelta64(12, "h")) & (gt <= e_ + np.timedelta64(12, "h")))]
        lk["cme"].append(bool(g_.linked_cme.notna().any()))
        lk["hss"].append(bool(g_.linked_hss.notna().any()))
        lk["ipsl"].append(bool(g_.linked_ips.notna().any()))
    f.update({k_: np.array(v) for k_, v in lk.items()})
    f["any"] = f["cme"] | f["hss"] | f["ipsl"] | f["icme"] | f["ssc"] | f["ips"]
    f["cme_hss_icme"] = f["cme"] | f["hss"] | f["icme"]
    return f


g3d = ev[(ev.peak_k3 >= G3) & ev.in_donki_period & (ev.onset <= "2026-06-30")]
rng_c = np.random.default_rng(11)
chance_any, chance_ci = [], []
for _ in range(30):
    sh = (rng_c.integers(5, 26, len(g3d)) * rng_c.choice([-1, 1], len(g3d))).astype("timedelta64[D]")
    f_ = cause_flags(g3d.onset.to_numpy() + sh, g3d.peak_time.to_numpy() + sh, g3d.end.to_numpy() + sh)
    chance_any.append(f_["any"].mean())
    chance_ci.append(f_["cme_hss_icme"].mean())
f_real = cause_flags(g3d.onset, g3d.peak_time, g3d.end)
R["knowledge_link_chance_level_G3plus_2010_2026"] = {
    "n": int(len(g3d)), "actual_any_cause_pct": round(100 * f_real["any"].mean(), 1),
    "actual_cme_hss_or_icme_pct": round(100 * f_real["cme_hss_icme"].mean(), 1),
    "shifted_windows_any_cause_pct": round(100 * float(np.mean(chance_any)), 1),
    "shifted_windows_cme_hss_or_icme_pct": round(100 * float(np.mean(chance_ci)), 1),
    "note": "same windows shifted by a random 5-25 days, 30 repetitions"}
R["icme_disturbance_equals_an_SSC_time"] = int(icme.disturbance_time.isin(set(ssc.t)).sum())
# consistency: DONKI storms (NOAA Kp) vs our GFZ-Kp events
kps_k3 = pd.Series(k3, index=pd.DatetimeIndex(t3))
gst_in =gst[(gst.t >= DONKI_START) & (gst.t <= DONKI_END) & (gst.gst_id != "none")]
ev_g2 = ev[ev.peak_k3 >= G2]
matched = [bool(((ev_g2.onset - pd.Timedelta(hours=12) <= t) & (ev_g2.end + pd.Timedelta(hours=12) >= t)).any())
           for t in gst_in.t]
unm = gst_in[~np.array(matched)]
gfz_max_near = [kp_label(int(kps_k3[(t - pd.Timedelta(hours=12)):(t + pd.Timedelta(hours=36))].max()))
                for t in unm.t] if len(unm) else []
ge6 = (gst_in.kp_max >= 17 / 3 - 0.01).to_numpy()              # NOAA Kp >= 6- (5.67)
unm6 = gst_in[ge6 & ~np.array(matched)]
R["donki_gst_consistency"] = {"donki_gst_records": int(len(gst_in)),
                              "pct_matching_a_GFZ_Kp_G2plus_event": round(100 * np.mean(matched), 1),
                              "unmatched_GFZ_max_kp_near_start": pd.Series(gfz_max_near).value_counts().to_dict(),
                              "records_with_NOAA_kp_ge_6minus": int(ge6.sum()),
                              "of_these_below_G2_in_GFZ": int(len(unm6)),
                              "of_these_GFZ_max_kp": pd.Series([kp_label(int(kps_k3[(t - pd.Timedelta(hours=12)):(t + pd.Timedelta(hours=36))].max()))
                                                                for t in unm6.t]).value_counts().to_dict(),
                              "donki_kp_max_distribution": gst_in.kp_max.round().value_counts().sort_index().to_dict()}
ev.drop(columns=["i_onset", "i_end", "i_peak"]).to_csv(RES / "storm_events_kp_1957_2026_with_catalogue_links.csv", index=False)

# ============================================================================ 5. anomaly detection vs independent catalogues
rng = np.random.default_rng(7)


def catalogue_precision(onsets, peaks, n_shift=30):
    """Share of detections with an SSC (Ebre/ISGI list) in [onset-24h, peak+3h], vs. the same windows shifted
    by a random 5-25 days (base rate)."""
    onsets, peaks = np.asarray(onsets, "datetime64[ns]"), np.asarray(peaks, "datetime64[ns]")
    hit = any_in(SSC_T, onsets - np.timedelta64(24, "h"), peaks + np.timedelta64(3, "h"))
    base = []
    for _ in range(n_shift):
        sh = (rng.integers(5, 26, len(onsets)) * rng.choice([-1, 1], len(onsets))).astype("timedelta64[D]")
        base.append(any_in(SSC_T, onsets + sh - np.timedelta64(24, "h"), peaks + sh + np.timedelta64(3, "h")).mean())
    return round(100 * hit.mean(), 1), round(100 * float(np.mean(base)), 1)


la = pd.Series(np.log1p(ap3))
hist = la.shift(1).rolling(216, min_periods=200)                       # trailing 27 days, not including now
z = ((la - hist.median()) / ((hist.quantile(0.75) - hist.quantile(0.25)) / 1.349 + 0.15)).to_numpy()
Z_THR = 3.0
R["anomaly_detector_settings"] = {"robust_z": "log(ap+1) vs. trailing 27-day median, scale = IQR/1.349 + 0.15",
                                  "threshold": Z_THR}
zi = np.flatnonzero(np.nan_to_num(z) >= Z_THR)
zb = np.flatnonzero(np.diff(zi) > 8)
zs, ze = np.r_[zi[0], zi[zb + 1]], np.r_[zi[zb], zi[-1]]
zev = pd.DataFrame([(s, s + int(np.nanargmax(z[s:e + 1])), float(np.nanmax(z[s:e + 1])), int(k3[s:e + 1].max()))
                    for s, e in zip(zs, ze)], columns=["i_on", "i_pk", "score", "max_k3"])
zev = zev[t3[zev.i_on] <= np.datetime64(SSC_END)].sort_values("score", ascending=False)
det = {}
for name, sub in [("robust_z_top200", zev.head(200)), ("robust_z_all", zev),
                  ("robust_z_below_G1_only", zev[zev.max_k3 < G1])]:
    p, b = catalogue_precision(t3[sub.i_on], t3[sub.i_pk])
    det[name] = {"n": int(len(sub)), "pct_with_SSC": p, "base_rate_pct": b}
thr_ev = ev[ev.in_ssc_period]
for name, sub in [("kp_threshold_G1plus_events", thr_ev), ("kp_threshold_G3plus_events", thr_ev[thr_ev.peak_k3 >= G3])]:
    p, b = catalogue_precision(sub.onset, sub.peak_time)
    det[name] = {"n": int(len(sub)), "pct_with_SSC": p, "base_rate_pct": b}
det["robust_z_all"]["share_reaching_G1"] = round(100 * (zev.max_k3 >= G1).mean(), 1)
det["robust_z_all"]["share_reaching_G3"] = round(100 * (zev.max_k3 >= G3).mean(), 1)
g3_ev = thr_ev[thr_ev.peak_k3 >= G3]
z_on = t3[zev.i_on].astype("datetime64[ns]")
det["recall_of_G3plus_storms_by_robust_z"] = round(100 * np.mean(
    [bool(((z_on >= o - np.timedelta64(24, "h")) & (z_on <= e_)).any()) for o, e_ in zip(g3_ev.onset.to_numpy(), g3_ev.end.to_numpy())]), 1)
low = zev[zev.max_k3 < G1].head(5)
det["examples_below_G1"] = [(str(pd.Timestamp(t3[i]))[:16], kp_label(k_), round(s_, 1))
                            for i, k_, s_ in zip(low.i_on, low.max_k3, low.score)]
try:
    import stumpy
    xa = np.log1p(d.Ap.to_numpy(float))
    mp = stumpy.stump(xa, m=3, normalize=False)[:, 0].astype(float)   # level-aware (not z-normalised)
    order, chosen = np.argsort(-mp), []
    for i in order:
        if all(abs(i - j) >= 3 for j in chosen):
            chosen.append(int(i))
        if len(chosen) == 50:
            break
    on_ = d.date.to_numpy()[chosen]
    p, b = catalogue_precision(on_, on_ + np.timedelta64(3, "D"))
    det["matrix_profile_discords_top50_daily_Ap_m3"] = {
        "n": 50, "pct_with_SSC": p, "base_rate_pct": b,
        "pct_containing_G3plus_day": round(100 * np.mean([dmax[i:i + 3].max() >= G3 for i in chosen]), 1)}
except ImportError:
    det["matrix_profile_discords_top50_daily_Ap_m3"] = "stumpy not installed"
R["anomaly_detection_vs_SSC"] = det

# ============================================================================ 6. "what happened after": analogue backtest (storm scale, 3-h)
W, H, H72, K = 16, 8, 24, 10
Xw = np.ascontiguousarray(sliding_window_view(kpf, W))   # row r = window ending at j = r + W - 1
XX = (Xw.astype(np.float64) ** 2).sum(axis=1)
mx24 = sliding_window_view(kpf, H).max(axis=1)
mx72 = sliding_window_view(kpf, H72).max(axis=1)
y24, y72 = np.full(N, np.nan), np.full(N, np.nan)
y24[:N - H] = mx24[1:N - H + 1]
y72[:N - H72] = mx72[1:N - H72 + 1]
EPS = 1e-4
TH3, TH4 = G3 / 3 - EPS, G4 / 3 - EPS


def crps(ens, y):
    x = np.sort(np.asarray(ens, float))
    n = len(x)
    return float(np.mean(np.abs(x - y)) - np.sum((2 * np.arange(1, n + 1) - n - 1) * x) / n ** 2)


def dense_analogues(i, k=K, horizon=H72):
    """Past-only level-mode kNN for the window ending at i: candidate continuations must end before i.
    Non-overlapping hits (non-maximum suppression), as in MultiTimeframeIndex.search."""
    m_ = i - horizon - W + 1                              # rows 0..m_-1 end at j <= i - horizon - 1
    if m_ <= k * W:
        return np.array([], int)
    q = Xw[i - W + 1]
    d2 = XX[:m_] + float(q @ q) - 2 * (Xw[:m_] @ q)
    cand = np.argpartition(d2, min(600, m_ - 1))[:600]
    cand = cand[np.argsort(d2[cand])]
    out = []
    for r in cand:
        if all(abs(r - o) >= W for o in out):
            out.append(int(r))
        if len(out) == k:
            break
    return np.array(out) + W - 1                          # end indices


onset_i = ev.i_onset.to_numpy()
qmask = (t3[onset_i] >= np.datetime64("1963-01-01")) & (onset_i + H72 < N) & (t3[onset_i] <= np.datetime64(SSC_END))
LEVEL_BIN = lambda k: 0 if k == 14 else 1 if k == 15 else 2 if k == 16 else 3 if k <= 19 else 4
OB = np.array([LEVEL_BIN(int(k)) for k in k3[onset_i]])      # onset level class, for conditional climatology
# knowledge feature known when the onset interval closes: an SSC (shock arrival) in [onset-24h, onset+3h]
SSCF = any_in(SSC_T, t3[onset_i] - np.timedelta64(24, "h"), t3[onset_i] + np.timedelta64(3, "h"))
R["onsets_with_SSC_pct"] = round(100 * SSCF[qmask].mean(), 1)
WLAST = np.linspace(0.3, 1.0, W) ** 2                         # weights: recent intervals count more
rows = []
for qi in np.flatnonzero(qmask):
    i = onset_i[qi]
    pm = (onset_i <= i - H72 - 1) & (onset_i >= W - 1)
    past = onset_i[pm]
    yp24, yp72 = y24[past], y72[past]
    a_end = dense_analogues(i)
    e_ana = {"24": y24[a_end], "72": y72[a_end]}
    q = Xw[i - W + 1].astype(np.float64)
    dpo = ((Xw[past - W + 1] - q) ** 2).sum(axis=1)
    o_end = past[np.argsort(dpo)[:K]]
    e_ons = {"24": y24[o_end], "72": y72[o_end]}
    o30 = past[np.argsort(dpo)[:30]]
    e_o30 = {"24": y24[o30], "72": y72[o30]}
    dpw = (((Xw[past - W + 1] - q) ** 2) * WLAST).sum(axis=1)
    ow = past[np.argsort(dpw)[:30]]
    e_ow = {"24": y24[ow], "72": y72[ow]}
    same = past[OB[pm] == LEVEL_BIN(int(k3[i]))]
    cc = same if len(same) >= 20 else past
    e_cc = {"24": y24[cc], "72": y72[cc]}
    same_s = past[(OB[pm] == LEVEL_BIN(int(k3[i]))) & (SSCF[pm] == SSCF[qi])]
    cs = same_s if len(same_s) >= 20 else cc
    e_cs = {"24": y24[cs], "72": y72[cs]}
    ps = past[SSCF[pm] == SSCF[qi]]
    os_ = ps[np.argsort(dpw[SSCF[pm] == SSCF[qi]])[:30]] if len(ps) >= 30 else ow
    e_os = {"24": y24[os_], "72": y72[os_]}
    e_cl = {"24": yp24, "72": yp72}
    row = {"onset": pd.Timestamp(t3[i]), "onset_kp": float(kpf[i]), "ssc_at_onset": bool(SSCF[qi]),
           "y24": y24[i], "y72": y72[i]}
    for nm, ens in [("analogue_dense", e_ana), ("analogue_onsets", e_ons), ("analogue_onsets_k30", e_o30),
                    ("analogue_onsets_k30_weighted", e_ow), ("cond_climatology", e_cc),
                    ("cond_climatology_plus_SSC", e_cs), ("analogue_k30_weighted_plus_SSC", e_os),
                    ("climatology", e_cl)]:
        for h_ in ["24", "72"]:
            row[f"{nm}_med{h_}"] = float(np.median(ens[h_]))
            row[f"{nm}_crps{h_}"] = crps(ens[h_], row[f"y{h_}"])
        row[f"{nm}_p3"] = float(np.mean(ens["24"] >= TH3))
        row[f"{nm}_p4"] = float(np.mean(ens["24"] >= TH4))
    row["persistence_med24"] = row["persistence_med72"] = float(kpf[i])
    row["persistence_crps24"], row["persistence_crps72"] = abs(kpf[i] - row["y24"]), abs(kpf[i] - row["y72"])
    row["persistence_p3"], row["persistence_p4"] = float(kpf[i] >= TH3), float(kpf[i] >= TH4)
    row["top3_analogue_ends"] = ";".join(str(pd.Timestamp(t3[j]))[:16] for j in a_end[:3])
    rows.append(row)
bt = pd.DataFrame(rows)
bt.to_csv(RES / "backtest_storm_onsets_next24h_72h.csv", index=False)


def auc(p, o):
    from scipy.stats import rankdata
    o = np.asarray(o, bool)
    if o.all() or (~o).all():
        return np.nan
    rk = rankdata(p)
    return (rk[o].sum() - o.sum() * (o.sum() + 1) / 2) / (o.sum() * (~o).sum())


def summarise(b: pd.DataFrame) -> pd.DataFrame:
    o3, o4 = b.y24 >= TH3, b.y24 >= TH4
    out = []
    bs3c = np.mean((b.climatology_p3 - o3) ** 2)
    bs4c = np.mean((b.climatology_p4 - o4) ** 2)
    for nm in ["analogue_dense", "analogue_onsets", "analogue_onsets_k30", "analogue_onsets_k30_weighted",
               "cond_climatology", "cond_climatology_plus_SSC", "analogue_k30_weighted_plus_SSC", "climatology",
               "persistence"]:
        bs3, bs4 = np.mean((b[f"{nm}_p3"] - o3) ** 2), np.mean((b[f"{nm}_p4"] - o4) ** 2)
        out.append({"method": nm, "n": len(b),
                    "MAE_next24h_peak_Kp": round(np.mean(np.abs(b[f"{nm}_med24"] - b.y24)), 3),
                    "CRPS_next24h": round(b[f"{nm}_crps24"].mean(), 3), "CRPS_next72h": round(b[f"{nm}_crps72"].mean(), 3),
                    "Brier_G3plus": round(bs3, 4), "BSS_G3plus_vs_climatology": round(1 - bs3 / bs3c, 3),
                    "AUC_G3plus": round(auc(b[f"{nm}_p3"], o3), 3),
                    "Brier_G4plus": round(bs4, 4), "BSS_G4plus_vs_climatology": round(1 - bs4 / bs4c, 3)})
    return pd.DataFrame(out)


bs_all = summarise(bt)
bs_all.to_csv(RES / "backtest_summary_storm_scale.csv", index=False)
bs_new = summarise(bt[bt.onset >= "1996-01-01"])
bs_new.to_csv(RES / "backtest_summary_storm_scale_1996_2026.csv", index=False)
big = bt[bt.y24 >= TH4]
R["backtest_storm_scale"] = {
    "queries": int(len(bt)), "first_query": str(bt.onset.min())[:16], "base_rate_G3plus_next24h_pct": round(100 * (bt.y24 >= TH3).mean(), 1),
    "base_rate_G4plus_next24h_pct": round(100 * (bt.y24 >= TH4).mean(), 1),
    "summary_all": bs_all.to_dict("records"), "summary_1996_2026": bs_new.to_dict("records"),
    "extremes_actual_G4plus": {"n": int(len(big)), "mean_actual_peak": round(big.y24.mean(), 2),
                               "mean_analogue_median": round(big.analogue_dense_med24.mean(), 2),
                               "mean_analogue_P_G4": round(big.analogue_dense_p4.mean(), 3),
                               "mean_climatology_P_G4": round(big.climatology_p4.mean(), 3)}}

# hand-picked moments: the user marks the first 3-h interval at which a named storm reached the given level and asks
# "what happened after?" (next-24 h peak and hours at G1+ in the next 72 h), answered by past-only analogues
g1sum = sliding_window_view((k3 >= G1).astype(int), H72).sum(axis=1)
g1h72 = np.full(N, np.nan)
g1h72[:N - H72] = 3 * g1sum[1:N - H72 + 1]
picked = [("Halloween 2003", "2003-10-29", G3), ("St Patrick's Day 2015", "2015-03-17", G3),
          ("Starlink loss Feb 2022", "2022-02-03", G1), ("Gannon May 2024", "2024-05-10", G3),
          ("Nov 2025 storm", "2025-11-12", G3), ("Jan 2026 storm", "2026-01-19", G3)]
hp_rows = []
for label, day, lvl in picked:
    c = np.flatnonzero((t3 >= np.datetime64(day) - np.timedelta64(1, "D")) & (t3 < np.datetime64(day) + np.timedelta64(2, "D"))
                       & (k3 >= lvl))
    if len(c) == 0:
        continue
    i = int(c[0])
    a_end = dense_analogues(i, horizon=H72)
    e_ = ev[(ev.i_onset <= i) & (ev.i_end >= i)].iloc[0]
    hp_rows.append({"moment": label, "marked_interval_start": str(pd.Timestamp(t3[i]))[:16], "kp_marked": kp_label(k3[i]),
                    "actual_next24h_peak": kp_label(int(round(y24[i] * 3))), "actual_G1plus_hours_next72h": int(g1h72[i]),
                    "analogue_median_next24h_peak": kp_label(int(round(np.median(y24[a_end]) * 3))),
                    "analogue_P_G4plus_next24h": round(float(np.mean(y24[a_end] >= TH4)), 2),
                    "analogue_median_G1plus_hours_next72h": float(np.median(g1h72[a_end])),
                    "top5_analogues (interval, next-24h peak)": "; ".join(
                        f"{str(pd.Timestamp(t3[j]))[:13]}h {kp_label(int(round(y24[j] * 3)))}" for j in a_end[:5]),
                    "storm_peak_kp": e_.peak_kp, "donki_gst": e_.donki_gst_ids,
                    "ssc_in_storm": bool(e_.ssc), "icme": bool(e_.icme)})
hp = pd.DataFrame(hp_rows)
hp.to_csv(RES / "hand_picked_moments_analogues.csv", index=False)
R["hand_picked_moments"] = hp.to_dict("records")

# ============================================================================ 7. multi-timeframe: 27-day (Bartels rotation) scale
a = np.log1p(d.Ap.to_numpy(float))
L27 = 27
Aw = np.ascontiguousarray(sliding_window_view(a, L27))
AA = (Aw ** 2).sum(axis=1)
nd = len(a)
start_q = int(np.searchsorted(d.date.to_numpy(), np.datetime64("1965-01-01")))
rot = []
for e in range(start_q, nd - L27 - 1, L27):
    m_ = e - 2 * L27 + 1                                  # rows r end at r+26 <= e-28 -> continuation ends <= e-1
    q = Aw[e - L27 + 1]
    d2 = AA[:m_] + q @ q - 2 * Aw[:m_] @ q
    cand = np.argsort(d2)[:400]
    out = []
    for r in cand:
        if all(abs(r - o) >= L27 for o in out):
            out.append(int(r))
        if len(out) == K:
            break
    fut = Aw[e + 1]
    f_ana = np.mean([Aw[r + L27] for r in out], axis=0)
    f_rec = Aw[e - L27 + 1]
    f_cli = np.full(L27, a[e - 364:e + 1].mean())
    f_bl = 0.5 * (f_ana + f_rec)
    rot.append({"date": d.date.iloc[e], "declining": declining(d.date.iloc[e]),
                **{f"MAE_{n_}": float(np.mean(np.abs(f_ - fut))) for n_, f_ in
                   [("analogue", f_ana), ("recurrence", f_rec), ("climatology", f_cli), ("blend", f_bl)]}})
rot = pd.DataFrame(rot)
rs = []
for name, sub in [("all", rot), ("declining_phase", rot[rot.declining]), ("rising_or_max_phase", rot[~rot.declining])]:
    base = sub.MAE_climatology.mean()
    rs.append({"subset": name, "n": len(sub), **{f"skill_vs_climatology_{n_}": round(1 - sub[f"MAE_{n_}"].mean() / base, 3)
                                                 for n_ in ["analogue", "recurrence", "blend"]},
               "MAE_climatology_logAp": round(base, 3)})
rs = pd.DataFrame(rs)
rs.to_csv(RES / "backtest_rotation_scale_27d.csv", index=False)
R["backtest_rotation_scale"] = rs.to_dict("records")

# ============================================================================ 8. knowledge changes "what happened after": 27-day recurrence by driver
dg1 = pd.Series(dmax >= G1, index=d.date)


def recur(pday: pd.Timestamp) -> bool:
    return bool(dg1[pday + pd.Timedelta(days=25): pday + pd.Timedelta(days=29)].any())


rc = ev[(ev.onset >= "1996-06-01") & (ev.onset <= "2026-06-01")].copy()
rc["pday"] = rc.peak_time.dt.normalize()
rc["recur27"] = [recur(p) for p in rc.pday]
days = dg1["1996-06-01":"2026-06-01"].index
base27 = np.mean([recur(p) for p in days])
rows = {"base_rate_any_G1_day_in_a_5day_window_pct": round(100 * base27, 1)}
for name, msk in [("icme_driven", rc.icme), ("not_icme", ~rc.icme)]:
    s_ = rc[msk]
    rows[name] = {"n": int(len(s_)), "pct_G1_storm_again_25_29_days_later": round(100 * s_.recur27.mean(), 1),
                  "declining_phase_pct": round(100 * s_[[declining(t) for t in s_.pday]].recur27.mean(), 1)}
dk = ev[ev.in_donki_period & ev.donki_gst & (ev.onset <= "2026-08-31")].copy()
dk["recur27"] = [recur(p) for p in dk.peak_time.dt.normalize()]
for name, msk in [("donki_linked_HSS_only", dk.gst_linked_hss & ~dk.gst_linked_cme),
                  ("donki_linked_CME", dk.gst_linked_cme)]:
    rows[name] = {"n": int(msk.sum()), "pct_G1_storm_again_25_29_days_later": round(100 * dk[msk].recur27.mean(), 1)}
R["recurrence_by_driver"] = rows

# ============================================================================ 9. finer timeframe: Hp30 (30 min) vs Kp (3 h)
hp30 = pd.read_csv(DATA / "gfz_Hp30_selected_storms.csv")
g_ = pd.read_csv(SAMPLE / "gfz_Hp30_2024-05-07_to_14_gannon_storm.csv").assign(storm_window="Gannon2024")
hp30 = pd.concat([hp30, g_], ignore_index=True)
hp30["t"] = pd.to_datetime(hp30.datetime_utc)
kps = pd.Series(kpf, index=pd.DatetimeIndex(t3))
hrows = []
for wname, g in hp30.groupby("storm_window", sort=False):
    kw = kps[g.t.min(): g.t.max()]
    row = {"storm": wname, "max_Hp30": round(g.Hp30.max(), 3), "max_Hp30_time": str(g.loc[g.Hp30.idxmax(), "t"])[:16],
           "max_Kp": kp_label(int(round(kw.max() * 3)))}
    for thr_name, thr in [("G1", G1), ("G3", G3)]:
        h_on = g[g.Hp30 >= thr / 3 - EPS].t.min()
        k_on = kw[kw >= thr / 3 - EPS].index.min()
        row[f"{thr_name}_first_known_Hp30"] = str(h_on + pd.Timedelta(minutes=30))[:16] if pd.notna(h_on) else None
        row[f"{thr_name}_first_known_Kp"] = str(k_on + H3)[:16] if pd.notna(k_on) else None
        row[f"{thr_name}_lead_hours_Hp30_over_Kp"] = (round(((k_on + H3) - (h_on + pd.Timedelta(minutes=30))).total_seconds() / 3600, 1)
                                                       if pd.notna(h_on) and pd.notna(k_on) else None)
    hrows.append(row)
hp_tab = pd.DataFrame(hrows)
hp_tab.to_csv(RES / "hp30_vs_kp_storms.csv", index=False)
R["hp30_vs_kp"] = hp_tab.to_dict("records")

# ============================================================================ 10. knowledge-grounded explanation card: Gannon storm
T0, T1 = pd.Timestamp("2024-05-08"), pd.Timestamp("2024-05-14")
omni = pd.read_csv(DATA / "omni_hourly_2024-05-08_to_2024-05-15_gannon.csv", parse_dates=["datetime_utc"])
bel = pd.read_csv(DATA / "intermagnet_BEL_1min_2024-05-10T12_to_2024-05-11T12.csv", parse_dates=["datetime_utc"])
sep = pd.read_csv(DATA / "noaa_sep_events_1976_to_2026.csv")
sep["t"] = pd.to_datetime(sep.start_time, errors="coerce")
pv = pd.read_csv(ROOT / "samples/06_wikipedia_pageviews/wikipedia_pageviews_aurora_2024-04_to_11.csv", parse_dates=["date"])
g_gst = gst[(gst.t >= T0) & (gst.t < T1)]
cme_ids = sorted({x for v in g_gst.linked_cme.dropna() for x in v.split(";")})
g_cme = cme[cme.activity_id.isin(cme_ids)]
g_ips = ips[(ips.t >= T0) & (ips.t < T1)]
g_icme = icme[(icme.t0 >= T0) & (icme.t0 < T1)]
g_ssc = ssc[(ssc.t >= T0) & (ssc.t < T1)]
g_sep = sep[(sep.t >= T0) & (sep.t < T1)]
bel["dH"] = bel.H_nT.diff().abs()
pre = bel[(bel.datetime_utc >= "2024-05-10 16:50") & (bel.datetime_utc <= "2024-05-10 17:05")].H_nT
post = bel[(bel.datetime_utc >= "2024-05-10 17:08") & (bel.datetime_utc <= "2024-05-10 17:20")].H_nT
card = {
    "moment": "2024-05-10/11 geomagnetic storm ('Gannon')",
    "series_evidence": {
        "Kp_max": kp_label(int(round(kps["2024-05-10":"2024-05-12"].max() * 3))),
        "Hp30_max": float(hp30[hp30.storm_window == "Gannon2024"].Hp30.max()),
        "daily_Ap_2024-05-11": int(d.loc[d.date == "2024-05-11", "Ap"].iloc[0]),
        "rank_of_2024-05-11_by_daily_Ap_since_1957": int((d.Ap > d.loc[d.date == "2024-05-11", "Ap"].iloc[0]).sum() + 1),
        "OMNI_min_Bz_nT": float(omni.Bz_GSM_nT.min()), "OMNI_min_Bz_time": str(omni.loc[omni.Bz_GSM_nT.idxmin(), "datetime_utc"])[:16],
        "OMNI_max_speed_km_s": float(omni.flow_speed_km_s.max()),
        "OMNI_min_Dst_nT": float(omni.Dst_nT.min()), "OMNI_min_Dst_time": str(omni.loc[omni.Dst_nT.idxmin(), "datetime_utc"])[:16],
        "OMNI_max_AE_nT": float(omni.AE_nT.max()),
        "Belsk_H_step_at_SSC_nT": round(float(post.median() - pre.median()), 1),
        "Belsk_min_H_nT": float(bel.H_nT.min()), "Belsk_min_H_time": str(bel.loc[bel.H_nT.idxmin(), "datetime_utc"])[:16],
        "Belsk_H_range_nT": round(float(bel.H_nT.max() - bel.H_nT.min()), 1),
        "Belsk_max_1min_dH_nT": float(bel.dH.max()), "Belsk_max_1min_dH_time": str(bel.loc[bel.dH.idxmax(), "datetime_utc"])[:16],
        "Wikipedia_Aurora_en_views_2024-05-11": int(pv.loc[pv.date == "2024-05-11", "en_Aurora_views"].iloc[0])},
    "catalogue_evidence": {
        "DONKI_GST": g_gst[["gst_id", "kp_max"]].to_dict("records"),
        "DONKI_linked_CMEs": g_cme[["activity_id", "speed_kms", "source_location", "active_region_num", "type"]].to_dict("records"),
        "DONKI_IPS_at_Earth": g_ips.event_time.tolist(),
        "RichardsonCane_ICME": g_icme[["disturbance_time", "icme_start", "icme_end", "dst_min_nT", "v_icme", "lasco_cme"]].astype(str).to_dict("records"),
        "SSC_Ebre_ISGI": g_ssc[["datetime_utc", "type", "amplitude_nT"]].astype(str).to_dict("records"),
        "NOAA_SEP_events": g_sep[["start_time", "max_time", "peak_pfu_gt10MeV", "flare_importance", "location"]].astype(str).to_dict("records")}}
card["series_evidence"]["Wikipedia_Zorza_polarna_pl_views_2024-05-11"] = int(
    pv.loc[pv.date == "2024-05-11", "pl_Zorza_polarna_views"].iloc[0])
card["series_evidence"]["Wikipedia_Zorza_polarna_pl_median_daily_views_Apr_2024"] = float(
    pv[(pv.date >= "2024-04-01") & (pv.date < "2024-05-01")].pl_Zorza_polarna_views.median())
bh = bel.set_index("datetime_utc").H_nT
card["series_evidence"]["Belsk_H_17:05_17:06_17:07_17:08"] = [float(bh[f"2024-05-10 17:0{k_}"]) for k_ in (5, 6, 7, 8)]
(RES / "explanation_card_gannon_2024.json").write_text(json.dumps(card, indent=2, default=jdefault))
R["gannon_card"] = card


def catalogue_card(t0, t1):
    """The knowledge layer for any window: what the catalogues say happened (no model knowledge needed)."""
    t0, t1 = pd.Timestamp(t0), pd.Timestamp(t1)
    gg = gst[(gst.t >= t0) & (gst.t < t1)]
    ids = sorted({x for v in gg.linked_cme.dropna() for x in v.split(";")})
    dd = d[(d.date >= t0) & (d.date < t1)]
    return {"window": f"{t0.date()} to {t1.date()}", "Kp_max": kp_label(int(kps_k3[t0:t1 - H3].max())),
            "max_daily_Ap": int(dd.Ap.max()), "max_daily_Ap_date": str(dd.loc[dd.Ap.idxmax(), "date"].date()),
            "rank_of_that_day_by_Ap_since_1957": int((d.Ap > dd.Ap.max()).sum() + 1),
            "DONKI_GST": gg[["gst_id", "kp_max"]].to_dict("records"),
            "DONKI_linked_CMEs": cme[cme.activity_id.isin(ids)][["activity_id", "speed_kms", "source_location",
                                                                  "active_region_num", "type"]].to_dict("records"),
            "DONKI_IPS_at_Earth": ips[(ips.t >= t0) & (ips.t < t1)].event_time.tolist(),
            "RichardsonCane_ICME": icme[(icme.t0 >= t0) & (icme.t0 < t1)][["disturbance_time", "icme_start", "icme_end",
                                                                          "dst_min_nT", "dst_flag", "v_icme"]].astype(str).to_dict("records"),
            "SSC_Ebre_ISGI": ssc[(ssc.t >= t0) & (ssc.t < t1)][["datetime_utc", "type", "status"]].astype(str).to_dict("records"),
            "NOAA_SEP_events_from_3_days_before": sep[(sep.t >= t0 - pd.Timedelta(days=3)) & (sep.t < t1)][
                ["start_time", "max_time", "peak_pfu_gt10MeV", "flare_importance", "location"]].astype(str).to_dict("records")}


cards = {"Nov 2025 storm": catalogue_card("2025-11-10", "2025-11-15"),
         "Jan 2026 storm": catalogue_card("2026-01-18", "2026-01-23")}
(RES / "explanation_cards_recent_storms.json").write_text(json.dumps(cards, indent=2, default=jdefault))
R["recent_cards"] = cards

# ============================================================================ 11. figures
# fig 1: overview
fig, ax = plt.subplots(3, 1, figsize=(8.6, 6.4), sharex=True, gridspec_kw={"height_ratios": [1.1, 1, 1]})
ax[0].plot(mon.index, mon.SN, color=C4, lw=0.6, alpha=0.6, label="monthly sunspot number (SILSO v2)")
ax[0].plot(mon.index, mon.SN_13m, color=INK, lw=1.3, label="13-month smoothed")
for t in sn_max:
    ax[0].annotate(t.strftime("%Y-%m"), (t, mon.SN_13m[t]), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=6.5, color=INK2)
ax[0].set_ylabel("sunspot number")
ax[0].legend(frameon=False, fontsize=7, loc="upper right")
ax[0].set_title("A. Solar cycle: maxima of cycles 19-25 found in the data")
ax[1].plot(mon.index, mon.Ap, color=C1, lw=0.7)
ax[1].set_ylabel("monthly mean Ap")
ax[1].set_title("B. Geomagnetic activity (Ap): peaks often in the declining phase")
ev_y = ev.assign(y=ev.onset.dt.year)
cnt = ev_y[ev_y.peak_k3 >= G3].groupby("y").size().reindex(range(1957, 2027), fill_value=0)
cnt4 = ev_y[ev_y.peak_k3 >= G4].groupby("y").size().reindex(range(1957, 2027), fill_value=0)
xy = pd.to_datetime([f"{y}-07-01" for y in cnt.index])
ax[2].bar(xy, cnt.values, width=300, color=C2, label="storms reaching G3+ (Kp ≥ 7-)")
ax[2].bar(xy, cnt4.values, width=300, color=INK, label="of which G4+ (Kp ≥ 8-)")
ax[2].set_ylabel("storms per year")
ax[2].legend(frameon=False, fontsize=7, loc="upper right")
ax[2].set_title("C. Storm events detected from 3-h Kp (≥ 24 h quiet between events)")
for a_ in ax:
    style(a_)
fig.suptitle("Space weather data 1957-10 → 2026-10 (CelesTrak/GFZ Kp, SILSO SN)", x=0.01, ha="left", fontsize=9.5, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "fig1_data_overview.png", dpi=140)
plt.close(fig)

# fig 2: sanity checks
fig, ax = plt.subplots(2, 2, figsize=(8.6, 6.0))
ss = np.random.default_rng(1).choice(np.flatnonzero(m), 4000, replace=False)
ax[0, 0].scatter(doy[ss], ratio[ss], s=2, color=C1, alpha=0.4, label="adjusted / observed F10.7")
o_ = np.argsort(doy)
ax[0, 0].plot(doy[o_], r_au[o_] ** 2, color=C2, lw=1.4, label="expected (Earth-Sun distance)²")
ax[0, 0].set_xlabel("day of year")
ax[0, 0].set_title("A. F10.7: adjusted vs observed follows the orbit")
ax[0, 0].legend(frameon=False, fontsize=6.5)
mlab = list("JFMAMJJASOND")
ax[0, 1].bar(range(12), 100 * rate, color=[C2 if i in (2, 3, 8, 9) else C1 for i in range(12)])
ax[0, 1].set_xticks(range(12), mlab)
ax[0, 1].set_ylabel("% of 3-h intervals at G1+")
ax[0, 1].set_title("B. Equinox months are stormier (semiannual effect)")
ax[1, 0].plot(LAGS, AC, color=C1, lw=1.3)
ax[1, 0].axvline(27, color=C2, lw=0.9, ls="--")
ax[1, 0].text(27.8, AC.max() * 0.95, "27 days\n(solar rotation)", fontsize=6.5, color=C2, va="top")
ax[1, 0].set_xlabel("lag (days)")
ax[1, 0].set_ylabel("autocorrelation")
ax[1, 0].set_title("C. Daily Ap anomaly recurs every ~27 days")
xx = np.arange(5)
ax[1, 1].bar(xx - 0.27, gs.noaa_days_per_cycle, width=0.27, color=MUTED, label="NOAA scale: storm days per cycle")
ax[1, 1].bar(xx, gs.data_days_with_level_per_cycle_1957_2008, width=0.27, color=C1, label="data 1957-2008 (cycles 19-23)")
ax[1, 1].bar(xx + 0.27, gs.data_days_with_level_per_cycle, width=0.27, color=C3, label="data 1957-2026 (incl. weak cycle 24)")
ax[1, 1].set_yscale("log")
ax[1, 1].set_xticks(xx, gs.level)
ax[1, 1].set_ylabel("days per 11 years")
ax[1, 1].set_title("D. G-scale frequencies reproduce NOAA's published values")
ax[1, 1].legend(frameon=False, fontsize=6.5)
for a_ in ax.ravel():
    style(a_)
fig.tight_layout()
fig.savefig(FIG / "fig2_sanity_checks.png", dpi=140)
plt.close(fig)

# fig 3: what happened after - backtests
fig, ax = plt.subplots(1, 3, figsize=(10.4, 3.6), gridspec_kw={"width_ratios": [1.35, 1, 1]})
meth = ["analogue_dense", "analogue_onsets_k30_weighted", "persistence", "cond_climatology",
        "analogue_k30_weighted_plus_SSC", "cond_climatology_plus_SSC"]
lab = ["Kp analogues (platform default)", "Kp analogues (tuned: k=30, recent-weighted)", "persistence",
       "climatology by onset level", "tuned analogues + SSC (knowledge)", "climatology by level + SSC (knowledge)"]
v3 = [bs_all.set_index("method").loc[mm, "BSS_G3plus_vs_climatology"] for mm in meth]
v4 = [bs_all.set_index("method").loc[mm, "BSS_G4plus_vs_climatology"] for mm in meth]
yy = np.arange(len(meth))[::-1]
ax[0].barh(yy + 0.2, v3, 0.4, color=C1, label="P(G3+ in next 24 h)")
ax[0].barh(yy - 0.2, v4, 0.4, color=C2, label="P(G4+ in next 24 h)")
ax[0].axvline(0, color=INK2, lw=0.8)
ax[0].set_yticks(yy, lab, fontsize=6.5)
ax[0].set_xlabel("Brier skill score vs climatology (higher = better)")
ax[0].set_title("A. At storm onset: will it reach G3+/G4+?")
ax[0].legend(frameon=False, fontsize=6.5, loc="upper right")
jit = np.random.default_rng(3).normal(0, 0.07, len(bt))
ax[1].scatter(bt.analogue_dense_med24 + jit, bt.y24 + jit[::-1], s=3, color=C1, alpha=0.35)
ax[1].plot([4, 9], [4, 9], color=INK2, lw=0.8)
ax[1].set_xlabel("analogue median (platform default), next-24 h peak Kp")
ax[1].set_ylabel("actual next-24 h peak Kp")
ax[1].set_title("B. Analogues regress to typical storms")
rs_i = rs.set_index("subset")
groups = ["all", "declining_phase", "rising_or_max_phase"]
for j_, (nm, col) in enumerate([("analogue", C1), ("recurrence", C3), ("blend", C4)]):
    ax[2].bar(np.arange(3) + (j_ - 1) * 0.27, [rs_i.loc[g, f"skill_vs_climatology_{nm}"] for g in groups], 0.27, color=col, label=nm)
ax[2].axhline(0, color=INK2, lw=0.8)
ax[2].set_xticks(range(3), ["all", "declining\nphase", "rising/max\nphase"], fontsize=6.5)
ax[2].set_ylabel("MAE skill vs climatology")
ax[2].set_title("C. Next solar rotation (27 days)")
ax[2].legend(frameon=False, fontsize=6.5)
for a_ in ax:
    style(a_)
fig.tight_layout()
fig.savefig(FIG / "fig3_what_happened_after_backtests.png", dpi=140)
plt.close(fig)

# fig 4: knowledge links
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.3), gridspec_kw={"width_ratios": [1.35, 1]})
cv = cov.set_index("level")
lv = ["G2", "G3", "G4", "G5"]
items = [("pct_DONKI_GST", "DONKI storm record", C1), ("pct_GST_linked_CME", "…linked to a CME", C2),
         ("pct_with_ICME_1996_2026", "ICME (Richardson & Cane, 1996+)", C3), ("pct_with_SSC_1957_2026", "SSC (ISGI/Ebre, 1957+)", C4)]
for j_, (col, lab_, cl) in enumerate(items):
    ax[0].bar(np.arange(4) + (j_ - 1.5) * 0.2, [cv.loc[l_, col] for l_ in lv], 0.2, color=cl, label=lab_)
ax[0].set_xticks(range(4), [f"{l_}\n(n={cv.loc[l_, 'n_2010_2026']} / {cv.loc[l_, 'n_1957_2026']})" for l_ in lv], fontsize=6.5)
ax[0].set_ylabel("% of storms with this evidence")
ax[0].set_ylim(0, 128)
ax[0].set_yticks(range(0, 101, 20))
ax[0].set_title("A. Can a storm be linked to a catalogued cause?")
ax[0].legend(frameon=False, fontsize=6, loc="upper left", ncol=2)
rb = R["recurrence_by_driver"]
names = [("not_icme", "no ICME\n(likely stream)"), ("icme_driven", "ICME-driven"),
         ("donki_linked_HSS_only", "DONKI: HSS\nonly"), ("donki_linked_CME", "DONKI: CME")]
ax[1].bar(range(4), [rb[k_]["pct_G1_storm_again_25_29_days_later"] for k_, _ in names], color=[C3, C2, C3, C2])
ax[1].axhline(rb["base_rate_any_G1_day_in_a_5day_window_pct"], color=INK2, lw=0.9, ls="--")
ax[1].text(3.45, rb["base_rate_any_G1_day_in_a_5day_window_pct"] + 1, "base rate", fontsize=6.5, ha="right", color=INK2)
ax[1].set_xticks(range(4), [f"{n_}\n(n={rb[k_]['n']})" for k_, n_ in names], fontsize=6.5)
ax[1].set_ylabel("% with a G1+ storm 25-29 days later")
ax[1].set_title("B. Knowledge changes 'what happens next'")
for a_ in ax:
    style(a_)
fig.tight_layout()
fig.savefig(FIG / "fig4_knowledge_links.png", dpi=140)
plt.close(fig)

# fig 5: Gannon explanation card
P0, P1 = pd.Timestamp("2024-05-10 06:00"), pd.Timestamp("2024-05-12 06:00")
fig, ax = plt.subplots(4, 1, figsize=(8.6, 7.4), sharex=True)
om = omni[(omni.datetime_utc >= P0) & (omni.datetime_utc <= P1)]
ax[0].plot(om.datetime_utc, om.flow_speed_km_s, color=C1, lw=1.3)
ax[0].set_ylabel("solar wind speed\n(km/s)", color=C1)
tw = ax[0].twinx()
tw.plot(om.datetime_utc, om.Bz_GSM_nT, color=C2, lw=1.1)
tw.axhline(0, color=MUTED, lw=0.6)
tw.set_ylabel("Bz GSM (nT)", color=C2)
for s_ in ("top",):
    tw.spines[s_].set_visible(False)
ax[0].set_title("A. Cause upstream: NASA OMNI solar wind at L1 (hourly)")
hg = hp30[(hp30.storm_window == "Gannon2024") & (hp30.t >= P0) & (hp30.t <= P1)]
ax[1].step(hg.t, hg.Hp30, where="post", color=C1, lw=1.0, label="Hp30 (30 min, open-ended)")
kk = kps[P0:P1]
ax[1].step(kk.index, kk.values, where="post", color=C2, lw=1.6, label="Kp (3 h, capped at 9)")
ax[1].set_ylabel("index")
ax[1].legend(frameon=False, fontsize=6.5, loc="upper left")
ax[1].set_title("B. Same storm at two timeframes (GFZ)")
ax[2].plot(om.datetime_utc, om.Dst_nT, color=C4, lw=1.3)
ax[2].set_ylabel("Dst (nT)")
ax[2].set_title("C. Ring current: OMNI Dst (hourly, provisional)")
bb = bel[(bel.datetime_utc >= P0) & (bel.datetime_utc <= P1)]
ax[3].plot(bb.datetime_utc, bb.H_nT, color=C3, lw=0.8)
ax[3].set_ylabel("H (nT)")
ax[3].set_title("D. Ground effect in Poland: Belsk (BEL) magnetometer, 1 min (INTERMAGNET, definitive)")
ax[1].set_ylim(0, 13)
for a_ in ax:
    style(a_)
    for t in g_ssc.t[(g_ssc.t >= P0) & (g_ssc.t <= P1)]:
        a_.axvline(t, color=INK, lw=0.9, ls="--")
    for t in g_ips.t[(g_ips.t >= P0) & (g_ips.t <= P1)]:
        a_.axvline(t, color=C5, lw=1.0, ls=":")
    for r_ in g_icme.itertuples():
        if r_.icme_start < P1:
            a_.axvspan(max(r_.icme_start, P0), min(r_.icme_end, P1), color=GRID, alpha=0.6, lw=0)
    a_.axvline(pd.Timestamp("2024-05-10 22:54"), color=C2, lw=0.9)
    a_.set_xlim(P0, P1)
ax[0].text(g_ssc.t.iloc[0] if len(g_ssc) else P0, ax[0].get_ylim()[1], " SSC 17:05", fontsize=6.5, va="top")
ax[1].text(pd.Timestamp("2024-05-10 23:10"), 12.0, "NOAA: G5 observed 22:54 UT", fontsize=6.5, color=C2)
ax[3].xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
fig.suptitle("Explanation card: 10-11 May 2024 storm - series plus catalogue evidence", x=0.01, ha="left",
             fontsize=9.5, fontweight="bold")
fig.text(0.01, 0.005, "Black dashed = SSC (ISGI/Ebre list) · pink dotted = shock at Earth (NASA DONKI) · orange = NOAA G5 "
         "alert · grey band = ICME (Richardson & Cane list). DONKI links the 10-12 May storms to six CMEs launched "
         "8-10 May, five of them from active region 13664.", fontsize=6.5, color=INK2, wrap=True)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIG / "fig5_gannon_explanation_card.png", dpi=140)
plt.close(fig)

(RES / "results.json").write_text(json.dumps(R, indent=1, default=jdefault))
print("done:", ", ".join(R))
