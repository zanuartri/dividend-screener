# app.py
# Bloomberg Terminal-style Dividend Dashboard
# Professional dividend screener for IDX equities

from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Import from custom modules
from config import (
    EXCHANGE_SUFFIX, MANUAL_COLUMNS,
    DISPLAY_NAMES, FORMATTERS, MONTH_OPTIONS, SIGNAL_OPTIONS, FILTER_PRESETS
)
from data import load_csv, save_csv, fetch_all_tickers
from models import process_dataframe, apply_filters, apply_preset, clear_filters, _apply_pending_preset
from ui import get_custom_css, get_loading_skeleton, display_metric_cards, show_stock_details
from utils import coerce_float, style_signal, get_yield_color, get_discount_color, get_roe_color, get_dpr_color

try:
    import yfinance as yf
except ImportError:
    yf = None


# ============================
# PAGE CONFIGURATION
# ============================
st.set_page_config(
    page_title="Dividend Screener | IDX",
    layout="wide",
    page_icon="�",
    initial_sidebar_state="collapsed"
)

st.markdown(get_custom_css(), unsafe_allow_html=True)


# ============================
# CRUD DIALOG
# ============================
@st.dialog("MANAGE STOCKS", width="large")
def crud_dialog():
    """Dialog for adding, editing, or deleting stocks."""
    # Header with action selector
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a1a 0%, #242424 100%); padding: 14px 18px; border-left: 4px solid #ff8c00; border-radius: 4px; margin-bottom: 16px;'>
        <div style='font-size: 11px; color: #ff8c00; letter-spacing: 1px; font-weight: 700; font-family: IBM Plex Mono, monospace;'>SELECT ACTION</div>
    </div>
    """, unsafe_allow_html=True)
    
    action = st.radio("", ["Add New", "Edit Data", "Delete Data"], key="dialog_action", horizontal=True, label_visibility="collapsed")
    
    df = st.session_state.df
    ticker_to_edit = None
    index_to_edit = None
    stock_data = {}

    if action in ["Edit Data", "Delete Data"]:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        sorted_tickers = [""] + df["Ticker"].sort_values().tolist()
        ticker_to_edit = st.selectbox("SELECT STOCK", sorted_tickers)
        if ticker_to_edit:
            match = df[df["Ticker"] == ticker_to_edit]
            if not match.empty:
                index_to_edit = match.index[0]
                stock_data = match.iloc[0].to_dict()

    if action == "Delete Data":
        if ticker_to_edit:
            st.markdown(f"""
            <div style='background: rgba(255, 51, 51, 0.1); padding: 14px 18px; border-left: 4px solid #ff3333; border-radius: 4px; margin: 16px 0;'>
                <div style='font-size: 12px; color: #ff3333; font-weight: 700; font-family: IBM Plex Mono, monospace;'>⚠️ DELETE {ticker_to_edit}?</div>
                <div style='font-size: 10px; color: #aaa; margin-top: 4px;'>This action cannot be undone</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ CONFIRM DELETE", type="secondary", disabled=not ticker_to_edit, use_container_width=True):
            st.session_state.df = df.drop(index=index_to_edit).reset_index(drop=True)
            save_csv(st.session_state.df[MANUAL_COLUMNS])
            st.toast(f"✅ {ticker_to_edit} DELETED")
            st.rerun()
        return

    with st.form("dialog_form"):
        # Info banner
        st.markdown("""
        <div style='background: rgba(255, 140, 0, 0.1); padding: 12px 16px; border-left: 3px solid #ff8c00; border-radius: 3px; margin-bottom: 20px;'>
            <div style='font-size: 10px; color: #ff8c00; font-weight: 600; letter-spacing: 0.5px;'>ℹ️ SECTOR will be fetched automatically from Yahoo Finance</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ticker input
        st.markdown("<div style='font-size: 11px; color: #ff8c00; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; font-family: IBM Plex Mono, monospace;'>STOCK IDENTIFIER</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        new_data = {"Ticker": c1.text_input("TICKER", value=stock_data.get("Ticker", ""), placeholder="e.g., BBCA").upper()}

        # Financial metrics section
        st.markdown("<div style='font-size: 11px; color: #ff8c00; font-weight: 700; letter-spacing: 1px; margin: 20px 0 8px 0; font-family: IBM Plex Mono, monospace;'>FINANCIAL METRICS</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        new_data["DivTTM"] = c1.number_input("DIV TTM (IDR)", value=coerce_float(stock_data.get("DivTTM", 0)), min_value=0.0)
        
        # DPR and ROE stored as percentage values (17.3 = 17.3%), NOT decimal
        dpr_value = coerce_float(stock_data.get("DPR", 0))
        roe_value = coerce_float(stock_data.get("ROE", 0))
        
        dpr_input = c2.number_input("DPR (%)", value=dpr_value, min_value=0.0)
        roe_input = c3.number_input("ROE (%)", value=roe_value, min_value=0.0)
        
        # Store as percentage values directly
        new_data["DPR"] = dpr_input
        new_data["ROE"] = roe_input
        
        c4, c5 = st.columns(2)
        new_data["BVPS"] = c4.number_input("BVPS (IDR)", value=coerce_float(stock_data.get("BVPS", 0)), min_value=0.0)
        new_data["EPS"] = c5.number_input("EPS (IDR)", value=coerce_float(stock_data.get("EPS", 0)), min_value=0.0)
        
        # Manual Fair Value section
        st.markdown("<div style='font-size: 11px; color: #ff8c00; font-weight: 700; letter-spacing: 1px; margin: 20px 0 8px 0; font-family: IBM Plex Mono, monospace;'>VALUATION OVERRIDE (OPTIONAL)</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: rgba(255, 140, 0, 0.1); padding: 12px 16px; border-left: 3px solid #ff8c00; border-radius: 3px; margin-bottom: 12px;'>
            <div style='font-size: 10px; color: #ff8c00; font-weight: 600; letter-spacing: 0.5px;'>ℹ️ Set manual fair value to override Graham Number calculation. Leave at 0 to use automatic calculation.</div>
        </div>
        """, unsafe_allow_html=True)
        manual_fv_value = coerce_float(stock_data.get("ManualFairValue", 0))
        new_data["ManualFairValue"] = st.number_input(
            "MANUAL FAIR VALUE (IDR)", 
            value=manual_fv_value, 
            min_value=0.0,
            help="Enter custom fair value. Set to 0 to use Graham Number formula (√(22.5 × BVPS × EPS))"
        )

        # Dividend schedule section
        st.markdown("<div style='font-size: 11px; color: #ff8c00; font-weight: 700; letter-spacing: 1px; margin: 20px 0 8px 0; font-family: IBM Plex Mono, monospace;'>DIVIDEND SCHEDULE</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        try:
            interim_idx = MONTH_OPTIONS.index(stock_data.get("Interim", ""))
        except (ValueError, TypeError):
            interim_idx = 0
        try:
            final_idx = MONTH_OPTIONS.index(stock_data.get("Final", ""))
        except (ValueError, TypeError):
            final_idx = 0
        new_data["Interim"] = c1.selectbox("INTERIM DIVIDEND", options=MONTH_OPTIONS, index=interim_idx)
        new_data["Final"] = c2.selectbox("FINAL DIVIDEND", options=MONTH_OPTIONS, index=final_idx)

        # Submit button
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button(f"💾 SAVE {action.upper()}", type="primary", use_container_width=True):
            new_data["LastUpdated"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            if action == "Add New":
                if not new_data["Ticker"]:
                    st.error("❌ TICKER REQUIRED")
                elif new_data["Ticker"] in df["Ticker"].values:
                    st.error(f"❌ {new_data['Ticker']} ALREADY EXISTS")
                else:
                    st.session_state.df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            elif action == "Edit Data" and index_to_edit is not None:
                for k in MANUAL_COLUMNS:
                    st.session_state.df.at[index_to_edit, k] = new_data.get(k, "")

            save_csv(st.session_state.df[MANUAL_COLUMNS])
            st.toast(f"✅ {new_data['Ticker']} SAVED SUCCESSFULLY")
            st.rerun()


# ============================
# MAIN APPLICATION
# ============================
def main():
    """Main dashboard application with market data fetching and analysis."""
    _apply_pending_preset()
    
    if 'df' not in st.session_state:
        with st.spinner("⏳ Loading data..."):
            st.session_state.df = load_csv()

    df_ref = st.session_state.df
    tickers_to_fetch = df_ref["Ticker"].dropna().unique()

    # Fetch market data with optimized caching
    if yf is not None and len(tickers_to_fetch) > 0:
        # Only fetch if data is stale (older than 10 minutes)
        should_fetch = False
        if 'last_yf_fetch' not in st.session_state:
            should_fetch = True
        else:
            time_since_fetch = (datetime.now() - st.session_state.last_yf_fetch).total_seconds()
            if time_since_fetch > 600:  # 10 minutes
                should_fetch = True
        
        if should_fetch:
            # Show loading skeleton on first load
            loading_placeholder = st.empty()
            with loading_placeholder:
                st.markdown(get_loading_skeleton(), unsafe_allow_html=True)
            
            # Fetch data
            fetched_df = fetch_all_tickers(list(tickers_to_fetch))
            
            # Merge with base data (vectorized)
            if not fetched_df.empty:
                # Create a dict for O(1) lookup
                price_dict = fetched_df.set_index('Ticker')['CurrentPrice'].to_dict()
                sector_dict = fetched_df.set_index('Ticker')['Sector'].to_dict()
                
                # Update efficiently
                for ticker in tickers_to_fetch:
                    if ticker in price_dict:
                        mask = df_ref["Ticker"] == ticker
                        st.session_state.df.loc[mask, "CurrentPrice"] = price_dict[ticker]
                        if ticker in sector_dict:
                            st.session_state.df.loc[mask, "Sector"] = sector_dict[ticker]
            
            st.session_state.last_yf_fetch = datetime.now()
            loading_placeholder.empty()

    # Process dataframe with signals (cached)
    df_processed = process_dataframe(st.session_state.df.copy())

    # === HEADER ===
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
    
    # === ENHANCED HEADER ===
    col_header, col_time = st.columns([3, 1])
    with col_header:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1a1a1a 0%, #0f0f0f 100%); padding: 16px 20px; border-left: 4px solid #ff8c00; border-radius: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.5);">
            <div style="font-size: 24px; font-weight: 700; color: #ff8c00; letter-spacing: 4px; font-family: IBM Plex Mono, monospace;">
                DIVIDEND SCREENER
            </div>
            <div style="font-size: 10px; color: #808080; letter-spacing: 2px; margin-top: 6px; font-family: IBM Plex Mono, monospace;">
                IDX EQUITIES · REAL-TIME ANALYSIS · DIVIDEND FOCUSED
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_time:
        now = datetime.now()
        st.markdown(f"""
        <div style="background: #0f0f0f; padding: 16px 20px; border: 1px solid #262626; border-radius: 2px; text-align: right; height: 92px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.5);">
            <div style="font-size: 18px; color: #ff8c00; font-weight: 700; font-family: IBM Plex Mono, monospace; letter-spacing: 2px;">
                {now.strftime('%d %b %Y').upper()}
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 4px; letter-spacing: 1px; font-family: IBM Plex Mono, monospace;">
                {now.strftime('%H:%M:%S')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin: 16px 0;"></div>', unsafe_allow_html=True)

    # === SUMMARY METRICS ===
    display_metric_cards(df_processed)

    # === ACTION BUTTONS ===
    st.markdown('<div style="margin: 4px 0;"></div>', unsafe_allow_html=True)
    
    # Custom CSS for smaller buttons
    st.markdown("""
    <style>
    /* Target the specific button container */
    button[kind="primary"],
    button[kind="secondary"] {
        min-height: 32px !important;
        height: 32px !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
        font-size: 11px !important;
        min-width: 120px !important; /* keep single row without crowding */
        white-space: nowrap !important;
    }
    
    /* Target button text */
    button p {
        font-size: 11px !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }
    
    /* Target all buttons in streamlit */
    .stButton > button {
        min-height: 32px !important;
        height: 32px !important;
        padding: 4px 12px !important;
        font-size: 11px !important;
        min-width: 120px !important;
        white-space: nowrap !important;
    }
    
    /* Target download button specifically - match regular button style */
    .stDownloadButton > button {
        min-height: 32px !important;
        height: 32px !important;
        padding: 4px 12px !important;
        font-size: 11px !important;

    /* Responsive width for 4-button area: default 50%, below 1100px use 60% */
    /* Target the left column that contains the MANAGE button, then its sibling spacer */
    div[data-testid="column"]:has(button[key="btn_manage"]) {
        flex: 0 0 50% !important;
        max-width: 50% !important;
    }
    div[data-testid="column"]:has(button[key="btn_manage"]) + div[data-testid="column"] {
        flex: 0 0 50% !important;
        max-width: 50% !important;
    }
    @media (max-width: 1100px) {
        div[data-testid="column"]:has(button[key="btn_manage"]) {
            flex-basis: 60% !important;
            max-width: 60% !important;
        }
        div[data-testid="column"]:has(button[key="btn_manage"]) + div[data-testid="column"] {
            flex-basis: 40% !important;
            max-width: 40% !important;
        }
    }
        background: linear-gradient(to bottom, #262626, #1a1a1a) !important;
        border: 2px solid #ff8c00 !important;
        color: #ff8c00 !important;
        font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        border-radius: 0px !important;
        transition: all 0.2s !important;
        box-shadow: 0 0 10px rgba(255, 140, 0, 0.2) !important;
        min-width: 140px !important;
        white-space: nowrap !important;
    }
    
    .stDownloadButton > button:hover {
        background: #ff8c00 !important;
        color: #0d0d0d !important;
        box-shadow: 0 0 10px rgba(255, 140, 0, 0.2) !important;
        min-width: 120px !important;
    
    .stDownloadButton > button p {

    /* Responsive tweaks so buttons remain on one row without overlapping */
    @media (max-width: 1100px) {
        .stButton > button, .stDownloadButton > button, button[kind="primary"], button[kind="secondary"] {
            min-width: 110px !important;
            padding-left: 10px !important; padding-right: 10px !important;
            letter-spacing: 1px !important;
        }
    }
    @media (max-width: 880px) {
        .stButton > button, .stDownloadButton > button, button[kind="primary"], button[kind="secondary"] {
            min-width: 96px !important;
            font-size: 10px !important;
            letter-spacing: 1px !important;
            padding-left: 8px !important; padding-right: 8px !important;
        }
    }
        font-size: 11px !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Button layout area constrained to 50% width of the page
    group_col, spacer_col = st.columns([1, 1])
    with group_col:
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        with col_btn1:
            if st.button("⚙ MANAGE", use_container_width=True, key="btn_manage"):
                crud_dialog()
        with col_btn2:
            if st.button("⟳ REFRESH", use_container_width=True, key="btn_refresh"):
                st.session_state.pop('last_yf_fetch', None)
                st.session_state['force_recompute'] = True
                for key in list(st.session_state.keys()):
                    if key.startswith('processed_df_'):
                        del st.session_state[key]
                st.cache_data.clear()
                st.rerun()
        with col_btn3:
            if st.button("✕ CLEAR", use_container_width=True, key="btn_clear"):
                clear_filters()
                st.rerun()
        with col_btn4:
            # Read the existing data_saham.csv file and provide download
            import os
            csv_path = os.path.join(os.path.dirname(__file__), 'data_saham.csv')
            with open(csv_path, 'rb') as f:
                csv_data = f.read()
            
            st.download_button(
                label="⬇ DOWNLOAD",
                data=csv_data,
                file_name="data_saham.csv",
                mime="text/csv",
                key="btn_download",
                type="secondary",
                use_container_width=True
            )

    st.markdown('<div style="margin: 0;"></div>', unsafe_allow_html=True)

    # === FILTERS ===
    with st.expander("ADVANCED FILTERS", expanded=False):
        tab_presets, tab_filter, tab_method = st.tabs(["PRESETS", "FILTERS", "METHODOLOGY"])
        
        with tab_filter:
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_signals = st.multiselect(
                    "SIGNAL", SIGNAL_OPTIONS,
                    default=st.session_state.get('filter_signals', []),
                    key='filter_signals'
                )
                filter_sectors = st.multiselect(
                    "SECTOR", sorted(df_processed["Sector"].dropna().unique()),
                    default=st.session_state.get('filter_sectors', []),
                    key='filter_sectors'
                )
            
            with col2:
                # Static choices
                options_discount = [0, 10, 20, 30, 40, 50]
                options_yield = [0, 3, 5, 8, 10, 12, 15]
                # Determine default index based on session state
                try:
                    idx_disc = options_discount.index(int(st.session_state.get('filter_discount_min', 0)))
                except Exception:
                    idx_disc = 0
                try:
                    idx_yield = options_yield.index(int(float(st.session_state.get('filter_yield_min', 0))))
                except Exception:
                    idx_yield = 0
                filter_discount_min = st.selectbox(
                    "MIN DISCOUNT (%)",
                    options=options_discount,
                    index=idx_disc,
                    key='filter_discount_min'
                )
                filter_yield_min = st.selectbox(
                    "MIN YIELD (%)",
                    options=options_yield,
                    index=idx_yield,
                    key='filter_yield_min'
                )
            
            with col3:
                options_roe = [0, 5, 8, 10, 12, 15, 20]
                options_dpr = [50, 60, 70, 80, 90, 100, 200, 1000]
                try:
                    idx_roe = options_roe.index(int(float(st.session_state.get('filter_roe_min', 0))))
                except Exception:
                    idx_roe = 0
                try:
                    idx_dpr = options_dpr.index(int(st.session_state.get('filter_dpr_max', 1000)))
                except Exception:
                    idx_dpr = len(options_dpr) - 1
                filter_roe_min = st.selectbox(
                    "MIN ROE (%)",
                    options=options_roe,
                    index=idx_roe,
                    key='filter_roe_min'
                )
                filter_dpr_max = st.selectbox(
                    "MAX DPR (%)",
                    options=options_dpr,
                    index=idx_dpr,
                    key='filter_dpr_max'
                )
        
        with tab_presets:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 12px 16px; border-left: 3px solid #ff8c00; border-radius: 2px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #ff8c00; letter-spacing: 1.5px; font-family: IBM Plex Mono, monospace;">QUICK FILTER PRESETS</div>
                <div style="font-size: 9px; color: #808080; margin-top: 4px; font-family: IBM Plex Mono, monospace;">Apply predefined filter combinations for common screening strategies</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Define preset metadata
            presets_meta = {
                "High Yield": {
                    "icon": "💰",
                    "color": "#00ff41",
                    "desc": "Focus on high yields",
                    "criteria": "Yield ≥ 8%"
                },
                "Value Play": {
                    "icon": "📊",
                    "color": "#ffd700",
                    "desc": "Undervalued quality",
                    "criteria": "Discount ≥ 20% · ROE ≥ 10%"
                },
                "Growth Dividend": {
                    "icon": "🚀",
                    "color": "#90ee90",
                    "desc": "Strong ROE growth",
                    "criteria": "ROE ≥ 15% · Yield ≥ 5%"
                },
                "Safe Income": {
                    "icon": "🛡️",
                    "color": "#87ceeb",
                    "desc": "Conservative plays",
                    "criteria": "ROE ≥ 10% · Yield ≥ 5%"
                }
            }
            
            # Preset cards - HTML cards dengan button apply
            preset_cols = st.columns(4)
            
            for idx, (preset_name, preset_config) in enumerate(FILTER_PRESETS.items()):
                with preset_cols[idx]:
                    meta = presets_meta.get(preset_name, {})
                    
                    # Determine border color based on preset
                    border_colors = {
                        "High Yield": "#00ff41",
                        "Value Play": "#ff8c00", 
                        "Growth Dividend": "#00d4ff",
                        "Safe Income": "#9d4edd"
                    }
                    border_color = border_colors.get(preset_name, "#ff8c00")
                    
                    # Create card HTML
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); 
                                border: 1px solid #262626; 
                                border-left: 4px solid {border_color};
                                border-radius: 4px; 
                                padding: 20px 16px; 
                                min-height: 140px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                                margin-bottom: 8px;
                                text-align: center;
                                font-family: 'IBM Plex Mono', monospace;">
                        <div style="font-size: 32px; margin-bottom: 8px;">{meta.get('icon', '⭐')}</div>
                        <div style="font-size: 13px; font-weight: 700; color: {border_color}; 
                                    letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase;">
                            {preset_name}
                        </div>
                        <div style="font-size: 9px; color: #aaa; margin-bottom: 6px; font-style: italic;">
                            {meta.get('desc', '')}
                        </div>
                        <div style="font-size: 8px; color: #808080; line-height: 1.4;">
                            {meta.get('criteria', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Apply button below the card
                    if st.button(
                        f"APPLY {preset_name.upper()}",
                        key=f"preset_{preset_name}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        apply_preset(preset_name)
                        st.rerun()
        
        with tab_method:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #00ff41; margin-bottom: 10px;">
                    <div style="color: #00ff41; font-size: 11px; font-weight: 700; margin-bottom: 8px;">STRONG BUY</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Discount ≥ 25% · ROE ≥ 15% · Yield ≥ 8%
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #90ee90; margin-bottom: 10px;">
                    <div style="color: #90ee90; font-size: 11px; font-weight: 700; margin-bottom: 8px;">BUY</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Discount ≥ 15% · ROE ≥ 10% · Yield ≥ 8%
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #ffd700; margin-bottom: 10px;">
                    <div style="color: #ffd700; font-size: 11px; font-weight: 700; margin-bottom: 8px;">ACCUMULATE</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Discount ≥ 5% · ROE ≥ 8% · Yield ≥ 8%<br>
                        <span style="color: #808080; font-size: 9px;">Exception: High yield (≥10%) + discount (≥20%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #ff8c00; margin-bottom: 10px;">
                    <div style="color: #ff8c00; font-size: 11px; font-weight: 700; margin-bottom: 8px;">WAIT</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Below minimum thresholds
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #ff3333; margin-bottom: 10px;">
                    <div style="color: #ff3333; font-size: 11px; font-weight: 700; margin-bottom: 8px;">WAIT FOR DIP</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Overvalued (discount &lt; 0)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #1a1a1a; padding: 12px; border-left: 3px solid #666; margin-bottom: 10px;">
                    <div style="color: #ff8c00; font-size: 11px; font-weight: 700; margin-bottom: 8px;">VALUATION</div>
                    <div style="font-size: 10px; color: #ccc; line-height: 1.6;">
                        Fair Value = √(22.5 × BVPS × EPS)<br>
                        <span style="color: #808080; font-size: 9px;">Graham Number formula</span><br><br>
                        <span style="color: #00ff41; font-size: 9px;">⚙️ MANUAL OVERRIDE:</span><br>
                        <span style="color: #808080; font-size: 9px;">Stocks with ⚙️ icon use custom fair value set via MANAGE dialog</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Apply filters
    filters = {
        'signals': st.session_state.get('filter_signals', []),
        'sectors': st.session_state.get('filter_sectors', []),
        'discount_min': st.session_state.get('filter_discount_min', 0),
        'yield_min': st.session_state.get('filter_yield_min', 0),
        'roe_min': st.session_state.get('filter_roe_min', 0),
        'dpr_max': st.session_state.get('filter_dpr_max', 100)
    }
    df_filtered = apply_filters(df_processed, filters)
    
    # Sort by Ticker ascending (A-Z)
    df_filtered = df_filtered.sort_values('Ticker', ascending=True).reset_index(drop=True)

    # === MAIN DATA TABLE ===
    st.caption(f"Showing {len(df_filtered)} of {len(df_processed)} stocks · ⚙️ = Manual Fair Value")

    if not df_filtered.empty:
        # Two column layout: Table + Preview
        col_table, col_preview = st.columns([3, 1])
        
        with col_table:
            # Prepare display dataframe (hide DivTTM and LastUpdated)
            display_cols = ["Ticker", "Sector", "CurrentPrice", "FairValue", "Discount", 
                           "DivYield", "DPR", "ROE", "Signal"]
            df_display = df_filtered[display_cols].copy()
            
            # Add manual FV indicator to ticker
            if 'UsesManualFV' in df_filtered.columns:
                df_display['Ticker'] = df_filtered.apply(
                    lambda row: f"⚙️ {row['Ticker']}" if row.get('UsesManualFV', False) else row['Ticker'],
                    axis=1
                )
            
            # Rename columns
            df_display.columns = [DISPLAY_NAMES.get(c, c) for c in df_display.columns]
            
            # Style dataframe
            def style_row(row):
                styles = ['' for _ in row]
                signal_idx = list(df_display.columns).index('SIGNAL') if 'SIGNAL' in df_display.columns else -1
                if signal_idx >= 0:
                    styles[signal_idx] = style_signal(row.iloc[signal_idx])
                
                # Color code numeric columns
                if 'DIV YIELD' in df_display.columns:
                    yield_idx = list(df_display.columns).index('DIV YIELD')
                    styles[yield_idx] = get_yield_color(row.iloc[yield_idx])
                
                if 'DISCOUNT' in df_display.columns:
                    disc_idx = list(df_display.columns).index('DISCOUNT')
                    styles[disc_idx] = get_discount_color(row.iloc[disc_idx])
                
                if 'ROE' in df_display.columns:
                    roe_idx = list(df_display.columns).index('ROE')
                    styles[roe_idx] = get_roe_color(row.iloc[roe_idx])
                
                if 'DPR' in df_display.columns:
                    dpr_idx = list(df_display.columns).index('DPR')
                    styles[dpr_idx] = get_dpr_color(row.iloc[dpr_idx])
                
                return styles
            
            styled_df = df_display.style.apply(style_row, axis=1)
            
            # Format columns
            format_dict = {}
            for col in df_display.columns:
                if col in FORMATTERS:
                    format_dict[col] = FORMATTERS[col]
            
            if format_dict:
                styled_df = styled_df.format(format_dict)
            
            # Display with click handling - fixed height to prevent double render
            event = st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                height=700,
                key="stock_table"
            )
            
            # Handle row click
            if event.selection and event.selection.get('rows'):
                selected_idx = event.selection['rows'][0]
                selected_ticker = df_filtered.iloc[selected_idx]["Ticker"]
                st.session_state.selected_ticker = selected_ticker
        
        with col_preview:
            # Auto-select first stock if not in session_state
            if not df_filtered.empty:
                if 'selected_ticker' not in st.session_state or st.session_state.selected_ticker not in df_filtered["Ticker"].values:
                    st.session_state.selected_ticker = df_filtered.iloc[0]["Ticker"]
                
                ticker = st.session_state.selected_ticker
                preview_stock = df_filtered[df_filtered['Ticker'] == ticker]
                
                # Check if ticker exists in filtered data
                if preview_stock.empty:
                    st.warning("⚠️ Selected stock not in filtered results")
                else:
                    preview_stock = preview_stock.iloc[0]
                    
                    # Display selected ticker header
                    st.markdown(f"""
<div style='background: linear-gradient(to right, #1a1a1a, #262626); padding: 12px 16px; border-left: 3px solid #ff8c00; margin-bottom: 8px; font-family: IBM Plex Mono, monospace;'>
    <div style='font-size: 8px; color: #808080; letter-spacing: 1.5px; margin-bottom: 4px;'>SELECTED STOCK</div>
    <div style='font-size: 20px; font-weight: 700; color: #ff8c00; letter-spacing: 1px;'>{ticker}</div>
</div>
""", unsafe_allow_html=True)
                    
                    # Get data from CSV (table)
                    div_yield = preview_stock.get('DivYield', 0)
                    discount = preview_stock.get('Discount', 0)
                    fair_value = preview_stock.get('FairValue', 0)
                    signal = preview_stock.get('Signal', 'WAIT')
                    uses_manual_fv = preview_stock.get('UsesManualFV', False)
                    
                    # Discount color
                    discount_color = "#00ff41" if discount >= 0.25 else "#90ee90" if discount >= 0.15 else "#ffd700" if discount >= 0 else "#ff3333"
                    
                    # Fair value label with indicator
                    fv_label = "FAIR VALUE ⚙️" if uses_manual_fv else "FAIR VALUE"
                    fv_tooltip = "Manual Override" if uses_manual_fv else "Graham Number"
                    
                    # Signal color
                    signal_color_map = {
                        'STRONG BUY': '#00ff41',
                        'BUY': '#90ee90',
                        'ACCUMULATE': '#ffd700',
                        'WAIT': '#ff8c00',
                        'WAIT FOR DIP': '#ff3333'
                    }
                    signal_color = signal_color_map.get(signal, '#808080')
                    
                    # Get data from yfinance with proper error handling
                    # Skip if calendar filter changed (to avoid unnecessary fetches)
                    calendar_filter_changed = ('calendar_filter' in st.session_state and 
                                             st.session_state.get('_last_calendar_filter') != st.session_state.get('calendar_filter'))
                    
                    if calendar_filter_changed:
                        st.session_state['_last_calendar_filter'] = st.session_state.get('calendar_filter')
                        # Use cached data from CSV without fetching yfinance
                        current_price = preview_stock.get('CurrentPrice', 0)
                        price_change = 0
                        price_change_pct = 0
                        change_color = "#808080"
                        company_name = preview_stock.get('CompanyName', ticker)
                        sector = preview_stock.get('Sector', 'N/A')
                        industry = preview_stock.get('SubSector', 'N/A')
                        
                        # Try to get from session state cache if available
                        cache_key = f'yf_cache_{ticker}'
                        if cache_key in st.session_state:
                            cached_info = st.session_state[cache_key]
                            market_cap = cached_info.get('marketCap', 0)
                            beta = cached_info.get('beta', 0)
                            # Use cached sector/industry if available
                            if cached_info.get('sector'):
                                sector = cached_info.get('sector')
                            if cached_info.get('industry'):
                                industry = cached_info.get('industry')
                            if market_cap >= 1e12:
                                cap_str = f"{market_cap/1e12:.2f}T"
                            elif market_cap >= 1e9:
                                cap_str = f"{market_cap/1e9:.2f}B"
                            else:
                                cap_str = "N/A"
                            beta_display = f"{beta:.2f}" if beta else "N/A"
                        else:
                            # No cache available
                            market_cap = 0
                            cap_str = "N/A"
                            beta = 0
                            beta_display = "N/A"
                        
                        yield_color = "#00ff41" if div_yield >= 0.05 else "#90ee90" if div_yield >= 0.03 else "#ffd700" if div_yield >= 0.02 else "#ff8c00"
                    elif yf is not None:
                        try:
                            # Show loading state
                            preview_placeholder = st.empty()
                            with preview_placeholder:
                                st.info("⏳ Loading market data...")
                            
                            ticker_obj = yf.Ticker(ticker + EXCHANGE_SUFFIX)
                            info = ticker_obj.info
                            
                            # Clear loading state
                            preview_placeholder.empty()
                            
                            # Price data with fallbacks
                            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                            prev_close = info.get('previousClose', 0)
                            
                            # Calculate price change
                            price_change = current_price - prev_close if (current_price and prev_close) else 0
                            price_change_pct = (price_change / prev_close * 100) if prev_close else 0
                            change_color = "#00ff41" if price_change >= 0 else "#ff3333"
                            
                            # Div yield color
                            yield_color = "#00ff41" if div_yield >= 0.05 else "#90ee90" if div_yield >= 0.03 else "#ffd700" if div_yield >= 0.02 else "#ff8c00"
                            
                            # Company info from yfinance with fallbacks
                            company_name = info.get('shortName', info.get('longName', ticker))
                            sector = info.get('sector', 'N/A')
                            industry = info.get('industry', 'N/A')
                            market_cap = info.get('marketCap', 0)
                            beta = info.get('beta', 0)
                            
                            # Format market cap
                            if market_cap >= 1e12:
                                cap_str = f"{market_cap/1e12:.2f}T"
                            elif market_cap >= 1e9:
                                cap_str = f"{market_cap/1e9:.2f}B"
                            else:
                                cap_str = "N/A"
                            
                            beta_display = f"{beta:.2f}" if beta else "N/A"
                            
                            # Cache the yfinance data for later use
                            st.session_state[f'yf_cache_{ticker}'] = {
                                'marketCap': market_cap,
                                'beta': beta,
                                'sector': sector,
                                'industry': industry,
                                'companyName': company_name
                            }
                            
                        except Exception as e:
                            st.error(f"⚠️ Failed to load market data: {str(e)[:100]}")
                            # Use fallback values
                            current_price = preview_stock.get('CurrentPrice', 0)
                            price_change = 0
                            price_change_pct = 0
                            change_color = "#808080"
                            company_name = preview_stock.get('CompanyName', ticker)
                            sector = preview_stock.get('Sector', 'N/A')
                            industry = preview_stock.get('SubSector', 'N/A')
                            cap_str = "N/A"
                            beta_display = "N/A"
                            yield_color = "#00ff41" if div_yield >= 0.05 else "#90ee90" if div_yield >= 0.03 else "#ffd700" if div_yield >= 0.02 else "#ff8c00"
                    else:
                        st.warning("⚠️ yfinance not available")
                        # Use fallback values
                        current_price = preview_stock.get('CurrentPrice', 0)
                        price_change = 0
                        price_change_pct = 0
                        change_color = "#808080"
                        company_name = preview_stock.get('CompanyName', ticker)
                        sector = preview_stock.get('Sector', 'N/A')
                        industry = preview_stock.get('SubSector', 'N/A')
                        cap_str = "N/A"
                        beta_display = "N/A"
                        yield_color = "#00ff41" if div_yield >= 0.05 else "#90ee90" if div_yield >= 0.03 else "#ffd700" if div_yield >= 0.02 else "#ff8c00"
                    
                    # Get dividend schedule data
                    interim = preview_stock.get('Interim', '-')
                    final = preview_stock.get('Final', '-')
                    
                    # Render preview card (always, regardless of data source)
                    st.markdown(f"""
<div style='background: #1a1a1a; padding: 16px; border-radius: 2px; border: 1px solid #333; font-family: IBM Plex Mono, monospace;'>
    <div style='margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #333;'>
        <div style='font-size: 10px; color: #808080; letter-spacing: 1px; margin-bottom: 6px;'>LAST PRICE</div>
        <div style='font-size: 32px; font-weight: 700; color: #f5f5f5; line-height: 1;'>{current_price:,.0f}</div>
        <div style='font-size: 12px; color: {change_color}; margin-top: 4px; font-weight: 600;'>
            {price_change:+,.0f} ({price_change_pct:+.2f}%)
        </div>
    </div>
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #333;'>
        <div>
            <div style='font-size: 9px; color: #808080; letter-spacing: 1px; margin-bottom: 4px;' title='{fv_tooltip}'>{fv_label}</div>
            <div style='font-size: 20px; font-weight: 700; color: #f5f5f5;'>{fair_value:,.0f}</div>
        </div>
        <div>
            <div style='font-size: 9px; color: #808080; letter-spacing: 1px; margin-bottom: 4px;'>DIV YIELD</div>
            <div style='font-size: 20px; font-weight: 700; color: {yield_color};'>{div_yield:.2%}</div>
        </div>
    </div>
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #333;'>
        <div>
            <div style='font-size: 9px; color: #808080; letter-spacing: 1px; margin-bottom: 4px;'>DISCOUNT</div>
            <div style='font-size: 20px; font-weight: 700; color: {discount_color};'>{discount:+.1%}</div>
        </div>
        <div>
            <div style='font-size: 9px; color: #808080; letter-spacing: 1px; margin-bottom: 4px;'>SIGNAL</div>
            <div style='font-size: 16px; font-weight: 700; color: {signal_color};'>{signal}</div>
        </div>
    </div>
    <div>
        <div style='font-size: 10px; color: #808080; letter-spacing: 1px; margin-bottom: 10px;'>COMPANY INFO</div>
        <div style='font-size: 11px; line-height: 1.8; color: #cccccc;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Name:</span>
                <span style='color: #f5f5f5; font-weight: 600; text-align: right; font-size: 10px;'>{company_name}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Sector:</span>
                <span style='color: #f5f5f5; font-weight: 600; text-align: right;'>{sector}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Sub-Sector:</span>
                <span style='color: #f5f5f5; font-weight: 600; text-align: right;'>{industry}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Market Cap:</span>
                <span style='color: #f5f5f5; font-weight: 600;'>{cap_str}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Beta (Volatility):</span>
                <span style='color: #f5f5f5; font-weight: 600;'>{beta_display}</span>
            </div>
        </div>
    </div>
    <div style='margin-top: 16px; padding-top: 16px; border-top: 1px solid #333;'>
        <div style='font-size: 10px; color: #808080; letter-spacing: 1px; margin-bottom: 10px;'>DIVIDEND SCHEDULE</div>
        <div style='font-size: 11px; line-height: 1.6; color: #cccccc;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: #808080;'>Interim:</span>
                <span style='color: #ff8c00; font-weight: 600; font-size: 10px;'>{interim}</span>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: #808080;'>Final:</span>
                <span style='color: #ff8c00; font-weight: 600; font-size: 10px;'>{final}</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
                    
                    # Restore normal button size for VIEW DETAILS
                    st.markdown("""
                    <style>
                    button[key="preview_details"] {
                        min-height: 38px !important;
                        height: 38px !important;
                        padding: 8px 16px !important;
                        font-size: 14px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📈 VIEW DETAILS", use_container_width=True, key="preview_details"):
                        # Get stock data from filtered dataframe
                        stock_data = df_filtered[df_filtered['Ticker'] == ticker].iloc[0].to_dict()
                        show_stock_details(ticker, stock_data)
            else:
                st.markdown("""
<div style='background: #1a1a1a; padding: 40px 20px; text-align: center; border-radius: 2px; height: 500px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #333;'>
    <div style='font-size: 48px; margin-bottom: 16px; opacity: 0.3;'>📊</div>
    <div style='font-size: 14px; color: #808080; text-transform: uppercase; letter-spacing: 2px; font-family: IBM Plex Mono, monospace;'>
        NO SELECTION
    </div>
    <div style='font-size: 11px; color: #808080; margin-top: 8px; font-family: IBM Plex Mono, monospace;'>
        Click on any row to view details
    </div>
</div>
""", unsafe_allow_html=True)
    
    else:
        st.info("🔍 No stocks match the filter criteria. Try adjusting your filters.")

    # === TABS FOR ANALYSIS WITH LAZY RENDERING ===
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 STATISTICS", "📅 DIVIDEND CALENDAR"])

    # Only render the active tab to improve performance
    with tab1:
        if not df_filtered.empty:
            render_statistics_and_charts(df_filtered)
        else:
            st.info("🔍 No data to display statistics")

    with tab2:
        if not df_filtered.empty:
            render_dividend_calendar(df_filtered)
        else:
            st.info("🔍 No data to display calendar")


@st.cache_data(show_spinner=False, ttl=60)
def compute_monthly_summary(df: pd.DataFrame) -> list:
    """Cached computation of monthly dividend summary."""
    monthly_summary = []
    for month in MONTH_OPTIONS[1:]:
        interim_stocks = df[df["Interim"] == month]
        final_stocks = df[df["Final"] == month]
        total_stocks = len(interim_stocks) + len(final_stocks)
        avg_yield = 0
        if total_stocks > 0:
            all_month_stocks = pd.concat([interim_stocks, final_stocks])
            avg_yield = all_month_stocks['DivYield'].mean() * 100
        monthly_summary.append({'month': month[:3], 'count': total_stocks, 'avg_yield': avg_yield})
    return monthly_summary


def render_dividend_calendar(df: pd.DataFrame):
    """Render dividend payment calendar with cash flow insights."""
    st.markdown("#### EXPECTED DIVIDEND PAYMENT SCHEDULE")
    st.caption("Based on historical patterns · Not guaranteed")
    
    # Use cached computation
    monthly_summary = compute_monthly_summary(df)
    
    # Sort by count and get top 3
    monthly_summary_sorted = sorted(monthly_summary, key=lambda x: x['count'], reverse=True)
    top_months = [m for m in monthly_summary_sorted if m['count'] > 0][:3]
    
    # Display summary bar with larger text
    if len(top_months) > 0:
        summary_html = '<div style="font-size: 11px; color: #808080; letter-spacing: 1px; font-weight: 600; margin-bottom: 12px; font-family: IBM Plex Mono, monospace;">TOP DIVIDEND MONTHS</div>'
        summary_html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px;">'
        for ms in top_months:
            summary_html += f'<div style="background: #1a1a1a; padding: 12px; border-radius: 3px; border-left: 3px solid #ff8c00;">'
            summary_html += f'<div style="font-size: 13px; color: #ff8c00; font-weight: 700; margin-bottom: 6px; text-transform: uppercase;">{ms["month"]}</div>'
            summary_html += f'<div style="font-size: 11px; color: #00ff41; font-weight: 600; margin-bottom: 3px;">{ms["count"]} stocks</div>'
            summary_html += f'<div style="font-size: 11px; color: #90ee90; font-weight: 600;">{ms["avg_yield"]:.1f}% avg yield</div>'
            summary_html += '</div>'
        summary_html += '</div>'
        st.markdown(summary_html, unsafe_allow_html=True)
    
    # Filter dropdown for ticker selection
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        all_tickers = sorted(df["Ticker"].unique().tolist())
        ticker_options = ["All Stocks"] + all_tickers
        show_ticker_filter = st.selectbox(
            "FILTER BY TICKER",
            options=ticker_options,
            key="calendar_filter"
        )
    
    # Signal legend removed - signals now displayed directly on each stock
    
    cols = st.columns(4)
    current_month = datetime.now().month
    
    for idx, month in enumerate(MONTH_OPTIONS[1:], 1):
        with cols[(idx-1) % 4]:
            interim_stocks = df[df["Interim"] == month]
            final_stocks = df[df["Final"] == month]
            
            # Apply ticker filter
            if show_ticker_filter != "All Stocks":
                interim_stocks = interim_stocks[interim_stocks["Ticker"] == show_ticker_filter]
                final_stocks = final_stocks[final_stocks["Ticker"] == show_ticker_filter]
            
            total_count = len(interim_stocks) + len(final_stocks)
            
            is_current = idx == current_month
            
            # Signal color mapping
            signal_colors = {
                'STRONG BUY': '#00ff41',
                'BUY': '#90ee90',
                'ACCUMULATE': '#ffd700',
                'WAIT': '#ff8c00',
                'WAIT FOR DIP': '#ff3333'
            }
            
            # Build stock items HTML with cleaner design
            stocks_html = ""
            for _, stock in interim_stocks.iterrows():
                ticker = stock['Ticker']
                signal = stock.get('Signal', 'N/A')
                signal_color = signal_colors.get(signal, '#808080')
                
                stocks_html += f'<div style="margin: 0 0 8px 0; padding: 12px; background: #1f1f1f; border-radius: 4px; border-left: 3px solid {signal_color};">'
                stocks_html += f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
                stocks_html += f'<span style="font-size: 13px; font-weight: 700; color: #fff; letter-spacing: 0.5px;">{ticker}</span>'
                stocks_html += f'<span style="font-size: 8px; color: #aaa; background: #141414; padding: 3px 8px; border-radius: 3px; font-weight: 600; letter-spacing: 0.5px;">INTERIM</span>'
                stocks_html += '</div>'
                stocks_html += f'<div style="font-size: 9px; color: {signal_color}; font-weight: 600; letter-spacing: 0.5px;">{signal}</div>'
                stocks_html += '</div>'
            
            for _, stock in final_stocks.iterrows():
                ticker = stock['Ticker']
                signal = stock.get('Signal', 'N/A')
                signal_color = signal_colors.get(signal, '#808080')
                
                stocks_html += f'<div style="margin: 0 0 8px 0; padding: 12px; background: #1f1f1f; border-radius: 4px; border-left: 3px solid {signal_color};">'
                stocks_html += f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
                stocks_html += f'<span style="font-size: 13px; font-weight: 700; color: #fff; letter-spacing: 0.5px;">{ticker}</span>'
                stocks_html += f'<span style="font-size: 8px; color: #aaa; background: #141414; padding: 3px 8px; border-radius: 3px; font-weight: 600; letter-spacing: 0.5px;">FINAL</span>'
                stocks_html += '</div>'
                stocks_html += f'<div style="font-size: 9px; color: {signal_color}; font-weight: 600; letter-spacing: 0.5px;">{signal}</div>'
                stocks_html += '</div>'
            
            if total_count == 0:
                stocks_html = '<div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #666; font-size: 11px; letter-spacing: 1px; font-weight: 600;">NO DIVIDENDS</div>'
            
            # Card design
            month_name = month[:3].upper()
            card_bg = "#1a1a1a" if is_current else "#141414"
            card_border = "1px solid #ff8c00" if is_current else "1px solid #262626"
            header_bg = "linear-gradient(135deg, #ff8c00 0%, #ff6600 100%)" if is_current else "#1f1f1f"
            month_color = "#000" if is_current else "#ff8c00"
            count_bg = "#000" if is_current else "#ff8c00"
            count_color = "#ff8c00" if is_current else "#000"
            box_shadow = "0 4px 16px rgba(255,140,0,0.3)" if is_current else "0 2px 8px rgba(0,0,0,0.5)"
            
            month_html = f'<div style="background: {card_bg}; border: {card_border}; border-radius: 6px; margin-bottom: 16px; font-family: IBM Plex Mono, monospace; overflow: hidden; box-shadow: {box_shadow}; height: 400px; display: flex; flex-direction: column;">'
            month_html += f'<div style="padding: 14px 16px; background: {header_bg}; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">'
            month_html += f'<span style="font-size: 14px; font-weight: 700; color: {month_color}; letter-spacing: 1.5px;">{month_name}</span>'
            month_html += f'<span style="font-size: 11px; font-weight: 700; color: {count_color}; background: {count_bg}; padding: 4px 10px; border-radius: 4px; min-width: 30px; text-align: center;">{total_count}</span>'
            month_html += '</div>'
            month_html += f'<div style="padding: 12px; overflow-y: auto; flex: 1; scrollbar-width: thin; scrollbar-color: #333 transparent;">{stocks_html}</div>'
            month_html += '</div>'
            st.markdown(month_html, unsafe_allow_html=True)


def render_statistics_and_charts(df: pd.DataFrame):
    """Render combined statistics and charts with Bloomberg terminal styling."""
    if df.empty:
        st.info("No data to display")
        return
    
    # Add header with stats summary
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 12px 16px; border-left: 3px solid #ff8c00; border-radius: 2px; margin-bottom: 20px;">
        <div style="font-size: 11px; font-weight: 700; color: #ff8c00; letter-spacing: 1.5px; font-family: IBM Plex Mono, monospace;">PORTFOLIO STATISTICS</div>
        <div style="font-size: 9px; color: #808080; margin-top: 4px; font-family: IBM Plex Mono, monospace;">Comprehensive visual analysis of filtered stocks</div>
    </div>
    """, unsafe_allow_html=True)
    
    # === ROW 1: Sector Breakdown (Pie) + Sector Distribution (Bar) ===
    st.markdown("### 📊 SECTOR ANALYSIS")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SECTOR BREAKDOWN")
        sector_counts = df["Sector"].value_counts()
        fig_sector_pie = px.pie(
            values=sector_counts.values,
            names=sector_counts.index,
            color_discrete_sequence=px.colors.sequential.Oranges_r,
            hole=0.5
        )
        fig_sector_pie.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='IBM Plex Mono', size=10, color='#ccc'),
            height=320,
            showlegend=True,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="v", 
                yanchor="middle", 
                y=0.5, 
                xanchor="left", 
                x=1.02,
                font=dict(size=9)
            )
        )
        fig_sector_pie.update_traces(
            textposition='inside',
            textinfo='percent',
            textfont_size=9,
            marker=dict(line=dict(color='#000000', width=2))
        )
        st.plotly_chart(fig_sector_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### SECTOR DISTRIBUTION")
        sector_data = df.groupby('Sector').size().reset_index(name='count')
        sector_data = sector_data.sort_values('count', ascending=False)
        
        fig_sector_bar = px.bar(
            sector_data,
            x='Sector',
            y='count',
            color='count',
            color_continuous_scale='oranges'
        )
        fig_sector_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,1)',
            font=dict(family='IBM Plex Mono', size=9, color='#ccc'),
            height=320,
            margin=dict(l=50, r=20, t=20, b=100),
            xaxis=dict(
                tickangle=-45,
                gridcolor='#262626'
            ),
            yaxis=dict(
                title='Stock Count',
                gridcolor='#262626',
                showgrid=True
            ),
            showlegend=False
        )
        st.plotly_chart(fig_sector_bar, use_container_width=True)
    
    # === ROW 2: Top 10 by Yield + Top 10 by Discount ===
    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("### 🏆 TOP OPPORTUNITIES")
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### TOP 10 BY YIELD")
        st.caption("Highest income generation potential")
        top_yield = df.nlargest(10, 'DivYield')[['Ticker', 'DivYield', 'Signal', 'ROE']].copy()
        top_yield['DivYield'] = top_yield['DivYield'] * 100
        
        fig_top_yield = px.bar(
            top_yield,
            x='Ticker',
            y='DivYield',
            color='Signal',
            color_discrete_map={
                'STRONG BUY': '#00ff41',
                'BUY': '#90ee90',
                'ACCUMULATE': '#ffd700',
                'WAIT': '#ff8c00',
                'WAIT FOR DIP': '#ff3333'
            },
            hover_data={'ROE': ':.1f'}
        )
        fig_top_yield.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,1)',
            font=dict(family='IBM Plex Mono', size=9, color='#ccc'),
            height=320,
            margin=dict(l=50, r=20, t=20, b=50),
            xaxis=dict(
                title='',
                showgrid=False
            ),
            yaxis=dict(
                title='YIELD (%)',
                gridcolor='#262626',
                showgrid=True
            ),
            showlegend=False
        )
        fig_top_yield.update_traces(marker_line_color='#000', marker_line_width=1)
        st.plotly_chart(fig_top_yield, use_container_width=True)
    
    with col4:
        st.markdown("#### TOP 10 BY DISCOUNT")
        st.caption("Best value opportunities vs fair value")
        top_discount = df.nlargest(10, 'Discount')[['Ticker', 'Discount', 'Signal', 'DivYield']].copy()
        top_discount['Discount'] = top_discount['Discount'] * 100
        
        fig_top_disc = px.bar(
            top_discount,
            x='Ticker',
            y='Discount',
            color='Signal',
            color_discrete_map={
                'STRONG BUY': '#00ff41',
                'BUY': '#90ee90',
                'ACCUMULATE': '#ffd700',
                'WAIT': '#ff8c00',
                'WAIT FOR DIP': '#ff3333'
            },
            hover_data={'DivYield': ':.2%'}
        )
        fig_top_disc.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,1)',
            font=dict(family='IBM Plex Mono', size=9, color='#ccc'),
            height=320,
            margin=dict(l=50, r=20, t=20, b=50),
            xaxis=dict(
                title='',
                showgrid=False
            ),
            yaxis=dict(
                title='DISCOUNT (%)',
                gridcolor='#262626',
                showgrid=True
            ),
            showlegend=False
        )
        fig_top_disc.update_traces(marker_line_color='#000', marker_line_width=1)
        st.plotly_chart(fig_top_disc, use_container_width=True)
    
    # === ROW 3: Best Value Combo + Yield Sustainability ===
    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("### 💎 VALUE ANALYSIS")
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### BEST VALUE COMBO")
        st.caption("High yield + Undervalued + Quality (ROE ≥ 10%)")
        best_value = df[(df['DivYield'] >= 0.06) & (df['Discount'] >= 0.10) & (df['ROE'] >= 10)].nlargest(8, 'DivYield')[['Ticker', 'DivYield', 'Discount', 'ROE', 'Signal']].copy()
        
        if len(best_value) > 0:
            best_value['Size'] = best_value['DivYield'] * 100
            fig_value = px.scatter(
                best_value,
                x='Discount',
                y='ROE',
                size='Size',
                color='Signal',
                text='Ticker',
                color_discrete_map={
                    'STRONG BUY': '#00ff41',
                    'BUY': '#90ee90',
                    'ACCUMULATE': '#ffd700',
                    'WAIT': '#ff8c00',
                    'WAIT FOR DIP': '#ff3333'
                }
            )
            fig_value.update_traces(
                textposition='top center',
                marker=dict(line=dict(width=2, color='#000'))
            )
            fig_value.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10,10,10,1)',
                font=dict(family='IBM Plex Mono', size=9, color='#ccc'),
                height=320,
                margin=dict(l=50, r=20, t=20, b=50),
                xaxis=dict(
                    title='Discount',
                    tickformat='.0%',
                    gridcolor='#262626'
                ),
                yaxis=dict(
                    title='ROE (%)',
                    gridcolor='#262626'
                ),
                showlegend=False
            )
            st.plotly_chart(fig_value, use_container_width=True)
        else:
            st.info("No stocks match criteria. Try adjusting filters.")
    
    with col6:
        st.markdown("#### YIELD SUSTAINABILITY")
        st.caption("DPR analysis · Lower is more sustainable")
        sustainable = df[df['DivYield'] >= 0.05].nlargest(10, 'DivYield')[['Ticker', 'DivYield', 'DPR', 'Signal']].copy()
        
        if len(sustainable) > 0:
            sustainable['DivYield'] = sustainable['DivYield'] * 100
            
            fig_sustain = go.Figure()
            fig_sustain.add_trace(go.Bar(
                name='Div Yield',
                x=sustainable['Ticker'],
                y=sustainable['DivYield'],
                marker_color='#00ff41',
                marker_line_color='#000',
                marker_line_width=1,
                yaxis='y',
                offsetgroup=1
            ))
            fig_sustain.add_trace(go.Bar(
                name='DPR',
                x=sustainable['Ticker'],
                y=sustainable['DPR'],
                marker_color='#ff8c00',
                marker_line_color='#000',
                marker_line_width=1,
                yaxis='y2',
                offsetgroup=2
            ))
            
            fig_sustain.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10,10,10,1)',
                font=dict(family='IBM Plex Mono', size=9, color='#ccc'),
                height=320,
                margin=dict(l=50, r=50, t=20, b=50),
                xaxis=dict(
                    title='',
                    showgrid=False
                ),
                yaxis=dict(
                    title='Yield (%)',
                    gridcolor='#262626',
                    showgrid=True,
                    side='left'
                ),
                yaxis2=dict(
                    title='DPR (%)',
                    overlaying='y',
                    side='right',
                    gridcolor='#1a1a1a',
                    showgrid=False
                ),
                barmode='group',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=8)
                )
            )
            st.plotly_chart(fig_sustain, use_container_width=True)
        else:
            st.info("No high-yield stocks (≥5%) available.")
    
    # === KEY METRICS at the bottom ===
    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("### 📈 KEY METRICS")
    
    buy_signals = df[df['Signal'].isin(['STRONG BUY', 'BUY'])]
    high_yield_stocks = df[df['DivYield'] >= 0.08]
    undervalued_stocks = df[df['Discount'] >= 0.15]
    quality_stocks = df[df['ROE'] >= 15]
    
    stats_html = f"""
    <div style="background: #0f0f0f; border: 1px solid #262626; border-radius: 4px; padding: 16px; font-family: IBM Plex Mono, monospace;">
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #ff8c00; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">TOTAL STOCKS</div>
                <div style="font-size: 20px; font-weight: 700; color: #ff8c00;">{len(df)}</div>
            </div>
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #00ff41; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">BUY SIGNALS</div>
                <div style="font-size: 20px; font-weight: 700; color: #00ff41;">{len(buy_signals)}</div>
                <div style="font-size: 8px; color: #666; margin-top: 2px;">Strong Buy + Buy</div>
            </div>
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #90ee90; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">HIGH YIELD</div>
                <div style="font-size: 20px; font-weight: 700; color: #90ee90;">{len(high_yield_stocks)}</div>
                <div style="font-size: 8px; color: #666; margin-top: 2px;">Yield ≥ 8%</div>
            </div>
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #ffd700; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">UNDERVALUED</div>
                <div style="font-size: 20px; font-weight: 700; color: #ffd700;">{len(undervalued_stocks)}</div>
                <div style="font-size: 8px; color: #666; margin-top: 2px;">Discount ≥ 15%</div>
            </div>
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #4a90e2; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">QUALITY</div>
                <div style="font-size: 20px; font-weight: 700; color: #4a90e2;">{len(quality_stocks)}</div>
                <div style="font-size: 8px; color: #666; margin-top: 2px;">ROE ≥ 15%</div>
            </div>
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 10px 12px; border-left: 2px solid #ff8c00; border-radius: 2px;">
                <div style="font-size: 9px; color: #808080; margin-bottom: 4px; letter-spacing: 0.5px;">AVG DISCOUNT</div>
                <div style="font-size: 20px; font-weight: 700; color: #ff8c00;">{df['Discount'].mean() * 100:+.1f}%</div>
                <div style="font-size: 8px; color: #666; margin-top: 2px;">Portfolio avg</div>
            </div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)


def render_statistics(df: pd.DataFrame):
    """Render statistical analysis with Bloomberg terminal styling."""
    if df.empty:
        st.info("No data to display")
        return
    
    # Add header with stats summary
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 12px 16px; border-left: 3px solid #ff8c00; border-radius: 2px; margin-bottom: 20px;">
        <div style="font-size: 11px; font-weight: 700; color: #ff8c00; letter-spacing: 1.5px; font-family: IBM Plex Mono, monospace;">PORTFOLIO STATISTICS</div>
        <div style="font-size: 9px; color: #808080; margin-top: 4px; font-family: IBM Plex Mono, monospace;">Aggregate analysis of filtered stocks</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------
# ---- RUN APPLICATION ------
# --------------------------
if __name__ == "__main__":
    main()
