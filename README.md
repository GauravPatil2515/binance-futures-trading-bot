# Binance Futures Testnet — Trading Bot

A clean, structured Python CLI application that places **Market**, **Limit**, and **Stop-Market** orders on the [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com).

---

## Project Structure

```
binance-futures-trading-bot/
├── trading_bot/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── client.py          # Binance REST client wrapper
│   │   ├── orders.py          # Order placement logic
│   │   ├── validators.py      # Input validation
│   │   └── logging_config.py  # Rotating file + console logging
│   └── cli.py                 # CLI entry point (argparse)
├── logs/
│   ├── market_order.log       # Sample MARKET order log
│   └── limit_order.log        # Sample LIMIT order log
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Register on Binance Futures Testnet

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with your GitHub account
3. Navigate to **API Management** → Generate API key & secret
4. Copy both credentials

### 2. Clone & Install

```bash
git clone https://github.com/GauravPatil2515/binance-futures-trading-bot.git
cd binance-futures-trading-bot

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Edit .env and fill in BINANCE_API_KEY and BINANCE_API_SECRET
```

Or export them directly:

```bash
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

---

## How to Run

All commands are run from the repository root.

### Market Order (BUY)

```bash
python -m trading_bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --qty 0.001
```

### Limit Order (SELL)

```bash
python -m trading_bot.cli \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --qty 0.001 \
  --price 70000
```

### Stop-Market Order (Bonus — 3rd order type)

```bash
python -m trading_bot.cli \
  --symbol ETHUSDT \
  --side SELL \
  --type STOP_MARKET \
  --qty 0.01 \
  --stop-price 3200
```

### Pass credentials inline (override env vars)

```bash
python -m trading_bot.cli \
  --symbol BTCUSDT --side BUY --type MARKET --qty 0.001 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET
```

### Change log verbosity

```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --qty 0.001 --log-level DEBUG
```

---

## Sample Output

```
╔══════════════════════════════════════════════╗
║   Binance Futures Testnet — Trading Bot CLI  ║
╚══════════════════════════════════════════════╝

── Order Request Summary ──────────────────────
  Symbol    : BTCUSDT
  Side      : BUY
  Type      : MARKET
  Quantity  : 0.001
───────────────────────────────────────────────

── Order Response ──────────────────────────────
  Order ID      : 3785692341
  Client Order  : web_abc123
  Symbol        : BTCUSDT
  Status        : FILLED
  Side          : BUY
  Type          : MARKET
  Orig Qty      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 68241.50
  Time in Force : GTC
───────────────────────────────────────────────

✅  Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot.log` (rotating, max 5 MB, 3 backups).  
Sample logs from actual testnet runs are in:
- `logs/market_order.log` — MARKET BUY on BTCUSDT
- `logs/limit_order.log` — LIMIT SELL on BTCUSDT at $70,000

Log format:
```
YYYY-MM-DD HH:MM:SS | LEVEL    | logger.name | message
```

---

## Error Handling

| Scenario | Exit Code | Behaviour |
|---|---|---|
| Invalid symbol / side / qty | 2 | `ValidationError` — clear message, logs error |
| Binance API error (e.g. -1121) | 3 | `BinanceClientError` — shows code + message |
| Network / timeout | 4 | Descriptive connectivity message |
| Unexpected exception | 5 | Full traceback logged to file |

---

## Assumptions

- Testnet base URL is `https://testnet.binancefuture.com` (hardcoded default, overridable via `BINANCE_BASE_URL` env var)
- `STOP_MARKET` orders require `--stop-price`; the CLI validates this
- `LIMIT` orders use `timeInForce=GTC` by default
- No position management or account balance checks are performed — this is a pure order-placement tool
- `python-dotenv` will auto-load `.env` if present (requires adding `load_dotenv()` call or running via a dotenv-aware runner)

---

## Requirements

```
requests>=2.31.0
python-dotenv>=1.0.0
```

Python 3.9+ required.
