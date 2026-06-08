# Replication Package

Paper: **Digital Learning Resources, Socioeconomic Inequality, and Sustainable Educational Equity: Cross-National Evidence from PISA 2022**

This package provides the Python scripts used to reproduce the analytic sample, descriptive tables, regression models, and interaction figures.

## Repository Structure

```text
replication_package/
  data/
    README.md
    README_zh.md
  scripts/
    pisa_analysis.py
    download_data.py
    get_tables.py
    run_regression.py
    plot_results.py
    test_custom_solver.py
```

## Requirements

Python 3.8+ is required. Install dependencies with:

```bash
pip install pandas numpy scipy pyreadstat matplotlib requests
```

## Data

The analysis uses the PISA 2022 student and school questionnaire SPSS files:

```text
data/CY08MSP_STU_QQQ.SAV
data/CY08MSP_SCH_QQQ.SAV
```

They can be downloaded from the OECD PISA 2022 database:

```text
https://www.oecd.org/pisa/data/2022database/
```

The provided `download_data.py` script may be used when the OECD download URLs are available from your network.

## Reproduction Steps

From the project root, run:

```bash
python scripts/get_tables.py
python scripts/run_regression.py
python scripts/plot_results.py
python scripts/test_custom_solver.py
```

The regression script uses:

- final student weights: `W_FSTUWT`
- 80 Fay BRR replicate weights: `W_FSTURWT1` to `W_FSTURWT80`
- 10 plausible values per achievement domain
- Rubin's rules for plausible-value combination

## Outputs

Running the scripts creates:

```text
outputs/table1_sample.csv
outputs/table2_descriptive.csv
outputs/table3_correlations.csv
outputs/regression_results_long.csv
regression_results.txt
figures/fig_interaction_home_math.png
figures/fig_interaction_school_math.png
```

The long regression CSV is the source used by `plot_results.py`, so figures are generated from the fitted model coefficients rather than hard-coded values.
