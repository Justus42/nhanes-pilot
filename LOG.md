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

## 2026-11-24 – Nachtrag zum Eintrag „Abend 2: Positivkontrolle gerechnet“

### Änderungen an `A/03_positivkontrolle.R` nach dem ersten Lauf

Der Eintrag sagt, beide Skripte liefen „ohne Änderung nach dem ersten Lauf“. Für `A/04_zielvergleich.R` stimmt das. Für `A/03_positivkontrolle.R` stimmt es nicht. Nach dem ersten Lauf von A/03 habe ich drei Dinge geändert:

1. Die Zeile `sub_alter <- subset(des, basis[[gruppen[[g]]]])` gestrichen. Sie baute dasselbe Teilgruppen-Design wie das schon vorhandene Objekt `sub` ein zweites Mal.
2. In `svyby(...)` deshalb `sub_alter` durch `sub` ersetzt.
3. Am Ende fünf Zeilen ergänzt, die die größte Differenz zwischen SPEC-Formel und `svyciprop(method = "beta")` auf die Konsole schreiben. Sie schreiben nichts in eine Datei.

**Reihenfolge:** erster Lauf von A/03, dann die drei Änderungen, dann zweiter Lauf von A/03, erst danach der erste Lauf von A/04. A/04 hat also nie die Ausgabe der ersten Fassung von A/03 gelesen. Committet ist nur die geänderte Fassung (Commit `c0b4a40`).

**Wirkung auf `results/A/abend2_werte.csv`: keine.** Die Datei des ersten Laufs ist beim zweiten Lauf überschrieben worden und nicht erhalten. Geprüft habe ich deshalb so: Die erste Fassung wurde durch Rückbau genau dieser drei Änderungen wiederhergestellt (`diff` gegen die committete Fassung zeigt nur sie) und in einer getrennten Kopie des Arbeitsverzeichnisses außerhalb des Repos gegen dieselben Rohdaten ausgeführt, einmal mit und einmal ohne `LANG=C.UTF-8`, wie beim ersten Lauf. Beide Male ist die erzeugte Datei Byte für Byte gleich der committeten `abend2_werte.csv` (SHA-256 `1e2473729aca654823c5872ddc14b3d9408eea53afc56e66821c00ef0b170755`). Einschränkung: Verglichen ist eine Rekonstruktion der ersten Fassung, nicht die ursprüngliche Datei.

Der Satz „Ein zweiter Lauf hat beide CSV-Dateien Byte für Byte gleich erzeugt“ im Eintrag meint einen weiteren Lauf der schon geänderten Fassung von A/03 und von A/04. Er belegt nichts über die erste Fassung.

### Abgeschriebene Eingabe der Zeile Men, Non-Hispanic black

**Wo der Fehler stand:** nicht in `A/02_ki_formel_pruefung.R`, sondern in einem vorläufigen Prüfskript im Scratchpad der Sitzung, das ich vor A/02 geschrieben und nicht committet habe. A/02 entstand erst danach und enthielt von Anfang an den richtigen Wert.

**Zuerst stand da:** n = 195, n<sub>e</sub> = 242,2, Prozentwert **42,1**, f = 12, Grenzen 28,3–42,1. **Jetzt steht da** (in A/02, Zeile `Men_NH_black`): n = 195, n<sub>e</sub> = 242,2, Prozentwert **34,9**, f = 12, Grenzen 28,3–42,1. Falsch war nur der Prozentwert. Ich hatte die obere Grenze 42,1 in die Spalte „Percent estimate“ übernommen.

**Woran ich es bemerkt habe:** Im ersten Lauf des vorläufigen Skripts traf die SPEC-Formel 12 der 13 damals eingegebenen Zeilen auf höchstens 0,08 Prozentpunkte. Diese Zeile lag dagegen 7,26 Prozentpunkte daneben, die beiden anderen Lesarten 7,26 und 8,06. Dabei fiel auf, dass der eingegebene Prozentwert genau der veröffentlichten oberen Grenze glich. Ich habe dann die gerenderte Seite 9 der Quelle erneut angesehen. Dort lautet die Zeile „Non-Hispanic black … 195 242.2 34.9 3.06 8.8 28.3 42.1 13.8 39.5 12“. Am 24.11.2026 noch einmal im Text des PDF (`pdftotext -layout`) nachgesehen: dieselbe Zeile, Prozentwert 34.9. Anlass für das Nachsehen war also die Abweichung im eigenen Ergebnis. Grundlage der Korrektur ist allein die Quelle.

**Weitere Änderung an A/02 nach dessen erstem Lauf:** Ich habe die Prüfung ergänzt, ob die Abweichungen durch die Rundung der Eingaben erklärbar sind. Dazu kamen die Funktion `erklaerbar` und die Spalte `durch_rundung_erklaerbar` in `results/A/abend2_ki_formel_pruefung.csv` hinzu. Die übrigen Werte blieben gleich. Die Konsolenausgabe beider Läufe nennt dieselben größten Abweichungen (0,085, 2,326 und 1,053 Prozentpunkte). Committet ist der zweite Lauf (Commit `65048fa`).

## 2026-11-24 – Abend 3: Zweitauswertung durch B und Vergleich

Gerechnet von der Vergleichssitzung (Claude Code, nicht Auswerter A), Branch `abend-3` von `main` (Stand `d37f556`).

### Prüflauf `A/01_download.R`

Alle vier Dateien frisch geladen. Alle vier SHA-256-Prüfsummen stimmen mit `results/A/abend1_dateien.csv` überein, alle vier Zeilenzahlen mit SPEC.md. Kein Abbruch. Am Skript ist nichts geändert.

### Skript von Auswerter B

- `B/positivkontrolle.py`, geschrieben von Gemini 4 Neon, übergeben von Justus im Auftrag für Abend 3. Unverändert abgelegt und vor dem ersten Lauf einzeln committet (`c565808`).
- 534 Zeilen, SHA-256 `2da4f20041d573b61a26f96fb220593b69bbba8f50a9d5916401a4aac769141a`. Die Datei endet mit genau einem Zeilenumbruch nach der letzten Zeile. Ob die Vorlage einen hatte, lässt der Auftragstext nicht erkennen.
- Umgebung: Python 3.13.18, pandas 3.0.5, numpy 2.5.3. Nichts installiert. scipy ist vorhanden, lässt sich aber nicht importieren (für numpy < 1.28 gebaut). B importiert scipy nicht, der Lauf ist davon nicht betroffen.
- Lauf mit `python3 B/positivkontrolle.py` aus dem Wurzelverzeichnis: kein Abbruch. Ausgabe `results/B/abend2_positivkontrolle.csv`, 27 Zeilen. Prüfsumme des Skripts nach dem Lauf unverändert. Ein zweiter Lauf erzeugt die CSV Byte für Byte gleich (SHA-256 `0f80fae83bda82ae46cde19b8ae26d0b2b000aa60c57b3888944687585e5b461`).
- Konsolenausgabe von B, wörtlich:

```text
[Hinweis] P_DEMO.xpt: 574 SAS-XPT-Nullartefakte (|x| < 1e-50) in Spalte 'RIDAGEYR' auf 0.0 gesetzt.
[Hinweis] P_DEMO.xpt: 1260 SAS-XPT-Nullartefakte (|x| < 1e-50) in Spalte 'WTMECPRP' auf 0.0 gesetzt.
Designbasis: 14300 Personen, 24 Strata, 49 Cluster.
```

  Die zwei Hinweise betreffen Werte, die `pandas.read_sas` als winzige Zahl statt als 0 liest. 1.260 ist genau die Zahl der nicht untersuchten Personen (15.560 − 14.300), deren Gewicht 0 ist. 574 Werte betreffen das Alter 0 (unter einem Jahr). Weder Alter 0 noch Gewicht 0 gehört zur Analysegruppe (Alter ab 20, Gewicht > 0). Einfluss auf das Ergebnis: keiner. Designbasis, Strata und Cluster gleich wie bei A.

### `vergleich.py`

Neu, im Wurzelverzeichnis, nur Python-Standardbibliothek. Liest `SPEC.md`, `results/A/abend2_positivkontrolle.csv` und `results/B/abend2_positivkontrolle.csv` und schreibt `results/vergleich_abend2.csv`. Festlegungen:

- **Zeilen:** die 27 Zeilen, die B rechnet (Stufen 1, 2 und 4). Stufe 3 rechnet laut SPEC.md nur A. Ihr Urteil steht in der Datei von A. Für B gäbe es dort kein Urteil aus den drei zulässigen Werten.
- **Zuordnung:** eine sichtbare Tabelle `ZUORDNUNG_TEXT` mit 27 Zeilen im Skript. B schreibt `methode` = `ungewichtet` / `roh` / `altersadjustiert` und eine Spalte `einheit`, A schreibt `art` = leer / `roh` / `adjustiert`. Kennzahl, Gruppe und Größe heißen bei beiden gleich. Das Skript bricht ab, wenn eine Zeile von B oder eine Zeile von A der Stufen 1, 2, 4 nicht in der Tabelle steht, eine Bezeichnung nicht genau einmal vorkommt, die Stufe abweicht oder die Einheit von B nicht stimmt. Kein Abbruch.
- **Zielwerte und Toleranzen:** aus SPEC.md gelesen (Satz „Erwartet werden …“, Zieltabelle, Satz zu den zwei Standardfehlern, Tabellen „Toleranz, vorab festgelegt“ und „Übereinstimmung A gegen B“), nicht abgetippt. Gegenprobe: Die Spalte `zielwert` in der Datei von A muss gleich sein, ebenso das Urteil „A gegen Ziel“. Beides stimmt in allen 27 Zeilen. Gelesene Toleranzen: gegen Ziel 0 / 0,1 / 0,1, A gegen B 0 / 0,01 / 0,01 (Fallzahl / Prävalenz / Standardfehler). Unverändert.
- **Urteil:** Abweichung ungerundet, bestanden bei |Abweichung| ≤ Toleranz. Fallzahlen als ganze Zahlen exakt. Wie in `A/04_zielvergleich.R` wird |Abweichung| vorher auf 10 Nachkommastellen gerundet. Zusätzlich prüft das Skript, dass das Urteil ohne diese Rundung gleich ausfällt, sonst bricht es ab. Kein Grenzfall aufgetreten.
- An `vergleich.py` ist nach dem ersten Lauf nichts geändert. Ein zweiter Lauf erzeugt `results/vergleich_abend2.csv` Byte für Byte gleich.

SHA-256 der Eingaben beim Lauf: SPEC.md `2727ca9e15ceee64c3a8d4043f80be305bccb8d50ffdcd5f693e5ecb12d623cb`, `results/A/abend2_positivkontrolle.csv` `03925b3af59525105ad70f4a18c5310d2451dab8222a1bd108afd265bee88abd`.

### Ergebnis: Abend 3 bestanden

- **B gegen Ziel:** 17 von 17 extern geprüften Zellen der Stufen 1, 2 und 4 bestanden (3 Fallzahlen, 12 Prävalenzen, 2 Standardfehler). Die übrigen 10 Zeilen (Standardfehler) sind `extern nicht geprüft`.
- **A gegen Ziel:** dieselben 17 von 17 bestanden, wie in Abend 2.
- **A gegen B:** 27 von 27 bestanden. Die Fallzahlen sind gleich. Die größte Differenz bei Prävalenzen und Standardfehlern beträgt 7,1 · 10⁻¹⁵ Prozentpunkte (Adipositas, Frauen, roh und adjustiert), also Rechenrauschen der Gleitkommazahlen. In 14 der 24 gewichteten Zeilen sind die Werte bitgleich.

A (R, `survey`) und B (Python, Varianz von Hand) liefern damit auf getrennten Wegen dieselben Schätzer und Standardfehler. Das bestätigt die Programmierung, nicht die Spezifikation selbst (SPEC.md, Definition 6).

**Stand des Pilots:** Abende 1, 2 und 3 bestanden. Abend 4 steht aus.

## 2026-11-24 – Abend 4, Phase 1 (vor dem Zählen)

Auswerter A, Branch `abend-4` von `main` (Stand `e8d253c`, nach Abend 3). Gezählt ist noch nichts. Keine Datei von B, `results/B/`, `vergleich.py` oder `results/vergleich_abend2.csv` ist geöffnet worden.

### 1. Prüflauf `A/01_download.R`

Gestartet am 24.11.2026, 05:50 UTC. Alle vier Dateien wurden frisch geladen. Alle vier SHA-256-Prüfsummen stimmen mit `results/A/abend1_dateien.csv` überein, alle vier Zeilenzahlen stimmen mit SPEC.md. Kein Abbruch. Am Skript ist nichts geändert. R 4.3.3, von A nichts installiert.

### 2. Kreatinin zwischen den Geräten (P\_BIOPRO)

Gelesen: `docs/cdc/P_BIOPRO_2026-11-23.htm`, SHA-256 `ec7c2a15c1a114f907cc61f003b4c1218e625c4cbce2eadfa1e974d3bf4e38b5`, gleich der Prüfsumme aus Abend 1. Kopf der Seite: „Standard Biochemistry Profile (P_BIOPRO) … First Published: August 2021 Last Revised: NA“.

**Ergebnis: Die CDC schreibt für `LBXSCR` innerhalb des Zyklus 2017–März 2020 keine Umrechnung zwischen Geräten vor.** Laut der Seite ist der ganze Zyklus auf einem Gerät gemessen. Die Umrechnungsgleichungen gelten nur für den Vergleich mit den Zyklen bis 2015–2016. `LBXSCR` wird unverändert verwendet. Damit ist auch Punkt 4 der offenen Punkte in SPEC.md beantwortet: Die Gleichung der Dokumentation betrifft den Wechsel zwischen den Zyklen, nicht die kombinierte Datei.

Wörtlich, Abschnitt „Description of Laboratory Methodology“:

> All methods were measured on the Roche Cobas 6000 (c501 module) analyzer.

Wörtlich, Abschnitt „Analytic Notes“, Überschrift „Standard Biochemistry Profile regression equations to compare 2017-March 2020 and 2015-2016 data“:

> Method validation (bridging) studies were performed to compare results from a laboratory, instrument, and method change between the 2015-2016 and 2017-2018 survey cycles using NHANES samples from late 2016. During the 2015-2016 cycle the Beckman Coulter UniCel DxC 800 Synchron was upgraded to the Beckman Coulter UniCel DxC 660i Synchron Access chemistry analyzer (DxC 660i). Previous analyses indicated that no statistical adjustment is needed for results obtained between the two Beckman UniCel® analyzers (i.e., DxC 800 and DxC 660i). During the 2017-2018 cycle the Roche Cobas 6000 chemistry analyzer (Cobas 6000) was used for the entire 2017-2018 cycle. Analyses comparing results obtained from the Cobas 6000 to those obtained from the DxC 660i using selected serum samples (n=248) from NHANES participants in 2016 indicate that adjustments are needed for some analytes as described below.

> It is recommended that these equations be used when examining trends among standard biochemistry profile data across 1999-2016 and 2017-2018 cycles, or when combining 2017-2018 data with previous cycles.

Zeile `LBXSCR` der Tabelle, wörtlich:

> LBXSCR (mg/dL) | Non-weighted Deming | X (Cobas 6000) = 0.9515 [95% CI: 0.9365 to 0.9665] * Y (DxC 660i) + 0.06608 [95% CI: 0.05252 to 0.07963] | X (DxC 660i) = 1.051 [95%CI: 1.034 to 1.068] * Y (Cobas 6000) - 0.06945 [95%CI: -0.08474 to -0.05415] | 3.354 | 0.993

Einschränkung: Der Satz zu den Bridging-Studien nennt ausdrücklich nur 2017–2018. Für 2019–März 2020 stützt sich das Ergebnis auf den Satz „All methods were measured on the Roche Cobas 6000 (c501 module) analyzer“ in der Dokumentation der kombinierten Datei. Die Seite listet die Methodendokumente zu Kreatinin in zwei Fassungen („February 2020“ und „August 2021“). Diese Dokumente sind nicht gesichert und nicht gelesen.

Codebuch `LBXSCR`, wörtlich: „0.25 to 14.97 | Range of Values | 9475“, „. | Missing | 934 | 10409“. Untere Nachweisgrenze laut Analytic Notes: 0.10 mg/dL. Kein Wert liegt laut Codebuch darunter.

### 3. Formeln gegen die Originalarbeiten

**CKD-EPI 2021: geprüft, stimmt.**

Quelle: Inker LA, Eneanya ND, Coresh J, et al. New Creatinine- and Cystatin C–Based Equations to Estimate GFR without Race. N Engl J Med 2021;385:1737–1749. doi:[10.1056/NEJMoa2102953](https://doi.org/10.1056/NEJMoa2102953), PMID 34554658. Gelesen am 24.11.2026 über PubMed Central (PMC8822996). Das ist das Autorenmanuskript in PMC, nicht der gesetzte Text des NEJM.

Tabelle 2, Zeile „2021 CKD-EPI creatinine (2009 CKD-EPI creatinine fit without race); eGFRcr(AS), new“, wörtlich:

> 142 (139 to 144) | F: −0.241 (−0.344 to −0.138); M: −0.302 (−0.403 to −0.202) | −1.200 (−1.211 to −1.189) | — | — | 0.9938 (0.9935 to 0.9942) | 1.012 (1.000 to 1.023) | —

Fußnote zu Tabelle 2, wörtlich:

> The cells show coefficients to use in the following formula: eGFR=μ×min(Scr/k,1)^a_1_^×max(Scr/k,1)^a_2_^×min(Scys/0.8,1)^b_1_^×max(Scys/0.8,1)^b_2_^×c^Age^×d[if female]×e[if Black]. Here, κ is 0.7 for female participants and 0.9 for male participants, min indicates the minimum of Scr/κ and 1, and max indicates the maximum of Scr/κ and 1.

> The coefficient a_1_ is used for levels of creatinine less than or equal to 0.9 mg per deciliter for male participants and 0.7 mg per deciliter for female participants. The coefficient a_2_ is used for levels of creatinine greater than 0.9 mg per deciliter for male participants and 0.7 mg per deciliter for female participants.

| SPEC.md | Originalarbeit, Tabelle 2 | Urteil |
| --- | --- | --- |
| 142 | μ = 142 | gleich |
| min(Krea/k, 1)^a, Frauen a = −0,241, Männer a = −0,302 | a₁: F −0.241, M −0.302 | gleich |
| max(Krea/k, 1)^(−1,200) | a₂ = −1.200 | gleich |
| k = 0,7 Frauen, 0,9 Männer | κ = 0.7 female, 0.9 male | gleich |
| 0,9938^Alter | c = 0.9938 | gleich |
| bei Frauen mal 1,012 | d = 1.012 | gleich |
| kein Faktor für Rasse | e: „—“ | gleich |

Die Arbeit nennt Kreatinin in mg/dL („mg per deciliter“) und Ergebnisse in ml/min/1,73 m². Die Studienteilnehmer waren laut Methodenteil „18 years of age or older“, passend zur Analysegruppe ab 18.

**Körperoberfläche nach DuBois: nicht gegen das Original geprüft.**

Quelle: Du Bois D, Du Bois EF. A formula to estimate the approximate surface area if height and weight be known. Arch Intern Med 1916;17:863–871; Nachdruck Nutrition 1989;5:303–311 (PMID 2520314). PubMed führt nur den Nachdruck, ohne Abstract und ohne Volltext in PMC. Die Verlagsseite (`jamanetwork.com`), `doi.org` und `archive.org` sind aus dieser Cloud-Sitzung gesperrt: `CONNECT tunnel failed, response 403` vom Proxy; ein zweiter Versuch über das Abrufwerkzeug scheiterte an der Namensauflösung. **Die Formel der Spezifikation ist hier nicht belegt.**

**Cockcroft-Gault: nicht gegen das Original geprüft.**

Quelle: Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine. Nephron 1976;16:31–41. doi:[10.1159/000180580](https://doi.org/10.1159/000180580), PMID 1244564. Kein Volltext in PMC. `karger.com` und `doi.org` sind gesperrt, wie oben. Gelesen ist nur das Abstract in PubMed, wörtlich:

> A formula has been developed to predict creatinine clearance (Ccr) from serum creatinine (Scr) in adult males: (see article)(15% less in females). Derivation included the relationship found between age and 24-hour creatinine excretion/kg in 249 patients aged 18-92.

Damit ist nur der Faktor 0,85 bei Frauen belegt („15% less in females“). Der Aufbau der Formel ((140 − Alter) · Gewicht / (72 · Kreatinin)) ist hier nicht belegt.

**De-Indexierung** (indexierter Wert · Körperoberfläche / 1,73) ist eine Umrechnung der Einheit und stammt aus keiner der drei Arbeiten.

Aus dem Gedächtnis ist keine Formel geprüft. Die Erwartungswerte der Rechentests hat die Spezifikation aus ihren eigenen Formeln berechnet (offener Punkt 7). Die Tests zeigen also, dass der Code die Formeln der Spezifikation umsetzt. Ob diese Formeln den Originalen entsprechen, zeigen sie nicht. Die Frage, ob trotzdem gezählt wird, steht als Frage 4 in `OFFEN.md`.

### 4. Funktionen und Rechentests

**Skripte, neu:**

- `A/05_formeln.R`: nur Funktionen, liest keine Daten. `ckd_epi_2021`, `kof_dubois`, `ckd_epi_deindex`, `cockcroft_gault`, `kategorie` und `name_trifft` (Namensabgleich für `RXDDRUG` nach SPEC.md). Jede Funktion bricht bei fehlender, nicht endlicher oder nicht positiver Eingabe ab, beim Geschlecht bei einem anderen Wert als 1 oder 2. Vor dem ersten Lauf ergänzt: In `name_trifft` wird ein fehlender Name vor der Zerlegung durch einen leeren Text ersetzt. Er ergibt ohnehin keinen Treffer.
- `A/06_rechentests.R`: die neun Rechentests aus SPEC.md mit den Erwartungswerten und Toleranzen der Spezifikation (0,01, bei der Körperoberfläche 0,0001 m²), dazu neun eigene Zusatzprüfungen von A zu Kategoriegrenzen und Namensabgleich. Die Zusatzprüfungen sind kein Kriterium der Spezifikation. Bricht ab, wenn ein Test nicht besteht. Schreibt `results/A/abend4_rechentests.csv`.

**Ergebnis des ersten Laufs: alle 9 Rechentests der Spezifikation und alle 9 Zusatzprüfungen bestanden.** Die Werte stammen aus `results/A/abend4_rechentests.csv`, auf sechs Stellen gerundet:

| Fall | Erwartet | Berechnet | Abweichung | Toleranz |
| --- | --- | --- | --- | --- |
| Mann, 60 J., 72 kg, Krea 1,0: Cockcroft-Gault | 80,00 | 80,000000 | 0,000000 | 0,01 |
| Frau, 60 J., 72 kg, Krea 1,0: Cockcroft-Gault | 68,00 | 68,000000 | 0,000000 | 0,01 |
| Mann, 60 J., Krea 0,9: CKD-EPI indexiert | 97,78 | 97,775014 | −0,004986 | 0,01 |
| Frau, 60 J., Krea 0,7: CKD-EPI indexiert | 98,95 | 98,948315 | −0,001685 | 0,01 |
| Mann, 60 J., Krea 1,8: CKD-EPI indexiert | 42,56 | 42,559047 | −0,000953 | 0,01 |
| Mann, 60 J., Krea 0,45: CKD-EPI indexiert | 120,54 | 120,542154 | 0,002154 | 0,01 |
| Frau, 60 J., Krea 0,35: CKD-EPI indexiert | 116,94 | 116,938261 | −0,001739 | 0,01 |
| 72 kg, 175 cm: Körperoberfläche | 1,8704 | 1,870403 | 0,000003 | 0,0001 |
| Mann, 60 J., 72 kg, 175 cm, Krea 1,8: CKD-EPI de-indexiert | 46,01 | 46,013049 | 0,003049 | 0,01 |

Alle Abweichungen sind kleiner als 0,005 (Körperoberfläche: kleiner als 0,00005). Das passt zur Rundung der Erwartungswerte auf zwei beziehungsweise vier Nachkommastellen. Die Konsole zeigt Umlaute als Oktalfolgen, weil die Sitzung ohne `LANG` läuft. Die CSV-Datei ist UTF-8.

SHA-256 beim Lauf: `A/05_formeln.R` `f0645e738f4bc4a111f3a9ee863d16b472cd7e3e405c54876574477b7e921172`, `A/06_rechentests.R` `5ac912fbb4e9f1f507aed15b4a5768f3aa5542cbe9ad5a6a5699e8eeb5a995b4`, `results/A/abend4_rechentests.csv` `78a3bc2896d2d5275297730f52acbaf1f2bb7fb34306793c69123b10a57b8547`.

### 5. Abschnitt „Abend 4“ erneut gelesen: Fragen vor dem Zählen

Gegen die gesicherten Seiten zu P\_RXQ\_RX, P\_BMX und P\_BIOPRO gelesen. Vier Fragen stehen in `OFFEN.md`:

- Frage 4: Cockcroft-Gault und DuBois nicht gegen das Original geprüft. **Vor dem Zählen zu entscheiden.**
- Frage 5: Name der Bezeichnerspalte und Reihenfolge in beiden Ausgabedateien. Nicht blockierend.
- Frage 6: „Ein Gewichtskriterium gibt es hier nicht“ meint nach Lesart von A das Stichprobengewicht. Ohne Wirkung auf die Analysegruppe. Nicht blockierend.
- Frage 7: Die Rückführbarkeit des Kreatinins auf IDMS ist in der Dokumentation nicht belegt. Nicht blockierend.

**Stellen ohne Widerspruch zur Spezifikation**, wörtlich aus der Dokumentation:

- P\_RXQ\_RX, RXDUSE: „In the past 30 days, have you used or taken medication for which a prescription is needed?“ Codes „1 | Yes | 24246“, „2 | No | 8701“, „7 | Refused | 7“, „9 | Don't know | 8“. Das passt zu „berichtete Einnahme im letzten Monat“.
- P\_RXQ\_RX, RXDDRUG: „For multi-ingredient products, the ingredients were listed in alphabetical order (i.e., Acetaminophen; Codeine).“ Codes „55555 | Unknown | 20“, „77777 | Refused | 46“, „99999 | Don't know | 156“, „< blank > | Missing | 8716“. 24.024 Zeilen mit Namen plus 20 + 46 + 156 ergeben genau die 24.246 Zeilen mit `RXDUSE = 1`.
- P\_RXQ\_RX: „Respondent sequence number (SEQN) in the prescription medication data is not a unique identifier. […] Analysts should convert a drug-level data to a person-level data […] before merging“. Das deckt sich mit SPEC.md.
- P\_BMX: „RIDEXPRG for several pregnant women who were outside of this age range are not reported due to disclosure concerns. The body measures data for these participants are also not reported.“ Schwangere außerhalb von 20–44 Jahren haben also kein `BMXWT` und kein `BMXHT`. Sie fallen über die Bedingung „vorhanden“ ohnehin aus der Analysegruppe. Kein Widerspruch zu Definition 1.
- P\_BMX: „The body weight data for participants who had limb amputations were set to “missing.”“ Diese Personen fallen ebenfalls aus der Analysegruppe. Das ist eine Folge der Spezifikation, kein Widerspruch.

## 2026-11-24 – Abend 4, Phase 1, Zusatz: Lesart der Ausgabe (vor dem Zählen)

Auftrag von Justus nach dem Entwurfs-PR 6. Es ist weiterhin nichts gezählt. Kein Skript ist geändert. Das Zählskript gibt es noch nicht. Es setzt die folgende Lesart um.

**Bezeichnungen.** A ist die Analysegruppe aus SPEC.md, Abend 4: alle `SEQN` aus P\_DEMO mit `RIDAGEYR >= 18`, `RIDSTATR = 2`, `RIAGENDR` gleich 1 oder 2, `is.na(RIDEXPRG) | RIDEXPRG != 1` sowie `LBXSCR`, `BMXWT` und `BMXHT` jeweils vorhanden und größer null. P\_BIOPRO und P\_BMX werden per `SEQN` an P\_DEMO angefügt, ohne Personen zu verlieren. Eine Trefferzeile ist eine Zeile aus P\_RXQ\_RX mit `RXDUSE = 1` (nicht fehlend) und einem Namen, der laut `name_trifft` einen Suchbegriff der Zeile trifft. P(z) ist die Personenmenge der Ausgabezeile z: in einer Wirkstoffzeile die Personen aus A mit mindestens einer Trefferzeile für deren Suchbegriffe, in `GESAMT` ganz A. Alle Werte gehen ungerundet ein. „Unter 60“ heißt Wert < 60, gleichbedeutend mit einer Kategorie aus `u30`, `30_45`, `45_60`.

### 1. Welche Personenmenge zählt jede Spalte?

| Spalte | gezählte Personenmenge |
| --- | --- |
| `n_personen` | Alle Personen in P(z), also in einer Wirkstoffzeile die Personen der Analysegruppe mit mindestens einer Trefferzeile, in `GESAMT` die ganze Analysegruppe. |
| `n_ckdepi_u60` | Die Personen in P(z), deren CKD-EPI 2021 indexiert unter 60 ml/min/1,73 m² liegt. |
| `n_deindex_u60` | Die Personen in P(z), deren CKD-EPI 2021 de-indexiert (indexiert · KOF nach DuBois / 1,73) unter 60 ml/min liegt. |
| `n_cg_u60` | Die Personen in P(z), deren Cockcroft-Gault-Wert unter 60 ml/min liegt. |
| `n_irgendeine_u60` | Die Personen in P(z), bei denen mindestens einer der drei Werte unter 60 liegt; jede Person zählt höchstens einmal (Vereinigung, nicht Summe). |
| `n_diskordant_cg_ckdepi` | Die Personen in P(z), deren Kategorie nach Cockcroft-Gault (`u30`, `30_45`, `45_60`, `ab60`) sich von der Kategorie nach CKD-EPI indexiert unterscheidet, egal an welcher der drei Grenzen. |
| `n_diskordant_cg_deindex` | Die Personen in P(z), deren Kategorie nach Cockcroft-Gault sich von der Kategorie nach CKD-EPI de-indexiert unterscheidet, egal an welcher Grenze. |
| `n_alter_80` | Die Personen in P(z) mit `RIDAGEYR = 80`, also mit dem auf 80 gedeckelten Alter. |

Jede Spalte außer `n_personen` ist eine Teilmenge von P(z). Daraus folgen Prüfungen, die das Zählskript vor dem Schreiben macht: Jede Spalte ist kleiner oder gleich `n_personen`. `n_irgendeine_u60` ist mindestens so groß wie das Maximum der drei u60-Spalten und höchstens so groß wie ihre Summe. `DOAK_GESAMT` ist mindestens so groß wie jede einzelne DOAK-Zeile und höchstens so groß wie ihre Summe.

Bei den zwei Diskordanz-Spalten steht in SPEC.md kein „davon“. A liest sie wie die übrigen Spalten als Teilmenge von P(z). Das steht als Frage 8a in `OFFEN.md`.

### 2. Erste Spalte und Reihenfolge in `results/A/abend4_fallzahlen.csv`

- Kopf der ersten Spalte: `zeile`.
- Danach die acht Spalten in der Reihenfolge der Tabelle „Ausgabe“: `n_personen`, `n_ckdepi_u60`, `n_deindex_u60`, `n_cg_u60`, `n_irgendeine_u60`, `n_diskordant_cg_ckdepi`, `n_diskordant_cg_deindex`, `n_alter_80`.
- Zwölf Zeilen in dieser Reihenfolge: `METFORMIN`, `GABAPENTIN`, `PREGABALIN`, `DOAK_GESAMT`, `ALLOPURINOL`, `SITAGLIPTIN`, `SPIRONOLACTONE`, `APIXABAN`, `RIVAROXABAN`, `DABIGATRAN`, `EDOXABAN`, `GESAMT`. Zuerst die sieben Zeilen der Tabelle in SPEC.md, dann die vier DOAK in der Reihenfolge des Satzes „Zusätzlich gibt es je eine Zeile …“, zuletzt `GESAMT`.
- Format: Komma als Trenner, Kopfzeile, keine Anführungszeichen, keine Zeilennamen, Zeilenende LF, nur ASCII. Die Zahlen sind ganze Zahlen ohne Dezimalpunkt.

Die Spezifikation legt Spaltenkopf und Reihenfolge nicht fest. Diese Festlegung ist die von A, siehe Frage 5 in `OFFEN.md`.

### 3. Format von `data/work/abend4_personen_A.csv`

- Genau 15.560 Datenzeilen, eine je `SEQN` aus P\_DEMO, aufsteigend nach `SEQN` sortiert, dazu eine Kopfzeile. Das Skript bricht ab, wenn `SEQN` in P\_DEMO nicht eindeutig ist oder die Zeilenzahl nicht 15.560 beträgt.
- Spalten in dieser Reihenfolge: `SEQN`, `analysegruppe`, `METFORMIN`, `GABAPENTIN`, `PREGABALIN`, `DOAK_GESAMT`, `ALLOPURINOL`, `SITAGLIPTIN`, `SPIRONOLACTONE`, `APIXABAN`, `RIVAROXABAN`, `DABIGATRAN`, `EDOXABAN`, `kat_ckdepi`, `kat_deindex`, `kat_cg`. Eine Spalte `GESAMT` gibt es nicht.
- `SEQN`: ganze Zahl ohne Dezimalpunkt und ohne wissenschaftliche Schreibweise, z. B. `109263`.
- `analysegruppe`: `1` oder `0` für jede Person, nie leer.
- Elf Trefferspalten: `1` oder `0` für Personen der Analysegruppe, auch für Personen ohne Medikamentenzeile (dann `0`). Für Personen außerhalb der Analysegruppe ein leeres Feld. Geschrieben wird `1` oder `0`, nicht `1.0`, `TRUE` oder `NA`.
- `kat_ckdepi`, `kat_deindex`, `kat_cg`: `u30`, `30_45`, `45_60` oder `ab60` für Personen der Analysegruppe, ein leeres Feld für alle anderen.
- Leere Werte: nichts zwischen zwei Kommas, beziehungsweise nichts nach dem letzten Komma. Kein `NA`, keine Anführungszeichen, kein Leerzeichen.
- Format sonst wie oben: Komma, keine Anführungszeichen, keine Zeilennamen, LF, ASCII. Die Datei liegt laut SPEC.md nicht im Git.

Welche Zahlenformate B schreibt, legt die Spezifikation nicht fest, etwa `1.0` statt `1` oder `109263.0` statt `109263`. Ein Vergleich als Text würde das als Abweichung zählen. Das steht als Frage 8b in `OFFEN.md`.

## 2026-11-24 – Abend 4, Phase 1: Antworten von Justus, zweiter Versuch an den Originalen

### Antworten auf `OFFEN.md`

Justus hat die Fragen 5, 6, 7, 8a und 8b am 24.11.2026 beantwortet. Die Antworten stehen als Status in `OFFEN.md`. SPEC.md bleibt unverändert. Die Lesart von A aus dem vorigen Eintrag gilt damit unverändert, einschließlich der Diskordanz-Spalten (8a).

### Erreichbarkeit nach der Freigabe der Domains

Justus hat die vier zuvor gesperrten Domains freigegeben. Geprüft am 24.11.2026 zwischen 06:04 und 06:06 UTC mit `curl`:

| Host | Ergebnis |
| --- | --- |
| `doi.org` | erreichbar, leitet weiter (zu `karger.com` bzw. `archinte.jamanetwork.com`) |
| `karger.com` | Proxy lässt durch. Die Website antwortet mit HTTP 403, `server: cloudflare`, `cf-mitigated: challenge`, Seitentext „Just a moment… Enable JavaScript and cookies to continue“. Kein Artikel, kein PDF. |
| `jamanetwork.com` | Proxy lässt durch. Die Website antwortet mit HTTP 403, `cf-mitigated: challenge`, wie bei Karger. |
| `archinte.jamanetwork.com` | Ziel der DOI-Weiterleitung für DuBois. „Could not resolve host“. |
| `archive.org` | erreichbar (HTTP 200). Suche, Metadaten und die Textansicht `/stream/…` funktionieren. |
| `ia800100.us.archive.org` | Proxy sperrt (kein Verbindungsaufbau). Dort liegen die Dateien der Scans (PDF, Seitenbilder). Bilder der Seiten konnten deshalb nicht angesehen werden. |
| `zenodo.org` | Proxy sperrt (`CONNECT tunnel failed, response 403`). Die Adresse `https://zenodo.org/records/1423319` ist nicht erreichbar. |
| `scholar.archive.org`, `api.fatcat.wiki` | Proxy sperrt (kein Verbindungsaufbau). |

Die Cloudflare-Prüfung bei Karger und JAMA hat A nicht umgangen.

### DuBois: gegen das Original geprüft, stimmt mit SPEC.md überein

Quelle: Du Bois D, Du Bois EF. Clinical calorimetry. Tenth paper. A formula to estimate the approximate surface area if height and weight be known. Arch Intern Med 1916;17(6, Teil 2):863–871. Gelesen am 24.11.2026 als OCR-Text zweier unabhängiger Scans auf archive.org, Textansicht `https://archive.org/stream/<ID>/<ID>_djvu.txt`:

- Scan 1: `n062archivesofintern17ameruoft`, „Archives of internal medicine“, Band „17 n.06 pt.02“, Beitrag „Gerstein - University of Toronto“. SHA-256 der abgerufenen Seite `8008ee01a1d502d4537d2d06f4e36eba6cb4964c6661a2d1d5400b27a416a1f8`.
- Scan 2: `sim_jama-internal-medicine_1916-06-15_17_6`, „The Archives of Internal Medicine 1916-06-15: Vol 17 Iss 6“. SHA-256 der abgerufenen Seite `6b0c510b0e5c63380103642194d377406fc27e734bb966277b14ce2351692738`.

Kopf des Artikels in Scan 2, wörtlich: „CLINICAL CALORIMETRY / TENTH PAPER / A FORMULA TO ESTIMATE THE APPROXIMATE SURFACE AREA IF HEIGHT AND WEIGHT BE KNOWN* / DELAFIELD Dv BOIS, B.S. … AND EUGENE F. Dv BOIS, M.D.“ („Dv“ ist ein OCR-Fehler für „Du“.)

Seite 870 laut Seitenkopf („870 THE ARCHIVES OF INTERNAL MEDICINE“), Scan 1, wörtlich, einschließlich der OCR-Fehler:

> The best values of "a" and "b" were found to be a = 2.35 and b = 1.38 giving the formula the final form of A = 1'2-35 X H1/13S X C or A = W0-425 X H0T25 X 71.84. This formula can be solved by logarithms as follows : Log. A = Log. W X 0.425 + Log. H X 0.725 + 1.8564. 1.8564 is a constant equal to Log. C.

Dieselbe Logarithmus-Zeile in Scan 2: „Log. A= Log. W X 0.425 + Log. H &amp; 0.725 + 1.8564.“

Seite 871, „SUMMARY AND CONCLUSIONS“, Scan 1, wörtlich:

> This is expressed in the terms A = W0-*23 X H0-725 X C. A being the surface area in square centimeters, H the height in centimeters. W the weight in kilograms and C the constant, 71.84.

Scan 2, gleiche Stelle: „A being the surface area in square centimeters, H the height in centimeters, W the weight in kilo- grams and C the constant, 71.84.“

**Lesung:** In der direkten Schreibweise sind die Hochzahlen in beiden Scans von der OCR verstümmelt („W0-425“, „H0T25“, „W0-*23“). In beiden Scans eindeutig ist die Logarithmusform: log A = 0,425 · log W + 0,725 · log H + 1,8564. Sie bestätigt die Hochzahlen 0,425 und 0,725. Zwei weitere Angaben passen dazu: Die Exponenten folgen aus a = 2,35 und b = 1,38 (1/2,35 = 0,4255, 1/1,38 = 0,7246), und 1,8564 ist der Zehnerlogarithmus von 71,84 (log₁₀ 71,84 = 1,85637). Einheiten laut Original: A in cm², W in kg, H in cm.

| SPEC.md | Original | Urteil |
| --- | --- | --- |
| Gewicht^0,425 | W^0.425, W in Kilogramm | gleich |
| Größe^0,725 | H^0.725, H in Zentimetern | gleich |
| 0,007184, Ergebnis in m² | C = 71.84, A in Quadratzentimetern; 71,84 cm² = 0,007184 m² | gleich |

**Einschränkung:** Gelesen ist OCR-Text, nicht das Seitenbild. Die Bilder liegen auf `ia800100.us.archive.org`, und den sperrt der Proxy. Die Prüfung stützt sich auf die Übereinstimmung zweier unabhängiger Scans und auf die in sich stimmigen Angaben a, b und log C.

### Cockcroft-Gault: Original weiterhin nicht erreichbar

Versucht am 24.11.2026:

- `https://doi.org/10.1159/000180580` leitet weiter zu `https://karger.com/article/doi/10.1159/000180580` und endet dort in der Cloudflare-Prüfung (HTTP 403).
- `https://karger.com/nef/article/16/1/31/823303`: Cloudflare-Prüfung (HTTP 403).
- `https://karger.com/nef/article-pdf/16/1/31/3301838/000180580.pdf`: Cloudflare-Prüfung (HTTP 403).
- archive.org: Die Suche nach „nephron“ im Jahr 1976 und nach „cockcroft gault creatinine clearance“ findet keinen Scan des Originals, nur spätere PMC-Arbeiten, die die Formel zitieren. Diese sind Sekundärquellen und zählen nicht. Die Suche nach der DOI lieferte einen Fehler des Suchdienstes.
- `scholar.archive.org` und `api.fatcat.wiki`: vom Proxy gesperrt.
- PubMed Central: kein Volltext (PMID 1244564 ohne PMCID).

**Belegt bleibt nur das PubMed-Abstract** („…in adult males: (see article)(15% less in females)“). Der Aufbau (140 − Alter) · Gewicht / (72 · Kreatinin) ist nicht am Original geprüft.

### Folge

Nach der Vorgabe von Justus gilt: Bleibt ein Original unerreichbar, wird angehalten und nicht gezählt. Frage 4 in `OFFEN.md` bleibt offen. Phase 2 hat nicht begonnen. Kein Skript ist geändert, nichts ist gezählt.

## 2026-11-24 – Abend 4, Phase 1: DuBois am Seitenbild geprüft (Zenodo)

Justus hat `zenodo.org` freigegeben. Am 24.11.2026 um 06:07 UTC ist `zenodo.org` erreichbar (HTTP 200).

**Quelle:** Zenodo-Eintrag 1423319 (`https://zenodo.org/records/1423319`), laut API: Titel „Clinical Calorimetry: Tenth Paper a Formula to Estimate the Approximate Surface Area if Height and Weight Be Known“, Datum 1916-06-01, DOI 10.1001/archinte.1916.00080130010002, Lizenz `cc-zero`. Datei `article.pdf`, 1.017.854 Bytes, 9 Seiten. MD5 `dbdc38f50b63153c67dad5900cfa205c`, gleich der Prüfsumme in der API. SHA-256 `2ee8b596cf23ee09e3ace524700747e544444a991073274636cc90306f8a1ba9`. Die Fußzeile jeder Seite lautet „Downloaded From: http://archinte.jamanetwork.com/ by a University of Arizona Health Sciences Library User on 08/31/2013“. Es ist also der Scan des Verlags.

Die PDF-Seiten 8 und 9 (Heftseiten 870 und 871) hat A mit `pdftoppm` als Bild gerendert und vom Bild abgelesen.

Seite 870, wörtlich nach dem Seitenbild (Hochzahlen mit ^):

> The best values of "a" and "b" were found to be a = 2.35 and b = 1.38 giving the formula the final form of A = W^1/2.35 × H^1/1.38 × C or A = W^0.425 × H^0.725 × 71.84. This formula can be solved by logarithms as follows:
> Log. A = Log. W × 0.425 + Log. H × 0.725 + 1.8564.
> 1.8564 is a constant equal to Log. C.

Seite 871, „Summary and Conclusions“, wörtlich nach dem Seitenbild:

> This is expressed in the terms A = W^0.425 × H^0.725 × C. A being the surface area in square centimeters, H the height in centimeters, W the weight in kilograms and C the constant, 71.84.

Das Seitenbild bestätigt die Lesung aus dem vorigen Eintrag. Die Einschränkung „nur OCR-Text, nicht das Seitenbild“ ist damit erledigt. **Ergebnis unverändert: Die DuBois-Formel in SPEC.md stimmt mit dem Original überein** (W^0,425 · H^0,725 · 71,84 cm² = 0,007184 · W^0,425 · H^0,725 m², W in kg, H in cm).

**Cockcroft-Gault:** Der Zenodo-Eintrag enthält nur die Arbeit von DuBois. Das Original von Cockcroft und Gault bleibt unerreichbar (siehe voriger Eintrag). Frage 4 bleibt offen. Nichts gezählt.
