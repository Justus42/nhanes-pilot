#!/usr/bin/env python3
"""Auswerter B – Abend 4: Ungewichtete Fallzahlen je Wirkstoff und Nierenfunktion.

Spezifikation: SPEC.md (Version 2.1 vom 24.11.2026), Repo Justus42/nhanes-pilot.
Abhängigkeiten: ausschließlich Standardbibliothek, numpy und pandas.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# Erwartete Zeilenzahlen laut CDC-Dokumentation (SPEC.md, Abend 1)
EXPECTED_ROWS: dict[str, int] = {
    "P_DEMO.xpt": 15_560,
    "P_BMX.xpt": 14_300,
    "P_BIOPRO.xpt": 10_409,
    "P_RXQ_RX.xpt": 32_962,
}

# Benötigte Variablen je Rohdatei (SPEC.md, Abend 1 & 4)
REQUIRED_COLS: dict[str, list[str]] = {
    "P_DEMO.xpt": ["SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG"],
    "P_BMX.xpt": ["SEQN", "BMXWT", "BMXHT"],
    "P_BIOPRO.xpt": ["SEQN", "LBXSCR"],
    "P_RXQ_RX.xpt": ["SEQN", "RXDUSE", "RXDDRUG"],
}

# Suchbegriffe je Wirkstoffzeile (SPEC.md, Abend 4)
DRUG_SEARCH_TERMS: dict[str, set[str]] = {
    "METFORMIN": {"METFORMIN"},
    "GABAPENTIN": {"GABAPENTIN"},
    "PREGABALIN": {"PREGABALIN"},
    "DOAK_GESAMT": {"APIXABAN", "RIVAROXABAN", "DABIGATRAN", "EDOXABAN"},
    "ALLOPURINOL": {"ALLOPURINOL"},
    "SITAGLIPTIN": {"SITAGLIPTIN"},
    "SPIRONOLACTONE": {"SPIRONOLACTONE"},
    "APIXABAN": {"APIXABAN"},
    "RIVAROXABAN": {"RIVAROXABAN"},
    "DABIGATRAN": {"DABIGATRAN"},
    "EDOXABAN": {"EDOXABAN"},
}

DRUG_COLUMN_ORDER: list[str] = list(DRUG_SEARCH_TERMS.keys())
FALLZAHLEN_ROW_ORDER: list[str] = DRUG_COLUMN_ORDER + ["GESAMT"]

EXCLUDED_DRUG_CODES: set[str] = {"55555", "77777", "99999"}
TOKEN_PATTERN: re.Pattern[str] = re.compile(r"[A-Z0-9]+")


# ---------------------------------------------------------------------------
# Formeln für Nierenfunktion und Körperoberfläche (SPEC.md, Abend 4)
# ---------------------------------------------------------------------------

def calc_ckdepi_2021_indexed(
    scr_mg_dl: np.ndarray | float,
    age_yr: np.ndarray | float,
    is_female: np.ndarray | bool,
) -> np.ndarray:
    """CKD-EPI 2021 (ohne Rasse), indexiert in ml/min/1,73 m² (Inker et al., NEJM 2021)."""
    scr = np.asarray(scr_mg_dl, dtype=np.float64)
    age = np.asarray(age_yr, dtype=np.float64)
    female = np.asarray(is_female, dtype=bool)

    kappa = np.where(female, 0.7, 0.9)
    alpha = np.where(female, -0.241, -0.302)
    sex_factor = np.where(female, 1.012, 1.0)

    ratio = scr / kappa
    return (
        142.0
        * np.power(np.minimum(ratio, 1.0), alpha)
        * np.power(np.maximum(ratio, 1.0), -1.200)
        * np.power(0.9938, age)
        * sex_factor
    )


def calc_bsa_dubois(
    weight_kg: np.ndarray | float,
    height_cm: np.ndarray | float,
) -> np.ndarray:
    """Körperoberfläche nach DuBois in m² (Du Bois & Du Bois, 1916)."""
    weight = np.asarray(weight_kg, dtype=np.float64)
    height = np.asarray(height_cm, dtype=np.float64)
    return 0.007184 * np.power(weight, 0.425) * np.power(height, 0.725)


def calc_ckdepi_2021_deindexed(
    scr_mg_dl: np.ndarray | float,
    age_yr: np.ndarray | float,
    is_female: np.ndarray | bool,
    weight_kg: np.ndarray | float,
    height_cm: np.ndarray | float,
) -> np.ndarray:
    """CKD-EPI 2021 de-indexiert in ml/min."""
    indexed = calc_ckdepi_2021_indexed(scr_mg_dl, age_yr, is_female)
    bsa = calc_bsa_dubois(weight_kg, height_cm)
    return indexed * bsa / 1.73


def calc_cockcroft_gault(
    scr_mg_dl: np.ndarray | float,
    age_yr: np.ndarray | float,
    weight_kg: np.ndarray | float,
    is_female: np.ndarray | bool,
) -> np.ndarray:
    """Cockcroft-Gault in ml/min mit tatsächlichem Körpergewicht (Cockcroft & Gault, 1976)."""
    scr = np.asarray(scr_mg_dl, dtype=np.float64)
    age = np.asarray(age_yr, dtype=np.float64)
    weight = np.asarray(weight_kg, dtype=np.float64)
    female = np.asarray(is_female, dtype=bool)

    sex_factor = np.where(female, 0.85, 1.0)
    return ((140.0 - age) * weight / (72.0 * scr)) * sex_factor


def categorize_egfr(values: np.ndarray) -> np.ndarray:
    """Ordnet ungerundete Werte den Kategorien u30, 30_45, 45_60, ab60 zu."""
    arr = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError("Nicht-finite Werte bei der Kategorisierung der Nierenfunktion.")
    return np.select(
        [arr < 30.0, arr < 45.0, arr < 60.0],
        ["u30", "30_45", "45_60"],
        default="ab60",
    )


def run_formula_tests() -> None:
    """Prüft alle neun Rechentests aus SPEC.md vor dem Laden und Zählen."""
    tests: list[tuple[str, float, float, float]] = [
        (
            "Mann, 60 J, 72 kg, Kreatinin 1,0: Cockcroft-Gault",
            float(calc_cockcroft_gault(1.0, 60.0, 72.0, False)),
            80.00,
            0.01,
        ),
        (
            "Frau, 60 J, 72 kg, Kreatinin 1,0: Cockcroft-Gault",
            float(calc_cockcroft_gault(1.0, 60.0, 72.0, True)),
            68.00,
            0.01,
        ),
        (
            "Mann, 60 J, Kreatinin 0,9: CKD-EPI indexiert",
            float(calc_ckdepi_2021_indexed(0.9, 60.0, False)),
            97.78,
            0.01,
        ),
        (
            "Frau, 60 J, Kreatinin 0,7: CKD-EPI indexiert",
            float(calc_ckdepi_2021_indexed(0.7, 60.0, True)),
            98.95,
            0.01,
        ),
        (
            "Mann, 60 J, Kreatinin 1,8: CKD-EPI indexiert",
            float(calc_ckdepi_2021_indexed(1.8, 60.0, False)),
            42.56,
            0.01,
        ),
        (
            "Mann, 60 J, Kreatinin 0,45: CKD-EPI indexiert",
            float(calc_ckdepi_2021_indexed(0.45, 60.0, False)),
            120.54,
            0.01,
        ),
        (
            "Frau, 60 J, Kreatinin 0,35: CKD-EPI indexiert",
            float(calc_ckdepi_2021_indexed(0.35, 60.0, True)),
            116.94,
            0.01,
        ),
        (
            "72 kg, 175 cm: Körperoberfläche (DuBois)",
            float(calc_bsa_dubois(72.0, 175.0)),
            1.8704,
            0.0001,
        ),
        (
            "Mann, 60 J, 72 kg, 175 cm, Kreatinin 1,8: CKD-EPI de-indexiert",
            float(calc_ckdepi_2021_deindexed(1.8, 60.0, False, 72.0, 175.0)),
            46.01,
            0.01,
        ),
    ]

    failures: list[str] = []
    for label, actual, expected, tol in tests:
        diff = abs(actual - expected)
        if not np.isfinite(actual) or diff > tol:
            failures.append(
                f"  - {label}: erhalten={actual:.6f}, erwartet={expected}, "
                f"Abweichung={diff:.6f} > Toleranz={tol}"
            )

    if failures:
        raise RuntimeError(
            "Rechentests fehlgeschlagen – Abbruch vor dem Zählen:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# Laden, Prüfen und Aufbereiten der XPT-Rohdaten
# ---------------------------------------------------------------------------

def resolve_repo_root() -> Path:
    """Ermittelt das Repo-Wurzelverzeichnis robust (unabhängig vom Aufrufort)."""
    script_root = Path(__file__).resolve().parent.parent
    if (script_root / "data" / "raw").is_dir():
        return script_root
    cwd_root = Path.cwd()
    if (cwd_root / "data" / "raw").is_dir():
        return cwd_root
    raise FileNotFoundError(
        "Verzeichnis 'data/raw/' nicht gefunden "
        f"(gesucht unter '{script_root}' und '{cwd_root}')."
    )


def load_xpt_checked(raw_dir: Path, filename: str) -> pd.DataFrame:
    """Lädt eine NHANES-.xpt-Datei und prüft Zeilenzahl sowie Pflichtspalten."""
    path = raw_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"Rohdatei fehlt: {path}")

    df = pd.read_sas(path, format="xport")

    expected_rows = EXPECTED_ROWS[filename]
    if len(df) != expected_rows:
        raise ValueError(
            f"Unerwartete Zeilenzahl in {filename}: "
            f"erhalten {len(df)}, erwartet exakt {expected_rows}."
        )

    missing_cols = [col for col in REQUIRED_COLS[filename] if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Fehlende Spalten in {filename}: {', '.join(missing_cols)}"
        )

    return df


def sanitize_sas_zeros(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    """Korrigiert mögliche SAS-XPORT-Nullwerte (~5.3976e-79) auf 0.0, erhält NaN."""
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="raise")
        df[col] = series.where(series.isna() | (series.abs() >= 1e-50), 0.0)
    return df


def normalize_seqn(df: pd.DataFrame, filename: str, require_unique: bool) -> pd.DataFrame:
    """Prüft SEQN auf Vollständigkeit, Ganzzahligkeit und ggf. Eindeutigkeit."""
    seqn = pd.to_numeric(df["SEQN"], errors="raise")
    if seqn.isna().any():
        raise ValueError(f"{filename}: Fehlende Werte in SEQN gefunden.")
    if not np.all(np.isfinite(seqn)) or not np.all(np.mod(seqn, 1.0) == 0.0):
        raise ValueError(f"{filename}: Nicht-ganzzahlige Werte in SEQN gefunden.")
    df["SEQN"] = seqn.astype(np.int64)
    if require_unique and not df["SEQN"].is_unique:
        n_dups = int(df["SEQN"].duplicated().sum())
        raise ValueError(f"{filename}: {n_dups} doppelte SEQN gefunden.")
    return df


def extract_drug_tokens(raw_value: object) -> set[str]:
    """Dekodiert RXDDRUG (falls Bytes), trimmt, wandelt in Großbuchstaben und zerlegt in [A-Z0-9]+."""
    if raw_value is None:
        return set()
    if isinstance(raw_value, (bytes, bytearray)):
        try:
            text = raw_value.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_value.decode("latin-1")
    elif isinstance(raw_value, str):
        text = raw_value
    else:
        if pd.isna(raw_value):
            return set()
        text = str(raw_value)

    cleaned = text.strip().upper()
    if not cleaned or cleaned in EXCLUDED_DRUG_CODES:
        return set()
    return set(TOKEN_PATTERN.findall(cleaned))


def collect_drug_hit_seqns(rx_df: pd.DataFrame) -> dict[str, set[int]]:
    """Aggregiert P_RXQ_RX auf Personenebene (Treffer-SEQN je Wirkstoffgruppe)."""
    rx_use_mask = rx_df["RXDUSE"].notna() & (rx_df["RXDUSE"] == 1)
    rx_active = rx_df.loc[rx_use_mask, ["SEQN", "RXDDRUG"]]

    hit_seqns: dict[str, set[int]] = {name: set() for name in DRUG_COLUMN_ORDER}

    for seqn, raw_drug in zip(rx_active["SEQN"], rx_active["RXDDRUG"]):
        tokens = extract_drug_tokens(raw_drug)
        if not tokens:
            continue
        seqn_int = int(seqn)
        for drug_name, search_terms in DRUG_SEARCH_TERMS.items():
            if tokens & search_terms:
                hit_seqns[drug_name].add(seqn_int)

    return hit_seqns


# ---------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Rechentests vor dem Zählen
    run_formula_tests()

    # 2. Pfade prüfen und Rohdaten laden
    repo_root = resolve_repo_root()
    raw_dir = repo_root / "data" / "raw"

    demo = load_xpt_checked(raw_dir, "P_DEMO.xpt")
    bmx = load_xpt_checked(raw_dir, "P_BMX.xpt")
    biopro = load_xpt_checked(raw_dir, "P_BIOPRO.xpt")
    rx = load_xpt_checked(raw_dir, "P_RXQ_RX.xpt")

    demo = sanitize_sas_zeros(demo, ["SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG"])
    bmx = sanitize_sas_zeros(bmx, ["SEQN", "BMXWT", "BMXHT"])
    biopro = sanitize_sas_zeros(biopro, ["SEQN", "LBXSCR"])
    rx = sanitize_sas_zeros(rx, ["SEQN", "RXDUSE"])

    demo = normalize_seqn(demo, "P_DEMO.xpt", require_unique=True)
    bmx = normalize_seqn(bmx, "P_BMX.xpt", require_unique=True)
    biopro = normalize_seqn(biopro, "P_BIOPRO.xpt", require_unique=True)
    rx = normalize_seqn(rx, "P_RXQ_RX.xpt", require_unique=False)

    # Konsistenzprüfung: alle SEQN der Nebendateien müssen in P_DEMO vorkommen
    demo_seqns = set(demo["SEQN"])
    for fname, sub_df in [("P_BMX.xpt", bmx), ("P_BIOPRO.xpt", biopro), ("P_RXQ_RX.xpt", rx)]:
        unknown_seqns = set(sub_df["SEQN"]) - demo_seqns
        if unknown_seqns:
            raise ValueError(
                f"{fname}: {len(unknown_seqns)} SEQN kommen nicht in P_DEMO.xpt vor."
            )

    # 3. Personenebene zusammenführen (alle 15.560 SEQN aus P_DEMO erhalten, sortiert nach SEQN)
    merged = (
        demo[["SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "RIDEXPRG"]]
        .merge(bmx[["SEQN", "BMXWT", "BMXHT"]], on="SEQN", how="left", validate="one_to_one")
        .merge(biopro[["SEQN", "LBXSCR"]], on="SEQN", how="left", validate="one_to_one")
        .sort_values("SEQN", kind="mergesort")
        .reset_index(drop=True)
    )
    if len(merged) != EXPECTED_ROWS["P_DEMO.xpt"]:
        raise RuntimeError(
            f"Zeilenzahl nach Merge unerwartet: {len(merged)} != {EXPECTED_ROWS['P_DEMO.xpt']}."
        )

    # 4. Analysegruppe (Abend 4, Definitionen 1–3 und 7; kein Gewichtskriterium)
    mask_age = merged["RIDAGEYR"].notna() & (merged["RIDAGEYR"] >= 18)
    mask_stat = merged["RIDSTATR"].notna() & (merged["RIDSTATR"] == 2)
    mask_sex = merged["RIAGENDR"].notna() & merged["RIAGENDR"].isin([1, 2])
    mask_not_preg = merged["RIDEXPRG"].isna() | (merged["RIDEXPRG"] != 1)
    mask_scr = merged["LBXSCR"].notna() & (merged["LBXSCR"] > 0)
    mask_wt = merged["BMXWT"].notna() & (merged["BMXWT"] > 0)
    mask_ht = merged["BMXHT"].notna() & (merged["BMXHT"] > 0)

    in_analysis = (
        mask_age
        & mask_stat
        & mask_sex
        & mask_not_preg
        & mask_scr
        & mask_wt
        & mask_ht
    )

    if int(in_analysis.sum()) == 0:
        raise RuntimeError("Analysegruppe ist leer – unerwarteter Datenzustand.")

    # 5. Wirkstofftreffer je Person aus P_RXQ_RX (erst nach Bildung der Analysegruppe anfügen)
    drug_hit_seqns = collect_drug_hit_seqns(rx)

    # 6. Nierenfunktionsschätzer und Kategorien für die Analysegruppe
    ana = merged.loc[in_analysis, ["SEQN", "RIDAGEYR", "RIAGENDR", "LBXSCR", "BMXWT", "BMXHT"]].copy()
    is_female = (ana["RIAGENDR"] == 2).to_numpy(dtype=bool)
    scr = ana["LBXSCR"].to_numpy(dtype=np.float64)
    age = ana["RIDAGEYR"].to_numpy(dtype=np.float64)
    weight = ana["BMXWT"].to_numpy(dtype=np.float64)
    height = ana["BMXHT"].to_numpy(dtype=np.float64)

    ckdepi = calc_ckdepi_2021_indexed(scr, age, is_female)
    deindex = calc_ckdepi_2021_deindexed(scr, age, is_female, weight, height)
    cg = calc_cockcroft_gault(scr, age, weight, is_female)

    for label, arr in [("ckdepi", ckdepi), ("deindex", deindex), ("cg", cg)]:
        if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
            raise RuntimeError(f"Ungültige oder nicht-positive Werte in {label} berechnet.")

    kat_ckdepi = categorize_egfr(ckdepi)
    kat_deindex = categorize_egfr(deindex)
    kat_cg = categorize_egfr(cg)

    ana["ckdepi"] = ckdepi
    ana["deindex"] = deindex
    ana["cg"] = cg
    ana["kat_ckdepi"] = kat_ckdepi
    ana["kat_deindex"] = kat_deindex
    ana["kat_cg"] = kat_cg

    for drug_name in DRUG_COLUMN_ORDER:
        ana[drug_name] = ana["SEQN"].isin(drug_hit_seqns[drug_name])

    # Plausibilitätsprüfung: DOAK_GESAMT muss exakt die Vereinigung der 4 Einzel-DOAK sein
    doak_union = ana["APIXABAN"] | ana["RIVAROXABAN"] | ana["DABIGATRAN"] | ana["EDOXABAN"]
    if not (ana["DOAK_GESAMT"] == doak_union).all():
        raise RuntimeError("Interner Konsistenzfehler: DOAK_GESAMT != Vereinigung der Einzel-DOAK.")

    # 7. Ausgabe 1: results/B/abend4_fallzahlen.csv
    rows: list[dict[str, object]] = []
    for row_name in FALLZAHLEN_ROW_ORDER:
        sub = ana if row_name == "GESAMT" else ana.loc[ana[row_name]]

        u60_ckdepi = sub["ckdepi"] < 60.0
        u60_deindex = sub["deindex"] < 60.0
        u60_cg = sub["cg"] < 60.0

        rows.append(
            {
                "wirkstoff": row_name,
                "n_personen": int(len(sub)),
                "n_ckdepi_u60": int(u60_ckdepi.sum()),
                "n_deindex_u60": int(u60_deindex.sum()),
                "n_cg_u60": int(u60_cg.sum()),
                "n_irgendeine_u60": int((u60_ckdepi | u60_deindex | u60_cg).sum()),
                "n_diskordant_cg_ckdepi": int((sub["kat_cg"] != sub["kat_ckdepi"]).sum()),
                "n_diskordant_cg_deindex": int((sub["kat_cg"] != sub["kat_deindex"]).sum()),
                "n_alter_80": int((sub["RIDAGEYR"] == 80).sum()),
            }
        )

    fallzahlen_df = pd.DataFrame(rows)

    # 8. Ausgabe 2: data/work/abend4_personen_B.csv (alle 15.560 SEQN aus P_DEMO)
    personen_df = pd.DataFrame({"SEQN": merged["SEQN"]})
    personen_df["analysegruppe"] = in_analysis.to_numpy(dtype=np.int64)

    for drug_name in DRUG_COLUMN_ORDER:
        hits_all = merged["SEQN"].isin(drug_hit_seqns[drug_name]).to_numpy(dtype=np.int64)
        personen_df[drug_name] = pd.Series(
            hits_all, index=merged.index, dtype="Int64"
        ).where(in_analysis, pd.NA)

    for kat_col, kat_vals in [
        ("kat_ckdepi", kat_ckdepi),
        ("kat_deindex", kat_deindex),
        ("kat_cg", kat_cg),
    ]:
        series = pd.Series(pd.NA, index=merged.index, dtype="object")
        series.loc[in_analysis] = kat_vals
        personen_df[kat_col] = series

    # Endprüfung der Personendatei vor dem Schreiben
    if len(personen_df) != EXPECTED_ROWS["P_DEMO.xpt"]:
        raise RuntimeError("Personendatei hat nicht exakt 15.560 Zeilen.")
    if not personen_df["SEQN"].is_monotonic_increasing or not personen_df["SEQN"].is_unique:
        raise RuntimeError("Personendatei ist nicht eindeutig aufsteigend nach SEQN sortiert.")
    if personen_df.loc[in_analysis, DRUG_COLUMN_ORDER + ["kat_ckdepi", "kat_deindex", "kat_cg"]].isna().any().any():
        raise RuntimeError("Unerwartete fehlende Werte innerhalb der Analysegruppe.")
    if personen_df.loc[~in_analysis, DRUG_COLUMN_ORDER + ["kat_ckdepi", "kat_deindex", "kat_cg"]].notna().any().any():
        raise RuntimeError("Unerwartete belegte Werte außerhalb der Analysegruppe.")

    # 9. Dateien schreiben
    out_fallzahlen = repo_root / "results" / "B" / "abend4_fallzahlen.csv"
    out_personen = repo_root / "data" / "work" / "abend4_personen_B.csv"
    out_fallzahlen.parent.mkdir(parents=True, exist_ok=True)
    out_personen.parent.mkdir(parents=True, exist_ok=True)

    fallzahlen_df.to_csv(out_fallzahlen, index=False, na_rep="")
    personen_df.to_csv(out_personen, index=False, na_rep="")

    print("Rechentests: alle 9 bestanden.")
    print(f"Analysegruppe: {int(in_analysis.sum())} von {len(merged)} Personen.")
    print(f"Geschrieben: {out_fallzahlen}")
    print(f"Geschrieben: {out_personen}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FEHLER in B/fallzahlen.py: {exc}", file=sys.stderr)
        sys.exit(1)
