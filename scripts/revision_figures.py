"""Create publication figures for the clean post-SEE manuscript."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "revision_submission" / "analysis" / "multiple_imputation_results.csv"
OUT_DIR = ROOT / "revision_submission" / "figures"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = pd.read_csv(RESULTS)
    panels = [
        ("ESCS_x_Home_ICT", "Home ICT availability"),
        ("ESCS_x_School_ICT", "School computer provision"),
    ]
    domains = ["Math", "Reading", "Science"]
    labels = {"Math": "Mathematics", "Reading": "Reading", "Science": "Science"}
    colors = {"Math": "#2F5597", "Reading": "#C55A11", "Science": "#548235"}

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), sharey=True)
    for axis, (variable, title) in zip(axes, panels):
        subset = results[results["variable"].eq(variable)].set_index("subject")
        for position, domain in enumerate(domains):
            row = subset.loc[domain]
            lower = row["coef"] - row["ci_low"]
            upper = row["ci_high"] - row["coef"]
            axis.errorbar(
                row["coef"],
                position,
                xerr=[[lower], [upper]],
                fmt="o",
                color=colors[domain],
                capsize=3,
                markersize=6,
                linewidth=1.5,
            )
        axis.axvline(0, color="#666666", linestyle="--", linewidth=1)
        axis.set_title(title, fontsize=11, weight="bold")
        axis.set_xlabel("ESCS × resource coefficient (score points)")
        axis.grid(axis="x", color="#D9D9D9", linewidth=0.6)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(axis="y", length=0)
    axes[0].set_yticks(range(len(domains)), [labels[domain] for domain in domains])
    axes[0].invert_yaxis()
    fig.suptitle("Socioeconomic moderation differs between home and school resources", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Fig1_moderation_coefficients.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "Fig1_moderation_coefficients.png", dpi=400, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
