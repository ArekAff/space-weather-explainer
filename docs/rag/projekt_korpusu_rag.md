# Baza wiedzy dla RAG: skład korpusu i reguły

Napisane 11.10.2026. Dotyczy wariantu C z [z_czym_porownac.md](../metodologia/z_czym_porownac.md) (dane + katalogi + RAG). Źródła, licencje i zakresy czasowe pochodzą z [dostep_do_zrodel_danych.xlsx](../zrodla_danych/dostep_do_zrodel_danych.xlsx). Liczby w sekcji 7 to szacunki, nie pomiar. Projekt bez kodu.

## 0. Najważniejsze decyzje w skrócie

1. **Korpus = teksty eksperckie pisane na bieżąco** (NOAA SWPC, komunikaty DONKI) + **mała warstwa wiedzy ogólnej** (otwarte artykuły przeglądowe, kilka polskich źródeł).
2. **Klucz odpowiedzi nigdy nie trafia do systemu**: lista ICME Richardsona i Cane'a, lista SSC, dane o skutkach (IGS TEC, EPN, orbity), komunikaty GUGiK o konkretnych zakłóceniach.
3. **Reguła odcięcia w czasie**: dla zdarzenia *e* dokument jest widoczny tylko wtedy, gdy `issued_at ≤ t0(e)`, gdzie `t0` to moment wykrycia anomalii. Liczy się **data publikacji**, nie okres, którego tekst dotyczy. Ta sama reguła obowiązuje katalogi w wariancie B i C.
4. **Wiedza ogólna** (przeglądy) jest zwolniona z odcięcia w czasie, ale fragmenty, które wspominają testowane zdarzenie, są dla niego maskowane.
5. Teksty zostają **w języku oryginału** (angielski), bez tłumaczenia. Wyjaśnienie jest po polsku, cytaty w oryginale.

## 1. Co wchodzi do korpusu

### 1a. Teksty NOAA SWPC z archiwum NCEI (główny korpus)

| Produkt | Od | Częstotliwość | Co daje dla RAG | Decyzja |
|---|---|---|---|---|
| **Forecast Discussion** | 03/2024 | co 12 h | Opisowy komentarz prognostyka: co się dzieje, czego się spodziewać, dlaczego | **Tak, priorytet** |
| **SGAS** (Solar and Geophysical Activity Summary) | 1996 | codziennie | Podsumowanie ostatniej doby: rozbłyski, CME, stan geomagnetyczny | **Tak** |
| **RSGA** (Report of Solar-Geophysical Activity) | 1966 | codziennie | Półustrukturyzowany raport z krótkimi opisami i prognozą | **Tak od 1996** (TXT); 1966–1995 tylko po teście OCR na próbce |
| **The Weekly** (PRF) | 1997 | co tydzień | Sekcje „Highlights” i prognoza na 27 dni | **Tak, tylko części opisowe**, bez tabel |
| 3-day Forecast / 3-day Geomagnetic Forecast | 03/2022, 11/2022 | co 12 h | Głównie liczby; wartościowe są tylko zdania „Rationale” | **Tak, tylko zdania uzasadnienia** |
| Event Reports, Solar Region Summary | 1996 | codziennie | Tabele, w praktyce katalog | **Nie** (to dane liczbowe, nie tekst; zaciera granicę między B i C) |
| Geoalert | 1996–05/2026 | codziennie | Kody | **Nie** |

Dlaczego RSGA od 1996, a nie od 1966: zdarzenia testowe są od 2010 r., ale platforma szuka podobnych sytuacji w całej historii. Teksty z czasu takiego historycznego analogu (np. 2003) są dozwolone przy wyjaśnianiu zdarzenia z 2024 r., więc 1996–2009 się przydaje. Starsze RSGA warto dodać tylko wtedy, gdy OCR na próbce da czytelny tekst.

### 1b. NASA CCMC DONKI: tylko część tekstowa

DONKI występuje w dwóch rolach i trzeba je rozdzielić:

| Część DONKI | Gdzie trafia |
|---|---|
| Pola strukturalne (typ zdarzenia, czasy, `linkedEvents`, prędkość CME) | Warstwa katalogów (wariant B i C), nie RAG |
| **Notifications** (komunikaty z `messageIssueTime`: FLR, CME, IPS, GST, SEP, MPC, RBE) | **RAG, priorytet**: pisane na bieżąco, z dokładnym czasem wydania, zawierają też prognozy przybycia CME z modelu WSA-ENLIL |
| **Weekly Space Weather Summary** (raporty tygodniowe) | **RAG** |
| Pole `note` we wpisach o zdarzeniach | RAG **tylko gdy wpis ma czas utworzenia** (`submissionTime`); inaczej poza trybem głównym |

Ważne: katalog M2M działa formalnie od 06/2020, a wcześniejsze wpisy dodał zespół SWRC później. Notatki we wpisach sprzed 06/2020 są więc retrospektywne i mogą zawierać wiedzę „po fakcie”. W trybie głównym (sekcja 3) nie wchodzą. Od kiedy dostępne są archiwalne notifications, trzeba sprawdzić w API (tego nie sprawdziłem).

### 1c. Wiedza ogólna: otwarte artykuły przeglądowe

Rdzeń z tabeli źródeł:
- Temmer M. (2021) *Space weather: the solar perspective*, LRSP 18:4.
- Richardson I.G. (2018) *Solar wind stream interaction regions throughout the heliosphere*, LRSP 15:1.

Kandydaci do dołączenia (wszystkie z Living Reviews in Solar Physics, open access; licencję każdego trzeba potwierdzić na stronie artykułu):
- Kilpua E., Koskinen H., Pulkkinen T. (2017) *Coronal mass ejections and their sheath regions in interplanetary space*, LRSP 14:5. Mechanizm burz od CME, rola osłony (sheath) i Bz.
- Webb D., Howard T. (2012) *Coronal Mass Ejections: Observations*, LRSP 9:3.

Do warstwy GNSS i satelitów warto dobrać 2–4 otwarte artykuły przeglądowe o scyntylacjach i zaburzeniach jonosfery (wpływ na RTK) oraz o oporze atmosfery dla satelitów LEO. Tych konkretnych tytułów nie wybrałem; kryterium jest w sekcji 5.

**Nie wchodzą** studia przypadków testowanych zdarzeń (np. artykuły o burzy z maja 2024 r. albo o utracie satelitów Starlink w lutym 2022 r.). To de facto gotowe wyjaśnienia, czyli klucz odpowiedzi. Mogą służyć ocenie eksperckiej, ale nie systemowi.

### 1d. Źródła polskie (mała warstwa kontekstu)

Nie znam polskiego odpowiednika operacyjnych tekstów NOAA, więc polska część korpusu będzie mała i pełni rolę kontekstu lokalnego, nie źródła przyczyn:
- **Ogólne** komunikaty GUGiK o zagłuszaniu GNSS w Polsce (np. ten z 26.02.2024) i opis metod portalu rtgms.pl. Uczą system, że zagłuszanie w Polsce w ogóle występuje i jak wygląda. Podlegają odcięciu w czasie.
- Otwarte artykuły polskich zespołów o jonosferze nad Polską i jej wpływie na pozycjonowanie (np. UWM Olsztyn, UPWr Wrocław, CBK PAN). Konkretne tytuły i licencje do wybrania.
- Dokumentacja ASG-EUPOS o usługach RTK, jeśli opisuje wpływ jonosfery.

**Nie wchodzą** komunikaty GUGiK o konkretnych przypadkach zakłóceń (np. Siedlce 30.06.2026): to kontrprzykłady w kluczu odpowiedzi.

## 2. Co zostaje poza korpusem i dlaczego

| Źródło | Powód |
|---|---|
| **Lista ICME Richardsona i Cane'a** | Klucz odpowiedzi dla przyczyny |
| **Lista SSC (Ebre/ISGI)** | Klucz odpowiedzi dla momentu początku burzy |
| Mapy TEC/ROTI (IGS), obserwacje EPN, orbity CelesTrak/Space-Track | Klucz odpowiedzi dla skutku; poza tym to liczby, nie tekst |
| Komunikaty GUGiK i rtgms.pl o konkretnych zakłóceniach | Klucz odpowiedzi dla kontrprzykładów |
| Studia przypadków testowanych zdarzeń | Gotowe wyjaśnienia (patrz 1c) |
| Prace opisujące listę R-C lub klasyfikujące konkretne burze (np. Richardson i Cane, ICME w cyklu 23) | Zawierają klucz w formie tekstu |
| Wikipedia, media, spaceweather.com, media społecznościowe | Brak wiarygodnej daty publikacji, ryzyko przecieku, prawa autorskie |
| Artykuły bez otwartej licencji | Licencja (sekcja 5); można je normalnie cytować w pracy, ale nie umieszczać w bazie |

**Dwie niespójności z mailem do promotora** (warto znać, zanim zacznie się budować):
1. W mailu lista SSC służy też jako cecha „czy dotarła fala uderzeniowa”. Jeśli SSC ma być niezależnym kluczem, ta cecha musi w wariancie C pochodzić z DONKI IPS. To i tak lepsze dla trybu real time, bo SSC jest aktualizowana kilka razy w roku.
2. W mailu lista R-C „pozwala odróżnić burze od CME i od szybkiego wiatru”. Jeśli R-C ma też trenować klasyfikator przyczyny, to tylko na zdarzeniach sprzed 2010 r. (1996–2009), a testowanie na 2010+. Wtedy klucz i dane uczące się nie pokrywają.

**Uwaga o Richardson 2018:** autor przeglądu jest współautorem klucza. Przegląd jest dobry jako wiedza o mechanizmach, ale fragmenty, które przypisują przyczynę konkretnym burzom, muszą być maskowane (sekcja 3c).

## 3. Reguła odcięcia w czasie

### 3a. Definicja

Dla każdego zdarzenia testowego *e* ustalamy `t0(e)`: moment, w którym system ma wyjaśnić zdarzenie.

- **Tryb główny (real time):** `t0` = pierwsza chwila, w której platforma wykryła anomalię (np. pierwsze przekroczenie progu Hp30 lub Kp). Dla kontrprzykładów i dni spokojnych: moment zgłoszenia zapytania o dany przedział.
- **Tryb pomocniczy (analiza wrażliwości):** `t0 + 24 h`. Pozwala sprawdzić, ile daje wiedza z doby po zdarzeniu. Ten tryb faworyzuje C, więc wyniki raportować osobno.

Dokument (fragment) jest widoczny dla zdarzenia *e*, gdy:

```
issued_at(d) ≤ t0(e)                      dla tekstów bieżących (1a, 1b, 1d)
oraz nie masked(d, e)                     dla wiedzy ogólnej (1c, 1d) — sekcja 3c
```

### 3b. Szczegóły, które łatwo przeoczyć

- **Liczy się data wydania, nie okres opisany.** The Weekly za tydzień z burzą wychodzi w kolejny poniedziałek, więc przy wyjaśnianiu tej burzy jest niewidoczny.
- **Precyzja czasu.** Produkty NOAA mają w nagłówku godzinę wydania (`:Issued: ... UTC`); parsujemy ją. Gdy znana jest tylko data, przyjmujemy koniec dnia (23:59 UTC), czyli tekst z dnia zdarzenia jest niewidoczny. To zachowawcze, przeciek jest gorszy niż utrata jednego tekstu.
- **Teksty poprawiane później** (notatki DONKI): obowiązuje czas utworzenia, a gdy go nie ma, dokument jest retrospektywny (`is_retrospective = true`) i nie wchodzi w trybie głównym. Dla danych zbieranych od teraz zapisujemy `fetched_at` i hash, żeby widzieć późniejsze zmiany.
- **Katalogi też.** Wpis DONKI GST dla testowanej burzy, utworzony po fakcie i połączony z CME przez `linkedEvents`, podaje gotową przyczynę. Odcięcie po `submissionTime` dotyczy więc także warstwy katalogów w B i C, inaczej B jest nieszczelne.
- **Wiedza modelu.** LLM może znać duże burze (np. maj 2024) z danych treningowych. To dotyczy A i C jednakowo, więc porównanie pozostaje uczciwe, ale wyniki bezwzględne są zawyżone. Warto pokazać osobno wyniki dla zdarzeń po dacie odcięcia wiedzy modelu.

### 3c. Maskowanie wiedzy ogólnej

Przeglądy i źródła polskie opisują mechanizmy, które były znane przed 2010 r., więc ich data publikacji nie tworzy anachronizmu. Mogą jednak opisywać konkretne testowane zdarzenie. Reguła:

- przy indeksowaniu z każdego fragmentu wyciągamy wzmianki o zdarzeniach: daty (np. „10–11 May 2024”), nazwy burz („Halloween storms”, „St. Patrick's Day storm”), numery regionów aktywnych NOAA, identyfikatory DONKI;
- fragment jest maskowany dla zdarzenia *e*, gdy wspomina datę w oknie `[początek(e) − 3 dni, koniec(e) + 3 dni]` albo nazwę tego zdarzenia;
- w pracy podajemy, ile fragmentów zamaskowano na zdarzenie (to też miara szczelności).

### 3d. Konsekwencja: korpus ma różną gęstość w czasie

| Okres | Teksty bieżące dostępne w trybie głównym |
|---|---|
| 2010 – 05/2020 | RSGA, SGAS, The Weekly, DONKI notifications (od kiedy, do sprawdzenia) |
| 06/2020 – 02/2024 | jw. + notatki DONKI z czasem utworzenia; od 03/2022 uzasadnienia 3-day Forecast |
| od 03/2024 | jw. + **Forecast Discussion** |

Wyniki wariantu C warto więc raportować osobno dla tych trzech okresów. Inaczej poprawa w ostatnim okresie (bogaty korpus) może zostać przypisana RAG ogólnie.

## 4. Metadane dokumentu i fragmentu

Potrzebne do cytowania, do reguły odcięcia i do odtwarzalności.

| Pole | Przykład | Po co |
|---|---|---|
| `doc_id` | `noaa-fd-2024-05-10T1230Z` | Stały identyfikator |
| `source` | `NOAA_SWPC` / `CCMC_DONKI` / `LRSP` / `GUGIK` / … | Grupowanie, licencja |
| `product` | `forecast_discussion`, `sgas`, `rsga`, `weekly`, `donki_notification`, `review` | Filtry, raport |
| `doc_class` | `realtime_expert` / `background` | Która reguła odcięcia obowiązuje |
| `title` | „Forecast Discussion” | Cytat |
| `author_org` | NOAA SWPC; dla artykułów lista autorów | Cytat |
| `issued_at` + `issued_precision` | `2024-05-10T12:30Z`, `minute` / `day` | Reguła odcięcia |
| `coverage_start`, `coverage_end` | okres opisany w tekście | Wyszukiwanie po czasie, wykrywanie przecieków |
| `is_retrospective` | `true` dla notatek DONKI bez czasu utworzenia | Tryb główny vs pomocniczy |
| `url` | stały adres w archiwum NCEI / API DONKI / DOI | Weryfikowalny link w cytacie |
| `doi` | dla artykułów | Bibliografia |
| `license` | `public-domain-US-gov`, `CC-BY-4.0`, … | Sekcja 5 |
| `citation` | gotowy ciąg do bibliografii | Cytat bez ręcznej pracy |
| `language` | `en` / `pl` | Strategia językowa |
| `fetched_at`, `sha256` | | Odtwarzalność, wykrywanie zmian |
| `ocr`, `ocr_quality` | dla starych RSGA | Ocena jakości |
| **Fragment:** `chunk_id`, `section`, `char_start`, `char_end`, `page` | sekcja „Geospace” w Forecast Discussion; strona w przeglądzie | Cytat do konkretnego fragmentu i sprawdzenie, czy go potwierdza |
| **Fragment:** `mentioned_events` | daty, nazwy burz, numery regionów | Maskowanie (3c) |

Fragmenty dzielimy wzdłuż naturalnych sekcji produktu: Forecast Discussion i RSGA po sekcjach (aktywność Słońca, cząstki, wiatr słoneczny, geosfera), The Weekly na „Highlights” i prognozę, jeden komunikat DONKI = jeden fragment, przeglądy po podrozdziałach z numerem strony. Dzięki temu każdy cytat ma czas wydania i nazwę sekcji.

**Postać cytatu w wyjaśnieniu:** `[NOAA SWPC, Forecast Discussion, 2024-05-10 12:30 UTC, sekcja Geospace]` z linkiem. W bibliografii pracy: archiwum jako jedna pozycja (NOAA SWPC przez NCEI, data dostępu) zamiast setek raportów; artykuły osobno.

## 5. Licencje i warunki cytowania

| Źródło | Licencja | Wolno w bazie RAG? | Jak cytować / podziękować |
|---|---|---|---|
| Teksty NOAA SWPC (NCEI) | Dane rządu USA, w praktyce domena publiczna; The Weekly wprost bez praw autorskich | Tak | „NOAA Space Weather Prediction Center, archiwum NCEI”, data dostępu |
| DONKI | „As is”, Experimental Research Information | Tak | Podziękowanie według polityki CCMC; w pracy zaznaczyć, że dane są eksperymentalne. CCMC prosi o kontakt przy pracach walidacyjnych, więc krótki e-mail do CCMC jest zalecany |
| Living Reviews in Solar Physics | CC BY 4.0 (potwierdzić na stronie każdego artykułu) | Tak | Pełny opis bibliograficzny z DOI |
| Treści gov.pl | CC BY-SA 4.0 | Tak | Źródło i link |
| geoportal.gov.pl | Licencja nie podana (regulamin) | Tylko ogólne komunikaty, z podaniem źródła | Źródło i link |

**Reguła dla innych artykułów:** do bazy wchodzą tylko teksty na licencji CC (BY, BY-SA, BY-NC, BY-NC-ND). Fragmenty przechowujemy dosłownie i z cytatem, bez tłumaczenia i zmian, co pasuje nawet do klauzuli ND, a NC nie przeszkadza w pracy dyplomowej. Artykuły bez otwartej licencji można cytować w tekście pracy, ale nie umieszczać w bazie. Granicę dozwolonego użytku do celów badawczych warto potwierdzić z promotorem, ale przy tej regule nie jest potrzebna.

**Licencje NC w kluczu odpowiedzi** (SSC, Belsk) nie dotyczą korpusu, bo te źródła do niego nie trafiają.

**Udostępnienie korpusu:** wszystkie źródła w bazie pozwalają na rozpowszechnianie z podaniem źródła, więc zamrożoną wersję korpusu (lista `doc_id` + hash, a teksty NOAA i DONKI w całości) można dołączyć do pracy jako załącznik. To wzmacnia odtwarzalność.

## 6. Strategia językowa

- Korpus zostaje w języku oryginału. Tłumaczenie psułoby weryfikację cytatów (porównujemy twierdzenie z dosłownym fragmentem), a przy CC BY-ND byłoby utworem zależnym.
- Zapytania do wyszukiwarki po angielsku (z opisu anomalii); model osadzeń wielojęzyczny, żeby polskie źródła też były znajdowane.
- Wyjaśnienie dla odbiorcy po polsku, cytowane fragmenty w oryginale, ewentualnie z polskim streszczeniem obok.

## 7. Oczekiwany rozmiar (szacunek)

Okres rdzenia: 1996 – 10/2026. Liczby tokenów to moje przybliżenie, do sprawdzenia na próbce jednego miesiąca.

| Część | Dokumenty | Tokeny (ok.) |
|---|---|---|
| Forecast Discussion (03/2024 – 10/2026, co 12 h) | ~1 900 | 1–1,5 mln |
| SGAS (1996–2026, codziennie) | ~11 000 | 3–5 mln |
| RSGA (1996–2026, codziennie) | ~11 000 | 6–10 mln |
| The Weekly, części opisowe (1997–2026) | ~1 550 | 1–2 mln |
| Uzasadnienia 3-day Forecast (03/2022 – 2026) | ~3 300 | 0,2 mln |
| DONKI notifications i raporty tygodniowe | kilka tysięcy (do sprawdzenia) | 2–4 mln |
| Notatki DONKI z czasem utworzenia | ~kilka tysięcy krótkich | <1 mln |
| Przeglądy (4–8 artykułów) | 4–8 | 0,4–0,8 mln |
| Polskie źródła | dziesiątki | <0,1 mln |
| **Razem** | **~30–35 tys.** | **~15–25 mln** |

Przy fragmentach rzędu 300–500 tokenów to ok. 40–70 tys. fragmentów. Indeks wektorowy tej wielkości (np. 1024 wymiary, float32) zajmuje kilkaset MB, czyli mieści się na laptopie. Ewentualne RSGA 1966–1995 po OCR dodałoby ok. 11 tys. dokumentów.

Dla jednego zdarzenia testowego widoczna część korpusu jest mniejsza (wszystko sprzed `t0`), a najistotniejsze są teksty z kilku dni przed `t0`.

## 8. Do sprawdzenia przed budową

1. Od kiedy API DONKI zwraca archiwalne notifications i które typy wpisów mają `submissionTime`.
2. Format nagłówków (godzina wydania) w SGAS, RSGA i The Weekly w całym okresie 1996–2026.
3. Próbka OCR dla RSGA sprzed 1996 r., jeśli chcesz rozszerzyć korpus wstecz.
4. Licencje konkretnych przeglądów i polskich artykułów (stopka strony artykułu).
5. E-mail do CCMC w sprawie użycia DONKI w walidacji.
6. Decyzja o `t0`: domyślnie przyjąłem moment wykrycia anomalii przez platformę.
