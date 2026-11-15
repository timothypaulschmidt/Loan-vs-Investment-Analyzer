"""Loan and investment calculations.

Every function here gets everything it needs through its arguments
(no global variables), so each one can be tested on its own.
Rates are decimals: 0.0299 means 2.99%.
"""

# How a partial payoff changes the loan:
PAY_OFF_SOONER = "sooner"  # payment stays the same, loan ends early (most common)
RECAST = "recast"          # lender recalculates a lower payment over the same term


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


def monthly_return(annual_return):
    """Monthly growth rate that compounds to `annual_return` over 12 months.

    10% a year is NOT 10%/12 a month when compounded: (1 + 0.10) ** (1/12) - 1 = 0.797%.
    """
    return (1 + annual_return) ** (1 / 12) - 1


def future_value_of_monthly(amount, annual_return, years):
    """Value after `years` of investing `amount` at the end of every month."""
    m = monthly_return(annual_return)
    n = years * 12
    if m == 0:
        return amount * n
    return amount * ((1 + m) ** n - 1) / m


def simulate_scenario(payoff, loan_balance, interest_rate, loan_years,
                      investment_balance, investment_return, scenario_years,
                      payoff_mode=PAY_OFF_SOONER):
    """Pay `payoff` toward the loan from the investment, then follow it month by month.

    The fair-comparison rule (the "cash-flow fix"):
      Every scenario sets aside the same monthly BUDGET = the Keep Loan payment.
      Each month the loan payment comes out of the budget, and whatever is left
      over is invested at `investment_return`. So no scenario gets free money.

    Returns a dict with the values after `scenario_years`, plus when the loan is paid off.
    """
    budget = monthly_payment(loan_balance, interest_rate, loan_years)

    # Step 1: apply the upfront payoff and work out the new monthly loan payment
    balance = loan_balance - payoff
    if balance <= 0:
        balance, payment = 0.0, 0.0                       # loan is gone
    elif payoff_mode == RECAST:
        payment = monthly_payment(balance, interest_rate, loan_years)  # lower payment
    else:
        payment = budget                                  # same payment, ends sooner

    loan_rate = interest_rate / 12
    invest_rate = monthly_return(investment_return)
    lump = investment_balance - payoff   # the investment left after the payoff
    side_fund = 0.0                      # leftover budget invested each month
    horizon = scenario_years * 12
    payoff_month = 0 if balance == 0 else None
    balance_at_horizon = balance
    total_loan_payments = 0.0
    total_invested_from_budget = 0.0

    # Step 2: month by month. We keep going past the horizon (loan only)
    # just to find out when the loan would be paid off.
    for month in range(1, loan_years * 12 + 1):
        # Loan: add a month of interest, then pay (never more than what's owed)
        paid = 0.0
        if balance > 0:
            balance += balance * loan_rate
            paid = min(payment, balance)
            balance -= paid
            if balance < 0.005:          # less than half a cent: treat as paid off
                balance = 0.0
                payoff_month = month

        if month <= horizon:
            leftover = budget - paid                          # what the loan didn't need
            lump *= 1 + invest_rate                           # original investment grows
            side_fund = side_fund * (1 + invest_rate) + leftover  # grow, then add this month
            total_loan_payments += paid
            total_invested_from_budget += leftover
            if month == horizon:
                balance_at_horizon = balance
        elif balance == 0:
            break                                             # past the horizon and paid off

    investments = lump + side_fund
    return {
        "monthly_payment": payment,
        "investment_value": lump,              # what's left of the original investment, grown
        "payments_invested": side_fund,        # the freed-up budget, invested and grown
        "loan_remaining": balance_at_horizon,
        "net_worth": investments - balance_at_horizon,
        "payoff_month": payoff_month,          # month the loan hits $0 (None = not within term)
        "total_loan_payments": total_loan_payments,
        "total_invested_from_budget": total_invested_from_budget,
        "budget": budget,
    }
