"""Stock signal calculation and valuation logic."""

import numpy as np
import pandas as pd
import streamlit as st
from utils.formatters import coerce_float
from config import THRESHOLDS


@st.cache_data(show_spinner=False)
def compute_fair_value_vectorized(bvps_series: pd.Series, eps_series: pd.Series) -> pd.Series:
    """Vectorized fair value computation for entire series."""
    fair_value = np.sqrt(
        THRESHOLDS['GRAHAM_MULTIPLIER'] * 
        bvps_series.fillna(0) * 
        eps_series.fillna(0)
    )
    # Set invalid values to NaN
    fair_value = fair_value.where((bvps_series > 0) & (eps_series > 0), np.nan)
    return fair_value


def compute_fair_value(row: pd.Series) -> float:
    """
    Compute Graham's fair value using BVPS and EPS.
    Formula: sqrt(22.5 * BVPS * EPS)
    
    Note: This is kept for backwards compatibility but vectorized version is preferred.
    """
    bvps = coerce_float(row.get("BVPS"))
    eps = coerce_float(row.get("EPS"))
    
    if pd.isna(bvps) or pd.isna(eps) or bvps <= 0 or eps <= 0:
        return np.nan
    
    return float(np.sqrt(THRESHOLDS['GRAHAM_MULTIPLIER'] * bvps * eps))


@st.cache_data(show_spinner=False)
def assign_signals_vectorized(discount: pd.Series, div_yield: pd.Series, roe: pd.Series) -> pd.Series:
    """
    Vectorized signal assignment for entire dataframe.
    Much faster than row-by-row apply.
    """
    signals = pd.Series("WAIT", index=discount.index)
    
    # Handle NaN values
    valid_mask = discount.notna() & div_yield.notna() & roe.notna()
    
    # MINIMUM YIELD CHECK
    yield_ok = div_yield >= THRESHOLDS['MIN_YIELD']
    
    # OVERVALUED CHECK
    overvalued = discount < 0
    signals = signals.where(~(valid_mask & overvalued & yield_ok), "WAIT FOR DIP")
    
    # ROE CHECK
    roe_basic = roe >= THRESHOLDS['MIN_ROE_BASIC']
    exceptional = (div_yield >= THRESHOLDS['EXCEPTIONAL_YIELD']) & (discount >= THRESHOLDS['HIGH_DISCOUNT'])
    
    # STRONG BUY
    strong_buy = (discount >= THRESHOLDS['HIGH_DISCOUNT']) & (roe >= THRESHOLDS['EXCELLENT_ROE']) & yield_ok
    signals = signals.where(~(valid_mask & strong_buy), "STRONG BUY")
    
    # BUY
    buy = (discount >= THRESHOLDS['GOOD_DISCOUNT']) & (roe >= THRESHOLDS['GOOD_ROE']) & yield_ok & ~strong_buy
    signals = signals.where(~(valid_mask & buy), "BUY")
    
    # ACCUMULATE
    accumulate = ((discount >= THRESHOLDS['FAIR_DISCOUNT']) & roe_basic & yield_ok) | (exceptional & yield_ok)
    accumulate = accumulate & ~strong_buy & ~buy
    signals = signals.where(~(valid_mask & accumulate), "ACCUMULATE")
    
    return signals


def assign_signal(row: pd.Series) -> str:
    """
    Assign buy/sell signal based on discount, dividend yield, and ROE.
    
    Note: This is kept for backwards compatibility but vectorized version is preferred.
    """
    discount = row.get("Discount", 0)
    div_yield = row.get("DivYield", 0)
    roe = row.get("ROE", 0)
    
    if pd.isna(discount) or pd.isna(div_yield) or pd.isna(roe):
        return "WAIT"
    
    # MINIMUM YIELD CHECK
    if div_yield < THRESHOLDS['MIN_YIELD']:
        return "WAIT"
    
    # OVERVALUED CHECK
    if discount < 0:
        return "WAIT FOR DIP"
    
    # ROE CHECK with exception for exceptional yield
    if roe < THRESHOLDS['MIN_ROE_BASIC']:
        # Exception: Very high yield and discount can compensate low ROE
        if div_yield >= THRESHOLDS['EXCEPTIONAL_YIELD'] and discount >= THRESHOLDS['HIGH_DISCOUNT']:
            return "ACCUMULATE"
        else:
            return "WAIT"
    
    # SIGNAL ASSIGNMENT (ROE ≥ 8%)
    if discount >= THRESHOLDS['HIGH_DISCOUNT'] and roe >= THRESHOLDS['EXCELLENT_ROE']:
        return "STRONG BUY"
    if discount >= THRESHOLDS['GOOD_DISCOUNT'] and roe >= THRESHOLDS['GOOD_ROE']:
        return "BUY"
    if discount >= THRESHOLDS['FAIR_DISCOUNT']:
        return "ACCUMULATE"
    
    return "WAIT"


@st.cache_data(show_spinner=False, ttl=60)
def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process dataframe: compute fair value, discount, yield, and signals.
    Fully vectorized for maximum performance with caching.
    Uses ManualFairValue if available, otherwise calculates using Graham Number.
    """
    if df.empty:
        return df
    
    # Convert to numeric (vectorized)
    numeric_cols = ["BVPS", "EPS", "ROE", "DivTTM", "DPR", "CurrentPrice", "ManualFairValue"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Compute Graham fair value (vectorized with caching)
    df['GrahamFairValue'] = compute_fair_value_vectorized(df['BVPS'], df['EPS'])
    
    # Use ManualFairValue if available, otherwise use Graham calculation
    # ManualFairValue > 0 means user has set a manual value
    if 'ManualFairValue' not in df.columns:
        df['ManualFairValue'] = np.nan
    
    df['FairValue'] = np.where(
        (df['ManualFairValue'].notna()) & (df['ManualFairValue'] > 0),
        df['ManualFairValue'],
        df['GrahamFairValue']
    )
    
    # Mark stocks using manual fair value
    df['UsesManualFV'] = (df['ManualFairValue'].notna()) & (df['ManualFairValue'] > 0)
    
    # Compute discount (vectorized)
    df['Discount'] = np.where(
        (df['FairValue'] > 0) & (df['CurrentPrice'] > 0),
        (df['FairValue'] - df['CurrentPrice']) / df['FairValue'],
        np.nan
    )
    
    # Compute dividend yield (vectorized)
    df['DivYield'] = np.where(
        df['CurrentPrice'] > 0,
        df['DivTTM'] / df['CurrentPrice'],
        np.nan
    )
    
    # Assign signals (vectorized with caching)
    df['Signal'] = assign_signals_vectorized(df['Discount'], df['DivYield'], df['ROE'])
    
    return df
