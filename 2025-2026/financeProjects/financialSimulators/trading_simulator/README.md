# Trading Simulator

Streamlit trading simulator using historical OHLCV data from Yahoo Finance.

## Main Files

- `app.py` : Streamlit UI + simulation flow.
- `run_simulation_service.py` : market data retrieval/validation (`yfinance`).
- `trade_service.py` : order/position logic, PnL, fees, and updates.
- `requirements.txt` : Python dependencies.

## Features

- Manual and automatic stepping through candles.
- Order and position tracking.
- Fee-aware gross/net PnL computation.
- Interactive charts and dashboard metrics.

## Setup

1. Create and activate a Python environment.
2. Install deps:
   - `pip install -r requirements.txt`

## Run

- `streamlit run app.py`

## Notes

- The folder currently contains committed local artifacts (`venv/`, caches, diagrams).
- For cleaner versioning, keep only source + requirements and ignore local runtime artifacts.
