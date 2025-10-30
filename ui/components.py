"""Reusable UI components for metric display."""

import streamlit as st
import pandas as pd


def display_metric_cards(df: pd.DataFrame):
    """
    Display Bloomberg-style metric cards showing portfolio summary.
    
    Args:
        df: Processed dataframe with stock data
    """
    # Calculate metrics
    total_stocks = len(df)
    avg_yield = df["DivYield"].mean() * 100 if not df.empty else 0
    avg_roe = df["ROE"].mean() if not df.empty else 0  # ROE already stored as percentage
    avg_discount = df["Discount"].mean() * 100 if not df.empty else 0
    
    # Count signals
    strong_buy = len(df[df["Signal"] == "STRONG BUY"])
    buy = len(df[df["Signal"] == "BUY"])
    accumulate = len(df[df["Signal"] == "ACCUMULATE"])
    
    # Determine status classes
    yield_status = "status-strong" if avg_yield >= 5 else "status-moderate" if avg_yield >= 3 else "status-weak"
    yield_text = "STRONG" if avg_yield >= 5 else "GOOD" if avg_yield >= 3 else "LOW"
    
    roe_status = "status-strong" if avg_roe >= 15 else "status-moderate" if avg_roe >= 10 else "status-weak"
    roe_text = "EXCELLENT" if avg_roe >= 15 else "GOOD" if avg_roe >= 10 else "WEAK"
    
    discount_status = "status-strong" if avg_discount >= 15 else "status-moderate" if avg_discount >= 0 else "status-weak"
    discount_text = "UNDERVALUED" if avg_discount >= 15 else "FAIR" if avg_discount >= 0 else "OVERVALUED"
    
    # Render cards
    st.markdown(f"""
<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; margin-bottom: 20px;'>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>UNIVERSE</div>
        <div class='bbg-value' style='font-size: 28px; margin: 8px 0;'>{total_stocks}</div>
        <div style='font-size: 9px; color: #666; letter-spacing: 1px;'>STOCKS</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>AVG YIELD</div>
        <div class='bbg-value' style='font-size: 26px; margin: 8px 0; color: #ff8c00;'>{avg_yield:.2f}%</div>
        <div class='bbg-status {yield_status}' style='font-size: 8px; padding: 3px 8px; border-radius: 2px;'>{yield_text}</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>AVG ROE</div>
        <div class='bbg-value' style='font-size: 26px; margin: 8px 0; color: #ff8c00;'>{avg_roe:.1f}%</div>
        <div class='bbg-status {roe_status}' style='font-size: 8px; padding: 3px 8px; border-radius: 2px;'>{roe_text}</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>AVG DISCOUNT</div>
        <div class='bbg-value' style='font-size: 26px; margin: 8px 0; color: #ff8c00;'>{avg_discount:+.1f}%</div>
        <div class='bbg-status {discount_status}' style='font-size: 8px; padding: 3px 8px; border-radius: 2px;'>{discount_text}</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; border-left: 3px solid #00ff41; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>STRONG BUY</div>
        <div class='bbg-value' style='color: #00ff41; font-size: 28px; margin: 8px 0; font-weight: 700;'>{strong_buy}</div>
        <div style='font-size: 9px; color: #00ff41; opacity: 0.6; letter-spacing: 1px;'>SIGNALS</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; border-left: 3px solid #90ee90; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>BUY</div>
        <div class='bbg-value' style='color: #90ee90; font-size: 28px; margin: 8px 0; font-weight: 700;'>{buy}</div>
        <div style='font-size: 9px; color: #90ee90; opacity: 0.6; letter-spacing: 1px;'>SIGNALS</div>
    </div>
    <div class='bbg-box' style='background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); border: 1px solid #262626; border-left: 3px solid #ffd700; box-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
        <div class='bbg-label' style='font-size: 9px; letter-spacing: 1.5px;'>ACCUMULATE</div>
        <div class='bbg-value' style='color: #ffd700; font-size: 28px; margin: 8px 0; font-weight: 700;'>{accumulate}</div>
        <div style='font-size: 9px; color: #ffd700; opacity: 0.6; letter-spacing: 1px;'>SIGNALS</div>
    </div>
</div>
""", unsafe_allow_html=True)


def display_summary_stats(df: pd.DataFrame):
    """
    Display summary statistics in tabular format.
    
    Args:
        df: Processed dataframe with stock data
    """
    if df.empty:
        st.info("No data to display")
        return
    
    stats = {
        "Metric": ["Stocks", "Avg Yield", "Avg ROE", "Avg DPR", "Avg Discount", "Max Yield", "Min Yield"],
        "Value": [
            len(df),
            f"{df['DivYield'].mean() * 100:.2f}%",
            f"{df['ROE'].mean() * 100:.2f}%",
            f"{df['DPR'].mean() * 100:.2f}%",
            f"{df['Discount'].mean() * 100:+.2f}%",
            f"{df['DivYield'].max() * 100:.2f}%",
            f"{df['DivYield'].min() * 100:.2f}%"
        ]
    }
    
    stats_df = pd.DataFrame(stats)
    st.table(stats_df)
