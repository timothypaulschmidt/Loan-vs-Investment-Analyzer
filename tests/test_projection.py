"""Tests for the projection: who wins, by how much, and where the answer flips."""
import pytest

from utils.loan_math import PAY_OFF_SOONER, RECAST
from utils.projection import project, break_even_return, net_worths, leader

# The project's original example
INPUTS = dict(loan_balance=824_000, interest_rate=0.0299, loan_years=30, investment_balance=824_000,
              investment_return=0.101, scenario_years=4, payoff_mode=PAY_OFF_SOONER)
SCENARIOS = {"Keep Loan": 0, "Partial Payoff": 200_000, "Full Payoff": 824_000}


def with_(**changes):
    return {**INPUTS, **changes}


def test_example_keep_loan_wins_with_correct_margins():
    p = project(SCENARIOS, INPUTS)
    assert p["winner"] == "Keep Loan"
    margins = {a["name"]: a["by"] for a in p["ahead_of"]}
    assert margins["Partial Payoff"] == pytest.approx(458_938.06 - 390_427.47, abs=1)
    assert margins["Full Payoff"] == pytest.approx(458_938.06 - 202_314.50, abs=1)


def test_expensive_loan_low_return_payoff_wins():
    p = project(SCENARIOS, with_(interest_rate=0.07, investment_return=0.04))
    assert p["winner"] == "Full Payoff"


@pytest.mark.parametrize("inputs", [
    INPUTS,
    with_(interest_rate=0.07, investment_return=0.04),
    with_(payoff_mode=RECAST),
    with_(scenario_years=15),
])
def test_break_even_really_is_where_the_leader_changes(inputs):
    # Just on the user's side of the break-even the current winner leads;
    # just past it, the new leader does. This checks the search, whatever the numbers are.
    be = break_even_return(SCENARIOS, inputs)
    assert be is not None
    current = leader(net_worths(SCENARIOS, inputs))
    nudge = 0.0001 if be["direction"] == "above" else -0.0001
    assert leader(net_worths(SCENARIOS, inputs, be["rate"] - nudge)) == current
    assert leader(net_worths(SCENARIOS, inputs, be["rate"] + nudge)) == be["new_leader"]


def test_example_flips_below_current_return():
    be = break_even_return(SCENARIOS, INPUTS)
    assert be["direction"] == "below"
    assert be["rate"] < INPUTS["investment_return"]


def test_zero_percent_loan_breaks_even_at_zero_return():
    # With a free loan, investing beats paying off whenever returns are above 0%
    inputs = with_(interest_rate=0, investment_return=0.05)
    be = break_even_return({"Keep Loan": 0, "Full Payoff": 824_000}, inputs)
    assert be["rate"] == pytest.approx(0, abs=0.0001)
    assert be["new_leader"] == "Full Payoff"


def test_what_if_rows_include_current_return():
    p = project(SCENARIOS, INPUTS)
    current = [row for row in p["what_if"] if row["is_current"]]
    assert len(current) == 1
    assert current[0]["rate"] == pytest.approx(0.101)
    assert current[0]["leader"] == "Keep Loan"
    assert len(p["what_if"]) == 5


def test_nothing_to_compare_returns_none():
    assert project({"Keep Loan": 0}, INPUTS) is None
