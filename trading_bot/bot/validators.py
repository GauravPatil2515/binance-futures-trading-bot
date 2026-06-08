"""Input validation helpers."""
from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}'. Must be alphanumeric, e.g. BTCUSDT.")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {VALID_SIDES}.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(f"Invalid order type '{order_type}'. Must be one of {VALID_ORDER_TYPES}.")
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValidationError(f"Quantity must be > 0, got {q}.")
    return q


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type in {"LIMIT", "STOP_MARKET"}:
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValidationError(f"Price must be > 0, got {p}.")
        return p
    return None
