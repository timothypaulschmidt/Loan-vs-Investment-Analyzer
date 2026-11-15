"""Loan and investment calculations.

Every function here gets everything it needs through its arguments
(no global variables), so each one can be tested on its own.
Rates are decimals: 0.0299 means 2.99%.
"""


def monthly_payment(loan_balance, annual_rate, years):
    """Fixed monthly payment that pays off the loan in `years` (amortization formula)."""
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        # At 0% interest the formula divides by zero, so just split the balance evenly
        return loan_balance / n
    return loan_balance * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def remaining_balance(loan_balance, annual_rate, years_total, years_elapsed):
    """Loan balance left after `years_elapsed` years of regular payments."""
    r = annual_rate / 12
    n_total = years_total * 12
    n_elapsed = years_elapsed * 12
    if r == 0:
        # 0% interest: balance drops by the same amount every month
        return loan_balance * (1 - n_elapsed / n_total)
    return loan_balance * ((1 + r) ** n_total - (1 + r) ** n_elapsed) / ((1 + r) ** n_total - 1)


def simulate_scenario(payoff, loan_balance, interest_rate, loan_years,
                      investment_balance, investment_return, scenario_years):
    """Pay `payoff` toward the loan from the investment, then project `scenario_years` ahead.

    Returns (investment_value, loan_remaining, net_worth).
    """
    invest = investment_balance - payoff
    loan = loan_balance - payoff

    investment_value = invest * ((1 + investment_return) ** scenario_years)
    # If you made no payments on loan, such as credit card and interest kept compounding
    # loan_remaining = loan * ((1 + interest_rate) ** scenario_years) if loan > 0 else 0
    loan_remaining = remaining_balance(loan, interest_rate, loan_years, scenario_years) if loan > 0 else 0

    net_worth = investment_value - loan_remaining
    return investment_value, loan_remaining, net_worth
