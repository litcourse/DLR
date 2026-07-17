"""Multilevel predictive-mean-matching sensitivity analysis.

School variables are imputed on a unique-school file; student variables are
then imputed within education system using school context and achievement
plausible-value means as auxiliaries. Ten completed datasets are analysed
with all 10 plausible values and 80 Fay BRR replicate weights. The final variance
adds sampling, between-plausible-value, and between-imputation components.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats

from revision_core_analysis import (
    AUDIT_FILE,
    DATA_DIR,
    FINAL_WEIGHT,
    OUT_DIR,
    REPLICATE_WEIGHTS,
    SUBJECTS,
    add_model_terms,
    estimate_brr,
    standardize_within_country,
)


M_IMPUTATIONS = 10
PMM_DONORS = 5
PMM_CYCLES = 3
BASE_SEED = 20260717


def pmm_update(
    frame: pd.DataFrame,
    target: str,
    predictors: list[str],
    original_observed: pd.Series,
    rng: np.random.Generator,
) -> None:
    """One within-system predictive-mean-matching update."""
    for _, index in frame.groupby("CNT", sort=False).groups.items():
        index = np.asarray(list(index))
        observed_mask = original_observed.loc[index].to_numpy(bool)
        missing_mask = ~observed_mask
        if missing_mask.sum() == 0 or observed_mask.sum() < 10:
            continue
        x = frame.loc[index, predictors].to_numpy(float)
        y = frame.loc[index, target].to_numpy(float)
        for j in range(x.shape[1]):
            column = x[:, j]
            finite = np.isfinite(column)
            fill = np.nanmedian(column[finite]) if finite.any() else 0.0
            column[~finite] = fill
            x[:, j] = column
        means = x[observed_mask].mean(axis=0)
        sds = x[observed_mask].std(axis=0)
        keep = sds > 1e-8
        x = x[:, keep]
        means = means[keep]
        sds = sds[keep]
        x = (x - means) / sds
        x = np.column_stack([np.ones(len(x)), x])

        xo = x[observed_mask]
        yo = y[observed_mask]
        ridge = np.eye(xo.shape[1]) * 1e-6
        ridge[0, 0] = 0.0
        xtx_inv = np.linalg.pinv(xo.T @ xo + ridge, rcond=1e-10)
        beta = xtx_inv @ (xo.T @ yo)
        residual = yo - xo @ beta
        sigma2 = max(float(np.sum(residual**2) / max(len(yo) - xo.shape[1], 1)), 1e-8)
        covariance = sigma2 * xtx_inv
        try:
            beta_draw = rng.multivariate_normal(beta, covariance, check_valid="ignore")
        except np.linalg.LinAlgError:
            beta_draw = beta

        predicted = x @ beta_draw
        observed_positions = np.flatnonzero(observed_mask)
        missing_positions = np.flatnonzero(missing_mask)
        order = np.argsort(predicted[observed_positions])
        sorted_positions = observed_positions[order]
        sorted_prediction = predicted[sorted_positions]
        donor_values = y[sorted_positions]

        for position in missing_positions:
            insertion = int(np.searchsorted(sorted_prediction, predicted[position]))
            left = max(0, insertion - PMM_DONORS)
            right = min(len(sorted_positions), insertion + PMM_DONORS)
            candidates = np.arange(left, right)
            if len(candidates) > PMM_DONORS:
                distance = np.abs(sorted_prediction[candidates] - predicted[position])
                candidates = candidates[np.argsort(distance)[:PMM_DONORS]]
            chosen = int(rng.choice(candidates))
            y[position] = donor_values[chosen]
        frame.loc[index, target] = y


def initialise_by_country(frame: pd.DataFrame, targets: list[str]) -> None:
    for target in targets:
        fills = frame.groupby("CNT")[target].transform("median")
        frame[target] = frame[target].fillna(fills).fillna(frame[target].median())


def school_imputation(
    school_base: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    school = school_base.copy()
    targets = ["RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]
    observed = {target: school[target].notna().copy() for target in targets}
    initialise_by_country(school, targets)
    predictors = {
        "RATCMP1": ["Private", "Urban", "STRATIO", "SCHSIZE", "School_math", "School_ESCS_observed"],
        "Private": ["RATCMP1", "Urban", "STRATIO", "SCHSIZE", "School_math", "School_ESCS_observed"],
        "Urban": ["RATCMP1", "Private", "STRATIO", "SCHSIZE", "School_math", "School_ESCS_observed"],
        "STRATIO": ["RATCMP1", "Private", "Urban", "SCHSIZE", "School_math", "School_ESCS_observed"],
        "SCHSIZE": ["RATCMP1", "Private", "Urban", "STRATIO", "School_math", "School_ESCS_observed"],
    }
    for _ in range(PMM_CYCLES):
        for target in targets:
            pmm_update(school, target, predictors[target], observed[target], rng)
    school["Private"] = (school["Private"] >= 0.5).astype(float)
    school["Urban"] = (school["Urban"] >= 0.5).astype(float)
    school["RATCMP1"] = school["RATCMP1"].clip(lower=0)
    school["STRATIO"] = school["STRATIO"].clip(lower=0.1)
    school["SCHSIZE"] = school["SCHSIZE"].clip(lower=1)
    return school


def student_imputation(
    student_small: pd.DataFrame,
    school: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    frame = student_small.merge(
        school[["CNT", "CNTSCHID", "RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]],
        on=["CNT", "CNTSCHID"],
        how="left",
    )
    targets = ["ESCS", "ICTAVHOM", "Male", "GRADE", "Immigrant"]
    observed = {target: frame[target].notna().copy() for target in targets}
    initialise_by_country(frame, targets)
    common_school = ["RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]
    predictors = {
        "ESCS": ["ICTAVHOM", "Male", "GRADE", "Immigrant", "Math_mean_PV", "Reading_mean_PV", "Science_mean_PV"] + common_school,
        "ICTAVHOM": ["ESCS", "Male", "GRADE", "Immigrant", "Math_mean_PV", "Reading_mean_PV", "Science_mean_PV"] + common_school,
        "Male": ["ESCS", "ICTAVHOM", "GRADE", "Immigrant", "Math_mean_PV", "Reading_mean_PV", "Science_mean_PV"] + common_school,
        "GRADE": ["ESCS", "ICTAVHOM", "Male", "Immigrant", "Math_mean_PV", "Reading_mean_PV", "Science_mean_PV"] + common_school,
        "Immigrant": ["ESCS", "ICTAVHOM", "Male", "GRADE", "Math_mean_PV", "Reading_mean_PV", "Science_mean_PV"] + common_school,
    }
    for _ in range(PMM_CYCLES):
        for target in targets:
            pmm_update(frame, target, predictors[target], observed[target], rng)
    frame["Male"] = (frame["Male"] >= 0.5).astype(float)
    frame["Immigrant"] = (frame["Immigrant"] >= 0.5).astype(float)
    frame["ICTAVHOM"] = frame["ICTAVHOM"].clip(0, 6)
    return frame


def load_base() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    audit = pd.read_csv(AUDIT_FILE)
    eligible = audit.loc[audit["primary_eligible"], "CNT"].tolist()
    y_columns = [f"PV{i}{suffix}" for suffix in SUBJECTS.values() for i in range(1, 11)]
    student_columns = [
        "CNT",
        "CNTSCHID",
        "CNTSTUID",
        "ESCS",
        "ICTAVHOM",
        "ST004D01T",
        "GRADE",
        "IMMIG",
        FINAL_WEIGHT,
    ] + REPLICATE_WEIGHTS + y_columns
    school_columns = [
        "CNT",
        "CNTSCHID",
        "RATCMP1",
        "PRIVATESCH",
        "SC001Q01TA",
        "STRATIO",
        "SCHSIZE",
    ]
    students, _ = pyreadstat.read_sav(
        str(DATA_DIR / "CY08MSP_STU_QQQ.SAV"), usecols=student_columns
    )
    students = students[students["CNT"].isin(eligible)].reset_index(drop=True)
    school_raw, _ = pyreadstat.read_sav(
        str(DATA_DIR / "CY08MSP_SCH_QQQ.SAV"), usecols=school_columns
    )
    school_raw = school_raw[school_raw["CNT"].isin(eligible)].drop_duplicates(["CNT", "CNTSCHID"])

    students["Male"] = np.where(
        students["ST004D01T"].isin([1.0, 2.0]),
        (students["ST004D01T"] == 2.0).astype(float),
        np.nan,
    )
    students["Immigrant"] = np.where(
        students["IMMIG"].isin([1.0, 2.0, 3.0]),
        students["IMMIG"].isin([2.0, 3.0]).astype(float),
        np.nan,
    )
    students["Math_mean_PV"] = students[[f"PV{i}MATH" for i in range(1, 11)]].mean(axis=1)
    students["Reading_mean_PV"] = students[[f"PV{i}READ" for i in range(1, 11)]].mean(axis=1)
    students["Science_mean_PV"] = students[[f"PV{i}SCIE" for i in range(1, 11)]].mean(axis=1)

    private_text = school_raw["PRIVATESCH"].astype("string").str.lower()
    school_raw["Private"] = np.where(
        private_text.str.contains("private", na=False),
        1.0,
        np.where(private_text.str.contains("public", na=False), 0.0, np.nan),
    )
    school_raw["Urban"] = np.where(
        school_raw["SC001Q01TA"].isin([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        school_raw["SC001Q01TA"].isin([3.0, 4.0, 5.0, 6.0]).astype(float),
        np.nan,
    )

    school_universe = students[["CNT", "CNTSCHID"]].drop_duplicates()
    school = school_universe.merge(
        school_raw[["CNT", "CNTSCHID", "RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]],
        on=["CNT", "CNTSCHID"],
        how="left",
    )
    school_aux = (
        students.groupby(["CNT", "CNTSCHID"])
        .agg(School_math=("Math_mean_PV", "mean"), School_ESCS_observed=("ESCS", "mean"))
        .reset_index()
    )
    school = school.merge(school_aux, on=["CNT", "CNTSCHID"], how="left")

    student_small = students[
        [
            "CNT",
            "CNTSCHID",
            "CNTSTUID",
            "ESCS",
            "ICTAVHOM",
            "Male",
            "GRADE",
            "Immigrant",
            "Math_mean_PV",
            "Reading_mean_PV",
            "Science_mean_PV",
            FINAL_WEIGHT,
        ]
    ].copy()
    big_columns = ["CNT", "CNTSCHID", "CNTSTUID", FINAL_WEIGHT] + REPLICATE_WEIGHTS + y_columns
    analysis_base = students[big_columns].copy()
    return student_small, school, analysis_base, y_columns


def build_model_frame(
    imputed: pd.DataFrame, analysis_base: pd.DataFrame
) -> pd.DataFrame:
    frame = analysis_base.merge(
        imputed[
            [
                "CNT",
                "CNTSCHID",
                "CNTSTUID",
                "ESCS",
                "ICTAVHOM",
                "Male",
                "GRADE",
                "Immigrant",
                "RATCMP1",
                "Private",
                "Urban",
                "STRATIO",
                "SCHSIZE",
            ]
        ],
        on=["CNT", "CNTSCHID", "CNTSTUID"],
        how="left",
    )
    caps = frame.groupby("CNT")["RATCMP1"].transform(lambda x: x.quantile(0.99))
    frame["Home_ICT"] = frame["ICTAVHOM"]
    frame["School_ICT"] = np.log1p(np.minimum(frame["RATCMP1"], caps))

    numerator = (frame["ESCS"] * frame[FINAL_WEIGHT]).groupby([frame["CNT"], frame["CNTSCHID"]]).transform("sum")
    denominator = frame[FINAL_WEIGHT].groupby([frame["CNT"], frame["CNTSCHID"]]).transform("sum")
    frame["School_SES"] = numerator / denominator
    standardize_within_country(
        frame,
        ["ESCS", "Home_ICT", "School_ICT", "GRADE", "STRATIO", "SCHSIZE", "School_SES"],
    )
    add_model_terms(frame)
    return frame


def combine_crossed(
    estimates: np.ndarray,
    sampling: np.ndarray,
    columns: list[str],
) -> pd.DataFrame:
    m_count = estimates.shape[0]
    rows = []
    offset = 0
    for subject in SUBJECTS:
        q = estimates[:, :, offset : offset + 10]
        u = sampling[:, :, offset : offset + 10]
        point = q.mean(axis=(0, 2))
        ubar = u.mean(axis=(0, 2))
        imputation_means = q.mean(axis=2)
        b_mi = imputation_means.var(axis=0, ddof=1)
        b_pv = q.var(axis=2, ddof=1).mean(axis=0)
        total = ubar + (1.0 + 1.0 / m_count) * b_mi + 1.1 * b_pv
        se = np.sqrt(np.maximum(total, 0.0))
        p = 2.0 * stats.norm.sf(np.abs(point / se))
        for variable, coef, std_error, p_value, u_part, mi_part, pv_part in zip(
            columns, point, se, p, ubar, b_mi, b_pv
        ):
            rows.append(
                {
                    "subject": subject,
                    "variable": variable,
                    "coef": coef,
                    "se": std_error,
                    "p_value": p_value,
                    "ci_low": coef - 1.96 * std_error,
                    "ci_high": coef + 1.96 * std_error,
                    "sampling_variance_component": u_part,
                    "between_imputation_component": b_mi,
                    "between_pv_component": b_pv,
                }
            )
        offset += 10
    return pd.DataFrame(rows)


def main() -> None:
    student_small, school_base, analysis_base, y_columns = load_base()
    controls = ["Male", "GRADE", "Immigrant", "Private", "Urban", "STRATIO", "SCHSIZE", "School_SES"]
    columns = [
        "ESCS",
        "Home_ICT",
        "Home_ICT_sq",
        "School_ICT",
        "School_ICT_sq",
        "ESCS_x_Home_ICT",
        "ESCS_x_Home_ICT_sq",
        "ESCS_x_School_ICT",
        "ESCS_x_School_ICT_sq",
    ] + controls

    estimates = []
    sampling = []
    diagnostic_rows = []
    original_missing = {
        variable: int(student_small[variable].isna().sum())
        for variable in ["ESCS", "ICTAVHOM", "Male", "GRADE", "Immigrant"]
    }
    original_missing.update(
        {
            variable: int(school_base[variable].isna().sum())
            for variable in ["RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]
        }
    )

    for imputation in range(1, M_IMPUTATIONS + 1):
        print(f"Creating and estimating imputation {imputation}/{M_IMPUTATIONS}...")
        rng = np.random.default_rng(BASE_SEED + imputation)
        school = school_imputation(school_base, rng)
        imputed = student_imputation(student_small, school, rng)
        for variable in ["ESCS", "ICTAVHOM", "Male", "GRADE", "Immigrant", "RATCMP1", "Private", "Urban", "STRATIO", "SCHSIZE"]:
            source = imputed[variable] if variable in imputed else school[variable]
            diagnostic_rows.append(
                {
                    "imputation": imputation,
                    "variable": variable,
                    "original_missing_n": original_missing[variable],
                    "imputed_mean": float(source.mean()),
                    "imputed_sd": float(source.std(ddof=0)),
                }
            )
        model_frame = build_model_frame(imputed, analysis_base)
        estimate, sample_var = estimate_brr(model_frame, columns, y_columns)
        estimates.append(estimate)
        sampling.append(sample_var)

    estimates_array = np.stack(estimates, axis=0)
    sampling_array = np.stack(sampling, axis=0)
    results = combine_crossed(estimates_array, sampling_array, columns)
    results.to_csv(OUT_DIR / "multiple_imputation_results.csv", index=False)
    pd.DataFrame(diagnostic_rows).to_csv(OUT_DIR / "imputation_diagnostics.csv", index=False)

    focal = results[results["variable"].isin([
        "Home_ICT", "Home_ICT_sq", "School_ICT", "School_ICT_sq",
        "ESCS_x_Home_ICT", "ESCS_x_Home_ICT_sq",
        "ESCS_x_School_ICT", "ESCS_x_School_ICT_sq",
    ])]
    summary = f"""# Multiple-Imputation Results

- Education systems: {student_small['CNT'].nunique()}
- Students retained after imputation: {len(student_small):,}
- Completed datasets: {M_IMPUTATIONS}
- School variables imputed on a unique-school file before student-level imputation
- Within-system predictive mean matching with {PMM_DONORS} donors and {PMM_CYCLES} cycles
- Variance combines Fay BRR sampling, plausible-value, and imputation components

## Focal coefficients

{focal[['subject', 'variable', 'coef', 'se', 'p_value', 'ci_low', 'ci_high']].to_markdown(index=False)}
"""
    (OUT_DIR / "multiple_imputation_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
