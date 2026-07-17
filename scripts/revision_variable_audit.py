"""Audit PISA 2022 variables and country coverage for the post-SEE revision.

This script is intentionally separate from the original analysis so that the
submitted SEE package remains reproducible and unchanged.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "revision_submission" / "analysis"

STUDENT_FILE = DATA_DIR / "CY08MSP_STU_QQQ.SAV"
SCHOOL_FILE = DATA_DIR / "CY08MSP_SCH_QQQ.SAV"

OLD_TEN_SYSTEMS = {
    "AUS",
    "CAN",
    "DEU",
    "FRA",
    "GBR",
    "IRL",
    "NZL",
    "SGP",
    "SWE",
    "USA",
}


def weighted_corr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    if mask.sum() < 3:
        return np.nan
    xv = x.loc[mask].to_numpy(float)
    yv = y.loc[mask].to_numpy(float)
    wv = w.loc[mask].to_numpy(float)
    mx = np.average(xv, weights=wv)
    my = np.average(yv, weights=wv)
    cov = np.average((xv - mx) * (yv - my), weights=wv)
    vx = np.average((xv - mx) ** 2, weights=wv)
    vy = np.average((yv - my) ** 2, weights=wv)
    if vx <= 0 or vy <= 0:
        return np.nan
    return float(cov / np.sqrt(vx * vy))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    student_cols = [
        "CNT",
        "CNTSCHID",
        "ESCS",
        "ICTRES",
        "ICTHOME",
        "ICTAVHOM",
        "W_FSTUWT",
    ]
    school_cols = ["CNT", "CNTSCHID", "RATCMP1"]

    students, student_meta = pyreadstat.read_sav(
        str(STUDENT_FILE), usecols=student_cols
    )
    schools, school_meta = pyreadstat.read_sav(
        str(SCHOOL_FILE), usecols=school_cols
    )
    schools = schools.drop_duplicates(["CNT", "CNTSCHID"])
    frame = students.merge(schools, on=["CNT", "CNTSCHID"], how="left")

    rows = []
    core = ["ESCS", "ICTAVHOM", "RATCMP1"]
    for cnt, group in frame.groupby("CNT", sort=True):
        complete_core = group[core].notna().all(axis=1)
        has_escs = group["ESCS"].notna().any()
        has_home = group["ICTAVHOM"].notna().any()
        has_school = group["RATCMP1"].notna().any()
        rows.append(
            {
                "CNT": cnt,
                "old_ten_system_sample": cnt in OLD_TEN_SYSTEMS,
                "students": len(group),
                "schools": group["CNTSCHID"].nunique(),
                "ESCS_nonmissing": int(group["ESCS"].notna().sum()),
                "ICTRES_nonmissing": int(group["ICTRES"].notna().sum()),
                "ICTHOME_nonmissing": int(group["ICTHOME"].notna().sum()),
                "ICTAVHOM_nonmissing": int(group["ICTAVHOM"].notna().sum()),
                "RATCMP1_nonmissing_students": int(group["RATCMP1"].notna().sum()),
                "complete_core": int(complete_core.sum()),
                "complete_core_rate": float(complete_core.mean()),
                "primary_eligible": bool(has_escs and has_home and has_school),
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_DIR / "variable_audit_by_system.csv", index=False)

    eligible_codes = audit.loc[audit["primary_eligible"], "CNT"].tolist()
    eligible = frame[frame["CNT"].isin(eligible_codes)].copy()
    complete = eligible[core].notna().all(axis=1)

    student_labels = dict(
        zip(student_meta.column_names, student_meta.column_labels)
    )
    school_labels = dict(zip(school_meta.column_names, school_meta.column_labels))

    summary = f"""# Variable and Sample Audit for the New Submission

Generated from the local OECD PISA 2022 public-use files.

## Variable labels in the public-use files

| Variable | Public-use label | Role in new analysis |
| --- | --- | --- |
| `ICTRES` | {student_labels['ICTRES']} | Excluded as the primary home ICT measure |
| `ICTHOME` | {student_labels['ICTHOME']} | Sensitivity measure (IRT/WLE scale) |
| `ICTAVHOM` | {student_labels['ICTAVHOM']} | Primary home ICT availability measure |
| `RATCMP1` | {school_labels['RATCMP1']} | Primary school computer provision measure |

## Coverage

- PISA systems/economies in the files: {len(audit)}
- Systems with non-missing ESCS, ICTAVHOM, and RATCMP1 data: {len(eligible_codes)}
- Students in those systems before item-level exclusions: {len(eligible):,}
- Students complete on ESCS, ICTAVHOM, and RATCMP1: {int(complete.sum()):,}
- Complete-core retention rate: {complete.mean():.1%}
- Eligible systems: {', '.join(eligible_codes)}

The former 10-system sample is therefore not an eligibility-defined sample.

## Construct overlap diagnostic

- Weighted correlation between ESCS and ICTRES: {weighted_corr(eligible['ESCS'], eligible['ICTRES'], eligible['W_FSTUWT']):.3f}
- Weighted correlation between ESCS and ICTAVHOM: {weighted_corr(eligible['ESCS'], eligible['ICTAVHOM'], eligible['W_FSTUWT']):.3f}

## Decisions for the clean revision

1. Use `ICTAVHOM` as the primary home ICT availability indicator.
2. Use `ICTHOME` as a sensitivity measure where available.
3. Retain all eligible systems rather than the former convenience sample.
4. Treat remaining item nonresponse explicitly; do not rely only on listwise deletion.
5. Keep the rejected SEE submission package unchanged for reproducibility.
"""
    (OUT_DIR / "variable_audit_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
