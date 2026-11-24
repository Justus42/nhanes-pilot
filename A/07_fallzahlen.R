# A/07_fallzahlen.R – Abend 4: Fallzahlen je Wirkstoff (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis des Repos:  Rscript A/07_fallzahlen.R
# Vorher: Rscript A/01_download.R (Rohdaten) und Rscript A/06_rechentests.R.
#
# Grundlage: SPEC.md Version 2.1, Abschnitt "Abend 4", mit den Antworten auf
# OFFEN.md, Fragen 4 bis 8 (24.11.2026), und der Lesart in LOG.md
# ("Abend 4, Phase 1, Zusatz: Lesart der Ausgabe").
#
# Ungewichtete Personenzahlen. Kein Survey-Design, keine Gewichte.
# Die Entscheidungsregel wendet dieses Skript nicht an.
#
# Ausgaben:
#   results/A/abend4_fallzahlen.csv     12 Zeilen x (zeile + 8 Zahlenspalten)
#   results/A/abend4_treffernamen.csv   jede RXDDRUG-Schreibweise mit Treffer,
#                                       Zahl der Trefferzeilen (RXDUSE = 1) je Ausgabezeile
#   data/work/abend4_personen_A.csv     eine Zeile je SEQN aus P_DEMO (nicht im Git)

suppressPackageStartupMessages({
  library(foreign)
  library(digest)
})

if (!file.exists("SPEC.md")) stop("Bitte aus dem Wurzelverzeichnis des Repos starten.")
source(file.path("A", "05_formeln.R"))

# ---------------------------------------------------------------------------
# 0. Rechentests müssen vorher bestanden sein (SPEC.md: Abbruch sonst)
# ---------------------------------------------------------------------------
pfad_tests <- file.path("results", "A", "abend4_rechentests.csv")
if (!file.exists(pfad_tests)) stop("Erst Rscript A/06_rechentests.R ausführen.", call. = FALSE)
rt <- read.csv(pfad_tests, stringsAsFactors = FALSE)
if (nrow(rt) == 0 || any(rt$urteil != "bestanden"))
  stop("Rechentests nicht bestanden. Abbruch vor dem Zählen.", call. = FALSE)

# ---------------------------------------------------------------------------
# 1. Rohdaten: Prüfsummen gegen Abend 1 (Regel 3), dann lesen
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

demo <- lese("P_DEMO",   c("SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG"))
bmx  <- lese("P_BMX",    c("SEQN", "BMXWT", "BMXHT"))
bio  <- lese("P_BIOPRO", c("SEQN", "LBXSCR"))
rx   <- lese("P_RXQ_RX", c("SEQN", "RXDUSE", "RXDDRUG"))

if (nrow(demo) != 15560) stop("P_DEMO hat ", nrow(demo), " statt 15560 Zeilen.", call. = FALSE)
for (nm in c("demo", "bmx", "bio")) {
  s <- get(nm)$SEQN
  if (anyNA(s) || anyDuplicated(s)) stop("SEQN in ", nm, " fehlt oder ist nicht eindeutig.", call. = FALSE)
}
if (any(demo$SEQN != round(demo$SEQN))) stop("SEQN in P_DEMO ist nicht ganzzahlig.", call. = FALSE)
if (anyNA(rx$SEQN)) stop("SEQN in P_RXQ_RX fehlt.", call. = FALSE)
rx_fremd <- sum(!(unique(rx$SEQN) %in% demo$SEQN))
message("P_RXQ_RX: ", nrow(rx), " Zeilen, ", length(unique(rx$SEQN)), " Personen, davon nicht in P_DEMO: ", rx_fremd)
if (rx_fremd > 0) stop("P_RXQ_RX enthält SEQN, die nicht in P_DEMO stehen.", call. = FALSE)

# ---------------------------------------------------------------------------
# 2. Personenebene: P_BMX und P_BIOPRO an P_DEMO anfügen, ohne Personen zu verlieren
# ---------------------------------------------------------------------------
p <- merge(demo, bmx, by = "SEQN", all.x = TRUE, sort = TRUE)
p <- merge(p,    bio, by = "SEQN", all.x = TRUE, sort = TRUE)
if (nrow(p) != nrow(demo) || !identical(p$SEQN, sort(demo$SEQN)))
  stop("Beim Anfügen hat sich die Personenmenge geändert.", call. = FALSE)

# ---------------------------------------------------------------------------
# 3. Analysegruppe (SPEC.md, Abend 4; Definitionen 1, 2, 7; OFFEN.md Frage 6)
#    Jede Bedingung als vollständige Ja/Nein-Maske ohne NA.
# ---------------------------------------------------------------------------
ja <- function(x) !is.na(x) & x
m_alter   <- ja(p$RIDAGEYR >= 18)
m_status  <- ja(p$RIDSTATR == 2)
m_sex     <- ja(p$RIAGENDR %in% c(1, 2))
m_schwang <- is.na(p$RIDEXPRG) | p$RIDEXPRG != 1          # Definition 1
m_scr     <- ja(p$LBXSCR > 0)
m_wt      <- ja(p$BMXWT  > 0)
m_ht      <- ja(p$BMXHT  > 0)
p$analysegruppe <- m_alter & m_status & m_sex & m_schwang & m_scr & m_wt & m_ht
stopifnot(!anyNA(p$analysegruppe))

stufen <- data.frame(
  bedingung = c("P_DEMO", "Alter >= 18", "RIDSTATR = 2", "RIAGENDR 1 oder 2",
                "ohne dokumentierte Schwangerschaft", "LBXSCR > 0", "BMXWT > 0", "BMXHT > 0"),
  personen = c(nrow(p), sum(m_alter), sum(m_alter & m_status), sum(m_alter & m_status & m_sex),
               sum(m_alter & m_status & m_sex & m_schwang),
               sum(m_alter & m_status & m_sex & m_schwang & m_scr),
               sum(m_alter & m_status & m_sex & m_schwang & m_scr & m_wt),
               sum(p$analysegruppe)))
message("Analysegruppe, kumulativ:")
print(stufen, row.names = FALSE)

# ---------------------------------------------------------------------------
# 4. Schätzer und Kategorien, nur für die Analysegruppe (ungerundet)
# ---------------------------------------------------------------------------
a <- p$analysegruppe
p$egfr_index <- NA_real_; p$kof <- NA_real_; p$egfr_deindex <- NA_real_; p$cg <- NA_real_
p$egfr_index[a]   <- ckd_epi_2021(p$LBXSCR[a], p$RIDAGEYR[a], p$RIAGENDR[a])
p$kof[a]          <- kof_dubois(p$BMXWT[a], p$BMXHT[a])
p$egfr_deindex[a] <- ckd_epi_deindex(p$egfr_index[a], p$kof[a])
p$cg[a]           <- cockcroft_gault(p$RIDAGEYR[a], p$BMXWT[a], p$LBXSCR[a], p$RIAGENDR[a])
p$kat_ckdepi <- NA_character_; p$kat_deindex <- NA_character_; p$kat_cg <- NA_character_
p$kat_ckdepi[a]  <- kategorie(p$egfr_index[a])
p$kat_deindex[a] <- kategorie(p$egfr_deindex[a])
p$kat_cg[a]      <- kategorie(p$cg[a])

# ---------------------------------------------------------------------------
# 5. Treffer je Medikamentenzeile, dann Oder je Person (SPEC.md, "Wirkstoffnutzer")
# ---------------------------------------------------------------------------
suchbegriffe <- list(
  METFORMIN      = "METFORMIN",
  GABAPENTIN     = "GABAPENTIN",
  PREGABALIN     = "PREGABALIN",
  DOAK_GESAMT    = c("APIXABAN", "RIVAROXABAN", "DABIGATRAN", "EDOXABAN"),
  ALLOPURINOL    = "ALLOPURINOL",
  SITAGLIPTIN    = "SITAGLIPTIN",
  SPIRONOLACTONE = "SPIRONOLACTONE",
  APIXABAN       = "APIXABAN",
  RIVAROXABAN    = "RIVAROXABAN",
  DABIGATRAN     = "DABIGATRAN",
  EDOXABAN       = "EDOXABAN"
)
rx_use <- ja(rx$RXDUSE == 1)
namen_tab <- list()
for (z in names(suchbegriffe)) {
  treffer_zeile <- rx_use & name_trifft(rx$RXDDRUG, suchbegriffe[[z]])
  seqn_treffer  <- unique(rx$SEQN[treffer_zeile])
  # 1/0 für die Analysegruppe, leer (NA) für alle anderen
  p[[z]] <- ifelse(a, as.integer(p$SEQN %in% seqn_treffer), NA_integer_)
  if (any(treffer_zeile)) {
    tb <- table(trimws(as.character(rx$RXDDRUG[treffer_zeile])))
    namen_tab[[z]] <- data.frame(zeile = z, rxddrug = names(tb),
                                 trefferzeilen = as.integer(tb), stringsAsFactors = FALSE)
  }
}

# ---------------------------------------------------------------------------
# 6. Fallzahlen je Ausgabezeile
# ---------------------------------------------------------------------------
zeilen <- c(names(suchbegriffe)[1:7], names(suchbegriffe)[8:11], "GESAMT")
zaehle <- function(menge) {
  u_ck <- p$egfr_index[menge]   < 60
  u_de <- p$egfr_deindex[menge] < 60
  u_cg <- p$cg[menge]           < 60
  c(n_personen              = sum(menge),
    n_ckdepi_u60            = sum(u_ck),
    n_deindex_u60           = sum(u_de),
    n_cg_u60                = sum(u_cg),
    n_irgendeine_u60        = sum(u_ck | u_de | u_cg),
    n_diskordant_cg_ckdepi  = sum(p$kat_cg[menge] != p$kat_ckdepi[menge]),
    n_diskordant_cg_deindex = sum(p$kat_cg[menge] != p$kat_deindex[menge]),
    n_alter_80              = sum(p$RIDAGEYR[menge] == 80))
}
erg <- do.call(rbind, lapply(zeilen, function(z) {
  menge <- if (z == "GESAMT") a else (a & !is.na(p[[z]]) & p[[z]] == 1L)
  zaehle(menge)
}))
erg <- data.frame(zeile = zeilen, erg, stringsAsFactors = FALSE, row.names = NULL)
for (s in names(erg)[-1]) erg[[s]] <- as.integer(erg[[s]])

# ---------------------------------------------------------------------------
# 7. Plausibilitätsprüfungen (LOG.md, Lesart der Ausgabe); Abbruch bei Verstoß
# ---------------------------------------------------------------------------
if (anyNA(erg)) stop("Fehlender Wert in den Fallzahlen.", call. = FALSE)
for (s in names(erg)[3:9])
  if (any(erg[[s]] > erg$n_personen)) stop("Spalte ", s, " größer als n_personen.", call. = FALSE)
u3 <- erg[, c("n_ckdepi_u60", "n_deindex_u60", "n_cg_u60")]
if (any(erg$n_irgendeine_u60 < apply(u3, 1, max)) || any(erg$n_irgendeine_u60 > rowSums(u3)))
  stop("n_irgendeine_u60 außerhalb [Maximum, Summe] der drei Einzelspalten.", call. = FALSE)
doak <- erg[erg$zeile %in% c("APIXABAN", "RIVAROXABAN", "DABIGATRAN", "EDOXABAN"), "n_personen"]
n_doak <- erg$n_personen[erg$zeile == "DOAK_GESAMT"]
if (n_doak < max(doak) || n_doak > sum(doak)) stop("DOAK_GESAMT außerhalb [Maximum, Summe] der Einzel-DOAK.", call. = FALSE)
if (erg$n_personen[erg$zeile == "GESAMT"] != sum(a)) stop("GESAMT ungleich Analysegruppe.", call. = FALSE)
doak_oder <- with(p, (APIXABAN == 1L | RIVAROXABAN == 1L | DABIGATRAN == 1L | EDOXABAN == 1L))
if (!identical(as.integer(doak_oder[a]), p$DOAK_GESAMT[a]))
  stop("DOAK_GESAMT ist nicht das Oder der vier Einzel-DOAK.", call. = FALSE)
if (any(!a & !is.na(p$kat_cg)) || any(a & is.na(p$kat_cg)))
  stop("Kategorien nicht genau für die Analysegruppe gefüllt.", call. = FALSE)

# ---------------------------------------------------------------------------
# 8. Schreiben
# ---------------------------------------------------------------------------
schreibe <- function(df, pfad) {
  write.table(df, pfad, sep = ",", quote = FALSE, row.names = FALSE, na = "", eol = "\n",
              fileEncoding = "UTF-8")
}
dir.create(file.path("results", "A"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path("data", "work"), recursive = TRUE, showWarnings = FALSE)

schreibe(erg, file.path("results", "A", "abend4_fallzahlen.csv"))

namen <- do.call(rbind, namen_tab)
namen <- namen[order(match(namen$zeile, zeilen), namen$rxddrug), ]
if (any(grepl(",", namen$rxddrug))) stop("Komma in RXDDRUG, CSV ohne Anführungszeichen nicht möglich.")
schreibe(namen, file.path("results", "A", "abend4_treffernamen.csv"))

personen <- data.frame(SEQN = sprintf("%d", as.integer(p$SEQN)),
                       analysegruppe = as.integer(p$analysegruppe),
                       stringsAsFactors = FALSE)
for (z in names(suchbegriffe)) personen[[z]] <- p[[z]]
personen$kat_ckdepi  <- p$kat_ckdepi
personen$kat_deindex <- p$kat_deindex
personen$kat_cg      <- p$kat_cg
if (nrow(personen) != 15560 || is.unsorted(as.integer(personen$SEQN), strictly = TRUE))
  stop("Personendatei: nicht 15560 Zeilen oder nicht streng aufsteigend nach SEQN.", call. = FALSE)
schreibe(personen, file.path("data", "work", "abend4_personen_A.csv"))

print(erg, row.names = FALSE)
message("Geschrieben: results/A/abend4_fallzahlen.csv, results/A/abend4_treffernamen.csv, ",
        "data/work/abend4_personen_A.csv")
