# A/05_formeln.R – Abend 4: Funktionen für Nierenformeln, Kategorien und Namensabgleich
# (Auswerter A)
#
# Nur Funktionen, keine Daten. Wird von A/06_rechentests.R und vom Zählskript
# mit source() geladen. Grundlage: SPEC.md Version 2.1, Abschnitt "Abend 4".
#
# Einheiten: Kreatinin (scr) in mg/dL, Gewicht in kg, Größe in cm, Alter in Jahren.
# Geschlecht nach Definition 7: 1 = männlich, 2 = weiblich.
# Alter wird unverändert übernommen (Definition 3); ab 80 steht in RIDAGEYR schon 80.
#
# Jede Funktion bricht ab, wenn eine Eingabe fehlt, nicht endlich oder nicht
# größer null ist (Geschlecht: nicht 1 oder 2). Rechnen auf fehlenden Werten
# ist im Pilot nicht vorgesehen; die Analysegruppe verlangt vollständige Werte.

pruefe_positiv <- function(x, name) {
  if (any(is.na(x)) || any(!is.finite(x)) || any(x <= 0)) {
    stop(name, ": fehlender, nicht endlicher oder nicht positiver Wert.", call. = FALSE)
  }
}

pruefe_geschlecht <- function(g) {
  if (any(is.na(g)) || any(!(g %in% c(1, 2)))) {
    stop("Geschlecht muss 1 (männlich) oder 2 (weiblich) sein.", call. = FALSE)
  }
}

# CKD-EPI 2021 (Kreatinin, ohne Rasse), indexiert, ml/min/1,73 m²
#   142 · min(scr/k, 1)^a · max(scr/k, 1)^(-1,200) · 0,9938^alter · (1,012 bei Frauen)
#   Frauen: k = 0,7, a = -0,241; Männer: k = 0,9, a = -0,302
ckd_epi_2021 <- function(scr, alter, geschlecht) {
  pruefe_positiv(scr, "Kreatinin")
  pruefe_positiv(alter, "Alter")
  pruefe_geschlecht(geschlecht)
  frau <- geschlecht == 2
  k <- ifelse(frau, 0.7, 0.9)
  a <- ifelse(frau, -0.241, -0.302)
  q <- scr / k
  142 * pmin(q, 1)^a * pmax(q, 1)^(-1.200) * 0.9938^alter * ifelse(frau, 1.012, 1)
}

# Körperoberfläche nach DuBois, m²: 0,007184 · gewicht^0,425 · groesse^0,725
kof_dubois <- function(gewicht, groesse) {
  pruefe_positiv(gewicht, "Gewicht")
  pruefe_positiv(groesse, "Größe")
  0.007184 * gewicht^0.425 * groesse^0.725
}

# CKD-EPI 2021 de-indexiert, ml/min: indexierter Wert · KOF / 1,73
ckd_epi_deindex <- function(egfr_index, kof) {
  pruefe_positiv(egfr_index, "eGFR indexiert")
  pruefe_positiv(kof, "Körperoberfläche")
  egfr_index * kof / 1.73
}

# Cockcroft-Gault, ml/min: (140 - alter) · gewicht / (72 · scr), bei Frauen · 0,85
# Tatsächliches Körpergewicht, kein Bezug auf die Körperoberfläche.
cockcroft_gault <- function(alter, gewicht, scr, geschlecht) {
  pruefe_positiv(alter, "Alter")
  pruefe_positiv(gewicht, "Gewicht")
  pruefe_positiv(scr, "Kreatinin")
  pruefe_geschlecht(geschlecht)
  (140 - alter) * gewicht / (72 * scr) * ifelse(geschlecht == 2, 0.85, 1)
}

# Kategorie des ungerundeten Werts: u30, 30_45, 45_60, ab60
#   unter 30 | 30 bis unter 45 | 45 bis unter 60 | ab 60
kategorie <- function(x) {
  if (any(is.na(x)) || any(!is.finite(x))) {
    stop("Kategorie: fehlender oder nicht endlicher Wert.", call. = FALSE)
  }
  ifelse(x < 30, "u30",
  ifelse(x < 45, "30_45",
  ifelse(x < 60, "45_60", "ab60")))
}

# Namensabgleich für RXDDRUG (SPEC.md, Abend 4, "Wirkstoffnutzer"):
#   als Text lesen, Leerzeichen außen entfernen, Großbuchstaben,
#   in Folgen [A-Z0-9]+ zerlegen; Treffer = exakte Gleichheit einer Folge mit
#   einem Suchbegriff. Fehlender Name, 55555, 77777, 99999: kein Treffer.
# Gibt je Eintrag TRUE/FALSE zurück, nie NA.
name_trifft <- function(rxddrug, begriffe) {
  txt <- toupper(trimws(as.character(rxddrug)))
  ungueltig <- is.na(txt) | txt == "" | txt %in% c("55555", "77777", "99999")
  txt[is.na(txt)] <- ""
  folgen <- regmatches(txt, gregexpr("[A-Z0-9]+", txt))
  treffer <- vapply(folgen, function(f) any(f %in% begriffe), logical(1))
  treffer[ungueltig] <- FALSE
  treffer
}
