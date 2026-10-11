# Zestaw zdarzeń do ewaluacji (warianty A, B, C): zasady wyboru

Napisane 11.10.2026. Tabela: [zestaw_zdarzen_ewaluacja.xlsx](zestaw_zdarzen_ewaluacja.xlsx) (to samo w CSV: [zestaw_zdarzen_ewaluacja.csv](zestaw_zdarzen_ewaluacja.csv), skrypt: [zestaw_zdarzen_build.py](zestaw_zdarzen_build.py)). Plan oceny: [z_czym_porownac.md](z_czym_porownac.md).

Dane pochodzą z katalogów pobranych 10.10.2026 na laptopie (`dataset_research/space_weather_decision/data`). Okres to 04/2010 (początek DONKI) do 09.10.2026.

## Co jest w zestawie (131 zdarzeń)

| Kategoria | Jak wybrane | DEV | TEST |
|---|---|---|---|
| Burze G3–G5 | **Wszystkie** epizody z Kp ≥ 7- (GFZ) | 43 | 12 |
| Burze G1–G2 | Losowo, po równo G1 i G2, ziarno 2026. Do tego ręcznie dodana burza Starlink 3–4.02.2022 | 21 | 12 |
| Dni spokojne | Losowo z dni z Kp ≤ 2+, w których przez ±3 dni nie było Kp ≥ 5- | 14 | 8 |
| Wstrząs bez burzy | Losowo z SSC/SI (ISGI), po których przez 48 h Kp < 5- | 7 | 5 |
| Zagłuszanie GNSS | Wszystkie przypadki z datą, które udało się znaleźć (GUGiK, IŁ-PIB, prasa) | 3 | 6 |

Dni spokojne i wstrząsy bez burzy to fałszywe alarmy. Prawidłowa odpowiedź brzmi wtedy „nic się nie dzieje” albo „fala dotarła, ale burzy nie będzie”. Sprawdzają, czy system nie wymyśla przyczyn.

## Podział na DEV i TEST

- **TEST to zdarzenia od 01.01.2025.** Ocenia się je raz, na koniec. Prompty, progi i wybór fragmentów RAG stroi się tylko na DEV.
- Dlaczego ta data: wszystkie zdarzenia testowe mają tekst prognostyka NOAA (Forecast Discussion od 03/2024, czyli wariant D) i DONKI prowadzone na bieżąco. Do tego część testu wypada po dacie odcięcia wiedzy popularnych LLM, więc model nie zna odpowiedzi z treningu. Wyniki warto podać osobno dla zdarzeń po dacie odcięcia wiedzy modelu, którego użyjesz.
- Kolumna „Okres korpusu” dzieli zdarzenia na P1 (przed 06/2020, notatki DONKI dopisane po fakcie), P2 (06/2020–02/2024) i P3 (od 03/2024). Wyniki wariantu C raportuj osobno dla każdego okresu.

## Klucz odpowiedzi

- **Przyczyna:** lista ICME Richardsona i Cane'a. Jeśli ICME obejmuje szczyt burzy, przyczyną jest CME. Jeśli ICME nie ma, przyczyną jest „nie-CME”, a DONKI HSS doprecyzowuje to do HSS/CIR. R-C nie trafia do systemu. DONKI jest wejściem wariantów B i C, więc klucz oparty tylko na DONKI jest oznaczony jako osłabiony. Dotyczy to jednej burzy testowej (18.08.2026, po końcu listy R-C).
- **7 burz ma oznaczenie SPORNE** (R-C nie ma ICME, a DONKI łączy burzę z CME, np. 19.04.2024, 12.09.2024). To dobry materiał do analizy jakościowej. W liczeniu trafności użyj R-C albo wyłącz te przypadki i napisz to w pracy.
- **Moment:** czas SSC z listy ISGI, a gdy go nie ma, czas zaburzenia z R-C. Jako wejście „dotarła fala uderzeniowa” system dostaje DONKI IPS, nie SSC.
- **Burza radiacyjna:** największe zdarzenie protonowe NOAA w oknie, z poziomem S (np. 19.01.2026: 37 000 pfu, S4).
- **t0:** moment, w którym system ma wyjaśnić zdarzenie. Dla burz to początek + 3 h, czyli pierwsza dostępna wartość Kp ≥ 5-. Dokumenty i wpisy katalogów są widoczne tylko wtedy, gdy issued_at ≤ t0.

## Skutki

Dla każdej burzy podany jest skutek oczekiwany wg skali NOAA (G i S) oraz, gdy istnieje, skutek udokumentowany. Udokumentowane są: 03/2015, 09/2017, 02/2022 (Starlink), 05/2024 i 10/2024 (komunikat ASG-EUPOS). Dwa z nich (03/2015 i 09/2017) podałem z własnej wiedzy. W arkuszu mają status **DO SPRAWDZENIA** i pomarańczowe tło; sprawdź je przed cytowaniem. Skutek trzeba potem zmierzyć: ROTI/TEC z IGS, obserwacje EPN ze stacji w Polsce, TLE ze Space-Track.

## Zagłuszanie: czego brakuje

- Komunikatów z dokładną datą jest mało. Zamość (02/2024) jest przypadkiem niejednoznacznym, bo GUGiK wspomina też aktywność Słońca, a Kp nie przekraczało 3.
- Trzy wpisy z 2026 r. to **okresy**, nie zdarzenia (np. maj–czerwiec 2026, zakłócenia w ok. 70% dni). Konkretne dni i godziny trzeba odczytać z rtgms.pl, którego nie dało się otworzyć z chmury. Dni z Kp ≥ 5- oznacz jako przypadki mieszane.
- Komunikatu o Siedlcach z 30.06.2026 nie udało się ponownie znaleźć, więc jest oznaczony „do potwierdzenia”.
- Dwa przypadki zbiegają się z podwyższonym Kp (14.06.2025 na końcu burzy G3 i 30.06.2026), a w okresach z 2026 r. też są dni burzowe. Prawidłowa odpowiedź to wtedy „zagłuszanie przy jednoczesnej burzy”, a nie samo „nie pogoda kosmiczna”.
