"""Buduje zestaw zdarzeń ewaluacyjnych (warianty A/B/C) z katalogów pobranych na laptopie Arka."""
import sys
import numpy as np
import pandas as pd

D = sys.argv[1]  # .../space_weather_decision
OUT = sys.argv[2]
SEED = 2026
TEST_START = pd.Timestamp("2025-01-01")
FD_START = pd.Timestamp("2024-03-01")      # NOAA Forecast Discussion
DONKI_LIVE = pd.Timestamp("2020-06-01")    # M2M katalog na bieżąco
RC_END = pd.Timestamp("2026-07-06 15:00")  # ostatni icme_end w liście R-C (rew. 23.07.2026)
SSC_END = pd.Timestamp("2026-08-11 11:26")
START = pd.Timestamp("2010-04-01")
DATA_END = pd.Timestamp("2026-10-09 23:59")

storms = pd.read_csv(f"{D}/results/storm_events_kp_1957_2026_with_catalogue_links.csv",
                     parse_dates=["onset", "peak_time", "end"])
storms = storms[storms.onset >= START].reset_index(drop=True)
kp = pd.read_csv(f"{D}/results/kp_ap_Ap_SN_F107_daily_1957-10-01_to_2026-10-09_merged.csv.gz", parse_dates=["date"])
kcols = [c for c in kp.columns if c.startswith("kp_")]
kp3 = kp.melt(id_vars="date", value_vars=kcols, var_name="h", value_name="kp")
kp3["t"] = kp3.date + pd.to_timedelta(kp3.h.str[3:5].astype(int), unit="h")
kp3 = kp3.set_index("t").kp.sort_index()
kp["kpmax"] = kp[kcols].max(axis=1)

def ts(s):
    return pd.to_datetime(s.str.replace("Z", "", regex=False), errors="coerce")

rc = pd.read_csv(f"{D}/data/richardson_cane_icme_1996_to_2026.csv")
for c in ["disturbance_time", "icme_start", "icme_end"]:
    rc[c] = pd.to_datetime(rc[c], errors="coerce")
ssc = pd.read_csv(f"{D}/data/isgi_ssc_1957_to_2026.csv")
ssc["t"] = pd.to_datetime(ssc.datetime_utc)
ssc["typ"] = ssc.type.fillna("SSC")
gst = pd.read_csv(f"{D}/data/donki_gst_2010-01-01_to_2026-10-09.csv")
gst["t"] = ts(gst.start_time)
cme = pd.read_csv(f"{D}/data/donki_cme_linked_to_gst.csv").set_index("activity_id")
ips = pd.read_csv(f"{D}/data/donki_ips_earth_2010-01-01_to_2026-10-09.csv")
ips["t"] = ts(ips.event_time)
sep = pd.read_csv(f"{D}/data/noaa_sep_events_1976_to_2026.csv")
sep["t"] = pd.to_datetime(sep.start_time)
sep["pfu"] = pd.to_numeric(sep.peak_pfu_gt10MeV.astype(str).str.replace(",", ""), errors="coerce")

def s_level(p):
    if pd.isna(p):
        return ""
    return "S5" if p >= 1e5 else "S4" if p >= 1e4 else "S3" if p >= 1e3 else "S2" if p >= 100 else "S1"

def fmt(t):
    return "" if pd.isna(t) else pd.Timestamp(t).strftime("%Y-%m-%d %H:%M")

def kp_str(v):
    if pd.isna(v):
        return ""
    base = int(np.floor(v + 1e-6 + 0.34))
    frac = v - base
    suf = "o" if abs(frac) < 0.15 else ("+" if frac > 0 else "-")
    return f"{base}{suf}"

# ---------- dopasowanie katalogów do okna ----------
def match(t_on, t_peak, t_end):
    r = {}
    w0, w1 = t_on - pd.Timedelta(hours=24), t_peak
    s = ssc[(ssc.t >= w0) & (ssc.t <= w1 + pd.Timedelta(hours=3))]
    s_ssc = s[s.typ == "SSC"]
    pool = s_ssc if len(s_ssc) else s
    if len(pool):
        before = pool[pool.t <= t_on + pd.Timedelta(hours=3)]
        row = before.iloc[-1] if len(before) else pool.iloc[0]
        r["ssc"] = fmt(row.t)
        r["ssc_typ"] = row.typ
        others = [f"{fmt(x.t)} ({x.typ})" for _, x in s.iterrows() if x.t != row.t]
        r["ssc_all"] = "; ".join(others)
    else:
        r["ssc"] = "brak" if t_on <= SSC_END else "poza zasięgiem listy (do 2026-08-11)"
        r["ssc_typ"] = ""
        r["ssc_all"] = ""
    # Richardson-Cane: ICME, którego przedział [zaburzenie, koniec ICME] obejmuje szczyt lub nachodzi na okno
    r["rc_dist"] = pd.NaT
    rr = rc[(rc.disturbance_time <= t_end) & (rc.icme_end >= t_on - pd.Timedelta(hours=12))]
    covers = rr[(rr.disturbance_time <= t_peak + pd.Timedelta(hours=3)) & (rr.icme_end >= t_peak)]
    if len(covers):
        x = covers.sort_values("disturbance_time").iloc[-1]
        part = "osłona (sheath)" if t_peak < x.icme_start else "ejekta ICME"
        mc = " (obłok magnetyczny)" if str(x.mc) == "2" else ""
        r["rc"] = f"zaburzenie {fmt(x.disturbance_time)}; ICME {fmt(x.icme_start)}–{fmt(x.icme_end)}; Dst {x.dst_min_nT} nT{mc}"
        r["rc_cls"] = f"CME – {part}"
        r["rc_dist"] = x.disturbance_time
    elif len(rr):
        x = rr.iloc[0]
        r["rc"] = f"ICME częściowo w oknie: {fmt(x.icme_start)}–{fmt(x.icme_end)}; Dst {x.dst_min_nT} nT"
        r["rc_cls"] = "CME (częściowo w oknie)"
    elif t_end <= RC_END:
        r["rc"] = "brak ICME"
        r["rc_cls"] = "nie-CME"
    else:
        r["rc"] = "poza zasięgiem listy (do 07/2026)"
        r["rc_cls"] = ""
    # DONKI GST
    g = gst[(gst.t >= t_on - pd.Timedelta(hours=12)) & (gst.t <= t_end)]
    cm, hs, ip = [], [], []
    for _, x in g.iterrows():
        for c in str(x.linked_cme).split(";"):
            if c and c != "nan":
                cm.append(c)
        for c in str(x.linked_hss).split(";"):
            if c and c != "nan":
                hs.append(c)
    r["gst"] = "; ".join(g.gst_id) if len(g) else "brak"
    descr = []
    for c in dict.fromkeys(cm):
        if c in cme.index:
            x = cme.loc[c]
            ar = "" if pd.isna(x.active_region_num) else f", AR {int(x.active_region_num)}"
            src = "" if pd.isna(x.source_location) else f", {x.source_location}"
            descr.append(f"CME {c[:16]} {x.speed_kms:.0f} km/s{src}{ar}")
        else:
            descr.append(f"CME {c[:16]}")
    r["donki_cme"] = "; ".join(descr)
    r["donki_hss"] = "; ".join(h[:16] for h in dict.fromkeys(hs))
    ii = ips[(ips.t >= t_on - pd.Timedelta(hours=24)) & (ips.t <= t_peak + pd.Timedelta(hours=3))]
    r["donki_ips"] = "; ".join(fmt(t) for t in ii.t) if len(ii) else "brak"
    if cm and hs:
        r["donki_cls"] = "mieszana (CME + HSS)"
    elif cm:
        r["donki_cls"] = "CME"
    elif hs:
        r["donki_cls"] = "HSS/CIR"
    elif len(g):
        r["donki_cls"] = "GST bez powiązań"
    else:
        r["donki_cls"] = "brak GST"
    # SPE
    sp = sep[(sep.t >= t_on - pd.Timedelta(hours=72)) & (sep.t <= t_end)]
    if len(sp):
        x = sp.loc[sp.pfu.idxmax()]
        r["spe"] = f"{fmt(x.t)}, {x.pfu:.0f} pfu ({s_level(x.pfu)}), rozbłysk {x.flare_importance}"
        r["s_level"] = s_level(x.pfu)
    else:
        r["spe"] = "brak"
        r["s_level"] = ""
    return r

def key_cause(r):
    """Klucz przyczyny: R-C (niezależny) > DONKI (zależny od wejścia B/C)."""
    rcc, dc = r["rc_cls"], r["donki_cls"]
    if rcc.startswith("CME"):
        k, src = "CME", "Richardson-Cane"
        if dc == "mieszana (CME + HSS)" or (dc == "HSS/CIR"):
            k = "CME (+ HSS wg DONKI)"
    elif rcc == "nie-CME":
        k = "HSS/CIR" if dc in ("HSS/CIR", "mieszana (CME + HSS)") else "nie-CME (HSS/CIR prawdopodobny)"
        src = "Richardson-Cane (brak ICME) + DONKI HSS" if k == "HSS/CIR" else "Richardson-Cane (brak ICME)"
        if dc == "CME":
            k = "SPORNE: R-C brak ICME, DONKI CME"
    else:
        k = {"CME": "CME", "HSS/CIR": "HSS/CIR", "mieszana (CME + HSS)": "mieszana (CME + HSS)"}.get(dc, "nieustalona")
        src = "tylko DONKI (klucz zależny od wejścia B/C)"
    if r["s_level"]:
        k += f" + burza radiacyjna {r['s_level']}"
    return k, src

# ---------- skutki ----------
G_GNSS = {
    "G1": "Skala NOAA nie przewiduje skutków dla GNSS; w Polsce zwykle brak efektu (oczekiwany wynik: brak degradacji RTK).",
    "G2": "Skala NOAA nie przewiduje skutków dla GNSS; możliwy wzrost ROTI w wysokich szerokościach, w Polsce zwykle słaby.",
    "G3": "NOAA G3: „intermittent satellite navigation … problems may occur”. W Polsce możliwe przejścia RTK fixed→float, dłuższa inicjalizacja (ASG-EUPOS 29.10.2024).",
    "G4": "NOAA G4: „satellite navigation degraded for hours”. W Polsce oczekiwane utraty fixed RTK, błędy pozycji dm–m (ASG-EUPOS 29.10.2024).",
    "G5": "NOAA G5: „satellite navigation may be degraded for days”. Silna degradacja RTK/PPP w średnich szerokościach.",
}
G_SAT = {
    "G1": "NOAA G1: „minor impact on satellite operations possible”.",
    "G2": "NOAA G2: korekty orientacji; zmiana oporu atmosfery wpływa na prognozy orbit LEO.",
    "G3": "NOAA G3: ładowanie powierzchniowe, wzrost oporu dla LEO, korekty orientacji.",
    "G4": "NOAA G4: ładowanie powierzchniowe, problemy ze śledzeniem i orientacją; wyraźny wzrost oporu LEO.",
    "G5": "NOAA G5: rozległe ładowanie, problemy z orientacją, łącznością i śledzeniem satelitów.",
}
S_SAT = {
    "S1": "", "S2": " S2: pojedyncze zdarzenia SEU.",
    "S3": " S3: SEU, szum w detektorach, degradacja paneli.",
    "S4": " S4: problemy z pamięcią, szum w star trackerach, utrata orientacji.",
    "S5": " S5: możliwa utrata satelitów, trwałe uszkodzenia.",
}
SRC_SCALE = "NOAA Space Weather Scales (swpc.noaa.gov/noaa-scales-explanation); ASG-EUPOS „Uwaga na wpływ jonosfery…” 29.10.2024"

# Udokumentowane skutki dla wybranych zdarzeń (klucz: data szczytu YYYY-MM-DD lub onset)
DOC = {
    "2015-03-17": ("Silne nieregularności jonosfery (ROTI) w wysokich i średnich szerokościach; degradacja RTK i PPP w Norwegii.", "",
                   "Cherniak i in. 2015 (Space Weather, doi:10.1002/2015SW001237); Jacobsen i Andalsvik 2016 (JSWSC 6, A9)", "DO SPRAWDZENIA (źródło podane z wiedzy modelu)"),
    "2017-09-08": ("Rozbłyski X 6.09 i burza 7–8.09: zakłócenia GNSS i łączności HF.", "",
                   "Yasyukevich i in. 2018 (Space Weather 16, doi:10.1029/2018SW001932)", "DO SPRAWDZENIA (źródło podane z wiedzy modelu)"),
    "2022-02-03": ("", "38 z 49 nowo wystrzelonych satelitów Starlink spłonęło po burzy G1 (wzrost oporu na niskiej orbicie).",
                   "SpaceX 08.02.2022; Dang i in. 2022 (Space Weather, doi:10.1029/2022SW003152); CIRES/NOAA", "zweryfikowane (weryfikacja_maila.md)"),
    "2024-05-11": ("Błędy PPP do 70 m w środkowych USA; rolnicy w USA: błędy 3–9 m i przestoje RTK; straty kukurydzy 53 mln–1,29 mld USD (Griffin 2025).",
                   "Ok. 5000 satelitów (głównie Starlink) wykonało manewry; system unikania kolizji potrzebował ≥2 dni na restart.",
                   "Younas i in. 2025 (JGR Space Physics); ankieta NOAA 26.09.2024; Parker i Linares 2024; Griffin 2025 (poster SWW)", "zweryfikowane (weryfikacja_maila.md)"),
    "2024-10-10": ("ASG-EUPOS ostrzega przed wpływem jonosfery: fixed→float, przesunięcia od kilkunastu cm do kilku m, I95>4.", "",
                   "ASG-EUPOS, 29.10.2024 (bez wskazania konkretnej burzy)", "pobrane 11.10.2026"),
}

def effects(level, s_lvl, key_dates):
    gn, sat, src, status = G_GNSS.get(level, ""), G_SAT.get(level, ""), SRC_SCALE, "oczekiwane wg skali NOAA"
    if s_lvl:
        sat += S_SAT[s_lvl]
    for d in key_dates:
        if d in DOC:
            dg, ds, dsrc, dst = DOC[d]
            gn = (dg + " | " if dg else "") + gn
            sat = (ds + " | " if ds else "") + sat
            src = dsrc + "; " + src
            status = "udokumentowane: " + dst
    return gn, sat, src, status

MEASURE = ("GNSS: ROTI/TEC z IGS (IONEX, CDDIS) nad Polską; obserwacje EPN (np. BOGO, JOZE, WROC, LAMA) – błąd pozycji; "
           "wskaźnik I95 ASG-EUPOS. Satelity: TLE Space-Track (spadek wysokości/B* Starlink, LEO)")

def period(t):
    if t < DONKI_LIVE:
        return "P1: przed 06/2020 (DONKI retrospektywne)"
    if t < FD_START:
        return "P2: 06/2020–02/2024 (DONKI na żywo, bez Forecast Discussion)"
    return "P3: od 03/2024 (pełny korpus z Forecast Discussion)"

rows = []

def add(cat, onset, peak, end, level, kpmax, extra_key=None, key_src=None, note="", forced=False):
    r = match(onset, peak, end)
    k, ks = key_cause(r)
    if extra_key:
        k, ks = extra_key, key_src
    kd = {onset.strftime("%Y-%m-%d"), peak.strftime("%Y-%m-%d")}
    if level in G_GNSS:
        gn, sat, src, status = effects(level, r["s_level"], kd)
    else:
        gn, sat, src, status = "", "", "", ""
    rows.append(dict(
        kategoria=cat, zbior="TEST" if onset >= TEST_START else "DEV",
        okres_korpusu=period(onset),
        poczatek_utc=fmt(onset), szczyt_utc=fmt(peak), koniec_utc=fmt(end),
        t0_utc=fmt(onset + pd.Timedelta(hours=3)) if cat.startswith("Burza") else fmt(onset),
        kp_max=kp_str(kpmax) if not pd.isna(kpmax) else "", poziom=level,
        klucz_przyczyna=k, klucz_zrodlo=ks,
        moment_klucz=(f"{r['ssc']} (ISGI {r['ssc_typ']})" if r["ssc_typ"] else (f"{fmt(r['rc_dist'])} (R-C zaburzenie)" if not pd.isna(r["rc_dist"]) else "brak wstrząsu w kluczu")),
        rc_icme=r["rc"], ssc_isgi=r["ssc"] + (f" ({r['ssc_typ']})" if r["ssc_typ"] and r["ssc_typ"] != "SSC" else ""),
        ssc_inne_w_oknie=r["ssc_all"], donki_gst=r["gst"], donki_cme=r["donki_cme"], donki_hss=r["donki_hss"], donki_ips=r["donki_ips"],
        donki_klasa=r["donki_cls"], spe=r["spe"],
        skutek_gnss=gn, skutek_satelity=sat, skutek_zrodlo=src, skutek_status=status,
        pomiar_skutku=MEASURE if cat != "Zagłuszanie GNSS (kontrprzykład)" else "rtgms.pl (archiwum stacji ASG-EUPOS), GPSJam; ROTI IGS jako kontrola (oczekiwane: spokojna jonosfera)",
        noaa_forecast_discussion="tak" if onset >= FD_START else "nie (przed 03/2024)",
        wymuszone=("tak" if forced else ""), uwagi=note))

# 1) wszystkie G3+
for _, s in storms[storms.level.isin(["G3", "G4", "G5"])].iterrows():
    v = kp3[s.onset:s.end].max()
    note = ""
    if s.onset.strftime("%Y-%m-%d") == "2024-05-10":
        note = "Studium przypadku (Gannon). LLM prawdopodobnie zna to zdarzenie z treningu."
    if s.onset.strftime("%Y-%m-%d") == "2026-01-19":
        note = "Burza geomagnetyczna G4 + burza radiacyjna S4 (37 000 pfu) – test dla operatorów satelitów."
    add(f"Burza {s.level}", s.onset, s.peak_time, s.end, s.level, v, note=note)

# 2) próbka G1–G2 + Starlink 2022
rng = np.random.default_rng(SEED)
weak = storms[storms.level.isin(["G1", "G2"])].copy()
weak = weak[~weak.onset.dt.strftime("%Y-%m-%d").isin(["2022-02-03", "2022-02-04"])]
pick = []
for split, n in (("DEV", 10), ("TEST", 6)):
    sub = weak[(weak.onset >= TEST_START) if split == "TEST" else (weak.onset < TEST_START)]
    for lv in ("G1", "G2"):
        cand = sub[sub.level == lv]
        pick.append(cand.sample(n=min(n, len(cand)), random_state=int(rng.integers(1e9))))
for _, s in pd.concat(pick).sort_values("onset").iterrows():
    add(f"Burza {s.level}", s.onset, s.peak_time, s.end, s.level, kp3[s.onset:s.end].max())
add("Burza G1", pd.Timestamp("2022-02-03 06:00"), pd.Timestamp("2022-02-03 09:00"), pd.Timestamp("2022-02-04 21:00"), "G1",
    kp3["2022-02-03 06:00":"2022-02-04 21:00"].max(),
    note="Dwa epizody G1 (3 i 4.02) połączone; start Starlink 3.02 18:13 UTC.", forced=True)

# 3) dni spokojne
kp_idx = kp.set_index("date").kpmax
quiet = []
for d, v in kp_idx[START:DATA_END].items():
    if v <= 2.34 and kp_idx[d - pd.Timedelta(days=3): d + pd.Timedelta(days=3)].max() < 4.6:
        quiet.append(d)
quiet = pd.Series(quiet)
for split, n in (("DEV", 14), ("TEST", 8)):
    sub = quiet[(quiet >= TEST_START) if split == "TEST" else (quiet < TEST_START)]
    for d in sub.sample(n=n, random_state=int(rng.integers(1e9))).sort_values():
        add("Dzień spokojny (fałszywy alarm)", d, d + pd.Timedelta(hours=12), d + pd.Timedelta(hours=23, minutes=59), "brak",
            kp_idx[d], extra_key="brak zdarzenia (Kp ≤ 2+, ±3 dni bez Kp ≥ 5-)", key_src="GFZ Kp")

# 4) fala/impuls bez burzy
si = ssc[(ssc.t >= START) & (ssc.typ.isin(["SI", "SSC"]))].copy()
def no_storm(t):
    return kp3[t - pd.Timedelta(hours=3): t + pd.Timedelta(hours=48)].max() < 4.6
si = si[si.t.apply(no_storm)]
for split, n in (("DEV", 7), ("TEST", 5)):
    sub = si[(si.t >= TEST_START) if split == "TEST" else (si.t < TEST_START)]
    for _, x in sub.sample(n=min(n, len(sub)), random_state=int(rng.integers(1e9))).sort_values("t").iterrows():
        t = x.t
        add("Impuls/fala bez burzy (fałszywy alarm)", t, t, t + pd.Timedelta(hours=48), "brak",
            kp3[t - pd.Timedelta(hours=3): t + pd.Timedelta(hours=48)].max(),
            extra_key=f"wstrząs/impuls ({x.typ}) bez burzy – system nie powinien zapowiadać burzy",
            key_src="ISGI SSC/SI + GFZ Kp")

# 5) zagłuszanie
JAM = [
    ("2023-12-25 00:00", "2023-12-28 23:59", "N i NE Polska, Bałtyk", "Zagłuszanie GPS widoczne w GPSJam; NOTAM 25–27.12; GUGiK: brak wpływu na ASG-EUPOS, zakłócenia na wysokościach lotniczych.",
     "Geoforum.pl 27.12.2023 (aktualizacja z komunikatem GUGiK 28.12.2023); geoportal.gov.pl/aktualnosci/zaklocenia-systemu-gps-na-terytorium-polski", "dzień"),
    ("2024-02-19 00:00", "2024-02-26 23:59", "stacja ASG-EUPOS Zamość", "Spadek liczby śledzonych satelitów GPS i Galileo na stacji Zamość. Komunikat wspomina też aktywność Słońca, ale nie wskazuje przyczyny – przypadek niejednoznaczny.",
     "GUGiK, geoportal.gov.pl/aktualnosci/zaklocenia-systemow-gnss-na-terytorium-polski (26.02.2024)", "przybliżona (komunikat: „w ostatnim czasie”)"),
    ("2024-03-13 00:00", "2024-03-13 23:59", "N Polska, S Szwecja", "Jednodniowe zakłócenia GPS (GPSJam); samolot RAF z ministrem Shappsem ok. 30 min bez GPS.",
     "zaufanatrzeciastrona.pl 29.11.2025 (za GPSJam/ADS-B Exchange)", "dzień"),
    ("2025-06-14 00:00", "2025-06-15 23:59", "Hel, Trójmiasto", "Upadki dronów do Bałtyku, pojazdy na mapach w morzu; PAŻP: ostrzeżenie NW „ZAKLOCENIA GPS” dla całej Polski (NOTAM M0520/25). Zbiega się z końcem burzy G3 11–14.06 i ćwiczeniami BALTOPS 25.",
     "zaufanatrzeciastrona.pl 29.11.2025; swiatdronow.pl 16.06.2025", "dzień"),
    ("2026-05-01 00:00", "2026-06-30 23:59", "Pomorze (stacja IŁ-PIB Gdańsk)", "Wielogodzinne zakłócenia wszystkich pasm GNSS w ok. 70% dni maja i czerwca. OKRES, nie zdarzenie: konkretne dni wybrać z rtgms.pl.",
     "IŁ-PIB 27.08.2026; naukawpolsce.pl 10.09.2026", "okres – do rozbicia na dni"),
    ("2026-06-30 00:00", "2026-06-30 23:59", "stacja ASG-EUPOS Siedlce", "Komunikat GUGiK wskazany we wcześniejszej weryfikacji maila; dziś nie udało się go ponownie odnaleźć.",
     "weryfikacja_maila.md (pkt 2.10) – do potwierdzenia", "do potwierdzenia"),
    ("2026-07-01 00:00", "2026-07-31 23:59", "Pomorze", "Ok. 90 h zakłóceń pasma L1 w lipcu (12–20% miesiąca). OKRES – dni z rtgms.pl.",
     "Euronews 25.08.2026 (za IŁ-PIB/PAP)", "okres – do rozbicia na dni"),
    ("2026-08-01 00:00", "2026-08-19 23:59", "Pomorze", "Całkowite zakłócenia w 63% dni 1–19.08. OKRES – dni z rtgms.pl.",
     "IŁ-PIB 27.08.2026", "okres – do rozbicia na dni"),
    ("2026-08-21 00:00", "2026-08-21 23:59", "Bałtyk (ORP Albatros)", "Zagłuszanie GPS na okręcie ORP Albatros podczas operacji NATO.",
     "Euronews 25.08.2026 (za JFC Brunssum)", "dzień"),
]
for a, b, where, what, src, prec in JAM:
    t0, t1 = pd.Timestamp(a), pd.Timestamp(b)
    v = kp3[t0:t1].max()
    is_period = prec.startswith("okres")
    mixed = v >= 4.6 and not is_period
    key = "nie pogoda kosmiczna (zagłuszanie)"
    if is_period:
        key = "nie pogoda kosmiczna (zagłuszanie); dni z Kp ≥ 5- w tym okresie oznaczyć jako mieszane"
    if "Zamość" in where:
        key = "nie pogoda kosmiczna (Kp ≤ 3; źródło zakłóceń nieustalone)"
    if mixed:
        key = f"zagłuszanie przy jednoczesnej aktywności geomagnetycznej (Kp max {kp_str(v)}) – przypadek mieszany"
    add("Zagłuszanie GNSS (kontrprzykład)", t0, t0, t1, ("okres" if is_period else "brak") if not mixed else f"Kp {kp_str(v)}", v,
        extra_key=key, key_src=src, note=f"{where}. {what} Precyzja daty: {prec}.")
    rows[-1]["skutek_gnss"] = what
    rows[-1]["skutek_zrodlo"] = src
    rows[-1]["skutek_status"] = "udokumentowane (komunikat/prasa)"

df = pd.DataFrame(rows)
order = {"Burza G5": 0, "Burza G4": 1, "Burza G3": 2, "Burza G2": 3, "Burza G1": 4}
df["_o"] = df.kategoria.map(order).fillna(9)
df = df.sort_values(["poczatek_utc"]).reset_index(drop=True)
pref = {"Burza": "B", "Dzień": "Q", "Impuls/fala": "F", "Zagłuszanie": "J"}
df.insert(0, "id", [f"{pref[c.split()[0]]}{i+1:03d}" for i, c in enumerate(df.kategoria)])
df = df.drop(columns="_o")
df.to_csv(OUT, index=False)
print(df.groupby(["kategoria", "zbior"]).size().unstack(fill_value=0))
print(df.klucz_przyczyna.value_counts().head(20))
