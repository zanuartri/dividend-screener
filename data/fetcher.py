"""Yahoo Finance data fetching operations."""

import logging
import numpy as np
import pandas as pd
import streamlit as st
import requests

try:
    import yfinance as yf
except ImportError:
    yf = None

from config import EXCHANGE_SUFFIX


@st.cache_data(ttl=600, show_spinner=False)
def fetch_single_ticker_data(ticker: str, exchange_suffix: str = EXCHANGE_SUFFIX):
    """
    Fetch data for a single ticker with individual caching and proper error handling.
    
    Returns:
        dict: {"Ticker": str, "CurrentPrice": float, "Sector": str, "Error": str or None}
    """
    if yf is None:
        return {"Ticker": ticker, "CurrentPrice": np.nan, "Sector": "Unknown", 
                "Error": "yfinance not installed"}
    
    yf_ticker = ticker + exchange_suffix
    
    try:
        ticker_obj = yf.Ticker(yf_ticker)
        price = None
        
        # Try fast_info first (faster)
        try:
            if hasattr(ticker_obj, "fast_info") and "last_price" in ticker_obj.fast_info:
                price = ticker_obj.fast_info["last_price"]
        except (KeyError, AttributeError):
            pass
        
        # Fallback to info dictionary
        if price is None or price == 0:
            try:
                info = ticker_obj.info
                price = info.get("currentPrice", None) or info.get("regularMarketPrice", None)
            except (KeyError, TypeError, requests.exceptions.HTTPError):
                pass
        
        # Last resort: historical data
        if price is None or price == 0:
            try:
                hist = ticker_obj.history(period="1d")
                if not hist.empty:
                    price = hist["Close"].iloc[-1]
            except Exception as e:
                logging.warning(f"Historical data fetch failed for {ticker}: {e}")
        
        # Fetch sector with error handling
        sector = "Unknown"
        try:
            sector = ticker_obj.info.get("sector", "Unknown")
        except (KeyError, TypeError, requests.exceptions.HTTPError):
            pass
        
        # Validate price
        if price is not None and (price <= 0 or pd.isna(price)):
            price = np.nan
        
        return {"Ticker": ticker, "CurrentPrice": price, "Sector": sector, "Error": None}
        
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Network error fetching {ticker}: {e}")
        return {"Ticker": ticker, "CurrentPrice": np.nan, "Sector": "Unknown", 
                "Error": "Network error"}
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout fetching {ticker}: {e}")
        return {"Ticker": ticker, "CurrentPrice": np.nan, "Sector": "Unknown", 
                "Error": "Timeout"}
    except KeyError as e:
        logging.error(f"Missing data field for {ticker}: {e}")
        return {"Ticker": ticker, "CurrentPrice": np.nan, "Sector": "Unknown", 
                "Error": f"Missing field: {e}"}
    except Exception as e:
        logging.exception(f"Unexpected error fetching {ticker}: {e}")
        return {"Ticker": ticker, "CurrentPrice": np.nan, "Sector": "Unknown", 
                "Error": str(e)[:50]}


def fetch_all_tickers(tickers: list, progress_callback=None) -> pd.DataFrame:
    """
    Fetch data for all tickers.
    
    Args:
        tickers: List of ticker symbols
        progress_callback: Optional callback function(current, total) for progress
        
    Returns:
        DataFrame with columns: Ticker, CurrentPrice, Sector
    """
    results = []
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        result = fetch_single_ticker_data(ticker)
        results.append(result)
        
        if progress_callback:
            progress_callback(i + 1, total)
    
    return pd.DataFrame(results)
