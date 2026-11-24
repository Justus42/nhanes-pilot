# Offene Fragen an die Spezifikation

Jede Frage mit Datum, Anlass und Beleg. Entscheidung durch Justus; Auswerter A ändert SPEC.md nicht.

## 1. Standardfehler 1,2 und 0,6 gehören zur altersadjustierten Schätzung (23.11.2026, Auswerter A)

**Anlass:** SPEC.md, Abend 2, lässt offen, zu welcher Schätzung die beiden Standardfehler gehören, und verweist auf Tabelle 2 des NHSR Nr. 158. Die Stufen nennen „2. Rohe Prävalenzen und Standardfehler“ und „4. Altersadjustierte Prävalenzen und Standardfehler“.

**Beleg:** NHSR Nr. 158, Tabelle 2, Anmerkung: „Outcomes for adults and older adults were age adjusted by the direct method to the projected U.S. Census 2000 population.“ Bei schwerer Adipositas steht in Tabelle 2 der altersadjustierte Wert „9.2 (8.0–10.6)“ mit dem Standardfehler 0.6, nicht der rohe Wert 9.0 (7.8–10.3). Wörtliche Zitate in `LOG.md`.

**Frage:** Soll SPEC.md als Klarstellung festhalten, dass die Standardfehler 1,2 (Adipositas, gesamt) und 0,6 (schwere Adipositas, gesamt) zur **altersadjustierten** Schätzung gehören und in **Stufe 4** geprüft werden? Dann haben alle rohen Standardfehler kein externes Ziel und stehen auf `extern nicht geprüft`. Zielwerte und Toleranzen ändern sich dadurch nicht.

**Status:** beantwortet durch SPEC.md Version 2.1 (Pull Request 3). Die Standardfehler 1,2 und 0,6 gehören zur altersadjustierten Schätzung und werden in Stufe 4 geprüft.

## 2. Standardanteile: vier statt sechs Nachkommastellen (23.11.2026, Auswerter A)

**Anlass:** Prüfauftrag aus SPEC.md, Abend 2 („A prüft die drei Werte vor Abend 2 gegen die NCHS-Quelle. Weichen sie ab, hält A an.“).

**Beleg:** Klein und Schoenborn, Healthy People 2010 Statistical Notes Nr. 20 (NCHS, 2001), Tabelle 2, Distribution #12: 20–39 Jahre 0.396579, 40–59 Jahre 0.371795, ab 60 Jahre 0.231626. SPEC.md nennt 0,3966, 0,3718 und 0,2316.

**Einschätzung von A:** Kein Widerspruch. Die Werte der Spezifikation sind die auf vier Stellen gerundeten Quellwerte, und beide Fassungen summieren sich zu 1. A und B nutzen dieselben festen Werte, der Vergleich A gegen B ist also nicht betroffen. Gegenüber dem Report kann die Rundung den Wert nur sehr wenig verschieben. Das ist hier nicht nachgerechnet.

**Frage:** Bleibt es bei den vier Stellen der Spezifikation, oder sollen beide Auswerter die sechs Stellen der Quelle verwenden? A rechnet bis zur Entscheidung mit den Werten aus SPEC.md.

**Status:** beantwortet durch SPEC.md Version 2.1 (Pull Request 3). Es gelten die sechsstelligen Werte der Quelle: 0,396579, 0,371795, 0,231626.

## 3. Konfidenzintervall bei p = 0 oder p = 1 (24.11.2026, Auswerter A)

**Anlass:** Prüfung der KI-Formel gegen NCHS Series 2 Nr. 175 vor Abend 2 (Zusatzauftrag 4).

**Beleg:** Series 2 Nr. 175, Seite 3, wörtlich: „If the number of numerator events is 0 or equal to the denominator (the complement of 0 events), the estimated proportion will be 0 or 1, respectively. As a result, the estimated variance of the proportion will be 0, and the effective sample size will be undefined. In these cases, the sample size should be used to determine whether the minimum sample size criterion is met, and it should also be used for CIs and other computations that include the effective sample size.“ SPEC.md, Abend 2, schreibt m = min(n, p · (1 − p) / V · …) ohne diesen Fall. Bei V = 0 ist der Ausdruck nicht definiert.

**Einschätzung von A:** Kein Widerspruch zur Formel, sondern ein ungeregelter Randfall. Für Abend 2 ohne Folge, weil keine der sechs rohen Prävalenzen 0 oder 1 sein kann. Das Auswertungsskript bricht in diesem Fall ab, statt zu raten. Der Rest der Formel ist gegen die Beispiele der Standards geprüft (`LOG.md`, 24.11.2026).

**Frage:** Soll SPEC.md als Klarstellung ergänzen: „Ist p = 0 oder p = 1, gilt m = n“? Nicht blockierend für Abend 2.

**Status:** beantwortet am 24.11.2026 durch Justus: keine Änderung an SPEC.md. Der Fall kann im Pilot nicht eintreten, das Skript bricht ab. Die Regel wird im Protokoll der Hauptanalyse festgelegt.

## 4. Cockcroft-Gault und DuBois nicht gegen die Originalarbeit geprüft (24.11.2026, Auswerter A, Abend 4)

**Anlass:** SPEC.md, Abend 4: „Jeder Auswerter prüft die Formeln gegen die Originalarbeit und nennt sie in `LOG.md`.“

**Beleg:** CKD-EPI 2021 ist gegen Tabelle 2 der Originalarbeit geprüft und stimmt (`LOG.md`, 24.11.2026, Abend 4). An die Originale von Cockcroft und Gault (Nephron 1976) und von DuBois und DuBois (Arch Intern Med 1916) kommt A nicht heran: Der Netzwerk-Proxy der Cloud-Sitzung sperrt `karger.com`, `doi.org`, `jamanetwork.com` und `archive.org`. PubMed Central hat keinen Volltext. Das PubMed-Abstract von Cockcroft und Gault zeigt die Formel nicht („(see article)“), belegt nur „15% less in females“. Aus dem Gedächtnis prüft A nicht.

**Frage:** Darf A mit diesen zwei Formeln zählen, obwohl sie nicht gegen das Original geprüft sind? Oder sollen erst die Hosts in der Umgebung freigegeben oder die Originale (PDF) ins Repo gelegt werden? Das Karger-PDF ist vermutlich kostenpflichtig, die Arbeit von 1916 gemeinfrei.

**Status:** offen, vor dem Zählen zu entscheiden.

## 5. Bezeichnerspalte und Reihenfolge der Ausgabedateien von Abend 4 (24.11.2026, Auswerter A)

**Anlass:** SPEC.md verlangt, dass `results/A/abend4_fallzahlen.csv` und `results/B/abend4_fallzahlen.csv` „in jeder Zelle exakt übereinstimmen“. Die Spezifikation nennt die acht Zahlenspalten, aber nicht den Namen der Spalte mit dem Zeilennamen und nicht die Reihenfolge der Zeilen. Für `abend4_personen_*.csv` fehlen der Name der SEQN-Spalte und die Reihenfolge der Spalten.

**Umsetzung von A, falls nichts anderes entschieden wird:** Erste Spalte `zeile`, Zeilen in der Reihenfolge der Spezifikation: METFORMIN, GABAPENTIN, PREGABALIN, DOAK\_GESAMT, ALLOPURINOL, SITAGLIPTIN, SPIRONOLACTONE, APIXABAN, RIVAROXABAN, DABIGATRAN, EDOXABAN, GESAMT; danach die acht Spalten in der Reihenfolge der Tabelle „Ausgabe“. Personendatei: `SEQN`, `analysegruppe`, die elf Trefferspalten in derselben Reihenfolge, `kat_ckdepi`, `kat_deindex`, `kat_cg`; ein leerer Wert ist ein leeres Feld.

**Frage:** Reicht es, wenn `vergleich.py` Zeilen und Spalten über ihre Namen zuordnet? Dann beeinflussen Spaltenname und Reihenfolge das Ergebnis nicht. Nicht blockierend für A.

**Status:** offen.

## 6. „Ein Gewichtskriterium gibt es hier nicht“ (24.11.2026, Auswerter A)

**Anlass:** SPEC.md, Abend 4, Analysegruppe. „Gewicht“ kann das Stichprobengewicht `WTMECPRP` oder das Körpergewicht `BMXWT` meinen.

**Lesart von A:** gemeint ist das Stichprobengewicht, also keine Bedingung `WTMECPRP > 0`. `BMXWT` vorhanden und größer null wird im selben Satz ausdrücklich verlangt. Laut `LOG.md` (Abend 2) haben alle 14.300 Personen mit `RIDSTATR = 2` ein `WTMECPRP > 0`. Die Lesart ändert die Analysegruppe also nicht.

**Frage:** Ist die Lesart richtig? Nicht blockierend.

**Status:** offen.

## 7. Rückführbarkeit des Kreatinins auf IDMS (24.11.2026, Auswerter A)

**Anlass:** CKD-EPI 2021 setzt standardisiertes Kreatinin voraus. Die gesicherte Seite zu P\_BIOPRO beschreibt eine enzymatische Methode auf dem Roche Cobas 6000, die „agrees well with recognized HPLC methods“. IDMS oder Rückführbarkeit nennt sie nicht (Suche nach „IDMS“, „traceab“, „isotope“, „standardiz“ ohne Treffer).

**Einschätzung von A:** Kein Widerspruch zur Spezifikation. Die verlangt `LBXSCR` unverändert, solange die CDC keine Umrechnung vorschreibt, und das tut sie nicht (`LOG.md`, Abend 4). A rechnet nichts um.

**Frage:** Soll die Rückführbarkeit vor der Hauptanalyse in einer Quelle der CDC belegt werden? Für den Pilot nicht blockierend.

**Status:** offen.
