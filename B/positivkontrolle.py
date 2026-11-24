#!/usr/bin/env python3
"""
Auswerter B – Positivkontrolle (Stufen 1, 2 und 4) gemäß SPEC.md (Version 2.1).

Berechnet aus den NHANES-Rohdaten 2017–März 2020 (P_DEMO.xpt, P_BMX.xpt):
- Stufe 1: Ungewichtete Fallzahlen der Analysegruppe (Gesamt, Männer, Frauen)
- Stufe 2: Rohe Prävalenzen (%) und Standardfehler (Prozentpunkte) per Taylor-Linearisierung
- Stufe 4: Altersadjustierte Prävalenzen (%) und Standardfehler (Prozentpunkte)

Verwendet ausschließlich Python-Standardbibliothek, numpy und pandas (keine Survey-Bibliothek).
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


EXPECTED_ROWS_DEMO = 15560
EXPECTED_ROWS_BMX = 14300

REQUIRED_COLS_DEMO = [
    "SEQN",
    "RIDSTATR",
    "RIDAGEYR",
    "RIAGENDR",
    "RIDEXPRG",
    "WTMECPRP",
    "SDMVSTRA",
    "SDMVPSU",
]
REQUIRED_COLS_BMX = [
    "SEQN",
    "BMXWT",
    "BMXHT",
    "BMXBMI",
]

# Feste Standardanteile der projizierten US-Bevölkerung 2000 (Altersverteilung Nr. 12)
AGE_STD_WEIGHTS = [
    ("20-39", 20, 39, 0.396579),
    ("40-59", 40, 59, 0.371795),
    ("60+", 60, None, 0.231626),
]

# Schwelle zur Bereinigung von SAS-XPT-Nullartefakten (z. B. 5.3976e-79 in pandas.read_sas)
SAS_XPT_ZERO_TOL = 1e-50


def resolve_repo_root() -> Path:
    """Ermittelt das Repo-Wurzelverzeichnis anhand des Ordners data/raw/."""
    cwd = Path.cwd()
    if (cwd / "data" / "raw").is_dir():
        return cwd

    script_parent_root = Path(__file__).resolve().parent.parent
    if (script_parent_root / "data" / "raw").is_dir():
        return script_parent_root

    raise FileNotFoundError(
        "Verzeichnis 'data/raw/' wurde weder im aktuellen Arbeitsverzeichnis "
        f"({cwd}) noch relativ zum Skript ({script_parent_root}) gefunden."
    )


def decode_bytes_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Dekodiert etwaige Bytes-Werte in Text-/Object-Spalten nach UTF-8 (Fallback latin-1)."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            has_bytes = df[col].map(lambda v: isinstance(v, (bytes, bytearray))).any()
            if has_bytes:
                def _decode(val):
                    if isinstance(val, (bytes, bytearray)):
                        try:
                            return val.decode("utf-8")
                        except UnicodeDecodeError:
                            return val.decode("latin-1")
                    return val

                df[col] = df[col].map(_decode)
    return df


def clean_sas_xpt_zeros(
    df: pd.DataFrame,
    numeric_cols: list[str],
    file_label: str,
) -> pd.DataFrame:
    """Prüft numerische Spalten und setzt SAS-XPT-Nullartefakte (< 1e-50) auf exakt 0.0."""
    df = df.copy()
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(
                f"{file_label}: Spalte '{col}' ist nicht numerisch (dtype={df[col].dtype})."
            )
        vals = df[col].to_numpy(dtype=np.float64, copy=True)
        near_zero = np.isfinite(vals) & (vals != 0.0) & (np.abs(vals) < SAS_XPT_ZERO_TOL)
        n_fixed = int(near_zero.sum())
        if n_fixed > 0:
            vals[near_zero] = 0.0
            df[col] = vals
            print(
                f"[Hinweis] {file_label}: {n_fixed} SAS-XPT-Nullartefakte "
                f"(|x| < {SAS_XPT_ZERO_TOL:.0e}) in Spalte '{col}' auf 0.0 gesetzt."
            )
    return df


def to_exact_int64(series: pd.Series, col_name: str, context: str) -> np.ndarray:
    """Konvertiert eine numerische Spalte nach strenger Ganzzahligkeitsprüfung in int64."""
    vals = series.to_numpy(dtype=np.float64)
    if not np.isfinite(vals).all():
        raise ValueError(f"{context}: Fehlende oder nicht-endliche Werte in '{col_name}'.")
    rounded = np.rint(vals)
    if not np.all(np.abs(vals - rounded) < 1e-9):
        raise ValueError(f"{context}: Nicht-ganzzahlige Werte in '{col_name}' gefunden.")
    return rounded.astype(np.int64)


def load_xpt(
    filepath: Path,
    expected_rows: int,
    required_cols: list[str],
) -> pd.DataFrame:
    """Lädt eine SAS-XPT-Datei und prüft Existenz, Zeilenzahl, Spalten und SEQN-Eindeutigkeit."""
    if not filepath.is_file():
        raise FileNotFoundError(f"Benötigte Rohdatei nicht gefunden: {filepath}")

    df = pd.read_sas(filepath, format="xport")
    df = decode_bytes_columns(df)

    if len(df) != expected_rows:
        raise ValueError(
            f"Unerwartete Zeilenzahl in {filepath.name}: "
            f"erwartet {expected_rows}, gefunden {len(df)}."
        )

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Fehlende Spalten in {filepath.name}: {missing_cols}. "
            f"Vorhandene Spalten (erste 20): {list(df.columns)[:20]}"
        )

    df = clean_sas_xpt_zeros(df, required_cols, filepath.name)
    df["SEQN"] = to_exact_int64(df["SEQN"], "SEQN", filepath.name)

    if df["SEQN"].duplicated().any():
        n_dup = int(df["SEQN"].duplicated().sum())
        raise ValueError(f"{filepath.name}: {n_dup} doppelte SEQN-Werte gefunden.")

    return df


def prepare_design_structure(
    strata: np.ndarray,
    psus: np.ndarray,
) -> tuple[np.ndarray, int, list[tuple[int, np.ndarray]]]:
    """
    Erzeugt die vollständige Liste aller Cluster (SDMVSTRA, SDMVPSU) aus der Designbasis.
    Bricht ab, falls ein Stratum weniger als zwei Cluster besitzt.
    """
    pairs_df = pd.DataFrame({"stratum": strata, "psu": psus})
    unique_clusters = (
        pairs_df.drop_duplicates()
        .sort_values(["stratum", "psu"], kind="mergesort")
        .reset_index(drop=True)
    )
    unique_clusters["cluster_id"] = np.arange(len(unique_clusters), dtype=np.int64)

    merged = pairs_df.merge(
        unique_clusters,
        on=["stratum", "psu"],
        how="left",
        validate="many_to_one",
    )
    if merged["cluster_id"].isna().any():
        raise RuntimeError("Interner Fehler: Cluster-Zuordnung der Designbasis unvollständig.")

    cluster_ids = merged["cluster_id"].to_numpy(dtype=np.int64)
    n_clusters = len(unique_clusters)

    strata_clusters: list[tuple[int, np.ndarray]] = []
    singleton_strata: list[int] = []
    for stratum_id, grp in unique_clusters.groupby("stratum", sort=True):
        c_ids = grp["cluster_id"].to_numpy(dtype=np.int64)
        if len(c_ids) < 2:
            singleton_strata.append(int(stratum_id))
        strata_clusters.append((int(stratum_id), c_ids))

    if singleton_strata:
        raise ValueError(
            "Designbasis enthält Strata mit weniger als 2 Clustern "
            f"(Varianz nicht schätzbar): {singleton_strata}"
        )

    return cluster_ids, n_clusters, strata_clusters


def compute_taylor_variance(
    z: np.ndarray,
    cluster_ids: np.ndarray,
    n_clusters: int,
    strata_clusters: list[tuple[int, np.ndarray]],
) -> float:
    """
    Berechnet die Varianz über alle Cluster der vollständigen Designbasis.
    Cluster ohne Personen in der Analysegruppe gehen mit Clustersumme 0.0 ein.
    """
    if z.shape != cluster_ids.shape:
        raise ValueError("Länge von z stimmt nicht mit der Designbasis überein.")
    if not np.isfinite(z).all():
        raise ValueError("Linearisierte Variable z enthält NaN oder unendliche Werte.")

    cluster_sums = np.bincount(cluster_ids, weights=z, minlength=n_clusters).astype(np.float64)
    if len(cluster_sums) != n_clusters:
        raise RuntimeError("Unerwartete Länge des Cluster-Summenvektors.")

    total_var = 0.0
    for stratum_id, c_ids in strata_clusters:
        z_h = cluster_sums[c_ids]
        n_h = len(z_h)
        if n_h < 2:
            raise ValueError(f"Stratum {stratum_id} hat weniger als 2 Cluster (n_h={n_h}).")
        z_bar = float(np.mean(z_h))
        diff = z_h - z_bar
        total_var += (n_h / (n_h - 1.0)) * float(np.sum(diff * diff))

    if not np.isfinite(total_var) or total_var < 0.0:
        raise ValueError(f"Ungültige Varianz berechnet: {total_var}")

    return total_var


def estimate_crude(
    weights: np.ndarray,
    y: np.ndarray,
    domain_mask: np.ndarray,
    cluster_ids: np.ndarray,
    n_clusters: int,
    strata_clusters: list[tuple[int, np.ndarray]],
    label: str,
) -> tuple[float, float]:
    """Berechnet rohe Prävalenz (Anteil 0..1) und Standardfehler (0..1)."""
    if not domain_mask.any():
        raise ValueError(f"Teilgruppe '{label}' ist leer; rohe Schätzung nicht möglich.")

    w_dom = weights[domain_mask]
    y_dom = y[domain_mask]
    if not (np.isfinite(w_dom).all() and np.isfinite(y_dom).all()):
        raise ValueError(f"Nicht-endliche Gewichte oder Zielwerte in '{label}'.")

    W = float(np.sum(w_dom))
    if W <= 0.0:
        raise ValueError(f"Gewichtssumme W <= 0 in '{label}' (W={W}).")

    p = float(np.sum(w_dom * y_dom) / W)

    z = np.zeros(len(weights), dtype=np.float64)
    z[domain_mask] = w_dom * (y_dom - p) / W

    var_p = compute_taylor_variance(z, cluster_ids, n_clusters, strata_clusters)
    se_p = float(np.sqrt(var_p))
    return p, se_p


def estimate_age_adjusted(
    weights: np.ndarray,
    y: np.ndarray,
    domain_mask: np.ndarray,
    age_groups: list[tuple[str, np.ndarray, float]],
    cluster_ids: np.ndarray,
    n_clusters: int,
    strata_clusters: list[tuple[int, np.ndarray]],
    label: str,
) -> tuple[float, float]:
    """
    Berechnet altersadjustierte Prävalenz (0..1) und Standardfehler (0..1).
    Summiert z je Cluster über alle Altersgruppen gemeinsam auf.
    """
    p_adj = 0.0
    z = np.zeros(len(weights), dtype=np.float64)
    covered = np.zeros(len(weights), dtype=bool)

    for age_label, age_mask, s_a in age_groups:
        sub_mask = domain_mask & age_mask
        if not sub_mask.any():
            raise ValueError(
                f"Altersgruppe '{age_label}' in '{label}' ist leer; "
                "altersadjustierter Wert nicht schätzbar."
            )
        if (covered & sub_mask).any():
            raise ValueError(
                f"Überlappende Altersgruppenzuordnung bei '{age_label}' in '{label}'."
            )
        covered |= sub_mask

        w_a = weights[sub_mask]
        y_a = y[sub_mask]
        if not (np.isfinite(w_a).all() and np.isfinite(y_a).all()):
            raise ValueError(f"Nicht-endliche Werte in Altersgruppe '{age_label}' ({label}).")

        W_a = float(np.sum(w_a))
        if W_a <= 0.0:
            raise ValueError(
                f"Gewichtssumme W_a <= 0 in Altersgruppe '{age_label}' ({label}): W_a={W_a}."
            )

        p_a = float(np.sum(w_a * y_a) / W_a)
        p_adj += s_a * p_a
        z[sub_mask] = s_a * w_a * (y_a - p_a) / W_a

    if not np.array_equal(covered, domain_mask):
        n_missing = int((domain_mask & ~covered).sum())
        raise ValueError(
            f"{n_missing} Personen in '{label}' wurden keiner Altersgruppe zugeordnet."
        )

    var_p = compute_taylor_variance(z, cluster_ids, n_clusters, strata_clusters)
    se_p = float(np.sqrt(var_p))
    return p_adj, se_p


def format_exact_float(value: float) -> str:
    """Gibt eine 64-Bit-Gleitkommazahl mit voller Rechengenauigkeit aus."""
    return repr(float(value))


def main() -> None:
    repo_root = resolve_repo_root()
    raw_dir = repo_root / "data" / "raw"
    out_path = repo_root / "results" / "B" / "abend2_positivkontrolle.csv"

    # Prüfung der festen Standardanteile (müssen exakt 1 ergeben)
    std_weight_sum = sum(s for _, _, _, s in AGE_STD_WEIGHTS)
    if not np.isclose(std_weight_sum, 1.0, atol=1e-12):
        raise ValueError(f"Standardanteile summieren sich nicht zu 1: {std_weight_sum}")

    # 1. Rohdateien laden und validieren
    demo = load_xpt(raw_dir / "P_DEMO.xpt", EXPECTED_ROWS_DEMO, REQUIRED_COLS_DEMO)
    bmx = load_xpt(raw_dir / "P_BMX.xpt", EXPECTED_ROWS_BMX, REQUIRED_COLS_BMX)

    # 2. Designbasis bilden (Definition 4: RIDSTATR = 2 und WTMECPRP > 0)
    mask_design = (
        demo["RIDSTATR"].notna()
        & (demo["RIDSTATR"] == 2)
        & demo["WTMECPRP"].notna()
        & np.isfinite(demo["WTMECPRP"])
        & (demo["WTMECPRP"] > 0.0)
    ).to_numpy(dtype=bool)

    design = demo.loc[mask_design, REQUIRED_COLS_DEMO].copy().reset_index(drop=True)
    if len(design) == 0:
        raise ValueError("Designbasis (RIDSTATR == 2 und WTMECPRP > 0) ist leer.")

    # P_BMX je Person anfügen, ohne Personen der Designbasis zu verlieren
    n_design_before = len(design)
    design = design.merge(
        bmx[["SEQN", "BMXBMI"]],
        on="SEQN",
        how="left",
        validate="one_to_one",
    )
    if len(design) != n_design_before:
        raise RuntimeError(
            f"Zeilenzahl der Designbasis änderte sich beim Merge: "
            f"{n_design_before} -> {len(design)}."
        )

    # Designvariablen prüfen
    weights = design["WTMECPRP"].to_numpy(dtype=np.float64)
    if not (np.isfinite(weights).all() and (weights > 0.0).all()):
        raise ValueError("Ungültige oder nicht-positive Gewichte WTMECPRP in der Designbasis.")

    strata = to_exact_int64(design["SDMVSTRA"], "SDMVSTRA", "Designbasis")
    psus = to_exact_int64(design["SDMVPSU"], "SDMVPSU", "Designbasis")
    cluster_ids, n_clusters, strata_clusters = prepare_design_structure(strata, psus)

    # BMI-Plausibilitätsprüfung (keine negativen oder Null-Werte als gültiger BMI)
    bmi_non_null = design["BMXBMI"].dropna().to_numpy(dtype=np.float64)
    if (bmi_non_null <= 0.0).any():
        raise ValueError("Unerwartete nicht-positive BMXBMI-Werte (<= 0) gefunden.")

    # 3. Vollständige Ja/Nein-Masken auf der Designbasis bilden (Definitionen 1, 2, 3, 7)
    age_vals = design["RIDAGEYR"].to_numpy(dtype=np.float64)
    bmi_vals = design["BMXBMI"].to_numpy(dtype=np.float64)
    gender_vals = design["RIAGENDR"].to_numpy(dtype=np.float64)
    preg_vals = design["RIDEXPRG"].to_numpy(dtype=np.float64)

    age_ge_20 = np.isfinite(age_vals) & (age_vals >= 20.0)
    valid_bmi = np.isfinite(bmi_vals)
    # Definition 1: nur dokumentiertes RIDEXPRG = 1 ausschließen; NaN und Code 3 bleiben drin
    not_pregnant = np.isnan(preg_vals) | (preg_vals != 1.0)

    mask_gesamt = age_ge_20 & valid_bmi & not_pregnant
    mask_maenner = mask_gesamt & np.isfinite(gender_vals) & (gender_vals == 1.0)
    mask_frauen = mask_gesamt & np.isfinite(gender_vals) & (gender_vals == 2.0)

    groups = [
        ("Gesamt", mask_gesamt),
        ("Männer", mask_maenner),
        ("Frauen", mask_frauen),
    ]

    # Altersgruppenmasken (Definition 3: RIDAGEYR unverändert, ab 80 = 80)
    age_groups: list[tuple[str, np.ndarray, float]] = []
    for age_label, low, high, std_w in AGE_STD_WEIGHTS:
        if high is None:
            a_mask = np.isfinite(age_vals) & (age_vals >= float(low))
        else:
            a_mask = np.isfinite(age_vals) & (age_vals >= float(low)) & (age_vals <= float(high))
        age_groups.append((age_label, a_mask, std_w))

    # Zielvariablen (Definition 2: fehlende Werte erfüllen keine Bedingung)
    y_adipositas = (valid_bmi & (bmi_vals >= 30.0)).astype(np.float64)
    y_schwere_adipositas = (valid_bmi & (bmi_vals >= 40.0)).astype(np.float64)

    outcomes = [
        ("Adipositas", y_adipositas),
        ("Schwere Adipositas", y_schwere_adipositas),
    ]

    rows: list[dict[str, object]] = []

    # Stufe 1: Fallzahlen
    for group_name, g_mask in groups:
        n_group = int(g_mask.sum())
        if n_group == 0:
            raise ValueError(f"Analysegruppe '{group_name}' hat 0 Personen.")
        rows.append(
            {
                "stufe": 1,
                "kennzahl": "Analysegruppe",
                "gruppe": group_name,
                "methode": "ungewichtet",
                "groesse": "Fallzahl",
                "einheit": "Personen",
                "wert": str(n_group),
            }
        )

    # Stufe 2: Rohe Prävalenzen und Standardfehler
    for outcome_name, y_vec in outcomes:
        for group_name, g_mask in groups:
            label = f"{outcome_name} / {group_name} / roh"
            p, se = estimate_crude(
                weights=weights,
                y=y_vec,
                domain_mask=g_mask,
                cluster_ids=cluster_ids,
                n_clusters=n_clusters,
                strata_clusters=strata_clusters,
                label=label,
            )
            rows.append(
                {
                    "stufe": 2,
                    "kennzahl": outcome_name,
                    "gruppe": group_name,
                    "methode": "roh",
                    "groesse": "Praevalenz",
                    "einheit": "Prozent",
                    "wert": format_exact_float(p * 100.0),
                }
            )
            rows.append(
                {
                    "stufe": 2,
                    "kennzahl": outcome_name,
                    "gruppe": group_name,
                    "methode": "roh",
                    "groesse": "Standardfehler",
                    "einheit": "Prozentpunkte",
                    "wert": format_exact_float(se * 100.0),
                }
            )

    # Stufe 4: Altersadjustierte Prävalenzen und Standardfehler
    for outcome_name, y_vec in outcomes:
        for group_name, g_mask in groups:
            label = f"{outcome_name} / {group_name} / altersadjustiert"
            p_adj, se_adj = estimate_age_adjusted(
                weights=weights,
                y=y_vec,
                domain_mask=g_mask,
                age_groups=age_groups,
                cluster_ids=cluster_ids,
                n_clusters=n_clusters,
                strata_clusters=strata_clusters,
                label=label,
            )
            rows.append(
                {
                    "stufe": 4,
                    "kennzahl": outcome_name,
                    "gruppe": group_name,
                    "methode": "altersadjustiert",
                    "groesse": "Praevalenz",
                    "einheit": "Prozent",
                    "wert": format_exact_float(p_adj * 100.0),
                }
            )
            rows.append(
                {
                    "stufe": 4,
                    "kennzahl": outcome_name,
                    "gruppe": group_name,
                    "methode": "altersadjustiert",
                    "groesse": "Standardfehler",
                    "einheit": "Prozentpunkte",
                    "wert": format_exact_float(se_adj * 100.0),
                }
            )

    # 4. Ausgabe schreiben
    result_df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(out_path, index=False, encoding="utf-8")

    print(
        f"Designbasis: {len(design)} Personen, "
        f"{len(strata_clusters)} Strata, {n_clusters} Cluster."
    )
    print(f"Ergebnis geschrieben nach: {out_path} ({len(result_df)} Zeilen)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        sys.exit(1)
