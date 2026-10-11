# Wybór obszaru biznesowego: porównanie trzech kandydatów

Kontekst: prof. Surma (21 maja) poprosił o wskazanie jednego obszaru biznesowego dla platformy „real time + RAG”. Obecny szkic maila wymienia naraz trzy grupy odbiorców: użytkowników GNSS (rolnictwo precyzyjne), operatorów satelitów i sieci energetyczne. Poniżej porównanie tych trzech na czterech kryteriach.

Liczby i źródła pochodzą z obecnego szkicu maila. Ocena „czy dane wystarczą” to moja analiza listy 12 źródeł z sekcji 5 maila, nie test dostępu (ten trwa w osobnym wątku).

## Podsumowanie

| | **A. Rolnictwo precyzyjne / użytkownicy GNSS (RTK)** | B. Operatorzy satelitów (LEO, np. Starlink) | C. Polska sieć energetyczna |
|---|---|---|---|
| **Kto decyduje** | Operator maszyn lub usługodawca rolnictwa precyzyjnego; po stronie państwa operator ASG-EUPOS (GUGiK) | Inżynier dynamiki lotu / zespół operacyjny konstelacji | Dyspozytor operatora sieci (PSE, OSD typu TAURON) |
| **Jaka decyzja** | Kontynuować prace polowe z RTK czy wstrzymać; czy przyczyną utraty precyzji jest pogoda kosmiczna, zagłuszanie czy lokalna usterka; jak długo potrwa | Przesunąć start, podnieść orbitę, przejść w tryb bezpieczny; przypisać anomalię przyczynie | Przekonfigurować sieć, przesunąć prace serwisowe, zwiększyć rezerwy na czas burzy |
| **Mierzalny koszt błędu** | Maj 2024: 53 mln – 1,29 mld USD utraconych przychodów z kukurydzy w USA (Kansas State); w Polsce ok. 48 tys. kont ASG-EUPOS | Luty 2022: 38 z 49 satelitów Starlink utraconych przy burzy G1; analiza jednej awarii ok. 1 mln USD | Wzrost liczby awarii w sieci TAURON po burzach (Gil i in. 2021), ale bez kwot w złotówkach |
| **Dane o przyczynie (Kp, NOAA, OMNI, DONKI, katalogi)** | Tak | Tak, a zdarzenia protonowe NOAA szczególnie pasują | Tak, a magnetometr w Belsku daje lokalne dB/dt |
| **Dane o skutku (do weryfikacji)** | **Tak: stacje EPN w Polsce (błąd pozycji) + komunikaty GUGiK o zagłuszaniu jako kontrprzykłady** | Nie ma w liście: brak otwartej bazy anomalii satelitów | Nie ma w liście: dane o awariach TAURON nie są publiczne |
| **Polski kontekst** | Silny | Słaby | Silny, ale niesprawdzalny bez danych operatora |

## Rekomendacja: A, rolnictwo precyzyjne i inni użytkownicy GNSS w Polsce

1. To jedyny obszar, w którym z 12 wybranych otwartych źródeł da się sprawdzić zarówno przyczynę, jak i skutek. EPN pokazuje, o ile spadła dokładność pozycji, a komunikaty GUGiK o zagłuszaniu dają przypadki „to nie była pogoda kosmiczna”. Dzięki temu pytanie „pogoda kosmiczna czy zagłuszanie?” staje się mierzalnym zadaniem klasyfikacji, co wzmacnia ewaluację pracy.
2. Decyzja jest konkretna i powtarzalna (pracować czy czekać, ok. 74 dni burzowych w roku), a koszt błędu ma oszacowanie w literaturze.
3. Ma polskiego odbiorcę (ASG-EUPOS, GUGiK), co dobrze wygląda w pracy na polskiej uczelni.

Ryzyka, które warto znać:
- Przetworzenie danych EPN (pliki RINEX → błąd pozycji) to dodatkowa praca. Prostsza droga: gotowe szeregi współrzędnych stacji z EPN zamiast własnego przetwarzania.
- Indeks Kp słabo opisuje jonosferę, która bezpośrednio psuje GNSS. Może być potrzebne jedno dodatkowe źródło (np. mapy TEC jonosfery z IGS). To mój wniosek, nie coś sprawdzonego.

Dlaczego nie B: najbardziej spektakularny przykład (Starlink), ale bez otwartych danych o anomaliach nie da się sprawdzić, czy wyjaśnienia platformy są trafne, a decydent jest poza Polską.

Dlaczego nie C: dobry polski wątek naukowy, ale bez danych o awariach od operatora sieci warstwa „skutku” zostaje nieweryfikowalna, a skutki burz w Polsce (średnie szerokości) są słabsze.

Satelity i energetyka mogą zostać w pracy jako wzmianka w motywacji („te same mechanizmy dotyczą też…”), bez rozszerzania zakresu.

## Co zmieni się w mailu, jeśli wybierzesz A

W sekcji 1 zdanie „Wybrałem pogodę kosmiczną i jej wpływ na użytkowników nawigacji satelitarnej, operatorów satelitów oraz sieci energetyczne” zawęża się do użytkowników GNSS, a temat roboczy dostaje dopisek „…na przykładzie wpływu pogody kosmicznej na precyzyjne pozycjonowanie GNSS”. Reszta maila (przykład z maja 2024, dane) pasuje bez zmian.

## Decyzja (11.10.2026)

Arek wybrał A + B: użytkownicy GNSS (rolnictwo precyzyjne) oraz operatorzy satelitów. Energetyka zostaje jako kontekst w motywacji. Luka dla B: wśród 12 źródeł nie ma otwartych danych o anomaliach satelitów, więc weryfikacja skutków dla B wymaga dodatkowego źródła.
