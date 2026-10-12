import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src).fillna("")

COLS = [  # (kolumna, nagłówek, szerokość, opis)
    ("id", "ID", 7, "B = burza, Q = dzień spokojny, F = wstrząs/impuls bez burzy, J = zagłuszanie GNSS"),
    ("kategoria", "Kategoria", 22, "Typ zdarzenia"),
    ("stacja", "Stacja GNSS", 9, "Kod stacji ASG-EUPOS dla zdarzeń z rtgms.pl (WIKO = Wicko, BRWO = Braniewo)"),
    ("zbior", "Zbiór", 7, "DEV = strojenie promptów i progów; TEST = odłożony, oceniany raz (od 2025-01-01). Wyjątek: alarmy rtgms.pl z maja 2026 (J132–J139) są w DEV – decyzja Arka 11.10.2026"),
    ("okres_korpusu", "Okres korpusu", 26, "P1 przed 06/2020 (notatki DONKI retrospektywne), P2 06/2020–02/2024, P3 od 03/2024 (Forecast Discussion). Wyniki C raportować osobno per okres"),
    ("poczatek_utc", "Początek (UTC)", 16, "Burze: początek pierwszego 3-h przedziału z Kp ≥ 5-. Dni spokojne: 00:00. Impulsy: czas SSC/SI. Alarmy rtgms.pl: początek pierwszego alarmu epizodu, przeliczony z czasu polskiego na UTC"),
    ("poczatek_rtgms_pl", "Początek wg rtgms.pl (czas polski)", 16, "Tylko alarmy rtgms.pl: początek tak, jak pokazuje strona (czas polski, latem UTC+2), żeby łatwo odszukać alarm na rtgms.pl"),
    ("szczyt_utc", "Szczyt (UTC)", 16, "Przedział 3-h z maksymalnym Kp"),
    ("koniec_utc", "Koniec (UTC)", 16, "Koniec epizodu Kp ≥ 5- (impulsy: +48 h)"),
    ("t0_utc", "t0 (UTC)", 16, "Moment, w którym system ma wyjaśnić zdarzenie (tryb real time): burze = początek + 3 h (pierwsza dostępna wartość Kp). Odcięcie wiedzy: issued_at ≤ t0"),
    ("kp_max", "Kp max", 7, "Maksymalny Kp w oknie (GFZ)"),
    ("poziom", "Poziom", 8, "Skala NOAA G (Kp 5 = G1 … 9o = G5)"),
    ("klucz_przyczyna", "KLUCZ: przyczyna", 30, "Prawidłowa odpowiedź dla klasyfikacji przyczyny"),
    ("klucz_zrodlo", "KLUCZ: źródło", 26, "Richardson-Cane = niezależny klucz. „tylko DONKI” = klucz zależny od wejścia B/C (osłabiony)"),
    ("moment_klucz", "KLUCZ: moment wstrząsu", 24, "SSC z listy ISGI (niezależny klucz czasu); gdy brak – czas zaburzenia z listy R-C"),
    ("rc_icme", "Richardson-Cane ICME", 40, "ICME obejmujący szczyt burzy (lub częściowo w oknie), Dst min; tylko klucz, nie wejście systemu"),
    ("ssc_isgi", "SSC (ISGI)", 18, "Wybrany wstrząs: ostatni SSC przed początkiem+3 h, inaczej pierwszy po"),
    ("ssc_inne_w_oknie", "Inne SSC/SI w oknie", 22, "Pozostałe wstrząsy w oknie [początek−24 h, szczyt+3 h]"),
    ("donki_gst", "DONKI GST", 26, "Wpisy burz DONKI zaczynające się w [początek−12 h, koniec]"),
    ("donki_cme", "DONKI CME", 40, "CME powiązane z GST: czas startu, prędkość, położenie źródła, region aktywny"),
    ("donki_hss", "DONKI HSS", 18, "Strumienie szybkiego wiatru powiązane z GST"),
    ("donki_ips", "DONKI IPS (Ziemia)", 18, "Wstrząsy międzyplanetarne DONKI w [początek−24 h, szczyt+3 h]; to ma być wejście „dotarła fala” w B/C (SSC zostaje kluczem)"),
    ("donki_klasa", "DONKI: klasa", 16, "CME / HSS/CIR / mieszana / brak"),
    ("spe", "Zdarzenie protonowe (SPE)", 30, "Największe SPE NOAA (>10 MeV ≥ 10 pfu) w [początek−72 h, koniec], z poziomem S"),
    ("skutek_gnss", "Oczekiwany skutek GNSS", 50, "Udokumentowany skutek (jeśli jest) | skutek wg skali NOAA"),
    ("skutek_satelity", "Oczekiwany skutek satelity", 45, "Udokumentowany skutek (jeśli jest) | skutek wg skali NOAA G i S"),
    ("skutek_zrodlo", "Źródło skutku", 40, "Publikacja lub komunikat"),
    ("skutek_status", "Status skutku", 24, "„udokumentowane” vs „oczekiwane wg skali”; „DO SPRAWDZENIA” (pomarańczowe) = źródło podane z wiedzy modelu, sprawdź przed cytowaniem"),
    ("pomiar_skutku", "Jak zmierzyć skutek", 40, "Dane do weryfikacji skutku (katalogi opisują tylko przyczynę)"),
    ("noaa_forecast_discussion", "NOAA Forecast Discussion", 14, "Czy istnieje tekst prognostyka (od 03/2024) – wariant D"),
    ("wymuszone", "Dodane ręcznie", 9, "Zdarzenie spoza losowania (ważne dla motywacji)"),
    ("uwagi", "Uwagi", 50, ""),
    ("wersja", "Wersja", 16, "Kiedy zdarzenie dodano. ID są stabilne; ID usuniętych zdarzeń (J121, J126, J128) nie są używane ponownie"),
]

wb = Workbook()
ws = wb.active
ws.title = "Zdarzenia"
hdr_fill = PatternFill("solid", fgColor="1F3864")
key_fill = PatternFill("solid", fgColor="2E75B6")
test_fill = PatternFill("solid", fgColor="FFF2CC")
for j, (c, h, w, _) in enumerate(COLS, 1):
    cell = ws.cell(1, j, h)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = key_fill if h.startswith("KLUCZ") else hdr_fill
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.column_dimensions[get_column_letter(j)].width = w
for i, row in enumerate(d.itertuples(index=False), 2):
    rd = row._asdict()
    for j, (c, *_r) in enumerate(COLS, 1):
        v = rd[c]
        cell = ws.cell(i, j, v)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        if rd["zbior"] == "TEST":
            cell.fill = test_fill
        if (c == "klucz_przyczyna" and ("niejednoznaczna" in str(v) or "SPRAWDZIĆ" in str(v))) or \
           (c == "uwagi" and "SPRAWDZIĆ" in str(v)) or \
           (c in ("skutek_zrodlo", "skutek_status") and "DO SPRAWDZENIA" in str(rd["skutek_status"])):
            cell.fill = PatternFill("solid", fgColor="F4B084")
            cell.font = Font(bold=True)
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{len(d)+1}"
ws.row_dimensions[1].height = 32

# Podsumowanie
ps = wb.create_sheet("Podsumowanie")
r = 1
def table(title, df):
    global r
    ps.cell(r, 1, title).font = Font(bold=True, size=12)
    r += 1
    df = df.reset_index()
    for j, c in enumerate(df.columns, 1):
        ps.cell(r, j, str(c)).font = Font(bold=True)
    r += 1
    for row in df.itertuples(index=False):
        for j, v in enumerate(row, 1):
            ps.cell(r, j, v if not hasattr(v, "item") else v.item())
        r += 1
    r += 1

t = d.groupby(["kategoria", "zbior"]).size().unstack(fill_value=0)
t["razem"] = t.sum(axis=1)
t.loc["RAZEM"] = t.sum()
table("Liczba zdarzeń: kategoria × zbiór", t)
b = d[d.id.str.startswith("B")]
cls = b.klucz_przyczyna.str.replace(r" \+ burza radiacyjna S\d", "", regex=True)
table("Burze: klasa przyczyny w kluczu × zbiór", b.assign(klasa=cls).groupby(["klasa", "zbior"]).size().unstack(fill_value=0))
table("Burze: źródło klucza", b.groupby(["klucz_zrodlo", "zbior"]).size().unstack(fill_value=0))
table("Okres korpusu × zbiór (wszystkie zdarzenia)", d.groupby(["okres_korpusu", "zbior"]).size().unstack(fill_value=0))
j = d[d.kategoria.str.startswith("Zagłuszanie")]
table("Zagłuszanie: źródło przypadku × zbiór", j.assign(zrodlo=j.stacja.where(j.stacja != "", "komunikat/prasa")).groupby(["zrodlo", "zbior"]).size().unstack(fill_value=0))
table("NOAA Forecast Discussion dostępne (wariant D)", d.groupby(["noaa_forecast_discussion", "zbior"]).size().unstack(fill_value=0))
ps.column_dimensions["A"].width = 60
for c in "BCD":
    ps.column_dimensions[c].width = 10

lg = wb.create_sheet("Legenda")
lg.append(["Kolumna", "Opis"])
for c, h, w, desc in COLS:
    lg.append([h, desc])
for cell in lg[1]:
    cell.font = Font(bold=True)
lg.column_dimensions["A"].width = 28
lg.column_dimensions["B"].width = 120

zr = wb.create_sheet("Źródła")
SRC = [
    ("Kp, ap (GFZ Potsdam / CelesTrak)", "results/kp_ap_Ap_SN_F107_daily_1957-10-01_to_2026-10-09_merged.csv.gz; epizody burz: results/storm_events_kp_1957_2026_with_catalogue_links.csv", "do 2026-10-09 (od 2026-10-01 wartości wstępne)"),
    ("Lista ICME Richardson i Cane", "data/richardson_cane_icme_1996_to_2026.csv (rewizja 23.07.2026, DOI 10.7910/DVN/C2MHTH)", "zaburzenia do 2026-07-03; burze po 07/2026 bez klucza R-C"),
    ("Lista SSC/SI (ISGI / Ebre)", "data/isgi_ssc_1957_to_2026.csv", "do 2026-08-11; od 2024 wartości wstępne"),
    ("NASA DONKI GST, CME, IPS (nowe API ccmc.gsfc.nasa.gov/DONKI-API)", "data/donki_gst_…csv, donki_cme_linked_to_gst.csv, donki_ips_earth_…csv", "2010-04 – 2026-10-09; wpisy sprzed 06/2020 dodane retrospektywnie"),
    ("NOAA SWPC zdarzenia protonowe (SPE)", "data/noaa_sep_events_1976_to_2026.csv", "do 2026-07-30"),
    ("Skala NOAA (G, S)", "https://www.swpc.noaa.gov/noaa-scales-explanation", ""),
    ("ASG-EUPOS: wpływ jonosfery na pomiary GNSS", "https://www.asgeupos.pl/uwaga-na-wplyw-jonosfery-w-trakcie-pomiarow-gnss/ (29.10.2024)", ""),
    ("GUGiK: zakłócenia GPS (28.12.2023)", "https://www.geoportal.gov.pl/aktualnosci/zaklocenia-systemu-gps-na-terytorium-polski/", ""),
    ("GUGiK: zakłócenia GNSS, Zamość (26.02.2024)", "https://www.geoportal.gov.pl/aktualnosci/zaklocenia-systemow-gnss-na-terytorium-polski/", ""),
    ("Geoforum: zakłócenia GPS 12/2023", "https://geoforum.pl/news/34550/-aktualizacja-zaklocenia-sygnalu-gps-na-obszarze-polski", ""),
    ("Zaufana Trzecia Strona: kto zakłóca GPS (29.11.2025)", "https://zaufanatrzeciastrona.pl/post/kto-kiedy-i-dlaczego-zakloca-sygnal-gps-nad-polska-i-nie-tylko/", ""),
    ("Świat Dronów: NW PAŻP 06/2025", "https://www.swiatdronow.pl/ostrzezenie-nawigacyjne-nw-dla-calej-polski-zaklocenia-gps", ""),
    ("IŁ-PIB: monitoring zakłóceń GNSS (27.08.2026)", "https://www.il-pib.pl/aktualnosci/gdy-gps-wariuje-instytut-acznosci-monitoruje-zakocenia-gnss-i-buduje-nawigacyjne-koa-zapasowe/", ""),
    ("Nauka w Polsce: prof. Figurski (10.09.2026)", "https://naukawpolsce.pl/aktualnosci/news,114756,prof-figurski-skala-zaklocen-gnss-w-2026-r-jest-bezprecedensowa-w-historii", ""),
    ("Euronews (25.08.2026)", "https://www.euronews.com/my-europe/2026/08/25/phones-drones-and-ships-running-blind-as-gps-malfunctions-across-poland", ""),
    ("Alarmy rtgms.pl WIKO i BRWO (odczyt ręczny Arka)", "rtgms_alarmy_2026_surowe.txt (tekst), rtgms_alarmy_2026.csv (78 okien), rtgms_parse.py", "05–10/2026; rtgms.pl podaje czas polski (wg Arka 11.10.2026), w tabeli przeliczony na UTC"),
    ("NASA DONKI rozbłyski M/X", "donki_flr_mx_2026-05_2026-10.csv (z https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR, odczyt 11.10.2026)", "do sprawdzenia, czy alarm nie pokrywa się z rozbłyskiem radiowym Słońca"),
    ("rtgms.pl (GUGiK, IŁ-PIB)", "https://www.rtgms.pl/monitoring-medium (statystyki RINEX), https://www.rtgms.pl/monitoring-low (dobowe widma per stacja)", "archiwum wg informacji Arka 11.10.2026; z chmury niedostępne – dni zagłuszania odczytuje Arek"),
    ("ASG-EUPOS – dane RINEX", "https://system.asgeupos.pl/", "pomiar skutku (ROTI, błąd pozycji, C/N0); dodane 11.10.2026 za zgodą Arka; dostęp i zasięg archiwum niesprawdzone"),
]
zr.append(["Źródło", "Plik / adres", "Zasięg i uwagi"])
for x in SRC:
    zr.append(list(x))
for cell in zr[1]:
    cell.font = Font(bold=True)
zr.column_dimensions["A"].width = 50
zr.column_dimensions["B"].width = 110
zr.column_dimensions["C"].width = 60
wb.save(out)
print(t)
