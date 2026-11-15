"""Projection: compare the scenarios and explain which one comes out ahead.

This is a projection under the user's assumptions (steady returns, no taxes),
not a prediction. The page says so.
"""
from utils.loan_math import simulate_scenario

# Range of annual returns searched for the break-even point, and the step size
SEARCH_LOW, SEARCH_HIGH, SEARCH_STEP = -0.20, 0.30, 0.0025
WHAT_IF_OFFSETS = (-0.04, -0.02, 0.0, 0.02, 0.04)   # +/- percentage points around the user's return
TIE_DOLLARS = 1.0                                     # closer than this counts as a tie


def run_all(scenarios, inputs, investment_return=None):
    """Simulate every scenario. scenarios: {name: payoff}. Returns {name: result dict}.

    investment_return lets us ask "what if returns were different?" without changing inputs.
    """
    rate = inputs["investment_return"] if investment_return is None else investment_return
    return {
        name: simulate_scenario(payoff, inputs["loan_balance"], inputs["interest_rate"],
                                inputs["loan_years"], inputs["investment_balance"], rate,
                                inputs["scenario_years"], inputs["payoff_mode"])
        for name, payoff in scenarios.items()
    }


def net_worths(scenarios, inputs, investment_return=None):
    """Just the net worth of each scenario: {name: dollars}."""
    return {name: r["net_worth"] for name, r in run_all(scenarios, inputs, investment_return).items()}


def leader(nets):
    """Name of the scenario with the highest net worth."""
    return max(nets, key=nets.get)


def break_even_return(scenarios, inputs):
    """The annual return, closest to the user's, at which a different scenario takes the lead.

    How it works:
      1. Walk away from the user's return in small steps (down, then up) until the leader changes.
      2. The flip happened somewhere inside that last step. Bisect: test the midpoint,
         keep the half where the flip is, repeat 40 times. That pins it down to a tiny fraction of 1%.
    Returns {"rate", "direction" ("below"/"above"), "new_leader"} or None if no flip in the range.
    """
    current = inputs["investment_return"]
    current_leader = leader(net_worths(scenarios, inputs))
    found = []

    for direction in (-1, +1):
        k = 1
        while True:
            rate = current + direction * SEARCH_STEP * k
            if (direction < 0 and rate < SEARCH_LOW) or (direction > 0 and rate > SEARCH_HIGH):
                break                                   # searched as far as we go this way
            nets = net_worths(scenarios, inputs, rate)
            new_leader = leader(nets)
            if new_leader != current_leader:
                # Bisect between the last rate where the current leader won ("still") and this one ("flipped")
                still, flipped = rate - direction * SEARCH_STEP, rate
                for _ in range(40):
                    mid = (still + flipped) / 2
                    n = net_worths(scenarios, inputs, mid)
                    if n[current_leader] >= n[new_leader]:
                        still = mid
                    else:
                        flipped = mid
                found.append({"rate": (still + flipped) / 2,
                              "direction": "below" if direction < 0 else "above",
                              "new_leader": new_leader})
                break
            k += 1

    if not found:
        return None
    # If it flips in both directions, report the one nearest the user's return
    return min(found, key=lambda f: abs(f["rate"] - current))


def what_if(scenarios, inputs):
    """Net worth of each scenario if returns were a few points lower or higher."""
    rows = []
    for offset in WHAT_IF_OFFSETS:
        rate = inputs["investment_return"] + offset
        if rate < -1 or rate > 1:
            continue                                    # outside -100%..100%: skip
        nets = net_worths(scenarios, inputs, rate)
        rows.append({"rate": rate, "is_current": offset == 0, "nets": nets, "leader": leader(nets)})
    return rows


def project(scenarios, inputs):
    """Everything the projection panel shows. Returns None if there's nothing to compare."""
    if len(scenarios) < 2:
        return None

    nets = net_worths(scenarios, inputs)
    ranking = sorted(nets, key=nets.get, reverse=True)   # best first
    winner, runner_up = ranking[0], ranking[1]
    margin = nets[winner] - nets[runner_up]

    return {
        "winner": winner,
        "is_tie": margin < TIE_DOLLARS,
        "ahead_of": [{"name": name, "by": nets[winner] - nets[name]} for name in ranking[1:]],
        "break_even": break_even_return(scenarios, inputs),
        "what_if": what_if(scenarios, inputs),
        "scenario_names": list(scenarios),
    }
