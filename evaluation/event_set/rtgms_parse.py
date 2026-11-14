"""Parse Arek's manual transcription of rtgms.pl Monitoring Low alarms into a CSV.

Usage: python rtgms_parse.py rtgms_alarmy_2026_surowe.txt rtgms_alarmy_2026.csv

Rules:
- An end time of 00:00 (or any end <= start) means the window runs past midnight: end += 1 day.
- Per-band flags (L1, L2, L5, E6): 0 = no interference, 1 = possible, 2 = interference; empty = not given.
  A missing digit is inferred from the text ("brak" -> 0, "możliwe" -> 1, "zakłócenia" -> 2).
- Times are copied as shown by rtgms.pl, which uses Polish local time (CET/CEST; confirmed by Arek 11.10.2026).
  start_utc and koniec_utc are the same times converted to UTC with the Europe/Warsaw zone.
"""
import re
import sys
from datetime import datetime, timedelta

import pandas as pd

src, out = sys.argv[1], sys.argv[2]
STATION_HDR = re.compile(r"stacji\s+(\w+),\s*miasto:\s*(.+)$", re.I)
DAY = re.compile(r"^([A-Z]{4})\s*-\s*(\d{4})\s*-\s*(\d{2})\s*-\s*(\d{2})")
ALARM = re.compile(r"^Alarm\s+(\d)", re.I)
WINDOW = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})")
BAND = re.compile(r"^(L1|L2|L5|E6)\s*[:;]\s*(\d)?\s*(.*)$", re.I)

cities, rows, cur = {}, [], None
for n, raw in enumerate(open(src, encoding="utf-8"), 1):
    line = raw.strip()
    if not line:
        continue
    if m := STATION_HDR.search(line):
        cities[m.group(1)] = m.group(2).strip()
        continue
    if m := DAY.match(line):
        cur = dict(stacja=m.group(1), data=f"{m.group(2)}-{m.group(3)}-{m.group(4)}",
                   alarm_poziom=None, L1="", L2="", L5="", E6="", linia_zrodla=n)
        rows.append(cur)
        continue
    if cur is None:
        continue
    if m := ALARM.match(line):
        cur["alarm_poziom"] = int(m.group(1))
    elif m := WINDOW.match(line):
        d = datetime.strptime(cur["data"], "%Y-%m-%d")
        s = d + timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
        e = d + timedelta(hours=int(m.group(3)), minutes=int(m.group(4)))
        if e <= s:
            e += timedelta(days=1)
        cur["start"], cur["koniec"] = s, e
    elif m := BAND.match(line):
        val = m.group(2)
        if val is None:
            t = m.group(3).lower()
            val = "0" if "brak" in t else "1" if ("mozliwe" in t or "możliwe" in t) else "2"
        cur[m.group(1).upper()] = int(val)

def to_utc(s):
    return (s.dt.tz_localize("Europe/Warsaw", ambiguous="raise", nonexistent="raise")
            .dt.tz_convert("UTC").dt.tz_localize(None))

df = pd.DataFrame(rows)
df["miasto"] = df.stacja.map(cities)
df["start_utc"], df["koniec_utc"] = to_utc(df.start), to_utc(df.koniec)
df["czas_strefa"] = "start/koniec: czas polski (Europe/Warsaw), wg Arka 11.10.2026"
df["zrodlo"] = "rtgms.pl/monitoring-low, odczyt ręczny Arka 11.10.2026"
df = df.sort_values(["stacja", "start"])[["stacja", "miasto", "data", "start", "koniec", "start_utc", "koniec_utc",
                                          "alarm_poziom", "L1", "L2", "L5", "E6", "czas_strefa", "zrodlo", "linia_zrodla"]]
for c in ["start", "koniec", "start_utc", "koniec_utc"]:
    df[c] = df[c].dt.strftime("%Y-%m-%d %H:%M")
df.to_csv(out, index=False)
print(df.groupby("stacja").size().to_string())
