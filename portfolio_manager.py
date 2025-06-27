# -*- coding: utf-8 -*-
"""
Portfolio management and data persistence
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from market_data import MarketDataProvider


class PortfolioManager:
    """Manages portfolio holdings and data persistence"""
    
    def __init__(self, market_provider: MarketDataProvider, filename: str = 'portfolio_data.json'):
        self.market_provider = market_provider
        self.filename = filename
        self.portfolio_holdings = []
        self.total_invested_from_holdings = 0
        
        # Load configuration for fallback prices
        try:
            import config
            self.fallback_prices = getattr(config, 'FALLBACK_PRICES', {})
            self.dividend_stocks = config.DIVIDEND_STOCKS
        except ImportError:
            self.fallback_prices = {
                "O": 55.0, "TROW": 110.0, "SCHD": 75.0, "HDV": 105.0,
                "MO": 45.0, "APLE": 15.0, "ABBV": 165.0, "VZ": 40.0
            }
            self.dividend_stocks = []

    def load_portfolio_data(self) -> Dict:
        """Load portfolio data from JSON file"""
        try:
            if Path(self.filename).exists():
                with open(self.filename, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "portfolio": [],
                    "total_invested": 0,
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            return {"portfolio": [], "total_invested": 0}

    def save_portfolio_data(self, portfolio_data: Dict):
        """Save portfolio data to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            print(f"Portfolio saved: {len(portfolio_data['portfolio'])} stocks, ${portfolio_data['total_invested']:.2f}")
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            raise

    def load_portfolio_holdings(self) -> bool:
        """Load portfolio holdings from portfolio_data.json - supports both old and new formats"""
        try:
            portfolio_file = Path(self.filename)
            if portfolio_file.exists():
                with open(portfolio_file, 'r') as f:
                    data = json.load(f)
                
                # Check if this is the new transaction-based format
                if "transactions" in data and "summary" in data:
                    print("Loading new transaction-based portfolio format...")
                    # Convert new format to old format for compatibility
                    self.portfolio_holdings = []
                    total_invested = 0
                    
                    for symbol, summary in data["summary"].items():
                        holding = {
                            "symbol": symbol,
                            "shares": summary["total_shares"],
                            "purchase_price": summary["avg_cost_per_share"],
                            "total_cost": summary["total_cost"],
                            "current_price": summary.get("current_price", 0),
                            "current_value": summary.get("current_value", 0),
                            "purchase_date": "2024-01-01",  # Default from your data
                            "last_purchase_date": "2024-01-01"
                        }
                        self.portfolio_holdings.append(holding)
                        total_invested += summary["total_cost"]
                    
                    self.total_invested_from_holdings = total_invested
                    print(f"Loaded {len(self.portfolio_holdings)} holdings from new format: ${total_invested:.2f}")
                    return True
                
                # Legacy format support
                elif "portfolio" in data:
                    self.portfolio_holdings = data.get("portfolio", [])
                    self.total_invested_from_holdings = data.get("total_invested", 0)
                    print(f"Loaded {len(self.portfolio_holdings)} holdings from legacy format: ${self.total_invested_from_holdings:.2f}")
                    return True
                
                else:
                    print("Unknown portfolio format")
                    return False
                    
            else:
                print(f"No {self.filename} found - using manual entries")
                self.portfolio_holdings = []
                self.total_invested_from_holdings = 0
                return False
                
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            self.portfolio_holdings = []
            self.total_invested_from_holdings = 0
            return False

    def update_portfolio_from_calculation(self, calculation_data: List[Dict], use_live_data: bool = False) -> bool:
        """Update portfolio holdings based on calculation data with live market data"""
        try:
            if not calculation_data:
                print("No calculation data to process")
                return False
            
            # Load existing portfolio
            portfolio_data = self.load_portfolio_data()
            
            # Get total investment amount from calculation
            total_investment = calculation_data[0]["Total Investment"]
            
            print(f"Processing ${total_investment:.2f} investment with {'live' if use_live_data else 'static'} market data...")
            
            # Process each stock in the calculation
            shares_purchased = []
            for stock_data in calculation_data:
                symbol = stock_data["Ticker"]
                allocated_amount = stock_data["Amount Invested"]
                
                # Get current price (from live data if available)
                current_price = None
                
                if use_live_data:
                    quote_data = self.market_provider.get_stock_quote(symbol)
                    if quote_data and quote_data.get("price", 0) > 0:
                        current_price = quote_data["price"]
                        print(f"  {symbol}: Using live price ${current_price:.2f}")
                    else:
                        print(f"  {symbol}: Live price not available, using fallback")
                        current_price = None
                else:
                    current_price = None
                
                if current_price is None:
                    # Use fallback prices
                    current_price = self.fallback_prices.get(symbol, 100.0)
                    print(f"  {symbol}: Using fallback price ${current_price:.2f}")
                
                # Calculate shares that can be purchased
                shares_to_buy = allocated_amount / current_price
                
                shares_purchased.append({
                    "symbol": symbol,
                    "shares": shares_to_buy,
                    "price": current_price,
                    "allocated": allocated_amount,
                    "total_cost": allocated_amount
                })
                
                print(f"  {symbol}: {shares_to_buy:.6f} shares @ ${current_price:.2f} = ${allocated_amount:.2f}")
            
            # Update portfolio holdings
            portfolio_updated = False
            for purchase in shares_purchased:
                symbol = purchase["symbol"]
                shares = purchase["shares"]
                price = purchase["price"]
                cost = purchase["total_cost"]
                
                # Find existing holding
                existing_stock = None
                for stock in portfolio_data["portfolio"]:
                    if stock["symbol"] == symbol:
                        existing_stock = stock
                        break
                
                if existing_stock:
                    # Update existing holding with weighted average price
                    old_shares = existing_stock["shares"]
                    old_total_cost = existing_stock["total_cost"]
                    
                    new_shares = old_shares + shares
                    new_total_cost = old_total_cost + cost
                    new_avg_price = new_total_cost / new_shares if new_shares > 0 else price
                    
                    existing_stock["shares"] = new_shares
                    existing_stock["total_cost"] = new_total_cost
                    existing_stock["purchase_price"] = new_avg_price
                    existing_stock["last_purchase_date"] = datetime.now().strftime("%Y-%m-%d")
                    
                    print(f"  Updated {symbol}: {old_shares:.6f} -> {new_shares:.6f} shares")
                    portfolio_updated = True
                    
                else:
                    # Add new holding
                    new_stock = {
                        "symbol": symbol,
                        "shares": shares,
                        "purchase_price": price,
                        "total_cost": cost,
                        "purchase_date": datetime.now().strftime("%Y-%m-%d"),
                        "last_purchase_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    portfolio_data["portfolio"].append(new_stock)
                    print(f"  Added {symbol}: {shares:.6f} shares @ ${price:.2f}")
                    portfolio_updated = True
            
            if portfolio_updated:
                # Update portfolio totals
                portfolio_data["total_invested"] = sum(stock["total_cost"] for stock in portfolio_data["portfolio"])
                portfolio_data["last_updated"] = datetime.now().isoformat()
                
                # Save updated portfolio
                self.save_portfolio_data(portfolio_data)
                
                # Reload into manager
                self.load_portfolio_holdings()
                
                print(f"Portfolio updated! New total: ${portfolio_data['total_invested']:.2f}")
                return True
            else:
                print("No portfolio changes made")
                return False
                
        except Exception as e:
            print(f"Error updating portfolio: {e}")
            return False

    def get_portfolio_summary(self) -> Dict:
        """Get a summary of current portfolio holdings"""
        if not self.portfolio_holdings:
            return {
                "total_stocks": 0,
                "total_invested": 0,
                "holdings": []
            }
        
        holdings_summary = []
        for holding in self.portfolio_holdings:
            holdings_summary.append({
                "symbol": holding["symbol"],
                "shares": holding["shares"],
                "avg_price": holding["purchase_price"],
                "total_cost": holding["total_cost"],
                "purchase_date": holding.get("purchase_date", "Unknown"),
                "last_purchase": holding.get("last_purchase_date", "Unknown")
            })
        
        return {
            "total_stocks": len(self.portfolio_holdings),
            "total_invested": self.total_invested_from_holdings,
            "holdings": holdings_summary
        }

    def export_portfolio_to_csv(self, filename: str = None) -> str:
        """Export portfolio holdings to CSV"""
        import pandas as pd
        
        if filename is None:
            filename = f"portfolio_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.portfolio_holdings:
            raise ValueError("No portfolio holdings to export")
        
        # Convert holdings to DataFrame
        df = pd.DataFrame(self.portfolio_holdings)
        
        # Add current market values if possible
        current_values = []
        for holding in self.portfolio_holdings:
            symbol = holding["symbol"]
            shares = holding["shares"]
            
            # Try to get current price
            quote_data = self.market_provider.get_stock_quote(symbol)
            if quote_data and quote_data.get("price", 0) > 0:
                current_price = quote_data["price"]
                current_value = shares * current_price
                gain_loss = current_value - holding["total_cost"]
            else:
                current_price = 0
                current_value = 0
                gain_loss = 0
            
            current_values.append({
                "current_price": current_price,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percent": (gain_loss / holding["total_cost"] * 100) if holding["total_cost"] > 0 else 0
            })
        
        # Add market data to DataFrame
        market_df = pd.DataFrame(current_values)
        export_df = pd.concat([df, market_df], axis=1)
        
        # Export to CSV
        export_df.to_csv(filename, index=False)
        print(f"Portfolio exported to {filename}")
        
        return filename