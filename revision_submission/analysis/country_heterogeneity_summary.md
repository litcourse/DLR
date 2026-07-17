# Cross-System Heterogeneity

Country-specific models use the fully hierarchical quadratic specification,
selection adjustment, final student weights, 80 Fay BRR replicate weights, and
10 plausible values. Each system is standardized internally before estimation.

## Random-effects synthesis at the mean resource level

| subject   | variable          |   k |   pooled_coef |   pooled_se |    p_value |    tau2 |   Q_p_value |      I2 |   positive_systems |   negative_systems |
|:----------|:------------------|----:|--------------:|------------:|-----------:|--------:|------------:|--------:|-------------------:|-------------------:|
| Math      | ESCS_x_Home_ICT   |  51 |      1.35757  |    0.522776 | 0.00940838 | 4.73998 |  0.00625989 | 36.2472 |                 35 |                 16 |
| Math      | ESCS_x_School_ICT |  51 |     -0.291622 |    0.261483 | 0.264738   | 0.38397 |  0.244081   | 11.5623 |                 26 |                 25 |
| Reading   | ESCS_x_Home_ICT   |  51 |      1.43592  |    0.59481  | 0.015775   | 5.62143 |  0.0133272  | 33.0787 |                 31 |                 20 |
| Reading   | ESCS_x_School_ICT |  51 |     -0.67885  |    0.275807 | 0.0138426  | 0       |  0.618742   |  0      |                 20 |                 31 |
| Science   | ESCS_x_Home_ICT   |  51 |      1.17755  |    0.582208 | 0.0431195  | 5.49674 |  0.011549   | 33.7194 |                 33 |                 18 |
| Science   | ESCS_x_School_ICT |  51 |     -0.645058 |    0.264825 | 0.0148593  | 0       |  0.509142   |  0      |                 24 |                 27 |

`ESCS_x_resource` is the difference in the conditional resource slope by ESCS
when the standardized resource is at its system-specific mean. Large I2 values
indicate that a single common interaction is not an adequate description of all
education systems.
