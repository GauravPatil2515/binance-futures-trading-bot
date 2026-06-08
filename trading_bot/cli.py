"""CLI entry point for the Binance Futures Trading Bot."""
from __future__ import annotations

import os
import sys
import argparse
from typing import Optional

# Ensure package root is in path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from trading_bot.bot.logging_config import setup_logging
from trading_bot.bot.client import BinanceFuturesClient, BinanceClientError
from trading_bot.bot.orders import OrderManager
from trading_bot.bot.validators import ValidationError



BANNER = """
╔══════════════════════════════════════════════╗
║   Binance Futures Testnet — Trading Bot CLI  ║
╚══════════════════════════════════════════════╝
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit / Stop-Market orders on Binance Futures Testnet.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True,  choices=["BUY", "SELL"],         help="Order side")
    parser.add_argument("--type",       required=True,  dest="order_type",
                        choices=["MARKET", "LIMIT", "STOP_MARKET"],                      help="Order type")
    parser.add_argument("--qty",        required=True,  type=float,                      help="Order quantity")
    parser.add_argument("--price",      required=False, type=float, default=None,        help="Limit price (required for LIMIT)")
    parser.add_argument("--stop-price", required=False, type=float, default=None,        help="Stop price (required for STOP_MARKET)")
    parser.add_argument("--api-key",    required=False, default=None,
                        help="Binance API key (overrides BINANCE_API_KEY env var)")
    parser.add_argument("--api-secret", required=False, default=None,
                        help="Binance API secret (overrides BINANCE_API_SECRET env var)")
    parser.add_argument("--log-level",  required=False, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],                   help="Log verbosity")
    return parser


def _resolve_credentials(args) -> tuple[str, str]:
    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")
    if not api_key or not api_secret:
        print("[ERROR] API credentials are required.\n"
              "       Set BINANCE_API_KEY and BINANCE_API_SECRET env vars,\n"
              "       or pass --api-key / --api-secret flags.", file=sys.stderr)
        sys.exit(1)
    return api_key, api_secret


def _print_summary(args) -> None:
    print(BANNER)
    print("── Order Request Summary ──────────────────────")
    print(f"  Symbol    : {args.symbol.upper()}")
    print(f"  Side      : {args.side}")
    print(f"  Type      : {args.order_type}")
    print(f"  Quantity  : {args.qty}")
    if args.price:
        print(f"  Price     : {args.price}")
    if args.stop_price:
        print(f"  Stop Price: {args.stop_price}")
    print("───────────────────────────────────────────────")


def _print_response(response: dict) -> None:
    print("\n── Order Response ──────────────────────────────")
    print(f"  Order ID      : {response.get('orderId')}")
    print(f"  Client Order  : {response.get('clientOrderId')}")
    print(f"  Symbol        : {response.get('symbol')}")
    print(f"  Status        : {response.get('status')}")
    print(f"  Side          : {response.get('side')}")
    print(f"  Type          : {response.get('type')}")
    print(f"  Orig Qty      : {response.get('origQty')}")
    print(f"  Executed Qty  : {response.get('executedQty')}")
    print(f"  Avg Price     : {response.get('avgPrice') or response.get('price', 'N/A')}")
    print(f"  Time in Force : {response.get('timeInForce', 'N/A')}")
    print("───────────────────────────────────────────────")


def main():
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log_level)
    api_key, api_secret = _resolve_credentials(args)

    _print_summary(args)

    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    manager = OrderManager(client=client)

    try:
        response = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.qty,
            price=args.price,
            stop_price=args.stop_price,
        )
        _print_response(response)
        print("\n✅  Order placed successfully!")
        logger.info("CLI order completed successfully. orderId=%s", response.get("orderId"))

    except ValidationError as exc:
        print(f"\n❌  Validation error: {exc}", file=sys.stderr)
        logger.error("Validation error: %s", exc)
        sys.exit(2)

    except BinanceClientError as exc:
        print(f"\n❌  Binance API error [{exc.code}]: {exc.msg}", file=sys.stderr)
        logger.error("BinanceClientError: code=%s msg=%s", exc.code, exc.msg)
        sys.exit(3)

    except (ConnectionError, TimeoutError) as exc:
        print(f"\n❌  Network error: {exc}", file=sys.stderr)
        logger.error("Network error: %s", exc)
        sys.exit(4)

    except Exception as exc:
        print(f"\n❌  Unexpected error: {exc}", file=sys.stderr)
        logger.exception("Unexpected error: %s", exc)
        sys.exit(5)


if __name__ == "__main__":
    main()
