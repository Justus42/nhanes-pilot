# A/03_positivkontrolle.R – Abend 2: Positivkontrolle, Auswertung (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis des Repos:  Rscript A/03_positivkontrolle.R
# Vorher muss A/01_download.R gelaufen sein (Rohdaten in data/raw/).
#
# Dieses Skript kennt keine Zielwerte und keine erwarteten Fallzahlen. Es rechnet nur.
# Zielwert, Abweichung und Urteil ergänzt erst A/04_zielvergleich.R.
#
# Was es rechnet (SPEC.md, Abend 2):
#   Stufe 1  Fallzahlen der Analysegruppe: Gesamt, Männer, Frauen
#   Stufe 2  rohe Prävalenzen von Adipositas (BMI >= 30) und schwerer Adipositas
#            (BMI >= 40) mit Standardfehler (Taylor-Linearisierung)
#   Stufe 3  Konfidenzintervalle der rohen Prävalenzen nach Korn und Graubard in der
#            Fassung der SPEC (mit n, f, m); zusätzlich svyciprop(method = "beta")
#   Stufe 4  altersadjustierte Prävalenzen und Standardfehler (direkt, Standard-
#            bevölkerung 2000, Anteile 0,396579 / 0,371795 / 0,231626)
#
# Ausgabe: results/A/abend2_werte.csv
# Alle Prävalenzen, Standardfehler und Grenzen in Prozent bzw. Prozentpunkten, ungerundet.

suppressPackageStartupMessages({
  library(foreign)
  library(survey)
  library(digest)
})

if (!file.exists("SPEC.md")) stop("Bitte aus dem Wurzelverzeichnis des Repos starten.")

# ---------------------------------------------------------------------------
# 0. Rohdaten: Prüfsummen gegen Abend 1 (Regel 3), dann lesen
# ---------------------------------------------------------------------------
referenz <- read.csv(file.path("results", "A", "abend1_dateien.csv"),
                     stringsAsFactors = FALSE, colClasses = "character")
lese <- function(name, variablen) {
  pfad <- file.path("data", "raw", paste0(name, ".xpt"))
  if (!file.exists(pfad)) stop(pfad, " fehlt. Erst Rscript A/01_download.R ausführen.", call. = FALSE)
  sha <- digest(pfad, algo = "sha256", file = TRUE)
  if (!identical(sha, referenz$sha256[referenz$datei == name]))
    stop("Prüfsumme von ", pfad, " weicht von results/A/abend1_dateien.csv ab.", call. = FALSE)
  d <- read.xport(pfad)
  fehlend <- setdiff(variablen, names(d))
  if (length(fehlend)) stop("In ", name, " fehlen: ", paste(fehlend, collapse = ", "), call. = FALSE)
  d[, variablen]
}

demo <- lese("P_DEMO", c("SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG",
                         "WTMECPRP", "SDMVSTRA", "SDMVPSU"))
bmx  <- lese("P_BMX",  c("SEQN", "BMXBMI"))
if (anyDuplicated(demo$SEQN)) stop("SEQN in P_DEMO nicht eindeutig.")
if (anyDuplicated(bmx$SEQN))  stop("SEQN in P_BMX nicht eindeutig.")

# ---------------------------------------------------------------------------
# 1. Designbasis (Definition 4): RIDSTATR = 2 und WTMECPRP > 0
# ---------------------------------------------------------------------------
in_basis <- demo$RIDSTATR %in% 2 & !is.na(demo$WTMECPRP) & demo$WTMECPRP > 0
basis <- demo[in_basis, ]
n_basis <- nrow(basis)
basis <- merge(basis, bmx, by = "SEQN", all.x = TRUE, sort = TRUE)
if (nrow(basis) != n_basis) stop("Beim Anfügen von P_BMX hat sich die Personenzahl geändert.")

cat(sprintf("P_DEMO: %d Personen; RIDSTATR = 2: %d; davon WTMECPRP > 0: %d (Designbasis)\n",
            nrow(demo), sum(demo$RIDSTATR %in% 2), n_basis))

# Stratum mit nur einem Cluster? Dann anhalten (SPEC.md, Methode).
psu_je_stratum <- tapply(basis$SDMVPSU, basis$SDMVSTRA, function(x) length(unique(x)))
if (any(psu_je_stratum < 2)) {
  stop("Stratum mit nur einem Cluster in der Designbasis: ",
       paste(names(psu_je_stratum)[psu_je_stratum < 2], collapse = ", "),
       ". Anhalten und in OFFEN.md eintragen.", call. = FALSE)
}
cat(sprintf("Designbasis: %d Strata, %d Cluster (Strata-PSU-Paare), Cluster je Stratum %d bis %d\n",
            length(psu_je_stratum), sum(psu_je_stratum), min(psu_je_stratum), max(psu_je_stratum)))

# ---------------------------------------------------------------------------
# 2. Vollständige Ja/Nein-Masken (Definitionen 1, 2, 3, 7)
# ---------------------------------------------------------------------------
alter_ab20      <- !is.na(basis$RIDAGEYR) & basis$RIDAGEYR >= 20
bmi_gueltig     <- !is.na(basis$BMXBMI)
nicht_schwanger <- is.na(basis$RIDEXPRG) | basis$RIDEXPRG != 1

basis$d_gesamt <- alter_ab20 & bmi_gueltig & nicht_schwanger
basis$d_maenner <- basis$d_gesamt & basis$RIAGENDR %in% 1
basis$d_frauen  <- basis$d_gesamt & basis$RIAGENDR %in% 2

basis$adip        <- as.numeric(bmi_gueltig & basis$BMXBMI >= 30)
basis$adip_schwer <- as.numeric(bmi_gueltig & basis$BMXBMI >= 40)

basis$altersgruppe <- factor(
  ifelse(!alter_ab20, "unter20",
         ifelse(basis$RIDAGEYR <= 39, "20-39",
                ifelse(basis$RIDAGEYR <= 59, "40-59", "60+"))),
  levels = c("unter20", "20-39", "40-59", "60+"))

masken <- c("d_gesamt", "d_maenner", "d_frauen", "adip", "adip_schwer")
if (anyNA(basis[, masken]) || anyNA(basis$altersgruppe)) stop("Fehlender Wert in einer Maske.")

# ---------------------------------------------------------------------------
# 3. Design (SPEC.md, Methode), Teilgruppen über subset() auf dem Designobjekt
# ---------------------------------------------------------------------------
des <- svydesign(ids = ~SDMVPSU, strata = ~SDMVSTRA, weights = ~WTMECPRP,
                 nest = TRUE, data = basis)

gruppen <- c(Gesamt = "d_gesamt", "Männer" = "d_maenner", Frauen = "d_frauen")
kennzahlen <- c(Adipositas = "adip", "Schwere Adipositas" = "adip_schwer")

standardanteile <- c("20-39" = 0.396579, "40-59" = 0.371795, "60+" = 0.231626)
stopifnot(abs(sum(standardanteile) - 1) < 1e-12)

zeilen <- list()
neu <- function(stufe, kennzahl, gruppe, art, groesse, wert, n = NA, f = NA, m = NA) {
  zeilen[[length(zeilen) + 1]] <<- data.frame(
    stufe = stufe, kennzahl = kennzahl, gruppe = gruppe, art = art, groesse = groesse,
    wert = wert, n = n, f = f, m = m, stringsAsFactors = FALSE)
}

for (g in names(gruppen)) {
  maske <- basis[[gruppen[[g]]]]
  sub <- subset(des, basis[[gruppen[[g]]]])

  # Stufe 1: Fallzahl
  n <- sum(maske)
  neu(1, "Analysegruppe", g, "", "Fallzahl", n)

  # f: Cluster minus Strata, nur solche mit Personen der Teilgruppe
  teil <- basis[maske, ]
  f <- length(unique(paste(teil$SDMVSTRA, teil$SDMVPSU))) - length(unique(teil$SDMVSTRA))

  for (k in names(kennzahlen)) {
    y <- kennzahlen[[k]]
    fml <- as.formula(paste0("~", y))

    # Stufe 2: rohe Prävalenz und Standardfehler
    est <- svymean(fml, sub)
    p <- unname(coef(est)[1])
    V <- unname(vcov(est)[1, 1])
    neu(2, k, g, "roh", "Praevalenz", 100 * p)
    neu(2, k, g, "roh", "Standardfehler", 100 * sqrt(V))

    # Stufe 3: Korn-Graubard nach SPEC.md
    if (!(p > 0 && p < 1 && V > 0)) {
      stop("p = 0 oder 1 bzw. V = 0 bei ", k, ", ", g,
           ": Randfall nicht in SPEC.md geregelt (OFFEN.md, Frage 3). Anhalten.", call. = FALSE)
    }
    m <- min(n, p * (1 - p) / V * (qt(0.975, n - 1) / qt(0.975, f))^2)
    x <- m * p
    unten <- qbeta(0.025, x, m - x + 1)
    oben  <- qbeta(0.975, x + 1, m - x)
    neu(3, k, g, "roh", "KI_unten", 100 * unten, n, f, m)
    neu(3, k, g, "roh", "KI_oben",  100 * oben,  n, f, m)

    # Zusatz: svyciprop(method = "beta"); maßgeblich ist die Formel oben
    cip <- svyciprop(fml, sub, method = "beta")
    ci  <- confint(cip)
    neu(3, k, g, "roh", "KI_unten_svyciprop_beta", 100 * ci[1, 1])
    neu(3, k, g, "roh", "KI_oben_svyciprop_beta",  100 * ci[1, 2])

    # Stufe 4: altersadjustiert, Altersgruppen gemeinsam mit voller Kovarianzmatrix
    leer <- names(standardanteile)[!names(standardanteile) %in% unique(as.character(teil$altersgruppe))]
    if (length(leer)) stop("Leere Altersgruppe ", paste(leer, collapse = ", "), " bei ", g, call. = FALSE)
    by <- svyby(fml, ~altersgruppe, sub, svymean, covmat = TRUE, drop.empty.groups = TRUE)
    if (!setequal(names(coef(by)), names(standardanteile)))
      stop("svyby liefert unerwartete Altersgruppen: ", paste(names(coef(by)), collapse = ", "))

    # Gegenprobe: jede Altersgruppe einzeln als Domäne muss dasselbe ergeben
    for (a in names(standardanteile)) {
      einzel <- svymean(fml, subset(des, basis[[gruppen[[g]]]] & basis$altersgruppe == a))
      if (abs(coef(einzel)[[1]] - coef(by)[[a]]) > 1e-12 ||
          abs(vcov(einzel)[1, 1] - vcov(by)[a, a]) > 1e-14)
        stop("svyby und Einzelschätzung weichen ab: ", k, ", ", g, ", ", a)
    }

    adj <- svycontrast(by, standardanteile[names(coef(by))])
    neu(4, k, g, "adjustiert", "Praevalenz",     100 * unname(coef(adj)[1]))
    neu(4, k, g, "adjustiert", "Standardfehler", 100 * unname(sqrt(vcov(adj)[1, 1])))
  }
}

werte <- do.call(rbind, zeilen)

# Volle Rechengenauigkeit: 17 signifikante Stellen statt der 15 von write.csv
voll <- function(v) ifelse(is.na(v), NA, sprintf("%.17g", v))
aus <- werte
for (sp in c("wert", "m")) aus[[sp]] <- voll(aus[[sp]])
dir.create(file.path("results", "A"), recursive = TRUE, showWarnings = FALSE)
write.csv(aus, file.path("results", "A", "abend2_werte.csv"), row.names = FALSE, na = "",
          quote = which(names(aus) %in% c("kennzahl", "gruppe", "art", "groesse")))

cat(sprintf("Freiheitsgrade des Designs (degf): %d\n", degf(des)))
cat(sprintf("R %s.%s, survey %s\n", R.version$major, R.version$minor, packageVersion("survey")))
anzeige <- werte
anzeige$wert <- signif(anzeige$wert, 6); anzeige$m <- signif(anzeige$m, 6)
print(anzeige, row.names = FALSE)

# SPEC-Formel gegen svyciprop(method = "beta"): größte Differenz der Grenzen
spec_ki <- werte[werte$groesse %in% c("KI_unten", "KI_oben"), ]
cip_ki  <- werte[werte$groesse %in% c("KI_unten_svyciprop_beta", "KI_oben_svyciprop_beta"), ]
cat(sprintf("Größte Differenz SPEC-Formel gegen svyciprop(beta): %.3g Prozentpunkte\n",
            max(abs(spec_ki$wert - cip_ki$wert))))
cat("Geschrieben: results/A/abend2_werte.csv\n")
