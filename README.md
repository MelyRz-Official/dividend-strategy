# 💸 Real-Time Dividend Strategy Calculator

A comprehensive dividend investment tracking platform with unlimited live market data integration via Yahoo Finance.

## 🚀 Features

- **🔥 Unlimited real-time data** - No API limits with Yahoo Finance integration
- **📈 Portfolio performance tracking** with precise gains/losses analysis  
- **💼 Professional transaction tracking** with detailed share-level accounting
- **📊 Interactive visualizations** with Plotly charts
- **🎯 Strategy comparison tools** against benchmarks
- **📋 CSV export capabilities** for advanced analysis
- **🌙 Modern dark theme UI** with professional styling

## 📋 Quick Start

1. **Install Python 3.8+** if not already installed

2. **Install dependencies**
   ```bash
   pip install yfinance pandas plotly sv-ttk pywebview
   ```

3. **Run the application**
   ```bash
   python dividend_gui.py
   ```

4. **Enable live data**
   - Check "Use Live Market Data" ✅
   - No API key required - unlimited requests!

5. **Start calculating**
   - Enter investment amount
   - Get real-time dividend projections instantly

## 🆕 What's New in V2.0

### 🎉 Major Improvements
- **✅ Yahoo Finance Integration** - No more API key headaches!
- **✅ Unlimited Data Requests** - No rate limiting
- **✅ Better Performance** - Faster data fetching
- **✅ Enhanced Portfolio Tracking** - Transaction-level detail
- **✅ Improved Error Handling** - More reliable operation

### 🏗️ Architecture
The application is now modular with clean separation:
- `dividend_gui.py` - Main application interface
- `yahoo_finance_provider.py` - Market data integration
- `portfolio_manager.py` - Transaction and holdings management
- `chart_generator.py` - Interactive visualizations
- `data_processor.py` - Calculations and analytics
- `utils.py` - Helper functions

## 📦 File Structure

```
dividend-calculator/
├── dividend_gui.py           # 🖥️ Main application
├── yahoo_finance_provider.py # 📡 Market data (Yahoo Finance)
├── portfolio_manager.py      # 💼 Portfolio tracking
├── chart_generator.py        # 📊 Plotly visualizations
├── data_processor.py         # 🧮 Calculations & analytics
├── utils.py                  # 🔧 Utility functions
├── config.py                 # ⚙️ Configuration settings
├── requirements.txt          # 📋 Dependencies
└── README.md                 # 📖 This file
```

## 🔧 Configuration

### Default Portfolio Allocation
Edit `config.py` to customize your dividend stock allocation:

```python
DIVIDEND_STOCKS = (
    {"ticker": "O", "name": "Realty Income", "yield": 0.055, "allocation": 0.20},
    {"ticker": "SCHD", "name": "Schwab US Dividend", "yield": 0.038, "allocation": 0.15},
    # Add your preferred dividend stocks...
)
```

### Cache Settings
```python
CACHE_DURATION_HOURS = 1  # How long to cache market data
```

## 📊 Features Deep Dive

### 💰 Investment Calculator
- Real-time dividend yield calculations
- Allocation across dividend-focused portfolio
- Monthly and annual income projections
- Live vs. static yield comparisons

### 📈 Portfolio Analytics
- **Allocation Charts** - Visual portfolio breakdown
- **Yield Comparison** - Static configuration vs. live market data
- **Performance Tracking** - Gains/losses with percentage returns
- **Investment Timeline** - Historical investment patterns

### 🔄 Data Management
- **Automatic CSV Export** - Investment history tracking
- **Portfolio Persistence** - JSON-based transaction storage
- **Market Data Caching** - Optimized performance
- **Backup Functionality** - Data protection

### 📱 User Experience
- **Dark Theme** - Professional appearance
- **Progress Indicators** - For long operations
- **Error Handling** - Graceful degradation
- **Responsive Design** - Clean, organized layout

## 🎯 Default Stock Portfolio

| Ticker | Company | Allocation | Target Yield |
|--------|---------|------------|--------------|
| **O** | Realty Income | 20% | 5.5% |
| **TROW** | T. Rowe Price | 15% | 4.3% |
| **SCHD** | Schwab US Dividend ETF | 15% | 3.8% |
| **HDV** | iShares Core High Dividend | 10% | 3.8% |
| **MO** | Altria Group | 10% | 8.0% |
| **APLE** | Apple Hospitality REIT | 10% | 6.0% |
| **ABBV** | AbbVie | 10% | 4.0% |
| **VZ** | Verizon Communications | 10% | 6.6% |

*Customize in `config.py` - allocations must sum to 100%*

## 🚀 Advanced Usage

### Building Standalone App
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name="DividendTracker" dividend_gui.py
```

### Batch Processing
```bash
# Run calculations for multiple amounts
python -c "
from dividend_gui import DividendApp
import tkinter as tk
# Automated testing/batch processing
"
```

### Data Export
- **Portfolio Export**: JSON format with transaction details
- **Market Data Export**: CSV with current prices and yields
- **Historical Analysis**: CSV export of all calculations

## 🆘 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'yfinance'"**
```bash
pip install yfinance
```

**Charts not displaying**
```bash
pip install pywebview  # For embedded charts
# Or charts will fallback to browser automatically
```

**Slow performance**
- Disable live data for faster calculations
- Increase cache duration in `config.py`
- Check internet connection

**Data not updating**
- Clear cache files in Documents folder
- Restart application
- Verify internet connectivity

### Debug Mode
Add debug output by running:
```bash
python dividend_gui.py --debug
```

## 🔄 Migration from V1.x

If upgrading from Alpha Vantage version:

1. **Backup your data**
   ```bash
   cp dividend_history.csv dividend_history_backup.csv
   cp portfolio_data.json portfolio_data_backup.json
   ```

2. **Install new dependencies**
   ```bash
   pip install yfinance
   ```

3. **Remove Alpha Vantage config** (optional)
   - Remove `ALPHA_VANTAGE_API_KEY` from `config.py`

4. **Run application** - automatic compatibility mode

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/dividend-calculator.git
cd dividend-calculator

# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run tests
python -m pytest tests/

# Format code
black *.py
```

### Feature Requests
- 🌟 Star the repository
- 📝 Open an issue with feature description
- 🔧 Submit pull requests

## 📊 Roadmap

### Upcoming Features
- [ ] **Multi-currency support** for international dividends
- [ ] **Tax optimization** calculations
- [ ] **DRIP modeling** (Dividend Reinvestment Plans)
- [ ] **Sector analysis** and diversification metrics
- [ ] **Mobile app** development
- [ ] **Cloud sync** for multi-device access

## 🏆 Acknowledgments

- **Yahoo Finance** for providing free market data
- **Plotly** for beautiful interactive charts
- **tkinter & sv-ttk** for the user interface
- **Community contributors** for feedback and improvements

## 📄 License

MIT License - Open source for educational and personal use.

## ⚠️ Important Disclaimers

- **Educational Purpose**: This tool is for learning and analysis only
- **Not Financial Advice**: Always consult with qualified financial advisors
- **Market Risk**: Past performance doesn't guarantee future results
- **Data Accuracy**: While we strive for accuracy, verify important data independently
- **Tax Implications**: Consult tax professionals for investment tax strategies

---

## 🌟 Love the project? 

⭐ **Star this repository** to show your support!  
🐛 **Found a bug?** Open an issue  
💡 **Have an idea?** Submit a feature request  
🤝 **Want to contribute?** Fork and create a pull request  

**Happy dividend investing! 💰📈**