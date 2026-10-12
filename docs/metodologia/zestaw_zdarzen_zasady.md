# Zestaw zdarzeń do ewaluacji (warianty A, B, C): zasady wyboru

Napisane 11.10.2026, uzupełnione tego samego dnia o dni zagłuszania z rtgms.pl (wersja v2, czasy alarmów w UTC). Tabela: [zestaw_zdarzen_ewaluacja.xlsx](zestaw_zdarzen_ewaluacja.xlsx) (to samo w CSV: [zestaw_zdarzen_ewaluacja.csv](zestaw_zdarzen_ewaluacja.csv)). Skrypty: [zestaw_zdarzen_build.py](zestaw_zdarzen_build.py) (CSV), [zestaw_zdarzen_xlsx.py](zestaw_zdarzen_xlsx.py) (arkusz), [rtgms_parse.py](rtgms_parse.py) (alarmy rtgms.pl). Plan oceny: [z_czym_porownac.md](z_czym_porownac.md).

Dane pochodzą z katalogów pobranych 10.10.2026 na laptopie (`dataset_research/space_weather_decision/data`). Okres to 04/2010 (początek DONKI) do 09.10.2026.

## Co jest w zestawie (157 zdarzeń)

| Kategoria | Jak wybrane | DEV | TEST |
|---|---|---|---|
| Burze G3–G5 | **Wszystkie** epizody z Kp ≥ 7- (GFZ) | 43 | 12 |
| Burze G1–G2 | Losowo, po równo G1 i G2, ziarno 2026. Do tego ręcznie dodana burza Starlink 3–4.02.2022 | 21 | 12 |
| Dni spokojne | Losowo z dni z Kp ≤ 2+, w których przez ±3 dni nie było Kp ≥ 5- | 14 | 8 |
| Wstrząs bez burzy | Losowo z SSC/SI (ISGI), po których przez 48 h Kp < 5- | 7 | 5 |
| Zagłuszanie GNSS | Wszystkie przypadki z datą z komunikatów i prasy (6) oraz wszystkie epizody alarmów rtgms.pl ze stacji WIKO i BRWO, 05–10/2026 (29). Maj 2026 w DEV (wyjątek, niżej) | 11 | 24 |

Dni spokojne i wstrząsy bez burzy to fałszywe alarmy. Prawidłowa odpowiedź brzmi wtedy „nic się nie dzieje” albo „fala dotarła, ale burzy nie będzie”. Sprawdzają, czy system nie wymyśla przyczyn.

Zagłuszanie to teraz ok. 40% zbioru TEST (24 z 61), a dla wariantu A jest raczej łatwe (spokojne Kp). **Wyniki raportuj osobno dla każdej kategorii**, inaczej średnia trafność zatrze różnice na burzach.

**ID są stabilne.** Skrypt zachowuje ID istniejących zdarzeń, a nowe dostają kolejne numery (J132–J160). Alarmy rtgms.pl rozpoznaje po godzinie ze strony, więc przeliczenie na UTC nie zmieniło ich ID. ID usuniętych wpisów (J121, J126, J128) nie są używane ponownie. Kolumna „Wersja” mówi, kiedy zdarzenie dodano.

## Podział na DEV i TEST

- **TEST to zdarzenia od 01.01.2025.** Ocenia się je raz, na koniec. Prompty, progi i wybór fragmentów RAG stroi się tylko na DEV.
- **Wyjątek (decyzja Arka, 11.10.2026):** 8 epizodów zagłuszania z rtgms.pl z maja 2026 (J132–J139, stacja BRWO) jest w DEV. Bez nich DEV nie miałby żadnego alarmu ze stacji, a potok „objaw z RINEX → wyjaśnienie” zobaczyłby taki przypadek pierwszy raz dopiero w TEST. Podział zostaje czasowy wewnątrz 2026: maj w DEV, czerwiec–październik w TEST. Razem: DEV 96, TEST 61.
- Dlaczego ta data: wszystkie zdarzenia testowe mają tekst prognostyka NOAA (Forecast Discussion od 03/2024, czyli wariant D) i DONKI prowadzone na bieżąco. Do tego część testu wypada po dacie odcięcia wiedzy popularnych LLM, więc model nie zna odpowiedzi z treningu. Wyniki warto podać osobno dla zdarzeń po dacie odcięcia wiedzy modelu, którego użyjesz.
- Kolumna „Okres korpusu” dzieli zdarzenia na P1 (przed 06/2020, notatki DONKI dopisane po fakcie), P2 (06/2020–02/2024) i P3 (od 03/2024). Wyniki wariantu C raportuj osobno dla każdego okresu.

## Klucz odpowiedzi

- **Przyczyna:** lista ICME Richardsona i Cane'a. Jeśli ICME obejmuje szczyt burzy, przyczyną jest CME. Jeśli ICME nie ma, przyczyną jest „nie-CME”, a DONKI HSS doprecyzowuje to do HSS/CIR. R-C nie trafia do systemu. DONKI jest wejściem wariantów B i C, więc klucz oparty tylko na DONKI jest oznaczony jako osłabiony. Dotyczy to jednej burzy testowej (18.08.2026, po końcu listy R-C).
- **7 burz ma oznaczenie SPORNE** (R-C nie ma ICME, a DONKI łączy burzę z CME, np. 19.04.2024, 12.09.2024). To dobry materiał do analizy jakościowej. W liczeniu trafności użyj R-C albo wyłącz te przypadki i napisz to w pracy.
- **Moment:** czas SSC z listy ISGI, a gdy go nie ma, czas zaburzenia z R-C. Jako wejście „dotarła fala uderzeniowa” system dostaje DONKI IPS, nie SSC.
- **Burza radiacyjna:** największe zdarzenie protonowe NOAA w oknie, z poziomem S (np. 19.01.2026: 37 000 pfu, S4).
- **t0:** moment, w którym system ma wyjaśnić zdarzenie. Dla burz to początek + 3 h, czyli pierwsza dostępna wartość Kp ≥ 5-. Dokumenty i wpisy katalogów są widoczne tylko wtedy, gdy issued_at ≤ t0.

## Skutki

Dla każdej burzy podany jest skutek oczekiwany wg skali NOAA (G i S) oraz, gdy istnieje, skutek udokumentowany. Udokumentowane są: 03/2015, 09/2017, 02/2022 (Starlink), 05/2024 i 10/2024 (komunikat ASG-EUPOS). Dwa z nich (03/2015 i 09/2017) podałem z własnej wiedzy. W arkuszu mają status **DO SPRAWDZENIA** i pomarańczowe tło; sprawdź je przed cytowaniem. Skutek trzeba potem zmierzyć: dane RINEX ze stacji ASG-EUPOS (https://system.asgeupos.pl/, ROTI i błąd pozycji; dostęp i zasięg archiwum do sprawdzenia), ROTI/TEC z IGS, obserwacje EPN, TLE ze Space-Track.

## Zagłuszanie z rtgms.pl (dodane 11.10.2026)

- **Źródło:** alarmy „Monitoring Low” (analiza widma, alarm 2 = zakłócenia) ze stacji WIKO (Wicko) i BRWO (Braniewo), przepisane ręcznie przez Arka z https://www.rtgms.pl/monitoring-low. Tekst: [rtgms_alarmy_2026_surowe.txt](rtgms_alarmy_2026_surowe.txt), tabela 78 okien: [rtgms_alarmy_2026.csv](rtgms_alarmy_2026.csv). Zastąpiły trzy wpisy-okresy (maj–czerwiec, lipiec, 1–19 sierpnia 2026).
- **Zdarzenie = epizod:** ciąg alarmów na jednej stacji z przerwami krótszymi niż 6 h. Z 78 okien powstało 29 epizodów (21 BRWO, 8 WIKO). Kolejne alarmy w ciągu kilku godzin to ta sama sytuacja, więc liczenie ich osobno sztucznie zwiększyłoby liczbę niezależnych przypadków.
- **Czas:** rtgms.pl pokazuje czas polski, latem UTC+2 (informacja od Arka z 11.10.2026). W tabeli wszystkie czasy są w UTC, a kolumna „Początek wg rtgms.pl” ma godzinę ze strony, żeby łatwo znaleźć alarm. Kp liczę dla okna alarmu w UTC. Po przeliczeniu Kp zmieniło się w 10 epizodach, ale wszystkie zostały poniżej 5-, więc ich klucz się nie zmienił.
- **J151 i J155** (WIKO 18.07 i BRWO 23.08.2026) mają te same godziny. Arek sprawdził, że to poprawny odczyt, a nie pomyłka.
- **Klucz:** „nie pogoda kosmiczna (zakłócenie RF)”. Analiza widma wykrywa obcy sygnał radiowy, a burza jonosferyczna nie zmienia widma. Etykieta i pasmo z rtgms.pl są kluczem odpowiedzi, tak jak komunikaty GUGiK: system dostaje tylko objaw (stacja, czas, spadek jakości sygnału z RINEX), nigdy samą etykietę „Zakłócenia”.
- **Rozbłyski:** żaden krótki alarm nie pokrywa się z rozbłyskiem M/X z DONKI ([donki_flr_mx_2026-05_2026-10.csv](donki_flr_mx_2026-05_2026-10.csv)), więc rozbłysk radiowy Słońca nie wyjaśnia żadnego z nich.
- **Przypadek niejednoznaczny, 05.06.2026 (J140, J141):** alarm o 12:38–12:45 UTC (14:38 czasu polskiego) jednocześnie na WIKO i BRWO (ok. 150 km od siebie), w czasie burzy G2 wywołanej przez CME (Kp 5+ w tym przedziale, 6o w następnym). Alarm zaczął się 32 min po drugiej fali uderzeniowej w DONKI (12:06 UTC). DONKI mierzy falę przy L1, a pierwsza fala tego dnia (04:23) dała SSC na Ziemi o 05:05 (ISGI), czyli 42 min później. Druga fala mogła więc dotrzeć do Ziemi właśnie w czasie alarmu; drugiego SSC tego dnia na liście ISGI nie ma. Jednoczesność na dwóch stacjach i zbieżność z falą wskazują na wspólną przyczynę, ale z samych alarmów nie wiadomo, czy to zagłuszanie o dużym zasięgu, czy skutek burzy. Oznaczony jako mieszany i niejednoznaczny. RINEX z obu stacji może to rozstrzygnąć: spadek C/N0 na wszystkich satelitach naraz wskazuje na zagłuszanie, a zaburzenia zależne od satelity i wysokie ROTI na jonosferę.
- **Różne wzory:** w Braniewie (przy granicy z obwodem królewieckim) dominuje L1, typowe dla zagłuszania GPS. W Wicku ciąg 24.08–03.09.2026 (J156, ok. 220 h) dotyczy L5 i L2 przy czystym L1, więc źródło może być inne. Tego nie sprawdzałem.

## Zagłuszanie: czego brakuje

- **BRWO 10.10.2026 (J160):** Kp jeszcze nie ma (dane do 09.10.2026). Uzupełni się po ponownym uruchomieniu skryptu na nowszych danych.
- Komunikatów GUGiK z dokładną datą jest mało. Zamość (02/2024) jest przypadkiem niejednoznacznym, bo GUGiK wspomina też aktywność Słońca, a Kp nie przekraczało 3.
- Komunikatu o Siedlcach z 30.06.2026 nie udało się ponownie znaleźć, więc jest oznaczony „do potwierdzenia”.
- Przypadki mieszane (zakłócenie w czasie podwyższonego Kp): 14.06.2025 (koniec burzy G3), 30.06.2026 (Siedlce) i 05.06.2026 (WIKO i BRWO). Prawidłowa odpowiedź to wtedy „zakłócenie przy jednoczesnej burzy”, a nie samo „nie pogoda kosmiczna”.
