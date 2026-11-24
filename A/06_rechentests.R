# A/06_rechentests.R – Abend 4: Rechentests vor dem Zählen (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis:  Rscript A/06_rechentests.R
#
# Teil 1: die neun Rechentests aus SPEC.md, Abend 4, "Rechentests vor dem Zählen".
#   Abbruch, wenn ein Wert um mehr als 0,01 abweicht, bei der Körperoberfläche
#   um mehr als 0,0001 m². Erwartungswerte und Toleranzen sind aus SPEC.md
#   abgeschrieben (Version 2.1) und unverändert.
# Teil 2: eigene Zusatzprüfungen von A (nicht aus SPEC.md, kein Kriterium der
#   Spezifikation): Kategoriegrenzen und Namensabgleich an konstruierten Fällen.
#   Sie prüfen nur, ob der Code die Textregeln der Spezifikation umsetzt.
#
# Liest keine NHANES-Daten. Schreibt results/A/abend4_rechentests.csv.

if (!file.exists("SPEC.md")) stop("Bitte aus dem Wurzelverzeichnis des Repos starten.")
source(file.path("A", "05_formeln.R"))

M <- 1; F <- 2
kof_test <- kof_dubois(72, 175)

tests <- data.frame(
  fall = c(
    "Mann, 60 J., 72 kg, Krea 1,0: Cockcroft-Gault",
    "Frau, 60 J., 72 kg, Krea 1,0: Cockcroft-Gault",
    "Mann, 60 J., Krea 0,9: CKD-EPI indexiert",
    "Frau, 60 J., Krea 0,7: CKD-EPI indexiert",
    "Mann, 60 J., Krea 1,8: CKD-EPI indexiert",
    "Mann, 60 J., Krea 0,45: CKD-EPI indexiert",
    "Frau, 60 J., Krea 0,35: CKD-EPI indexiert",
    "72 kg, 175 cm: Körperoberfläche",
    "Mann, 60 J., 72 kg, 175 cm, Krea 1,8: CKD-EPI de-indexiert"
  ),
  erwartet = c(80.00, 68.00, 97.78, 98.95, 42.56, 120.54, 116.94, 1.8704, 46.01),
  berechnet = c(
    cockcroft_gault(60, 72, 1.0, M),
    cockcroft_gault(60, 72, 1.0, F),
    ckd_epi_2021(0.9, 60, M),
    ckd_epi_2021(0.7, 60, F),
    ckd_epi_2021(1.8, 60, M),
    ckd_epi_2021(0.45, 60, M),
    ckd_epi_2021(0.35, 60, F),
    kof_test,
    ckd_epi_deindex(ckd_epi_2021(1.8, 60, M), kof_dubois(72, 175))
  ),
  toleranz = c(rep(0.01, 7), 0.0001, 0.01),
  stringsAsFactors = FALSE
)
tests$teil <- "SPEC"
tests$abweichung <- tests$berechnet - tests$erwartet
# Wie an Abend 2: |Abweichung| vor dem Vergleich auf 10 Stellen runden, damit
# Gleitkommareste nicht zählen. Die Toleranz selbst ist unverändert.
tests$urteil <- ifelse(round(abs(tests$abweichung), 10) <= tests$toleranz,
                       "bestanden", "nicht bestanden")

# Teil 2: eigene Zusatzprüfungen (erwartet = 1 heißt "trifft zu")
zusatz <- function(fall, ok) data.frame(
  fall = fall, erwartet = 1, berechnet = as.numeric(isTRUE(ok)), toleranz = 0,
  teil = "Zusatz A", abweichung = as.numeric(isTRUE(ok)) - 1,
  urteil = ifelse(isTRUE(ok), "bestanden", "nicht bestanden"),
  stringsAsFactors = FALSE)

z <- rbind(
  zusatz("Kategorie: 29.999999 -> u30, 30 -> 30_45",
         identical(kategorie(c(29.999999, 30)), c("u30", "30_45"))),
  zusatz("Kategorie: 44.999999 -> 30_45, 45 -> 45_60",
         identical(kategorie(c(44.999999, 45)), c("30_45", "45_60"))),
  zusatz("Kategorie: 59.999999 -> 45_60, 60 -> ab60",
         identical(kategorie(c(59.999999, 60)), c("45_60", "ab60"))),
  zusatz("Name: 'METFORMIN; SITAGLIPTIN' trifft METFORMIN und SITAGLIPTIN",
         name_trifft("METFORMIN; SITAGLIPTIN", "METFORMIN") &&
         name_trifft("METFORMIN; SITAGLIPTIN", "SITAGLIPTIN")),
  zusatz("Name: '  metformin ' trifft METFORMIN (trim, Großbuchstaben)",
         name_trifft("  metformin ", "METFORMIN")),
  zusatz("Name: 'HYDROCHLOROTHIAZIDE; SPIRONOLACTONE' trifft SPIRONOLACTONE",
         name_trifft("HYDROCHLOROTHIAZIDE; SPIRONOLACTONE", "SPIRONOLACTONE")),
  zusatz("Name: 'METFORMINX' trifft METFORMIN nicht (keine Teilfolge)",
         !name_trifft("METFORMINX", "METFORMIN")),
  zusatz("Name: 'DABIGATRAN ETEXILATE' trifft DOAK-Begriffe",
         name_trifft("DABIGATRAN ETEXILATE",
                     c("APIXABAN", "RIVAROXABAN", "DABIGATRAN", "EDOXABAN"))),
  zusatz("Name: 55555, 77777, 99999, leer, NA -> kein Treffer, nie NA",
         identical(name_trifft(c("55555", "77777", "99999", "", NA), c("55555", "77777", "99999")),
                   rep(FALSE, 5)))
)

alle <- rbind(tests, z)[, c("teil", "fall", "erwartet", "berechnet", "abweichung", "toleranz", "urteil")]

dir.create(file.path("results", "A"), recursive = TRUE, showWarnings = FALSE)
write.csv(alle, file.path("results", "A", "abend4_rechentests.csv"), row.names = FALSE)

print(transform(alle, berechnet = formatC(berechnet, digits = 6, format = "f"),
                abweichung = formatC(abweichung, digits = 6, format = "f")),
      row.names = FALSE, right = FALSE)

if (any(alle$urteil != "bestanden")) {
  stop("RECHENTEST NICHT BESTANDEN. Abbruch vor dem Zählen.", call. = FALSE)
}
message("Alle ", sum(alle$teil == "SPEC"), " Rechentests der Spezifikation und alle ",
        sum(alle$teil != "SPEC"), " Zusatzprüfungen bestanden.")
