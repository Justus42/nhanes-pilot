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

**Status:** offen.
