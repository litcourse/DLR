import numpy as np
import pandas as pd

from pisa_analysis import (
    COUNTRY_NAMES,
    FINAL_WEIGHT_COL,
    SELECTED_CNTS,
    load_and_prepare_data,
    output_dir,
    weighted_corr,
    weighted_mean,
    weighted_var,
)


def pv_descriptive(df, prefix, label):
    pv_cols = [f"PV{i}{prefix}" for i in range(1, 11)]
    means = [weighted_mean(df[col], df[FINAL_WEIGHT_COL]) for col in pv_cols]
    variances = [weighted_var(df[col], df[FINAL_WEIGHT_COL]) for col in pv_cols]
    all_values = df[pv_cols].to_numpy(dtype=float)
    return {
        "Variable": label,
        "Mean": float(np.nanmean(means)),
        "SD": float(np.sqrt(np.nanmean(variances))),
        "Min": float(np.nanmin(all_values)),
        "Max": float(np.nanmax(all_values)),
    }


def weighted_descriptive(df, col, label):
    return {
        "Variable": label,
        "Mean": weighted_mean(df[col], df[FINAL_WEIGHT_COL]),
        "SD": np.sqrt(weighted_var(df[col], df[FINAL_WEIGHT_COL])),
        "Min": df[col].min(),
        "Max": df[col].max(),
    }


def sample_table(df):
    rows = []
    for cnt in SELECTED_CNTS:
        sub = df[df["CNT"] == cnt]
        rows.append(
            {
                "Code": cnt,
                "Country": COUNTRY_NAMES[cnt],
                "Students": len(sub),
                "Schools": sub["SchoolID"].nunique(),
            }
        )
    table = pd.DataFrame(rows)
    table.loc[len(table)] = {
        "Code": "Total",
        "Country": "",
        "Students": int(table["Students"].sum()),
        "Schools": int(table["Schools"].sum()),
    }
    return table


def descriptive_table(df):
    rows = [
        pv_descriptive(df, "MATH", "Math Score"),
        pv_descriptive(df, "READ", "Reading Score"),
        pv_descriptive(df, "SCIE", "Science Score"),
    ]
    rows += [
        weighted_descriptive(df, "ESCS", "ESCS"),
        weighted_descriptive(df, "Home_ICT", "Home ICT (ICTRES)"),
        weighted_descriptive(df, "School_ICT", "School ICT (RATCMP1)"),
        weighted_descriptive(df, "School_SES", "School-average SES"),
        weighted_descriptive(df, "Male", "Male"),
        weighted_descriptive(df, "Grade", "Grade"),
        weighted_descriptive(df, "Immigrant", "Immigrant"),
        weighted_descriptive(df, "Belonging", "Belonging"),
        weighted_descriptive(df, "Private", "Private"),
        weighted_descriptive(df, "Urban", "Urban"),
        weighted_descriptive(df, "STRatio", "Student-Teacher Ratio"),
        weighted_descriptive(df, "SchoolSize", "School Size"),
    ]
    return pd.DataFrame(rows)


def correlation_table(df):
    labels = ["Math Score", "ESCS", "Home ICT", "School ICT", "School SES"]
    non_pv_cols = ["ESCS", "Home_ICT", "School_ICT", "School_SES"]
    matrices = []
    for i in range(1, 11):
        cols = [f"PV{i}MATH"] + non_pv_cols
        mat = np.eye(len(cols))
        for r in range(len(cols)):
            for c in range(r + 1, len(cols)):
                mat[r, c] = mat[c, r] = weighted_corr(df[cols[r]], df[cols[c]], df[FINAL_WEIGHT_COL])
        matrices.append(mat)
    corr = np.nanmean(np.stack(matrices, axis=0), axis=0)
    return pd.DataFrame(corr, index=labels, columns=labels)


def main():
    df = load_and_prepare_data(standardize=False)
    out = output_dir()

    tbl1 = sample_table(df)
    tbl2 = descriptive_table(df)
    tbl3 = correlation_table(df)

    tbl1.to_csv(out / "table1_sample.csv", index=False)
    tbl2.to_csv(out / "table2_descriptive.csv", index=False)
    tbl3.to_csv(out / "table3_correlations.csv")

    summary_path = out / "tables_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("--- Table 1: Sample Countries and Sizes ---\n")
        f.write(tbl1.to_string(index=False))
        f.write("\n\n--- Table 2: Weighted Descriptive Statistics ---\n")
        f.write(
            tbl2.to_string(
                index=False,
                formatters={
                    "Mean": "{:.3f}".format,
                    "SD": "{:.3f}".format,
                    "Min": "{:.3f}".format,
                    "Max": "{:.3f}".format,
                },
            )
        )
        f.write("\n\n--- Table 3: Weighted Correlation Matrix ---\n")
        f.write(tbl3.to_string(float_format="{:.3f}".format))

    print(summary_path.read_text(encoding="utf-8"))
    print("\nSaved table CSV files under outputs/.")


if __name__ == "__main__":
    main()
