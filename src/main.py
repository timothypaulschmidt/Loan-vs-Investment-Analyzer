# Library widely used for data manipulation and analysis
import pandas as pd
# Our reusable "ask until valid" input function
from utils.helpers import get_number
# The loan and investment calculations
from utils.loan_math import monthly_payment, remaining_balance, simulate_scenario


def main():
    # ---- 1. Inputs (example values in comments) ----
    # loan_balance = 824000
    loan_balance = get_number("Enter your loan balance (e.g. $250,000): ", min_value=1)

    # interest_rate = 2.99%  -> stored as 0.0299
    interest_rate = get_number("Enter loan interest rate in % (e.g. 2.99): ",
                               min_value=0, max_value=100, is_percent=True)

    # loan_years = 30
    loan_years = get_number("Enter number of years for loan (e.g. 30): ",
                            min_value=1, max_value=50, whole_number=True)

    # investment_balance = 824000
    investment_balance = get_number("Enter your investment amount to compare against the loan (e.g. $250,000): ",
                                    min_value=0)

    # investment_return = 10.1%  -> stored as 0.101
    investment_return = get_number("Enter expected annual investment return in % (e.g. 10.1): ",
                                   min_value=-100, max_value=100, is_percent=True)

    # partial_payoff = 200000
    # You can't pay off more than you owe, or more than you have invested
    max_payoff = min(loan_balance, investment_balance)
    partial_payoff = get_number(f"Enter partial payoff amount, if considering paying down the loan early "
                                f"(0 to ${max_payoff:,.2f}): ",
                                min_value=0, max_value=max_payoff)

    # scenario_years = 4
    # Can't analyze further than the end of the loan
    scenario_years = get_number(f"Enter number of years into the loan to analyze (1 to {loan_years}): ",
                                min_value=1, max_value=loan_years, whole_number=True)

    # ---- 2. Keep Loan payment details ----
    payment = monthly_payment(loan_balance, interest_rate, loan_years)
    balance_after_n_years = remaining_balance(loan_balance, interest_rate, loan_years, scenario_years)

    # Total paid over N years, split into principal and interest
    total_paid = payment * scenario_years * 12
    principal_paid = loan_balance - balance_after_n_years
    interest_paid = total_paid - principal_paid

    # ---- 3. Scenarios ----
    scenarios = {
        "Keep Loan": {"payoff": 0},
        # "Half Payoff": {"payoff": loan_balance / 2},
        "Partial Payoff": {"payoff": partial_payoff},  # Pay toward loan at beginning
    }

    # Full payoff is only possible if the investment can cover the whole loan
    if investment_balance >= loan_balance:
        scenarios["Full Payoff"] = {"payoff": loan_balance}
    else:
        print(f"\nNote: Full Payoff skipped. Your investment (${investment_balance:,.2f}) "
              f"is less than the loan (${loan_balance:,.2f}).")

    results = []
    for name, params in scenarios.items():
        growth, remaining, net = simulate_scenario(
            params["payoff"], loan_balance, interest_rate, loan_years,
            investment_balance, investment_return, scenario_years)
        results.append({
            "Scenario": name,
            f"Investment Value After {scenario_years}Y": round(growth, 2),
            f"Loan Balance After {scenario_years}Y": round(remaining, 2),
            f"Net Worth After {scenario_years}Y": round(net, 2),
        })

    # ---- 4. Output ----
    df = pd.DataFrame(results)
    print(df)
    print(f"Keep Loan Monthly Payment: ${payment:,.2f}")
    print(f"Keep Loan Principal Paid On Loan After {scenario_years} Years: ${principal_paid:,.2f}")
    print(f"Keep Loan Interest Paid On Loan After {scenario_years} Years: ${interest_paid:,.2f}")


# Only run main() when this file is run directly (python src/main.py),
# not when another file (like a test) imports it
if __name__ == "__main__":
    main()
