# Missing-Data Audit

The audit uses all 51 education systems meeting the primary
variable-availability rule. Pooled descriptive comparisons use final student
weights rescaled so that every education system contributes equal total weight.

## Core analytic retention

- Students before item-level exclusions: 387,494
- Complete on ESCS, ICTAVHOM, and RATCMP1: 296,527
- Complete-core retention rate: 76.5%

## Systems with the lowest complete-core retention

| CNT   |   students |   complete_core |   complete_core_rate |
|:------|-----------:|----------------:|---------------------:|
| BRA   |      10798 |            5606 |             0.51917  |
| DOM   |       6868 |            3674 |             0.534945 |
| PAN   |       4544 |            2479 |             0.545555 |
| GEO   |       6583 |            3698 |             0.56175  |
| MAR   |       6867 |            3921 |             0.570992 |
| GBR   |      12972 |            7618 |             0.587265 |
| ALB   |       6129 |            3600 |             0.587372 |
| ISR   |       6251 |            3758 |             0.601184 |
| DEU   |       6116 |            3694 |             0.60399  |
| HKG   |       5907 |            3626 |             0.613848 |

## Largest observable differences between retained and dropped students

| variable        |   retained_mean |   dropped_mean |   standardized_mean_difference |
|:----------------|----------------:|---------------:|-------------------------------:|
| Science_mean_PV |     476.925     |     428.88     |                       0.485071 |
| Math_mean_PV    |     467.498     |     420.743    |                       0.478539 |
| Reading_mean_PV |     463.954     |     416.52     |                       0.464384 |
| SCHSIZE         |     832.15      |     677.253    |                       0.254407 |
| GRADE           |      -0.0920806 |      -0.217611 |                       0.204082 |
| ESCS            |      -0.19115   |      -0.393437 |                       0.184247 |
| Urban           |       0.732517  |       0.678486 |                       0.118746 |
| RATCMP1         |       0.699524  |       0.614987 |                       0.089438 |

Absolute standardized mean differences above 0.10 are treated as evidence that
complete-case deletion changes the observable sample composition.

## Consequence for the revised analysis

Complete-case estimates will be retained only as a benchmark. The primary
analysis must use an explicit missing-data procedure and report a complete-case
and inverse-probability-weighted sensitivity comparison.
