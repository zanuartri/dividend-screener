"""Filter and preset management for stock screening."""

import pandas as pd
import streamlit as st
from config import FILTER_PRESETS


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply filter criteria to dataframe.
    
    Args:
        df: Input dataframe
        filters: Dict with keys:
            - signals: List of allowed signals
            - sectors: List of allowed sectors
            - discount_min: Minimum discount (%)
            - yield_min: Minimum yield (%)
            - roe_min: Minimum ROE (%)
            - dpr_max: Maximum DPR (%)
    
    Returns:
        Filtered dataframe
    """
    if df.empty:
        return df
    
    filtered = df.copy()
    
    # Signal filter
    if filters.get('signals'):
        filtered = filtered[filtered['Signal'].isin(filters['signals'])]
    
    # Sector filter
    if filters.get('sectors'):
        filtered = filtered[filtered['Sector'].isin(filters['sectors'])]
    
    # Numeric filters using df.eval for performance
    conditions = []
    
    discount_min = filters.get('discount_min', 0)
    if discount_min > 0:
        conditions.append(f"Discount >= {discount_min / 100}")
    
    yield_min = filters.get('yield_min', 0)
    if yield_min > 0:
        conditions.append(f"DivYield >= {yield_min / 100}")
    
    roe_min = filters.get('roe_min', 0)
    if roe_min > 0:
        conditions.append(f"ROE >= {roe_min}")  # ROE stored as percentage in CSV
    
    dpr_max = filters.get('dpr_max', 1000)
    if dpr_max < 1000:
        conditions.append(f"DPR <= {dpr_max}")  # DPR stored as percentage in CSV
    
    # Apply all conditions with df.eval
    if conditions:
        query_string = " and ".join(conditions)
        try:
            filtered = filtered.query(query_string)
        except Exception:
            # Fallback to traditional filtering if eval fails
            for condition in conditions:
                col, op, val = condition.replace('>=', '|>=|').replace('<=', '|<=|').split('|')
                val = float(val)
                if op == '>=':
                    filtered = filtered[filtered[col.strip()] >= val]
                else:  # <=
                    filtered = filtered[filtered[col.strip()] <= val]
    
    return filtered


def apply_preset(preset_name: str):
    """
    Apply predefined filter preset to session state.
    Uses a flag to trigger preset application before widgets are rendered.
    
    Available presets:
    - High Yield: Focus on high dividend yields
    - Value Play: Undervalued stocks with good ROE
    - Growth Dividend: Strong ROE with sustainable dividends
    - Safe Income: Conservative dividend plays
    """
    if preset_name in FILTER_PRESETS:
        # Set flag to apply preset on next rerun
        st.session_state['_pending_preset'] = preset_name


def _apply_pending_preset():
    """
    Internal function to apply pending preset before widgets are rendered.
    This must be called before any filter widgets are instantiated.
    """
    if '_pending_preset' in st.session_state:
        preset_name = st.session_state['_pending_preset']
        if preset_name in FILTER_PRESETS:
            preset = FILTER_PRESETS[preset_name]
            
            # Apply all preset values
            for key, value in preset.items():
                st.session_state[key] = value
        
        # Clear the pending flag
        del st.session_state['_pending_preset']


def clear_filters():
    """Reset all filters to default values."""
    st.session_state.filter_signals = []
    st.session_state.filter_sectors = []
    # Default to the lowest options available in new static dropdowns
    st.session_state.filter_discount_min = 0
    st.session_state.filter_yield_min = 0  # user requested default 0
    st.session_state.filter_roe_min = 0    # user requested default 0
    st.session_state.filter_dpr_max = 1000
