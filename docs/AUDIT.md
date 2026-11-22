# Teammate Repository Audit

Repository: https://github.com/Jassyq/dsc190-ma6

## Leakage Auditor Output (Verbatim)

~~~~text
Here are the complete findings from the leakage-auditor subagent:

---

FINDINGS: CHECK #5 FAILS - Baselines Not Reported in Metrics Output

File: src/train.py

Lines 48-56, 77-85:

The MODELS dictionary includes both baselines, and the loop calls .fit() on train data for each model. However, there is a fundamental mismatch: while the baseline models exist in the codebase, their performance scores are never printed or reported.

def fit_and_score() -> dict:
    df = pd.read_parquet(PROCESSED)
    cols = feature_columns(df)
    train, valid, test = temporal_split(df)

    results = {
        "n_features": len(cols),
        "features": cols,
        "n_train": len(train),
        "n_valid": len(valid),
        "n_test": len(test),
    }
    for name, model in MODELS.items():  # Lines 77-85
        model.fit(train[cols], train[TARGET])
        results[name] = {
            split: {
                "r2": round(float(r2_score(part[TARGET], model.predict(part[cols]))), 4),
                "mae": round(float(mean_absolute_error(part[TARGET], model.predict(part[cols]))), 1),
            }
            for split, part in [("valid", valid), ("test", test)]
        }
    return results

Concrete scenario: A user runs python -m src.train, receives the output with ridge and hgb scores, but has no reference point to judge whether either model learned anything useful. With lagged-demand features dominating, a naive persistence predictor is the "embarrassing baseline" that should make it obvious what the models achieved. Without seeing baseline_persistence's R²/MAE side-by-side with ridge/hgb, there's no immediate signal about extrapolation failure (ridget) or model overfitting (hgb).

Minimal fix: The code already computes and stores these scores in the results dictionary—they just aren't printed. Add a final print block after writing the metrics file:

if __name__ == "__main__":
    res = fit_and_score()
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps(res, indent=2))

    # Explicitly report baselines alongside models
    print("=== Baseline Performance (Test Set) ===")
    for name in ["baseline_mean", "baseline_persistence"]:
        mae = res[name]["test"]["mae"]
        r2 = res[name]["test"]["r2"]
        print(f"{name:25}  R²={r2:6.4f}  MAE={mae:.1f}")

    print("=== Model Performance (Test Set) ===")
    for name in ["ridge", "hgb"]:
        mae = res[name]["test"]["mae"]
        r2 = res[name]["test"]["r2"]
        improvement_vs_persist = r2 - res["baseline_persistence"]["test"]["r2"]
        print(f"{name:25}  R²={r2:6.4f}  MAE={mae:.1f}  Δvs-persist={improvement_vs_persist:+.4f}")

---

FINDINGS: CHECK #4 - Silent Row Loss Without Bounding

File: src/features.py

Line 80:

return out.dropna().reset_index(drop=True)

The .dropna() call removes rows with any NaN values. This is not bounded by an assertion in build_features().

Concrete scenario: If a calendar gap (like 2011-03-10) causes multiple downstream features to be NaN for more than LAG_WARMUP rows, those extra lost rows are silently deleted without any warning. The test test_only_expected_rows_are_dropped in tests/test_contract.py does bound the loss, but that test runs on the final output—there's no intermediate assertion after .dropna() to catch if something unexpected caused additional NaNs beyond calendar gaps.

Minimal fix: Add an assertion bounding lost rows immediately before returning:

from src.config import LAG_WARMUP

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = reindex_to_calendar(df.sort_values("dteday").reset_index(drop=True)).copy()
    # ... feature engineering ...

    lost = len(out) - (len(raw_df) + LAG_WARMUP)  # after reindex, expect warmup rows
    max_allowed = LAG_WARMUP + LAG_WARMUP * missing_days
    assert lost <= max_allowed, f"dropped {lost} rows; expected at most {max_allowed}"

    return out.dropna().reset_index(drop=True)

Alternatively, duplicate test_only_expected_rows_are_dropped from tests/test_contract.py into tests/test_leakage.py and ensure it runs after every .build_features() call in the pipeline.
~~~~

## My Verdict

I disagree with Finding #5 because `src/train.py` already computes and reports both the mean and persistence baselines, including their validation and test R² and MAE in `reports/metrics.json`. The training script also prints these results, so the auditor's proposed fix would only change their presentation, not the reported numbers. I partially agree with Finding #4: `src/features.py` uses `dropna()` without an inline assertion, but `tests/test_contract.py` already contains `test_only_expected_rows_are_dropped`, which bounds row loss based on the lag warm-up period and missing calendar days. An inline check could strengthen protection, but the auditor did not establish that unexpected row loss occurred or affected the reported metrics. Overall, neither finding demonstrates an incorrect numerical result or invalidates the current conclusions.
