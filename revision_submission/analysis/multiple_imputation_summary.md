# Multiple-Imputation Results

- Education systems: 51
- Students retained after imputation: 387,494
- Completed datasets: 10
- School variables imputed on a unique-school file before student-level imputation
- Within-system predictive mean matching with 5 donors and 3 cycles
- Variance combines Fay BRR sampling, plausible-value, and imputation components

## Focal coefficients

| subject   | variable             |         coef |        se |     p_value |     ci_low |    ci_high |
|:----------|:---------------------|-------------:|----------:|------------:|-----------:|-----------:|
| Math      | Home_ICT             |  4.92987     | 0.364196  | 9.54471e-42 |  4.21605   |  5.6437    |
| Math      | Home_ICT_sq          | -0.752272    | 0.0948049 | 2.10598e-15 | -0.938089  | -0.566454  |
| Math      | School_ICT           |  0.909396    | 0.368099  | 0.0134915   |  0.187923  |  1.63087   |
| Math      | School_ICT_sq        | -0.341499    | 0.245094  | 0.163517    | -0.821883  |  0.138885  |
| Math      | ESCS_x_Home_ICT      |  1.5849      | 0.35241   | 6.88184e-06 |  0.894175  |  2.27562   |
| Math      | ESCS_x_Home_ICT_sq   |  0.0799773   | 0.0856488 | 0.350417    | -0.0878944 |  0.247849  |
| Math      | ESCS_x_School_ICT    | -0.352499    | 0.308603  | 0.253354    | -0.957362  |  0.252363  |
| Math      | ESCS_x_School_ICT_sq | -0.0177038   | 0.147926  | 0.904736    | -0.307639  |  0.272231  |
| Reading   | Home_ICT             |  5.71594     | 0.438723  | 8.41487e-39 |  4.85605   |  6.57584   |
| Reading   | Home_ICT_sq          | -0.937506    | 0.125074  | 6.5992e-14  | -1.18265   | -0.692361  |
| Reading   | School_ICT           |  1.03669     | 0.426044  | 0.0149625   |  0.201641  |  1.87173   |
| Reading   | School_ICT_sq        | -0.321185    | 0.220877  | 0.145908    | -0.754103  |  0.111733  |
| Reading   | ESCS_x_Home_ICT      |  1.69595     | 0.348341  | 1.12366e-06 |  1.0132    |  2.3787    |
| Reading   | ESCS_x_Home_ICT_sq   |  0.0883272   | 0.0889811 | 0.32088     | -0.0860758 |  0.26273   |
| Reading   | ESCS_x_School_ICT    | -0.696578    | 0.324718  | 0.0319383   | -1.33303   | -0.0601317 |
| Reading   | ESCS_x_School_ICT_sq | -0.0919413   | 0.162154  | 0.570715    | -0.409764  |  0.225881  |
| Science   | Home_ICT             |  5.00222     | 0.413346  | 1.03338e-33 |  4.19206   |  5.81238   |
| Science   | Home_ICT_sq          | -0.927551    | 0.120057  | 1.11034e-14 | -1.16286   | -0.69224   |
| Science   | School_ICT           |  1.1         | 0.389964  | 0.00479064  |  0.335675  |  1.86433   |
| Science   | School_ICT_sq        | -0.254567    | 0.238094  | 0.284986    | -0.721231  |  0.212098  |
| Science   | ESCS_x_Home_ICT      |  1.48855     | 0.391333  | 0.000142498 |  0.721536  |  2.25556   |
| Science   | ESCS_x_Home_ICT_sq   |  0.0314276   | 0.0975452 | 0.747313    | -0.159761  |  0.222616  |
| Science   | ESCS_x_School_ICT    | -0.519987    | 0.340881  | 0.127154    | -1.18811   |  0.14814   |
| Science   | ESCS_x_School_ICT_sq | -8.51219e-05 | 0.160459  | 0.999577    | -0.314584  |  0.314414  |
