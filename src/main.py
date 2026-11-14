# Library widely used for data manipulation and analysis
import pandas as pd
# Our reusable "ask until valid" input function
from utils.helpers import get_number

# Given data (example values in comments)
# loan_balance = 824000
loan_balance = get_number("Enter your loan balance (e.g. $250,000): ", min_value=1)

# interest_rate = 2.99%  -> stored as 0.0299
interest_rate = get_number("Enter loan interest rate in % (e.g. 2.99): ",
                           min_value=0, max_value=100, is_percent=True)

# loan_years = 30
loan_years = get_number("Enter number of years for loan (e.g. 30): ",
                        min_value=1, max_value=50, whole_number=True)
months = loan_years * 12
monthly_rate = interest_rate / 12

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

# Monthly payment (amortization formula)
# At 0% interest the formula divides by zero, so just split the balance evenly
if monthly_rate == 0:
    payment = loan_balance / months
else:
    payment = loan_balance * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

# Function to calculate remaining balance after N years
def remaining_balance(loan_balance, annual_rate, years_total, years_elapsed):
    r = annual_rate / 12
    n_total = years_total * 12
    n_elapsed = years_elapsed * 12
    if r == 0:
        # 0% interest: balance drops by the same amount every month
        return loan_balance * (1 - n_elapsed / n_total)
    balance = loan_balance * ((1 + r) ** n_total - (1 + r) ** n_elapsed) / ((1 + r) ** n_total - 1)
    return balance

# Calculate remaining balance after scenario_years
balance_after_N_years = remaining_balance(loan_balance, interest_rate, loan_years, scenario_years)

# Calculate total paid over N years
payments_made = scenario_years * 12
total_paid = payment * payments_made

# Calculate total interest paid so far
principal_paid = loan_balance - balance_after_N_years
interest_paid = total_paid - principal_paid

# Scenarios
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

# Function to calculate outcomes
def simulate_scenario(payoff):
    invest = investment_balance - payoff
    loan = loan_balance - payoff
    
    investment_growth = invest * ((1 + investment_return) ** scenario_years)
    # If you made no payments on loan, such as credit card and interest kept compounding
    # loan_remaining = loan * ((1 + interest_rate) ** scenario_years) if loan > 0 else 0
    loan_remaining = remaining_balance(loan, interest_rate, loan_years, scenario_years) if loan > 0 else 0
        
    net_worth = investment_growth - loan_remaining
    return investment_growth, loan_remaining, net_worth

results = []

for name, params in scenarios.items():
    growth, remaining, net = simulate_scenario(params["payoff"])
    results.append({
        "Scenario": name,
        "Investment Value After " + str(scenario_years) + "Y": round(growth, 2),
        "Loan Balance After " + str(scenario_years) + "Y": round(remaining, 2),
        "Net Worth After " + str(scenario_years) + "Y": round(net, 2)
    })

df = pd.DataFrame(results)
print(df)
print(f"Keep Loan Monthly Payment: ${payment:,.2f}")
print(f"Keep Loan Principal Paid On Loan After {scenario_years} Years: ${principal_paid:,.2f}")
print(f"Keep Loan Interest Paid On Loan After {scenario_years} Years: ${interest_paid:,.2f}")

