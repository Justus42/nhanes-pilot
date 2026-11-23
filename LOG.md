# Änderungsprotokoll

Jede Änderung an der Spezifikation oder an einem Skript steht hier mit Datum und Grund.

## 2026-11-23 – Spezifikation Version 2, vor Beginn von Abend 1

**Anlass:** Review der Version 1 durch GPT 6.2 Astra, abgelegt unter `review/openrouter/spec-v1-astra.md`. Astra meldete 4 Fehler und 14 Unklarheiten. Alle 18 Befunde sind übernommen, in knapperer Form als die vorgeschlagenen Ersatztexte.

**Nicht geändert:** die Zielwerte der Positivkontrolle, alle Toleranzen, das Abbruchkriterium und die Schwelle der Entscheidungsregel (mindestens drei Zeilen mit 30 oder mehr Personen).

**Bis zu diesem Zeitpunkt lagen keine Daten und keine Ergebnisse vor.**

| Befund | Änderung in Version 2 |
| --- | --- |
| 1 | Schwangerschaft: ausgeschlossen wird nur `RIDEXPRG = 1`, fehlende Angaben bleiben drin. Neue Definition 1. |
| 2 | Konfidenzintervall nach Korn und Graubard als Formel ausgeschrieben. Die R-Funktion ist nur noch Zusatz. |
| 3 | Festgelegt, welche Größen ein externes Ziel haben. Übrige Standardfehler: `extern nicht geprüft`. |
| 4 | Standardanteile der Altersgruppen fest vorgegeben: 0,3966, 0,3718, 0,2316. |
| 5 | Designbasis definiert, Aufruf von `svydesign` ausgeschrieben, Verhalten bei Stratum mit einem Cluster. |
| 6 | Varianz für B: Maske zuerst, z beginnt bei 0, fehlende Werte nie in z. |
| 7 | Altersadjustierte Varianz: je Cluster über alle Altersgruppen summieren, dann erst die Stratum-Formel. |
| 8 | Einheiten der drei Schätzer klargestellt. „Diskordant“ definiert. |
| 9 | Alter ab 80 geht mit genau 80 ein. Neue Spalte `n_alter_80`. |
| 10 | Analysegruppe von Abend 4 präzisiert: Werte größer null, eindeutige `SEQN`, Medikamente danach anfügen. |
| 11 | Wirkstoffnutzer: Treffer je Zeile, danach Oder je Person. Unbekannte Namen sind kein Treffer. |
| 12 | Namensabgleich als exakter Vergleich von Folgen aus Buchstaben und Ziffern. Hinweis auf Bytes in Python. |
| 13 | Kategorien werden aus ungerundeten Werten gebildet. |
| 14 | Spalte `n_nutzer` heißt jetzt `n_personen`. Zeile `GESAMT` definiert. |
| 15 | Aussagekraft des Vergleichs A gegen B korrigiert. Neu: Rechentests und Vergleich Person für Person. |
| 16 | Vergleichsregeln: ungerundet, in Prozentpunkten, kleiner oder gleich Toleranz. Bestehen von Abend 3 definiert. |
| 17 | Entscheidungsregel nennt die sieben Zeilen ausdrücklich. Fall „Pilot nicht bestanden“ ergänzt. |
| 18 | Die Zahl 30 ist als reine Machbarkeitsschwelle gekennzeichnet. |

**Zweites Review** durch Gemini 4 Neon auf dem Stand von Version 2, abgelegt unter `review/gemini/spec-v2-neon.md`. Neon meldete 3 Fehler und 2 Unklarheiten. Alle fünf sind übernommen. Claude hat die vorgeschlagenen Erwartungswerte nachgerechnet, sie stimmen.

| Befund | Änderung |
| --- | --- |
| N1 | Rechentests: Toleranz 0,01 ergänzt. Zwei neue Fälle prüfen den geschlechtsabhängigen Exponenten, ein neuer Fall die De-Indexierung. |
| N2 | Datei je Person genau festgelegt: alle 15.560 `SEQN`, Spalten, leere Werte außerhalb der Analysegruppe. Startauftrag für B ergänzt. |
| N3 | Kodierung von `RIAGENDR` als Definition 7 aufgenommen (1 männlich, 2 weiblich, laut CDC-Dokumentation zu P_DEMO). |
| N4 | Kreatinin: Kein Auswerter rechnet von sich aus um. Verlangt die CDC eine Umrechnung, kommt die Formel erst in die Spezifikation. |
| N5 | Prüfliste Abend 3: B muss nur die Stufen 1, 2 und 4 treffen. |

Drei der fünf Befunde (N1, N2, N5) betreffen Text, der erst mit Version 2 entstanden ist.

**Neuer Abschnitt „Änderungen an dieser Spezifikation“** auf Vorschlag von Claude: Er trennt einen festen Kern (Toleranzen, Abbruchkriterium, Entscheidungsregel, Zielwerte) von Klarstellungen, die auch nach Beginn erlaubt sind, wenn sie belegt und protokolliert werden.

**Weitere Änderungen ohne Bezug zum Review:**

- Das Wort „lokal“ ist gestrichen. Die Arbeitsumgebung (Cloud-Sitzung oder PC) ist offen und wird vor Abend 1 hier eingetragen.
- Auswerter B heißt „ein Gemini-Modell“. Modell und Weg sind offen.
- Die Erwartungswerte der Rechentests hat Claude aus den Formeln der Spezifikation berechnet.
- `.gitignore` schließt zusätzlich `data/work/` aus.

**Bewertung der Befunde durch Claude:** Befund 2 behauptet, die R-Funktion setze die NCHS-Regel nicht genau um. Das ist nicht geprüft. Die Änderung ist davon unabhängig richtig, weil die Formel jetzt ausgeschrieben ist.

## 2026-11-23 – Entscheidungen von Justus vor Abend 1

Erledigt damit Punkt 5 der offenen Punkte der Spezifikation.

- **Arbeitsumgebung:** Cloud-Sitzung von Claude Code.
- **Auswerter B:** Gemini 4 Neon über die Gemini-App. Justus überträgt das Skript unverändert.

## 2026-11-23 – Abend 1: Download-Skript

**Skript:** `A/01_download.R`, neu. Lädt die vier `.xpt`-Dateien nach `data/raw/` und bildet direkt nach jedem Download die SHA-256-Prüfsumme. Beim ersten Lauf legt es `results/A/abend1_dateien.csv` an. Bei jedem späteren Lauf vergleicht es jede Prüfsumme mit dieser Datei und bricht bei einer Abweichung ab. Danach zählt es Zeilen und Spalten, prüft die Zeilenzahl gegen SPEC.md und die benötigten Variablen, schreibt `data/raw/CHECKSUMS.txt` und sichert die vier Dokumentationsseiten in `docs/cdc/<NAME>_<Abrufdatum>.htm`, falls dort noch keine Fassung liegt.

**Grund:** Jede Cloud-Sitzung startet ohne Rohdaten. Spätere Abende rufen dasselbe Skript auf und erkennen so, ob die CDC eine Datei geändert hat.

**Erreichbarkeit, geprüft am 23.11.2026 mit `curl`:** `wwwn.cdc.gov` und `stacks.cdc.gov` sind aus der Cloud-Sitzung erreichbar. Das Download-Muster der Spezifikation (offener Punkt 3) liefert eine SAS-Transportdatei: `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.xpt` antwortet mit HTTP 200, 3.614.720 Bytes, und die Datei beginnt mit `HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!`. Für die anderen drei Dateien ist das Muster erst mit dem Skriptlauf getestet.

**Stand:** Das Skript ist noch nicht gelaufen. R fehlt in der Sitzung. Die Installation von `r-base-core`, `r-cran-survey`, `r-cran-foreign` und `r-cran-digest` per apt wurde von der Rechteprüfung der Sitzung abgelehnt und wartet auf die Freigabe durch Justus. Deshalb gibt es noch keine `results/A/abend1_dateien.csv`, keine Zeilenzahlen und keine gesicherten Seiten in `docs/cdc/`.

## 2026-11-23 – Zusatzaufgabe vor Abend 2: Quellenprüfung (nur gelesen, nichts gerechnet)

Abgerufen am 23.11.2026, Text aus dem PDF mit `pdftotext -layout` gelesen.

### 1. Zielwerte von Abend 2 gegen NHSR Nr. 158, Tabellen 2, 5 und 6

Quelle: Stierman B, Afful J, Carroll MD, et al. National Health and Nutrition Examination Survey 2017–March 2020 Prepandemic Data Files—Development of Files and Prevalence Estimates for Selected Health Outcomes. National Health Statistics Reports Nr. 158, 14. Juni 2021. <https://stacks.cdc.gov/view/cdc/106273/cdc_106273_DS1.pdf>

**Ergebnis: Alle 12 Prävalenzen, alle 12 Konfidenzintervalle und die drei Fallzahlen in SPEC.md stimmen mit dem Report überein.**

Tabelle 5 (Adipositas), Seite 14, wörtlich:

```text
Total (age adjusted) . . .   8,295   41.9 (39.4–44.3)   4,051   41.8 (37.7–45.9)   4,244   41.8 (39.3–44.4)
Total (crude) . . .          8,295   41.9 (39.4–44.3)   4,051   41.6 (37.4–45.8)   4,244   42.1 (39.6–44.8)
```

Tabelle 6 (schwere Adipositas), Seite 15, wörtlich (die hochgestellte 1 bei Frauen, altersadjustiert, heißt „Significantly different from men“):

```text
Total (age adjusted) . . .   8,295   9.2 (8.0–10.6)   4,051   6.6 (5.3–8.1)   4,244   11.7 (10.0–13.7)
Total (crude) . . .          8,295   9.0 (7.8–10.3)   4,051   6.4 (5.1–8.0)   4,244   11.4 (9.7–13.3)
```

Spaltenreihenfolge in beiden Tabellen: „Both sexes“, „Men“, „Women“, jeweils „Sample size“ und „Prevalence percentage (95% confidence interval)“.

| Kennzahl | Gruppe | SPEC roh | Report roh | SPEC adjustiert | Report adjustiert | Urteil |
| --- | --- | --- | --- | --- | --- | --- |
| Adipositas | Gesamt | 41,9 (39,4–44,3) | 41.9 (39.4–44.3) | 41,9 (39,4–44,3) | 41.9 (39.4–44.3) | gleich |
| Adipositas | Männer | 41,6 (37,4–45,8) | 41.6 (37.4–45.8) | 41,8 (37,7–45,9) | 41.8 (37.7–45.9) | gleich |
| Adipositas | Frauen | 42,1 (39,6–44,8) | 42.1 (39.6–44.8) | 41,8 (39,3–44,4) | 41.8 (39.3–44.4) | gleich |
| Schwere Adipositas | Gesamt | 9,0 (7,8–10,3) | 9.0 (7.8–10.3) | 9,2 (8,0–10,6) | 9.2 (8.0–10.6) | gleich |
| Schwere Adipositas | Männer | 6,4 (5,1–8,0) | 6.4 (5.1–8.0) | 6,6 (5,3–8,1) | 6.6 (5.3–8.1) | gleich |
| Schwere Adipositas | Frauen | 11,4 (9,7–13,3) | 11.4 (9.7–13.3) | 11,7 (10,0–13,7) | 11.7 (10.0–13.7) | gleich |

Fallzahlen: SPEC 8.295 / 4.051 / 4.244, Report 8,295 / 4,051 / 4,244. Gleich.

**Standardfehler 1,2 und 0,6: Sie gehören zur altersadjustierten Schätzung.** Tabelle 2, Seite 11, Spalte „2017–March 2020 prepandemic“, wörtlich:

```text
Adult obesity (20 years and over)3 . . .          8,295   41.9 (39.4–44.3)   1.2
Adult severe obesity (20 years and over)4 . . .   8,295    9.2 (8.0–10.6)    0.6
```

Anmerkung unter Tabelle 2, wörtlich: „NOTES: Outcomes for adults and older adults were age adjusted by the direct method to the projected U.S. Census 2000 population. Age groups used for adult obesity, adult severe obesity, and adult diabetes are 20–39, 40–59, and 60 and over.“

Begründung: (a) Die Anmerkung erklärt alle Erwachsenen-Werte der Tabelle 2 für altersadjustiert. (b) Bei schwerer Adipositas steht in Tabelle 2 „9.2 (8.0–10.6)“. Das ist der altersadjustierte Wert aus Tabelle 6. Der rohe Wert wäre „9.0 (7.8–10.3)“. (c) Bei Adipositas sind roh und adjustiert in Tabelle 5 auf eine Nachkommastelle gleich, „41.9 (39.4–44.3)“. Dort trennt nur die Anmerkung (a). Folge für Abend 2: Die beiden Standardfehler sind in Stufe 4 zu prüfen, nicht in Stufe 2. Das steht als Frage 1 in `OFFEN.md`.

Weitere Anmerkung unter Tabelle 5 und 6, wörtlich: „Except where reported as crude estimates, estimates were age adjusted by the direct method to the projected U.S. Census 2000 population using the age groups 20–39, 40–59, and 60 and over. […] Pregnant women were excluded from the analysis.“ Das deckt sich mit SPEC.md.

### 2. Standardanteile 0,3966, 0,3718 und 0,2316

Quelle: Klein RJ, Schoenborn CA. Age Adjustment Using the 2000 Projected U.S. Population. Healthy People 2010 Statistical Notes Nr. 20. Hyattsville, MD: National Center for Health Statistics, Januar 2001. <https://www.cdc.gov/nchs/data/statnt/statnt20.pdf>

Tabelle 2, „Selected age distributions and age-adjustment weights based on the 2000 projected U.S. population“, Distribution #12, Seite 3, wörtlich:

```text
Distribution #12                       Population in thousands   Adjustment weight
20 years and over . . . . . . . . .    195,850                   1.000000
20–39 years . . . . . . . . . . . .     77,670                   0.396579
40–59 years . . . . . . . . . . . .     72,816                   0.371795
60 years and over . . . . . . . . .     45,364                   0.231626
```

**Ergebnis:** Die drei Werte der Spezifikation sind die auf vier Stellen gerundeten Gewichte dieser Quelle: 0,396579 → 0,3966; 0,371795 → 0,3718; 0,231626 → 0,2316. Beide Fassungen summieren sich zu 1. Altersgruppen und Bezugsbevölkerung („projected U.S. Census 2000 population“, „20–39, 40–59, and 60 and over“) passen zu NHSR 158. Ein Widerspruch liegt nicht vor. Die Rundung steht als Hinweis (Frage 2) in `OFFEN.md`, weil die Quelle sechs Stellen nennt.

### 3. Definitionen 1 und 7 gegen die Dokumentation zu P_DEMO

Quelle: NHANES 2017–March 2020 Data Documentation, Codebook, and Frequencies, Demographic Variables and Sample Weights (P_DEMO), „First Published: May 2021, Last Revised: NA“. <https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm>

**Einschränkung:** Die gesicherte Fassung in `docs/cdc/` entsteht erst mit dem Lauf von `A/01_download.R`, also nach der R-Freigabe. Geprüft wurde deshalb die Live-Seite vom 23.11.2026 (SHA-256 der abgerufenen HTML-Datei: `6ac8f9b394615b8b53e1de3bc089c51bd8f1004c01efb746e303476c1f918b86`). Nach dem Skriptlauf wird die gesicherte Seite mit dieser Prüfsumme verglichen. Weicht sie ab, prüft A die Zitate erneut.

**Definition 1 (Schwangerschaft): stimmt mit der Dokumentation überein.**

- Codebuch, wörtlich: „English Text: Pregnancy status for females between 20 and 44 years of age at the time of MEC exam. Target: Females only 20 YEARS - 44 YEARS“
- Codes laut Codebuch, wörtlich: „1 | Yes, positive lab pregnancy test or self-reported pregnant at exam | 87“, „2 | The participant was not pregnant at exam | 1604“, „3 | Cannot ascertain if the participant is pregnant at exam | 183“, „. | Missing | 13686 | 15560“.
- Data Processing and Editing, wörtlich: „RIDEXPRG: Pregnancy status at the time of the health examination was ascertained for females 8–59 years of age. Due to disclosure risks pregnancy status is only released for women 20-44 years of age.“ Weiter: „Persons who were interviewed, but not examined also have an RIDEXPRG value = 3 (could not be determined).“
- Analytic Notes, wörtlich: „RIDEXPRG: Because of possible disclosure risks, pregnancy status is only released for women aged 20-44 years. The percentage of pregnant women/girls aged 8-19 or 45-59 years is less than 1% in the 2017-March 2020 pre-pandemic sample.“

Damit sind die Aussagen der Definition 1 belegt: Code 1 heißt schwanger, Code 3 heißt nicht feststellbar, und die Variable ist nur für Frauen von 20 bis 44 Jahren belegt. Die Regel `is.na(RIDEXPRG) | RIDEXPRG != 1` schließt nur Code 1 aus. Beobachtung ohne Handlungsbedarf: Schwangere von 45 bis 59 Jahren sind in den öffentlichen Daten nicht erkennbar. Ob NCHS sie für Report 158 intern ausgeschlossen hat, sagt die Dokumentation nicht. Die Fallzahl 8.295 an Abend 2 zeigt, ob das eine Rolle spielt.

**Definition 7 (Geschlecht): stimmt mit der Dokumentation überein.**

- Codebuch, wörtlich: „RIAGENDR - Gender … English Text: Gender of the participant. Target: Both males and females 0 YEARS - 150 YEARS“
- Codes, wörtlich: „1 | Male | 7721 | 7721“, „2 | Female | 7839 | 15560“, „. | Missing | 0 | 15560“.

Also 1 = männlich, 2 = weiblich, keine fehlenden Werte.

**Nebenbefund für Abend 2** (Analytic Notes, wörtlich): „Twenty-four masked variance strata and 49 masked primary sampling units (PSUs) are included in the NHANES 2017-March 2020 pre-pandemic demographics file. Each stratum has 2-3 PSUs.“ Ein Stratum mit nur einem Cluster ist danach in der vollen Datei nicht zu erwarten. Die Prüfung an Abend 2 auf der Designbasis bleibt trotzdem nötig.
