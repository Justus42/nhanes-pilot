# A/04_zielvergleich.R – Abend 2: Vergleich mit den Zielwerten (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis des Repos:  Rscript A/04_zielvergleich.R
# Vorher muss A/03_positivkontrolle.R gelaufen sein.
#
# Liest results/A/abend2_werte.csv (gerechnet ohne Kenntnis der Ziele) und ergänzt
# Zielwert, Toleranz, Abweichung und Urteil. Nur dieses Skript enthält Zielwerte.
#
# Zielwerte: SPEC.md Version 2.1, Abend 2, abgelesen aus NCHS, National Health
# Statistics Report Nr. 158 (Stierman et al., 2021), Tabellen 2, 5 und 6.
# Toleranzen: SPEC.md, Abend 2, „Toleranz, vorab festgelegt“. Beide hier unverändert.
#
# Regeln (SPEC.md, Definition 5): ungerundete Werte, in Prozentpunkten,
# „bestanden“ heißt |Abweichung| kleiner oder gleich Toleranz.
# Abweichung = Wert − Zielwert.
#
# Ausgabe: results/A/abend2_positivkontrolle.csv

if (!file.exists("SPEC.md")) stop("Bitte aus dem Wurzelverzeichnis des Repos starten.")

werte <- read.csv(file.path("results", "A", "abend2_werte.csv"),
                  stringsAsFactors = FALSE, na.strings = "", encoding = "UTF-8")
werte$art[is.na(werte$art)] <- ""

# --- Zielwerte (SPEC.md v2.1) ---------------------------------------------
ziele <- read.table(header = TRUE, sep = "|", strip.white = TRUE, stringsAsFactors = FALSE,
                    encoding = "UTF-8", text = "
kennzahl           | gruppe | art        | groesse        | zielwert
Analysegruppe      | Gesamt |            | Fallzahl       | 8295
Analysegruppe      | Männer |            | Fallzahl       | 4051
Analysegruppe      | Frauen |            | Fallzahl       | 4244
Adipositas         | Gesamt | roh        | Praevalenz     | 41.9
Adipositas         | Gesamt | roh        | KI_unten       | 39.4
Adipositas         | Gesamt | roh        | KI_oben        | 44.3
Adipositas         | Männer | roh        | Praevalenz     | 41.6
Adipositas         | Männer | roh        | KI_unten       | 37.4
Adipositas         | Männer | roh        | KI_oben        | 45.8
Adipositas         | Frauen | roh        | Praevalenz     | 42.1
Adipositas         | Frauen | roh        | KI_unten       | 39.6
Adipositas         | Frauen | roh        | KI_oben        | 44.8
Schwere Adipositas | Gesamt | roh        | Praevalenz     | 9.0
Schwere Adipositas | Gesamt | roh        | KI_unten       | 7.8
Schwere Adipositas | Gesamt | roh        | KI_oben        | 10.3
Schwere Adipositas | Männer | roh        | Praevalenz     | 6.4
Schwere Adipositas | Männer | roh        | KI_unten       | 5.1
Schwere Adipositas | Männer | roh        | KI_oben        | 8.0
Schwere Adipositas | Frauen | roh        | Praevalenz     | 11.4
Schwere Adipositas | Frauen | roh        | KI_unten       | 9.7
Schwere Adipositas | Frauen | roh        | KI_oben        | 13.3
Adipositas         | Gesamt | adjustiert | Praevalenz     | 41.9
Adipositas         | Männer | adjustiert | Praevalenz     | 41.8
Adipositas         | Frauen | adjustiert | Praevalenz     | 41.8
Schwere Adipositas | Gesamt | adjustiert | Praevalenz     | 9.2
Schwere Adipositas | Männer | adjustiert | Praevalenz     | 6.6
Schwere Adipositas | Frauen | adjustiert | Praevalenz     | 11.7
Adipositas         | Gesamt | adjustiert | Standardfehler | 1.2
Schwere Adipositas | Gesamt | adjustiert | Standardfehler | 0.6
")
ziele$art[is.na(ziele$art)] <- ""

# --- Toleranzen (SPEC.md, fester Kern) ------------------------------------
toleranz <- c(Fallzahl = 0, Praevalenz = 0.1, Standardfehler = 0.1, KI_unten = 0.2, KI_oben = 0.2)

schluessel <- function(d) paste(d$kennzahl, d$gruppe, d$art, d$groesse, sep = "|")
if (anyDuplicated(schluessel(ziele))) stop("Doppelter Zielwert.")
fehlt <- setdiff(schluessel(ziele), schluessel(werte))
if (length(fehlt)) stop("Zu diesen Zielwerten fehlt ein gerechneter Wert: ", paste(fehlt, collapse = "; "))

erg <- werte
erg$zielwert <- ziele$zielwert[match(schluessel(erg), schluessel(ziele))]
erg$toleranz <- ifelse(is.na(erg$zielwert), NA, toleranz[erg$groesse])
erg$abweichung <- erg$wert - erg$zielwert
# Auf 10 Nachkommastellen gerundet nur, damit Gleitkommadarstellung (z. B. 41,8 − 41,9)
# nicht als 0,1000000000000014 zählt. Die Toleranz selbst bleibt unverändert.
erg$urteil <- ifelse(is.na(erg$zielwert), "extern nicht geprüft",
                     ifelse(round(abs(erg$abweichung), 10) <= erg$toleranz,
                            "bestanden", "nicht bestanden"))

spalten <- c("stufe", "kennzahl", "gruppe", "art", "groesse", "wert", "zielwert",
             "abweichung", "toleranz", "urteil", "n", "f", "m")
erg <- erg[, spalten]

aus <- erg
voll <- function(v) ifelse(is.na(v), NA, sprintf("%.17g", v))
for (sp in c("wert", "abweichung", "m")) aus[[sp]] <- voll(aus[[sp]])
write.csv(aus, file.path("results", "A", "abend2_positivkontrolle.csv"), row.names = FALSE, na = "",
          quote = which(names(aus) %in% c("kennzahl", "gruppe", "art", "groesse", "urteil")),
          fileEncoding = "UTF-8")

# --- Übersicht -------------------------------------------------------------
geprueft <- erg[erg$urteil != "extern nicht geprüft", ]
anzeige <- geprueft
anzeige$wert <- round(anzeige$wert, 3); anzeige$abweichung <- round(anzeige$abweichung, 3)
print(anzeige[, c("stufe", "kennzahl", "gruppe", "art", "groesse", "wert", "zielwert",
                  "abweichung", "toleranz", "urteil")], row.names = FALSE)
cat("\nExtern geprüfte Zellen je Stufe:\n")
print(table(stufe = geprueft$stufe, urteil = geprueft$urteil))
cat(sprintf("\nExtern geprüft: %d, bestanden: %d, nicht bestanden: %d, extern nicht geprüft: %d\n",
            nrow(geprueft), sum(geprueft$urteil == "bestanden"),
            sum(geprueft$urteil == "nicht bestanden"), sum(erg$urteil == "extern nicht geprüft")))
cat("Geschrieben: results/A/abend2_positivkontrolle.csv\n")
