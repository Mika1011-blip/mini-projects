# Trading Simulator

Streamlit trading simulator based on historical OHLCV market data (Yahoo Finance).

## Main Files

- `app.py`: Streamlit UI and simulation orchestration.
- `run_simulation_service.py`: market data retrieval/validation (`yfinance`).
- `trade_service.py`: order management, position updates, PnL/fees logic.
- `requirements.txt`: Python dependencies.

## Features

- Manual and automatic stepping through candles.
- Position and trade tracking.
- Fee-aware gross/net PnL.
- Interactive charting and dashboard metrics.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:
   - `pip install -r requirements.txt`

## Run

- `streamlit run app.py`

## Design Docs

- `Conceptual__design/`: architecture and sequence diagrams (`.drawio`).

## Notes

- The folder currently includes local runtime artifacts (`venv/`, caches, generated files).
- For cleaner history, keep source/design files and ignore machine-local artifacts.
