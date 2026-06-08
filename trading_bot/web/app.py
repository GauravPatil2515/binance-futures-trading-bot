"""Flask web UI for the Binance Futures Trading Bot."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from trading_bot.bot.logging_config import setup_logging
from trading_bot.bot.client import BinanceFuturesClient, BinanceClientError
from trading_bot.bot.orders import OrderManager
from trading_bot.bot.validators import ValidationError

app = Flask(__name__, template_folder="templates", static_folder="static")
logger = setup_logging("INFO")


def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    if not api_key or not api_secret:
        raise EnvironmentError("BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env")
    return BinanceFuturesClient(api_key=api_key, api_secret=api_secret)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.get_json(force=True)
    try:
        client = _get_client()
        manager = OrderManager(client=client)
        response = manager.place_order(
            symbol=data.get("symbol", ""),
            side=data.get("side", ""),
            order_type=data.get("order_type", ""),
            quantity=data.get("quantity"),
            price=data.get("price") or None,
            stop_price=data.get("stop_price") or None,
        )
        return jsonify({"success": True, "data": response})
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except BinanceClientError as e:
        return jsonify({"success": False, "error": f"Binance API [{e.code}]: {e.msg}"}), 502
    except EnvironmentError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        logger.exception("Unhandled error in /api/order: %s", e)
        return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
