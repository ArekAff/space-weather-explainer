# Z czym porównać analizę i skąd wziąć dane porównawcze

Dotyczy pytania badawczego: *czy połączenie analizy danych czasu rzeczywistego z wiedzą ekspercką (katalogi i RAG) daje trafniejsze i lepiej udokumentowane wyjaśnienia zdarzeń niż analiza samych danych liczbowych?*

Napisane 11.10.2026 na podstawie tabeli [dostep_do_zrodel_danych.xlsx](../zrodla_danych/dostep_do_zrodel_danych.xlsx) i [weryfikacji maila](../zrodla_danych/weryfikacja_maila.md).

## 1. Co z czym porównujesz

Pytanie samo wyznacza punkt odniesienia: **ta sama platforma bez wiedzy eksperckiej**. To eksperyment typu ablacja, czyli te same zdarzenia przechodzą przez kilka wersji systemu, a różni je tylko to, do czego system ma dostęp.

| Wariant | Co dostaje | Rola |
|---|---|---|
| A. Same dane liczbowe | Szeregi Kp/Hp30, wiatr słoneczny (OMNI/NOAA), wykryte anomalie; LLM pisze wyjaśnienie tylko z liczb | **Punkt odniesienia z pytania badawczego** |
| B. Dane + katalogi | A + katalogi zdarzeń (DONKI, zdarzenia protonowe) | Pokazuje, ile daje sama ustrukturyzowana wiedza |
| C. Dane + katalogi + RAG | B + wyszukiwanie w tekstach NOAA i artykułach przeglądowych, z cytatami | **Twoja platforma** |
| (opcjonalnie) D. Ekspert NOAA | Oficjalne teksty NOAA (Forecast Discussion od 03/2024, The Weekly od 1997) | Zewnętrzny „sufit”: jak zdarzenie wyjaśnił człowiek |

Wariant B jest opcjonalny, ale bez niego nie da się powiedzieć, czy poprawa wynika z katalogów, czy z RAG.

## 2. Skąd „prawidłowe odpowiedzi” (dane porównawcze)

Wyjaśnienie zdarzenia ma trzy elementy, a każdy da się sprawdzić na niezależnym źródle:

| Element wyjaśnienia | Prawidłowa odpowiedź z | Uwagi |
|---|---|---|
| **Przyczyna** (CME, szybki wiatr z dziury koronalnej, burza radiacyjna, brak związku z pogodą kosmiczną) | Lista ICME Richardsona i Cane'a (CME vs inne), DONKI (łańcuch rozbłysk → CME → fala uderzeniowa → burza), zdarzenia protonowe SPE.txt | Richardson-Cane to standard w literaturze do klasyfikacji przyczyn burz |
| **Moment** (kiedy dotarła fala uderzeniowa, kiedy zaczęła się burza) | Lista SSC (Ebre/ISGI), DONKI IPS | Np. czy system podał czas z dokładnością do 1 h |
| **Skutek** dla odbiorcy | GNSS: mapy TEC/ROTI z IGS (CDDIS), obserwacje EPN; satelity: spadek orbit z CelesTrak SupGP / Space-Track | Skutek trzeba zmierzyć, bo katalogi opisują tylko przyczynę |
| **Kontrprzykłady** | Komunikaty GUGiK i rtgms.pl o zagłuszaniu | Poprawne wyjaśnienie brzmi „to nie pogoda kosmiczna”; zbiór budowany ręcznie, przypadków jest mało |

### Uwaga: nie oceniaj na tym, co system dostał na wejściu

Jeśli DONKI jest w bazie wiedzy wariantu C, to sprawdzanie przyczyny na DONKI faworyzuje C (system przepisuje odpowiedź z katalogu). Dwa proste rozwiązania:

1. **Rozdzielenie źródeł:** DONKI i teksty NOAA idą do bazy wiedzy, a **Richardson-Cane i lista SSC służą wyłącznie jako klucz odpowiedzi** i nigdy nie trafiają do systemu.
2. **Rozdzielenie w czasie:** baza RAG zawiera tylko teksty sprzed daty zdarzenia (np. raport NOAA z dnia burzy jest niedostępny przy jej wyjaśnianiu). To też symuluje prawdziwy tryb czasu rzeczywistego.

Najlepiej zastosować oba.

## 3. Jak mierzyć „trafniejsze” i „lepiej udokumentowane”

**Trafność** (automatycznie, na kluczu z sekcji 2):
- trafność klasyfikacji przyczyny (CME / szybki wiatr / radiacja / inna) względem Richardson-Cane i DONKI, np. accuracy i F1;
- błąd czasu początku burzy względem SSC;
- czy wskazany skutek się zgadza (np. ROTI powyżej progu nad Polską; spadek orbity Starlink);
- odsetek kontrprzykładów (zagłuszanie) poprawnie uznanych za „nie pogoda kosmiczna”.

**Udokumentowanie:**
- odsetek twierdzeń w wyjaśnieniu, które mają cytat;
- trafność cytatów: czy cytowany fragment rzeczywiście potwierdza twierdzenie (ocena ręczna na próbie albo LLM jako sędzia z ręczną kontrolą części przypadków);
- odsetek twierdzeń fałszywych (halucynacji).

**Ocena ekspercka (uzupełniająca):** na mniejszej próbie zdarzeń ślepa ocena wyjaśnień A i C (bez informacji, który wariant jest który) według prostej skali, np. poprawność, kompletność, przydatność dla rolnika lub operatora. Oceniający: promotor, specjalista od pogody kosmicznej albo porównanie z tekstem prognostyka NOAA (wariant D).

**Test statystyczny:** te same zdarzenia w obu wariantach, więc porównanie parami, np. test McNemara dla trafności przyczyny i test Wilcoxona dla ocen.

## 4. Zbiór zdarzeń testowych (propozycja domyślna)

- Wszystkie burze G3 i silniejsze od 2010 r. (DONKI zaczyna się w 2010 r.).
- Próba słabszych burz G1–G2 i dni spokojnych, żeby sprawdzić, czy system nie „wymyśla” przyczyn.
- Wszystkie znalezione przypadki zagłuszania GNSS (GUGiK, rtgms.pl).
- Szczegółowe studium przypadku: maj 2024 (pełny łańcuch DONKI, Forecast Discussion NOAA dostępny, skutki GNSS i Starlink udokumentowane).

Ograniczenie: teksty eksperckie NOAA (Forecast Discussion) są dopiero od 03/2024, więc porównanie z wariantem D obejmie tylko zdarzenia od tej daty.

## 5. Jedno zdanie do maila

> „Wyjaśnienia platformy porównam z wariantem bazowym opartym wyłącznie na danych liczbowych, na tych samych zdarzeniach z lat 2010–2026; poprawność przyczyny sprawdzę na niezależnych katalogach (lista ICME Richardsona i Cane'a, lista SSC), skutki na danych jonosferycznych IGS i orbitalnych, a jakość cytowań na podstawie odsetka twierdzeń potwierdzonych przez cytowane źródło.”
