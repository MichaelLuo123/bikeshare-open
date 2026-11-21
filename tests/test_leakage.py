"""The tests that make the agent honest.

test_no_forbidden_features is the single most valuable test in this repo:
casual + registered == cnt exactly, so any model handed those columns
scores R^2 = 1.0 and looks brilliant while having learned nothing.
"""
import pandas as pd
import pytest

from src.config import FORBIDDEN, TARGET
from src.features import build_features, feature_columns
from src.ingest import load_raw


@pytest.fixture(scope="module")
def feats():
    return build_features(load_raw())


def test_leakage_identity_holds(feats):
    """Documents *why* casual and registered are forbidden."""
    assert (feats.casual + feats.registered == feats[TARGET]).all()


def test_no_forbidden_features(feats):
    """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
    construction, so this cannot discover a *new* leaky column. What it
    catches is someone editing feature_columns() or FORBIDDEN -- which is
    exactly the fault the Step 7 hook demonstrates."""
    cols = set(feature_columns(feats))
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"


def test_lags_are_true_calendar_lags(feats):
    """cnt_lag_1 for date d must equal cnt on d-1, in calendar days."""
    by_date = feats.set_index("dteday")[TARGET]
    checked = 0
    for date, lag in feats.set_index("dteday").cnt_lag_1.items():
        prev = date - pd.Timedelta(days=1)
        if prev in by_date.index:
            assert lag == pytest.approx(by_date[prev]), f"bad lag at {date.date()}"
            checked += 1
    assert checked > 600, "too few rows actually verified"


def test_lag_is_not_the_target(feats):
    assert not (feats.cnt_lag_1 == feats[TARGET]).all()


def test_rolling_mean_excludes_today(feats):
    """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
    by_date = feats.set_index("dteday")[TARGET]
    date = feats.dteday.iloc[200]
    window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
    if all(d in by_date.index for d in window):
        expected = sum(by_date[d] for d in window) / 7
        assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)


def test_no_missing_values(feats):
    assert feats[feature_columns(feats)].isna().sum().sum() == 0


def test_dates_are_sorted_and_unique(feats):
    assert feats.dteday.is_monotonic_increasing
    assert feats.dteday.is_unique


def test_cnt_roll_14_at_named_date_is_correct_value(feats):
    """cnt_roll_14 at 2012-07-15 must equal mean of cnt for July 1 through July 14.

    The feature must use exactly the 14 calendar days before the target date,
    excluding the current day.
    """
    # Target date: 2012-07-15
    target_date = pd.Timestamp("2012-07-15")

    # Expected dates: exactly 14 prior calendar days (July 1 through July 14)
    expected_dates = pd.date_range("2012-07-01", "2012-07-14", freq="D")

    # Assert all required dates exist in the features dataframe
    by_date = feats.set_index("dteday")
    assert target_date in by_date.index, f"Target date {target_date.date()} not in features"
    for d in expected_dates:
        assert d in by_date.index, f"Required prior date {d.date()} not in features"

    # Calculate expected value from independently sourced data (July 1-14)
    expected = sum(by_date.loc[d, TARGET] for d in expected_dates) / len(expected_dates)

    # Get actual value (will fail if cnt_roll_14 is not implemented)
    actual = by_date.loc[target_date, "cnt_roll_14"]

    assert actual == pytest.approx(expected), f"cnt_roll_14 at {target_date.date()} has wrong value: got {actual}, expected {expected}"
