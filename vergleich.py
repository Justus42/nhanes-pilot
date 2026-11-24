#!/usr/bin/env python3
"""
vergleich.py – Abend 3: A, B und Zielwert nebeneinander (SPEC.md, Abschnitt „Abend 3“).

Aufruf aus dem Wurzelverzeichnis des Repos:  python3 vergleich.py

Eingaben (werden nur gelesen, nie verändert):
  SPEC.md                                   Zielwerte und Toleranzen
  results/A/abend2_positivkontrolle.csv     Auswerter A (R, survey)
  results/B/abend2_positivkontrolle.csv     Auswerter B (Python, von Hand)
Ausgabe:
  results/vergleich_abend2.csv

Regeln:
- Verglichen werden die Zeilen, die B rechnet: Stufen 1, 2 und 4 (27 Zeilen).
  Stufe 3 (Konfidenzintervalle) rechnet nur A; ihr Urteil steht in der Datei von A.
- Zielwerte und Toleranzen werden aus SPEC.md gelesen, nicht abgetippt.
  Gegenprobe: Die Spalte „zielwert“ in der Datei von A muss dieselben Ziele enthalten.
- Abweichung = erster Wert minus zweiter Wert, ungerundet, in Prozentpunkten.
  „bestanden“ heißt |Abweichung| <= Toleranz (SPEC.md, Definition 5).
  Fallzahlen werden als ganze Zahlen exakt verglichen.
- Wie A/04_zielvergleich.R wird |Abweichung| vor dem Vergleich auf 10 Nachkommastellen
  gerundet, damit Gleitkommareste nicht zählen. Das Skript prüft zusätzlich, dass das
  Urteil ohne diese Rundung gleich ausfällt. Sonst bricht es ab (Grenzfall, nicht raten).
- Ohne Zielwert lautet das Urteil gegen das Ziel „extern nicht geprüft“.
  A gegen B wird in jeder Zeile geprüft.
- Jede Zeile muss über die Zuordnungstabelle unten genau einer Zeile in A und genau
  einer Zeile in B entsprechen. Sonst bricht das Skript ab.

Abend 4 (SPEC.md, Abschnitt „Abend 4“, OFFEN.md Fragen 5 und 8b), danach im selben Lauf:
  results/A/abend4_fallzahlen.csv, results/B/abend4_fallzahlen.csv
  data/work/abend4_personen_A.csv, data/work/abend4_personen_B.csv (nicht im Git)
Ausgabe:
  results/vergleich_abend4.csv  (nur die Zahl der Abweichungen je Spalte der Personendateien)
- Fallzahlen: Zeilen über die 12 Zeilennamen, Spalten über die 8 Spaltennamen aus SPEC.md.
  Jede der 96 Zellen wird exakt als ganze Zahl verglichen. Das Ergebnis steht nur auf der
  Konsole. Abbruch, wenn eine Zeile oder Spalte fehlt, doppelt oder unbekannt ist.
- Personen: beide Dateien müssen dieselben 15.560 SEQN enthalten. SEQN, analysegruppe und
  die Trefferspalten als ganze Zahlen (1 gleich 1.0), Kategorien als Text, leer gegen
  gefüllt ist eine Abweichung. Abbruch bei jedem anderen Wert.
  Einzelne SEQN werden weder ausgegeben noch geschrieben.

Nur Python-Standardbibliothek.
"""

import csv
import hashlib
import re
import sys
from pathlib import Path

SPEC = Path("SPEC.md")
DATEI_A = Path("results/A/abend2_positivkontrolle.csv")
DATEI_B = Path("results/B/abend2_positivkontrolle.csv")
AUSGABE = Path("results/vergleich_abend2.csv")

BESTANDEN = "bestanden"
NICHT_BESTANDEN = "nicht bestanden"
NICHT_GEPRUEFT = "extern nicht geprüft"

# ---------------------------------------------------------------------------
# Zuordnungstabelle B -> A
# Links die Bezeichnung in der Datei von A (kennzahl | gruppe | art | groesse),
# rechts die Bezeichnung in der Datei von B (kennzahl | gruppe | methode | groesse | einheit).
# Unterschiede in der Benennung: A „art“ = "" / "roh" / "adjustiert",
# B „methode“ = "ungewichtet" / "roh" / "altersadjustiert". B nennt zusätzlich die Einheit.
# ---------------------------------------------------------------------------
ZUORDNUNG_TEXT = """
zeile | stufe | A_kennzahl         | A_gruppe | A_art      | A_groesse      | B_kennzahl         | B_gruppe | B_methode        | B_groesse      | B_einheit
 1    | 1     | Analysegruppe      | Gesamt   |            | Fallzahl       | Analysegruppe      | Gesamt   | ungewichtet      | Fallzahl       | Personen
 2    | 1     | Analysegruppe      | Männer   |            | Fallzahl       | Analysegruppe      | Männer   | ungewichtet      | Fallzahl       | Personen
 3    | 1     | Analysegruppe      | Frauen   |            | Fallzahl       | Analysegruppe      | Frauen   | ungewichtet      | Fallzahl       | Personen
 4    | 2     | Adipositas         | Gesamt   | roh        | Praevalenz     | Adipositas         | Gesamt   | roh              | Praevalenz     | Prozent
 5    | 2     | Adipositas         | Gesamt   | roh        | Standardfehler | Adipositas         | Gesamt   | roh              | Standardfehler | Prozentpunkte
 6    | 2     | Adipositas         | Männer   | roh        | Praevalenz     | Adipositas         | Männer   | roh              | Praevalenz     | Prozent
 7    | 2     | Adipositas         | Männer   | roh        | Standardfehler | Adipositas         | Männer   | roh              | Standardfehler | Prozentpunkte
 8    | 2     | Adipositas         | Frauen   | roh        | Praevalenz     | Adipositas         | Frauen   | roh              | Praevalenz     | Prozent
 9    | 2     | Adipositas         | Frauen   | roh        | Standardfehler | Adipositas         | Frauen   | roh              | Standardfehler | Prozentpunkte
10    | 2     | Schwere Adipositas | Gesamt   | roh        | Praevalenz     | Schwere Adipositas | Gesamt   | roh              | Praevalenz     | Prozent
11    | 2     | Schwere Adipositas | Gesamt   | roh        | Standardfehler | Schwere Adipositas | Gesamt   | roh              | Standardfehler | Prozentpunkte
12    | 2     | Schwere Adipositas | Männer   | roh        | Praevalenz     | Schwere Adipositas | Männer   | roh              | Praevalenz     | Prozent
13    | 2     | Schwere Adipositas | Männer   | roh        | Standardfehler | Schwere Adipositas | Männer   | roh              | Standardfehler | Prozentpunkte
14    | 2     | Schwere Adipositas | Frauen   | roh        | Praevalenz     | Schwere Adipositas | Frauen   | roh              | Praevalenz     | Prozent
15    | 2     | Schwere Adipositas | Frauen   | roh        | Standardfehler | Schwere Adipositas | Frauen   | roh              | Standardfehler | Prozentpunkte
16    | 4     | Adipositas         | Gesamt   | adjustiert | Praevalenz     | Adipositas         | Gesamt   | altersadjustiert | Praevalenz     | Prozent
17    | 4     | Adipositas         | Gesamt   | adjustiert | Standardfehler | Adipositas         | Gesamt   | altersadjustiert | Standardfehler | Prozentpunkte
18    | 4     | Adipositas         | Männer   | adjustiert | Praevalenz     | Adipositas         | Männer   | altersadjustiert | Praevalenz     | Prozent
19    | 4     | Adipositas         | Männer   | adjustiert | Standardfehler | Adipositas         | Männer   | altersadjustiert | Standardfehler | Prozentpunkte
20    | 4     | Adipositas         | Frauen   | adjustiert | Praevalenz     | Adipositas         | Frauen   | altersadjustiert | Praevalenz     | Prozent
21    | 4     | Adipositas         | Frauen   | adjustiert | Standardfehler | Adipositas         | Frauen   | altersadjustiert | Standardfehler | Prozentpunkte
22    | 4     | Schwere Adipositas | Gesamt   | adjustiert | Praevalenz     | Schwere Adipositas | Gesamt   | altersadjustiert | Praevalenz     | Prozent
23    | 4     | Schwere Adipositas | Gesamt   | adjustiert | Standardfehler | Schwere Adipositas | Gesamt   | altersadjustiert | Standardfehler | Prozentpunkte
24    | 4     | Schwere Adipositas | Männer   | adjustiert | Praevalenz     | Schwere Adipositas | Männer   | altersadjustiert | Praevalenz     | Prozent
25    | 4     | Schwere Adipositas | Männer   | adjustiert | Standardfehler | Schwere Adipositas | Männer   | altersadjustiert | Standardfehler | Prozentpunkte
26    | 4     | Schwere Adipositas | Frauen   | adjustiert | Praevalenz     | Schwere Adipositas | Frauen   | altersadjustiert | Praevalenz     | Prozent
27    | 4     | Schwere Adipositas | Frauen   | adjustiert | Standardfehler | Schwere Adipositas | Frauen   | altersadjustiert | Standardfehler | Prozentpunkte
"""


class Abbruch(Exception):
    pass


def sha256(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def zahl_de(text: str) -> float:
    """Deutsche Dezimalzahl aus SPEC.md, z. B. '41,9' -> 41.9."""
    if not re.fullmatch(r"\d+(,\d+)?", text):
        raise Abbruch(f"Keine Dezimalzahl in SPEC.md: {text!r}")
    return float(text.replace(",", "."))


def zuordnung_lesen() -> list[dict]:
    zeilen = [z for z in ZUORDNUNG_TEXT.strip().splitlines()]
    kopf = [s.strip() for s in zeilen[0].split("|")]
    tabelle = []
    for z in zeilen[1:]:
        felder = [s.strip() for s in z.split("|")]
        if len(felder) != len(kopf):
            raise Abbruch(f"Zuordnungstabelle: falsche Spaltenzahl in Zeile {z!r}")
        tabelle.append(dict(zip(kopf, felder)))
    for schluessel in (("A_kennzahl", "A_gruppe", "A_art", "A_groesse"),
                       ("B_kennzahl", "B_gruppe", "B_methode", "B_groesse")):
        werte = [tuple(t[k] for k in schluessel) for t in tabelle]
        if len(set(werte)) != len(werte):
            raise Abbruch(f"Zuordnungstabelle: doppelte Bezeichnung in {schluessel}")
    return tabelle


# ---------------------------------------------------------------------------
# Zielwerte und Toleranzen aus SPEC.md
# ---------------------------------------------------------------------------
def abschnitt(text: str, anfang: str, ende: str) -> str:
    i = text.find(anfang)
    if i < 0 or text.find(anfang, i + 1) >= 0:
        raise Abbruch(f"SPEC.md: Abschnitt {anfang!r} nicht genau einmal gefunden.")
    j = text.find(ende, i + len(anfang))
    if j < 0:
        raise Abbruch(f"SPEC.md: Ende {ende!r} nach {anfang!r} nicht gefunden.")
    return text[i:j]


def toleranzen_lesen(teil: str, erwartet: dict[str, str]) -> dict[str, float]:
    """Liest eine Tabelle '| Größe | Erlaubte Abweichung |' und gibt {groesse: toleranz}."""
    tol: dict[str, float] = {}
    for zeile in teil.splitlines():
        m = re.fullmatch(r"\| (.+?) \| (.+?) \|", zeile.strip())
        if not m or m.group(1) in ("Größe", "---"):
            continue
        name, wert = m.group(1), m.group(2)
        if name not in erwartet:
            continue  # z. B. Grenzen des Konfidenzintervalls: an Abend 3 nicht verglichen
        if wert == "keine":
            t = 0.0
        else:
            mw = re.fullmatch(r"([\d,]+) Prozentpunkte", wert)
            if not mw:
                raise Abbruch(f"SPEC.md: Toleranz nicht lesbar: {zeile!r}")
            t = zahl_de(mw.group(1))
        if erwartet[name] in tol:
            raise Abbruch(f"SPEC.md: Toleranz für {name} doppelt.")
        tol[erwartet[name]] = t
    if set(tol) != set(erwartet.values()):
        raise Abbruch(f"SPEC.md: Toleranzen unvollständig: {tol}")
    return tol


def spec_lesen() -> tuple[dict, dict, dict]:
    text = SPEC.read_text(encoding="utf-8")
    abend2 = abschnitt(text, "## Abend 2 – Positivkontrolle", "## Abend 3")
    abend3 = abschnitt(text, "## Abend 3 – Zweitauswertung durch Gemini", "## Abend 4")

    ziele: dict[tuple, float] = {}

    # Stufe 1: Fallzahlen
    m = re.findall(r"Erwartet werden ([\d.]+) Personen, davon ([\d.]+) Männer und ([\d.]+) Frauen\.",
                   abend2)
    if len(m) != 1:
        raise Abbruch("SPEC.md: Satz mit den erwarteten Fallzahlen nicht genau einmal gefunden.")
    for gruppe, wert in zip(("Gesamt", "Männer", "Frauen"), m[0]):
        if not re.fullmatch(r"\d{1,3}(\.\d{3})*", wert):
            raise Abbruch(f"SPEC.md: Fallzahl nicht lesbar: {wert!r}")
        ziele[("Analysegruppe", gruppe, "", "Fallzahl")] = int(wert.replace(".", ""))

    # Stufen 2 und 4: Prävalenzen aus der Zieltabelle
    muster = re.compile(
        r"^\| (Adipositas|Schwere Adipositas) \| (Gesamt|Männer|Frauen) \| "
        r"([\d,]+) \([\d,]+–[\d,]+\) \| ([\d,]+) \([\d,]+–[\d,]+\) \|$",
        re.MULTILINE,
    )
    treffer = muster.findall(abend2)
    if len(treffer) != 6:
        raise Abbruch(f"SPEC.md: Zieltabelle hat {len(treffer)} statt 6 lesbare Zeilen.")
    for kennzahl, gruppe, roh, adj in treffer:
        for art, wert in (("roh", roh), ("adjustiert", adj)):
            k = (kennzahl, gruppe, art, "Praevalenz")
            if k in ziele:
                raise Abbruch(f"SPEC.md: Zielwert doppelt: {k}")
            ziele[k] = zahl_de(wert)

    # Stufe 4: die zwei Standardfehler der Gesamtgruppe (laut SPEC.md altersadjustiert)
    m = re.findall(
        r"Der Report nennt Standardfehler nur für die Gesamtgruppe: ([\d,]+) \(Adipositas\) "
        r"und ([\d,]+) \(schwere Adipositas\)\. Laut Tabelle 2 gehören beide zur "
        r"altersadjustierten Schätzung\.",
        abend2,
    )
    if len(m) != 1:
        raise Abbruch("SPEC.md: Satz mit den zwei Standardfehlern nicht genau einmal gefunden.")
    ziele[("Adipositas", "Gesamt", "adjustiert", "Standardfehler")] = zahl_de(m[0][0])
    ziele[("Schwere Adipositas", "Gesamt", "adjustiert", "Standardfehler")] = zahl_de(m[0][1])

    namen = {"Fallzahlen": "Fallzahl", "Prävalenz": "Praevalenz", "Standardfehler": "Standardfehler"}
    tol_ziel = toleranzen_lesen(
        abschnitt(abend2, "**Toleranz, vorab festgelegt:**", "**Fertig ist Abend 2"), namen)
    tol_ab = toleranzen_lesen(
        abschnitt(abend3, "**Übereinstimmung A gegen B:**", "Die Toleranz zwischen A und B"), namen)
    return ziele, tol_ziel, tol_ab


# ---------------------------------------------------------------------------
# Ergebnisdateien
# ---------------------------------------------------------------------------
def csv_lesen(pfad: Path) -> list[dict]:
    if not pfad.is_file():
        raise Abbruch(f"Datei fehlt: {pfad}")
    with pfad.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def genau_eine(zeilen: list[dict], bedingung: dict, wer: str) -> dict:
    gefunden = [z for z in zeilen if all(z[k] == v for k, v in bedingung.items())]
    if len(gefunden) != 1:
        raise Abbruch(f"{wer}: {len(gefunden)} statt genau 1 Zeile für {bedingung}. "
                      "Zeile nicht eindeutig zuordenbar.")
    return gefunden[0]


def als_wert(text: str, groesse: str, wer: str):
    if groesse == "Fallzahl":
        if not re.fullmatch(r"\d+", text):
            raise Abbruch(f"{wer}: Fallzahl ist keine ganze Zahl: {text!r}")
        return int(text)
    try:
        return float(text)
    except ValueError:
        raise Abbruch(f"{wer}: Wert nicht lesbar: {text!r}") from None


def urteil(a, b, tol: float, groesse: str, was: str) -> tuple[object, str]:
    """Abweichung a - b und Urteil. Bricht bei einem Grenzfall ab."""
    if groesse == "Fallzahl":
        abw = a - b
        return abw, BESTANDEN if abw == 0 else NICHT_BESTANDEN
    abw = a - b
    mit_rundung = round(abs(abw), 10) <= tol
    ohne_rundung = abs(abw) <= tol
    if mit_rundung != ohne_rundung:
        raise Abbruch(f"Grenzfall bei {was}: |Abweichung| = {abs(abw)!r}, Toleranz {tol}. "
                      "Urteil hängt an der Gleitkommarundung. Bitte entscheiden.")
    return abw, BESTANDEN if mit_rundung else NICHT_BESTANDEN


def zahl_text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, int):
        return str(v)
    return repr(float(v))


def abend3() -> None:
    if not SPEC.is_file():
        raise Abbruch("Bitte aus dem Wurzelverzeichnis des Repos starten (SPEC.md fehlt).")

    zuordnung = zuordnung_lesen()
    ziele, tol_ziel, tol_ab = spec_lesen()
    a_zeilen = csv_lesen(DATEI_A)
    b_zeilen = csv_lesen(DATEI_B)

    # Jede Zeile von B und jede Zeile von A der Stufen 1, 2 und 4 muss in der Tabelle stehen.
    b_bekannt = {(t["B_kennzahl"], t["B_gruppe"], t["B_methode"], t["B_groesse"]) for t in zuordnung}
    for z in b_zeilen:
        k = (z["kennzahl"], z["gruppe"], z["methode"], z["groesse"])
        if k not in b_bekannt:
            raise Abbruch(f"B: Zeile {k} steht nicht in der Zuordnungstabelle.")
    a_bekannt = {(t["A_kennzahl"], t["A_gruppe"], t["A_art"], t["A_groesse"]) for t in zuordnung}
    for z in a_zeilen:
        k = (z["kennzahl"], z["gruppe"], z["art"], z["groesse"])
        if z["stufe"] in ("1", "2", "4") and k not in a_bekannt:
            raise Abbruch(f"A: Zeile {k} der Stufe {z['stufe']} steht nicht in der Zuordnungstabelle.")
    if len(b_zeilen) != len(zuordnung):
        raise Abbruch(f"B hat {len(b_zeilen)} Zeilen, die Zuordnungstabelle {len(zuordnung)}.")
    benutzte_ziele = {(t["A_kennzahl"], t["A_gruppe"], t["A_art"], t["A_groesse"]) for t in zuordnung}
    if not set(ziele) <= benutzte_ziele:
        raise Abbruch(f"Zielwerte ohne Zeile: {set(ziele) - benutzte_ziele}")

    aus = []
    for t in zuordnung:
        za = genau_eine(a_zeilen, {"kennzahl": t["A_kennzahl"], "gruppe": t["A_gruppe"],
                                   "art": t["A_art"], "groesse": t["A_groesse"]}, "A")
        zb = genau_eine(b_zeilen, {"kennzahl": t["B_kennzahl"], "gruppe": t["B_gruppe"],
                                   "methode": t["B_methode"], "groesse": t["B_groesse"]}, "B")
        if za["stufe"] != t["stufe"] or zb["stufe"] != t["stufe"]:
            raise Abbruch(f"Zeile {t['zeile']}: Stufe passt nicht (A {za['stufe']}, B {zb['stufe']}, "
                          f"Tabelle {t['stufe']}).")
        if zb["einheit"] != t["B_einheit"]:
            raise Abbruch(f"Zeile {t['zeile']}: Einheit von B ist {zb['einheit']!r}, "
                          f"erwartet {t['B_einheit']!r}.")

        groesse = t["A_groesse"]
        was = f"Zeile {t['zeile']} ({t['A_kennzahl']} / {t['A_gruppe']} / {t['A_art']} / {groesse})"
        wa = als_wert(za["wert"], groesse, "A")
        wb = als_wert(zb["wert"], groesse, "B")
        ziel = ziele.get((t["A_kennzahl"], t["A_gruppe"], t["A_art"], groesse))

        # Gegenprobe: Zielwert in der Datei von A gleich dem aus SPEC.md
        a_ziel = za["zielwert"]
        if (ziel is None) != (a_ziel == ""):
            raise Abbruch(f"{was}: Zielwert aus SPEC.md {ziel!r}, in der Datei von A {a_ziel!r}.")
        if ziel is not None and float(a_ziel) != float(ziel):
            raise Abbruch(f"{was}: Zielwert aus SPEC.md {ziel!r}, in der Datei von A {a_ziel!r}.")

        if ziel is None:
            abw_a = abw_b = None
            u_a = u_b = NICHT_GEPRUEFT
            t_ziel = None
        else:
            t_ziel = tol_ziel[groesse]
            abw_a, u_a = urteil(wa, ziel, t_ziel, groesse, was + ", A gegen Ziel")
            abw_b, u_b = urteil(wb, ziel, t_ziel, groesse, was + ", B gegen Ziel")
        abw_ab, u_ab = urteil(wa, wb, tol_ab[groesse], groesse, was + ", A gegen B")

        # Gegenprobe: eigenes Urteil A gegen Ziel gleich dem Urteil in der Datei von A
        if za["urteil"] != u_a:
            raise Abbruch(f"{was}: Urteil A gegen Ziel hier {u_a!r}, in der Datei von A {za['urteil']!r}.")

        aus.append({
            "zeile": t["zeile"],
            "stufe": t["stufe"],
            "kennzahl": t["A_kennzahl"],
            "gruppe": t["A_gruppe"],
            "art": t["A_art"],
            "groesse": groesse,
            "bezeichnung_B": f"{t['B_kennzahl']} / {t['B_gruppe']} / {t['B_methode']} / "
                             f"{t['B_groesse']} / {t['B_einheit']}",
            "wert_A": zahl_text(wa),
            "wert_B": zahl_text(wb),
            "zielwert": zahl_text(ziel),
            "abweichung_A_ziel": zahl_text(abw_a),
            "abweichung_B_ziel": zahl_text(abw_b),
            "abweichung_A_B": zahl_text(abw_ab),
            "toleranz_ziel": zahl_text(t_ziel),
            "toleranz_A_B": zahl_text(tol_ab[groesse]),
            "urteil_A_gegen_ziel": u_a,
            "urteil_B_gegen_ziel": u_b,
            "urteil_A_gegen_B": u_ab,
        })

    AUSGABE.parent.mkdir(parents=True, exist_ok=True)
    with AUSGABE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(aus[0].keys()))
        w.writeheader()
        w.writerows(aus)

    # --- Übersicht auf der Konsole ---------------------------------------
    print("Eingaben (SHA-256):")
    for p in (SPEC, DATEI_A, DATEI_B, Path("B/positivkontrolle.py")):
        print(f"  {sha256(p)}  {p}")
    print(f"Toleranz gegen Ziel: {tol_ziel}")
    print(f"Toleranz A gegen B:  {tol_ab}")
    print()
    print(f"{'Zeile':>5}  {'Kennzahl / Gruppe / Art / Größe':<56} {'A':>10} {'B':>10} {'Ziel':>6} "
          f"{'A-B':>10}  A/Ziel | B/Ziel | A/B")
    for z in aus:
        name = f"{z['kennzahl']} / {z['gruppe']} / {z['art'] or '-'} / {z['groesse']}"
        def kurz(s, n=3):
            return "" if s == "" else (s if z["groesse"] == "Fallzahl" else f"{float(s):.{n}f}")
        print(f"{z['zeile']:>5}  {name:<56} {kurz(z['wert_A']):>10} {kurz(z['wert_B']):>10} "
              f"{kurz(z['zielwert'], 1):>6} {float(z['abweichung_A_B']):>10.1e}  "
              f"{z['urteil_A_gegen_ziel']} | {z['urteil_B_gegen_ziel']} | {z['urteil_A_gegen_B']}")

    geprueft = [z for z in aus if z["zielwert"] != ""]
    b_ok = all(z["urteil_B_gegen_ziel"] == BESTANDEN for z in geprueft)
    ab_ok = all(z["urteil_A_gegen_B"] == BESTANDEN for z in aus)
    max_ab = max(abs(float(z["abweichung_A_B"])) for z in aus)
    print()
    print(f"Extern geprüfte Zellen: {len(geprueft)}; B bestanden: "
          f"{sum(z['urteil_B_gegen_ziel'] == BESTANDEN for z in geprueft)}; "
          f"A bestanden: {sum(z['urteil_A_gegen_ziel'] == BESTANDEN for z in geprueft)}")
    print(f"A gegen B: {sum(z['urteil_A_gegen_B'] == BESTANDEN for z in aus)} von {len(aus)} bestanden; "
          f"größte |A-B| = {max_ab!r} Prozentpunkte bzw. Personen")
    print(f"Abend 3 nach SPEC.md: {'bestanden' if (b_ok and ab_ok) else 'nicht bestanden'}")
    print(f"Geschrieben: {AUSGABE} ({len(aus)} Zeilen)")


# ===========================================================================
# Abend 4: Fallzahlen und Vergleich Person für Person
# ===========================================================================
FALL_A = Path("results/A/abend4_fallzahlen.csv")
FALL_B = Path("results/B/abend4_fallzahlen.csv")
PERS_A = Path("data/work/abend4_personen_A.csv")
PERS_B = Path("data/work/abend4_personen_B.csv")
AUSGABE4 = Path("results/vergleich_abend4.csv")
N_SEQN = 15560  # SPEC.md: „Genau eine Zeile für jede der 15.560 SEQN aus P_DEMO“


def spec_abend4_lesen() -> tuple[list[str], list[str], list[str], list[str]]:
    """Zeilennamen (12), Spaltennamen (8), Trefferspalten (11) und Kategoriewerte aus SPEC.md."""
    text = SPEC.read_text(encoding="utf-8")
    abend4 = abschnitt(text, "## Abend 4 – Fallzahlen je Wirkstoff", "## Entscheidungsregel")

    tabelle = abschnitt(abend4, "| Zeilenname in der Ausgabe |", "Zusätzlich gibt es")
    haupt = re.findall(r"^\| `([A-Z_]+)` \| [^|]+ \|$", tabelle, re.MULTILINE)
    if len(haupt) != 7:
        raise Abbruch(f"SPEC.md: {len(haupt)} statt 7 Zeilennamen in der Wirkstofftabelle.")
    m = re.findall(r"Zusätzlich gibt es je eine Zeile `([A-Z_]+)`, `([A-Z_]+)`, `([A-Z_]+)` und "
                   r"`([A-Z_]+)` sowie die Zeile `([A-Z_]+)` für die ganze Analysegruppe\.", abend4)
    if len(m) != 1:
        raise Abbruch("SPEC.md: Satz „Zusätzlich gibt es je eine Zeile …“ nicht genau einmal gefunden.")
    doak, gesamt = list(m[0][:4]), m[0][4]
    zeilen = haupt + doak + [gesamt]
    if len(set(zeilen)) != 12:
        raise Abbruch(f"SPEC.md: Zeilennamen nicht eindeutig: {zeilen}")

    ausgabe = abschnitt(abend4, "**Ausgabe:**", "**Vergleich Person für Person.**")
    spalten = re.findall(r"^\| `(n_[a-z0-9_]+)` \| [^|]+ \|$", ausgabe, re.MULTILINE)
    if len(spalten) != 8 or len(set(spalten)) != 8:
        raise Abbruch(f"SPEC.md: {len(spalten)} statt 8 Spaltennamen in der Tabelle „Ausgabe“.")

    person = abschnitt(abend4, "**Vergleich Person für Person.**", "`vergleich.py` prüft")
    m = re.findall(r"Drei Kategoriespalten `(kat_[a-z]+)`, `(kat_[a-z]+)` und `(kat_[a-z]+)` "
                   r"mit den Werten `([^`]+)`, `([^`]+)`, `([^`]+)` oder `([^`]+)`\.", person)
    if len(m) != 1:
        raise Abbruch("SPEC.md: Satz zu den drei Kategoriespalten nicht genau einmal gefunden.")
    kat_spalten, kat_werte = list(m[0][:3]), list(m[0][3:])
    if "Eine Spalte `GESAMT` gibt es nicht." not in person:
        raise Abbruch("SPEC.md: Satz „Eine Spalte `GESAMT` gibt es nicht.“ nicht gefunden.")
    treffer = [z for z in zeilen if z != gesamt]
    pers_spalten = ["SEQN", "analysegruppe"] + treffer + kat_spalten
    return zeilen, spalten, pers_spalten, kat_werte


def csv_roh_lesen(pfad: Path) -> tuple[list[str], list[list[str]]]:
    if not pfad.is_file():
        raise Abbruch(f"Datei fehlt: {pfad}")
    with pfad.open(encoding="utf-8", newline="") as f:
        zeilen = list(csv.reader(f))
    if not zeilen:
        raise Abbruch(f"{pfad}: Datei ist leer.")
    kopf, daten = zeilen[0], zeilen[1:]
    if len(set(kopf)) != len(kopf):
        raise Abbruch(f"{pfad}: Spaltenname doppelt im Kopf {kopf}.")
    for nr, z in enumerate(daten, start=2):
        if len(z) != len(kopf):
            raise Abbruch(f"{pfad}, Zeile {nr}: {len(z)} statt {len(kopf)} Felder.")
    return kopf, daten


def fallzahlen_lesen(pfad: Path, zeilen: list[str], spalten: list[str]) -> dict:
    """{(zeilenname, spaltenname): int}. Zuordnung nur über Namen (OFFEN.md, Frage 5)."""
    kopf, daten = csv_roh_lesen(pfad)
    fehlend = [s for s in spalten if s not in kopf]
    if fehlend:
        raise Abbruch(f"{pfad}: Spalte(n) fehlen: {fehlend}")
    rest = [s for s in kopf if s not in spalten]
    if len(rest) != 1:
        raise Abbruch(f"{pfad}: statt genau einer Bezeichnerspalte gibt es {rest}.")
    i_name = kopf.index(rest[0])
    namen = [z[i_name] for z in daten]
    fehlend = [n for n in zeilen if n not in namen]
    if fehlend:
        raise Abbruch(f"{pfad}: Zeile(n) fehlen: {fehlend}")
    fremd = [n for n in namen if n not in zeilen]
    doppelt = sorted({n for n in namen if namen.count(n) > 1})
    if fremd or doppelt:
        raise Abbruch(f"{pfad}: unbekannte Zeile(n) {fremd}, doppelte Zeile(n) {doppelt}.")
    werte = {}
    for z in daten:
        for s in spalten:
            text = z[kopf.index(s)]
            if not re.fullmatch(r"\d+", text):
                raise Abbruch(f"{pfad}: Zelle {z[i_name]} / {s} ist keine ganze Zahl: {text!r}")
            werte[(z[i_name], s)] = int(text)
    return werte


def personen_wert(text: str, spalte: str, kat_spalten: set[str], kat_werte: list[str],
                  pfad: Path):
    """Wert einer Zelle der Personendatei (OFFEN.md, Frage 8b).
    Leer -> None. SEQN, analysegruppe, Trefferspalten -> ganze Zahl (1 und 1.0 gleich).
    Kategorien -> Text. Jeder andere Wert -> Abbruch."""
    if text == "":
        if spalte == "SEQN":
            raise Abbruch(f"{pfad}: leere SEQN.")
        return None
    if spalte in kat_spalten:
        if text not in kat_werte:
            raise Abbruch(f"{pfad}: Spalte {spalte}: unzulässiger Wert {text!r}.")
        return text
    m = re.fullmatch(r"(\d+)(\.0+)?", text)
    if not m:
        raise Abbruch(f"{pfad}: Spalte {spalte}: keine ganze Zahl: {text!r}.")
    wert = int(m.group(1))
    if spalte != "SEQN" and wert not in (0, 1):
        raise Abbruch(f"{pfad}: Spalte {spalte}: unzulässiger Wert {text!r} (erlaubt 1, 0, leer).")
    return wert


def personen_lesen(pfad: Path, pers_spalten: list[str], kat_werte: list[str]) -> dict:
    """{SEQN: {spalte: wert}}. Spalten werden über ihre Namen zugeordnet."""
    kopf, daten = csv_roh_lesen(pfad)
    fehlend = [s for s in pers_spalten if s not in kopf]
    fremd = [s for s in kopf if s not in pers_spalten]
    if fehlend or fremd:
        raise Abbruch(f"{pfad}: fehlende Spalte(n) {fehlend}, unbekannte Spalte(n) {fremd}.")
    kat_spalten = {s for s in pers_spalten if s.startswith("kat_")}
    personen: dict[int, dict] = {}
    for z in daten:
        satz = {s: personen_wert(z[kopf.index(s)], s, kat_spalten, kat_werte, pfad)
                for s in pers_spalten}
        if satz["SEQN"] in personen:
            raise Abbruch(f"{pfad}: SEQN doppelt.")
        personen[satz["SEQN"]] = satz
    return personen


def abend4() -> None:
    zeilen, spalten, pers_spalten, kat_werte = spec_abend4_lesen()

    # --- a) Fallzahlen, Zelle für Zelle ------------------------------------
    fa = fallzahlen_lesen(FALL_A, zeilen, spalten)
    fb = fallzahlen_lesen(FALL_B, zeilen, spalten)

    print()
    print("=" * 78)
    print("Abend 4")
    print("Eingaben (SHA-256):")
    for p in (SPEC, FALL_A, FALL_B, PERS_A, PERS_B, Path("B/fallzahlen.py")):
        print(f"  {sha256(p) if p.is_file() else 'fehlt':<64}  {p}")
    print()
    print("a) Fallzahlen: Zeilen über die 12 Zeilennamen, Spalten über die 8 Spaltennamen")
    print("   Zelle: A, B; '*' markiert eine ungleiche Zelle")
    breite = max(len(s) for s in spalten)
    print(f"{'':<15}" + "".join(f"{s[2:]:>{breite - 1}}" for s in spalten))
    ungleich = []
    for z in zeilen:
        felder = []
        for s in spalten:
            a, b = fa[(z, s)], fb[(z, s)]
            if a != b:
                ungleich.append((z, s, a, b))
            felder.append(f"{a}|{b}{'*' if a != b else ''}")
        print(f"{z:<15}" + "".join(f"{f:>{breite - 1}}" for f in felder))
    n_zellen = len(zeilen) * len(spalten)
    print(f"Zellen verglichen: {n_zellen}; gleich: {n_zellen - len(ungleich)}; "
          f"ungleich: {len(ungleich)}")
    for z, s, a, b in ungleich:
        print(f"  ungleich: {z} / {s}: A {a}, B {b}, A - B = {a - b}")

    # --- b) Person für Person --------------------------------------------
    pa = personen_lesen(PERS_A, pers_spalten, kat_werte)
    pb = personen_lesen(PERS_B, pers_spalten, kat_werte)
    if len(pa) != N_SEQN or len(pb) != N_SEQN:
        raise Abbruch(f"Personendateien: A {len(pa)}, B {len(pb)} SEQN, erwartet je {N_SEQN}.")
    if set(pa) != set(pb):
        raise Abbruch(f"Personendateien: verschiedene SEQN (nur in A: {len(set(pa) - set(pb))}, "
                      f"nur in B: {len(set(pb) - set(pa))}).")

    abw = {s: 0 for s in pers_spalten}
    for seqn in sorted(pa):
        for s in pers_spalten:
            if pa[seqn][s] != pb[seqn][s]:  # leer (None) gegen gefüllt ist ungleich
                abw[s] += 1

    with AUSGABE4.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["spalte", "abweichungen"])
        for s in pers_spalten:
            w.writerow([s, abw[s]])

    print()
    print(f"b) Person für Person: beide Dateien enthalten dieselben {N_SEQN} SEQN; "
          "Zuordnung über SEQN")
    for s in pers_spalten:
        print(f"  {s:<16} {abw[s]:>6}")
    print(f"Spalten mit Abweichung: {sum(1 for v in abw.values() if v)} von {len(pers_spalten)}; "
          f"Abweichungen gesamt: {sum(abw.values())}")
    print()
    fertig = not ungleich and not any(abw.values())
    print(f"Abend 4 nach SPEC.md (Fallzahlen identisch, null Abweichungen je Person): "
          f"{'erfüllt' if fertig else 'nicht erfüllt'}")
    print(f"Geschrieben: {AUSGABE4} ({len(pers_spalten)} Zeilen)")


def main() -> None:
    abend3()
    abend4()


if __name__ == "__main__":
    try:
        main()
    except Abbruch as e:
        print(f"ABBRUCH: {e}", file=sys.stderr)
        sys.exit(1)
