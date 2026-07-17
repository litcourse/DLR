"""Country-specific moderation estimates and random-effects synthesis."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from revision_core_analysis import (
    OUT_DIR,
    SUBJECTS,
    add_model_terms,
    combine_pvs,
    estimate_brr,
    prepare_data,
)


TARGET_TERMS = [
    "ESCS_x_Home_ICT",
    "ESCS_x_Home_ICT_sq",
    "ESCS_x_School_ICT",
    "ESCS_x_School_ICT_sq",
]


def random_effects(group: pd.DataFrame) -> dict[str, float]:
    usable = group[
        np.isfinite(group["coef"])
        & np.isfinite(group["se"])
        & (group["se"] > 0)
    ].copy()
    y = usable["coef"].to_numpy(float)
    v = usable["se"].to_numpy(float) ** 2
    k = len(y)
    if k < 2:
        return {
            "k": k,
            "pooled_coef": np.nan,
            "pooled_se": np.nan,
            "p_value": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "tau2": np.nan,
            "Q": np.nan,
            "Q_p_value": np.nan,
            "I2": np.nan,
            "positive_systems": int((y > 0).sum()),
            "negative_systems": int((y < 0).sum()),
        }
    w = 1.0 / v
    fixed = np.sum(w * y) / np.sum(w)
    q = np.sum(w * (y - fixed) ** 2)
    c = np.sum(w) - np.sum(w**2) / np.sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    wr = 1.0 / (v + tau2)
    pooled = np.sum(wr * y) / np.sum(wr)
    pooled_se = np.sqrt(1.0 / np.sum(wr))
    p_value = 2.0 * stats.norm.sf(abs(pooled / pooled_se))
    i2 = max(0.0, (q - (k - 1)) / q) * 100.0 if q > 0 else 0.0
    return {
        "k": k,
        "pooled_coef": pooled,
        "pooled_se": pooled_se,
        "p_value": p_value,
        "ci_low": pooled - 1.96 * pooled_se,
        "ci_high": pooled + 1.96 * pooled_se,
        "tau2": tau2,
        "Q": q,
        "Q_p_value": stats.chi2.sf(q, k - 1),
        "I2": i2,
        "positive_systems": int((y > 0).sum()),
        "negative_systems": int((y < 0).sum()),
    }


def main() -> None:
    frame, ipw_adjustment, _ = prepare_data()
    add_model_terms(frame)
    frame["selection_adjustment"] = ipw_adjustment.to_numpy(float)

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

    country_results = []
    for cnt, sub in frame.groupby("CNT", sort=True):
        print(f"Estimating {cnt} ({len(sub):,} students)...")
        estimable = []
        for column in quadratic:
            values = sub[column].to_numpy(float)
            if np.nanstd(values) > 1e-8:
                estimable.append(column)
        missing_targets = [term for term in TARGET_TERMS if term not in estimable]
        if missing_targets:
            for subject in SUBJECTS:
                for term in missing_targets:
                    country_results.append(
                        {
                            "CNT": cnt,
                            "students": len(sub),
                            "subject": subject,
                            "variable": term,
                            "coef": np.nan,
                            "se": np.nan,
                            "p_value": np.nan,
                            "ci_low": np.nan,
                            "ci_high": np.nan,
                        }
                    )
        if not all(term in estimable for term in TARGET_TERMS):
            continue
        estimates, sampling = estimate_brr(
            sub,
            estimable,
            y_columns,
            selection_adjustment=sub["selection_adjustment"].to_numpy(float),
        )
        combined = combine_pvs(estimates, sampling, estimable)
        combined = combined[combined["variable"].isin(TARGET_TERMS)].copy()
        combined.insert(0, "CNT", cnt)
        combined.insert(1, "students", len(sub))
        country_results.extend(combined.to_dict("records"))

    country = pd.DataFrame(country_results)
    country.to_csv(OUT_DIR / "country_specific_moderation.csv", index=False)

    meta_rows = []
    for (subject, variable), group in country.groupby(["subject", "variable"]):
        meta_rows.append(
            {
                "subject": subject,
                "variable": variable,
                **random_effects(group),
            }
        )
    meta = pd.DataFrame(meta_rows)
    meta.to_csv(OUT_DIR / "country_random_effects_meta.csv", index=False)

    focal = meta[meta["variable"].isin(["ESCS_x_Home_ICT", "ESCS_x_School_ICT"])]
    summary = f"""# Cross-System Heterogeneity

Country-specific models use the fully hierarchical quadratic specification,
selection adjustment, final student weights, 80 Fay BRR replicate weights, and
10 plausible values. Each system is standardized internally before estimation.

## Random-effects synthesis at the mean resource level

{focal[['subject', 'variable', 'k', 'pooled_coef', 'pooled_se', 'p_value', 'tau2', 'Q_p_value', 'I2', 'positive_systems', 'negative_systems']].to_markdown(index=False)}

`ESCS_x_resource` is the difference in the conditional resource slope by ESCS
when the standardized resource is at its system-specific mean. Large I2 values
indicate that a single common interaction is not an adequate description of all
education systems.
"""
    (OUT_DIR / "country_heterogeneity_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
