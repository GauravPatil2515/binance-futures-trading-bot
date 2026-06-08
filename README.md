# Binance Futures Testnet — Trading Bot

A clean, structured Python application that places **Market**, **Limit**, and **Stop-Market** orders on the [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com) — available as both a **CLI tool** and a **web UI**.

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
│   ├── web/
│   │   ├── app.py             # Flask web UI server
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── static/
│   │       ├── style.css
│   │       └── app.js
│   └── cli.py                 # CLI entry point (argparse)
├── logs/
│   ├── market_order.log
│   └── limit_order.log
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Register on Binance Futures Testnet

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with your GitHub account
3. **API Management** → Generate API key & secret

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

---

## Usage — CLI

### Market Order (BUY)
```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### Limit Order (SELL)
```bash
python -m trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 70000
```

### Stop-Market Order (Bonus)
```bash
python -m trading_bot.cli --symbol ETHUSDT --side SELL --type STOP_MARKET --qty 0.01 --stop-price 3200
```

---

## Usage — Web UI (Bonus)

```bash
python -m trading_bot.web.app
```

Then open **http://localhost:5000** in your browser.

Features:
- Dark trading dashboard (Binance-inspired)
- BUY / SELL toggle with color coding
- Dynamic price fields (shown only when relevant)
- Live order response with all fields
- In-session order history table

---

## Sample CLI Output

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
  Status        : FILLED
  Executed Qty  : 0.001
  Avg Price     : 68241.50
───────────────────────────────────────────────

✅  Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot.log` (rotating, max 5 MB, 3 backups).

Log format:
```
YYYY-MM-DD HH:MM:SS | LEVEL    | logger.name | message
```

---

## Error Handling

| Scenario | Exit Code | Behaviour |
|---|---|---|
| Invalid symbol / side / qty | 2 | `ValidationError` — clear message |
| Binance API error | 3 | `BinanceClientError` — code + message |
| Network / timeout | 4 | Connectivity message |
| Unexpected exception | 5 | Full traceback logged to file |

---

## Assumptions

- Testnet base URL: `https://testnet.binancefuture.com` (overridable via `BINANCE_BASE_URL`)
- `LIMIT` orders use `timeInForce=GTC`
- `STOP_MARKET` requires `--stop-price`
- No position management — pure order-placement tool

---

## Requirements

```
requests>=2.31.0
python-dotenv>=1.0.0
flask>=3.0.0
```

Python 3.9+ required.
