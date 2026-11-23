# A/01_download.R – Abend 1: NHANES-Dateien laden und prüfen (Auswerter A)
#
# Aufruf aus dem Wurzelverzeichnis des Repos:  Rscript A/01_download.R
#
# Was das Skript tut:
#   1. Lädt die vier .xpt-Dateien des Zyklus 2017–März 2020 nach data/raw/.
#   2. Bildet je Datei die SHA-256-Prüfsumme.
#        - Gibt es results/A/abend1_dateien.csv noch nicht (erster Lauf),
#          legt das Skript sie an.
#        - Gibt es sie schon (spätere Abende), vergleicht es jede Prüfsumme
#          mit dieser Datei und bricht bei der ersten Abweichung ab.
#   3. Liest jede Datei, zählt Zeilen und Spalten, prüft die Zeilenzahl gegen
#      die CDC-Dokumentation (SPEC.md, Abend 1) und die benötigten Variablen.
#   4. Schreibt data/raw/CHECKSUMS.txt (Regel 3 der Spezifikation).
#   5. Sichert die vier Dokumentationsseiten in docs/cdc/ mit Abrufdatum im
#      Dateinamen, sofern dort noch keine Fassung der Seite liegt.
#
# Benötigt: R, Pakete foreign (read.xport) und digest (SHA-256).
# Die Rohdateien werden nie verändert.

suppressPackageStartupMessages({
  library(foreign)
  library(digest)
})

if (!file.exists("SPEC.md")) {
  stop("Bitte aus dem Wurzelverzeichnis des Repos starten (SPEC.md fehlt).")
}

basis_url <- "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/"

dateien <- data.frame(
  datei      = c("P_DEMO", "P_BMX", "P_BIOPRO", "P_RXQ_RX"),
  zeilen_cdc = c(15560L, 14300L, 10409L, 32962L),
  stringsAsFactors = FALSE
)

benoetigt <- list(
  P_DEMO   = c("SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG",
               "WTMECPRP", "SDMVSTRA", "SDMVPSU"),
  P_BMX    = c("SEQN", "BMXWT", "BMXHT", "BMXBMI"),
  P_BIOPRO = c("SEQN", "LBXSCR"),
  P_RXQ_RX = c("SEQN", "RXDUSE", "RXDDRUG", "RXDDRGID", "RXDDAYS")
)

dir_raw  <- file.path("data", "raw")
dir_docs <- file.path("docs", "cdc")
dir_res  <- file.path("results", "A")
for (d in c(dir_raw, dir_docs, dir_res)) dir.create(d, recursive = TRUE, showWarnings = FALSE)

pfad_csv  <- file.path(dir_res, "abend1_dateien.csv")
erstlauf  <- !file.exists(pfad_csv)
referenz  <- if (erstlauf) NULL else
  read.csv(pfad_csv, stringsAsFactors = FALSE, colClasses = "character")

heute <- format(Sys.Date(), "%Y-%m-%d")
options(timeout = max(600, getOption("timeout")))

sha256_datei <- function(pfad) digest(pfad, algo = "sha256", file = TRUE)

laden <- function(url, ziel) {
  tmp <- paste0(ziel, ".part")
  status <- tryCatch(
    download.file(url, tmp, mode = "wb", quiet = TRUE),
    error = function(e) {
      stop("Download fehlgeschlagen: ", url, "\n", conditionMessage(e),
           "\nIst der Host gesperrt, bitte anhalten und den Hostnamen melden.",
           call. = FALSE)
    }
  )
  if (status != 0) stop("Download fehlgeschlagen (Status ", status, "): ", url, call. = FALSE)
  file.rename(tmp, ziel)
}

ergebnis <- vector("list", nrow(dateien))

for (i in seq_len(nrow(dateien))) {
  name  <- dateien$datei[i]
  url   <- paste0(basis_url, name, ".xpt")
  ziel  <- file.path(dir_raw, paste0(name, ".xpt"))

  # 1. Download (immer frisch, weil jede Cloud-Sitzung ohne Rohdaten startet;
  #    eine schon vorhandene Datei wird ebenfalls gegen die Prüfsumme geprüft)
  if (!file.exists(ziel)) {
    message("Lade ", url)
    laden(url, ziel)
  } else {
    message("Vorhanden: ", ziel)
  }

  # 2. Prüfsumme sofort nach dem Download
  sha <- sha256_datei(ziel)
  if (!erstlauf) {
    soll <- referenz$sha256[referenz$datei == name]
    if (length(soll) != 1) {
      stop("Keine Referenzprüfsumme für ", name, " in ", pfad_csv, call. = FALSE)
    }
    if (!identical(tolower(soll), tolower(sha))) {
      stop("PRÜFSUMME WEICHT AB für ", name, "\n  erwartet: ", soll,
           "\n  erhalten: ", sha,
           "\nAbbruch. Die Datei bei der CDC hat sich geändert oder der Download ist defekt.",
           call. = FALSE)
    }
    message("  SHA-256 stimmt mit ", pfad_csv, " überein.")
  }

  # 3. Lesen, Zeilen und Spalten zählen, Variablen prüfen
  df <- read.xport(ziel)
  fehlend <- setdiff(benoetigt[[name]], names(df))

  ergebnis[[i]] <- data.frame(
    datei              = name,
    url                = url,
    bytes              = file.size(ziel),
    sha256             = sha,
    zeilen             = nrow(df),
    zeilen_cdc         = dateien$zeilen_cdc[i],
    zeilen_ok          = nrow(df) == dateien$zeilen_cdc[i],
    spalten            = ncol(df),
    variablen_fehlend  = paste(fehlend, collapse = " "),
    abgerufen          = heute,
    r_version          = paste(R.version$major, R.version$minor, sep = "."),
    stringsAsFactors   = FALSE
  )
  message(sprintf("  %s: %d Zeilen (CDC %d), %d Spalten",
                  name, nrow(df), dateien$zeilen_cdc[i], ncol(df)))
  rm(df); invisible(gc())
}

tab <- do.call(rbind, ergebnis)

# 4. CHECKSUMS.txt im Format von sha256sum
writeLines(paste0(tab$sha256, "  ", tab$datei, ".xpt"),
           file.path(dir_raw, "CHECKSUMS.txt"))

# Ergebnisdatei nur beim ersten Lauf anlegen; später dient sie als Referenz
if (erstlauf) {
  write.csv(tab, pfad_csv, row.names = FALSE)
  message("Angelegt: ", pfad_csv)
}

# 5. Dokumentationsseiten sichern (nur wenn noch keine Fassung vorliegt)
for (name in dateien$datei) {
  vorhanden <- list.files(dir_docs, pattern = paste0("^", name, "_\\d{4}-\\d{2}-\\d{2}\\.htm$"))
  if (length(vorhanden) == 0) {
    url  <- paste0(basis_url, name, ".htm")
    ziel <- file.path(dir_docs, paste0(name, "_", heute, ".htm"))
    message("Sichere Dokumentation ", url)
    laden(url, ziel)
  }
}

# Abschlussprüfung
print(tab[, c("datei", "zeilen", "zeilen_cdc", "zeilen_ok", "spalten", "variablen_fehlend")],
      row.names = FALSE)

if (any(tab$variablen_fehlend != "")) {
  stop("Benötigte Variablen fehlen. Siehe Spalte variablen_fehlend.", call. = FALSE)
}
if (!all(tab$zeilen_ok)) {
  stop("Zeilenzahl weicht von der CDC-Dokumentation ab. Abend 1 nicht bestanden.", call. = FALSE)
}
message("Abend 1: alle vier Zeilenzahlen stimmen.")
