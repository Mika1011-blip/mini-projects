import random
import pandas as pd
import streamlit as st
import yfinance as yf
import datetime 
import plotly.graph_objects as go


def get_stockData(tickerSymbol : str, period : str = "1y"):
    try :
        if not isinstance(tickerSymbol, str) or not tickerSymbol.strip():
            raise ValueError(f"Invalid tickerSymbol : {tickerSymbol}")
        if not isinstance(period, str) or not period.strip():
            raise ValueError(f"Invalid period : {period}")

        tickerSymbol = tickerSymbol.strip().upper()
        period = period.strip()

        data = yf.Ticker(tickerSymbol).history(period=period)
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"Invalid data returned for {tickerSymbol} : {type(data)}")
        if data.shape[0] == 0:
            raise ValueError(f"No data returned for {tickerSymbol} with period {period}")
        data = data.copy()
        data.reset_index(inplace=True)
        if "Date" not in data.columns:
            raise ValueError("Missing Date column after reset_index")

        data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.tz_localize(None)
        if data["Date"].isna().any():
            raise ValueError("Invalid Date values in stock data")

        for col in ('Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'):
            if col not in data.columns:
                raise ValueError(f"Missing {col} column in stock data")
            data[col] = pd.to_numeric(data[col], errors="coerce")
            if data[col].isna().any():
                raise ValueError(f"Invalid {col} values in stock data")
        return data
    except Exception as e :
        return str(e)

def rand_initialize(dates: pd.Series):
    try :
        if not isinstance(dates, pd.Series):
            raise ValueError(f"Invalid dates : {dates}")
        if dates.shape[0] == 0:
            raise ValueError("dates must not be empty")

        dates = pd.to_datetime(dates, errors="coerce")
        valid_dates = dates.dropna()
        if valid_dates.shape[0] == 0:
            raise ValueError("dates must contain at least one valid datetime")
        now = valid_dates.max()
        cutoff = now + pd.DateOffset(months=1)

        eligible = valid_dates[valid_dates >= cutoff]
        if eligible.shape[0] == 0:
            raise ValueError("No dates at least 1 month from the current date")

        return eligible.iloc[random.randrange(eligible.shape[0])]
    except Exception as e:
        return str(e)
    
