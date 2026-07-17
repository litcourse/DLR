# Variable and Sample Audit for the New Submission

Generated from the local OECD PISA 2022 public-use files.

## Variable labels in the public-use files

| Variable | Public-use label | Role in new analysis |
| --- | --- | --- |
| `ICTRES` | ICT Resources (WLE) | Excluded as the primary home ICT measure |
| `ICTHOME` | ICT availability outside of school  (WLE) | Sensitivity measure (IRT/WLE scale) |
| `ICTAVHOM` | Availability and Usage of ICT at Home | Primary home ICT availability measure |
| `RATCMP1` | Availability of computers | Primary school computer provision measure |

## Coverage

- PISA systems/economies in the files: 80
- Systems with non-missing ESCS, ICTAVHOM, and RATCMP1 data: 51
- Students in those systems before item-level exclusions: 387,494
- Students complete on ESCS, ICTAVHOM, and RATCMP1: 296,527
- Complete-core retention rate: 76.5%
- Eligible systems: ALB, ARG, AUS, AUT, BEL, BGR, BRA, BRN, CHE, CHL, CZE, DEU, DNK, DOM, ESP, EST, FIN, GBR, GEO, GRC, HKG, HRV, HUN, IRL, ISL, ISR, ITA, JOR, JPN, KAZ, KOR, LTU, LVA, MAC, MAR, MLT, MYS, PAN, POL, QUR, ROU, SAU, SGP, SVK, SVN, SWE, TAP, THA, TUR, URY, USA

The former 10-system sample is therefore not an eligibility-defined sample.

## Construct overlap diagnostic

- Weighted correlation between ESCS and ICTRES: 0.690
- Weighted correlation between ESCS and ICTAVHOM: 0.123

## Decisions for the clean revision

1. Use `ICTAVHOM` as the primary home ICT availability indicator.
2. Use `ICTHOME` as a sensitivity measure where available.
3. Retain all eligible systems rather than the former convenience sample.
4. Treat remaining item nonresponse explicitly; do not rely only on listwise deletion.
5. Keep the rejected SEE submission package unchanged for reproducibility.
