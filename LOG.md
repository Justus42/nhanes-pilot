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

**Weitere Änderungen ohne Bezug zum Review:**

- Das Wort „lokal“ ist gestrichen. Die Arbeitsumgebung (Cloud-Sitzung oder PC) ist offen und wird vor Abend 1 hier eingetragen.
- Auswerter B heißt „ein Gemini-Modell“. Modell und Weg sind offen.
- Die Erwartungswerte der Rechentests hat Claude aus den Formeln der Spezifikation berechnet.
- `.gitignore` schließt zusätzlich `data/work/` aus.

**Bewertung der Befunde durch Claude:** Befund 2 behauptet, die R-Funktion setze die NCHS-Regel nicht genau um. Das ist nicht geprüft. Die Änderung ist davon unabhängig richtig, weil die Formel jetzt ausgeschrieben ist.
