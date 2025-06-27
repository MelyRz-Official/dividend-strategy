# -*- coding: utf-8 -*-
"""
Yahoo Finance data provider - No API key required, more generous limits
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os


class YahooFinanceProvider:
    """Yahoo Finance data provider with no API limits"""
    
    def __init__(self):
        self.cache = self._load_cache()
        
        # Load configuration if available
        try:
            import config
            self.cache_duration_hours = getattr(config, 'CACHE_DURATION_HOURS', 1)
            self.cache_filename = getattr(config, 'CACHE_FILENAME', 
                                        os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json"))
        except ImportError:
            self.cache_duration_hours = 1
            self.cache_filename = os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json")

    def _load_cache(self) -> Dict:
        """Load cached market data"""
        try:
            cache_filename = getattr(self, 'cache_filename', 
                                   os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json"))
            
            if os.path.exists(cache_filename):
                with open(cache_filename, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                    cache_valid_hours = getattr(self, 'cache_duration_hours', 1)
                    if datetime.now() - cache_time < timedelta(hours=cache_valid_hours):
                        return cache_data.get('data', {})
            return {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}

    def _save_cache(self):
        """Save market data to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_filename), exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': self.cache
            }
            with open(self.cache_filename, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get current stock price and basic info"""
        if symbol in self.cache and 'quote' in self.cache[symbol]:
            return self.cache[symbol]['quote']

        try:
            print(f"[API] Fetching Yahoo Finance data for {symbol}...")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get current data
            info = ticker.info
            history = ticker.history(period="2d")  # Get last 2 days for change calculation
            
            if len(history) >= 2:
                current_price = history['Close'].iloc[-1]
                previous_close = history['Close'].iloc[-2]
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                volume = int(history['Volume'].iloc[-1])
            else:
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                change = info.get('regularMarketChange', 0)
                change_percent = info.get('regularMarketChangePercent', 0)
                volume = info.get('volume', 0)
            
            quote_info = {
                'symbol': symbol,
                'price': float(current_price),
                'change': float(change),
                'change_percent': f"{change_percent:.2f}",
                'volume': int(volume),
                'timestamp': datetime.now().isoformat()
            }
            
            if symbol not in self.cache:
                self.cache[symbol] = {}
            self.cache[symbol]['quote'] = quote_info
            self._save_cache()
            
            print(f"[OK] Got {symbol}: ${current_price:.2f}")
            return quote_info
            
        except Exception as e:
            print(f"[ERROR] Error fetching quote for {symbol}: {e}")
            return None

    def get_dividend_data(self, symbol: str) -> Optional[Dict]:
        """Get dividend data for a stock"""
        if symbol in self.cache and 'dividends' in self.cache[symbol]:
            return self.cache[symbol]['dividends']

        try:
            print(f"[API] Fetching dividend data for {symbol}...")
            
            ticker = yf.Ticker(symbol)
            
            # Get dividend history
            dividends = ticker.dividends
            if len(dividends) == 0:
                print(f"[WARNING] No dividend data found for {symbol}")
                return None
            
            # Calculate annual dividend (last 12 months) - FIX: Use timezone-naive comparison
            import pandas as pd
            one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
            
            # Convert dividend index to timezone-naive if needed
            if dividends.index.tz is not None:
                dividend_index_naive = dividends.index.tz_convert(None)
                dividends_naive = pd.Series(dividends.values, index=dividend_index_naive)
            else:
                dividends_naive = dividends
            
            # Filter for recent dividends
            recent_dividends = dividends_naive[dividends_naive.index > one_year_ago]
            annual_dividend = recent_dividends.sum()
            
            # Get current price for yield calculation
            current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
            if current_price == 0:
                # Fallback to recent price
                history = ticker.history(period="1d")
                if len(history) > 0:
                    current_price = history['Close'].iloc[-1]
            
            dividend_yield = (annual_dividend / current_price) if current_price > 0 else 0
            
            dividend_info = {
                'annual_dividend': float(annual_dividend),
                'dividend_yield': float(dividend_yield),
                'last_price': float(current_price),
                'timestamp': datetime.now().isoformat()
            }
            
            if symbol not in self.cache:
                self.cache[symbol] = {}
            self.cache[symbol]['dividends'] = dividend_info
            self._save_cache()
            
            print(f"[OK] Got dividend data for {symbol}: {dividend_yield*100:.2f}% yield")
            return dividend_info
            
        except Exception as e:
            print(f"[ERROR] Error fetching dividend data for {symbol}: {e}")
            return None

    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Get company fundamental data"""
        if symbol in self.cache and 'overview' in self.cache[symbol]:
            return self.cache[symbol]['overview']

        try:
            print(f"[API] Fetching company overview for {symbol}...")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get dividend information
            dividend_yield = info.get('dividendYield', 0)
            if dividend_yield:
                dividend_yield = float(dividend_yield)
            
            dividend_per_share = info.get('trailingAnnualDividendRate', 0)
            if dividend_per_share:
                dividend_per_share = float(dividend_per_share)
            
            ex_dividend_date = info.get('exDividendDate', '')
            if ex_dividend_date:
                # Convert timestamp to date string
                try:
                    if isinstance(ex_dividend_date, (int, float)):
                        ex_dividend_date = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
                except:
                    ex_dividend_date = str(ex_dividend_date)
            
            overview_info = {
                'name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'dividend_yield': dividend_yield,
                'dividend_per_share': dividend_per_share,
                'ex_dividend_date': ex_dividend_date,
                'pe_ratio': info.get('trailingPE', 0),
                'market_cap': info.get('marketCap', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            if symbol not in self.cache:
                self.cache[symbol] = {}
            self.cache[symbol]['overview'] = overview_info
            self._save_cache()
            
            print(f"[OK] Got overview for {symbol}")
            return overview_info
            
        except Exception as e:
            print(f"[ERROR] Error fetching overview for {symbol}: {e}")
            return None


# Drop-in replacement function
def create_market_provider():
    """Factory function to create the best available market provider"""
    try:
        import yfinance
        print("[LAUNCH] Using Yahoo Finance provider (unlimited requests)")
        return YahooFinanceProvider()
    except ImportError:
        print("[WARNING] yfinance not installed, falling back to Alpha Vantage")
        from market_data import MarketDataProvider
        return MarketDataProvider()