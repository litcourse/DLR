"""Core complete-case and selection-weighted analyses for the clean revision.

Key departures from the rejected SEE analysis:
* ICTAVHOM replaces ICTRES as the primary home ICT availability measure.
* All education systems satisfying a reproducible availability rule are used.
* Pooled weights are rescaled so every education system has equal total weight.
* BELONG is excluded from the primary adjustment set.
* Home and school channels are estimated jointly.
* Quadratic moderation follows the hierarchy principle by including interactions
  with both the linear and squared resource terms.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "revision_submission" / "analysis"
AUDIT_FILE = OUT_DIR / "variable_audit_by_system.csv"

FINAL_WEIGHT = "W_FSTUWT"
REPLICATE_WEIGHTS = [f"W_FSTURWT{i}" for i in range(1, 81)]
FAY = 0.5
SUBJECTS = {"Math": "MATH", "Reading": "READ", "Science": "SCIE"}


def weighted_mean_sd(values: pd.Series, weights: pd.Series) -> tuple[float, float]:
    mask = values.notna() & weights.notna() & (weights > 0)
    x = values.loc[mask].to_numpy(float)
    w = weights.loc[mask].to_numpy(float)
    mean = np.average(x, weights=w)
    sd = np.sqrt(np.average((x - mean) ** 2, weights=w))
    return float(mean), float(sd)


def fill_country(frame: pd.DataFrame, column: str, binary: bool = False) -> None:
    missing = frame[column].isna().astype(float)
    frame[f"{column}_missing"] = missing
    if binary:
        def mode_or_zero(x: pd.Series) -> float:
            mode = x.mode(dropna=True)
            return float(mode.iloc[0]) if len(mode) else 0.0

        fills = frame.groupby("CNT")[column].transform(mode_or_zero)
        frame[column] = frame[column].fillna(fills).fillna(0.0)
    else:
        fills = frame.groupby("CNT")[column].transform("median")
        frame[column] = frame[column].fillna(fills).fillna(frame[column].median())


def standardize_within_country(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        result = pd.Series(index=frame.index, dtype=float)
        for _, index in frame.groupby("CNT").groups.items():
            mean, sd = weighted_mean_sd(
                frame.loc[index, column], frame.loc[index, FINAL_WEIGHT]
            )
            if not np.isfinite(sd) or sd <= 0:
                result.loc[index] = 0.0
            else:
                result.loc[index] = (frame.loc[index, column] - mean) / sd
        frame[column] = result


def equal_system_weights(
    raw_weights: np.ndarray, groups: np.ndarray, adjustment: np.ndarray | None = None
) -> np.ndarray:
    weights = np.asarray(raw_weights, dtype=float).copy()
    if adjustment is not None:
        weights *= adjustment
    totals = np.bincount(groups, weights=weights)
    valid = totals[groups] > 0
    scaled = np.zeros_like(weights)
    scaled[valid] = weights[valid] / totals[groups[valid]]
    scaled *= len(weights) / scaled.sum()
    return scaled


def solve_absorbed_country_fe(
    x: np.ndarray, y: np.ndarray, weights: np.ndarray, groups: np.ndarray
) -> np.ndarray:
    """Weighted least squares after analytically absorbing country intercepts."""
    n_groups = int(groups.max()) + 1
    sw = np.bincount(groups, weights=weights, minlength=n_groups)
    sx = np.column_stack(
        [np.bincount(groups, weights=weights * x[:, j], minlength=n_groups) for j in range(x.shape[1])]
    )
    sy = np.column_stack(
        [np.bincount(groups, weights=weights * y[:, j], minlength=n_groups) for j in range(y.shape[1])]
    )
    xtwx = x.T @ (x * weights[:, None])
    xtwy = x.T @ (y * weights[:, None])
    valid = sw > 0
    xtwx -= sx[valid].T @ (sx[valid] / sw[valid, None])
    xtwy -= sx[valid].T @ (sy[valid] / sw[valid, None])
    try:
        return np.linalg.solve(xtwx, xtwy)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(xtwx, rcond=1e-10) @ xtwy


def estimate_brr(
    frame: pd.DataFrame,
    x_columns: list[str],
    y_columns: list[str],
    selection_adjustment: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    x = frame[x_columns].to_numpy(float)
    y = frame[y_columns].to_numpy(float)
    groups, _ = pd.factorize(frame["CNT"], sort=True)

    final_w = equal_system_weights(
        frame[FINAL_WEIGHT].to_numpy(float), groups, selection_adjustment
    )
    full = solve_absorbed_country_fe(x, y, final_w, groups)

    squared_differences = np.zeros((x.shape[1], y.shape[1]), dtype=float)
    for column in REPLICATE_WEIGHTS:
        rep_w = equal_system_weights(
            frame[column].to_numpy(float), groups, selection_adjustment
        )
        replicate = solve_absorbed_country_fe(x, y, rep_w, groups)
        squared_differences += (replicate - full) ** 2
    sampling_variance = squared_differences / (
        len(REPLICATE_WEIGHTS) * (1.0 - FAY) ** 2
    )
    return full, sampling_variance


def combine_pvs(
    estimates: np.ndarray,
    sampling_variances: np.ndarray,
    x_columns: list[str],
) -> pd.DataFrame:
    rows = []
    offset = 0
    for subject in SUBJECTS:
        block = estimates[:, offset : offset + 10]
        block_sampling = sampling_variances[:, offset : offset + 10]
        point = block.mean(axis=1)
        within = block_sampling.mean(axis=1)
        between = block.var(axis=1, ddof=1)
        total = within + 1.1 * between
        se = np.sqrt(np.maximum(total, 0.0))
        z = point / se
        p = 2.0 * stats.norm.sf(np.abs(z))
        for variable, coef, std_error, p_value in zip(x_columns, point, se, p):
            rows.append(
                {
                    "subject": subject,
                    "variable": variable,
                    "coef": coef,
                    "se": std_error,
                    "p_value": p_value,
                    "ci_low": coef - 1.96 * std_error,
                    "ci_high": coef + 1.96 * std_error,
                }
            )
        offset += 10
    return pd.DataFrame(rows)


def selection_adjustment(full_frame: pd.DataFrame, retained: pd.Series) -> pd.Series:
    features = full_frame[
        [
            "Math_mean_PV",
            "Reading_mean_PV",
            "Science_mean_PV",
            "Male",
            "GRADE",
            "Immigrant",
            "Private",
            "Urban",
            "SCHSIZE",
        ]
    ].copy()
    for column in features.columns:
        indicator = features[column].isna().astype(float)
        features[f"{column}_missing"] = indicator
        fills = features.groupby(full_frame["CNT"])[column].transform("median")
        features[column] = features[column].fillna(fills).fillna(features[column].median())
    countries = pd.get_dummies(full_frame["CNT"], drop_first=True, dtype=float)
    features = pd.concat([features, countries], axis=1)
    means = features.mean()
    sds = features.std(ddof=0).replace(0, 1)
    features = (features - means) / sds

    groups, _ = pd.factorize(full_frame["CNT"], sort=True)
    sample_weight = equal_system_weights(
        full_frame[FINAL_WEIGHT].to_numpy(float), groups
    )
    model = LogisticRegression(max_iter=500, solver="lbfgs")
    model.fit(features.to_numpy(float), retained.astype(int), sample_weight=sample_weight)
    probability = np.clip(model.predict_proba(features.to_numpy(float))[:, 1], 0.05, 0.99)
    country_rate = retained.groupby(full_frame["CNT"]).transform("mean").to_numpy(float)
    return pd.Series(country_rate / probability, index=full_frame.index)


def prepare_data() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    audit = pd.read_csv(AUDIT_FILE)
    eligible_codes = audit.loc[audit["primary_eligible"], "CNT"].tolist()
    pv_columns = [f"PV{i}{suffix}" for suffix in SUBJECTS.values() for i in range(1, 11)]
    student_columns = [
        "CNT",
        "CNTSCHID",
        "CNTSTUID",
        "ESCS",
        "ICTAVHOM",
        "ICTHOME",
        "ST004D01T",
        "GRADE",
        "IMMIG",
        FINAL_WEIGHT,
    ] + REPLICATE_WEIGHTS + pv_columns
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
    students = students[students["CNT"].isin(eligible_codes)].copy()
    schools, _ = pyreadstat.read_sav(
        str(DATA_DIR / "CY08MSP_SCH_QQQ.SAV"), usecols=school_columns
    )
    schools = schools[schools["CNT"].isin(eligible_codes)].drop_duplicates(
        ["CNT", "CNTSCHID"]
    )
    caps = schools.groupby("CNT")["RATCMP1"].quantile(0.99)
    schools["School_ICT_raw"] = schools.apply(
        lambda row: min(row["RATCMP1"], caps.loc[row["CNT"]])
        if pd.notna(row["RATCMP1"])
        else np.nan,
        axis=1,
    )
    schools["School_ICT"] = np.log1p(schools["School_ICT_raw"])
    frame = students.merge(schools, on=["CNT", "CNTSCHID"], how="left")

    valid_ses = frame["ESCS"].notna() & frame[FINAL_WEIGHT].notna() & (frame[FINAL_WEIGHT] > 0)
    numerator = (frame.loc[valid_ses, "ESCS"] * frame.loc[valid_ses, FINAL_WEIGHT]).groupby(
        [frame.loc[valid_ses, "CNT"], frame.loc[valid_ses, "CNTSCHID"]]
    ).sum()
    denominator = frame.loc[valid_ses].groupby(["CNT", "CNTSCHID"])[FINAL_WEIGHT].sum()
    school_ses = (numerator / denominator).rename("School_SES").reset_index()
    frame = frame.merge(school_ses, on=["CNT", "CNTSCHID"], how="left")

    frame["Home_ICT"] = frame["ICTAVHOM"]
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
    frame["Math_mean_PV"] = frame[[f"PV{i}MATH" for i in range(1, 11)]].mean(axis=1)
    frame["Reading_mean_PV"] = frame[[f"PV{i}READ" for i in range(1, 11)]].mean(axis=1)
    frame["Science_mean_PV"] = frame[[f"PV{i}SCIE" for i in range(1, 11)]].mean(axis=1)

    retained = frame[["ESCS", "Home_ICT", "School_ICT"]].notna().all(axis=1)
    adjustment = selection_adjustment(frame, retained)
    model_frame = frame.loc[retained].copy()
    model_adjustment = adjustment.loc[retained].copy()

    for column in ["Male", "Immigrant", "Private", "Urban"]:
        fill_country(model_frame, column, binary=True)
    for column in ["GRADE", "STRATIO", "SCHSIZE", "School_SES"]:
        fill_country(model_frame, column, binary=False)

    standardize_within_country(
        model_frame,
        [
            "ESCS",
            "Home_ICT",
            "School_ICT",
            "GRADE",
            "STRATIO",
            "SCHSIZE",
            "School_SES",
        ],
    )
    return model_frame, model_adjustment, retained


def add_model_terms(frame: pd.DataFrame) -> None:
    frame["Home_ICT_sq"] = frame["Home_ICT"] ** 2
    frame["School_ICT_sq"] = frame["School_ICT"] ** 2
    frame["ESCS_x_Home_ICT"] = frame["ESCS"] * frame["Home_ICT"]
    frame["ESCS_x_Home_ICT_sq"] = frame["ESCS"] * frame["Home_ICT_sq"]
    frame["ESCS_x_School_ICT"] = frame["ESCS"] * frame["School_ICT"]
    frame["ESCS_x_School_ICT_sq"] = frame["ESCS"] * frame["School_ICT_sq"]


def marginal_grid(results: pd.DataFrame, specification: str) -> pd.DataFrame:
    rows = []
    for subject in SUBJECTS:
        coef = results[results["subject"] == subject].set_index("variable")["coef"]
        for resource in ["Home_ICT", "School_ICT"]:
            for escs in [-1.0, 0.0, 1.0]:
                for level in [-1.0, 0.0, 1.0]:
                    if specification == "linear":
                        slope = coef[resource] + escs * coef[f"ESCS_x_{resource}"]
                    else:
                        slope = (
                            coef[resource]
                            + 2.0 * coef[f"{resource}_sq"] * level
                            + escs
                            * (
                                coef[f"ESCS_x_{resource}"]
                                + 2.0 * coef[f"ESCS_x_{resource}_sq"] * level
                            )
                        )
                    rows.append(
                        {
                            "specification": specification,
                            "subject": subject,
                            "resource": resource,
                            "ESCS": escs,
                            "resource_level": level,
                            "conditional_resource_slope": slope,
                        }
                    )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, ipw_adjustment, retained = prepare_data()
    add_model_terms(frame)
    y_columns = [f"PV{i}{suffix}" for suffix in SUBJECTS.values() for i in range(1, 11)]
    controls = [
        "Male",
        "GRADE",
        "Immigrant",
        "Private",
        "Urban",
        "STRATIO",
        "SCHSIZE",
        "School_SES",
    ]
    linear = [
        "ESCS",
        "Home_ICT",
        "School_ICT",
        "ESCS_x_Home_ICT",
        "ESCS_x_School_ICT",
    ] + controls
    quadratic = [
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

    result_frames = []
    grid_frames = []
    for weight_name, adjustment in [
        ("complete_case", None),
        ("selection_ipw", ipw_adjustment.to_numpy(float)),
    ]:
        for specification, columns in [("linear", linear), ("quadratic", quadratic)]:
            print(f"Estimating {weight_name} / {specification}...")
            estimates, sampling = estimate_brr(
                frame, columns, y_columns, selection_adjustment=adjustment
            )
            combined = combine_pvs(estimates, sampling, columns)
            combined.insert(0, "weighting", weight_name)
            combined.insert(1, "specification", specification)
            result_frames.append(combined)
            grid = marginal_grid(combined, specification)
            grid.insert(0, "weighting", weight_name)
            grid_frames.append(grid)

    results = pd.concat(result_frames, ignore_index=True)
    grids = pd.concat(grid_frames, ignore_index=True)
    results.to_csv(OUT_DIR / "core_model_results.csv", index=False)
    grids.to_csv(OUT_DIR / "conditional_slope_grid.csv", index=False)

    key_terms = results[results["variable"].str.startswith("ESCS_x_")].copy()
    summary = f"""# Corrected Core-Model Results

- Eligible education systems: {frame['CNT'].nunique()}
- Complete-core students: {len(frame):,}
- Former BELONG control: excluded from primary models
- Country contribution: equalised through within-system weight rescaling
- Country intercepts: absorbed in every full-sample and replicate estimate
- Home and school resource channels: estimated jointly

## Interaction coefficients

{key_terms[['weighting', 'specification', 'subject', 'variable', 'coef', 'se', 'p_value']].to_markdown(index=False)}

The quadratic specification includes both `ESCS x resource` and
`ESCS x resource squared`; interpretation must therefore use conditional slopes
rather than the sign of one interaction coefficient.
"""
    (OUT_DIR / "core_model_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
