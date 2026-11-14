import math


def _fmt(value):
    """Format a limit nicely: 100000.0 -> '100,000', 2.5 -> '2.5'."""
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def get_number(prompt, min_value=None, max_value=None, is_percent=False, whole_number=False):
    """Ask the user for a number until they enter a valid one.

    Accepts friendly formats like "$250,000.00", "2.99%" or "1e6".

    min_value / max_value: optional limits (checked on the number as typed).
    is_percent:   the user types 2.99 for 2.99%; the function returns 0.0299.
    whole_number: reject decimals (used for years) and return an int.
    """
    while True:
        text = input(prompt).strip()

        # Step 1: nothing typed
        if not text:
            print("  Please enter a value.")
            continue

        # Step 2: strip the formatting characters people naturally type
        text = text.replace("$", "").replace(",", "").replace("%", "").strip()

        # Step 3: convert to a number (only this line can raise ValueError)
        try:
            value = float(text)
        except ValueError:
            print("  Please enter a valid number (e.g. 250000 or $250,000).")
            continue

        # Step 4: reject "nan" and "inf", which float() accepts
        if not math.isfinite(value):
            print("  Please enter a real number.")
            continue

        # Step 5: whole numbers only, when asked for
        if whole_number and not value.is_integer():
            print("  Please enter a whole number (no decimals).")
            continue

        # Step 6: range checks, only if limits were given
        if min_value is not None and value < min_value:
            print(f"  Value must be at least {_fmt(min_value)}.")
            continue
        if max_value is not None and value > max_value:
            print(f"  Value must be at most {_fmt(max_value)}.")
            continue

        # Step 7: convert to the form the math needs
        if is_percent:
            return value / 100
        if whole_number:
            return int(value)
        return value
