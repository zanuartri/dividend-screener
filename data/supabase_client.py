"""Supabase client for database operations."""

import os
import logging
from typing import Optional, List
import pandas as pd
from supabase import create_client, Client
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper untuk Supabase client dengan caching dan error handling."""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL. If None, read from env var SUPABASE_URL
            key: Supabase API key. If None, read from env var SUPABASE_KEY
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and Key not found. "
                "Please set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        # Initialize client
        self.client: Client = create_client(self.url, self.key)
        logger.info("✅ Supabase client initialized")
    
    def load_saham(self) -> pd.DataFrame:
        """
        Load semua data saham dari Supabase.
        
        Returns:
            DataFrame dengan columns: ticker, div_ttm, dpr, roe, bvps, eps, 
                                     manual_fair_value, interim, final, last_updated
        """
        try:
            response = self.client.table("saham").select("*").execute()
            data = response.data
            
            if not data:
                logger.info("No data found in saham table")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Rename kolom ke format yang sesuai dengan app
            rename_map = {
                'ticker': 'Ticker',
                'div_ttm': 'DivTTM',
                'dpr': 'DPR',
                'roe': 'ROE',
                'bvps': 'BVPS',
                'eps': 'EPS',
                'manual_fair_value': 'ManualFairValue',
                'interim': 'Interim',
                'final': 'Final',
                'last_updated': 'LastUpdated'
            }
            
            for old_col, new_col in rename_map.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Convert numeric columns
            numeric_cols = ['DivTTM', 'DPR', 'ROE', 'BVPS', 'EPS', 'ManualFairValue']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert LastUpdated to datetime
            if 'LastUpdated' in df.columns:
                df['LastUpdated'] = pd.to_datetime(df['LastUpdated'], errors='coerce')
            
            logger.info(f"✅ Loaded {len(df)} stocks from Supabase")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading saham from Supabase: {e}")
            raise
    
    def save_saham(self, df: pd.DataFrame) -> bool:
        """
        Simpan atau update data saham ke Supabase.
        
        Args:
            df: DataFrame dengan columns: Ticker, DivTTM, DPR, ROE, BVPS, EPS, 
                                          ManualFairValue, Interim, Final, LastUpdated
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for Supabase (rename columns)
            rename_map = {
                'Ticker': 'ticker',
                'DivTTM': 'div_ttm',
                'DPR': 'dpr',
                'ROE': 'roe',
                'BVPS': 'bvps',
                'EPS': 'eps',
                'ManualFairValue': 'manual_fair_value',
                'Interim': 'interim',
                'Final': 'final',
                'LastUpdated': 'last_updated'
            }
            
            # Select only columns yang ada dan rename
            cols_to_use = [col for col in rename_map.keys() if col in df.columns]
            df_prep = df[cols_to_use].copy()
            df_prep = df_prep.rename(columns={old: new for old, new in rename_map.items() if old in cols_to_use})
            
            # Convert to dictionary
            records = df_prep.to_dict(orient='records')
            
            # Upsert ke Supabase (insert atau update jika sudah ada)
            for record in records:
                # Clean None values
                record = {k: v for k, v in record.items() if pd.notna(v) and v is not None}
                
                if 'ticker' not in record or not record['ticker']:
                    logger.warning(f"Skipping record without ticker: {record}")
                    continue
                
                # Use upsert untuk handle insert/update
                try:
                    self.client.table("saham").upsert(record).execute()
                except Exception as e:
                    logger.error(f"Error upserting record {record}: {e}")
            
            logger.info(f"✅ Saved {len(records)} stocks to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving saham to Supabase: {e}")
            raise
    
    def add_stock(self, ticker: str, div_ttm: float = 0, dpr: float = 0, 
                  roe: float = 0, bvps: float = 0, eps: float = 0,
                  manual_fair_value: float = 0, interim: str = "", final: str = "") -> bool:
        """
        Add single stock ke Supabase.
        
        Args:
            ticker: Stock ticker
            div_ttm: Dividend TTM
            dpr: Dividend Payout Ratio
            roe: Return on Equity
            bvps: Book Value Per Share
            eps: Earnings Per Share
            manual_fair_value: Manual Fair Value override
            interim: Interim dividend month
            final: Final dividend month
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'ticker': ticker.upper(),
                'div_ttm': div_ttm,
                'dpr': dpr,
                'roe': roe,
                'bvps': bvps,
                'eps': eps,
                'manual_fair_value': manual_fair_value,
                'interim': interim,
                'final': final
            }
            
            self.client.table("saham").upsert(data).execute()
            logger.info(f"✅ Added/Updated stock: {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding stock {ticker}: {e}")
            raise
    
    def delete_stock(self, ticker: str) -> bool:
        """
        Delete stock dari Supabase.
        
        Args:
            ticker: Stock ticker to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.table("saham").delete().eq('ticker', ticker.upper()).execute()
            logger.info(f"✅ Deleted stock: {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting stock {ticker}: {e}")
            raise
    
    def get_stock(self, ticker: str) -> Optional[dict]:
        """
        Get single stock data.
        
        Args:
            ticker: Stock ticker
        
        Returns:
            Dictionary dengan stock data atau None jika tidak ditemukan
        """
        try:
            response = self.client.table("saham").select("*").eq('ticker', ticker.upper()).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting stock {ticker}: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check connection ke Supabase.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            response = self.client.table("saham").select("ticker").limit(1).execute()
            logger.info("✅ Supabase connection healthy")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection error: {e}")
            return False


@st.cache_resource
def get_supabase_client() -> SupabaseClient:
    """Get cached Supabase client instance."""
    try:
        return SupabaseClient()
    except Exception as e:
        st.error(f"❌ Failed to initialize Supabase: {e}")
        raise


def migrate_csv_to_supabase(csv_path: str) -> bool:
    """
    Migrate data dari CSV file ke Supabase.
    
    Args:
        csv_path: Path ke CSV file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load CSV
        df = pd.read_csv(csv_path, dtype=str)
        
        # Get Supabase client
        client = get_supabase_client()
        
        # Save ke Supabase
        return client.save_saham(df)
        
    except Exception as e:
        logger.error(f"❌ Error migrating CSV to Supabase: {e}")
        raise
