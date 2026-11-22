# MA6 Agent Programming Report

## Results

I added `cnt_roll_14`, the average demand over the previous 14
calendar days. The feature uses `shift(1)` before rolling, so the
current day's target is excluded. I increased `LAG_WARMUP` from
7 to 14. Training rows decreased from 348 to 334, while validation
and test contain 182 and 184 days, respectively.

### Before-and-after model results

| Feature set | Model | Valid R² | Valid MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Before | Mean baseline | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | Persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | Ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | HGB | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | Mean baseline | -0.8583 | 1965.6 | -2.0333 | 2793.1 |
| After | Persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | Ridge | 0.6919 | 763.2 | 0.6268 | 870.9 |
| After | HGB | 0.1643 | 1341.2 | -0.6534 | 2087.9 |

Ridge improved on both splits. Validation R² increased from
0.6475 to 0.6919 and MAE decreased from 832.9 to 763.2.
Test R² increased from 0.5833 to 0.6268, while test MAE
decreased from 947.1 to 870.9. HGB worsened on both splits.

Because the longer warmup also changed the training rows, I ran
a validation-only ablation on identical rows. Ridge R² improved
from 0.6434 to 0.6919 (+0.0485), while HGB R² decreased from
0.1713 to 0.1643 (-0.0070). I kept `cnt_roll_14` because its
benefit to Ridge outweighed the small controlled HGB degradation.

## Headline finding

A naive model using `casual` and `registered` can achieve
a perfect R² of 1.000 because those columns sum to the target.
That is leakage, not a valid forecast. With an honest temporal
split (2011 training, H1 2012 validation, H2 2012 test), the
updated pipeline's test R² scores were -2.0333 for the mean
baseline, 0.5099 for persistence, 0.6268 for Ridge, and -0.6534
for HGB. HGB struggled to extrapolate the growing demand,
although it still beat the mean baseline. Ridge beat persistence
by 0.1169 test R², but persistence had a lower MAE (840.1 versus
870.9 rides). Adding `cnt_roll_14` improved Ridge test R² from
0.5833 to 0.6268 and reduced its MAE from 947.1 to 870.9;
HGB's test performance declined. I kept the feature for its
demonstrated benefit to Ridge while acknowledging the tradeoff.

## Exercise 4: target transformation

Two target transformations were tested on HGB to address the extrapolation problem:

1. **Residual target**: Predict `cnt - cnt_lag_1` (deviation from yesterday), then add `cnt_lag_1` back at prediction time. The residual is defensible because `cnt_lag_1` (yesterday's count) is known at prediction time. Results: R² = 0.6161, MAE = 823.5. This improved over the original HGB but still underperforms Ridge.

2. **Relative-demand target**: Predict `cnt / cnt_roll_14` (demand relative to recent history), then multiply by `cnt_roll_14` at prediction time. The transformation is defensible because `cnt_roll_14` uses only the previous 14 calendar days via `shift(1)`, so it does not leak the current day's target. Results: R² = 0.7347, MAE = 667.4. This outperformed Ridge on validation, achieving R² = 0.7347 versus 0.6919 (+0.0428) and reducing MAE from 763.2 to 667.4 (95.8 fewer rides). However, this improvement is based on validation performance and does not guarantee better generalization.

**Comparison to baseline**: Original HGB failed severely (R² = 0.1643, MAE = 1341.2) because tree models trained on 2011 cannot extrapolate to 2012's ~65% ridership growth. Relative-demand normalization addresses this by predicting demand relative to recent levels rather than absolute levels. The transformation does not introduce leakage because both `cnt_lag_1` (for residual) and `cnt_roll_14` (for relative demand) are computed from history only.

No test-set evaluation was performed for these experiments as requested.

## Exercise 5: ridge vs persistence

On the final updated pipeline, Ridge achieved higher
test R² than persistence (0.6268 versus 0.5099, a difference
of 0.1169), but persistence had lower test MAE (840.1 versus
870.9 rides, a 30.8-ride advantage). Ridge also beat persistence
on both validation metrics, indicating that it learns useful
patterns beyond yesterday's ridership. The original starter
pipeline showed a smaller test R² advantage of 0.0734 for Ridge,
with MAE of 947.1 versus persistence's 840.1. The new feature
substantially narrowed that error gap without reversing it.
For daily bike-demand planning, average error in rides is
operationally meaningful, and persistence is simpler to
maintain. I would favor persistence for deployment unless
further operational evaluation shows that Ridge's stronger R²
provides a practical benefit, such as reducing costly large errors.

## Attribution

Model used: `bikeshare-coder` (Qwen3.5:9b, 64k context), running locally through Ollama and Claude Code. I did not switch agent models during the assignment.

**Work performed with Claude Code:**
- Implemented the `cnt_roll_14` feature in `src/features.py` and updated `LAG_WARMUP` in `src/config.py`.
- Developed and ran leakage tests in `tests/test_leakage.py`, including the named-date test for the new feature.
- Introduced the three required seeded faults involving forbidden features, rolling-window leakage, and weather encoding.
- Investigated test failures, repaired the seeded faults, and added a regression test for unknown weather labels after the original tests failed to detect that fault.
- Assisted with documenting fault experiments and their outcomes in `docs/SEEDED_FAULTS.md`.
- Helped investigate target transformations and prepare the Exercise 4 discussion in `REPORT.md`.

**Methodological decisions I made:**
- Retained the starter's leakage exclusions, temporal data split, and mean and persistence baselines.
- Kept `cnt_roll_14` because it improved Ridge's validation performance, despite reducing HGB's performance.
- Evaluated residual and relative-demand target transformations and decided to keep the final pipeline untransformed.
- Chose not to recommend deploying Ridge solely on its higher R² because persistence achieved lower test MAE.
- Strengthened the weather-encoder verification after discovering that the original tests did not catch the missing error check.
- Created the `/seed-fault` skill to standardize the fault-testing workflow.

Additional AI assistance was used to draft experiment scripts and report text, which I executed, reviewed, and verified.

I reviewed the code changes, verified the experimental results, and made the final decisions about the methodology and interpretation.
