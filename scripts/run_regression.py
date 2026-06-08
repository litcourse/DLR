from pisa_analysis import SUBJECTS, load_and_prepare_data, run_subject_regressions, write_regression_outputs


def main():
    df = load_and_prepare_data(standardize=True)
    results_all = {}

    for subject_name, suffix in SUBJECTS.items():
        print("\n" + "=" * 42)
        print(f"RUNNING REGRESSIONS FOR {subject_name.upper()}")
        print("=" * 42)
        results_all[subject_name] = run_subject_regressions(df, suffix)

        for model_name, table in results_all[subject_name].items():
            print(f"\nSummary for {model_name} ({subject_name}):")
            for var in ["Intercept", "ESCS", "Home_ICT", "School_ICT", "ESCS_x_Home_ICT", "ESCS_x_School_ICT"]:
                if var in table["Variable"].values:
                    row = table.loc[table["Variable"] == var].iloc[0]
                    print(
                        f"  {var:<22}: Coef = {row['Coef']:8.3f}, "
                        f"SE = {row['SE']:6.3f}, t = {row['t']:6.2f}, p = {row['p-value']:.4f}"
                    )

    write_regression_outputs(results_all)
    print("\nSaved regression_results.txt and outputs/regression_results_long.csv.")


if __name__ == "__main__":
    main()
