"""Low-level Binance Futures REST client (USDT-M Testnet)."""
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
    """Raised when the Binance API returns a negative error code."""

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceFuturesClient:
    """Thin, stateless wrapper around the Binance Futures REST API (USDT-M)."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------ helpers

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append timestamp + HMAC-SHA256 signature to a copy of params."""
        signed = dict(params)          # never mutate the caller's dict
        signed["timestamp"] = int(time.time() * 1000)
        query_string = "&".join(f"{k}={v}" for k, v in signed.items())
        signed["signature"] = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signed

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        sign: bool = True,
    ) -> Dict:
        """Execute an HTTP request, handle signing, surface Binance errors."""
        payload = dict(params or {})
        if sign:
            payload = self._sign(payload)

        # Log request without leaking the signature
        safe_params = {k: v for k, v in payload.items() if k not in ("signature",)}
        logger.debug("→ %s %s  %s", method.upper(), path, safe_params)

        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(
                method, url,
                params=payload if method.upper() in ("GET", "DELETE") else None,
                data=payload  if method.upper() == "POST" else None,
                timeout=15,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network unreachable: %s", exc)
            raise ConnectionError(
                f"Cannot reach Binance Testnet at {self.base_url}. Check your network."
            ) from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out: %s %s", method, path)
            raise TimeoutError("Request to Binance Testnet timed out after 15 s.")

        logger.debug("← %s %s  HTTP %s", method.upper(), path, resp.status_code)

        try:
            data = resp.json()
        except ValueError:
            logger.error("Non-JSON response (HTTP %s): %s", resp.status_code, resp.text[:200])
            raise RuntimeError(f"Unexpected non-JSON response (HTTP {resp.status_code}).")

        # Binance signals errors with a negative `code` field
        if isinstance(data, dict) and isinstance(data.get("code"), int) and data["code"] < 0:
            logger.error("Binance error | code=%s | msg=%s", data["code"], data.get("msg"))
            raise BinanceClientError(code=data["code"], msg=data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------ public

    def get_exchange_info(self) -> Dict:
        """Fetch exchange metadata (no auth required)."""
        return self._request("GET", "/fapi/v1/exchangeInfo", sign=False)

    def get_account(self) -> Dict:
        """Fetch account balance and position info."""
        return self._request("GET", "/fapi/v2/account")

    def new_order(self, **kwargs) -> Dict:
        """Place a new futures order. Keyword args map 1-to-1 to Binance params."""
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def get_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("DELETE", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})
