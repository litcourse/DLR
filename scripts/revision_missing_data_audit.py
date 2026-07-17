"""Missing-data and complete-case selection audit for the clean revision."""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "revision_submission" / "analysis"
AUDIT_FILE = OUT_DIR / "variable_audit_by_system.csv"


def equal_system_weight(frame: pd.DataFrame) -> pd.Series:
    """Rescale final weights so every education system has equal total weight."""
    totals = frame.groupby("CNT")["W_FSTUWT"].transform("sum")
    return frame["W_FSTUWT"] / totals


def weighted_moments(values: pd.Series, weights: pd.Series) -> tuple[float, float]:
    mask = values.notna() & weights.notna() & (weights > 0)
    if mask.sum() == 0:
        return np.nan, np.nan
    x = values.loc[mask].to_numpy(float)
    w = weights.loc[mask].to_numpy(float)
    mean = np.average(x, weights=w)
    variance = np.average((x - mean) ** 2, weights=w)
    return float(mean), float(np.sqrt(variance))


def standardized_difference(
    values: pd.Series, retained: pd.Series, weights: pd.Series
) -> tuple[float, float, float]:
    keep_mean, keep_sd = weighted_moments(values[retained], weights[retained])
    drop_mean, drop_sd = weighted_moments(values[~retained], weights[~retained])
    pooled_sd = np.sqrt((keep_sd**2 + drop_sd**2) / 2.0)
    smd = (keep_mean - drop_mean) / pooled_sd if pooled_sd > 0 else np.nan
    return keep_mean, drop_mean, float(smd)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    eligible = pd.read_csv(AUDIT_FILE)
    eligible_codes = eligible.loc[eligible["primary_eligible"], "CNT"].tolist()

    pv_cols = (
        [f"PV{i}MATH" for i in range(1, 11)]
        + [f"PV{i}READ" for i in range(1, 11)]
        + [f"PV{i}SCIE" for i in range(1, 11)]
    )
    student_cols = [
        "CNT",
        "CNTSCHID",
        "CNTSTUID",
        "ESCS",
        "ICTAVHOM",
        "ICTHOME",
        "ST004D01T",
        "GRADE",
        "IMMIG",
        "BELONG",
        "W_FSTUWT",
    ] + pv_cols
    school_cols = [
        "CNT",
        "CNTSCHID",
        "RATCMP1",
        "PRIVATESCH",
        "SC001Q01TA",
        "STRATIO",
        "SCHSIZE",
    ]

    students, _ = pyreadstat.read_sav(
        str(DATA_DIR / "CY08MSP_STU_QQQ.SAV"), usecols=student_cols
    )
    students = students[students["CNT"].isin(eligible_codes)].copy()
    schools, _ = pyreadstat.read_sav(
        str(DATA_DIR / "CY08MSP_SCH_QQQ.SAV"), usecols=school_cols
    )
    schools = schools[schools["CNT"].isin(eligible_codes)].drop_duplicates(
        ["CNT", "CNTSCHID"]
    )
    frame = students.merge(schools, on=["CNT", "CNTSCHID"], how="left")
    frame["equal_system_weight"] = equal_system_weight(frame)

    frame["Male"] = np.where(
        frame["ST004D01T"].isin([1.0, 2.0]),
        (frame["ST004D01T"] == 2.0).astype(float),
        np.nan,
    )
    frame["Immigrant"] = np.where(
        frame["IMMIG"].isin([1.0, 2.0, 3.0]),
        frame["IMMIG"].isin([2.0, 3.0]).astype(float),
        np.nan,
    )
    private_text = frame["PRIVATESCH"].astype("string").str.lower()
    frame["Private"] = np.where(
        private_text.str.contains("private", na=False),
        1.0,
        np.where(private_text.str.contains("public", na=False), 0.0, np.nan),
    )
    frame["Urban"] = np.where(
        frame["SC001Q01TA"].isin([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        frame["SC001Q01TA"].isin([3.0, 4.0, 5.0, 6.0]).astype(float),
        np.nan,
    )
    frame["Math_mean_PV"] = frame[[f"PV{i}MATH" for i in range(1, 11)]].mean(
        axis=1
    )
    frame["Reading_mean_PV"] = frame[
        [f"PV{i}READ" for i in range(1, 11)]
    ].mean(axis=1)
    frame["Science_mean_PV"] = frame[
        [f"PV{i}SCIE" for i in range(1, 11)]
    ].mean(axis=1)

    core = ["ESCS", "ICTAVHOM", "RATCMP1"]
    retained = frame[core].notna().all(axis=1)
    frame["complete_core"] = retained

    variables = [
        "ESCS",
        "ICTAVHOM",
        "ICTHOME",
        "RATCMP1",
        "Male",
        "GRADE",
        "Immigrant",
        "BELONG",
        "Private",
        "Urban",
        "STRATIO",
        "SCHSIZE",
        "Math_mean_PV",
        "Reading_mean_PV",
        "Science_mean_PV",
    ]
    missing_rows = []
    for variable in variables:
        missing_rows.append(
            {
                "variable": variable,
                "missing_n": int(frame[variable].isna().sum()),
                "missing_rate": float(frame[variable].isna().mean()),
            }
        )
    missing_by_variable = pd.DataFrame(missing_rows)
    missing_by_variable.to_csv(
        OUT_DIR / "missingness_by_variable.csv", index=False
    )

    by_system = (
        frame.groupby("CNT")
        .agg(
            students=("CNTSTUID", "size"),
            complete_core=("complete_core", "sum"),
            ESCS_missing=("ESCS", lambda x: int(x.isna().sum())),
            ICTAVHOM_missing=("ICTAVHOM", lambda x: int(x.isna().sum())),
            RATCMP1_missing=("RATCMP1", lambda x: int(x.isna().sum())),
        )
        .reset_index()
    )
    by_system["complete_core_rate"] = (
        by_system["complete_core"] / by_system["students"]
    )
    by_system.to_csv(OUT_DIR / "missingness_by_system.csv", index=False)

    comparison_rows = []
    for variable in variables:
        keep_mean, drop_mean, smd = standardized_difference(
            frame[variable], retained, frame["equal_system_weight"]
        )
        comparison_rows.append(
            {
                "variable": variable,
                "retained_mean": keep_mean,
                "dropped_mean": drop_mean,
                "standardized_mean_difference": smd,
                "abs_smd": abs(smd) if np.isfinite(smd) else np.nan,
            }
        )
    comparison = pd.DataFrame(comparison_rows).sort_values(
        "abs_smd", ascending=False
    )
    comparison.to_csv(OUT_DIR / "retained_vs_dropped.csv", index=False)

    worst_systems = by_system.nsmallest(10, "complete_core_rate")
    largest_differences = comparison.head(8)
    summary = f"""# Missing-Data Audit

The audit uses all {len(eligible_codes)} education systems meeting the primary
variable-availability rule. Pooled descriptive comparisons use final student
weights rescaled so that every education system contributes equal total weight.

## Core analytic retention

- Students before item-level exclusions: {len(frame):,}
- Complete on ESCS, ICTAVHOM, and RATCMP1: {int(retained.sum()):,}
- Complete-core retention rate: {retained.mean():.1%}

## Systems with the lowest complete-core retention

{worst_systems[['CNT', 'students', 'complete_core', 'complete_core_rate']].to_markdown(index=False)}

## Largest observable differences between retained and dropped students

{largest_differences[['variable', 'retained_mean', 'dropped_mean', 'standardized_mean_difference']].to_markdown(index=False)}

Absolute standardized mean differences above 0.10 are treated as evidence that
complete-case deletion changes the observable sample composition.

## Consequence for the revised analysis

Complete-case estimates will be retained only as a benchmark. The primary
analysis must use an explicit missing-data procedure and report a complete-case
and inverse-probability-weighted sensitivity comparison.
"""
    (OUT_DIR / "missing_data_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
