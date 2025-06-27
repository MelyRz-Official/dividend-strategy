# 💸 Real-Time Dividend Strategy Calculator

A comprehensive dividend investment tracking platform with live market data integration.

## 🚀 Features

- **Real-time dividend calculations** with live market data
- **Portfolio performance tracking** with gains/losses analysis
- **Professional-grade analytics** and visualizations
- **Market data dashboard** for dividend stocks
- **Export capabilities** for further analysis
- **Strategy comparison** tools

## 📋 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dividend-calculator.git
   cd dividend-calculator
   ```

2. **Install dependencies**
   ```bash
   pip install pandas plotly pywebview sv-ttk requests
   ```

3. **Setup API configuration**
   ```bash
   # Copy the example config file
   cp config.example.py config.py
   ```

4. **Get your free API key**
   - Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Sign up for a free account (500 API calls/day)
   - Copy your API key

5. **Configure your API key**
   - Open `config.py` in a text editor
   - Replace `"your_api_key_here"` with your actual API key
   - Save the file

## 🔑 API Key Setup

### Method 1: Config File (Recommended)
Edit `config.py`:
```python
ALPHA_VANTAGE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

### Method 2: Environment Variable
Set environment variable:
```bash
# Windows
set ALPHA_VANTAGE_API_KEY=your_api_key_here

# macOS/Linux
export ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## 🖥️ Usage

1. **Run the application**
   ```bash
   python dividend_gui.py
   ```

2. **Enable live data**
   - Check "Use Live Market Data" in the app
   - Enter your API key if prompted

3. **Calculate dividends**
   - Enter investment amount
   - Click "Calculate" to see projections with live data

## 📦 Building Desktop App

Create a standalone executable:
```bash
pyinstaller --onefile --windowed --name="DividendTracker" dividend_app.py
```

## 🔒 Security Notes

- **Never commit `config.py`** - it contains your API keys
- The `.gitignore` file prevents accidental commits
- Use environment variables in production environments
- Rotate API keys regularly for security

## 📊 Features Overview

### Real-Time Data
- Live stock prices and dividend yields
- Current market values and gains/losses
- Ex-dividend date tracking

### Analytics
- Portfolio allocation pie charts
- Yield comparison (static vs live)
- Investment timeline tracking
- Performance vs strategy benchmarks

### Export & Analysis
- CSV export functionality
- Historical data tracking
- Professional-grade visualizations

## 🆘 Troubleshooting

### API Issues
- Verify your API key is correct in `config.py`
- Check rate limits (5 calls/minute for free tier)
- Demo key only works with AAPL stock

### Installation Issues
- Ensure Python 3.8+ is installed
- Use virtual environment for clean setup
- Install Visual C++ Build Tools if needed on Windows

## 📄 License

MIT License - feel free to use and modify for your investment needs!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**⚠️ Disclaimer:** This tool is for educational purposes. Always consult with financial advisors for investment decisions.