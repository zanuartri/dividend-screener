"""
Configuration constants and thresholds for the Dividend Dashboard.
Extract magic numbers into named constants for better maintainability.
"""

# File paths
CSV_PATH = "data_saham.csv"
EXCHANGE_SUFFIX = ".JK"

# Cache settings
CACHE_TTL_PRICES = 600  # 10 minutes
CACHE_TTL_DETAILS = 86400  # 24 hours

# Signal thresholds
THRESHOLDS = {
    'MIN_YIELD': 0.08,           # 8% minimum dividend yield (stored as decimal)
    'MIN_ROE_BASIC': 8.0,        # 8% minimum ROE (stored as percentage value)
    'EXCEPTIONAL_YIELD': 0.10,   # 10% yield exception for low ROE
    'HIGH_DISCOUNT': 0.20,       # 20% discount exception
    'EXCELLENT_ROE': 15.0,       # 15% ROE for excellent rating (stored as percentage value)
    'GOOD_ROE': 10.0,            # 10% ROE for good rating (stored as percentage value)
    'FAIR_DISCOUNT': 0.05,       # 5% discount for accumulate
    'GOOD_DISCOUNT': 0.15,       # 15% discount for buy
    'GRAHAM_MULTIPLIER': 22.5,   # Benjamin Graham formula constant
    'SAFE_DPR': 70.0,            # 70% DPR considered safe (stored as percentage value)
    'MODERATE_DPR': 80.0,        # 80% DPR moderate risk (stored as percentage value)
    'ELEVATED_DPR': 100.0,       # 100% DPR elevated risk (stored as percentage value)
}

# Display columns
MANUAL_COLUMNS = [
    "Ticker", "BVPS", "EPS", "ROE", "DivTTM", 
    "DPR", "Interim", "Final", "LastUpdated"
]

ALL_COLUMNS = [
    "Ticker", "BVPS", "EPS", "ROE", "DivTTM", "DPR", 
    "Interim", "Final", "LastUpdated", "CurrentPrice", 
    "DivYield", "Discount", "FairValue", "Signal", "Sector"
]

NUMERIC_COLS = [
    "DivTTM", "DivYield", "DPR", "ROE", "BVPS", 
    "EPS", "FairValue", "CurrentPrice", "Discount"
]

# UI Options
MONTH_OPTIONS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

SIGNAL_OPTIONS = [
    "STRONG BUY", "BUY", "ACCUMULATE", "WAIT", "WAIT FOR DIP"
]

# Display names for columns
DISPLAY_NAMES = {
    "Ticker": "TICKER",
    "Sector": "SECTOR",
    "LastUpdated": "LAST UPDATE",
    "DivTTM": "DIV TTM",
    "DivYield": "DIV YIELD",
    "DPR": "DPR",
    "Interim": "INTERIM",
    "Final": "FINAL",
    "ROE": "ROE",
    "BVPS": "BVPS",
    "EPS": "EPS",
    "FairValue": "FAIR VALUE",
    "CurrentPrice": "CURRENT PRICE",
    "Discount": "DISCOUNT",
    "Signal": "SIGNAL"
}

# Format strings for display
FORMATTERS = {
    "LAST UPDATE": "{:%d %b %Y %H:%M}",
    "DISCOUNT": "{:.2%}",
    "DIV YIELD": "{:.2%}",
    "DPR": "{:.1f}%",
    "ROE": "{:.1f}%",
    "FAIR VALUE": "{:.0f}",
    "CURRENT PRICE": "{:.0f}",
    "BVPS": "{:.2f}",
    "EPS": "{:.2f}",
    "DIV TTM": "{:.2f}",
}

# Filter presets
FILTER_PRESETS = {
    "High Yield": {
        "filter_yield_min": 8.0,
        "filter_signals": ["STRONG BUY", "BUY", "ACCUMULATE"],
        "filter_roe_min": 0.0,
        "filter_discount_min": 0.0,
        "filter_dpr_max": 1000.0,
        "filter_sectors": []
    },
    "Value Play": {
        "filter_discount_min": 20.0,
        "filter_roe_min": 10.0,
        "filter_signals": ["STRONG BUY", "BUY"],
        "filter_yield_min": 5.0,
        "filter_dpr_max": 1000.0,
        "filter_sectors": []
    },
    "Growth Dividend": {
        "filter_roe_min": 15.0,
        "filter_yield_min": 5.0,
        "filter_signals": ["STRONG BUY", "BUY"],
        "filter_discount_min": 0.0,
        "filter_dpr_max": 1000.0,
        "filter_sectors": []
    },
    "Safe Income": {
        "filter_roe_min": 10.0,
        "filter_yield_min": 5.0,
        "filter_signals": ["STRONG BUY", "BUY", "ACCUMULATE"],
        "filter_discount_min": 0.0,
        "filter_dpr_max": 1000.0,
        "filter_sectors": []
    }
}
