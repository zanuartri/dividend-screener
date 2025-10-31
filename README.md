# 💰 Dividend Screener

Professional Bloomberg Terminal-style dividend screener for Indonesian stock market (IDX).

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

- **📊 Real-time Market Data** - Fetches live stock prices from Yahoo Finance
- **💎 Smart Valuation** - Uses Graham Number formula for fair value calculation
- **🎯 Signal System** - Automated buy/sell signals based on yield, ROE, and discount metrics
- **📅 Dividend Calendar** - Visual calendar showing expected dividend payment schedules
- **📈 Portfolio Analytics** - Statistical analysis and charts for filtered stocks
- **⚡ Filter Presets** - Quick filter presets (High Yield, Value Play, Growth Dividend, Safe Income)
- **🎨 Bloomberg Style UI** - Professional dark theme with orange accents

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/zanuartri/dividend-screener.git
cd dividend-screener

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

Access the app at `http://localhost:8501`

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
4. Click **SAVE**

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

**Valuation Formula:** Fair Value = √(22.5 × BVPS × EPS)  
_Based on Benjamin Graham's value investing methodology_

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
Ticker,BVPS,EPS,ROE,DivTTM,DPR,Interim,Final,LastUpdated
TLKM,1334.0,222.0,17.3,212.47,96.89,,July,2025-10-26 12:00:00
```

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
