"""Order placement logic."""
from __future__ import annotations

import logging
from typing import Optional

from .client import BinanceFuturesClient
from .validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

logger = logging.getLogger("trading_bot.orders")


class OrderManager:
    """High-level order placement with validation and logging."""

    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:
        """Validate inputs, build the order payload, call the API, return response."""
        # --- validation ---
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity = validate_quantity(quantity)
        price = validate_price(price, order_type)

        # --- build payload ---
        payload: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            payload["price"] = price
            payload["timeInForce"] = "GTC"

        if order_type == "STOP_MARKET" and stop_price is not None:
            payload["stopPrice"] = stop_price

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            order_type, side, symbol, quantity, price,
        )

        response = self.client.new_order(**payload)
        logger.info(
            "Order placed | orderId=%s status=%s executedQty=%s avgPrice=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
            response.get("avgPrice"),
        )
        return response
