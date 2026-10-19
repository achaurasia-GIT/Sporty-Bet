from decimal import Decimal, ROUND_HALF_UP


def money(value) -> Decimal:
    """Round a stake, odds, or payout to euro cents."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_euro(text: str) -> Decimal:
    """Read a UI amount such as 'Balance: €125.50' or '€24.50'."""
    cleaned = text.replace("Balance:", "").replace("€", "").replace(",", "").strip()
    return money(cleaned)


def euro(value) -> str:
    return f"€{money(value)}"
