"""Web interface: one page with a form (GET) that posts back to itself (POST)."""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from utils.helpers import parse_number
from utils.loan_math import (monthly_payment, remaining_balance, simulate_scenario,
                             PAY_OFF_SOONER, RECAST)

# Find the templates folder next to this file, no matter where Python is started from
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(title="Loan vs Investment Analyzer")

MAX_AMOUNT = 1_000_000_000  # $1 billion: stops absurd values like 1e308

# Every form field in one place: the HTML form and the validation both use this list.
# "limits" are passed straight to parse_number().
FIELDS = [
    {"name": "loan_balance", "label": "Loan balance", "placeholder": "$250,000", "prefix": "$",
     "limits": {"min_value": 1, "max_value": MAX_AMOUNT}},
    {"name": "interest_rate", "label": "Loan interest rate", "placeholder": "2.99", "suffix": "%",
     "limits": {"min_value": 0, "max_value": 100, "is_percent": True}},
    {"name": "loan_years", "label": "Loan term", "placeholder": "30", "suffix": "years",
     "limits": {"min_value": 1, "max_value": 50, "whole_number": True}},
    {"name": "investment_balance", "label": "Investment amount", "placeholder": "$250,000", "prefix": "$",
     "limits": {"min_value": 0, "max_value": MAX_AMOUNT}},
    {"name": "investment_return", "label": "Expected annual return", "placeholder": "10.1", "suffix": "%",
     "limits": {"min_value": -100, "max_value": 100, "is_percent": True}},
    {"name": "partial_payoff", "label": "Partial payoff amount", "placeholder": "$100,000", "prefix": "$",
     "limits": {"min_value": 0, "max_value": MAX_AMOUNT}},
    {"name": "scenario_years", "label": "Years into the loan to analyze", "placeholder": "4", "suffix": "years",
     "limits": {"min_value": 1, "max_value": 50, "whole_number": True}},
]


def validate(form):
    """Check every field. Returns (values, errors); errors maps field name -> message."""
    values, errors = {}, {}

    # Pass 1: each field on its own
    for field in FIELDS:
        try:
            values[field["name"]] = parse_number(form.get(field["name"]), **field["limits"])
        except ValueError as e:
            errors[field["name"]] = str(e)

    # Pass 2: rules that compare two fields (only if both passed pass 1)
    if not {"loan_balance", "investment_balance", "partial_payoff"} & errors.keys():
        max_payoff = min(values["loan_balance"], values["investment_balance"])
        if values["partial_payoff"] > max_payoff:
            errors["partial_payoff"] = (f"Can't exceed the smaller of the loan and the investment "
                                        f"(${max_payoff:,.2f}).")

    if not {"loan_years", "scenario_years"} & errors.keys():
        if values["scenario_years"] > values["loan_years"]:
            errors["scenario_years"] = f"Can't be longer than the loan term ({values['loan_years']} years)."

    # The partial payoff choice (radio buttons): anything unexpected falls back to the default
    values["payoff_mode"] = RECAST if form.get("payoff_mode") == RECAST else PAY_OFF_SOONER

    return values, errors


def describe_payoff(month, loan_years):
    """Turn a payoff month into words, e.g. 'Paid off in 19.9 yrs (10.1 yrs early)'."""
    if month is None:
        return ""
    if month == 0:
        return "Paid off today"
    years = month / 12
    early = loan_years - years
    text = f"Paid off in {years:.1f} yrs"
    return text + (f" ({early:.1f} yrs early)" if early >= 0.05 else "")


def analyze(v):
    """Run every scenario with the same monthly budget (the cash-flow fix)."""
    payment = monthly_payment(v["loan_balance"], v["interest_rate"], v["loan_years"])
    balance_after = remaining_balance(v["loan_balance"], v["interest_rate"], v["loan_years"], v["scenario_years"])
    total_paid = payment * v["scenario_years"] * 12
    principal_paid = v["loan_balance"] - balance_after
    interest_paid = total_paid - principal_paid

    scenarios = {"Keep Loan": 0, "Partial Payoff": v["partial_payoff"]}
    note = None
    # Full payoff is only possible if the investment can cover the whole loan
    if v["investment_balance"] >= v["loan_balance"]:
        scenarios["Full Payoff"] = v["loan_balance"]
    else:
        note = (f"Full Payoff skipped: your investment (${v['investment_balance']:,.2f}) "
                f"is less than the loan (${v['loan_balance']:,.2f}).")

    rows = []
    for name, payoff in scenarios.items():
        r = simulate_scenario(
            payoff, v["loan_balance"], v["interest_rate"], v["loan_years"],
            v["investment_balance"], v["investment_return"], v["scenario_years"],
            v["payoff_mode"])
        rows.append({"name": name, "payoff": payoff,
                     "monthly_payment": r["monthly_payment"],
                     "investment": r["investment_value"],
                     "payments_invested": r["payments_invested"],
                     "loan": r["loan_remaining"], "net": r["net_worth"],
                     "payoff_text": describe_payoff(r["payoff_month"], v["loan_years"])})

    best = max(rows, key=lambda r: r["net"])["name"]
    return {"rows": rows, "best": best, "note": note, "payment": payment,
            "principal_paid": principal_paid, "interest_paid": interest_paid,
            "years": v["scenario_years"]}


@app.get("/")
def show_form(request: Request):
    """First visit: empty form."""
    return templates.TemplateResponse(request, "index.html",
                                      {"fields": FIELDS, "form": {}, "errors": {}, "result": None})


@app.post("/")
async def submit_form(request: Request):
    """Form submitted: validate, then show either the errors or the results."""
    form = await request.form()
    values, errors = validate(form)
    result = None if errors else analyze(values)
    return templates.TemplateResponse(request, "index.html",
                                      {"fields": FIELDS, "form": form, "errors": errors, "result": result,
                                       "values": values})
