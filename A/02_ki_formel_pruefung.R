# A/02_ki_formel_pruefung.R – Abend 2, vor dem Rechnen (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis des Repos:  Rscript A/02_ki_formel_pruefung.R
#
# Prüft die Formel des Konfidenzintervalls aus SPEC.md (Abend 2, „Konfidenzintervall
# der rohen Prävalenzen“) an den durchgerechneten Beispielen der NCHS-Standards:
#
#   Parker JD, Talih M, Malec DJ, et al. National Center for Health Statistics data
#   presentation standards for proportions. Vital Health Stat 2(175). 2017
#   (Tabelle II am 8.4.2021 berichtigt). https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf
#
# Die Anhangtabellen I und II nennen je Zeile Stichprobengröße n, effektive
# Stichprobengröße n_e = p(1 − p)/var(p), Prozentwert, Freiheitsgrade und die
# Korn-Graubard-Grenzen. Die Eingaben unten sind aus diesen Tabellen abgeschrieben
# (gerundet, wie veröffentlicht). Es werden keine NHANES-Rohdaten gelesen.
#
# Drei Lesarten werden gerechnet:
#   spec          m = min(n, n_e · (t(0,975; n−1) / t(0,975; f))²)        – SPEC.md
#   kappe_zuerst  m = min(n, n_e) · (t(0,975; n−1) / t(0,975; f))²        – wörtliche Lesart
#                 von „the sample size should be used … for CIs“, Kappung vor dem Faktor
#   ohne_df       m = min(n, n_e)                                          – ohne Freiheitsgrad-Faktor
# Grenzen jeweils: Beta(0,025; x, m − x + 1) und Beta(0,975; x + 1, m − x), x = m · p.
#
# Ausgabe: results/A/abend2_ki_formel_pruefung.csv

if (!file.exists("SPEC.md")) stop("Bitte aus dem Wurzelverzeichnis des Repos starten.")

grenzen <- function(p, n_e, n, f, lesart) {
  faktor <- (qt(0.975, n - 1) / qt(0.975, f))^2
  m <- switch(lesart,
              spec         = min(n, n_e * faktor),
              kappe_zuerst = min(n, n_e) * faktor,
              ohne_df      = min(n, n_e))
  x <- m * p
  c(m = m, unten = 100 * qbeta(0.025, x, m - x + 1), oben = 100 * qbeta(0.975, x + 1, m - x))
}

# Abgeschrieben aus Series 2 Nr. 175, Seite 8 (Tabelle I, NHANES 2013–2014, Kinder 8–17,
# erhöhter Blutdruck) und Seite 9 (Tabelle II, NHANES 2013–2014, ab 60 Jahre, Übergewicht).
beispiele <- read.table(header = TRUE, stringsAsFactors = FALSE, text = "
tabelle zeile                         n   n_e   prozent f  unten_pub oben_pub
I       NH_white_elevated             460 583.0 0.5     15 0.1       1.6
I       NH_white_normal_borderline    460 583.0 99.5    15 98.4      99.9
I       NH_black_elevated             447 145.3 2.0     13 0.3       6.4
I       NH_black_normal_borderline    447 145.3 98.0    13 93.6      99.7
I       NH_Asian_elevated             164 124.8 0.9     13 0.0       5.1
I       NH_Asian_normal_borderline    164 124.8 99.1    13 94.9      100.0
I       Hispanic_elevated             589 946.8 2.5     15 1.4       4.1
I       Hispanic_normal_borderline    589 946.8 97.5    15 95.9      98.6
II      Men_Hispanic                  169 124.0 52.2    11 42.0      62.3
II      Men_NH_white                  384 246.0 38.6    15 32.0      45.6
II      Men_NH_black                  195 242.2 34.9    12 28.3      42.1
II      Men_NH_Asian                  74  108.7 47.8    7  36.0      59.7
II      Women_Hispanic                184 152.0 36.1    12 27.7      45.1
II      Women_NH_white                466 296.4 34.3    15 28.4      40.5
II      Women_NH_black                175 235.3 25.1    12 18.8      32.2
II      Women_NH_Asian                82  108.4 25.0    7  15.8      36.2
")

zeilen <- list()
for (lesart in c("spec", "kappe_zuerst", "ohne_df")) {
  r <- t(mapply(function(p, n_e, n, f) grenzen(p / 100, n_e, n, f, lesart),
                beispiele$prozent, beispiele$n_e, beispiele$n, beispiele$f))
  d <- beispiele
  d$lesart       <- lesart
  d$m            <- r[, "m"]
  d$unten_ber    <- r[, "unten"]
  d$oben_ber     <- r[, "oben"]
  # Der veröffentlichte Wert ist auf 0,1 gerundet; verglichen wird der auf 0,1 gerundete
  # berechnete Wert und zusätzlich die ungerundete Abweichung.
  d$abw_max_ungerundet <- pmax(abs(d$unten_ber - d$unten_pub), abs(d$oben_ber - d$oben_pub))
  d$gleich_auf_0_1 <- round(d$unten_ber, 1) == d$unten_pub & round(d$oben_ber, 1) == d$oben_pub
  zeilen[[lesart]] <- d
}
tab <- do.call(rbind, zeilen)
rownames(tab) <- NULL

# Rundung der Eingaben: Prozentwert und n_e sind auf 0,1 gerundet veröffentlicht.
# Gibt es innerhalb dieser Rundung (± 0,05) Eingaben, mit denen beide berechneten
# Grenzen auf 0,1 gerundet genau die veröffentlichten treffen?
erklaerbar <- function(z, lesart) {
  for (dp in seq(-0.05, 0.05, by = 0.005)) for (dn in seq(-0.05, 0.05, by = 0.01)) {
    g <- grenzen((z$prozent + dp) / 100, z$n_e + dn, z$n, z$f, lesart)
    if (round(g[["unten"]], 1) == z$unten_pub && round(g[["oben"]], 1) == z$oben_pub) return(TRUE)
  }
  FALSE
}
tab$durch_rundung_erklaerbar <- vapply(seq_len(nrow(tab)), function(i) erklaerbar(tab[i, ], tab$lesart[i]), logical(1))

dir.create(file.path("results", "A"), recursive = TRUE, showWarnings = FALSE)
write.csv(tab, file.path("results", "A", "abend2_ki_formel_pruefung.csv"), row.names = FALSE)

cat("\nZusammenfassung je Lesart (16 Beispielzeilen):\n")
for (l in unique(tab$lesart)) {
  s <- tab[tab$lesart == l, ]
  cat(sprintf("  %-13s größte Abweichung %.3f Prozentpunkte, auf 0,1 gerundet gleich: %d von %d, mit Eingaben innerhalb der Rundung gleich: %d von %d\n",
              l, max(s$abw_max_ungerundet), sum(s$gleich_auf_0_1), nrow(s),
              sum(s$durch_rundung_erklaerbar), nrow(s)))
}
