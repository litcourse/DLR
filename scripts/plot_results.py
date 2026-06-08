from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def project_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "outputs" / "regression_results_long.csv").exists():
        return cwd
    package_root = Path(__file__).resolve().parents[1]
    return package_root


def coef(results, model, variable):
    row = results[
        (results["Subject"] == "Math")
        & (results["Model"] == model)
        & (results["Variable"] == variable)
    ]
    if row.empty:
        raise KeyError(f"Missing coefficient for {model}: {variable}")
    return float(row.iloc[0]["Coef"])


def save_to_targets(fig, filename):
    root = project_root()
    targets = [root / "figures"]
    manuscript_figures = root / "mdpi_submission" / "figures"
    if manuscript_figures.exists():
        targets.append(manuscript_figures)
    for target in targets:
        target.mkdir(exist_ok=True)
        fig.savefig(target / f"{filename}.pdf")
        fig.savefig(target / f"{filename}.png")


def plot_interaction(ax, ict_range, y_low, y_avg, y_high, xlabel, title, show_ylabel=False, show_legend=False):
    low_ses_color = "#2A9D8F"
    avg_ses_color = "#264653"
    high_ses_color = "#E76F51"

    ax.plot(ict_range, y_low, label="Low SES (ESCS = -1 SD)", color=low_ses_color, linestyle="--", marker="o", markevery=15)
    ax.plot(ict_range, y_avg, label="Average SES (ESCS = 0)", color=avg_ses_color, linestyle="-", marker="s", markevery=15)
    ax.plot(ict_range, y_high, label="High SES (ESCS = +1 SD)", color=high_ses_color, linestyle="-.", marker="^", markevery=15)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    if show_ylabel:
        ax.set_ylabel("Predicted Math Score")
    if show_legend:
        ax.legend(loc="lower left", fontsize=6.8, framealpha=0.9)


def generate_interaction_plots():
    results_path = project_root() / "outputs" / "regression_results_long.csv"
    if not results_path.exists():
        raise FileNotFoundError("Run scripts/run_regression.py before generating plots.")
    results = pd.read_csv(results_path)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "legend.fontsize": 8.5,
            "legend.frameon": True,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.15,
            "grid.linestyle": "-",
            "lines.linewidth": 1.8,
            "lines.markersize": 5,
        }
    )

    ict_range = np.linspace(-2, 2, 100)

    beta0 = coef(results, "Model 3 (Home ICT Interaction)", "Intercept")
    beta_escs = coef(results, "Model 3 (Home ICT Interaction)", "ESCS")
    beta_ict = coef(results, "Model 3 (Home ICT Interaction)", "Home_ICT")
    beta_int = coef(results, "Model 3 (Home ICT Interaction)", "ESCS_x_Home_ICT")
    y_low = beta0 + beta_escs * (-1) + beta_ict * ict_range + beta_int * (-1) * ict_range
    y_avg = beta0 + beta_ict * ict_range
    y_high = beta0 + beta_escs + beta_ict * ict_range + beta_int * ict_range
    home_series = (y_low, y_avg, y_high)

    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    plot_interaction(
        ax,
        ict_range,
        *home_series,
        xlabel="Home Digital Resources (Standardized)",
        title="Interaction Effect of Home Digital Resources and SES\non Mathematics Achievement",
        show_ylabel=True,
        show_legend=True,
    )
    save_to_targets(fig, "fig_interaction_home_math")
    plt.close(fig)

    beta0 = coef(results, "Model 4 (School ICT Interaction)", "Intercept")
    beta_escs = coef(results, "Model 4 (School ICT Interaction)", "ESCS")
    beta_ict = coef(results, "Model 4 (School ICT Interaction)", "School_ICT")
    beta_int = coef(results, "Model 4 (School ICT Interaction)", "ESCS_x_School_ICT")
    y_low = beta0 + beta_escs * (-1) + beta_ict * ict_range + beta_int * (-1) * ict_range
    y_avg = beta0 + beta_ict * ict_range
    y_high = beta0 + beta_escs + beta_ict * ict_range + beta_int * ict_range
    school_series = (y_low, y_avg, y_high)

    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    plot_interaction(
        ax,
        ict_range,
        *school_series,
        xlabel="School Digital Resources (Standardized)",
        title="Interaction Effect of School Digital Resources and SES\non Mathematics Achievement",
        show_ylabel=True,
        show_legend=True,
    )
    save_to_targets(fig, "fig_interaction_school_math")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(5.8, 2.75), sharey=True)
    plot_interaction(
        axes[0],
        ict_range,
        *home_series,
        xlabel="Home ICT (standardized)",
        title="(a) Home ICT",
        show_ylabel=True,
        show_legend=True,
    )
    plot_interaction(
        axes[1],
        ict_range,
        *school_series,
        xlabel="School ICT (standardized)",
        title="(b) School ICT",
    )
    fig.tight_layout(pad=0.7, w_pad=0.8)
    save_to_targets(fig, "fig_interactions_math")
    plt.close(fig)

    print("Interaction plots generated from outputs/regression_results_long.csv.")


if __name__ == "__main__":
    generate_interaction_plots()
