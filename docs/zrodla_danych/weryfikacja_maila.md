# Weryfikacja maila do prof. Surmy (wersja z 11.10.2026, 16:08)

Sprawdzone 11.10.2026 na podstawie pliku `email_promotor/odpowiedz_prof_surma_2026-10-11.txt`. Każda pozycja ma ocenę, dowód i (jeśli trzeba) gotowe nowe brzmienie. Tabela dostępu do danych: [dostep_do_zrodel_danych.xlsx](dostep_do_zrodel_danych.xlsx).

Legenda: **Błąd** trzeba poprawić, **Nieścisłość** warto doprecyzować, **OK** zgodne ze źródłem, **Nie sprawdzono** nie dało się zweryfikować z zewnątrz.

## 1. Twierdzenia do poprawienia (Błąd)

### 1.1 „ok. 5000 satelitów Starlink musiało wykonać manewry, a ocena ryzyka kolizji była osłabiona przez ok. 3 dni” (sekcja 3)
- Źródło (ankieta NOAA, 26.09.2024) mówi o ok. 5000 **statków kosmicznych w ogóle**, nie samych Starlinkach: „Early on May 11, roughly 5,000 spacecraft suddenly began to maneuver…”. O „3 dniach” nie ma mowy; jest „at least 2 days were needed for an effective restart” systemu unikania kolizji (za Parker i Linares 2024).
- Nowe brzmienie: **„Podczas burzy w maju 2024 r. ok. 5000 satelitów (w większości Starlink) jednocześnie zaczęło wykonywać manewry, a przywrócenie sprawnego systemu unikania kolizji na orbicie zajęło co najmniej 2 dni.”**

### 1.2 „10 maja o 16:36 UT do Ziemi dotarła fala uderzeniowa” (sekcja 4)
- DONKI (IPS 2024-05-10T16:36Z) ma lokalizację „Earth”, ale pomiar pochodzi z satelity ACE w punkcie L1, ok. 1,5 mln km przed Ziemią. Do magnetosfery fala dotarła ok. **17:05 UT** (Flash Data Report, arXiv 2407.07665).
- Nowe brzmienie: **„10 maja o 16:36 UT satelita ACE zarejestrował przed Ziemią falę uderzeniową, która ok. 17:05 UT dotarła do magnetosfery,”**

### 1.3 „8–9 maja ze Słońca wyleciało pięć obłoków plazmy z prędkością do 1330 km/s” (sekcja 4)
- DONKI (CMEAnalysis, najdokładniejsze pomiary) ma **sześć** CME z 8–9 maja (8.05: 05:36, 12:24, 19:12, 22:24; 9.05: 09:24, 18:23). 1330 km/s to prędkość głównej części CME z 9.05 09:24 (sam front uderzeniowy 1561 km/s). Prędkość się zgadza, liczba nie.
- Nowe brzmienie: **„8–9 maja ze Słońca wyleciało sześć obłoków plazmy z prędkością do 1330 km/s, z jednego aktywnego obszaru (NASA DONKI),”**

### 1.4 „Archiwum tekstów NOAA SWPC: codzienne raporty i komentarze prognostyków od 1966 r.” (sekcja 5c)
- Według NCEI od 1966 jest tylko ustrukturyzowany raport RSGA. Pełniejsze teksty (SGAS, raporty zdarzeń) są od 1996, „The Weekly” od 1997, a opisowe komentarze prognostyków (Forecast Discussion) dopiero od 03/2024.
- Nowe brzmienie: **„Zastosowanie: codzienne raporty prognostyczne od 1966 r. (RSGA), szczegółowe podsumowania od 1996 r. oraz komentarze prognostyków (domena publiczna). To główny korpus dla RAG…”** (reszta bez zmian).

### 1.5 „Zdarzenia protonowe NOAA … lista burz radiacyjnych od 1976 r.” (sekcja 5b)
- Tabela pod podanym linkiem NGDC kończy się (według mojego odczytu) na 03/2011. Aktualna lista SWPC jest w pliku SPE.txt na serwerze FTP NOAA (ftp://ftp.swpc.noaa.gov/pub/indices/SPE.txt).
- Nowe brzmienie linku: **„Dane: https://umbra.nascom.nasa.gov/SEP/ (aktualna wersja: ftp://ftp.swpc.noaa.gov/pub/indices/SPE.txt), od 2010 r. także zdarzenia SEP w NASA DONKI”**.

## 2. Twierdzenia do doprecyzowania (Nieścisłość)

### 2.1 „w maju 2024 r. błędy precyzyjnego pozycjonowania w środkowych stanach USA sięgały 70 m” (sekcja 3)
- Younas i in. 2025 (JGR Space Physics): „position errors in PPP mode reaching up to 70 m in the Central United States” w fazie głównej burzy 10 maja. Liczba się zgadza, ale chodzi o tryb **PPP**, a nie RTK, którego używają rolnicy. Ta sama ankieta NOAA podaje, że rolnicy widzieli błędy rzędu 10–30 stóp (3–9 m). Czytałem tylko streszczenie, bo strona wydawcy była niedostępna.
- Nowe brzmienie: **„w maju 2024 r. błędy pozycjonowania metodą PPP w środkowych stanach USA sięgały 70 m (Younas i in. 2025), a rolnicy zgłaszali błędy rzędu 3–9 m,”**

### 2.2 „ekonomiści z Kansas State University szacują straty przychodów z kukurydzy na 53 mln – 1,29 mld USD” (sekcja 3)
- To poster jednego autora (Terry Griffin, KSU) z Space Weather Workshop 2025, nie recenzowany artykuł. Straty dotyczą 12 stanów Środkowego Zachodu i wynikają z opóźnienia siewów. Liczby się zgadzają.
- Nowe brzmienie: **„według wstępnej analizy ekonomisty z Kansas State University (Griffin 2025) opóźnienie siewów mogło obniżyć przychody z kukurydzy w 12 stanach o 53 mln – 1,29 mld USD,”**

### 2.3 „ASG-EUPOS (GUGiK) ma ok. 48 tys. kont, głównie w rolnictwie precyzyjnym” (sekcja 3)
- Komunikat GUGiK (III kw. 2025): ok. 48 tys. **zarejestrowanych** kont, z czego 23 799 było używanych w III kwartale. Rolnictwo precyzyjne jest wymienione jako segment intensywnie korzystający z systemu, ale nie ma tam informacji, że to większość kont.
- Nowe brzmienie: **„ASG-EUPOS (GUGiK) ma ok. 48 tys. zarejestrowanych kont (ok. 24 tys. aktywnych w III kwartale 2025 r.), a intensywnie korzysta z niego m.in. rolnictwo precyzyjne,”**

### 2.4 „warunki burzowe występują średnio ok. 74 dni w roku, a silne burze (G3 i więcej) ok. 7 razy w roku” (sekcja 3)
- Mail nie podaje źródła, a liczby nie zgadzają się ze skalą NOAA. NOAA podaje na 11-letni cykl 900 dni z poziomem G1 (ok. 82 dni rocznie, sam G1) i 194 dni z G3 lub więcej (ok. 18 dni rocznie). „7 razy” może oznaczać liczbę osobnych burz, a nie dni, ale mail tego nie mówi. Jeśli to Twoje obliczenia na danych GFZ, napisz to wprost.
- Nowe brzmienie (wersja z NOAA): **„to nie są wyjątki: według NOAA warunki burzowe występują średnio przez ponad 80 dni w roku, a silne burze (G3 i więcej) przez kilkanaście dni w roku.”**
- Albo (jeśli liczby są Twoje): **„…według moich obliczeń na danych GFZ z lat 1957–2026 warunki burzowe (Kp ≥ 5) występują średnio przez ok. 74 dni w roku, a silne burze (G3 i więcej) ok. 7 razy w roku.”**

### 2.5 „Dziś na te pytania nie ma łatwej odpowiedzi” (sekcja 3)
- W Polsce od 25.11.2025 działa portal rtgms.pl (GUGiK i Instytut Łączności PIB, finansowanie ESA), który na żywo pokazuje zakłócenia GNSS na stacjach ASG-EUPOS. Promotor może o nim wiedzieć, więc lepiej go wymienić i pokazać różnicę: rtgms.pl pokazuje zakłócenie, a nie wyjaśnia jego przyczyny ani nie łączy go z pogodą kosmiczną.
- Proponowane dodanie po zdaniu o GUGiK: **„Od listopada 2025 r. GUGiK i Instytut Łączności udostępniają portal rtgms.pl, który pokazuje zakłócenia na bieżąco, ale nie wyjaśnia ich przyczyny.”**

### 2.6 „badacze z CBK PAN (Gil i in. 2021)” (sekcja 3)
- Pierwsza autorka i większość zespołu jest z Uniwersytetu w Siedlcach; CBK PAN jest jedną z afiliacji. Wyniki dotyczą TAURON i są korelacyjne. Treść się zgadza.
- Nowe brzmienie: **„badacze z Uniwersytetu w Siedlcach i CBK PAN (Gil i in. 2021)”**

### 2.7 OMNI: „To informacja o tym, co dopiero nadciąga ze Słońca” (sekcja 5a)
- OMNI jest przesunięte w czasie do frontu magnetosfery, więc opisuje to, co właśnie dociera, a dane pojawiają się z kilkudniowym opóźnieniem (ostatni pomiar 05.10.2026). Wyprzedzenie rzędu kilkudziesięciu minut dają tylko bieżące pomiary z L1 w NOAA SWPC.
- Nowe brzmienie: **„Zastosowanie: prędkość wiatru słonecznego i pole magnetyczne docierające do Ziemi, czyli informacja o przyczynie burzy, której nie ma w indeksie Kp. Posłuży jako dodatkowa cecha przy wyszukiwaniu podobnych sytuacji w danych historycznych; w trybie bieżącym te same wielkości dostarcza NOAA SWPC.”**

### 2.8 NOAA: „Oficjalne 3-dniowe prognozy NOAA posłużą jako punkt odniesienia” (sekcja 5a)
- Archiwum prognoz 3-dniowych w NCEI jest dopiero od 03/2022. Dłuższy punkt odniesienia daje przewidywany Ap w raportach RSGA (od 1966). Brzmienie może zostać, ale przy planowaniu oceny trzeba o tym pamiętać.

### 2.9 EPN: „pozycje stacji GNSS, na których można zmierzyć, o ile pogarsza się dokładność” (sekcja 5d)
- Dostęp jest prosty (CC BY 4.0), ale oficjalne rozwiązania EPN są dobowe, więc nie pokażą pogorszenia w ciągu godzin. Trzeba samemu przeliczyć obserwacje RINEX.
- Nowe brzmienie: **„Zastosowanie: obserwacje GNSS ze stacji w Polsce, z których przeliczę błąd pozycji w czasie burz.”**

### 2.10 GUGiK: link do komunikatów (sekcja 5d)
- Link prowadzi do jednego ogólnego artykułu z 26.02.2024 bez dat i godzin zakłóceń. Komunikatów jest niewiele i nie ma ich archiwum.
- Nowe brzmienie: **„Dane: komunikaty na https://www.geoportal.gov.pl/aktualnosci (np. Siedlce, 30.06.2026) oraz portal https://rtgms.pl. Zastosowanie: przypadki zagłuszania sygnału jako kontrprzykłady; zbiór tych przypadków zbiorę ręcznie.”**

## 3. Twierdzenia zgodne ze źródłami (OK)

| Twierdzenie | Dowód |
|---|---|
| Green, Likar i Shprits 2017: operatorzy chcą narzędzi do przypisywania anomalii pogodzie kosmicznej; analiza ok. 1 mln USD | Space Weather 15, 804–818: „the means to reduce the uncertainty about whether an anomaly is related to space weather”; „on the order of one million dollars” (dotyczy pełnej analizy anomalii przez komisję, ponoszonej przez producenta) |
| Luty 2022: 38 z 49 satelitów Starlink przy słabej burzy | CIRES/NOAA i doniesienia o badaniu NOAA: 38 satelitów zniszczonych, burza „minor”. Strony artykułu z DOI w mailu nie dało się odczytać, więc warto sprawdzić, czy DOI wskazuje na właściwy artykuł |
| Maj 2024 najsilniejsza od ponad 20 lat, poziom G5 | NOAA: pierwsze warunki G5 od października 2003 |
| Dobowa aktywność druga najwyższa od 1957 r. | Ap 11.05.2024 = 271, wyższy był tylko 13.11.1960 (280). Można nawet napisać „druga najwyższa w historii pomiarów” |
| Jeden aktywny obszar | AR 13664 (DONKI, Flash Data Report) |
| Obłok dociera po 1–3 dobach | Typowy czas przelotu CME; najszybsze docierają w mniej niż dobę, można dopisać „zwykle” |
| Skala G1–G5 jak skala huraganów | NOAA: „analogous to hurricanes, tornadoes, and earthquakes” |
| Zorza widoczna w Polsce w maju 2024 | Powszechnie udokumentowane |
| Gil i in. 2021: więcej awarii w sieci TAURON po burzach | SWSC 11, 30: „massive increase in the number of electrical grid failures in South Poland” |
| Szybki wiatr słoneczny powraca co ok. 27 dni | Okres synodyczny obrotu Słońca |
| Hp30 co 30 minut | GFZ, dane od 1995 r. |
| 69 lat danych 1957–2026 bez luk | Prawda, ale GFZ ma Kp od 1932 r.; warto umieć uzasadnić wybór 1957 |
| Wszystkie źródła można wykorzystać w pracy dyplomowej z cytowaniami | Potwierdzone w tabeli dostępu; dwa źródła są na licencji niekomercyjnej, a DONKI prosi o kontakt przy pracach walidacyjnych |

## 4. Nie sprawdzono (wymagają Twoich danych)
- „w Belsku pole zmieniło się w ciągu doby o ponad 1100 nT”: wynik z wcześniejszych obliczeń; nie mogłem pobrać danych z BGS, żeby go powtórzyć. Dane minutowe z Belska są dostępne (HAPI BGS), więc warto mieć ten wykres pod ręką.
- „wstępne testy pokazały…” i „dla wszystkich silnych burz z lat 2010–2026 udało się automatycznie wskazać przyczynę”: to Twoje własne wyniki; promotor może o nie zapytać, więc dobrze mieć je zapisane.
- Daty spotkań (16 maja, 21 maja, 30 września) i seminarium 15 października.

## 5. Jakie dane faktycznie masz dla nowego zakresu

**Przyczyna (wspólna dla obu grup odbiorców), wszystko dostępne i otwarte:** GFZ Kp/Hp30 (real time i historia), NOAA SWPC (real time, w tym wiatr słoneczny z L1 i protony z GOES), NASA OMNI (historia), DONKI (od 2010, prawie real time), Richardson i Cane, lista SSC, archiwum tekstów NOAA dla RAG, artykuły przeglądowe.

**Użytkownicy GNSS (rolnictwo precyzyjne):**
- Masz: EPN (obserwacje RINEX, CC BY 4.0, trzeba je przeliczyć), Belsk (lokalna burza), komunikaty GUGiK i rtgms.pl (kontrprzykłady zagłuszania, mało przypadków, zbierane ręcznie).
- Brakuje bezpośredniej miary jonosfery, która faktycznie psuje GNSS (Kp opisuje ją słabo). Warto dodać globalne mapy TEC i mapy ROTI z IGS (pliki IONEX w NASA CDDIS; bezpłatnie po założeniu konta Earthdata, według mojej wiedzy). To najprostszy sposób, żeby mierzyć skutek bez własnego przetwarzania RINEX.

**Operatorzy satelitów:**
- Masz: zdarzenia protonowe (zagrożenie dla elektroniki), DONKI (SEP, burze).
- Brakuje danych o skutku: nie ma otwartej bazy anomalii satelitów, więc trafności wyjaśnień dla operatorów nie da się sprawdzić na awariach. Da się ją sprawdzić na **spadku orbit**: CelesTrak SupGP udostępnia bezpłatnie efemerydy Starlink z danych SpaceX, a Space-Track ma historyczne elementy orbitalne (bezpłatne konto; według mojej wiedzy regulamin zabrania redystrybucji danych). Na nich widać np. przyspieszone opadanie satelitów w maju 2024 i lutym 2022.
- Warto w mailu dopisać jedno zdanie, że skutki dla satelitów będą weryfikowane na danych orbitalnych, bo w obecnej liście nie ma żadnego źródła o skutku dla tej grupy.

## Czego nie udało się odczytać
Strona artykułu Starlink w Wiley (limit zapytań) i pełny tekst Younas i in. 2025 (błąd strony wydawcy); użyłem streszczeń i stron NOAA/CIRES. Liczby z rekordu Ap pochodzą z Wikipedii, która powołuje się na GFZ.
