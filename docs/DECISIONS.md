# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-21 — Keep `cnt_roll_14`, the mean demand over the previous 14 calendar days. It is available at prediction time because `shift(1)` excludes the current day's target before the rolling mean is computed. Ridge validation R² improved from 0.6475 to 0.6919 (+0.0444), and MAE decreased from 832.9 to 763.2. On identical training rows, Ridge R² improved from 0.6434 to 0.6919 (+0.0485). HGB validation R² worsened from 0.2185 to 0.1643 (-0.0542). Keep the feature because its benefit to Ridge outweighs the small controlled degradation for HGB; the 14-day warmup also reduces training rows.

- 2026-11-21 — Exercise 4: Tested HGB target transformations using only 2011 training and H1 2012 validation data. Predicting `cnt - cnt_lag_1` achieved validation R² 0.6161 and MAE 823.5; predicting `cnt / cnt_roll_14` achieved R² 0.7347 and MAE 667.4, outperforming Ridge (R² 0.6919, MAE 763.2). The relative-demand transformation is defensible because `cnt_roll_14` uses only the previous 14 calendar days, although validation improvement does not guarantee generalization. Keep the final pipeline untransformed and do not evaluate the test set during experimentation.

- 2026-11-21 — Updated CLAUDE.md to enforce the 14-day lag feature's availability rule and document the new `/seed-fault` skill. Created this skill to standardize the repeated fault-seeding, verification, evidence collection, and restoration workflow used in Exercise 2.
