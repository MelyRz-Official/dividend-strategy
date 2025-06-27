# -*- coding: utf-8 -*-
"""
Market data provider for Alpha Vantage API integration
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path


def load_api_key():
    """Load API key from config file or environment variable"""
    # Try environment variable first
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if api_key:
        return api_key
    
    # Try config file
    try:
        import config
        return getattr(config, 'ALPHA_VANTAGE_API_KEY', 'demo')
    except ImportError:
        # Config file doesn't exist, show setup message
        print("⚠️  API Configuration Missing!")
        print("Please setup your API key:")
        print("1. Copy config.example.py to config.py")
        print("2. Add your Alpha Vantage API key to config.py")
        print("3. Or set ALPHA_VANTAGE_API_KEY environment variable")
        print("4. Get free key at: https://www.alphavantage.co/support/#api-key")
        return 'demo'


class MarketDataProvider:
    """Handles all market data API interactions"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or load_api_key()
        self.cache = self._load_cache()
        self.last_api_call = 0
        
        # Load configuration
        try:
            import config
            self.api_call_delay = getattr(config, 'API_CALL_DELAY', 12)
            self.cache_duration_hours = getattr(config, 'CACHE_DURATION_HOURS', 1)
            self.base_url = getattr(config, 'ALPHA_VANTAGE_BASE_URL', "https://www.alphavantage.co/query")
            self.cache_filename = getattr(config, 'CACHE_FILENAME', 
                                        os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json"))
        except ImportError:
            self.api_call_delay = 12
            self.cache_duration_hours = 1
            self.base_url = "https://www.alphavantage.co/query"
            self.cache_filename = os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json")

    def _load_cache(self) -> Dict:
        """Load cached market data"""
        try:
            cache_filename = getattr(self, 'cache_filename', 
                                   os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json"))
            
            if os.path.exists(cache_filename):
                with open(cache_filename, 'r') as f:
                    cache_data = json.load(f)
                    # Check if cache is less than configured hours old
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
            cache_filename = getattr(self, 'cache_filename', 
                                   os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json"))
            
            os.makedirs(os.path.dirname(cache_filename), exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': self.cache
            }
            with open(cache_filename, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _rate_limit(self):
        """Enforce API rate limiting"""
        time_since_last_call = time.time() - self.last_api_call
        if time_since_last_call < self.api_call_delay:
            time.sleep(self.api_call_delay - time_since_last_call)
        self.last_api_call = time.time()

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get current stock price and basic info"""
        if symbol in self.cache and 'quote' in self.cache[symbol]:
            return self.cache[symbol]['quote']

        try:
            self._rate_limit()
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data:
                quote_data = data['Global Quote']
                quote_info = {
                    'symbol': quote_data.get('01. symbol', symbol),
                    'price': float(quote_data.get('05. price', 0)),
                    'change': float(quote_data.get('09. change', 0)),
                    'change_percent': quote_data.get('10. change percent', '0%').replace('%', ''),
                    'volume': int(float(quote_data.get('06. volume', 0))),
                    'timestamp': datetime.now().isoformat()
                }
                
                if symbol not in self.cache:
                    self.cache[symbol] = {}
                self.cache[symbol]['quote'] = quote_info
                self._save_cache()
                
                return quote_info
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
        
        return None

    def get_dividend_data(self, symbol: str) -> Optional[Dict]:
        """Get dividend data for a stock"""
        if symbol in self.cache and 'dividends' in self.cache[symbol]:
            return self.cache[symbol]['dividends']

        try:
            self._rate_limit()
            # Using time series monthly adjusted to get dividend info
            params = {
                'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Monthly Adjusted Time Series' in data:
                time_series = data['Monthly Adjusted Time Series']
                
                # Calculate annual dividend from recent data
                recent_months = list(time_series.keys())[:12]  # Last 12 months
                total_dividends = 0
                
                for month in recent_months:
                    dividend = float(time_series[month].get('7. dividend amount', 0))
                    total_dividends += dividend
                
                # Get latest stock price for yield calculation
                latest_month = recent_months[0]
                latest_price = float(time_series[latest_month]['5. adjusted close'])
                
                dividend_info = {
                    'annual_dividend': total_dividends,
                    'dividend_yield': (total_dividends / latest_price) if latest_price > 0 else 0,
                    'last_price': latest_price,
                    'timestamp': datetime.now().isoformat()
                }
                
                if symbol not in self.cache:
                    self.cache[symbol] = {}
                self.cache[symbol]['dividends'] = dividend_info
                self._save_cache()
                
                return dividend_info
        except Exception as e:
            print(f"Error fetching dividend data for {symbol}: {e}")
        
        return None

    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Get company fundamental data"""
        if symbol in self.cache and 'overview' in self.cache[symbol]:
            return self.cache[symbol]['overview']

        try:
            self._rate_limit()
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Symbol' in data:
                overview_info = {
                    'name': data.get('Name', ''),
                    'sector': data.get('Sector', ''),
                    'dividend_yield': float(data.get('DividendYield', 0)) if data.get('DividendYield') != 'None' else 0,
                    'dividend_per_share': float(data.get('DividendPerShare', 0)) if data.get('DividendPerShare') != 'None' else 0,
                    'ex_dividend_date': data.get('ExDividendDate', ''),
                    'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') != 'None' else 0,
                    'market_cap': data.get('MarketCapitalization', ''),
                    'timestamp': datetime.now().isoformat()
                }
                
                if symbol not in self.cache:
                    self.cache[symbol] = {}
                self.cache[symbol]['overview'] = overview_info
                self._save_cache()
                
                return overview_info
        except Exception as e:
            print(f"Error fetching overview for {symbol}: {e}")
        
        return None