"""Stock detail dialog - Bloomberg terminal style analysis."""

import logging
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

try:
    import yfinance as yf
except ImportError:
    yf = None

from config import EXCHANGE_SUFFIX


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_yf_details(ticker: str):
    """
    Fetch detailed stock data from Yahoo Finance with proper error handling.
    
    Returns:
        tuple: (info dict, historical DataFrame, dividends Series)
    """
    try:
        ticker_obj = yf.Ticker(ticker + EXCHANGE_SUFFIX)
        
        # Fetch info with timeout handling
        try:
            info = ticker_obj.info
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            st.warning(f"⚠️ Network issue fetching company info for {ticker}")
            info = {}
        
        # Fetch historical data
        try:
            hist = ticker_obj.history(period="1y")
        except Exception as e:
            logging.warning(f"Historical data fetch failed for {ticker}: {e}")
            hist = pd.DataFrame()
        
        # Fetch dividends
        try:
            divs = ticker_obj.dividends
        except Exception as e:
            logging.warning(f"Dividend data fetch failed for {ticker}: {e}")
            divs = pd.Series()
        
        return info, hist, divs
    except Exception as e:
        logging.exception(f"Error fetching details for {ticker}")
        raise


@st.dialog("EQUITY ANALYSIS", width="large")
def show_stock_details(ticker: str, stock_data: dict = None):
    """
    Display comprehensive stock analysis dialog with price, dividends, and financials.
    
    Args:
        ticker: Stock ticker symbol (without exchange suffix)
        stock_data: Dictionary containing stock data from CSV table
    """
    if yf is None:
        st.error("❌ yfinance library not installed")
        return
    
    try:
        with st.spinner("LOADING..."):
            info, hist, divs = fetch_yf_details(ticker)
        
        # Validate that we got some data
        if not info:
            st.error(f"❌ Unable to fetch data for {ticker}. Please check the ticker symbol or try again later.")
            return
        
        # === HEADER WITH ENHANCED VISIBILITY ===
        company = info.get('longName', info.get('shortName', ticker))
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        
        st.markdown(f"""
<div style='background: linear-gradient(135deg, #0a0a0a 0%, #1a1000 100%); padding: 18px 20px; margin-bottom: 12px; border-left: 4px solid #ff8c00; border-radius: 4px; box-shadow: 0 4px 12px rgba(255,140,0,0.15); font-family: IBM Plex Mono, monospace;'>
    <div style='font-size: 24px; font-weight: 700; letter-spacing: 2px; color: #ff8c00; font-family: IBM Plex Mono, monospace;'>{ticker}</div>
    <div style='font-size: 14px; color: #e0e0e0; margin-top: 6px; font-weight: 500; font-family: IBM Plex Mono, monospace;'>{company}</div>
    <div style='font-size: 11px; color: #999; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; font-family: IBM Plex Mono, monospace;'>{sector} · {industry}</div>
</div>
""", unsafe_allow_html=True)
        
        # === DIVIDEND SCHEDULE - MOVED TO TOP ===
        if stock_data:
            st.markdown("#### 📅 DIVIDEND SCHEDULE")
            _render_dividend_schedule(stock_data)
        
        # === PRICE SNAPSHOT ===
        st.markdown("#### 💹 PRICE & VALUATION")
        st.markdown("<p style='font-size: 9px; color: #999; margin-top: -8px;'>⚠️ P/E and P/B ratios may be inaccurate for IDX stocks</p>", unsafe_allow_html=True)
        _render_price_metrics(info, hist)
        
        # === DIVIDEND METRICS ===
        st.markdown("#### 💰 DIVIDEND METRICS")
        st.markdown("<p style='font-size: 9px; color: #999; margin-top: -8px;'>⚠️ 5Y Avg Yield may be inaccurate for IDX stocks</p>", unsafe_allow_html=True)
        _render_dividend_metrics(info, divs, stock_data)
        
        # === FINANCIAL HEALTH ===
        st.markdown("#### 📊 FINANCIAL HEALTH")
        st.markdown("<p style='font-size: 9px; color: #999; margin-top: -8px;'>⚠️ Profit Margin, Debt/Equity, and Beta may be inaccurate for IDX stocks</p>", unsafe_allow_html=True)
        _render_financial_metrics(info, stock_data)
        
        # === CHARTS WITH ENHANCED SECTION ===
        st.markdown("#### 📈 HISTORICAL PERFORMANCE")
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.markdown("**PRICE CHART (1Y)**")
            _render_price_chart(hist)
        
        with col_r:
            st.markdown("**DIVIDEND HISTORY**")
            _render_dividend_chart(divs)
        
        # === COMPANY INFO ===
        if info.get('longBusinessSummary'):
            _render_company_profile(info)
        
    except requests.exceptions.ConnectionError:
        st.error("❌ **Network Connection Error**\n\nUnable to connect to Yahoo Finance. Please check your internet connection.")
    except requests.exceptions.Timeout:
        st.error("⏱️ **Request Timeout**\n\nThe request took too long. Please try again.")
    except KeyError as e:
        st.error(f"❌ **Data Not Available**\n\nRequired data field missing: {str(e)}")
    except Exception as e:
        st.error(f"❌ **Unexpected Error**\n\n{str(e)[:200]}")
        logging.exception("Stock details dialog error")


def _render_price_metrics(info: dict, hist: pd.DataFrame):
    """Render price and valuation metrics cards."""
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
    prev_close = info.get('previousClose', 0)
    week_52_high = info.get('fiftyTwoWeekHigh', 0)
    week_52_low = info.get('fiftyTwoWeekLow', 0)
    volume = info.get('volume', 0)
    market_cap = info.get('marketCap', 0)
    pe_ratio = info.get('trailingPE', 0)
    pb_ratio = info.get('priceToBook', 0)
    
    # Calculate 1 year return
    one_year_return = 0
    if not hist.empty and len(hist) > 0:
        year_ago_price = hist['Close'].iloc[0]
        if year_ago_price > 0:
            one_year_return = ((current_price - year_ago_price) / year_ago_price) * 100
    
    price_change = current_price - prev_close if (current_price and prev_close) else 0
    price_change_pct = (price_change / prev_close * 100) if prev_close else 0
    change_color = "#00ff00" if price_change >= 0 else "#ff0000"
    change_symbol = "▲" if price_change >= 0 else "▼"
    
    cap_str = f"{market_cap/1e12:.2f}T" if market_cap >= 1e12 else f"{market_cap/1e9:.2f}B"
    
    # PE status
    if pe_ratio < 15:
        pe_status, pe_text = "status-strong", "CHEAP"
    elif pe_ratio < 25:
        pe_status, pe_text = "status-moderate", "FAIR"
    else:
        pe_status, pe_text = "status-weak", "EXPENSIVE"
    
    # PB status
    if pb_ratio < 1.5:
        pb_status, pb_text = "status-strong", "UNDERVALUED"
    elif pb_ratio < 3:
        pb_status, pb_text = "status-moderate", "FAIR"
    else:
        pb_status, pb_text = "status-weak", "OVERVALUED"
    
    st.markdown(f"""
<div style='display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 18px;'>
    <div class='bbg-box' style='background: linear-gradient(135deg, #0f0f0f 0%, #1a0f00 100%); border: 1px solid #333; border-radius: 4px; padding: 12px;'>
        <div class='bbg-label'>LAST PRICE</div>
        <div class='bbg-value' style='font-size: 18px; color: #ff8c00;'>{current_price:,.0f}</div>
        <div style='font-size: 11px; font-weight: 700; color: {change_color}; margin-top: 4px;'>{change_symbol} {price_change:+,.0f} ({price_change_pct:+.2f}%)</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;'>
        <div class='bbg-label'>1Y RETURN</div>
        <div style='font-size: 16px; font-weight: 700; color: {"#00ff41" if one_year_return >= 0 else "#ff3333"}; margin: 8px 0;'>{one_year_return:+.2f}%</div>
        <div style='font-size: 10px; color: #999;'>Annual performance</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='52-week high and low prices from Yahoo Finance'>
        <div class='bbg-label'>52W RANGE</div>
        <div style='font-size: 17px; font-weight: 600; color: #e0e0e0; margin: 4px 0;'>{week_52_low:,.0f}</div>
        <div style='font-size: 17px; font-weight: 600; color: #e0e0e0;'>{week_52_high:,.0f}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='Market capitalization and trading volume from Yahoo Finance'>
        <div class='bbg-label'>MARKET CAP</div>
        <div class='bbg-value'>{cap_str}</div>
        <div class='bbg-label' style='margin-top: 6px;'>VOLUME</div>
        <div style='font-size: 13px; font-weight: 600; color: #e0e0e0;'>{volume/1e6:.1f}M</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>P/E RATIO <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{pe_ratio:.2f}x</div>
        <div class='bbg-status {pe_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{pe_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>P/B RATIO <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{pb_ratio:.2f}x</div>
        <div class='bbg-status {pb_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{pb_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)


def _render_dividend_metrics(info: dict, divs: pd.Series, stock_data: dict = None):
    """Render dividend metrics cards."""
    # Use data from table if available, otherwise fallback to yfinance
    if stock_data:
        # DivYield from table is already decimal (0.053 = 5.3%)
        div_yield = stock_data.get('DivYield', 0)
        yield_val = div_yield * 100  # Convert to percentage
        
        # DivTTM from table (annual dividend in IDR)
        div_rate = stock_data.get('DivTTM', 0)
        
        # DPR and ROE from table are already percentages
        payout_val = stock_data.get('DPR', 0)
        
        # 5Y AVG from yfinance - already percentage, don't multiply by 100
        five_yr_avg = info.get('fiveYearAvgDividendYield', 0)
        five_yr_avg_val = five_yr_avg  # Keep as is
    else:
        # Fallback to yfinance data
        div_yield = info.get('dividendYield', 0)
        div_rate = info.get('dividendRate', info.get('trailingAnnualDividendRate', 0))
        payout_ratio = info.get('payoutRatio', 0)
        five_yr_avg = info.get('fiveYearAvgDividendYield', 0)
        
        yield_val = div_yield * 100 if div_yield else 0
        payout_val = payout_ratio * 100 if payout_ratio else 0
        five_yr_avg_val = five_yr_avg  # Already percentage from yfinance
    
    # Calculate growth
    div_growth = None
    if not divs.empty and len(divs) >= 2:
        divs_naive = divs.copy()
        divs_naive.index = divs_naive.index.tz_localize(None) if divs_naive.index.tz else divs_naive.index
        recent = divs_naive.tail(4).sum()
        older = divs_naive.tail(8).head(4).sum()
        if older > 0:
            div_growth = ((recent - older) / older) * 100
    
    growth_val = f"{div_growth:.2f}%" if div_growth is not None else "N/A"
    
    # Yield status
    if yield_val >= 5:
        yield_status, yield_text = "status-strong", "STRONG"
    elif yield_val >= 3:
        yield_status, yield_text = "status-moderate", "GOOD"
    else:
        yield_status, yield_text = "status-weak", "LOW"
    
    # Payout status
    if payout_val < 70:
        payout_status, payout_text = "status-strong", "HEALTHY"
    elif payout_val < 90:
        payout_status, payout_text = "status-moderate", "MODERATE"
    else:
        payout_status, payout_text = "status-weak", "HIGH"

    # Growth status
    if div_growth and div_growth > 5:
        growth_status, growth_text = "status-strong", "GROWING"
    elif div_growth and div_growth > -5:
        growth_status, growth_text = "status-moderate", "STABLE"
    else:
        growth_status, growth_text = "status-weak", "DECLINING"
    
    st.markdown(f"""
<div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 18px;'>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;'>
        <div class='bbg-label'>DIVIDEND YIELD</div>
        <div class='bbg-value' style='font-size: 18px; color: #00ff41;'>{yield_val:.2f}%</div>
        <div class='bbg-status {yield_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{yield_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;'>
        <div class='bbg-label'>ANNUAL DIVIDEND</div>
        <div class='bbg-value'>{div_rate:.2f}</div>
        <div style='font-size: 9px; color: #999; margin-top: 2px;'>IDR per share</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='Payout ratio from CSV table data'>
        <div class='bbg-label'>PAYOUT RATIO</div>
        <div class='bbg-value'>{payout_val:.1f}%</div>
        <div class='bbg-status {payout_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{payout_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>5Y AVG YIELD <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{five_yr_avg_val:.2f}%</div>
        <div style='font-size: 9px; color: #999; margin-top: 2px;'>Historical average</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;'>
        <div class='bbg-label'>YoY GROWTH</div>
        <div class='bbg-value' style='color: {"#00ff41" if div_growth and div_growth > 0 else "#ff3333" if div_growth else "#999"};'>{growth_val}</div>
        <div class='bbg-status {growth_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{growth_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)


def _render_dividend_schedule(stock_data: dict):
    """Render dividend schedule from table data with historical warning."""
    interim = stock_data.get('Interim', '-')
    final = stock_data.get('Final', '-')
    
    # Convert to string and determine if dividends are scheduled
    interim = str(interim) if interim is not None else '-'
    final = str(final) if final is not None else '-'
    
    has_interim = interim and interim != '-' and interim.strip()
    has_final = final and final != '-' and final.strip()
    
    if not has_interim and not has_final:
        st.markdown("""
<div style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 16px; text-align: center;'>
    <div style='font-size: 11px; color: #808080; letter-spacing: 1px;'>NO DIVIDEND SCHEDULE AVAILABLE</div>
</div>
""", unsafe_allow_html=True)
        return
    
    st.markdown("<p style='font-size: 9px; color: #999; margin-bottom: 8px;'>⚠️ Based on historical pattern - verify with official announcements</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px;'>
    <div class='bbg-box' style='background: {"linear-gradient(135deg, #0f0f0f 0%, #1a0f00 100%)" if has_interim else "#0f0f0f"}; border: 1px solid {"#ff8c00" if has_interim else "#333"}; border-radius: 4px; padding: 16px;'>
        <div class='bbg-label' style='margin-bottom: 8px; display: flex; align-items: center; gap: 4px;'>INTERIM DIVIDEND {"<span style='font-size: 10px; color: #ff8c00;'>⚠️</span>" if has_interim else ""}</div>
        <div style='font-size: 24px; font-weight: 700; color: {"#ff8c00" if has_interim else "#555"}; letter-spacing: 1px; margin: 12px 0;'>{interim if has_interim else "NOT SCHEDULED"}</div>
        <div style='font-size: 9px; color: #999; text-transform: uppercase; letter-spacing: 0.5px;'>{"Historical pattern" if has_interim else "No interim payment"}</div>
    </div>
    <div class='bbg-box' style='background: {"linear-gradient(135deg, #0f0f0f 0%, #1a0f00 100%)" if has_final else "#0f0f0f"}; border: 1px solid {"#ff8c00" if has_final else "#333"}; border-radius: 4px; padding: 16px;'>
        <div class='bbg-label' style='margin-bottom: 8px; display: flex; align-items: center; gap: 4px;'>FINAL DIVIDEND {"<span style='font-size: 10px; color: #ff8c00;'>⚠️</span>" if has_final else ""}</div>
        <div style='font-size: 24px; font-weight: 700; color: {"#ff8c00" if has_final else "#555"}; letter-spacing: 1px; margin: 12px 0;'>{final if has_final else "NOT SCHEDULED"}</div>
        <div style='font-size: 9px; color: #999; text-transform: uppercase; letter-spacing: 0.5px;'>{"Historical pattern" if has_final else "No final payment"}</div>
    </div>
</div>
""", unsafe_allow_html=True)


def _render_financial_metrics(info: dict, stock_data: dict = None):
    """Render financial health metrics cards."""
    # Use ROE from table if available
    if stock_data:
        roe_val = stock_data.get('ROE', 0)  # Already percentage from table
    else:
        roe = info.get('returnOnEquity', 0)
        roe_val = roe * 100 if roe else 0
    
    profit_margin = info.get('profitMargins', 0)
    debt_equity = info.get('debtToEquity', 0)
    beta = info.get('beta', 0)
    
    margin_val = profit_margin * 100 if profit_margin else 0
    de_val = debt_equity / 100 if debt_equity else 0
    
    # ROE status
    if roe_val >= 15:
        roe_status, roe_text = "status-strong", "EXCELLENT"
    elif roe_val >= 10:
        roe_status, roe_text = "status-moderate", "GOOD"
    else:
        roe_status, roe_text = "status-weak", "WEAK"
    
    # Margin status
    if margin_val >= 15:
        margin_status, margin_text = "status-strong", "HIGH"
    elif margin_val >= 8:
        margin_status, margin_text = "status-moderate", "MODERATE"
    else:
        margin_status, margin_text = "status-weak", "LOW"
    
    # D/E status
    if de_val < 0.5:
        de_status, de_text = "status-strong", "LOW"
    elif de_val < 1.0:
        de_status, de_text = "status-moderate", "MODERATE"
    else:
        de_status, de_text = "status-weak", "HIGH"
    
    # Beta status
    if beta < 0.8:
        beta_status, beta_text = "status-strong", "LOW VOL"
    elif beta < 1.2:
        beta_status, beta_text = "status-moderate", "MODERATE"
    else:
        beta_status, beta_text = "status-weak", "HIGH VOL"
    
    st.markdown(f"""
<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px;'>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='ROE from CSV table data'>
        <div class='bbg-label'>RETURN ON EQUITY</div>
        <div class='bbg-value' style='color: #4a90e2;'>{roe_val:.1f}%</div>
        <div class='bbg-status {roe_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{roe_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>PROFIT MARGIN <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{margin_val:.1f}%</div>
        <div class='bbg-status {margin_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{margin_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>DEBT/EQUITY <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{de_val:.2f}x</div>
        <div class='bbg-status {de_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{de_text}</div>
    </div>
    <div class='bbg-box' style='background: #0f0f0f; border: 1px solid #333; border-radius: 4px; padding: 12px;' title='⚠️ Yahoo Finance data - may be inaccurate for IDX stocks. Verify with official sources.'>
        <div class='bbg-label' style='display: flex; align-items: center; gap: 4px;'>BETA (VOLATILITY) <span style='font-size: 10px; color: #ff8c00;'>⚠️</span></div>
        <div class='bbg-value'>{beta:.2f}</div>
        <div class='bbg-status {beta_status}' style='font-size: 9px; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px;'>{beta_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)


def _render_price_chart(hist: pd.DataFrame):
    """Render price chart with moving average."""
    if not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#ff7700', width=2)
        ))
        
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['MA50'],
            mode='lines',
            name='MA50',
            line=dict(color='#4a90e2', width=1, dash='dash')
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,1)',
            font=dict(family='IBM Plex Mono', size=10, color='#b3b3b3'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#1a1a1a'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NO PRICE DATA")


def _render_dividend_chart(divs: pd.Series):
    """Render dividend history bar chart."""
    if not divs.empty:
        div_df = divs.reset_index()
        div_df.columns = ['Date', 'Dividend']
        
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            x=div_df['Date'],
            y=div_df['Dividend'],
            marker_color='#ff7700'
        ))
        
        fig_div.update_layout(
            template='plotly_dark',
            height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,1)',
            font=dict(family='IBM Plex Mono', size=10, color='#b3b3b3'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#1a1a1a'),
            showlegend=False
        )
        st.plotly_chart(fig_div, use_container_width=True)
    else:
        st.info("NO DIVIDEND DATA")


def _render_company_profile(info: dict):
    """Render company profile section."""
    with st.expander("COMPANY PROFILE", expanded=False):
        st.caption(info.get("longBusinessSummary"))
        
        if info.get('website') or info.get('fullTimeEmployees'):
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if info.get('website'):
                    st.markdown(f"**WEBSITE:** [{info.get('website')}]({info.get('website')})")
                if info.get('city'):
                    st.markdown(f"**LOCATION:** {info.get('city')}, {info.get('country', '')}")
            with c2:
                if info.get('fullTimeEmployees'):
                    st.markdown(f"**EMPLOYEES:** {info.get('fullTimeEmployees'):,}")
