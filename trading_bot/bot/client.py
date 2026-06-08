"""Low-level Binance Futures REST client."""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
import logging

import requests

BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")

logger = logging.getLogger("trading_bot.client")


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceFuturesClient:
    """Thin wrapper around Binance Futures REST API (USDT-M)."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        params["signature"] = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        return params

    def _request(self, method: str, path: str, params: Optional[Dict] = None, sign: bool = True) -> Dict:
        params = params or {}
        if sign:
            params = self._sign(params)
        url = f"{self.base_url}{path}"
        logger.debug("REQUEST  %s %s  params=%s", method.upper(), path, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.request(method, url, params=params, timeout=15)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Cannot reach Binance Testnet ({self.base_url}). Check your network.") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out: %s %s", method, path)
            raise TimeoutError("Request to Binance Testnet timed out.")

        logger.debug("RESPONSE %s %s  status=%s", method.upper(), path, resp.status_code)
        data = resp.json()

        if isinstance(data, dict) and "code" in data and data["code"] != 200 and data["code"] < 0:
            logger.error("API error | code=%s msg=%s", data.get("code"), data.get("msg"))
            raise BinanceClientError(code=data["code"], msg=data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> Dict:
        return self._request("GET", "/fapi/v1/exchangeInfo", sign=False)

    def get_account(self) -> Dict:
        return self._request("GET", "/fapi/v2/account")

    def new_order(self, **kwargs) -> Dict:
        """Place a new futures order. Pass keyword args matching Binance API params."""
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def get_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("DELETE", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})
