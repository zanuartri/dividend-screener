"""Supabase database operations for dividend screener."""

import os
import pandas as pd
import numpy as np
import streamlit as st
from config import ALL_COLUMNS, NUMERIC_COLS, MANUAL_COLUMNS
from .supabase_client import get_supabase_client


@st.cache_data(ttl=300, show_spinner=False)
def load_supabase_cached() -> pd.DataFrame:
    """Load data dari Supabase dengan caching untuk 5 menit."""
    try:
        client = get_supabase_client()
        df = client.load_saham()
        return df
    except Exception as e:
        st.error(f"❌ Gagal load dari Supabase: {str(e)[:150]}")
        raise


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist in dataframe."""
    for col in ALL_COLUMNS:
        if col not in df.columns:
            if col in NUMERIC_COLS:
                df[col] = np.nan
            elif col == "LastUpdated":
                df[col] = ""  # Keep as string, not datetime
            else:
                df[col] = ""
    # Don't convert LastUpdated to datetime - keep it as string for Supabase compatibility
    # It comes from Supabase already as ISO string and needs to stay that way
    return df


def make_empty_df() -> pd.DataFrame:
    """Create empty dataframe with correct column types."""
    df = pd.DataFrame(columns=ALL_COLUMNS)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Keep LastUpdated as string for consistency
    df["LastUpdated"] = ""
    return df


def load_csv(file_path: str = None) -> pd.DataFrame:
    """
    Load data dari Supabase.
    
    Note: CSV parameter kept for backward compatibility but not used.
    All data now comes from Supabase cloud database.
    """
    try:
        # Set data source indicator
        st.session_state['data_source'] = '☁️ Supabase'
        
        # Load dari Supabase
        df = load_supabase_cached()
        
        if df.empty:
            st.warning("⚠️ Belum ada data di Supabase. Buat stock baru terlebih dahulu.")
            return make_empty_df()
        
        return ensure_columns(df)
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)[:150]}")
        raise


def save_csv(df: pd.DataFrame, file_path: str = None) -> bool:
    """
    Save data ke Supabase.
    
    Note: CSV parameter kept for backward compatibility but not used.
    All data is saved to Supabase cloud database only.
    """
    try:
        # Select hanya column yang perlu disimpan
        save_df = df[MANUAL_COLUMNS].copy()
        
        # Simpan ke Supabase
        client = get_supabase_client()
        client.save_saham(save_df)
        
        # Clear cache
        load_supabase_cached.clear()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to save data: {str(e)[:150]}")
        return False


def save_changed_rows(df: pd.DataFrame, df_original: pd.DataFrame, file_path: str = None) -> bool:
    """
    Save hanya rows yang berubah ke Supabase.
    
    Args:
        df: Current dataframe
        df_original: Original dataframe untuk detect changes
        file_path: Not used (kept for compatibility)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Simple approach: compare rows and find differences
        # If shapes different (row added/removed), save all
        if len(df) != len(df_original):
            # Row added or deleted - save all
            save_df = df[MANUAL_COLUMNS].copy()
        else:
            # Same number of rows - find changed ones
            # Compare each row
            changed_indices = []
            for idx in df.index:
                if idx < len(df_original):
                    row_current = df.iloc[idx][MANUAL_COLUMNS].fillna('')
                    row_original = df_original.iloc[idx][MANUAL_COLUMNS].fillna('')
                    # Compare values
                    if not (row_current == row_original).all():
                        changed_indices.append(idx)
                else:
                    # New row
                    changed_indices.append(idx)
            
            if len(changed_indices) == 0:
                # No changes
                return True
            
            # Save only changed rows
            save_df = df.iloc[changed_indices][MANUAL_COLUMNS].copy()
        
        # Simpan ke Supabase
        client = get_supabase_client()
        client.save_saham(save_df)
        
        # Clear cache
        load_supabase_cached.clear()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to save data: {str(e)[:150]}")
        return False
