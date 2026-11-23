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

## 2026-11-24 – Spezifikation Version 2.1, vor Beginn von Abend 2

**Anlass:** zwei Fragen von Auswerter A in `OFFEN.md` (Branch `abend-1`, Pull Request 2). Justus hat beide am 24.11.2026 entschieden. Zu diesem Zeitpunkt waren noch keine Daten geladen und keine Ergebnisse gerechnet.

| Frage | Entscheidung | Beleg |
| --- | --- | --- |
| Zu welcher Schätzung gehören die Standardfehler 1,2 und 0,6? | Zur altersadjustierten. Sie werden in Stufe 4 geprüft statt in Stufe 2. | NCHS-Report Nr. 158, Tabelle 2. Die Tabelle zeigt je Zeile nur eine Schätzung, und die Anmerkung lautet: „Outcomes for adults and older adults were age adjusted by the direct method to the projected U.S. Census 2000 population.“ |
| Welche Fassung der Altersanteile gilt? | Die sechsstelligen Werte der Quelle: 0,396579, 0,371795, 0,231626. | Klein und Schoenborn, Healthy People 2010 Statistical Notes Nr. 20, Altersverteilung Nr. 12 (20–39, 40–59, ab 60 Jahre). Summe 1,000000. |

Beide Belege hat Auswerter A gelesen. Claude hat sie als Prüfer unabhängig in den Quellen nachgeschlagen und kommt zum selben Ergebnis.

**Nicht geändert:** Zielwerte, Toleranzen, Abbruchkriterium und Entscheidungsregel. Die Standardfehler 1,2 und 0,6 waren schon in Version 2 Zielwerte. Neu ist nur, an welcher Stufe sie geprüft werden.

**Folge für Auswerter B:** B rechnet Stufe 4 ohnehin und wird damit auch gegen die zwei Standardfehler geprüft.

## 2026-11-24 – Abend 1: Lauf von `A/01_download.R`

**Zeitpunkt:** 23.11.2026, 23:28 UTC (24.11.2026, 00:28 MEZ). Das Skript nimmt das Abrufdatum aus der Systemuhr der Cloud-Sitzung, die UTC zeigt. Deshalb tragen `results/A/abend1_dateien.csv` und die Dateien in `docs/cdc/` das Datum 2026-11-23.

**Arbeitsumgebung:** R und Pakete kommen aus dem Setup-Skript der Umgebung. Von Auswerter A ist nichts installiert worden.

| Komponente | Version |
| --- | --- |
| R | 4.3.3 (2024-02-29) |
| survey | 4.2.1 |
| foreign | 0.8.86 |
| digest | 0.6.34 |

**Änderungen am Skript:** keine. `A/01_download.R` lief im ersten Versuch ohne Fehler durch.

**Ergebnis: Abend 1 bestanden.** Alle vier Dateien sind ladbar, alle Zeilenzahlen stimmen mit SPEC.md überein, keine benötigte Variable fehlt. Damit ist auch das Download-Muster der Spezifikation (offener Punkt 3) für alle vier Dateien getestet.

| Datei | Bytes | Zeilen | CDC | Spalten | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| P_DEMO | 3.614.720 | 15.560 | 15.560 | 29 | `2e46c6c26bf77cd8989f64011ace12cbf42c0f3e03414eb59acc5328c8f87913` |
| P_BMX | 2.520.640 | 14.300 | 14.300 | 22 | `7038d0da3169420a4a3cbaec09ac586a701b38e1c7b925431b60e13ac24fed66` |
| P_BIOPRO | 3.420.640 | 10.409 | 10.409 | 41 | `f242cb9f9da5787f77d81ffb02822350e01cea4adf072d23bc96eb008182010c` |
| P_RXQ_RX | 16.154.000 | 32.962 | 32.962 | 13 | `0ee30345ccfee5ce0ff55e51fca4dec7389d3a8e985c59485d13400e9ec2ee2e` |

Die Tabelle ist aus `results/A/abend1_dateien.csv` übernommen, die das Skript geschrieben hat. Die Rohdaten in `data/raw/` stehen laut SPEC.md nicht im Git; ihre Prüfsummen stehen in der CSV und in `data/raw/CHECKSUMS.txt`.

**Gesicherte Dokumentation** in `docs/cdc/`, SHA-256 mit `sha256sum`:

| Datei | SHA-256 |
| --- | --- |
| `P_DEMO_2026-11-23.htm` | `6ac8f9b394615b8b53e1de3bc089c51bd8f1004c01efb746e303476c1f918b86` |
| `P_BMX_2026-11-23.htm` | `4f3736812ce18aec46d2264791d17a5990d5354bf7835dadbefff978809aba78` |
| `P_BIOPRO_2026-11-23.htm` | `ec7c2a15c1a114f907cc61f003b4c1218e625c4cbce2eadfa1e974d3bf4e38b5` |
| `P_RXQ_RX_2026-11-23.htm` | `61fd01fba7680136125d63d4fdf86aa08f12b47057a68709ac34a8a51087f0e6` |

**Vergleich mit der Quellenprüfung:** Die gesicherte P\_DEMO-Seite hat dieselbe Prüfsumme wie die am 23.11.2026 gelesene Live-Seite (`6ac8f9b3…1f918b86`, Abschnitt „Zusatzaufgabe vor Abend 2“, Punkt 3). Die Seite ist also Byte für Byte dieselbe. Die dort zitierten Stellen zu Definition 1 und 7 gelten unverändert für die gesicherte Fassung; eine erneute Prüfung der Zitate ist nicht nötig.

## 2026-11-24 – Nachtrag zum Eintrag „Spezifikation Version 2.1“

Der Eintrag zu Version 2.1 sagt, es seien noch keine Daten geladen gewesen. Genauer: Laut Eintrag vom 23.11. war P_DEMO.xpt schon per curl zum Erreichbarkeitstest abgerufen. Gerechnet war nichts.

## 2026-11-24 – Abend 2, vor dem Rechnen: Prüflauf von `A/01_download.R` und Prüfung der KI-Formel

### Prüflauf `A/01_download.R`

Gestartet am 23.11.2026, 23:40 UTC, auf dem neuen Branch `abend-2` (von `main`, Stand `2c8c406`). Alle vier Dateien wurden frisch geladen. Alle vier SHA-256-Prüfsummen stimmen mit `results/A/abend1_dateien.csv` überein, alle vier Zeilenzahlen mit SPEC.md. Kein Abbruch. Am Skript ist nichts geändert.

### Formel des Konfidenzintervalls gegen NCHS Series 2 Nr. 175

**Quelle:** Parker JD, Talih M, Malec DJ, et al. National Center for Health Statistics data presentation standards for proportions. Vital Health Stat 2(175). 2017. <https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf>, abgerufen am 23.11.2026, SHA-256 `47a0d06b8f79ceb6de2725f1b94eb2320f7f41d64214790395b4bd035bd7b683`. Text mit `pdftotext` gelesen. Die Formeln stehen im PDF als Bild. Sie sind deshalb von den gerenderten Seiten abgeschrieben und hier als Formel wiedergegeben.

**Wörtliche Stellen:**

Titelseite: „This report was revised on November 1, 2018, where on page 4, RSE(Var) was misattributed as RSE(SE). This revision had no effect on the related standard. Table II (page 9) was updated on April 8, 2021, to fix a computing error affecting the confidence interval calculations.“

Seite 2–3, effektive Stichprobengröße: „For an estimate from a complex survey, the effective sample size, n<sub>e</sub>, is defined as the sample size, n, divided by the design effect (7). One approach used to calculate n<sub>e</sub> for estimated proportions from a complex sample survey is:“ — Formel (Bild): n<sub>e</sub> = p̂(1 − p̂) / var̂(p̂).

Seite 3, Kappung: „For complex sample surveys, due to sampling design and variability, there may be cases where the effective sample size is greater than the sample size. When the effective sample size is greater than the sample size, the sample size should be used to determine whether the minimum sample size criterion is met, and it should also be used for CIs and other computations that include the effective sample size.“

Seite 3, null Ereignisse: „If the number of numerator events is 0 or equal to the denominator (the complement of 0 events), the estimated proportion will be 0 or 1, respectively. As a result, the estimated variance of the proportion will be 0, and the effective sample size will be undefined. In these cases, the sample size should be used to determine whether the minimum sample size criterion is met, and it should also be used for CIs and other computations that include the effective sample size.“

Seite 3, Methode: „The Clopper-Pearson CI (2) [adapted for complex surveys by Korn and Graubard (3) when applicable] should be used to determine whether or not the CI of a proportion meets the presentation criteria.“ Und: „For complex sample surveys, the calculation of the Clopper-Pearson CI using the approach of Korn and Graubard incorporates information from the survey design, including the effective sample size and, when appropriate, the degrees of freedom.“

Seite 4: „For complex sample surveys, default calculations from survey software may not be appropriate or feasible for all situations, including age-adjusted estimates, estimates based on multiple imputation, estimates for subgroups represented in only a subset of primary sampling units (PSUs) (e.g., some racial and ethnic groups and region-specific estimates), and when calculating annual or survey cycle estimates using a multiyear or multicycle data file. In these instances, the relevant information should be extracted and the CIs directly calculated.“

Seite 4, Freiheitsgrade: „As one rule of thumb, the degrees of freedom can be calculated as the number of PSUs minus the number of strata. This calculation is used in most NCHS surveys and implemented in survey software, although specific calculations can vary across packages. However, default calculations of degrees of freedom from survey software may not be appropriate for subgroups represented in only a subset of PSUs (e.g., some racial and ethnic groups and region-specific estimates) and when calculating annual or survey cycle estimates using a multiyear or multicycle data file. In these instances, the relevant information should be extracted and the degrees of freedom directly calculated to assess estimate precision.“

Seite 9, Fußnoten zu Tabelle II: „Sample size divided by the design effect. It is calculated in this table using this formula: n<sub>e</sub> = p̂(1 − p̂)/var̂(p̂).“ — „Lower and upper confidence bounds were computed using the Korn-Graubard method.“ — „Effective sample size is greater than sample size. Sample size used for CI calculations.“

Literatur, Seite 6: „2. Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26(4):404–13. 1934.“ und „3. Korn EL, Graubard BI. Confidence intervals for proportions with small expected number of positive counts estimated from survey data. Surv Methodol 24(2):193–201. 1998.“

**Abgleich Punkt für Punkt:**

| SPEC.md | Series 2 Nr. 175 | Urteil |
| --- | --- | --- |
| p(1 − p) / V | n<sub>e</sub> = p̂(1 − p̂)/var̂(p̂), Seite 3 und Fußnote Tabelle II | gleich |
| min(n, …) | „When the effective sample size is greater than the sample size, the sample size should be used …“ | gleich im Ergebnis, siehe Rechenprobe |
| Faktor (t(0,975; n − 1) / t(0,975; f))² | im Text nicht ausgeschrieben; nur „including the effective sample size and, when appropriate, the degrees of freedom“ mit Verweis auf Korn und Graubard (1998) | im Text nicht belegbar, durch die Rechenprobe bestätigt |
| f = Cluster minus Strata der Teilgruppe | „number of PSUs minus the number of strata“; für Teilgruppen „directly calculated“ | gleich |
| Beta-Quantile mit x und m − x + 1 bzw. x + 1 und m − x | im Text nicht ausgeschrieben; „Clopper-Pearson … adapted … by Korn and Graubard“. Das ist die übliche Beta-Form der Clopper-Pearson-Grenzen. | im Text nicht belegbar, durch die Rechenprobe bestätigt |
| Fall p = 0 oder 1 | Series 2 Nr. 175: dann n statt n<sub>e</sub> | in SPEC.md nicht geregelt, siehe unten |

**Rechenprobe an den Beispielen der Standards:** Skript `A/02_ki_formel_pruefung.R`, neu, Ausgabe `results/A/abend2_ki_formel_pruefung.csv`. Es liest keine NHANES-Rohdaten, sondern rechnet die 16 Zeilen der Anhangtabellen I (Seite 8) und II (Seite 9) aus den dort veröffentlichten n, n<sub>e</sub>, Prozentwerten und Freiheitsgraden nach. Drei Lesarten:

| Lesart | größte Abweichung | auf 0,1 gleich | gleich mit Eingaben innerhalb ihrer Rundung (± 0,05) |
| --- | --- | --- | --- |
| SPEC.md: m = min(n, n<sub>e</sub> · Faktor) | 0,085 Prozentpunkte | 10 von 16 | 16 von 16 |
| erst kappen, dann Faktor: m = min(n, n<sub>e</sub>) · Faktor | 2,326 Prozentpunkte | 6 von 16 | 8 von 16 |
| ohne Faktor: m = min(n, n<sub>e</sub>) | 1,053 Prozentpunkte | 3 von 16 | 7 von 16 |

Die Zahlen stehen in der Ausgabe des Skripts. Nur die Formel der Spezifikation trifft alle veröffentlichten Grenzen. Die beiden anderen Lesarten verfehlen sie um bis zu 2,3 Prozentpunkte. Damit sind auch die zwei Teile belegt, die der Text nicht ausschreibt: der Freiheitsgrad-Faktor und die Kappung erst nach dem Faktor. Ein Widerspruch im Text der Standards fällt dabei auf: Bei Women, Non-Hispanic Asian (n = 82, n<sub>e</sub> = 108,4, f = 7) sagt die Fußnote „Sample size used for CI calculations“, die veröffentlichten Grenzen 15,8–36,2 ergeben sich aber mit m = n<sub>e</sub> · Faktor = 76,75, also nicht mit n = 82. Mit n wären es 16,1–35,8. Die Zahlen der Tabelle folgen der SPEC-Formel.

**Urteil: Die Formel der Spezifikation weicht nicht von Series 2 Nr. 175 ab.** Abend 2 wird gerechnet.

**Lücke ohne Folge für Abend 2:** SPEC.md regelt nicht den Fall p = 0 oder 1 (V = 0, n<sub>e</sub> nicht definiert). Series 2 Nr. 175 nimmt dann n. Bei den sechs rohen Prävalenzen von Abend 2 (Zielwerte 6,4 % bis 42,1 %) kann der Fall nicht eintreten. Das Auswertungsskript bricht ab, falls er doch eintritt. Frage 3 in `OFFEN.md`, nicht blockierend.

## 2026-11-24 – Abend 2: Positivkontrolle gerechnet

**Skripte, neu:**

- `A/03_positivkontrolle.R` rechnet die Stufen 1 bis 4 und schreibt `results/A/abend2_werte.csv`. Es enthält keine Zielwerte und keine erwarteten Fallzahlen. Vor dem Lesen prüft es die SHA-256 jeder Rohdatei gegen `results/A/abend1_dateien.csv`.
- `A/04_zielvergleich.R` liest diese Datei, ergänzt Zielwert, Toleranz, Abweichung und Urteil und schreibt `results/A/abend2_positivkontrolle.csv`. Nur dieses Skript enthält die Zielwerte, abgeschrieben aus SPEC.md Version 2.1. Zielwerte und Toleranzen sind unverändert.

Beide Skripte liefen ohne Fehler und ohne Änderung nach dem ersten Lauf. Ein zweiter Lauf hat beide CSV-Dateien Byte für Byte gleich erzeugt. R 4.3.3, survey 4.2.1.

**Umsetzung der Spezifikation:**

- Designbasis: 14.300 Personen mit `RIDSTATR = 2`, alle mit `WTMECPRP > 0`. P\_BMX per `SEQN` angefügt, keine Person verloren.
- 24 Strata, 49 Cluster, 2 bis 3 Cluster je Stratum. Kein Stratum mit nur einem Cluster, also kein Eintrag in `OFFEN.md`. Freiheitsgrade des Designs: 25.
- Masken für Analysegruppe, Geschlecht, Adipositas und schwere Adipositas sind vollständige Ja/Nein-Werte ohne fehlende Angaben. Ein fehlender BMI erfüllt keine Bedingung.
- Teilgruppen über `subset()` auf dem Designobjekt, keine Zeile vorher gelöscht.
- Altersadjustiert: `svyby(..., ~altersgruppe, covmat = TRUE)` und `svycontrast` mit 0,396579, 0,371795 und 0,231626. Gegenprobe im Skript: Jede Altersgruppe einzeln als Domäne gerechnet liefert dieselben Anteile und Varianzen wie `svyby`.
- Vergleich: ungerundet, Abweichung = Wert − Ziel, bestanden bei |Abweichung| ≤ Toleranz. Vor dem Vergleich wird |Abweichung| auf 10 Nachkommastellen gerundet, damit Gleitkommareste (z. B. 0,1000000000000014) nicht zählen. Die Toleranz selbst ist unverändert.

**Ergebnis: Abend 2 bestanden. Alle 29 extern geprüften Zellen liegen innerhalb der Toleranz.** Die größte Abweichung beträgt 0,049 Prozentpunkte (schwere Adipositas, Frauen, adjustiert). Alle Abweichungen sind kleiner als 0,05, also so klein, wie es die Rundung der Zielwerte auf eine Nachkommastelle erwarten lässt. Die Tabelle ist aus `results/A/abend2_positivkontrolle.csv` erzeugt, auf drei Stellen gerundet.

| Stufe | Kennzahl | Gruppe | Art | Größe | Wert | Ziel | Abweichung | Toleranz | Urteil |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Analysegruppe | Gesamt |  | Fallzahl | 8295 | 8295 | 0,000 | 0,0 | bestanden |
| 2 | Adipositas | Gesamt | roh | Praevalenz | 41,870 | 41,9 | -0,030 | 0,1 | bestanden |
| 3 | Adipositas | Gesamt | roh | KI_unten | 39,424 | 39,4 | 0,024 | 0,2 | bestanden |
| 3 | Adipositas | Gesamt | roh | KI_oben | 44,346 | 44,3 | 0,046 | 0,2 | bestanden |
| 4 | Adipositas | Gesamt | adjustiert | Praevalenz | 41,871 | 41,9 | -0,029 | 0,1 | bestanden |
| 4 | Adipositas | Gesamt | adjustiert | Standardfehler | 1,217 | 1,2 | 0,017 | 0,1 | bestanden |
| 2 | Schwere Adipositas | Gesamt | roh | Praevalenz | 8,976 | 9,0 | -0,024 | 0,1 | bestanden |
| 3 | Schwere Adipositas | Gesamt | roh | KI_unten | 7,780 | 7,8 | -0,020 | 0,2 | bestanden |
| 3 | Schwere Adipositas | Gesamt | roh | KI_oben | 10,289 | 10,3 | -0,011 | 0,2 | bestanden |
| 4 | Schwere Adipositas | Gesamt | adjustiert | Praevalenz | 9,238 | 9,2 | 0,038 | 0,1 | bestanden |
| 4 | Schwere Adipositas | Gesamt | adjustiert | Standardfehler | 0,634 | 0,6 | 0,034 | 0,1 | bestanden |
| 1 | Analysegruppe | Männer |  | Fallzahl | 4051 | 4051 | 0,000 | 0,0 | bestanden |
| 2 | Adipositas | Männer | roh | Praevalenz | 41,584 | 41,6 | -0,016 | 0,1 | bestanden |
| 3 | Adipositas | Männer | roh | KI_unten | 37,444 | 37,4 | 0,044 | 0,2 | bestanden |
| 3 | Adipositas | Männer | roh | KI_oben | 45,814 | 45,8 | 0,014 | 0,2 | bestanden |
| 4 | Adipositas | Männer | adjustiert | Praevalenz | 41,795 | 41,8 | -0,005 | 0,1 | bestanden |
| 2 | Schwere Adipositas | Männer | roh | Praevalenz | 6,425 | 6,4 | 0,025 | 0,1 | bestanden |
| 3 | Schwere Adipositas | Männer | roh | KI_unten | 5,095 | 5,1 | -0,005 | 0,2 | bestanden |
| 3 | Schwere Adipositas | Männer | roh | KI_oben | 7,977 | 8,0 | -0,023 | 0,2 | bestanden |
| 4 | Schwere Adipositas | Männer | adjustiert | Praevalenz | 6,617 | 6,6 | 0,017 | 0,1 | bestanden |
| 1 | Analysegruppe | Frauen |  | Fallzahl | 4244 | 4244 | 0,000 | 0,0 | bestanden |
| 2 | Adipositas | Frauen | roh | Praevalenz | 42,140 | 42,1 | 0,040 | 0,1 | bestanden |
| 3 | Adipositas | Frauen | roh | KI_unten | 39,559 | 39,6 | -0,041 | 0,2 | bestanden |
| 3 | Adipositas | Frauen | roh | KI_oben | 44,753 | 44,8 | -0,047 | 0,2 | bestanden |
| 4 | Adipositas | Frauen | adjustiert | Praevalenz | 41,847 | 41,8 | 0,047 | 0,1 | bestanden |
| 2 | Schwere Adipositas | Frauen | roh | Praevalenz | 11,381 | 11,4 | -0,019 | 0,1 | bestanden |
| 3 | Schwere Adipositas | Frauen | roh | KI_unten | 9,678 | 9,7 | -0,022 | 0,2 | bestanden |
| 3 | Schwere Adipositas | Frauen | roh | KI_oben | 13,267 | 13,3 | -0,033 | 0,2 | bestanden |
| 4 | Schwere Adipositas | Frauen | adjustiert | Praevalenz | 11,749 | 11,7 | 0,049 | 0,1 | bestanden |

**Standardfehler ohne externes Ziel** (Urteil `extern nicht geprüft`, maßgeblich ist später der Vergleich mit B), in Prozentpunkten:

| Kennzahl | Gruppe | Art | Standardfehler |
| --- | --- | --- | --- |
| Adipositas | Gesamt | roh | 1,181 |
| Schwere Adipositas | Gesamt | roh | 0,597 |
| Adipositas | Männer | roh | 1,993 |
| Adipositas | Männer | adjustiert | 2,050 |
| Schwere Adipositas | Männer | roh | 0,679 |
| Schwere Adipositas | Männer | adjustiert | 0,718 |
| Adipositas | Frauen | roh | 1,245 |
| Adipositas | Frauen | adjustiert | 1,248 |
| Schwere Adipositas | Frauen | roh | 0,852 |
| Schwere Adipositas | Frauen | adjustiert | 0,915 |

Beobachtung ohne Folge: Die rohen Standardfehler der Gesamtgruppe (1,181 und 0,597) lägen ebenfalls innerhalb der Toleranz zu 1,2 und 0,6. Die Zuordnung zur adjustierten Schätzung aus Version 2.1 entscheidet also nicht über das Ergebnis.

**Konfidenzintervalle, Angaben zur Formel:**

| Kennzahl | Gruppe | n | f | m |
| --- | --- | --- | --- | --- |
| Adipositas | Gesamt | 8295 | 25 | 1581,8 |
| Schwere Adipositas | Gesamt | 8295 | 25 | 2073,3 |
| Adipositas | Männer | 4051 | 25 | 554,1 |
| Schwere Adipositas | Männer | 4051 | 25 | 1181,6 |
| Adipositas | Frauen | 4244 | 25 | 1424,7 |
| Schwere Adipositas | Frauen | 4244 | 25 | 1257,6 |

In allen sechs Fällen ist m kleiner als n, die Kappung greift nicht. f = 25 in jeder Teilgruppe: Alle 49 Cluster und 24 Strata enthalten Personen jeder Teilgruppe.

**`svyciprop(method = "beta")`:** zusätzlich ausgegeben (Zeilen `KI_unten_svyciprop_beta` und `KI_oben_svyciprop_beta`, Urteil `extern nicht geprüft`). Größte Differenz zur Formel der Spezifikation: 7,1 · 10⁻¹⁵ Prozentpunkte, also Rechenrauschen. Laut Quelltext von survey 4.2.1 rechnet `svyciprop` mit n<sub>e</sub> · (t(nrow(design) − 1)/t(degf(design)))² ohne Kappung bei n. Für das Teilgruppen-Design ist `nrow` gleich n (geprüft für die Gesamtgruppe: 8.295) und `degf` gleich 25 = f. Weil die Kappung hier nicht greift, ist das dieselbe Rechnung. Unter offenem Punkt 8 der Spezifikation ist damit beantwortet, ob `svyciprop` dasselbe liefert: hier ja.

**Nicht gerechnet:** altersadjustierte Konfidenzintervalle. Laut SPEC.md sind sie kein Kriterium, und SPEC.md legt dafür keine Formel fest.

**Offen:** Frage 3 in `OFFEN.md` (Randfall p = 0 oder 1), ohne Einfluss auf Abend 2.
