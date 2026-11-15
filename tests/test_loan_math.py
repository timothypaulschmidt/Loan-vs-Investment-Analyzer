"""Tests for the loan formulas, checked against known answers."""
import pytest

from utils.loan_math import monthly_payment, remaining_balance


# ---- monthly_payment ----

def test_payment_textbook_example():
    # Standard example: $100,000 at 6% for 30 years = $599.55/month
    assert monthly_payment(100_000, 0.06, 30) == pytest.approx(599.55, abs=0.01)


def test_payment_original_example():
    # The numbers this project started with
    assert monthly_payment(824_000, 0.0299, 30) == pytest.approx(3469.57, abs=0.01)


def test_payment_zero_interest_splits_evenly():
    assert monthly_payment(120_000, 0, 10) == pytest.approx(1000)


# ---- remaining_balance ----

def test_balance_at_start_is_full_loan():
    assert remaining_balance(824_000, 0.0299, 30, 0) == pytest.approx(824_000)


def test_balance_at_end_is_zero():
    assert remaining_balance(824_000, 0.0299, 30, 30) == pytest.approx(0, abs=0.01)


def test_balance_original_example_after_4_years():
    assert remaining_balance(824_000, 0.0299, 30, 4) == pytest.approx(751_873.30, abs=0.01)


def test_balance_zero_interest_halfway():
    assert remaining_balance(100_000, 0, 30, 15) == pytest.approx(50_000)


# ---- monthly_return / future_value_of_monthly ----

from utils.loan_math import (monthly_return, future_value_of_monthly,
                             simulate_scenario, RECAST, PAY_OFF_SOONER)


def test_monthly_return_compounds_back_to_annual():
    m = monthly_return(0.101)
    assert (1 + m) ** 12 == pytest.approx(1.101)


def test_future_value_zero_return_is_just_the_sum():
    assert future_value_of_monthly(100, 0, 2) == pytest.approx(2400)


def test_future_value_matches_month_by_month_sum():
    # Formula vs. adding up each deposit's growth by hand
    m = monthly_return(0.08)
    by_hand = sum(500 * (1 + m) ** (120 - k) for k in range(1, 121))
    assert future_value_of_monthly(500, 0.08, 10) == pytest.approx(by_hand)


# ---- simulate_scenario: the cash-flow fix ----

# The project's original example, used by several tests
EXAMPLE = dict(loan_balance=824_000, interest_rate=0.0299, loan_years=30,
               investment_balance=824_000, investment_return=0.101, scenario_years=4)


def run(payoff, mode=PAY_OFF_SOONER, **overrides):
    return simulate_scenario(payoff, payoff_mode=mode, **{**EXAMPLE, **overrides})


def test_keep_loan_unchanged_from_before():
    # Keep Loan has no freed-up money, so the fix must not change it
    r = run(0)
    assert r["payments_invested"] == pytest.approx(0, abs=0.01)
    assert r["loan_remaining"] == pytest.approx(751_873.30, abs=0.01)
    assert r["net_worth"] == pytest.approx(458_938.06, abs=0.01)


def test_full_payoff_invests_the_whole_payment():
    # Used to show $0. Now the $3,469.57/month is invested for 48 months.
    r = run(824_000)
    expected_side_fund = future_value_of_monthly(3469.57, 0.101, 4)
    assert r["loan_remaining"] == 0
    assert r["payments_invested"] == pytest.approx(expected_side_fund, abs=1)
    assert r["net_worth"] == pytest.approx(202_314.50, abs=1)
    assert r["payoff_month"] == 0


def test_partial_payoff_recast_lowers_payment():
    r = run(200_000, RECAST)
    assert r["monthly_payment"] == pytest.approx(monthly_payment(624_000, 0.0299, 30))
    # The loan follows the normal schedule for the smaller balance
    assert r["loan_remaining"] == pytest.approx(remaining_balance(624_000, 0.0299, 30, 4), abs=0.01)
    assert r["net_worth"] == pytest.approx(396_650.79, abs=1)


def test_partial_payoff_sooner_keeps_payment_and_ends_early():
    r = run(200_000, PAY_OFF_SOONER)
    assert r["monthly_payment"] == pytest.approx(3469.57, abs=0.01)
    assert r["payments_invested"] == 0                      # nothing freed up yet
    assert r["loan_remaining"] < run(200_000, RECAST)["loan_remaining"]  # paid down faster
    assert r["payoff_month"] < 30 * 12                      # finishes before 30 years


@pytest.mark.parametrize("payoff, mode", [
    (0, PAY_OFF_SOONER), (200_000, PAY_OFF_SOONER), (200_000, RECAST), (824_000, PAY_OFF_SOONER),
])
def test_every_scenario_spends_the_same_cash(payoff, mode):
    # THE fairness rule: loan payments + invested leftovers = same budget every month
    r = run(payoff, mode)
    assert r["total_loan_payments"] + r["total_invested_from_budget"] == pytest.approx(r["budget"] * 48)


def test_sooner_payoff_invests_after_loan_is_gone():
    # Short horizon past the payoff: once the loan hits $0, the full budget gets invested
    r = run(700_000, PAY_OFF_SOONER, scenario_years=10)
    assert r["payoff_month"] < 120
    assert r["loan_remaining"] == 0
    assert r["payments_invested"] > 0


def test_zero_percent_loan():
    r = simulate_scenario(50_000, 100_000, 0, 10, 100_000, 0.08, 4, PAY_OFF_SOONER)
    # $833.33/month on $50k at 0% -> paid off in 60 months
    assert r["payoff_month"] == 60
    assert r["loan_remaining"] == pytest.approx(50_000 - 833.333 * 48, abs=1)


def test_when_investing_beats_the_loan_keep_loan_wins():
    keep, full = run(0), run(824_000)
    assert keep["net_worth"] > full["net_worth"]


def test_when_the_loan_costs_more_than_investing_payoff_wins():
    # 7% loan vs 4% return: paying it off should win
    keep = run(0, interest_rate=0.07, investment_return=0.04)
    full = run(824_000, interest_rate=0.07, investment_return=0.04)
    assert full["net_worth"] > keep["net_worth"]
