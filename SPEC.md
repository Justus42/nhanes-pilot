# NHANES-Pilot: Spezifikation für die Abende 1–4

Version 2 vom 23.11.2026 · Justus Jeserigk

Version 2 übernimmt die 18 Befunde des Reviews durch GPT 6.2 Astra (`review/openrouter/spec-v1-astra.md`). Die Änderungen stehen mit Begründung in `LOG.md`. Zielwerte, Toleranzen und die Schwelle der Entscheidungsregel sind unverändert.

## Zweck und Abbruchkriterium

Der Pilot klärt in vier Abenden, ob eine eigene NHANES-Auswertung vertrauenswürdig ist und ob das Projekt „Nierenformeln und Dosierungskategorien“ (G3) genug Fälle hat. Ein Forschungsergebnis liefert er noch nicht.

Er beantwortet drei Fragen:

1. Lassen sich die NHANES-Dateien des Zyklus 2017–März 2020 in der Arbeitsumgebung laden?
2. Trifft die Auswertung eine veröffentlichte CDC-Kennzahl samt Konfidenzintervall?
3. Wie viele Befragte nehmen die Zielwirkstoffe, insgesamt und bei eingeschränkter Nierenfunktion?

**Abbruch:** Das Projekt endet, wenn die Dateien nicht ladbar sind oder wenn die Positivkontrolle nach zwei Abenden nicht innerhalb der Toleranz liegt. Nachbessern an der Toleranz ist nicht erlaubt.

**Arbeitsumgebung:** eine Cloud-Sitzung mit freigegebenen CDC-Domains oder der PC. Justus legt das vor Abend 1 fest. Die Wahl steht in `LOG.md`.

## Regeln für beide Auswerter

Zwei Auswerter rechnen dieselbe Spezifikation getrennt nach. Auswerter A ist Claude Code und schreibt in R mit dem Paket `survey`. Auswerter B ist ein Gemini-Modell und schreibt in Python nur mit `pandas`, `numpy` und `scipy`, ohne Survey-Bibliothek.

1. **Unabhängigkeit.** A sieht weder Code noch Ergebnisse von B, und umgekehrt. B bekommt nur dieses Dokument.
2. **Kein fremder Eingriff.** Claude Code darf das Skript von B ausführen, aber nicht ändern. Fehlermeldungen gehen wörtlich an Gemini zurück.
3. **Rohdaten bleiben unverändert.** Sie liegen in `data/raw/`, jede Datei mit SHA-256-Prüfsumme in `data/raw/CHECKSUMS.txt`.
4. **Jede Zahl kommt aus einem Skriptlauf.** Nichts wird von Hand abgetippt. Ergebnisse landen als CSV in `results/A/` und `results/B/`.
5. **Survey-Design immer vollständig.** Gewicht `WTMECPRP`, Stratum `SDMVSTRA`, Cluster `SDMVPSU`. Teilgruppen werden als Domäne gerechnet. Zeilen außerhalb der Teilgruppe werden nicht vor der Varianzschätzung gelöscht.
6. **Kein Hinbiegen.** Weicht ein Wert vom Ziel ab, wird die Ursache in der CDC-Dokumentation gesucht. Jede Änderung am Skript steht mit Grund und Datum in `LOG.md`.
7. **Nicht raten.** Ist die Spezifikation unklar oder widerspricht sie der CDC-Dokumentation, hält der Auswerter an und schreibt die Frage in `OFFEN.md`.
8. **Keine Re-Identifikation.** Die NHANES-Daten werden nur statistisch ausgewertet und mit keinen anderen Personendaten verknüpft.

## Gemeinsame Definitionen

Diese sechs Festlegungen gelten an allen Abenden und für beide Auswerter.

1. **Schwangerschaft.** Ausgeschlossen wird nur ein dokumentierter Status `RIDEXPRG = 1`. Fehlende Angabe und Code 3 bleiben eingeschlossen. In R heißt das `is.na(RIDEXPRG) | RIDEXPRG != 1`. Die Variable ist laut CDC nur für Frauen von 20 bis 44 Jahren belegt. Die Gruppe heißt deshalb „ohne dokumentierte Schwangerschaft“.
2. **Fehlende Werte.** Jede Bedingung wird als vollständige Ja/Nein-Maske gebildet. Ein fehlender Wert erfüllt keine Bedingung. Einzige Ausnahme ist die Schwangerschaftsregel.
3. **Alter.** `RIDAGEYR` wird unverändert verwendet. Personen ab 80 gehen mit genau 80 in alle Formeln ein. Sie werden weder ausgeschlossen noch geschätzt.
4. **Designbasis.** Für alle gewichteten Schätzungen bilden die untersuchten Personen aus P\_DEMO (`RIDSTATR = 2`) mit `WTMECPRP > 0` das Design. Andere Dateien werden je Person angefügt, ohne Personen zu verlieren.
5. **Vergleiche.** Verglichen werden ungerundete Werte in Prozentpunkten. Die CSV-Dateien enthalten die volle Rechengenauigkeit. „Bestanden“ heißt: Abweichung kleiner oder gleich der Toleranz.
6. **Aussagekraft.** Stimmen A und B überein, ist ein Programmierfehler unwahrscheinlich. Fehler in dieser Spezifikation deckt der Vergleich nicht auf. Dafür gibt es die Zielwerte des Reports und die Rechentests unter Abend 4.

## Abend 1 – Daten laden

Vier Dateien aus dem Zyklus 2017–März 2020 werden geladen und unverändert abgelegt. Die Zeilenzahl jeder Datei muss exakt zur CDC-Dokumentation passen.

| Datei | Inhalt | Zeilen laut CDC | Benötigte Variablen |
| --- | --- | --- | --- |
| [P\_DEMO.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm) | Demografie, Gewichte, Design | 15.560 | SEQN, RIDSTATR, RIDAGEYR, RIAGENDR, RIDEXPRG, WTMECPRP, SDMVSTRA, SDMVPSU |
| [P\_BMX.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm) | Körpermaße | 14.300 | SEQN, BMXWT (kg), BMXHT (cm), BMXBMI (kg/m²) |
| [P\_BIOPRO.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BIOPRO.htm) | Serumchemie | 10.409 | SEQN, LBXSCR (Kreatinin, mg/dL) |
| [P\_RXQ\_RX.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_RXQ_RX.htm) | Verordnete Medikamente, eine Zeile je Medikament | 32.962 | SEQN, RXDUSE, RXDDRUG, RXDDRGID, RXDDAYS |

**Download:** Die Dateien liegen vermutlich im selben Verzeichnis wie ihre Dokumentation, also `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<NAME>.xpt`. Das Muster ist nicht getestet. Schlägt es fehl, führt die NHANES-Seite des Zyklus zu den Dateien.

**Dokumentation sichern:** Claude Code speichert zusätzlich die vier verlinkten Dokumentationsseiten als HTML in `docs/cdc/`, mit Abrufdatum im Dateinamen. Von Hand muss nichts gespeichert werden.

**Hinweise aus der CDC-Dokumentation:**

- Das Alter ist ab 80 Jahren auf 80 gedeckelt.
- `RIDSTATR = 2` heißt befragt und untersucht (14.300 Personen). Nur diese haben ein Untersuchungsgewicht größer null.
- `SEQN` wiederholt sich in P\_RXQ\_RX. Vor jedem Zusammenführen wird auf Personenebene verdichtet.
- In `RXDDRUG` stehen 55555 für unbekannt, 77777 für verweigert und 99999 für weiß nicht.
- Kombinationspräparate nennen ihre Wirkstoffe alphabetisch in einem Feld.

**Fertig ist Abend 1, wenn** `results/A/abend1_dateien.csv` für jede Datei Zeilenzahl, Spaltenzahl und Prüfsumme enthält und alle vier Zeilenzahlen stimmen.

## Abend 2 – Positivkontrolle

Auswerter A rechnet die Adipositas-Prävalenz Erwachsener nach, die das NCHS für denselben Zyklus veröffentlicht hat. Quelle der Zielwerte ist der [National Health Statistics Report Nr. 158](https://stacks.cdc.gov/view/cdc/106273/cdc_106273_DS1.pdf), Tabellen 2, 5 und 6.

**Analysegruppe:** Personen der Designbasis mit Alter ab 20 Jahren (`RIDAGEYR >= 20`), gültigem `BMXBMI` und ohne dokumentierte Schwangerschaft. Erwartet werden 8.295 Personen, davon 4.051 Männer und 4.244 Frauen.

**Definitionen:** Adipositas ist `BMXBMI >= 30`, schwere Adipositas `BMXBMI >= 40`.

| Kennzahl | Gruppe | Roh, % (95-%-KI) | Altersadjustiert, % (95-%-KI) |
| --- | --- | --- | --- |
| Adipositas | Gesamt | 41,9 (39,4–44,3) | 41,9 (39,4–44,3) |
| Adipositas | Männer | 41,6 (37,4–45,8) | 41,8 (37,7–45,9) |
| Adipositas | Frauen | 42,1 (39,6–44,8) | 41,8 (39,3–44,4) |
| Schwere Adipositas | Gesamt | 9,0 (7,8–10,3) | 9,2 (8,0–10,6) |
| Schwere Adipositas | Männer | 6,4 (5,1–8,0) | 6,6 (5,3–8,1) |
| Schwere Adipositas | Frauen | 11,4 (9,7–13,3) | 11,7 (10,0–13,7) |

Der Report nennt Standardfehler nur für die Gesamtgruppe: 1,2 (Adipositas) und 0,6 (schwere Adipositas). Zu welcher Schätzung sie gehören, klärt Tabelle 2 des Reports vor Abend 2.

**Was extern geprüft wird:**

- die drei Fallzahlen,
- die zwölf Prävalenzen,
- die sechs rohen Konfidenzintervalle,
- die zwei Standardfehler der Gesamtgruppe, sobald sie zugeordnet sind.

Alle übrigen Standardfehler haben kein externes Ziel. In der Ergebnisdatei steht dort `extern nicht geprüft`, und es zählt der Vergleich A gegen B. Altersadjustierte Konfidenzintervalle sind kein Kriterium.

**Methode:**

- Design in R: `svydesign(ids = ~SDMVPSU, strata = ~SDMVSTRA, weights = ~WTMECPRP, nest = TRUE, data = <Designbasis>)`. Keine Endlichkeitskorrektur, Standardoptionen des Pakets. Teilgruppen entstehen über `subset()` auf dem Designobjekt.
- Hat ein Stratum der Designbasis nur einen Cluster, hält A an und schreibt das in `OFFEN.md`.
- Standardfehler per Taylor-Linearisierung.
- Altersadjustierung direkt auf die projizierte US-Bevölkerung 2000, Altersgruppen 20–39, 40–59 und ab 60. Beide Auswerter verwenden fest die Standardanteile **0,3966, 0,3718 und 0,2316**, für Gesamt, Männer und Frauen gleich. A prüft die drei Werte vor Abend 2 gegen die NCHS-Quelle. Weichen sie ab, hält A an.
- Altersadjustiert in R: die Anteile der drei Altersgruppen gemeinsam schätzen, mit vollständiger Kovarianzmatrix (`svyby(..., covmat = TRUE)`), und mit `svycontrast` zur festen Summe verrechnen.

**Konfidenzintervall der rohen Prävalenzen** nach Korn und Graubard in der Fassung des NCHS, ausgeschrieben:

- p ist der Anteil auf der Skala 0 bis 1, V seine Varianz.
- n ist die ungewichtete Personenzahl der Teilgruppe.
- f ist die Zahl der Cluster minus die Zahl der Strata, jeweils nur solche mit Personen der Teilgruppe.
- m = min(n, p · (1 − p) / V · (t(0,975; n − 1) / t(0,975; f))²). Dabei ist t(0,975; k) das 97,5-%-Quantil der t-Verteilung mit k Freiheitsgraden.
- x = m · p, ohne Rundung.
- Untere Grenze: 2,5-%-Quantil der Beta-Verteilung mit den Parametern x und m − x + 1.
- Obere Grenze: 97,5-%-Quantil der Beta-Verteilung mit den Parametern x + 1 und m − x.

Maßgeblich ist diese Formel. A darf zusätzlich `svyciprop(..., method = "beta")` ausgeben. Unterscheiden sich beide, steht das in `LOG.md`.

**Vier Stufen, in dieser Reihenfolge:**

1. Fallzahlen: 8.295, 4.051 und 4.244 müssen exakt stimmen.
2. Rohe Prävalenzen und Standardfehler.
3. Konfidenzintervalle der rohen Prävalenzen.
4. Altersadjustierte Prävalenzen und Standardfehler.

**Toleranz, vorab festgelegt:**

| Größe | Erlaubte Abweichung |
| --- | --- |
| Fallzahlen | keine |
| Prävalenz | 0,1 Prozentpunkte |
| Standardfehler | 0,1 Prozentpunkte |
| Grenzen des Konfidenzintervalls (nur roh) | 0,2 Prozentpunkte |

**Fertig ist Abend 2, wenn** `results/A/abend2_positivkontrolle.csv` je Zeile Kennzahl, Gruppe, roh oder adjustiert, Größe, Wert, Zielwert, Abweichung und Urteil enthält. Das Urteil lautet „bestanden“, „nicht bestanden“ oder `extern nicht geprüft`. Für die Konfidenzintervalle stehen n, f und m dabei.

## Abend 3 – Zweitauswertung durch Gemini

Auswerter B rechnet die Stufen 1, 2 und 4 der Positivkontrolle in Python nach, ohne Survey-Bibliothek. B programmiert die Varianz von Hand und kommt damit auf einem anderen Weg zum selben Schätzer wie A.

**Ablauf:**

1. Gemini bekommt nur dieses Dokument und schreibt `B/positivkontrolle.py`.
2. Das Skript liest dieselben Rohdateien aus `data/raw/` und schreibt `results/B/abend2_positivkontrolle.csv`.
3. Claude Code führt das Skript aus, ohne es zu ändern.
4. Ein drittes, kurzes Skript `vergleich.py` stellt A, B und Zielwert nebeneinander.

**Varianzschätzung für B, von Hand programmiert:**

- Aus der Designbasis wird einmal die vollständige Liste aller Paare aus `SDMVSTRA` und `SDMVPSU` gebildet. Ein solches Paar ist ein Cluster. n\_h ist die Zahl der Cluster dieser Liste im Stratum h, nicht nur der Cluster mit Personen der Analysegruppe.
- Zuerst die Ja/Nein-Maske d der Analysegruppe bilden, einschließlich gültigem BMI. Gesamt, Männer und Frauen haben je eine eigene Maske und einen eigenen Nenner.
- W = Summe der Gewichte w über die Personen mit d = Ja. p = Summe(w · y) über dieselben Personen, geteilt durch W. Dabei ist y = 1 bei Adipositas.
- z beginnt für alle Personen der Designbasis bei 0. Nur für Personen mit d = Ja wird z = w · (y − p) / W gesetzt. Ein fehlender Wert darf nie in z landen.
- z wird je Cluster aufsummiert. Cluster ohne Personen der Analysegruppe haben die Summe 0 und bleiben in der Rechnung.
- Je Stratum h: Beitrag = n\_h / (n\_h − 1) · Summe der quadrierten Abweichungen der Clustersummen von ihrem Stratum-Mittel.
- Die Varianz ist die Summe der Beiträge aller Strata, der Standardfehler ihre Wurzel.

**Altersadjustiert:**

- Für jede Altersgruppe a: W\_a und p\_a wie oben, nur mit den Personen der Analysegruppe in dieser Altersgruppe. s\_a ist der feste Standardanteil.
- p\_adj = Summe über die drei Altersgruppen von s\_a · p\_a.
- Für jede Person der Analysegruppe in Altersgruppe a: z = s\_a · w · (y − p\_a) / W\_a. Für alle anderen bleibt z = 0.
- z wird je Cluster **über alle Altersgruppen** aufsummiert. Erst auf diese Clustersummen wird die Stratum-Formel angewendet.
- Falsch wäre, drei Varianzen getrennt zu rechnen und zu addieren. Das unterschlägt, dass dieselben Cluster zu mehreren Altersgruppen beitragen.
- Ist eine Altersgruppe leer, ist der Wert nicht schätzbar. B bricht dann mit klarer Meldung ab.

**Übereinstimmung A gegen B:**

| Größe | Erlaubte Abweichung |
| --- | --- |
| Fallzahlen | keine |
| Prävalenz | 0,01 Prozentpunkte |
| Standardfehler | 0,01 Prozentpunkte |

Die Toleranz zwischen A und B ist enger als die zum Report, weil beide dieselben Rohdaten ohne Rundung nutzen.

**Fertig ist Abend 3, wenn** `results/vergleich_abend2.csv` für jede Zeile das Urteil für „A gegen Ziel“, „B gegen Ziel“ und „A gegen B“ enthält. Bestanden ist der Abend, wenn B jede extern geprüfte Zelle der Stufen 1, 2 und 4 innerhalb der Toleranz trifft und jede gemeinsame Zelle innerhalb der Toleranz zu A liegt.

## Abend 4 – Fallzahlen je Wirkstoff

Beide Auswerter zählen, wie viele Befragte die Zielwirkstoffe nehmen und wie viele davon eine eingeschränkte Nierenfunktion haben. Gezählt werden ungewichtete Personen, weil es um die Machbarkeit geht.

**Analysegruppe:** eindeutige `SEQN` mit Alter ab 18 Jahren, `RIDSTATR = 2`, `RIAGENDR` gleich 1 oder 2, ohne dokumentierte Schwangerschaft, sowie `LBXSCR`, `BMXWT` und `BMXHT` vorhanden und größer null. Ein Gewichtskriterium gibt es hier nicht. Die Medikamentenangaben werden erst danach als Ja/Nein je Person angefügt. Personen ohne Medikamentenzeile bleiben in der Analysegruppe.

**Wirkstoffnutzer:** Gezählt wird berichtete Einnahme im letzten Monat, nicht bestätigte Dauertherapie.

- Eine Zeile aus P\_RXQ\_RX ist ein Treffer, wenn `RXDUSE = 1` ist und der Name passt.
- Eine Person nimmt einen Wirkstoff, wenn sie mindestens eine Trefferzeile hat.
- Namensabgleich: `RXDDRUG` als Text lesen, in Python gegebenenfalls aus Bytes dekodieren. Leerzeichen außen entfernen, in Großbuchstaben wandeln, in Folgen aus Buchstaben und Ziffern zerlegen (`[A-Z0-9]+`). Treffer ist die exakte Gleichheit einer solchen Folge mit einem Suchbegriff.
- Fehlender Name, 55555, 77777 und 99999 ergeben keinen Treffer.
- Kombinationspräparate zählen mit. Handelsnamen und unscharfe Suche gibt es nicht.

| Zeilenname in der Ausgabe | Suchbegriffe in RXDDRUG |
| --- | --- |
| `METFORMIN` | METFORMIN |
| `GABAPENTIN` | GABAPENTIN |
| `PREGABALIN` | PREGABALIN |
| `DOAK_GESAMT` | APIXABAN, RIVAROXABAN, DABIGATRAN oder EDOXABAN |
| `ALLOPURINOL` | ALLOPURINOL |
| `SITAGLIPTIN` | SITAGLIPTIN |
| `SPIRONOLACTONE` | SPIRONOLACTONE |

Zusätzlich gibt es je eine Zeile `APIXABAN`, `RIVAROXABAN`, `DABIGATRAN` und `EDOXABAN` sowie die Zeile `GESAMT` für die ganze Analysegruppe. Eine Person kann in mehreren Zeilen zählen, in jeder aber nur einmal.

**Formeln.** Kreatinin ist `LBXSCR` in mg/dL, Gewicht `BMXWT` in kg, Größe `BMXHT` in cm, Alter `RIDAGEYR` in Jahren. Jeder Auswerter prüft die Formeln gegen die Originalarbeit und nennt sie in `LOG.md`.

- CKD-EPI 2021, indexiert (ml/min/1,73 m²): 142 · min(Kreatinin/k, 1)^a · max(Kreatinin/k, 1)^(−1,200) · 0,9938^Alter, bei Frauen mal 1,012. Frauen: k = 0,7 und a = −0,241. Männer: k = 0,9 und a = −0,302.
- Körperoberfläche nach DuBois (m²): 0,007184 · Gewicht^0,425 · Größe^0,725.
- CKD-EPI 2021, de-indexiert (ml/min): indexierter Wert · Körperoberfläche / 1,73.
- Cockcroft-Gault (ml/min): (140 − Alter) · Gewicht / (72 · Kreatinin), bei Frauen mal 0,85. Verwendet wird das tatsächliche Körpergewicht. Die Formel schätzt die Kreatinin-Clearance und wird nicht auf die Körperoberfläche bezogen.

**Rechentests vor dem Zählen.** Beide Auswerter prüfen ihre Funktionen an diesen Fällen und brechen bei Abweichung ab:

| Fall | Erwartet |
| --- | --- |
| Mann, 60 Jahre, 72 kg, Kreatinin 1,0: Cockcroft-Gault | 80,0 ml/min |
| Frau, 60 Jahre, 72 kg, Kreatinin 1,0: Cockcroft-Gault | 68,0 ml/min |
| Mann, 60 Jahre, Kreatinin 0,9: CKD-EPI indexiert | 97,78 |
| Frau, 60 Jahre, Kreatinin 0,7: CKD-EPI indexiert | 98,95 |
| Mann, 60 Jahre, Kreatinin 1,8: CKD-EPI indexiert | 42,56 |
| 72 kg, 175 cm: Körperoberfläche | 1,8704 m² |
| Körperoberfläche genau 1,73 m² | indexierter und de-indexierter Wert sind gleich |

**Kategorien:** unter 30, 30 bis unter 45, 45 bis unter 60, ab 60. Zugeordnet wird der ungerundete Wert. Die Grenzen stehen beim indexierten Wert für ml/min/1,73 m² und bei den beiden anderen für ml/min. „Diskordant“ heißt verschiedene Kategorie, nicht nachgewiesene Fehldosierung.

**Vor dem Rechnen:** A liest die „Analytic Notes“ zu P\_BIOPRO und hält in `LOG.md` wörtlich fest, ob `LBXSCR` in der kombinierten Datei bereits zwischen den Geräten angeglichen ist. Die Doku nennt eine Umrechnungsgleichung. Ohne klare Anweisung der CDC wird nichts umgerechnet.

**Ausgabe:** eine Zeile je Zeilenname der Tabelle oben, je DOAK-Substanz und für `GESAMT`.

| Spalte | Bedeutung |
| --- | --- |
| `n_personen` | in Wirkstoffzeilen Personen mit Treffer, in `GESAMT` alle Personen der Analysegruppe |
| `n_ckdepi_u60` | davon CKD-EPI indexiert unter 60 |
| `n_deindex_u60` | davon CKD-EPI de-indexiert unter 60 |
| `n_cg_u60` | davon Cockcroft-Gault unter 60 |
| `n_irgendeine_u60` | davon mindestens ein Schätzer unter 60. Das ist die Vereinigung der drei Personenmengen, nicht ihre Summe |
| `n_diskordant_cg_ckdepi` | Kategorie verschieden zwischen Cockcroft-Gault und CKD-EPI indexiert |
| `n_diskordant_cg_deindex` | Kategorie verschieden zwischen Cockcroft-Gault und CKD-EPI de-indexiert |
| `n_alter_80` | davon mit gedeckeltem Alter (`RIDAGEYR = 80`) |

**Vergleich Person für Person.** Gleiche Zellenzahlen können aus verschiedenen Personen entstehen. Deshalb schreibt jeder Auswerter zusätzlich eine Datei mit einer Zeile je `SEQN`: Analysegruppe ja oder nein, Treffer je Zeilenname, die drei Kategorien. Diese Dateien liegen in `data/work/` und nicht im Git. `vergleich.py` schreibt nur die Zahl der Abweichungen je Merkmal nach `results/vergleich_abend4.csv`.

**Fertig ist Abend 4, wenn** `results/A/abend4_fallzahlen.csv` und `results/B/abend4_fallzahlen.csv` in jeder Zelle exakt übereinstimmen und der Vergleich Person für Person null Abweichungen zeigt.

## Entscheidungsregel

Für die Entscheidung zählen genau sieben Zeilen: `METFORMIN`, `GABAPENTIN`, `PREGABALIN`, `DOAK_GESAMT`, `ALLOPURINOL`, `SITAGLIPTIN` und `SPIRONOLACTONE`. Die Zeilen der einzelnen DOAK und `GESAMT` zählen nicht.

- **G3**, wenn der Pilot bestanden ist und mindestens drei dieser sieben Zeilen in `n_irgendeine_u60` den Wert 30 oder mehr haben.
- **K1** (Reanalyse-Audit mit drei Papern), wenn der Pilot bestanden ist und weniger als drei Zeilen die Schwelle erreichen.
- **Weder G3 noch K1**, wenn der Pilot nicht bestanden ist. Dann gilt das Abbruchkriterium.

Die Regel steht fest, bevor die Fallzahlen bekannt sind. Die Zahl 30 ist nur eine Machbarkeitsschwelle dieses Pilots. Sie sagt nichts darüber, ob ein späterer Anteil nach den NCHS-Standards darstellbar ist.

Bestanden ist der Pilot, wenn alle vier Punkte erfüllt sind:

- [ ] Abend 1: vier Dateien geladen, Zeilenzahlen stimmen
- [ ] Abend 2: A trifft jede extern geprüfte Zelle innerhalb der Toleranz
- [ ] Abend 3: B trifft jede extern geprüfte Zelle und liegt innerhalb der Toleranz zu A
- [ ] Abend 4: Rechentests bestanden, Fallzahlen von A und B identisch, null Abweichungen je Person

Nach der Entscheidung und vor jeder Hauptanalyse entsteht ein einseitiges Protokoll, das öffentlich registriert wird.

**Ablage im Repo:**

| Pfad | Inhalt |
| --- | --- |
| `SPEC.md` | diese Spezifikation, einzige maßgebliche Fassung |
| `data/raw/` | Rohdateien und `CHECKSUMS.txt`, nicht im Git |
| `data/work/` | Dateien mit einer Zeile je Person, nicht im Git |
| `docs/cdc/` | gesicherte Dokumentationsseiten der CDC |
| `A/` | R-Skripte von Claude Code |
| `B/` | Python-Skripte von Gemini |
| `results/A/`, `results/B/` | Ergebnis-CSV je Auswerter |
| `results/vergleich_*.csv` | Gegenüberstellung A, B, Zielwert |
| `review/` | Reviews der Spezifikation durch andere Modelle |
| `LOG.md` | Änderungen mit Grund und Datum, zitierte Quellen |
| `OFFEN.md` | offene Fragen an die Spezifikation |

## Startaufträge zum Kopieren

Drei Aufträge reichen für den Pilot. Die Stellen in spitzen Klammern passt du an.

**Claude Code als Auswerter A (Abende 1, 2 und 4):**

```text
Du bist Auswerter A in einem Pilotprojekt mit offenen NHANES-Daten.
Die Spezifikation liegt als SPEC.md im Repo. Lies sie vollständig, bevor du etwas tust.

Heute ist Abend <1 | 2 | 4>. Bearbeite nur diesen Abschnitt.

Regeln:
- Arbeite in R mit dem Paket survey. Fehlt R oder ein Paket, sag mir vor der Installation, was du installierst.
- Halte dich an die acht Regeln und die sechs gemeinsamen Definitionen der Spezifikation.
  Öffne die Ordner B/ und results/B/ nicht.
- Ist die Spezifikation unklar oder widerspricht sie der CDC-Dokumentation: anhalten, Frage in OFFEN.md schreiben, mich fragen.
- Ändere keine Toleranzen und keine Zielwerte.

Am Ende lieferst du die Ergebnis-CSV laut Spezifikation, einen Eintrag in LOG.md, einen Git-Commit
und eine Zusammenfassung in fünf Sätzen für einen Arzt ohne Programmierkenntnisse:
was bestanden ist, was nicht, was offen ist.
```

**Gemini als Auswerter B:**

```text
Du bist Auswerter B in einem Pilotprojekt mit offenen NHANES-Daten.
Die vollständige Spezifikation ist SPEC.md im Repo Justus42/nhanes-pilot. Du siehst weder Code noch Ergebnisse von Auswerter A.

Aufgabe: Schreibe ein einzelnes Python-Skript <B/positivkontrolle.py | B/fallzahlen.py>
für <die Stufen 1, 2 und 4 der Positivkontrolle | die Fallzahlen von Abend 4>.

Vorgaben:
- Nur pandas, numpy und scipy. Keine Survey-Bibliothek. Die Varianz programmierst du nach der Beschreibung unter "Abend 3".
- Halte dich an die sechs gemeinsamen Definitionen der Spezifikation.
- Eingabe: die .xpt-Dateien in data/raw/ (pandas.read_sas). Textspalten können als Bytes ankommen und müssen dekodiert werden.
- Ausgabe: die CSV laut Spezifikation in results/B/, mit voller Rechengenauigkeit.
- Schreib keine Zielwerte in das Skript. Der Vergleich läuft getrennt.
- Du kannst das Skript nicht selbst gegen die Daten laufen lassen. Es soll bei unerwarteten Zeilenzahlen
  oder fehlenden Spalten mit klarer Meldung abbrechen.
- Ist die Spezifikation unklar: Liste deine Fragen auf, statt zu raten.

Antworte mit dem Skript und darunter einer kurzen Liste deiner Annahmen.
```

**Claude Code für den Vergleich (Abend 3 und Ende von Abend 4):**

```text
Die Ergebnisse von Auswerter A sind committet. Führe jetzt <B/positivkontrolle.py | B/fallzahlen.py> aus, ohne die Datei zu ändern.
Bricht das Skript ab, gib mir die Fehlermeldung wörtlich, damit ich sie an Gemini zurückgebe.
Schreibe danach vergleich.py, das A, B und die Zielwerte aus SPEC.md nebeneinanderstellt
und je Zeile "bestanden", "nicht bestanden" oder "extern nicht geprüft" nach den Regeln der Spezifikation ausgibt.
An Abend 4 vergleicht es zusätzlich die Dateien je Person und schreibt nur die Zahl der Abweichungen je Merkmal.
Weichen A und B voneinander ab, ändere nichts an A. Beschreibe mir nur, in welcher Zeile und um wie viel.
```

## Offene und ungeprüfte Punkte

Zehn Angaben in dieser Spezifikation sind nicht abschließend belegt oder noch nicht entschieden. Die ersten fünf werden geklärt, bevor der jeweilige Abend beginnt.

1. **Zielwerte der Positivkontrolle.** Sie wurden maschinell aus dem PDF gelesen. Vor Abend 2 die Tabellen 2, 5 und 6 im Report selbst ansehen und mit der Tabelle oben vergleichen.
2. **Standardfehler 1,2 und 0,6.** Unklar ist, ob sie zur rohen oder zur altersadjustierten Schätzung gehören. Tabelle 2 des Reports klärt das.
3. **Download-Muster der Dateien.** Nicht getestet. In einer Cloud-Umgebung müssen die CDC-Domains freigegeben sein.
4. **Kreatinin zwischen den Geräten.** Die Doku nennt eine Umrechnungsgleichung. Offen ist, ob die kombinierte Datei sie schon enthält.
5. **Arbeitsumgebung und Auswerter B.** Noch nicht entschieden: Cloud-Sitzung oder PC, und welches Gemini-Modell auf welchem Weg das Skript von B schreibt.
6. **Standardanteile der Altersgruppen** (0,3966, 0,3718, 0,2316). Claude und GPT 6.2 Astra nennen sie übereinstimmend aus dem Gedächtnis. Ein Quellenbeleg fehlt. A prüft sie vor Abend 2.
7. **Die Formeln von Abend 4.** Claude und GPT 6.2 Astra nennen sie übereinstimmend aus dem Gedächtnis. Beide Auswerter prüfen sie gegen die Originalarbeiten. Die Erwartungswerte der Rechentests sind aus diesen Formeln berechnet.
8. **Formel des Konfidenzintervalls.** Sie ist aus dem Gedächtnis ausgeschrieben und gegen die NCHS-Standards zur Darstellung von Anteilen (laut Astra Series 2, Nr. 175) zu prüfen. Ob `svyciprop(method = "beta")` dasselbe liefert, ist offen. Deshalb bleibt die Toleranz dort 0,2 Prozentpunkte.
9. **Schwelle 30 Personen.** Für die Hauptanalyse gelten die NCHS-Standards. Sie betreffen den tatsächlichen und den effektiven Nenner eines Anteils und die Breite des Konfidenzintervalls und sind noch nachzulesen.
10. **Berufsrechtliche Beratung.** Ob die Sächsische Landesärztekammer für anonymisierte US-Surveydaten eine Beratung verlangt, ist offen. Die Frage stellt sich vor einer Einreichung, nicht vor dem Pilot.

Die EKFC-Formel fehlt im Pilot absichtlich. Sie kommt erst ins Protokoll, falls G3 gewählt wird.

## Quellen

- [NHANES 2017–März 2020: P\_DEMO, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm)
- [P\_BMX, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm)
- [P\_BIOPRO, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BIOPRO.htm)
- [P\_RXQ\_RX, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_RXQ_RX.htm)
- [National Health Statistics Report Nr. 158 (Stierman et al., 2021)](https://stacks.cdc.gov/view/cdc/106273/cdc_106273_DS1.pdf)
- [NCHS: Guidelines for High Quality Analyses of NHANES Data](https://wwwn.cdc.gov/nchs/nhanes/QualityAnalysesGuidelines.aspx)
