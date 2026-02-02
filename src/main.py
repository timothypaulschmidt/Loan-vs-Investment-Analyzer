# Library widely used for data manipulation and analysis
import pandas as pd
# from utils.helpers import greet

# Given data
# loan_balance = 824000
loan_balance = int(input("Enter your loan balance at a given period of time (e.g. 250,000): "))

# interest_rate = 0.0299  # 2.9%
interest_rate = float(input("Enter loan interest rate (e.g. .0299 for 2.99%): "))

# loan_years = 30
loan_years = int(input("Enter number of years for loan (e.g 30) "))
months = loan_years * 12
monthly_rate = interest_rate / 12

# investment_balance = 824000
investment_balance = int(input("Enter your investment to analyze vs the loan (e.g. 250,000): "))

# investment_return = 0.101 # 10.1%
investment_return = float(input("Enter expected investment return rate (e.g. 0.101 for 10.1%): "))

# partial_payoff = 200000
partial_payoff = int(input("Enter partial payoff loan amount, if considering paying down loan early (e.g. 100,000):: "))

# scenario_years = 4
scenario_years = int(input("Enter number of years to analyzer from start of loan until now (e.g. 4):: "))

# Monthly payment (amortization formula)
payment = loan_balance * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

# Function to calculate remaining balance after N years
def remaining_balance(loan_balance, annual_rate, years_total, years_elapsed):
    r = annual_rate / 12
    n_total = years_total * 12
    n_elapsed = years_elapsed * 12
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
    "Keep Mortgage": {"payoff": 0},
    # "Half Payoff": {"payoff": loan_balance / 2},
    "Partial Payoff": {"payoff": partial_payoff},  # Pay toward loan at begining
    "Full Payoff": {"payoff": loan_balance}
}

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
print(f"Keep Mortgage Monthly Payment: ${payment:,.2f}")
print(f"Keep Mortgage Principal Paid On Loan After {scenario_years} Years: ${principal_paid:,.2f}")
print(f"Keep Mortgage Interest Paid On Loan After {scenario_years} Years: ${interest_paid:,.2f}")

