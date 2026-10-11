"""
Re-creates every figure in ../samples/*/plot_*.png from the sample CSVs,
and runs two small proof-of-concept analyses (similarity search + discords).

Usage (from the dataset_research folder):
    pip install pandas numpy matplotlib wfdb stumpy
    python scripts/make_sample_plots.py

Every event annotation drawn on a plot comes from an external, citable source
(listed in ../samples/<folder>/SOURCE.md). The point of the figures is to show
"time-series moment  ->  expert explanation" pairs, i.e. the ground truth the
system should eventually reproduce automatically.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent / "samples"

# Categorical slots in fixed order (validated default palette, light mode)
C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, INK2, GRID, BAND = "#0b0b0b", "#52514e", "#e6e5e0", "#d9d8d2"

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlesize": 10,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.6,
    "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "#fcfcfb",
})


def band(ax, start, end, label=None, y=0.97):
    ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=BAND, alpha=0.6, lw=0, zorder=0)
    if label:
        ax.text(pd.Timestamp(start), y, " " + label, transform=ax.get_xaxis_transform(),
                va="top", ha="left", fontsize=8, color=INK2)


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path.relative_to(ROOT.parent))


# --------------------------------------------------------------------- 01 eclipse
def plot_eclipse():
    d = ROOT / "01_eclipse_solar"
    de = pd.read_csv(d / "energy_charts_DE_2015-03-19_to_21_15min.csv", parse_dates=["timestamp_utc"])
    z = pd.read_csv(d / "zurich_irradiance_and_load_2015-03-13_to_27_15min.csv", parse_dates=["Timestamp"])
    e26 = pd.read_csv(d / "energy_charts_DE_ES_PL_solar_2026-08-11_to_13_15min.csv", parse_dates=["timestamp_utc"])

    fig, axes = plt.subplots(3, 1, figsize=(8, 9))
    # (a) Germany 2015 — overlay the three days by time of day
    ax = axes[0]
    for day, col, lab in [("2015-03-19", C2, "19 Mar (day before)"), ("2015-03-20", C1, "20 Mar (eclipse)"),
                          ("2015-03-21", C3, "21 Mar (day after, cloudier)")]:
        s = de[de.timestamp_utc.dt.strftime("%Y-%m-%d") == day]
        tod = s.timestamp_utc.dt.hour + s.timestamp_utc.dt.minute / 60
        ax.plot(tod, s.solar_MW / 1000, color=col, label=lab, lw=2.2 if "eclipse" in lab else 1.4)
    ax.axvspan(8 + 33 / 60, 10 + 52 / 60, color=BAND, alpha=0.6, lw=0)
    ax.text(8.6, 0.03, " partial eclipse over Germany\n 08:33-10:52 UTC (ENTSO-E 2015)", transform=ax.get_xaxis_transform(),
            va="bottom", fontsize=8, color=INK2)
    ax.set(title="Germany: PV feed-in on 20 March 2015 vs. neighbouring days", xlabel="hour of day (UTC)",
           ylabel="solar generation [GW]", xlim=(4, 19))
    ax.legend(loc="upper right")

    # (b) Zurich measured global irradiance, eclipse day vs a clear reference day
    ax = axes[1]
    for day, col, lab in [("2015-03-19", C2, "19 Mar"), ("2015-03-20", C1, "20 Mar (eclipse)")]:
        s = z[z.Timestamp.dt.strftime("%Y-%m-%d") == day]
        tod = s.Timestamp.dt.hour + s.Timestamp.dt.minute / 60
        ax.plot(tod, s["StrGlo [W/m2]"], color=col, label=lab, lw=2.2 if "eclipse" in lab else 1.4)
    ax.axvspan(8 + 24 / 60, 10 + 44 / 60, color=BAND, alpha=0.6, lw=0)
    ax.text(8.45, 0.03, " eclipse in Bern 08:24-10:44 UTC,\n max 09:32, 70% obscured (EclipseWise)", transform=ax.get_xaxis_transform(),
            va="bottom", fontsize=8, color=INK2)
    ax.set(title="Zurich (Stampfenbachstrasse): measured global irradiance (hourly, interpolated to 15 min)",
           xlabel="hour of day (UTC)", ylabel="W/m²", xlim=(5, 18))
    ax.legend(loc="upper right")

    # (c) 12 Aug 2026 eclipse near sunset — Spain and Germany
    ax = axes[2]
    for day, ls in [("2026-08-11", ":"), ("2026-08-12", "-"), ("2026-08-13", "--")]:
        s = e26[e26.timestamp_utc.dt.strftime("%Y-%m-%d") == day]
        tod = s.timestamp_utc.dt.hour + s.timestamp_utc.dt.minute / 60
        ax.plot(tod, s.es_solar_MW / 1000, color=C1, ls=ls, lw=2 if ls == "-" else 1.2,
                label=f"Spain {day[5:]}")
        ax.plot(tod, s.de_solar_MW / 1000, color=C2, ls=ls, lw=2 if ls == "-" else 1.2,
                label=f"Germany {day[5:]}")
    ax.axvspan(17.25, 19.5, color=BAND, alpha=0.6, lw=0)
    ax.text(17.3, 0.97, " ENTSO-E alert window\n 19:15-21:30 CEST", transform=ax.get_xaxis_transform(), va="top",
            fontsize=8, color=INK2)
    ax.set(title="12 August 2026: total eclipse over northern Spain at sunset (solid = eclipse day)",
           xlabel="hour of day (UTC)", ylabel="solar generation [GW]", xlim=(14, 20.5), ylim=(0, 32))
    ax.legend(ncol=2, fontsize=7, loc="lower left")
    save(fig, d / "plot_eclipse_examples.png")


# ------------------------------------------------------------------ 02 space weather
def plot_space_weather():
    d = ROOT / "02_space_weather"
    sw = pd.read_csv(d / "celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv", parse_dates=["date"])
    hp = pd.read_csv(d / "gfz_Hp30_2024-05-07_to_14_gannon_storm.csv", parse_dates=["datetime_utc"])

    fig, axes = plt.subplots(3, 1, figsize=(8, 8.5))
    ax = axes[0]
    m = sw.set_index("date").sunspot_number_isn.rolling(81, center=True).mean()
    ax.plot(m.index, m.values, color=C4, lw=1.6)
    ax.set(title="Daily sunspot number (81-day mean): the ~11-year solar cycle", ylabel="ISN")
    ax = axes[1]
    ax.plot(sw.date, sw.ap_daily, color=C1, lw=0.6)
    for dt, lab in [("1989-03-13", "13 Mar 1989\nQuebec blackout"), ("2003-10-29", "29-30 Oct 2003\n'Halloween' storms"),
                    ("2024-05-11", "10-11 May 2024\n'Gannon' storm"), ("1960-11-13", "13 Nov 1960")]:
        v = sw.loc[sw.date == dt, "ap_daily"].iloc[0]
        ax.annotate(lab, (pd.Timestamp(dt), v), xytext=(6, -2), textcoords="offset points", fontsize=7.5, color=INK2,
                    va="top")
    ax.set(title="Daily Ap index 1957-2025: the largest geomagnetic storms are rare, labelled events", ylabel="Ap")
    ax = axes[2]
    ax.plot(hp.datetime_utc, hp.Hp30, color=C1, lw=1.6, drawstyle="steps-post")
    ax.axhline(9, color=INK2, lw=0.8)
    ax.text(hp.datetime_utc.iloc[2], 9.15, "Hp = 9 (Kp scale ceiling); Hp30 is open-ended", fontsize=7.5, color=INK2)
    band(ax, "2024-05-10 16:30", "2024-05-11 03:30")
    ax.axvline(pd.Timestamp("2024-05-10 22:54"), color=INK2, lw=0.8)
    ax.text(pd.Timestamp("2024-05-11 05:00"), 11.2, "NOAA SWPC: G5 (extreme) first\nobserved 22:54 UTC, 10 May", fontsize=7.5,
            color=INK2, va="top")
    ax.set(title="GFZ Hp30 (30-min) during the May 2024 storm", ylabel="Hp30")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    save(fig, d / "plot_space_weather.png")


def similarity_search_demo():
    """Query-by-example: find the historical 3-hour Kp windows most similar to the Gannon storm."""
    import stumpy
    d = ROOT / "02_space_weather"
    sw = pd.read_csv(d / "celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv", parse_dates=["date"])
    kcols = [c for c in sw.columns if c.startswith("kp_") and c.endswith("UT")]
    long = sw.melt(id_vars="date", value_vars=kcols, var_name="slot", value_name="kp")
    long["t"] = long.date + pd.to_timedelta(long.slot.str[3:5].astype(int), unit="h")
    long = long.sort_values("t").reset_index(drop=True)
    x = long.kp.to_numpy(float)
    q_start = long.index[long.t == pd.Timestamp("2024-05-10 12:00")][0]
    m = 24  # 24 x 3 h = 3 days
    q = x[q_start:q_start + m]
    dist = stumpy.mass(q, x, normalize=False)  # raw distance: storm *magnitude* matters
    order = np.argsort(dist)
    hits, used = [], []
    for i in order:
        if any(abs(i - j) < m for j in used):
            continue
        used.append(i)
        hits.append({"window_start_utc": long.t[i], "distance": round(float(dist[i]), 2),
                     "max_kp": float(x[i:i + m].max()), "is_query": i == q_start})
        if len(hits) == 11:
            break
    res = pd.DataFrame(hits)
    res.to_csv(d / "similarity_search_gannon_top10.csv", index=False)
    print(res.to_string(index=False))
    return res


# --------------------------------------------------------------------- 03 grid
def plot_grid():
    d = ROOT / "03_power_grid"
    es = pd.read_csv(d / "energy_charts_ES_2025-04-27_to_29_iberian_blackout_15min.csv", parse_dates=["timestamp_utc"])
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for col, c, lab in [("load_MW", INK, "load (missing after collapse)"), ("solar_MW", C4, "solar"),
                        ("nuclear_MW", C1, "nuclear"), ("fossil_gas_MW", C2, "fossil gas"),
                        ("hydro_water_reservoir_MW", C3, "hydro reservoir")]:
        ax.plot(es.timestamp_utc, es[col] / 1000, color=c, label=lab, lw=1.6)
    ax.axvline(pd.Timestamp("2025-04-28 10:33"), color=INK2, lw=0.8)
    ax.text(pd.Timestamp("2025-04-28 10:50"), 26, "12:33 CEST: Iberian system\nloses synchronism (ENTSO-E)", fontsize=8,
            color=INK2, va="top")
    ax.set(title="Spain, 27-29 April 2025: the Iberian blackout in public generation data", ylabel="GW")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    ax.legend(ncol=3, fontsize=7.5, loc="upper left", bbox_to_anchor=(0, -0.15))
    save(fig, d / "plot_iberian_blackout.png")


# --------------------------------------------------------------------- 04 NAB
NYC_EVENTS = [("2014-11-02", "NYC Marathon"), ("2014-11-27", "Thanksgiving"), ("2014-12-25", "Christmas"),
              ("2015-01-01", "New Year"), ("2015-01-26", "Blizzard 'Juno'\n(travel ban)")]


def plot_nab():
    import json
    d = ROOT / "04_nab_known_causes"
    s = pd.read_csv(d / "nyc_taxi.csv", parse_dates=["timestamp"])
    w = json.load(open(d / "nab_anomaly_windows_realKnownCause.json"))["realKnownCause/nyc_taxi.csv"]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(s.timestamp, s.value / 1000, color=C1, lw=0.5)
    for k, ((a, b), (_, lab)) in enumerate(zip(w, NYC_EVENTS)):
        band(ax, a, b)
        ax.text(pd.Timestamp(a), 0.98 if k % 2 == 0 else 0.86, lab, transform=ax.get_xaxis_transform(), fontsize=7.5,
                color=INK2, va="top")
    ax.set(title="NAB nyc_taxi: passengers per 30 min; grey = labelled anomaly windows", ylabel="thousand passengers",
           xlim=(pd.Timestamp("2014-10-01"), pd.Timestamp("2015-02-01")))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    save(fig, d / "plot_nyc_taxi.png")


def discord_demo():
    """Unsupervised check: do matrix-profile discords land on the labelled NYC events?"""
    import stumpy
    d = ROOT / "04_nab_known_causes"
    s = pd.read_csv(d / "nyc_taxi.csv", parse_dates=["timestamp"])
    m = 48  # one day of 30-min buckets
    mp = stumpy.stump(s.value.astype(float).to_numpy(), m)
    prof = mp[:, 0].astype(float)
    out = []
    for _ in range(6):
        i = int(np.nanargmax(prof))
        out.append({"discord_day_start": s.timestamp[i], "mp_distance": round(prof[i], 2)})
        prof[max(0, i - m):i + m] = -np.inf
    res = pd.DataFrame(out)
    res.to_csv(d / "matrix_profile_top_discords.csv", index=False)
    print(res.to_string(index=False))


# --------------------------------------------------------------------- 05 ECG
def plot_ecg():
    import wfdb
    d = ROOT / "05_ecg_mitbih"
    rec = wfdb.rdrecord(str(d / "mitdb_record_100" / "100"))
    ann = wfdb.rdann(str(d / "mitdb_record_100" / "100"), "atr")
    fs = rec.fs
    centre = 2044  # first 'A' (atrial premature) beat in record 100
    a, b = centre - 4 * fs, centre + 6 * fs
    t = np.arange(a, b) / fs
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.plot(t, rec.p_signal[a:b, 0], color=C1, lw=1.0)
    for smp, sym in zip(ann.sample, ann.symbol):
        if a <= smp < b and sym in "NAV":
            ax.text(smp / fs, 1.25 if sym == "N" else 1.45, sym, ha="center", fontsize=8 if sym == "N" else 10,
                    color=INK2 if sym == "N" else C2, fontweight="normal" if sym == "N" else "bold")
    ax.set(title="MIT-BIH record 100 (lead MLII): cardiologist labels, 'A' = atrial premature beat",
           xlabel="time [s]", ylabel="mV", ylim=(-0.9, 1.6))
    save(fig, d / "plot_ecg_record100.png")


# ---------------------------------------------------------------- 06 pageviews
def plot_pageviews():
    d = ROOT / "06_wikipedia_pageviews"
    pv = pd.read_csv(d / "wikipedia_pageviews_aurora_2024-04_to_11.csv", parse_dates=["date"])
    sw = pd.read_csv(ROOT / "02_space_weather" / "celestrak_kp_ap_sunspots_f107_daily_1957-2025.csv", parse_dates=["date"])
    sw = sw[(sw.date >= pv.date.min()) & (sw.date <= pv.date.max())]
    fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    axes[0].plot(pv.date, pv.en_Aurora_views / 1000, color=C1, label="en: Aurora")
    axes[0].plot(pv.date, pv.pl_Zorza_polarna_views / 1000, color=C2, label="pl: Zorza polarna")
    axes[0].set(title="Wikipedia daily page views (users)", ylabel="thousand views")
    axes[0].legend()
    axes[1].plot(sw.date, sw.ap_daily, color=C3)
    axes[1].set(title="Daily Ap geomagnetic index (CelesTrak / GFZ) - data ends 20 Jul 2025 in this file", ylabel="Ap")
    for ax in axes:
        band(ax, "2024-05-10", "2024-05-12")
        band(ax, "2024-10-10", "2024-10-12")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    save(fig, d / "plot_aurora_pageviews_vs_ap.png")


# ------------------------------------------------------------- 07 pressure wave
def plot_pressure():
    d = ROOT / "07_atmosphere_pressure_wave"
    p = pd.read_csv(d / "iem_asos_1min_DSM_pressure_2022-01-15_hunga_tonga.csv", parse_dates=["timestamp_utc"])
    p["hpa"] = p.pres1_inHg * 33.8639
    p["anom"] = p.hpa - p.hpa.rolling(121, center=True, min_periods=60).mean()
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(p.timestamp_utc, p.anom, color=C1, lw=1.0)
    band(ax, "2022-01-15 13:45", "2022-01-15 14:45", "1st pass (direct path)")
    band(ax, "2022-01-16 06:40", "2022-01-16 07:40", "2nd pass (antipodal path)")
    ax.set(title="Des Moines (ASOS 1-min): pressure minus 2-h running mean; Hunga Tonga erupted 15 Jan ~04:15 UTC",
           ylabel="hPa")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    save(fig, d / "plot_hunga_tonga_pressure.png")


# ----------------------------------------------------------------- 08 air quality
def plot_air():
    d = ROOT / "08_air_quality_pl"
    a = pd.read_csv(d / "gios_pm_hourly_waw_krk_2024-12-28_to_2025-01-04.csv", parse_dates=["datetime_CET"])
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(a.datetime_CET, a.waw_niepodleglosci_pm25, color=C1, label="Warszawa, Al. Niepodległości")
    ax.plot(a.datetime_CET, a.krk_krasinskiego_pm25, color=C2, label="Kraków, Al. Krasińskiego")
    band(ax, "2024-12-31 23:30", "2025-01-01 02:00", "New Year fireworks")
    band(ax, "2024-12-29 12:00", "2024-12-30 06:00", "evening smog\nepisode (Kraków)", y=0.16)
    ax.set(title="Hourly PM2.5 (GIOŚ): a 1-hour fireworks spike vs. a multi-hour smog build-up", ylabel="µg/m³")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.legend(loc="upper right")
    save(fig, d / "plot_pm25_new_year.png")


# -------------------------------------------------------------------- 09 hydro
def plot_hydro():
    d = ROOT / "09_hydrology_pl"
    h = pd.read_csv(d / "imgw_hydro_daily_HY2024_odra_nysa_flood.csv", parse_dates=["date"])
    h = h[(h.date >= "2024-09-05") & (h.date <= "2024-10-05")]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for col, c, lab in [("glucholazy_level_cm", C5, "Głuchołazy (Biała Głuchołaska)"),
                        ("klodzko_level_cm", C1, "Kłodzko (Nysa Kłodzka)"),
                        ("nysa_level_cm", C2, "Nysa (Nysa Kłodzka)"),
                        ("raciborz_miedonia_level_cm", C3, "Racibórz-Miedonia (Odra)"),
                        ("opole_groszowice_level_cm", C4, "Opole-Groszowice (Odra)"),
                        ("brzeg_dolny_level_cm", "#6250d6", "Brzeg Dolny (Odra)")]:
        ax.plot(h.date, h[col], color=c, label=lab, marker="o", ms=3)
    ax.set(title="Daily mean water level, September 2024 flood: the wave travels downstream (IMGW)", ylabel="cm")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.legend(fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.12))
    save(fig, d / "plot_flood_wave_sep2024.png")


# ------------------------------------------------------------------ 11 UCR
def plot_ucr():
    d = ROOT / "11_benchmarks_ucr_tsb"
    u = pd.read_csv(d / "135_UCR_Anomaly_InternalBleeding16_TEST.csv")
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.plot(u.timestamp, u.value, color=C1, lw=0.8)
    an = u[u.is_anomaly == 1]
    ax.axvspan(an.timestamp.min(), an.timestamp.max(), color=BAND, alpha=0.8, lw=0)
    ax.set(title="UCR anomaly archive #135 InternalBleeding16 (test part, grey = labelled anomaly)",
           xlim=(3500, 5000))
    save(fig, d / "plot_ucr_135.png")


if __name__ == "__main__":
    plot_eclipse()
    plot_space_weather()
    similarity_search_demo()
    plot_grid()
    plot_nab()
    discord_demo()
    plot_ecg()
    plot_pageviews()
    plot_pressure()
    plot_air()
    plot_hydro()
    plot_ucr()
