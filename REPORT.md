# MA6 Agent Programming Report

## Results

I added `cnt_roll_14`, which calculates average bike demand over the previous 14 calendar days. The feature uses `shift(1)` to exclude the prediction day's count and prevent target leakage. I also increased `LAG_WARMUP` from 7 to 14.

### Validation results

| Model | Original R² | Updated R² | Change |
|---|---:|---:|---:|
| Mean baseline | -0.9318 | -0.8583 | +0.0735 |
| Persistence | 0.4507 | 0.4507 | 0.0000 |
| Ridge | 0.6475 | 0.6919 | +0.0444 |
| Gradient boosting | 0.2185 | 0.1643 | -0.0542 |

Ridge validation MAE decreased from 832.9 to 763.2. Because the longer warmup reduced the training set from 348 to 334 rows, I also compared models with and without the feature using identical training and validation rows.

On identical rows, Ridge R² increased from 0.6434 to 0.6919 (+0.0485), while gradient boosting R² decreased from 0.1713 to 0.1643 (-0.0070). I decided to keep the feature because it substantially improved Ridge's validation performance.

Final test-set results will be recorded after feature and model experiments are complete.

## Headline finding

The 14-day rolling demand feature improved Ridge's validation performance but did not improve gradient boosting. The controlled comparison suggests Ridge benefits from the additional demand history rather than merely from the shorter training period.

## Exercise 4: target transformation

Two target transformations were tested on HGB to address the extrapolation problem:

1. **Residual target**: Predict `cnt - cnt_lag_1` (deviation from yesterday), then add `cnt_lag_1` back at prediction time. The residual is defensible because `cnt_lag_1` (yesterday's count) is known at prediction time. Results: R² = 0.6161, MAE = 823.5. This improved over the original HGB but still underperforms Ridge.

2. **Relative-demand target**: Predict `cnt / cnt_roll_14` (demand relative to recent history), then multiply by `cnt_roll_14` at prediction time. The transformation is defensible because `cnt_roll_14` uses only the previous 14 calendar days via `shift(1)`, so it does not leak the current day's target. Results: R² = 0.7347, MAE = 667.4. This outperformed Ridge on validation, achieving R² = 0.7347 versus 0.6919 (+0.0428) and reducing MAE from 763.2 to 667.4 (95.8 fewer rides). However, this improvement is based on validation performance and does not guarantee better generalization.

**Comparison to baseline**: Original HGB failed severely (R² = 0.1643, MAE = 1341.2) because tree models trained on 2011 cannot extrapolate to 2012's ~65% ridership growth. Relative-demand normalization addresses this by predicting demand relative to recent levels rather than absolute levels. The transformation does not introduce leakage because both `cnt_lag_1` (for residual) and `cnt_roll_14` (for relative demand) are computed from history only.

No test-set evaluation was performed for these experiments as requested.

## Exercise 5: ridge vs persistence

On the updated pipeline's validation set, Ridge outperformed persistence in both R² (0.6919 versus 0.4507) and MAE (763.2 versus 900.6), suggesting that it learns useful patterns beyond yesterday's ridership. However, the original starter pipeline's test results showed a much smaller R² advantage for Ridge of about 0.07, while persistence achieved a lower MAE of approximately 840 rides. These historical test results do not establish how the updated pipeline will perform. For daily bike-demand forecasting, MAE matters because it reflects the average size of prediction errors in rides. I would not deploy Ridge solely because of its higher R². Although its validation performance is promising, I would want to confirm that its improvements generalize to held-out data before choosing it over the simpler persistence baseline.

## Attribution

Model used: `bikeshare-coder` (Qwen3.5:9b through local Ollama and Claude Code).

Claude Code assisted with feature implementation. I reviewed the proposed edits, ran tests, and evaluated validation performance. ChatGPT provided guidance on implementation checks, experiment commands, and documentation.

Additional attribution details will be added as the remaining exercises are completed.
