"""Input validation — all public functions raise ValidationError on bad input."""
from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}

# Reasonable min/max guards (not exchange-specific)
_MAX_QTY   = 1_000_000
_MAX_PRICE = 10_000_000


class ValidationError(ValueError):
    """Raised for any invalid user-supplied input."""


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("Symbol must not be empty.")
    if not s.isalnum():
        raise ValidationError(f"Symbol '{s}' must be alphanumeric (e.g. BTCUSDT).")
    if len(s) > 20:
        raise ValidationError(f"Symbol '{s}' is too long (max 20 chars).")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Side must be one of {sorted(VALID_SIDES)}, got '{side}'.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type must be one of {sorted(VALID_ORDER_TYPES)}, got '{order_type}'."
        )
    return t


def validate_quantity(quantity: object) -> float:
    try:
        q = float(quantity)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if q <= 0:
        raise ValidationError(f"Quantity must be > 0, got {q}.")
    if q > _MAX_QTY:
        raise ValidationError(f"Quantity {q} exceeds maximum allowed ({_MAX_QTY}).")
    return q


def validate_price(price: object, order_type: str) -> float | None:
    """Return validated price float, or None for order types that don't need it."""
    if order_type == "LIMIT":
        if price is None or price == "":
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            p = float(price)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if p <= 0:
            raise ValidationError(f"Price must be > 0, got {p}.")
        if p > _MAX_PRICE:
            raise ValidationError(f"Price {p} exceeds maximum allowed ({_MAX_PRICE}).")
        return p
    return None


def validate_stop_price(stop_price: object, order_type: str) -> float | None:
    """Return validated stop price, or None when not applicable."""
    if order_type == "STOP_MARKET":
        if stop_price is None or stop_price == "":
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        try:
            p = float(stop_price)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if p <= 0:
            raise ValidationError(f"Stop price must be > 0, got {p}.")
        return p
    return None
