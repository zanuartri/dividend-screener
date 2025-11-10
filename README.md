# 💰 Dividend Screener - Supabase Cloud Edition

Professional Bloomberg Terminal-style dividend screener for Indonesian stock market (IDX).  
**Now powered by Supabase cloud database!** ☁️

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)
![Supabase](https://img.shields.io/badge/supabase-cloud-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

- **☁️ Cloud Database** - All data stored in Supabase (no local files)
- **📊 Real-time Market Data** - Fetches live stock prices from Yahoo Finance
- **💎 Smart Valuation** - Uses Graham Number formula for fair value calculation
- **⚙️ Manual Fair Value Override** - Set custom fair value for stocks (marked with ⚙️ icon)
- **🎯 Signal System** - Automated buy/sell signals based on yield, ROE, and discount metrics
- **📅 Dividend Calendar** - Visual calendar showing expected dividend payment schedules
- **📈 Portfolio Analytics** - Statistical analysis and charts for filtered stocks
- **⚡ Filter Presets** - Quick filter presets (High Yield, Value Play, Growth Dividend, Safe Income)
- **🎨 Bloomberg Style UI** - Professional dark theme with orange accents
- **🔄 Multi-device Sync** - Access same data from any device

## 🚀 Quick Start

### Prerequisites

1. **Supabase Account** (free at https://supabase.com)
2. **Supabase Project** with database table `saham`
3. **Python 3.11+** installed

### Setup

```bash
# 1. Clone repository
git clone https://github.com/zanuartri/dividend-screener.git
cd dividend-screener

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your Supabase credentials
cat > .env << EOF
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY_HERE
EOF

# 4. Run application
streamlit run app.py
```

Access the app at `http://localhost:8501`

## 📁 Project Structure

```
dividend-screener/
├── app.py                    # Main application entry point
├── config.py                 # Configuration & constants
├── requirements.txt          # Python dependencies
├── .env                      # Supabase credentials (SECRET!)
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── data/
│   ├── loader.py            # Supabase database operations
│   ├── fetcher.py           # Yahoo Finance API integration
│   └── supabase_client.py   # Supabase wrapper client
├── models/
│   ├── signals.py           # Fair value & signal calculation
│   └── filters.py           # Filter logic & presets
├── ui/
│   ├── styles.py            # Custom CSS styling
│   ├── components.py        # Reusable UI components
│   └── dialogs.py           # Stock detail dialogs
└── utils/
    └── formatters.py        # Data formatting utilities
```

## 📖 Usage Guide

### Managing Stocks

1. Click **⚙ MANAGE** button
2. Select action: Add New / Edit Data / Delete Data
3. Enter stock fundamentals:
   - Ticker symbol (e.g., TLKM)
   - BVPS (Book Value Per Share)
   - EPS (Earnings Per Share)
   - ROE (Return on Equity %)
   - DivTTM (Dividend Trailing Twelve Months)
   - DPR (Dividend Payout Ratio %)
   - Interim & Final dividend months
   - **Manual Fair Value (Optional)** - Override Graham Number calculation with custom value
4. Click **💾 SAVE**

**Note:** Stocks with manual fair value override are marked with ⚙️ icon in the main table.

### Filtering Stocks

**Quick Presets:**

- 💰 **High Yield** - Yield ≥ 8%
- 📊 **Value Play** - Discount ≥ 20% · ROE ≥ 10%
- 🚀 **Growth Dividend** - ROE ≥ 15% · Yield ≥ 5%
- 🛡️ **Safe Income** - ROE ≥ 10% · Yield ≥ 5%

**Custom Filters:**

- Signal type (STRONG BUY, BUY, ACCUMULATE, etc.)
- Sector selection
- Minimum discount percentage
- Minimum dividend yield
- Minimum ROE
- Maximum DPR

### Analysis Tabs

- **📅 DIVIDEND CALENDAR** - Monthly dividend payment schedule with stock filtering
- **📊 STATISTICS** - Sector breakdown, signal distribution, key portfolio metrics
- **📈 CHARTS** - Yield vs ROE scatter plot, sector distribution, top opportunities

## 🎯 Signal Criteria

| Signal              | Criteria                                |
| ------------------- | --------------------------------------- |
| **STRONG BUY** 🟢   | Discount ≥ 25% · ROE ≥ 15% · Yield ≥ 8% |
| **BUY** 🟢          | Discount ≥ 15% · ROE ≥ 10% · Yield ≥ 8% |
| **ACCUMULATE** 🟡   | Discount ≥ 5% · ROE ≥ 8% · Yield ≥ 8%   |
| **WAIT** 🟠         | Below minimum thresholds                |
| **WAIT FOR DIP** 🔴 | Overvalued (discount < 0)               |

**Valuation Formula:**  
Fair Value = √(22.5 × BVPS × EPS)  
_Based on Benjamin Graham's value investing methodology_

**⚙️ Manual Fair Value Override:**  
Users can set custom fair value for specific stocks. When enabled:

- Manual fair value is used instead of Graham Number calculation
- Discount and signals are calculated based on manual value
- Stock is marked with ⚙️ icon in the table
- Set to 0 to revert to automatic Graham calculation

## 🛠️ Tech Stack

- **Python 3.11+** - Core programming language
- **Streamlit 1.30+** - Web framework
- **Supabase** - PostgreSQL cloud database
- **pandas 2.0+** - Data manipulation
- **yfinance 0.2.32+** - Market data API
- **plotly 5.18+** - Interactive charts
- **numpy 1.24+** - Numerical computing

## 🔐 Security & Best Practices

- ✅ Credentials stored in `.env` (not hardcoded)
- ✅ API keys never exposed in code
- ✅ Row Level Security (RLS) enabled in Supabase
- ⚠️ **NEVER commit `.env` file!** Already in `.gitignore`

## 🌐 Deployment

### Streamlit Cloud (Recommended - FREE!)

**PENTING:** Streamlit Cloud tidak bisa akses `.env` lokal. Credentials harus disimpan di Streamlit Cloud secrets.

#### Step-by-Step Setup:

1. **Push ke GitHub**

   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud"
   git push origin main
   ```

2. **Deploy ke Streamlit Cloud**

   - Buka: https://share.streamlit.io
   - Klik: "New app"
   - Repository: `zanuartri/dividend-screener`
   - Branch: `main`
   - Main file path: `app.py`
   - Klik: "Deploy"

3. **Setup Secrets (CRITICAL!)**

   - Di Streamlit Cloud, klik nama app → Settings ⚙️
   - Buka: "Secrets" tab
   - Paste ini:

   ```toml
   SUPABASE_URL = "https://bwqbubmbihrygdbkznqe.supabase.co"
   SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

4. **Reboot app** dan selesai! ✅

#### Cara dapat URL & Key dari Supabase:

1. Buka: https://app.supabase.com
2. Pilih project Anda
3. Klik: Settings (gear icon)
4. Buka: API tab
5. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📊 Data Model

### Supabase Table: `saham`

```sql
id                    SERIAL PRIMARY KEY
ticker                TEXT UNIQUE NOT NULL
div_ttm               DECIMAL(15, 2)
dpr                   DECIMAL(5, 2)
roe                   DECIMAL(5, 2)
bvps                  DECIMAL(15, 2)
eps                   DECIMAL(15, 2)
manual_fair_value     DECIMAL(15, 2)
interim               TEXT
final                 TEXT
last_updated          TIMESTAMP
created_at            TIMESTAMP
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Zanuartri**

- GitHub: [@zanuartri](https://github.com/zanuartri)
- Repository: [dividend-screener](https://github.com/zanuartri/dividend-screener)

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## 🚀 Recent Updates (v2.0)

- ✅ Migrated to Supabase cloud database
- ✅ Removed CSV local storage
- ✅ Simplified data layer
- ✅ Optimized UI (3-button interface)
- ✅ Removed migration scripts
- ✅ Production-ready code

---

**Built with ❤️ for Indonesian dividend investors**

_Powered by Supabase ☁️ | Streamlit 🚀 | Python 🐍_

## 📁 Project Structure

```
dividend-screener/
├── app.py                  # Main application entry point
├── config.py              # Configuration & constants
├── requirements.txt       # Python dependencies
├── data_saham.csv        # Stock fundamental data
├── .streamlit/
│   └── config.toml       # Streamlit theme configuration
├── data/
│   ├── loader.py         # CSV data operations
│   └── fetcher.py        # Yahoo Finance API integration
├── models/
│   ├── signals.py        # Fair value & signal calculation
│   └── filters.py        # Filter logic & presets
├── ui/
│   ├── styles.py         # Custom CSS styling
│   ├── components.py     # Reusable UI components
│   └── dialogs.py        # Stock detail dialogs
└── utils/
    └── formatters.py     # Data formatting utilities
```

## 📖 Usage Guide

### Managing Stocks

1. Click **⚙ MANAGE** button
2. Select action: Add New / Edit Data / Delete Data
3. Enter stock fundamentals:
   - Ticker symbol (e.g., TLKM)
   - BVPS (Book Value Per Share)
   - EPS (Earnings Per Share)
   - ROE (Return on Equity %)
   - DivTTM (Dividend Trailing Twelve Months)
   - DPR (Dividend Payout Ratio %)
   - Interim & Final dividend months
   - **Manual Fair Value (Optional)** - Override Graham Number calculation with custom value
4. Click **SAVE**

**Note:** Stocks with manual fair value override are marked with ⚙️ icon in the main table.

### Filtering Stocks

**Quick Presets:**

- 💰 **High Yield** - Yield ≥ 8%
- 📊 **Value Play** - Discount ≥ 20% · ROE ≥ 10%
- 🚀 **Growth Dividend** - ROE ≥ 15% · Yield ≥ 5%
- 🛡️ **Safe Income** - ROE ≥ 10% · Yield ≥ 5%

**Custom Filters:**

- Signal type (STRONG BUY, BUY, ACCUMULATE, etc.)
- Sector selection
- Minimum discount percentage
- Minimum dividend yield
- Minimum ROE
- Maximum DPR

### Analysis Tabs

- **📅 DIVIDEND CALENDAR** - Monthly dividend payment schedule with stock filtering
- **📊 STATISTICS** - Sector breakdown, signal distribution, key portfolio metrics
- **📈 CHARTS** - Yield vs ROE scatter plot, sector distribution, top opportunities

## 🎯 Signal Criteria

| Signal              | Criteria                                |
| ------------------- | --------------------------------------- |
| **STRONG BUY** 🟢   | Discount ≥ 25% · ROE ≥ 15% · Yield ≥ 8% |
| **BUY** 🟢          | Discount ≥ 15% · ROE ≥ 10% · Yield ≥ 8% |
| **ACCUMULATE** 🟡   | Discount ≥ 5% · ROE ≥ 8% · Yield ≥ 8%   |
| **WAIT** 🟠         | Below minimum thresholds                |
| **WAIT FOR DIP** 🔴 | Overvalued (discount < 0)               |

**Valuation Formula:**  
Fair Value = √(22.5 × BVPS × EPS)  
_Based on Benjamin Graham's value investing methodology_

**⚙️ Manual Fair Value Override:**  
Users can set custom fair value for specific stocks via the MANAGE dialog. When enabled:

- Manual fair value is used instead of Graham Number calculation
- Discount and signals are calculated based on manual value
- Stock is marked with ⚙️ icon in the table
- Set to 0 to revert to automatic Graham calculation

## 🛠️ Tech Stack

- **Python 3.11+** - Core programming language
- **Streamlit 1.30+** - Web framework
- **pandas 2.0+** - Data manipulation
- **yfinance 0.2.32+** - Market data API
- **plotly 5.18+** - Interactive charts
- **numpy 1.24+** - Numerical computing

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repository: `dividend-screener`
5. Main file: `app.py`
6. Click **Deploy**

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t dividend-screener .
docker run -p 8501:8501 dividend-screener
```

## 🔧 Configuration

Edit `.streamlit/config.toml` to customize:

- Theme colors
- Server settings
- Browser behavior

## 📊 Data Management

**Updating Stock Data:**

1. Edit `data_saham.csv` with latest fundamentals
2. Click **⟳ REFRESH** button to reload

**CSV Format:**

```csv
Ticker,BVPS,EPS,ROE,DivTTM,DPR,Interim,Final,ManualFairValue,LastUpdated
TLKM,1334.0,222.0,17.3,212.47,96.89,,July,0,2025-10-26 12:00:00
BBCA,8500.0,850.0,15.2,450.0,52.94,May,,12000,2025-10-26 12:00:00
```

_Note: ManualFairValue = 0 means use Graham Number calculation_

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Zanuartri**

- GitHub: [@zanuartri](https://github.com/zanuartri)
- Repository: [dividend-screener](https://github.com/zanuartri/dividend-screener)

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## 🙏 Acknowledgments

- Benjamin Graham - Value investing methodology
- Yahoo Finance - Market data provider
- Streamlit - Amazing web framework
- Indonesian dividend investors community

---

**Built with ❤️ for Indonesian dividend investors**

_If you find this project helpful, please consider giving it a ⭐ on GitHub!_
