"""
Formatter utilities for displaying data in the dividend dashboard.
"""
import pandas as pd
import numpy as np


def style_signal(signal: str) -> str:
    """Apply color styling to signal cells"""
    if signal in ("STRONG BUY", "BUY", "ACCUMULATE"):
        return "background-color: #cc7a00; color: #000000; font-weight: bold;"
    return ""


def get_yield_color(val):
    """Color gradient for dividend yield: Green (high) -> Yellow -> Red (low)"""
    if pd.isna(val):
        return ""
    if val >= 0.1:
        return "background-color: rgba(0, 255, 65, 0.25); color: #00ff41; font-weight: 600;"
    elif val >= 0.08:
        return "background-color: rgba(144, 238, 144, 0.2); color: #90ee90; font-weight: 600;"
    elif val >= 0.05:
        return "background-color: rgba(255, 215, 0, 0.2); color: #ffd700; font-weight: 500;"
    else:
        return "background-color: rgba(255, 51, 51, 0.2); color: #ff6666; font-weight: 500;"


def get_discount_color(val):
    """Color gradient for discount: Green (positive/undervalued) -> Red (negative/overvalued)"""
    if pd.isna(val):
        return ""
    if val >= 0.25:
        return "background-color: rgba(0, 255, 65, 0.3); color: #00ff41; font-weight: 600;"
    elif val >= 0.15:
        return "background-color: rgba(144, 238, 144, 0.25); color: #90ee90; font-weight: 600;"
    elif val >= 0:
        return "background-color: rgba(255, 215, 0, 0.2); color: #ffd700; font-weight: 500;"
    else:
        return "background-color: rgba(255, 51, 51, 0.2); color: #ff6666; font-weight: 500;"


def get_roe_color(val):
    """Color gradient for ROE: Green (excellent) -> Yellow (good) -> Red (weak)
    ROE is stored as percentage value (15.0 = 15%), not decimal"""
    if pd.isna(val):
        return ""
    if val >= 15.0:
        return "background-color: rgba(0, 255, 65, 0.2); color: #00ff41; font-weight: 600;" 
    elif val >= 10.0:
        return "background-color: rgba(144, 238, 144, 0.25); color: #90ee90; font-weight: 600;"
    elif val >= 8.0:
        return "background-color: rgba(255, 215, 0, 0.2); color: #ffd700; font-weight: 500;"
    else:
        return "background-color: rgba(255, 51, 51, 0.2); color: #ff6666; font-weight: 500;"


def get_dpr_color(val):
    """Color gradient for DPR: Green (safe <70%) -> Yellow (elevated 70-100%) -> Red (risky >100%)
    DPR is stored as percentage value (70.0 = 70%), not decimal"""
    if pd.isna(val):
        return ""
    if val <= 70.0:
        return "background-color: rgba(0, 255, 65, 0.2); color: #00ff41; font-weight: 600;"  # Safe
    elif val <= 80.0:
        return "background-color: rgba(144, 238, 144, 0.25); color: #90ee90; font-weight: 600;" # Moderate
    elif val <= 100.0:
        return "background-color: rgba(255, 215, 0, 0.2); color: #ffd700; font-weight: 500;" # Elevated risk
    else:
        return "background-color: rgba(255, 51, 51, 0.2); color: #ff6666; font-weight: 500;" # High risk (>100%)


def coerce_float(x) -> float:
    """Convert various inputs to float, handling strings and errors gracefully"""
    try:
        if x is None or (isinstance(x, str) and x.strip() == ""):
            return np.nan
        if isinstance(x, str):
            x = x.replace(",", "")
        return float(x)
    except (ValueError, TypeError):
        return np.nan
