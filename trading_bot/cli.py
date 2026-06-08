"""CLI entry point — parse args, validate, place order, print results."""
from __future__ import annotations

import os
import sys
import argparse

# Support both `python trading_bot/cli.py` and `python -m trading_bot.cli`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()  # load .env before reading any env vars

from trading_bot.bot.logging_config import setup_logging
from trading_bot.bot.client import BinanceFuturesClient, BinanceClientError
from trading_bot.bot.orders import OrderManager, ValidationError


BANNER = """
\u2554" + "\u2550" * 46 + "\u2557
\u2551   Binance Futures Testnet \u2014 Trading Bot CLI  \u2551
\u255a" + "\u2550" * 46 + "\u255d
"""

DIVIDER = "\u2500" * 47


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit / Stop-Market orders on Binance Futures Testnet.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("--symbol",      required=True,  help="Trading pair, e.g. BTCUSDT")
    p.add_argument("--side",        required=True,  choices=["BUY", "SELL"],
                   help="Order side")
    p.add_argument("--type",        required=True,  dest="order_type",
                   choices=["MARKET", "LIMIT", "STOP_MARKET"],
                   help="Order type")
    p.add_argument("--qty",         required=True,  type=float,
                   help="Order quantity (e.g. 0.001)")
    p.add_argument("--price",       required=False, type=float, default=None,
                   help="Limit price in USDT (required for LIMIT orders)")
    p.add_argument("--stop-price",  required=False, type=float, default=None,
                   help="Stop price in USDT (required for STOP_MARKET orders)")
    p.add_argument("--api-key",     required=False, default=None,
                   help="Binance API key (overrides BINANCE_API_KEY env var)")
    p.add_argument("--api-secret",  required=False, default=None,
                   help="Binance API secret (overrides BINANCE_API_SECRET env var)")
    p.add_argument("--log-level",   required=False, default="INFO",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                   help="Log verbosity (default: INFO)")
    return p


def _resolve_credentials(args) -> tuple[str, str]:
    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")
    if not api_key or not api_secret:
        print(
            "[ERROR] API credentials missing.\n"
            "  Option 1: set BINANCE_API_KEY and BINANCE_API_SECRET in .env\n"
            "  Option 2: pass --api-key and --api-secret flags",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_key, api_secret


def _print_request_summary(args) -> None:
    print(BANNER)
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.order_type}")
    print(f"  Quantity   : {args.qty}")
    if args.price:
        print(f"  Price      : {args.price} USDT")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price} USDT")
    print(DIVIDER)


def _print_order_response(resp: dict) -> None:
    avg = resp.get("avgPrice") or resp.get("price") or "N/A"
    try:
        avg = f"{float(avg):.2f}" if float(avg) > 0 else "N/A"  # type: ignore
    except (TypeError, ValueError):
        avg = "N/A"

    print("\n" + DIVIDER)
    print(f"  Order ID      : {resp.get('orderId')}")
    print(f"  Client Order  : {resp.get('clientOrderId')}")
    print(f"  Symbol        : {resp.get('symbol')}")
    print(f"  Side          : {resp.get('side')}")
    print(f"  Type          : {resp.get('type')}")
    print(f"  Status        : {resp.get('status')}")
    print(f"  Orig Qty      : {resp.get('origQty')}")
    print(f"  Executed Qty  : {resp.get('executedQty')}")
    print(f"  Avg Price     : {avg}")
    print(f"  Time in Force : {resp.get('timeInForce', 'N/A')}")
    print(DIVIDER)


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    logger = setup_logging(args.log_level)

    api_key, api_secret = _resolve_credentials(args)
    _print_request_summary(args)

    client  = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    manager = OrderManager(client=client)

    try:
        resp = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.qty,
            price=args.price,
            stop_price=args.stop_price,
        )
        _print_order_response(resp)
        print("\n\u2705  Order placed successfully!")
        logger.info("CLI completed | orderId=%s status=%s", resp.get("orderId"), resp.get("status"))

    except ValidationError as exc:
        print(f"\n\u274c  Validation error: {exc}", file=sys.stderr)
        logger.warning("Validation error: %s", exc)
        sys.exit(2)

    except BinanceClientError as exc:
        print(f"\n\u274c  Binance API error [{exc.code}]: {exc.msg}", file=sys.stderr)
        logger.error("BinanceClientError: code=%s msg=%s", exc.code, exc.msg)
        sys.exit(3)

    except (ConnectionError, TimeoutError) as exc:
        print(f"\n\u274c  Network error: {exc}", file=sys.stderr)
        logger.error("Network error: %s", exc)
        sys.exit(4)

    except Exception as exc:
        print(f"\n\u274c  Unexpected error: {exc}", file=sys.stderr)
        logger.exception("Unexpected error")
        sys.exit(5)


if __name__ == "__main__":
    main()
