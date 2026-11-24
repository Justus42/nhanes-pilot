# NHANES-Pilot: Kurznotiz zur Arbeitsweise

Stand: 24.11.2026. Geschrieben vom Orchestrator (Claude) im Auftrag von Justus Jeserigk, nach Abschluss des Pilots. Kein Zeitschriftenartikel, kein Forschungsergebnis. Die Notiz hält fest, wie gearbeitet wurde, welche Fehler auftraten und welche Absicherung sie bemerkt hat.

**Belegregel dieser Notiz.** Jede Angabe ist gegen eine Datei dieses Repos geprüft, sofern nichts anderes dasteht. Die Zahlen in Abschnitt 1 sind mit einem eigenen kleinen Skript aus den CSV-Dateien unter `results/` nachgezählt und stimmen mit `LOG.md` überein. Angaben mit dem Zusatz **(nicht im Repo)** stammen aus Arbeitsnotizen außerhalb des Repos und lassen sich hier nicht nachprüfen. An `SPEC.md`, `LOG.md`, den Skripten und den Ergebnissen ändert diese Notiz nichts.

## 1. Was der Pilot war

Ein Arzt ohne Programmierkenntnisse wollte wissen, ob eine überwiegend von Sprachmodellen geschriebene Auswertung öffentlicher Surveydaten (NHANES 2017–März 2020) vertrauenswürdig ist. Der Pilot lief in vier Schritten („Abenden“) vom 23. auf den 24.11.2026. Er sollte kein Ergebnis liefern, sondern die Arbeitsweise prüfen und eine Machbarkeitsfrage entscheiden.

| Abend | Aufgabe | Ergebnis |
| --- | --- | --- |
| 1 | Vier Dateien der CDC laden, Zeilenzahlen prüfen | bestanden, alle vier Zeilenzahlen stimmen |
| 2 | Positivkontrolle: veröffentlichte Adipositas-Kennzahlen der CDC nachrechnen (Report Nr. 158) | 29 von 29 extern geprüften Zellen innerhalb der vorab festgelegten Toleranz; größte Abweichung 0,049 Prozentpunkte |
| 3 | Zweitauswertung derselben Kennzahlen durch ein anderes Modell in einer anderen Sprache | B trifft 17 von 17 extern geprüften Zellen; A gegen B 27 von 27, größte Differenz 7,1 · 10⁻¹⁵ Prozentpunkte |
| 4 | Fallzahlen je Wirkstoff und Nierenfunktionskategorie zählen | 96 von 96 Zellen bei A und B gleich; null Abweichungen Person für Person in 16 Spalten bei 15.560 Personen |

Die Entscheidungsregel stand vor dem Zählen fest. Sie ergab, dass genug Fälle für das geplante Projekt vorhanden wären. Das Projekt selbst wurde danach aus anderen Gründen nicht begonnen (Abschlussvermerk in `LOG.md`).

## 2. Wer was getan hat

- **Justus Jeserigk:** entscheidet, gibt frei, mergt. Überträgt Aufträge und Skripte von Hand zwischen den Beteiligten.
- **Orchestrator** (Claude, Chat): entwirft mit Justus Spezifikation und Aufträge, prüft Ergebnisse und Pull Requests, wertet nicht selbst aus. Dass Claude die Spezifikation entworfen hat, steht so nicht im Repo; belegt ist dort, dass Claude die Erwartungswerte der Rechentests berechnet und Quellen als Prüfer nachgeschlagen hat (`LOG.md`).
- **Auswerter A** (Claude Code, R mit dem Paket `survey`): rechnet nach `SPEC.md`.
- **Auswerter B** (Gemini 4 Neon, Python ohne Survey-Bibliothek): bekommt nur `SPEC.md`, schreibt ein Skript, das unverändert abgelegt und ausgeführt wird.
- **Vergleichssitzung** (Claude Code, jeweils eine neue Sitzung, nie die von A): führt das Skript von B aus und vergleicht.
- **Gutachter der Spezifikation:** GPT 6.2 Astra (Version 1) und Gemini 4 Neon (Version 2), Antworten unverändert unter `review/`.

Alle Beteiligten außer Justus sind Sprachmodelle. Drei der Rollen besetzt dieselbe Modellfamilie.

## 3. Die Absicherungen

| Kürzel | Absicherung | Wo im Repo |
| --- | --- | --- |
| S1 | Spezifikation vor dem ersten Datenzugriff, mit festem Kern: Toleranzen, Abbruchkriterium, Entscheidungsregel und Zielwerte sind danach unveränderlich | `SPEC.md`, Abschnitt „Änderungen an dieser Spezifikation“ |
| S2 | Review der Spezifikation durch zwei andere Modelle, vor dem ersten Datenzugriff | `review/` |
| S3 | Quellenprüfung vor dem Rechnen: Zielwerte, Konstanten und Formeln werden an der Primärquelle nachgelesen, mit wörtlichem Zitat | `LOG.md` |
| S4 | Rechenprobe an veröffentlichten Beispielen, bevor die eigenen Daten gerechnet werden | `A/02_ki_formel_pruefung.R` |
| S5 | Positivkontrolle an einer veröffentlichten Kennzahl; die Zielwerte stehen nur im Vergleichsskript, nicht im Rechenskript | `A/03_…`, `A/04_…` |
| S6 | Zweitauswertung durch ein anderes Modell in anderer Sprache, das nur die Spezifikation kennt | `B/` |
| S7 | Vergleich in einer neuen Sitzung, mit Gegenprobe: Erkennt der Vergleich absichtlich eingebaute Abweichungen? | `vergleich.py`, `LOG.md` |
| S8 | Anhalten statt raten: Unklarheiten gehen als Frage an den Menschen | `OFFEN.md` |
| S9 | Protokollpflicht: jede Skriptänderung nach dem ersten Lauf steht im Protokoll; Fehler im Protokoll werden als Nachtrag berichtigt, nicht überschrieben | `LOG.md` |
| S10 | Rechentests der Formeln mit festen Erwartungswerten vor dem Zählen | `A/06_rechentests.R` |

## 4. Fehlerprotokoll: Was falsch war und was es bemerkt hat

„Vor Daten“ heißt: bevor ein Auswerter Daten oder Ergebnisse gesehen hatte.

| Nr. | Was falsch oder unklar war | Entstanden bei | Bemerkt durch | Zeitpunkt | Folge für das Ergebnis |
| --- | --- | --- | --- | --- | --- |
| 1 | Spezifikation Version 1: 4 Fehler und 14 Unklarheiten. Beispiel: Der Ausschluss „`RIDEXPRG` ungleich 1“ hätte in R auch alle Personen mit fehlender Angabe entfernt, darunter die Männer, in Python nicht. Weiteres Beispiel: Die Behauptung, ein gemeinsamer Denkfehler von A und B sei unwahrscheinlich. | Spezifikation | S2, Review durch Astra | vor Daten | keine, Version 2 |
| 2 | Spezifikation Version 2: 3 Fehler und 2 Unklarheiten. Drei der fünf Befunde betrafen Text, der erst durch die Korrekturen aus Nr. 1 entstanden war. Beispiel: Erwartungswerte der Rechentests waren gerundet, eine Toleranz fehlte; richtige Programme wären abgebrochen. | Spezifikation, beim Einarbeiten von Nr. 1 | S2, Review durch Neon | vor Daten | keine |
| 3 | Aus demselben Review: Die Rechentests prüften zu wenig. Kein Fall traf den geschlechtsabhängigen Exponenten, und der Test der Umrechnung lag genau bei 1,73 m², wo ein umgedrehter Faktor nicht auffällt. | Spezifikation; die Erwartungswerte hatte Claude berechnet | S2, Review durch Neon | vor Daten | keine, drei Fälle ergänzt |
| 4 | Der erste Gutachter schlug Altersanteile mit vier Nachkommastellen vor, ausdrücklich aus dem Gedächtnis. Die Quelle nennt sechs. | Gutachter Astra, übernommen in Version 2 | S3, Quellenprüfung durch A; dann S8 | vor Daten | keine bekannte. Version 2.1 nimmt die sechs Stellen; wie viel die Rundung ausgemacht hätte, ist nicht nachgerechnet. |
| 5 | Die Spezifikation ließ offen, zu welcher Schätzung zwei Standardfehler gehören. Die Quelle ordnet sie der altersadjustierten Schätzung zu. | Spezifikation | S3, dann S8 | vor Daten | keine; die Zuordnung hätte das Urteil nicht geändert (`LOG.md`, Abend 2) |
| 6 | Der erste Gutachter meldete als „sicher“, aber nach eigener Angabe ungetestet, die R-Funktion `svyciprop` setze die Freiheitsgrad-Korrektur nicht um. Laut A wendet die verwendete Paketversion den Faktor an; ihr fehlt nur die Kappung bei n, die hier nicht griff. Funktion und ausgeschriebene Formel unterschieden sich um 7,1 · 10⁻¹⁵ Prozentpunkte. | Gutachter Astra, aus dem Gedächtnis | Kennzeichnung „nicht geprüft“ im Protokoll, dann Gegenrechnung durch A | bei Abend 2 | keine. Die Korrektur (Formel ausschreiben) war trotzdem richtig. |
| 7 | Die Formel des Konfidenzintervalls stand aus dem Gedächtnis in der Spezifikation. Der Text der NCHS-Standards schreibt zwei ihrer Teile nicht aus. | Spezifikation, nach Vorschlag des Gutachters | S4: Von drei möglichen Lesarten trifft nur die der Spezifikation alle 16 veröffentlichten Beispiele im Rahmen ihrer Rundung | vor dem Rechnen | keine |
| 8 | Abschreibfehler in einem vorläufigen Prüfskript: obere Intervallgrenze 42,1 statt des Prozentwerts 34,9 eingetragen. | Auswerter A | S4: Diese eine Zeile lag 7,26 Prozentpunkte daneben, die anderen höchstens 0,08. Korrigiert allein anhand der Quelle. | vor dem Rechnen | keine; der Fehler stand nie in einer committeten Datei |
| 9 | Widerspruch in der Quelle selbst: Eine Fußnote der NCHS-Standards beschreibt für eine Beispielzeile eine andere Rechnung, als die veröffentlichten Grenzen ergeben. | Quelle | S4 | vor dem Rechnen | keine; zeigt, dass Lesen allein nicht gereicht hätte |
| 10 | Protokoll sagte „ohne Änderung nach dem ersten Lauf“. Tatsächlich war ein Skript nach dem ersten Lauf an drei Stellen geändert worden. | Auswerter A | S9, Nachtrag mit Rekonstruktion: Ausgabe Byte für Byte gleich. Wer den Fehler bemerkt hat, ist im Repo nicht festgehalten. | nach Abend 2 | keine |
| 11 | Protokoll sagte, es seien noch keine Daten geladen. Eine Datei war schon zum Erreichbarkeitstest abgerufen. | Protokolleintrag zu Version 2.1, Verfasser im Repo nicht genannt | S9, Nachtrag. Auslöser im Repo nicht festgehalten. | vor Abend 2 | keine |
| 12 | Die Formeln von Abend 4 standen aus dem Gedächtnis in der Spezifikation (Claude und der erste Gutachter nannten sie übereinstimmend). | Spezifikation | S3: CKD-EPI 2021 und DuBois am Original bestätigt. Cockcroft-Gault war nicht erreichbar; A hielt an (S8), Justus entschied, mit dokumentierter Lücke zu zählen. | vor dem Zählen | Lücke bleibt offen, siehe Abschnitt 5 |
| 13 | Die Personendateien von A und B waren Byte für Byte gleich. „Null Abweichungen“ beweist dann nicht, dass der Vergleich Abweichungen findet. | – | S7, Gegenprobe: drei eingebaute Abweichungen genau gefunden, Formatunterschiede richtig ignoriert, ungültige Werte führen zum Abbruch | nach dem Zählen | keine |
| 14 | Ein Lese-Argument im Zählskript hätte eine zusätzliche Spalte erzeugt. | Auswerter A | A selbst, vor dem ersten Lauf | vor dem Zählen | keine |
| 15 | Ein Protokollentwurf für die Hauptanalyse behauptete, die Daten enthielten keine Angabe zur Indikation. Die gesicherte CDC-Seite nennt sechs solche Variablen. | Entwurf außerhalb des Repos, Verfasser dort nicht genannt | Abgleich mit der gesicherten CDC-Seite in `docs/cdc/` | nach dem Pilot | keine, der Entwurf wurde nie verwendet |
| 16 | Eine Arbeitsnotiz nannte eine „veröffentlichte Replik“ auf eine Vorarbeit. Die Literatursuche fand sie nicht. **(nicht im Repo)** | Orchestrator, ohne Beleg | spätere Literatursuche | nach dem Pilot | keine |

Was die Liste zeigt:

- **Die meisten Fehler entstanden beim Schreiben der Spezifikation und wurden bemerkt, bevor Daten im Spiel waren.** Die ergiebigsten Absicherungen waren das Review durch andere Modelle (S2) und das Nachlesen an der Primärquelle (S3, S4).
- **Angaben aus dem Gedächtnis eines Modells waren eine wiederkehrende Fehlerquelle** (Nr. 4, 6, 7, 12), auch beim Gutachter und auch dann, wenn zwei Modelle übereinstimmten.
- **Korrekturen erzeugen neue Fehler** (Nr. 2). Ein zweites Review nach der Korrektur war nötig.
- **Der Vergleich A gegen B (S6) hat keinen einzigen Fehler gefunden.** A und B stimmten von Anfang an überein. Das kann heißen, dass die Spezifikation nach zwei Reviews eindeutig genug war. Es heißt nicht, dass sie richtig war.
- **Das Protokoll enthielt zweimal eine falsche Angabe über den eigenen Ablauf** (Nr. 10, 11). Beide sind als Nachtrag berichtigt. Die Selbstauskunft eines Auswerters über seinen Ablauf ist kein Beleg.

## 5. Was keine Absicherung bemerkt hat

- **Die zwei Rechentests für Cockcroft-Gault rechnen beide mit Kreatinin 1,0** (`LOG.md`, Abend 4, Tabelle der Rechentests). Bei diesem Wert ist es gleich, ob das Kreatinin im Nenner oder im Zähler steht. Die Tests hätten genau den Fehler nicht erkannt, der bei dieser Formel naheliegt. Zwei Reviews und beide Auswerter haben das übersehen; aufgefallen ist es dem Orchestrator erst nach dem Pilot **(nicht im Repo)**. Dass der Fehler in der Praxis vorkommt, zeigt das R-Paket `nephro`: Laut dessen `NEWS.md` rechnete die Funktion `CG()` bis zur Korrektur in Version 1.2 (2017) mit `(140-age) * wt / 72 * creatinine` statt mit `(140-age) * wt / (72 * creatinine)` (github.com/cran/nephro, gelesen am 24.11.2026).
- **Cockcroft-Gault ist nicht am Volltext der Originalarbeit geprüft.** Der Verlag war aus der Arbeitsumgebung nicht erreichbar. Belegt ist nur, was das Abstract hergibt (`OFFEN.md`, Frage 4).
- **Die Erwartungswerte der Rechentests stammen aus den Formeln der Spezifikation.** Die Tests zeigen, dass der Code die Spezifikation umsetzt. Ob die Spezifikation stimmt, zeigen sie nicht.
- **Was vor einem Commit in einer Sitzung geschah, ist nicht belegbar.** Bekannt ist nur, was der Auswerter selbst ins Protokoll schrieb.

## 6. Vorlage für ein nächstes Projekt

Die Reihenfolge ist der Kern. Was davon in diesem Repo als Muster dienen kann, steht in Klammern.

1. **Spezifikation zuerst,** mit festem Kern und einem geregelten Weg für spätere Klarstellungen (`SPEC.md`, Abschnitte „Zweck und Abbruchkriterium“, „Entscheidungsregel“, „Änderungen an dieser Spezifikation“).
2. **Offene und ungeprüfte Punkte in der Spezifikation selbst benennen,** besonders alles, was aus dem Gedächtnis eines Modells stammt (`SPEC.md`, „Offene und ungeprüfte Punkte“).
3. **Zwei Reviews durch andere Modelle vor dem ersten Datenzugriff,** das zweite nach dem Einarbeiten des ersten. Antworten unverändert ablegen (`review/`).
4. **Quellenprüfung als eigener Schritt vor dem Rechnen,** mit wörtlichen Zitaten und Prüfsummen der gelesenen Dokumente, als eigener Commit (`LOG.md`, „Zusatzaufgabe vor Abend 2“).
5. **Rechenprobe an veröffentlichten Beispielen,** wenn es welche gibt (`A/02_ki_formel_pruefung.R`).
6. **Positivkontrolle vor der eigentlichen Frage.** Zielwerte nur im Vergleichsskript (`A/03_positivkontrolle.R`, `A/04_zielvergleich.R`).
7. **Zweitauswerter bekommt nur die Spezifikation.** Sein Skript wird unverändert und vor dem ersten Lauf committet (`SPEC.md`, „Regeln für beide Auswerter“ und „Startaufträge zum Kopieren“).
8. **Vergleich in einer neuen Sitzung,** die Zielwerte und Toleranzen aus der Spezifikation liest statt sie abzutippen, mit Gegenprobe durch eingebaute Fehler (`vergleich.py`).
9. **Bei Zählaufgaben zwei Phasen:** erst die Lesart der Ausgabe schriftlich festlegen und Fragen stellen, dann zählen (`LOG.md`, „Abend 4, Phase 1, Zusatz“).
10. **Anhalten statt raten** (`OFFEN.md`), und **Nachträge statt Überschreiben** (`LOG.md`).
11. **Rohdaten nicht ins Git, ihre Prüfsummen schon.** Das Ladeskript prüft sie bei jedem Lauf (`A/01_download.R`).
12. **Ein Branch je Schritt, Pull Request, Merge durch den Menschen, keine umgeschriebene Historie.**

Aus Abschnitt 5 folgt eine Ergänzung, die im Pilot fehlte: **Rechentests so wählen, dass jeder Eingabewert das Ergebnis verändert,** und die Erwartungswerte nicht aus der Spezifikation, sondern unabhängig aus der Originalquelle herleiten.

## 7. Aufwand

Aus dem Repo belegt:

- Erster Commit am 23.11.2026 um 21:26 Uhr, Merge des letzten Pilot-Schritts (Pull Request 7) am 24.11.2026 um 08:09 Uhr, jeweils mitteleuropäische Zeit. Dazwischen liegt eine Nacht; die Spanne ist keine Arbeitszeit.
- 32 Commits und 7 gemergte Pull Requests bis dahin.
- Ein Review über eine bezahlte Schnittstelle kostete laut Kopf der Antwortdatei 0,52 US-$ (`review/openrouter/spec-v1-astra.md`). Die übrigen Modellkosten sind nicht erfasst.

Aus den Arbeitsnotizen **(nicht im Repo)**, aus Git- und Chat-Zeitstempeln geschätzt:

- Zeit von Justus für den Pilot bis zum letzten Merge: mindestens 4 h 16 min, höchstens 5 h 34 min. Die Spanne entsteht, weil Lücken über 45 Minuten einmal als Pause und einmal als Arbeit zählen. Die Arbeitsnotiz nennt als Ende 08:21 Uhr, der Merge im Repo trägt 08:09 Uhr; woher die Differenz kommt, ist nicht geklärt.
- Die Schätzung misst verstrichene Zeit. Kurze Wartezeiten zählen voll mit, obwohl währenddessen anderes getan wurde. Sie überschätzt die aktive Zeit; wie stark, ist nicht gemessen.
- Nicht enthalten ist die Zeit vor dem ersten Commit (Themenwahl, erste Fassung der Spezifikation).
- 15 Nachrichten von Justus an den Orchestrator in dieser Zeit.

Jede Übergabe an den Zweitauswerter lief von Hand über Justus. Das war der Engpass im Ablauf.

## 8. Grenzen

- **Ein einzelner Durchlauf mit einer einfachen Aufgabe.** Eine gewichtete Prävalenz und eine Zählung sind eine niedrige Hürde.
- **Übereinstimmung von A und B belegt Treue zur Spezifikation, nicht Richtigkeit.** Gemeinsame Fehler an mehrdeutigen Stellen sind zu erwarten (`SPEC.md`, Definition 6).
- **Die Zielwerte der Positivkontrolle sind veröffentlicht** und stehen vermutlich in den Trainingsdaten der Modelle. Die Zielwerte standen aber nicht im Rechenskript, und B kannte sie nur aus der Spezifikation.
- **Kein Vergleich mit einem einzelnen Modell ohne Absicherungen.** Welche Absicherung nötig war und welche nur Aufwand, zeigt der Pilot nicht. Abschnitt 4 gibt dazu Hinweise, keinen Beleg.
- **Geprüft wurden Rechen- und Lesefehler, nicht inhaltliche Gültigkeit.** Ob eine Fragestellung sinnvoll oder eine Definition klinisch richtig ist, hat niemand außer Justus geprüft.
- **Der Prüfer war ein Sprachmodell derselben Familie wie Auswerter A.** Fehler in Texten, an denen Claude mitgeschrieben hat (Spezifikation, Arbeitsnotiz), wurden nur bemerkt, wo ein anderes Modell, eine Quelle oder eine Datei dagegenstand.
- **Nicht nachgeprüft** sind die Prüfsummen der Rohdateien und der Vergleich Person für Person: Beide Dateiarten liegen nicht im Git. Belegt sind sie nur durch die Protokolleinträge der Sitzungen.
