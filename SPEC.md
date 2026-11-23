# NHANES-Pilot: Spezifikation für die Abende 1–4

Nov 23, 2026 · @Justus Jeserigk

## Zweck und Abbruchkriterium

Der Pilot klärt in vier Abenden, ob eine lokal gerechnete NHANES-Auswertung vertrauenswürdig ist und ob das Projekt „Nierenformeln und Dosierungskategorien“ (G3) genug Fälle hat. Ein Forschungsergebnis liefert er noch nicht.

Er beantwortet drei Fragen:

1. Lassen sich die NHANES-Dateien des Zyklus 2017–März 2020 lokal laden?
2. Trifft die Auswertung eine veröffentlichte CDC-Kennzahl samt Konfidenzintervall?
3. Wie viele Befragte nehmen die Zielwirkstoffe, insgesamt und bei eingeschränkter Nierenfunktion?

**Abbruch:** Das Projekt endet, wenn die Dateien lokal nicht ladbar sind oder wenn die Positivkontrolle nach zwei Abenden nicht innerhalb der Toleranz liegt. Nachbessern an der Toleranz ist nicht erlaubt.

## Regeln für beide Auswerter

Zwei Auswerter rechnen dieselbe Spezifikation getrennt nach. Auswerter A ist Claude Code und schreibt in R mit dem Paket `survey`. Auswerter B ist Gemini über die Bridge und schreibt in Python nur mit `pandas`, `numpy` und `scipy`, ohne Survey-Bibliothek.

1. **Unabhängigkeit.** A sieht weder Code noch Ergebnisse von B, und umgekehrt. B bekommt nur dieses Dokument.
2. **Kein fremder Eingriff.** Claude Code darf das Skript von B ausführen, aber nicht ändern. Fehlermeldungen gehen wörtlich an Gemini zurück.
3. **Rohdaten bleiben unverändert.** Sie liegen in `data/raw/`, jede Datei mit SHA-256-Prüfsumme in `data/raw/CHECKSUMS.txt`.
4. **Jede Zahl kommt aus einem Skriptlauf.** Nichts wird von Hand abgetippt. Ergebnisse landen als CSV in `results/A/` und `results/B/`.
5. **Survey-Design immer vollständig.** Gewicht `WTMECPRP`, Stratum `SDMVSTRA`, Cluster `SDMVPSU`. Teilgruppen werden als Domäne gerechnet. Zeilen außerhalb der Teilgruppe werden nicht vor der Varianzschätzung gelöscht.
6. **Kein Hinbiegen.** Weicht ein Wert vom Ziel ab, wird die Ursache in der CDC-Dokumentation gesucht. Jede Änderung am Skript steht mit Grund und Datum in `LOG.md`.
7. **Nicht raten.** Ist die Spezifikation unklar oder widerspricht sie der CDC-Dokumentation, hält der Auswerter an und schreibt die Frage in `OFFEN.md`.
8. **Keine Re-Identifikation.** Die NHANES-Daten werden nur statistisch ausgewertet und mit keinen anderen Personendaten verknüpft.

## Abend 1 – Daten laden

Vier Dateien aus dem Zyklus 2017–März 2020 werden lokal geladen und unverändert abgelegt. Die Zeilenzahl jeder Datei muss exakt zur CDC-Dokumentation passen.

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

**Analysegruppe:** Alter ab 20 Jahren (`RIDAGEYR >= 20`), untersucht (`RIDSTATR = 2`), BMI vorhanden, nicht schwanger (`RIDEXPRG` ungleich 1). Erwartet werden 8.295 Personen, davon 4.051 Männer und 4.244 Frauen.

**Definitionen:** Adipositas ist BMI ab 30, schwere Adipositas BMI ab 40.

| Kennzahl | Gruppe | Roh, % (95-%-KI) | Altersadjustiert, % (95-%-KI) |
| --- | --- | --- | --- |
| Adipositas | Gesamt | 41,9 (39,4–44,3) | 41,9 (39,4–44,3) |
| Adipositas | Männer | 41,6 (37,4–45,8) | 41,8 (37,7–45,9) |
| Adipositas | Frauen | 42,1 (39,6–44,8) | 41,8 (39,3–44,4) |
| Schwere Adipositas | Gesamt | 9,0 (7,8–10,3) | 9,2 (8,0–10,6) |
| Schwere Adipositas | Männer | 6,4 (5,1–8,0) | 6,6 (5,3–8,1) |
| Schwere Adipositas | Frauen | 11,4 (9,7–13,3) | 11,7 (10,0–13,7) |

Der Report nennt für die Gesamtgruppe außerdem Standardfehler von 1,2 (Adipositas) und 0,6 (schwere Adipositas).

**Methode laut Report:**

- Standardfehler per Taylor-Linearisierung.
- Konfidenzintervalle nach Korn und Graubard. In R: `svyciprop(..., method = "beta")`.
- Altersadjustierung direkt auf die projizierte US-Bevölkerung 2000, Altersgruppen 20–39, 40–59 und ab 60.
- Die Standardgewichte der drei Altersgruppen entnimmt A der NCHS-Quelle und zitiert sie in `LOG.md`. Erwartet werden etwa 0,397, 0,372 und 0,232.

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

**Fertig ist Abend 2, wenn** `results/A/abend2_positivkontrolle.csv` alle Werte mit Zielwert, Abweichung und Urteil „bestanden“ oder „nicht bestanden“ enthält. Die Zahl der Freiheitsgrade steht dabei.

## Abend 3 – Zweitauswertung durch Gemini

Auswerter B rechnet die Stufen 1, 2 und 4 der Positivkontrolle in Python nach, ohne Survey-Bibliothek. Stimmen A und B überein, obwohl sie die Varianz auf verschiedenen Wegen rechnen, ist ein gemeinsamer Denkfehler unwahrscheinlich.

**Ablauf:**

1. Gemini bekommt über die Bridge nur dieses Dokument und schreibt `B/positivkontrolle.py`.
2. Das Skript liest dieselben Rohdateien aus `data/raw/` und schreibt `results/B/abend2_positivkontrolle.csv`.
3. Claude Code führt das Skript aus, ohne es zu ändern.
4. Ein drittes, kurzes Skript `vergleich.py` stellt A, B und Zielwert nebeneinander.

**Varianzschätzung für B, von Hand programmiert:**

- Geschätzt wird p = Summe(w · d · y) / Summe(w · d). Dabei ist w das Gewicht, d = 1 für Personen der Analysegruppe und sonst 0, y = 1 bei Adipositas.
- Für jede Person: z = w · d · (y − p) / Summe(w · d).
- z wird je Cluster aufsummiert. Cluster ist die Kombination aus `SDMVSTRA` und `SDMVPSU`.
- Je Stratum h mit n\_h Clustern: Beitrag = n\_h / (n\_h − 1) · Summe der quadrierten Abweichungen der Clustersummen von ihrem Stratum-Mittel.
- Die Varianz ist die Summe der Beiträge aller Strata, der Standardfehler ihre Wurzel.
- Alle Personen aus P\_DEMO bleiben im Datensatz. Wer nicht zur Analysegruppe gehört, trägt z = 0 bei.
- Altersadjustiert: p\_adj = Summe über die Altersgruppen von (Standardgewicht · p der Gruppe). z wird entsprechend je Altersgruppe gebildet und mit dem Standardgewicht multipliziert.

**Übereinstimmung A gegen B:**

| Größe | Erlaubte Abweichung |
| --- | --- |
| Fallzahlen | keine |
| Prävalenz | 0,01 Prozentpunkte |
| Standardfehler | 0,01 Prozentpunkte |

Die Toleranz zwischen A und B ist enger als die zum Report, weil beide dieselben Rohdaten ohne Rundung nutzen.

**Fertig ist Abend 3, wenn** `results/vergleich_abend2.csv` für jede Zeile das Urteil für „A gegen Ziel“, „B gegen Ziel“ und „A gegen B“ enthält.

## Abend 4 – Fallzahlen je Wirkstoff

Beide Auswerter zählen, wie viele Befragte die Zielwirkstoffe nehmen und wie viele davon eine eingeschränkte Nierenfunktion haben. Gezählt werden ungewichtete Personen, weil es um die Machbarkeit geht.

**Analysegruppe:** Alter ab 18 Jahren, untersucht (`RIDSTATR = 2`), nicht schwanger, Kreatinin, Gewicht und Größe vorhanden.

**Wirkstoffnutzer:** Eine Person nimmt einen Wirkstoff, wenn mindestens eine ihrer Zeilen in P\_RXQ\_RX `RXDUSE = 1` hat und `RXDDRUG` den Wirkstoffnamen als ganzes Wort enthält. Groß- und Kleinschreibung spielen keine Rolle. Kombinationspräparate zählen mit.

| Wirkstoff | Suchbegriff in RXDDRUG |
| --- | --- |
| Metformin | METFORMIN |
| Gabapentin | GABAPENTIN |
| Pregabalin | PREGABALIN |
| DOAK (als Gruppe und einzeln) | APIXABAN, RIVAROXABAN, DABIGATRAN, EDOXABAN |
| Allopurinol | ALLOPURINOL |
| Sitagliptin | SITAGLIPTIN |
| Spironolacton | SPIRONOLACTONE |

**Formeln.** Kreatinin in mg/dL, Gewicht in kg, Größe in cm, Alter in Jahren. Jeder Auswerter prüft die Formeln gegen die Originalarbeit und nennt sie in `LOG.md`.

- CKD-EPI 2021, indexiert (ml/min/1,73 m²): 142 · min(Kreatinin/k, 1)^a · max(Kreatinin/k, 1)^(−1,200) · 0,9938^Alter, bei Frauen mal 1,012. Frauen: k = 0,7 und a = −0,241. Männer: k = 0,9 und a = −0,302.
- Körperoberfläche nach DuBois (m²): 0,007184 · Gewicht^0,425 · Größe^0,725.
- CKD-EPI 2021, de-indexiert (ml/min): indexierter Wert · Körperoberfläche / 1,73.
- Cockcroft-Gault (ml/min): (140 − Alter) · Gewicht / (72 · Kreatinin), bei Frauen mal 0,85. Verwendet wird das tatsächliche Körpergewicht.

**Kategorien:** ab 60, 45 bis unter 60, 30 bis unter 45, unter 30. Sie gelten für alle drei Schätzer.

**Vor dem Rechnen:** A liest die „Analytic Notes“ zu P\_BIOPRO und hält in `LOG.md` wörtlich fest, ob `LBXSCR` in der kombinierten Datei bereits zwischen den Geräten angeglichen ist. Die Doku nennt eine Umrechnungsgleichung. Ohne klare Anweisung der CDC wird nichts umgerechnet.

**Ausgabe:** eine Zeile je Wirkstoff, dazu eine Zeile für die gesamte Analysegruppe.

| Spalte | Bedeutung |
| --- | --- |
| `n_nutzer` | Personen mit dem Wirkstoff |
| `n_ckdepi_u60` | davon CKD-EPI indexiert unter 60 |
| `n_deindex_u60` | davon CKD-EPI de-indexiert unter 60 |
| `n_cg_u60` | davon Cockcroft-Gault unter 60 |
| `n_irgendeine_u60` | davon mindestens ein Schätzer unter 60 |
| `n_diskordant_cg_ckdepi` | Kategorie verschieden zwischen Cockcroft-Gault und CKD-EPI indexiert |
| `n_diskordant_cg_deindex` | Kategorie verschieden zwischen Cockcroft-Gault und CKD-EPI de-indexiert |

**Fertig ist Abend 4, wenn** `results/A/abend4_fallzahlen.csv` und `results/B/abend4_fallzahlen.csv` vorliegen und in jeder Zelle exakt übereinstimmen.

## Entscheidungsregel

G3 wird das Projekt, wenn mindestens drei der sieben Wirkstoffgruppen in `n_irgendeine_u60` je 30 oder mehr Personen haben. Sonst wird es das Reanalyse-Audit K1 mit drei Papern. Die Regel steht fest, bevor die Fallzahlen bekannt sind.

Voraussetzung für beide Wege ist ein bestandener Pilot:

- [ ] Abend 1: vier Dateien geladen, Zeilenzahlen stimmen
- [ ] Abend 2: Positivkontrolle von A innerhalb der Toleranz
- [ ] Abend 3: B bestätigt A
- [ ] Abend 4: Fallzahlen von A und B identisch

Nach der Entscheidung und vor jeder Hauptanalyse entsteht ein einseitiges Protokoll, das öffentlich registriert wird.

**Ablage im Repo:**

| Pfad | Inhalt |
| --- | --- |
| `SPEC.md` | dieses Dokument als Markdown |
| `data/raw/` | Rohdateien und `CHECKSUMS.txt`, nicht im Git |
| `A/` | R-Skripte von Claude Code |
| `B/` | Python-Skripte von Gemini |
| `results/A/`, `results/B/` | Ergebnis-CSV je Auswerter |
| `results/vergleich_*.csv` | Gegenüberstellung A, B, Zielwert |
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
- Halte dich an die acht Regeln der Spezifikation. Öffne die Ordner B/ und results/B/ nicht.
- Ist die Spezifikation unklar oder widerspricht sie der CDC-Dokumentation: anhalten, Frage in OFFEN.md schreiben, mich fragen.
- Ändere keine Toleranzen und keine Zielwerte.

Am Ende lieferst du die Ergebnis-CSV laut Spezifikation, einen Eintrag in LOG.md, einen Git-Commit
und eine Zusammenfassung in fünf Sätzen für einen Arzt ohne Programmierkenntnisse:
was bestanden ist, was nicht, was offen ist.
```

**Gemini als Auswerter B (über die Bridge):**

```text
Du bist Auswerter B in einem Pilotprojekt mit offenen NHANES-Daten.
Die vollständige Spezifikation ist SPEC.md im Repo <Repo-Name>. Du siehst weder Code noch Ergebnisse von Auswerter A.

Aufgabe: Schreibe ein einzelnes Python-Skript <B/positivkontrolle.py | B/fallzahlen.py>
für <die Stufen 1, 2 und 4 der Positivkontrolle | die Fallzahlen von Abend 4>.

Vorgaben:
- Nur pandas, numpy und scipy. Keine Survey-Bibliothek. Die Varianz programmierst du nach der Beschreibung unter "Abend 3".
- Eingabe: die .xpt-Dateien in data/raw/ (pandas.read_sas). Ausgabe: die CSV laut Spezifikation in results/B/.
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
und je Zeile "bestanden" oder "nicht bestanden" nach den Toleranzen der Spezifikation ausgibt.
Weichen A und B voneinander ab, ändere nichts an A. Beschreibe mir nur, in welcher Zeile und um wie viel.
```

## Offene und ungeprüfte Punkte

Neun Angaben in dieser Spezifikation sind nicht abschließend belegt. Die ersten vier klärst du oder Claude Code, bevor der jeweilige Abend beginnt.

1. **Zielwerte der Positivkontrolle.** Sie wurden maschinell aus dem PDF gelesen. Vor Abend 2 die Tabellen 2, 5 und 6 im Report selbst ansehen und mit der Tabelle oben vergleichen.
2. **Standardfehler 1,2 und 0,6.** Unklar ist, ob sie zur rohen oder zur altersadjustierten Schätzung gehören. Tabelle 2 des Reports klärt das.
3. **Download-Muster der Dateien.** Nicht getestet, weil die CDC-Server aus der Cloud nicht erreichbar waren.
4. **Kreatinin zwischen den Geräten.** Die Doku nennt eine Umrechnungsgleichung. Offen ist, ob die kombinierte Datei sie schon enthält.
5. **Standardgewichte der Altersgruppen** (0,397, 0,372, 0,232) stammen aus dem Gedächtnis.
6. **Die drei Formeln von Abend 4** stammen aus dem Gedächtnis. Beide Auswerter prüfen sie gegen die Originalarbeiten.
7. **Richtwert 30 Personen.** Er stammt aus dem Gedächtnis. Für die Hauptanalyse gelten die NCHS-Standards zur Darstellung von Anteilen, die noch nachzulesen sind.
8. **Freiheitsgrade beim Konfidenzintervall.** Die Wahl kann die Grenzen um Zehntel verschieben. Deshalb ist die Toleranz dort 0,2 Prozentpunkte.
9. **Berufsrechtliche Beratung.** Ob die Sächsische Landesärztekammer für anonymisierte US-Surveydaten eine Beratung verlangt, ist offen. Die Frage stellt sich vor einer Einreichung, nicht vor dem Pilot.

Die EKFC-Formel fehlt im Pilot absichtlich. Sie kommt erst ins Protokoll, falls G3 gewählt wird.

## Quellen

- [NHANES 2017–März 2020: P\_DEMO, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm)
- [P\_BMX, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm)
- [P\_BIOPRO, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BIOPRO.htm)
- [P\_RXQ\_RX, Dokumentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_RXQ_RX.htm)
- [National Health Statistics Report Nr. 158 (Stierman et al., 2021)](https://stacks.cdc.gov/view/cdc/106273/cdc_106273_DS1.pdf)
- [NCHS: Guidelines for High Quality Analyses of NHANES Data](https://wwwn.cdc.gov/nchs/nhanes/QualityAnalysesGuidelines.aspx)
