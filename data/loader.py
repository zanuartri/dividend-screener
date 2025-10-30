"""CSV data loading and saving operations."""

import pandas as pd
import numpy as np
import streamlit as st
from config import CSV_PATH, ALL_COLUMNS, NUMERIC_COLS, MANUAL_COLUMNS


@st.cache_data(ttl=300, show_spinner=False)
def load_csv_cached(file_path: str = CSV_PATH) -> pd.DataFrame:
    """Load CSV with caching for 5 minutes."""
    try:
        df = pd.read_csv(file_path, dtype=str)
        return df
    except FileNotFoundError:
        # Create new CSV if not exists
        pd.DataFrame(columns=MANUAL_COLUMNS).to_csv(file_path, index=False)
        return pd.DataFrame(columns=MANUAL_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=MANUAL_COLUMNS)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist in dataframe."""
    for col in ALL_COLUMNS:
        if col not in df.columns:
            if col in NUMERIC_COLS:
                df[col] = np.nan
            elif col == "LastUpdated":
                df[col] = pd.NaT
            else:
                df[col] = ""
    df["LastUpdated"] = pd.to_datetime(df["LastUpdated"], errors='coerce')
    return df


def make_empty_df() -> pd.DataFrame:
    """Create empty dataframe with correct column types."""
    df = pd.DataFrame(columns=ALL_COLUMNS)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
    return df


def load_csv(file_path: str = CSV_PATH) -> pd.DataFrame:
    """Load and prepare dataframe from CSV file with caching."""
    df = load_csv_cached(file_path)
    if df.empty:
        return make_empty_df()
    df = ensure_columns(df)
    return df


def save_csv(df: pd.DataFrame, file_path: str = CSV_PATH) -> bool:
    """Save dataframe to CSV file and clear cache."""
    try:
        df.to_csv(file_path, index=False)
        # Clear cache after save
        load_csv_cached.clear()
        return True
    except Exception as e:
        st.error(f"❌ Failed to save data: {e}")
        return False
