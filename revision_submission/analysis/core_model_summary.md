# Corrected Core-Model Results

- Eligible education systems: 51
- Complete-core students: 296,527
- Former BELONG control: excluded from primary models
- Country contribution: equalised through within-system weight rescaling
- Country intercepts: absorbed in every full-sample and replicate estimate
- Home and school resource channels: estimated jointly

## Interaction coefficients

| weighting     | specification   | subject   | variable             |       coef |        se |     p_value |
|:--------------|:----------------|:----------|:---------------------|-----------:|----------:|------------:|
| complete_case | linear          | Math      | ESCS_x_Home_ICT      |  1.2103    | 0.182076  | 2.98655e-11 |
| complete_case | linear          | Math      | ESCS_x_School_ICT    | -0.396832  | 0.281051  | 0.157963    |
| complete_case | linear          | Reading   | ESCS_x_Home_ICT      |  1.294     | 0.203881  | 2.19758e-10 |
| complete_case | linear          | Reading   | ESCS_x_School_ICT    | -0.825515  | 0.279208  | 0.00311024  |
| complete_case | linear          | Science   | ESCS_x_Home_ICT      |  1.2892    | 0.204736  | 3.03743e-10 |
| complete_case | linear          | Science   | ESCS_x_School_ICT    | -0.592229  | 0.302075  | 0.0499333   |
| complete_case | quadratic       | Math      | ESCS_x_Home_ICT      |  1.51316   | 0.397982  | 0.000143488 |
| complete_case | quadratic       | Math      | ESCS_x_Home_ICT_sq   |  0.0612309 | 0.0919888 | 0.505645    |
| complete_case | quadratic       | Math      | ESCS_x_School_ICT    | -0.383043  | 0.316822  | 0.226656    |
| complete_case | quadratic       | Math      | ESCS_x_School_ICT_sq | -0.0195788 | 0.167794  | 0.90711     |
| complete_case | quadratic       | Reading   | ESCS_x_Home_ICT      |  1.5336    | 0.388519  | 7.90353e-05 |
| complete_case | quadratic       | Reading   | ESCS_x_Home_ICT_sq   |  0.0391815 | 0.0941274 | 0.67722     |
| complete_case | quadratic       | Reading   | ESCS_x_School_ICT    | -0.694228  | 0.343495  | 0.0432725   |
| complete_case | quadratic       | Reading   | ESCS_x_School_ICT_sq | -0.13034   | 0.161116  | 0.418524    |
| complete_case | quadratic       | Science   | ESCS_x_Home_ICT      |  1.4627    | 0.426439  | 0.000603511 |
| complete_case | quadratic       | Science   | ESCS_x_Home_ICT_sq   |  0.0240323 | 0.0983618 | 0.806979    |
| complete_case | quadratic       | Science   | ESCS_x_School_ICT    | -0.582924  | 0.349317  | 0.0951667   |
| complete_case | quadratic       | Science   | ESCS_x_School_ICT_sq | -0.0151813 | 0.165417  | 0.926876    |
| selection_ipw | linear          | Math      | ESCS_x_Home_ICT      |  1.27154   | 0.237354  | 8.45341e-08 |
| selection_ipw | linear          | Math      | ESCS_x_School_ICT    | -0.372705  | 0.288254  | 0.19602     |
| selection_ipw | linear          | Reading   | ESCS_x_Home_ICT      |  1.28879   | 0.296578  | 1.38931e-05 |
| selection_ipw | linear          | Reading   | ESCS_x_School_ICT    | -0.710019  | 0.296472  | 0.0166253   |
| selection_ipw | linear          | Science   | ESCS_x_Home_ICT      |  1.27523   | 0.265284  | 1.53188e-06 |
| selection_ipw | linear          | Science   | ESCS_x_School_ICT    | -0.571615  | 0.316637  | 0.0710328   |
| selection_ipw | quadratic       | Math      | ESCS_x_Home_ICT      |  1.74007   | 0.484973  | 0.000333268 |
| selection_ipw | quadratic       | Math      | ESCS_x_Home_ICT_sq   |  0.110375  | 0.110207  | 0.316577    |
| selection_ipw | quadratic       | Math      | ESCS_x_School_ICT    | -0.319571  | 0.332108  | 0.335924    |
| selection_ipw | quadratic       | Math      | ESCS_x_School_ICT_sq | -0.0593738 | 0.176243  | 0.736202    |
| selection_ipw | quadratic       | Reading   | ESCS_x_Home_ICT      |  1.74587   | 0.464505  | 0.000170891 |
| selection_ipw | quadratic       | Reading   | ESCS_x_Home_ICT_sq   |  0.103784  | 0.109865  | 0.344836    |
| selection_ipw | quadratic       | Reading   | ESCS_x_School_ICT    | -0.560117  | 0.358684  | 0.118384    |
| selection_ipw | quadratic       | Reading   | ESCS_x_School_ICT_sq | -0.151911  | 0.174594  | 0.384255    |
| selection_ipw | quadratic       | Science   | ESCS_x_Home_ICT      |  1.60872   | 0.497927  | 0.0012343   |
| selection_ipw | quadratic       | Science   | ESCS_x_Home_ICT_sq   |  0.073831  | 0.108706  | 0.497025    |
| selection_ipw | quadratic       | Science   | ESCS_x_School_ICT    | -0.541007  | 0.368343  | 0.141898    |
| selection_ipw | quadratic       | Science   | ESCS_x_School_ICT_sq | -0.0374042 | 0.177971  | 0.833535    |

The quadratic specification includes both `ESCS x resource` and
`ESCS x resource squared`; interpretation must therefore use conditional slopes
rather than the sign of one interaction coefficient.
