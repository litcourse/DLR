from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import scipy.stats as stats


SELECTED_CNTS = ["USA", "GBR", "DEU", "FRA", "AUS", "CAN", "SGP", "NZL", "SWE", "IRL"]
COUNTRY_NAMES = {
    "AUS": "Australia",
    "CAN": "Canada",
    "DEU": "Germany",
    "FRA": "France",
    "GBR": "United Kingdom",
    "IRL": "Ireland",
    "NZL": "New Zealand",
    "SGP": "Singapore",
    "SWE": "Sweden",
    "USA": "United States",
}
SUBJECTS = {"Math": "MATH", "Reading": "READ", "Science": "SCIE"}
REPLICATE_WEIGHT_COLS = [f"W_FSTURWT{i}" for i in range(1, 81)]
FINAL_WEIGHT_COL = "W_FSTUWT"
FAY_COEFFICIENT = 0.5


def project_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "data").exists():
        return cwd
    package_root = Path(__file__).resolve().parents[1]
    return package_root


def data_paths() -> tuple[Path, Path]:
    root = project_root()
    return root / "data" / "CY08MSP_STU_QQQ.SAV", root / "data" / "CY08MSP_SCH_QQQ.SAV"


def output_dir() -> Path:
    out = project_root() / "outputs"
    out.mkdir(exist_ok=True)
    return out


def weighted_mean(values, weights):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return np.nan
    return np.average(values[mask], weights=weights[mask])


def weighted_var(values, weights):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return np.nan
    mean = np.average(values[mask], weights=weights[mask])
    return np.average((values[mask] - mean) ** 2, weights=weights[mask])


def weighted_quantile(values, weights, quantile):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return np.nan
    values = values[mask]
    weights = weights[mask]
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cumulative = np.cumsum(weights) - 0.5 * weights
    cumulative = cumulative / np.sum(weights)
    return np.interp(quantile, cumulative, values)


def weighted_corr(x, y, weights):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(weights) & (weights > 0)
    if mask.sum() < 3:
        return np.nan
    x = x[mask]
    y = y[mask]
    weights = weights[mask]
    mx = np.average(x, weights=weights)
    my = np.average(y, weights=weights)
    vx = np.average((x - mx) ** 2, weights=weights)
    vy = np.average((y - my) ** 2, weights=weights)
    if vx <= 0 or vy <= 0:
        return np.nan
    cov = np.average((x - mx) * (y - my), weights=weights)
    return cov / np.sqrt(vx * vy)


def fill_by_country(df, col, method="median"):
    if method == "mean":
        values = df.groupby("CNT")[col].transform(lambda x: x.fillna(x.mean()))
        return values.fillna(df[col].mean())
    values = df.groupby("CNT")[col].transform(lambda x: x.fillna(x.median()))
    return values.fillna(df[col].median())


def fill_binary_by_country(df, col):
    def country_mode(x):
        modes = x.mode(dropna=True)
        return modes.iloc[0] if len(modes) else np.nan

    global_modes = df[col].mode(dropna=True)
    global_mode = global_modes.iloc[0] if len(global_modes) else 0.0
    modes = df.groupby("CNT")[col].transform(lambda x: country_mode(x))
    return df[col].fillna(modes).fillna(global_mode).astype(float)


def load_and_prepare_data(standardize=False):
    stu_path, sch_path = data_paths()
    if not stu_path.exists() or not sch_path.exists():
        raise FileNotFoundError("PISA .SAV files are missing. Run scripts/download_data.py first.")

    pv_cols = (
        [f"PV{i}MATH" for i in range(1, 11)]
        + [f"PV{i}READ" for i in range(1, 11)]
        + [f"PV{i}SCIE" for i in range(1, 11)]
    )
    cols_stu = [
        "CNT",
        "CNTSCHID",
        "CNTSTUID",
        "ESCS",
        "ST004D01T",
        "GRADE",
        "IMMIG",
        "BELONG",
        "ICTRES",
        FINAL_WEIGHT_COL,
    ] + REPLICATE_WEIGHT_COLS + pv_cols
    cols_sch = ["CNT", "CNTSCHID", "RATCMP1", "PRIVATESCH", "SC001Q01TA", "STRATIO", "SCHSIZE"]

    print("Loading student data with final and replicate weights...")
    df_stu, _ = pyreadstat.read_sav(str(stu_path), usecols=cols_stu)
    df_stu = df_stu[df_stu["CNT"].isin(SELECTED_CNTS)].copy()
    print(f"Loaded {len(df_stu):,} student records from selected countries.")

    print("Loading school data...")
    df_sch, _ = pyreadstat.read_sav(str(sch_path), usecols=cols_sch)
    df_sch = df_sch[df_sch["CNT"].isin(SELECTED_CNTS)].copy()
    print(f"Loaded {len(df_sch):,} school records from selected countries.")

    df = pd.merge(df_stu, df_sch, on=["CNT", "CNTSCHID"], how="left")
    df["SchoolID"] = df["CNT"].astype(str) + "_" + df["CNTSCHID"].astype(str)

    valid_ses = df["ESCS"].notna() & df[FINAL_WEIGHT_COL].notna() & (df[FINAL_WEIGHT_COL] > 0)
    school_num = (df.loc[valid_ses, "ESCS"] * df.loc[valid_ses, FINAL_WEIGHT_COL]).groupby(
        df.loc[valid_ses, "SchoolID"]
    ).sum()
    school_den = df.loc[valid_ses].groupby("SchoolID")[FINAL_WEIGHT_COL].sum()
    school_ses = (school_num / school_den).rename("School_SES").reset_index()
    df = pd.merge(df, school_ses, on="SchoolID", how="left")

    df["Male"] = np.where(df["ST004D01T"].isin([1.0, 2.0]), (df["ST004D01T"] == 2.0).astype(float), np.nan)
    df["Immigrant"] = np.where(df["IMMIG"].isin([1.0, 2.0, 3.0]), df["IMMIG"].isin([2.0, 3.0]).astype(float), np.nan)
    private_text = df["PRIVATESCH"].astype("string").str.lower()
    df["Private"] = np.where(
        private_text.str.contains("private", na=False),
        1.0,
        np.where(private_text.str.contains("public", na=False), 0.0, np.nan),
    )
    df["Urban"] = np.where(
        df["SC001Q01TA"].isin([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        df["SC001Q01TA"].isin([3.0, 4.0, 5.0, 6.0]).astype(float),
        np.nan,
    )

    df["Grade"] = fill_by_country(df, "GRADE", "median")
    df["Belonging"] = fill_by_country(df, "BELONG", "mean")
    df["STRatio"] = fill_by_country(df, "STRATIO", "median")
    df["SchoolSize"] = fill_by_country(df, "SCHSIZE", "median")
    df["Male"] = fill_binary_by_country(df, "Male")
    df["Immigrant"] = fill_binary_by_country(df, "Immigrant")
    df["Private"] = fill_binary_by_country(df, "Private")
    df["Urban"] = fill_binary_by_country(df, "Urban")

    df["Home_ICT"] = df["ICTRES"]
    cap_value = weighted_quantile(df["RATCMP1"], df[FINAL_WEIGHT_COL], 0.99)
    df["School_ICT"] = df["RATCMP1"].clip(upper=cap_value)

    required = ["ESCS", "Home_ICT", "School_ICT", "School_SES", FINAL_WEIGHT_COL] + REPLICATE_WEIGHT_COLS
    df_clean = df.dropna(subset=required).copy()
    print(f"Analytic sample after dropping missing core resources: {len(df_clean):,} students.")

    if standardize:
        continuous = ["ESCS", "Home_ICT", "School_ICT", "School_SES", "STRatio", "SchoolSize", "Belonging", "Grade"]
        for col in continuous:
            mean = weighted_mean(df_clean[col], df_clean[FINAL_WEIGHT_COL])
            sd = np.sqrt(weighted_var(df_clean[col], df_clean[FINAL_WEIGHT_COL]))
            df_clean[col] = (df_clean[col] - mean) / sd

    return df_clean


def regression_models(df):
    country_dummies = pd.get_dummies(df["CNT"], prefix="CNT", drop_first=True).astype(float)
    df_reg = pd.concat([df.reset_index(drop=True), country_dummies.reset_index(drop=True)], axis=1)
    df_reg["ESCS_x_Home_ICT"] = df_reg["ESCS"] * df_reg["Home_ICT"]
    df_reg["ESCS_x_School_ICT"] = df_reg["ESCS"] * df_reg["School_ICT"]
    cnt_cols = list(country_dummies.columns)
    controls = ["Male", "Grade", "Immigrant", "Belonging", "Private", "Urban", "STRatio", "SchoolSize", "School_SES"]
    controls += cnt_cols
    return df_reg, {
        "Model 1 (Baseline)": ["Intercept", "ESCS"] + controls,
        "Model 2 (Add ICT)": ["Intercept", "ESCS", "Home_ICT", "School_ICT"] + controls,
        "Model 3 (Home ICT Interaction)": [
            "Intercept",
            "ESCS",
            "Home_ICT",
            "School_ICT",
            "ESCS_x_Home_ICT",
        ]
        + controls,
        "Model 4 (School ICT Interaction)": [
            "Intercept",
            "ESCS",
            "Home_ICT",
            "School_ICT",
            "ESCS_x_School_ICT",
        ]
        + controls,
    }


def solve_wls(X, Y, weights):
    weights = np.asarray(weights, dtype=float)
    weights = weights / np.nanmean(weights)
    xtx = X.T @ (X * weights[:, None])
    xty = X.T @ (Y * weights[:, None])
    try:
        return np.linalg.solve(xtx, xty)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(xtx) @ xty


def estimate_with_replicates(X_df, Y_df, final_weights, replicate_weights):
    X = X_df.to_numpy(dtype=float)
    Y = Y_df.to_numpy(dtype=float)
    full_beta = solve_wls(X, Y, final_weights.to_numpy(dtype=float))

    replicate_diffs = []
    for col in REPLICATE_WEIGHT_COLS:
        rep_beta = solve_wls(X, Y, replicate_weights[col].to_numpy(dtype=float))
        replicate_diffs.append((rep_beta - full_beta) ** 2)
    sampling_var = np.sum(replicate_diffs, axis=0) / (len(REPLICATE_WEIGHT_COLS) * (1.0 - FAY_COEFFICIENT) ** 2)
    return full_beta.T, sampling_var.T


def combine_plausible_values(estimates, sampling_vars, covariates):
    m = estimates.shape[0]
    point = estimates.mean(axis=0)
    within = sampling_vars.mean(axis=0)
    between = estimates.var(axis=0, ddof=1)
    total = within + (1.0 + 1.0 / m) * between
    se = np.sqrt(np.maximum(total, 0.0))
    t_stat = point / se
    p_values = 2.0 * (1.0 - stats.norm.cdf(np.abs(t_stat)))
    return pd.DataFrame(
        {
            "Variable": covariates,
            "Coef": point,
            "SE": se,
            "t": t_stat,
            "p-value": p_values,
        }
    )


def run_subject_regressions(df, subject_suffix):
    df_reg, models = regression_models(df)
    pv_cols = [f"PV{i}{subject_suffix}" for i in range(1, 11)]
    results = {}
    for model_name, covariates in models.items():
        print(f"  Running {model_name}...")
        frame = df_reg[pv_cols + [FINAL_WEIGHT_COL] + REPLICATE_WEIGHT_COLS + [c for c in covariates if c != "Intercept"]].copy()
        frame["Intercept"] = 1.0
        frame = frame.dropna(subset=pv_cols + covariates + [FINAL_WEIGHT_COL] + REPLICATE_WEIGHT_COLS)
        estimates, sampling_vars = estimate_with_replicates(
            frame[covariates],
            frame[pv_cols],
            frame[FINAL_WEIGHT_COL],
            frame[REPLICATE_WEIGHT_COLS],
        )
        results[model_name] = combine_plausible_values(estimates, sampling_vars, covariates)
    return results


def significance_stars(p_value):
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return ""


def result_long_frame(results_all):
    rows = []
    for subject, models in results_all.items():
        for model_name, table in models.items():
            for _, row in table.iterrows():
                rows.append({"Subject": subject, "Model": model_name, **row.to_dict()})
    return pd.DataFrame(rows)


def write_regression_outputs(results_all):
    long_df = result_long_frame(results_all)
    out = output_dir()
    long_df.to_csv(out / "regression_results_long.csv", index=False)

    root_file = project_root() / "regression_results.txt"
    with root_file.open("w", encoding="utf-8") as f:
        f.write("Method: WLS with PISA final student weights, 80 Fay BRR replicate weights, and 10 plausible values.\n")
        f.write("Plausible-value estimates are combined using Rubin's rules; replicate weights estimate sampling variance.\n\n")
        for subject, models in results_all.items():
            f.write("=" * 78 + "\n")
            f.write(f"SUBJECT: {subject.upper()}\n")
            f.write("=" * 78 + "\n\n")
            for model_name, table in models.items():
                f.write(f"--- {model_name} ---\n")
                f.write(
                    table.to_string(
                        index=False,
                        formatters={
                            "Coef": "{:,.4f}".format,
                            "SE": "{:,.4f}".format,
                            "t": "{:,.4f}".format,
                            "p-value": "{:,.4f}".format,
                        },
                    )
                )
                f.write("\n\n")
    return long_df
