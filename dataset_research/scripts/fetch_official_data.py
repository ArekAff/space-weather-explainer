"""
Download more data from the official open sources used for the samples.

All endpoints below were checked by hand on 2026-10-10 and returned the formats the code expects.
This script itself was written in an environment without access to those hosts, so run a small
request first and look at the output before launching large downloads.

    pip install requests pandas
    python scripts/fetch_official_data.py energy_charts --country de --start 2015-03-01 --end 2015-03-31
    python scripts/fetch_official_data.py gfz --index Hp30 --start 2024-10-01 --end 2024-10-31
    python scripts/fetch_official_data.py pageviews --project en.wikipedia --article Aurora --start 20150701 --end 20251231
    python scripts/fetch_official_data.py iem --station DSM --vars pres1 --start 2022-01-15T00:00 --end 2022-01-17T00:00
    python scripts/fetch_official_data.py gios_stations
    python scripts/fetch_official_data.py gios --sensor 3585 --start "2024-01-01 00:00" --end "2024-12-31 23:00"
    python scripts/fetch_official_data.py imgw_hydro --year 2024
    python scripts/fetch_official_data.py pse --start 2025-01-01 --end 2025-01-31

Files are written to ./downloads/. Respect each provider's terms (see README.md, section "Licences").
"""
import argparse
import io
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

OUT = Path("downloads")
OUT.mkdir(exist_ok=True)
# Wikimedia asks for a descriptive User-Agent with contact details. Put your own e-mail here.
HEADERS = {"User-Agent": "space-weather-explainer-research/0.1 (contact: SET-YOUR-EMAIL)"}


def _get(url, **kw):
    r = requests.get(url, headers=HEADERS, timeout=120, **kw)
    r.raise_for_status()
    return r


# ---------------------------------------------------------------- Energy-Charts (Fraunhofer ISE)
def energy_charts(country, start, end):
    """Public net electricity generation and load, 15-min/hourly. Credit: Energy-Charts / Fraunhofer ISE."""
    j = _get("https://api.energy-charts.info/public_power",
             params={"country": country, "start": start, "end": end}).json()
    df = pd.DataFrame({p["name"]: p["data"] for p in j["production_types"]})
    df.insert(0, "timestamp_utc", pd.to_datetime(j["unix_seconds"], unit="s", utc=True))
    f = OUT / f"energy_charts_{country}_{start}_{end}.csv"
    df.to_csv(f, index=False)
    return f


# ---------------------------------------------------------------- GFZ Potsdam geomagnetic indices
def gfz(index, start, end):
    """index: Kp, ap, Ap, Hp30, Hp60, ap30, ap60, SN, Fobs, Fadj ... Licence CC BY 4.0 (GFZ Potsdam)."""
    j = _get("https://kp.gfz.de/app/json/",
             params={"start": f"{start}T00:00:00Z", "end": f"{end}T23:59:59Z", "index": index}).json()
    df = pd.DataFrame({"datetime_utc": j["datetime"], index: j[index]})
    f = OUT / f"gfz_{index}_{start}_{end}.csv"
    df.to_csv(f, index=False)
    return f


# ---------------------------------------------------------------- Wikimedia page views (CC0)
def pageviews(project, article, start, end, agent="user"):
    art = requests.utils.quote(article.replace(" ", "_"), safe="")
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/"
           f"{agent}/{art}/daily/{start}/{end}")
    items = _get(url).json()["items"]
    df = pd.DataFrame({"date": [pd.to_datetime(i["timestamp"][:8]) for i in items],
                       "views": [i["views"] for i in items]})
    f = OUT / f"pageviews_{project}_{art}_{start}_{end}.csv"
    df.to_csv(f, index=False)
    return f


# ---------------------------------------------------------------- Iowa Environmental Mesonet ASOS 1-min
def iem(station, vars_, start, end):
    """US ASOS 1-minute data (public domain). vars: pres1, tmpf, dwpf, sknt, drct, precip ..."""
    r = _get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py",
             params={"station": station, "vars": vars_, "sts": start + "Z", "ets": end + "Z",
                     "sample": "1min", "what": "download", "tz": "UTC"})
    f = OUT / f"iem_asos1min_{station}_{start[:10]}_{end[:10]}.csv".replace(":", "")
    f.write_text(r.text)
    return f


# ---------------------------------------------------------------- GIOŚ air quality (Poland)
GIOS = "https://api.gios.gov.pl/pjp-api/v1/rest"


def _gios_list(j):
    return next(v for v in j.values() if isinstance(v, list))


def gios_stations():
    rows = _gios_list(_get(f"{GIOS}/station/findAll", params={"page": 0, "size": 500}).json())
    df = pd.DataFrame(rows)
    sensors = []
    for sid in df["Identyfikator stacji"]:
        try:
            sensors += _gios_list(_get(f"{GIOS}/station/sensors/{sid}", params={"page": 0, "size": 50}).json())
        except Exception as e:  # keep going if one station fails
            print("station", sid, e)
        time.sleep(0.2)
    f1, f2 = OUT / "gios_stations.csv", OUT / "gios_sensors.csv"
    df.to_csv(f1, index=False)
    pd.DataFrame(sensors).to_csv(f2, index=False)
    return f1, f2


def gios(sensor, start, end):
    """Hourly archival data for one sensor; the API allows <= 366 days per call, so we chunk."""
    t0, t1 = datetime.fromisoformat(start), datetime.fromisoformat(end)
    out = []
    while t0 <= t1:
        t_end = min(t0 + timedelta(days=360), t1)
        page = 0
        while True:
            j = _get(f"{GIOS}/archivalData/getDataBySensor/{sensor}",
                     params={"dateFrom": t0.strftime("%Y-%m-%d %H:%M"), "dateTo": t_end.strftime("%Y-%m-%d %H:%M"),
                             "page": page, "size": 500}).json()
            out += _gios_list(j)
            page += 1
            if page >= j.get("totalPages", 1):
                break
            time.sleep(0.2)
        t0 = t_end + timedelta(hours=1)
    df = pd.DataFrame(out)
    f = OUT / f"gios_sensor{sensor}_{start[:10]}_{end[:10]}.csv"
    df.to_csv(f, index=False)
    return f


# ---------------------------------------------------------------- IMGW-PIB hydrology (Poland)
def imgw_hydro(year):
    """Daily water level / discharge / temperature for all gauges, one hydrological year (Nov..Oct).
    Attribution required: 'Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – PIB'."""
    base = "https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_hydrologiczne/dobowe"
    listing = _get(f"{base}/{year}/").text
    zips = sorted(set(p for p in listing.split('"') if p.startswith("codz_") and p.endswith(".zip")))
    frames = []
    for z in zips:
        content = zipfile.ZipFile(io.BytesIO(_get(f"{base}/{year}/{z}").content))
        for name in content.namelist():
            raw = content.read(name)
            try:
                txt = raw.decode("utf-8")
            except UnicodeDecodeError:
                txt = raw.decode("cp1250")
            rows = [l.replace('"', "").split(",") for l in txt.splitlines() if l.strip()]
            frames.append(pd.DataFrame([r[:10] for r in rows if len(r) >= 10]))
    df = pd.concat(frames, ignore_index=True)
    df.columns = ["station_code", "station_name", "river", "hydro_year", "hydro_month_idx", "day",
                  "level_cm", "flow_m3s", "water_temp_C", "calendar_month"]
    hy, cm, d = df.hydro_year.astype(int), df.calendar_month.astype(int), df.day.astype(int)
    df.insert(0, "date", pd.to_datetime(dict(year=hy.where(cm < 11, hy - 1), month=cm, day=d), errors="coerce"))
    for c, bad in [("level_cm", "9999"), ("flow_m3s", "99999.999"), ("water_temp_C", "99.9")]:
        df[c] = pd.to_numeric(df[c].replace({bad: None, "NULL": None, "": None}), errors="coerce")
    f = OUT / f"imgw_hydro_daily_HY{year}.csv"
    df.to_csv(f, index=False)
    return f


# ---------------------------------------------------------------- PSE (Polish TSO)
def pse(start, end):
    """Report 'his-wlk-cal' (demand, PV, wind, generation groups), 15-min, available from 2024-06-14."""
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    rows = []
    while d0 <= d1:
        j = _get("https://api.raporty.pse.pl/api/his-wlk-cal",
                 params={"$filter": f"business_date eq '{d0.isoformat()}'"}).json()
        rows += j.get("value", [])
        d0 += timedelta(days=1)
        time.sleep(0.1)
    f = OUT / f"pse_his_wlk_cal_{start}_{end}.csv"
    pd.DataFrame(rows).to_csv(f, index=False)
    return f


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("energy_charts"); p.add_argument("--country", required=True); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p = sp.add_parser("gfz"); p.add_argument("--index", default="Kp"); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p = sp.add_parser("pageviews"); p.add_argument("--project", default="en.wikipedia"); p.add_argument("--article", required=True); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p = sp.add_parser("iem"); p.add_argument("--station", required=True); p.add_argument("--vars", default="pres1"); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    sp.add_parser("gios_stations")
    p = sp.add_parser("gios"); p.add_argument("--sensor", required=True); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p = sp.add_parser("imgw_hydro"); p.add_argument("--year", required=True, type=int)
    p = sp.add_parser("pse"); p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    a = ap.parse_args()
    if a.cmd == "energy_charts":
        print(energy_charts(a.country, a.start, a.end))
    elif a.cmd == "gfz":
        print(gfz(a.index, a.start, a.end))
    elif a.cmd == "pageviews":
        print(pageviews(a.project, a.article, a.start, a.end))
    elif a.cmd == "iem":
        print(iem(a.station, a.vars, a.start, a.end))
    elif a.cmd == "gios_stations":
        print(gios_stations())
    elif a.cmd == "gios":
        print(gios(a.sensor, a.start, a.end))
    elif a.cmd == "imgw_hydro":
        print(imgw_hydro(a.year))
    elif a.cmd == "pse":
        print(pse(a.start, a.end))
