# -*- coding: utf-8 -*-
"""
Data processing logic for dividend calculations and portfolio analysis
"""

import pandas as pd
from functools import lru_cache
from typing import List, Dict, Optional, Tuple
from market_data import MarketDataProvider


class DataProcessor:
    """Enhanced data processing with market data integration"""
    
    def __init__(self, market_provider: MarketDataProvider):
        self.market_provider = market_provider

    @lru_cache(maxsize=128)
    def calculate_dividends(self, amount: float, stock_ticker: str, stock_name: str, 
                           stock_yield: float, stock_allocation: float, use_live_data: bool = False) -> Dict:
        """Calculate dividends with optional live market data"""
        allocated = amount * stock_allocation
        
        # Use live yield if available and requested
        final_yield = stock_yield
        current_price = None
        
        if use_live_data:
            # Try to get live dividend data
            dividend_data = self.market_provider.get_dividend_data(stock_ticker)
            if dividend_data and dividend_data['dividend_yield'] > 0:
                final_yield = dividend_data['dividend_yield']
            
            # Get current stock price
            quote_data = self.market_provider.get_stock_quote(stock_ticker)
            if quote_data:
                current_price = quote_data['price']
        
        annual_dividend = allocated * final_yield
        monthly_dividend = annual_dividend / 12
        
        return {
            "ticker": stock_ticker,
            "name": stock_name,
            "allocated": round(allocated, 2),
            "annual_dividend": round(annual_dividend, 2),
            "monthly_dividend": round(monthly_dividend, 2),
            "yield_percent": round(final_yield * 100, 2),
            "current_price": current_price,
            "is_live_data": use_live_data and (dividend_data is not None or quote_data is not None)
        }
    
    @staticmethod
    def process_csv_data(df: pd.DataFrame, mode: str) -> Tuple[pd.DataFrame, str]:
        """Process CSV data for chart generation"""
        if df.empty:
            raise ValueError("DataFrame is empty")
            
        required_cols = {"Timestamp", "Ticker", "Estimated Annual Dividend", "Monthly Dividend"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV missing required columns: {required_cols - set(df.columns)}")
        
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        y_col = "Estimated Annual Dividend" if mode == "Annual" else "Monthly Dividend"
        y_label = f"{mode} Dividend ($)"
        
        # Optimize grouping and pivoting
        grouped = df.groupby(["Timestamp", "Ticker"], as_index=False)[y_col].sum()
        pivoted = grouped.pivot(index="Timestamp", columns="Ticker", values=y_col).fillna(0)
        
        # Calculate cumulative sum for proper growth tracking
        pivoted_cumsum = pivoted.cumsum()
        pivoted_cumsum["Total"] = pivoted_cumsum.sum(axis=1)
        
        return pivoted_cumsum, y_label
    
    @staticmethod
    def calculate_portfolio_stats(df: pd.DataFrame) -> Dict:
        """Calculate portfolio statistics"""
        if df.empty:
            return {}
            
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        
        # Get unique total investments by timestamp (avoid double counting)
        unique_investments = df.groupby("Timestamp")["Total Investment"].first()
        total_invested = unique_investments.sum()
        
        # Get cumulative data for current portfolio
        latest_data = df.groupby("Ticker").last().reset_index()
        total_annual_dividend = latest_data["Estimated Annual Dividend"].sum()
        
        # Calculate weighted average yield
        total_amount_invested = latest_data["Amount Invested"].sum()
        avg_yield = (latest_data["Yield (%)"] * latest_data["Amount Invested"]).sum() / total_amount_invested if total_amount_invested > 0 else 0
        
        # Calculate investment frequency
        investment_count = len(unique_investments)
        date_range = (df["Timestamp"].max() - df["Timestamp"].min()).days
        investments_per_month = (investment_count / (date_range / 30.44)) if date_range > 0 else 0
        
        return {
            "total_invested": total_invested,
            "total_annual_dividend": total_annual_dividend,
            "avg_yield": avg_yield,
            "investment_count": investment_count,
            "investments_per_month": investments_per_month,
            "portfolio_yield": (total_annual_dividend / total_invested * 100) if total_invested > 0 else 0,
            "monthly_income": total_annual_dividend / 12
        }

    def get_portfolio_market_value(self, df: pd.DataFrame = None) -> Dict:
        """Calculate current market value of portfolio using portfolio manager data"""
        # Use portfolio manager's holdings instead of CSV data for more accuracy
        portfolio_manager = getattr(self, '_portfolio_manager', None)
        if not portfolio_manager:
            # Fallback to old CSV method if no portfolio manager available
            return self._get_portfolio_market_value_from_csv(df)
        
        holdings = portfolio_manager.portfolio_holdings
        if not holdings:
            return {"total_market_value": 0, "total_gain_loss": 0, "stocks": []}
        
        total_market_value = 0
        total_invested = 0
        stock_details = []
        
        print("[DATA] Calculating portfolio market value...")
        
        for holding in holdings:
            symbol = holding["symbol"]
            shares = holding["shares"]
            cost_basis = holding["total_cost"]
            avg_purchase_price = holding["purchase_price"]
            
            # Get current market price
            quote_data = self.market_provider.get_stock_quote(symbol)
            if quote_data and quote_data.get("price", 0) > 0:
                current_price = quote_data["price"]
                current_value = shares * current_price
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                stock_details.append({
                    "ticker": symbol,
                    "shares": shares,
                    "avg_purchase_price": avg_purchase_price,
                    "invested": cost_basis,
                    "current_price": current_price,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "gain_loss_percent": gain_loss_percent,
                    "change_percent": quote_data.get("change_percent", "0")
                })
                
                total_market_value += current_value
                total_invested += cost_basis
                
                print(f"  {symbol}: {shares:.3f} shares @ ${current_price:.2f} = ${current_value:.2f} (${gain_loss:+.2f})")
            else:
                print(f"  {symbol}: Could not get current price")
                # Use stored values if available
                current_value = holding.get("current_value", cost_basis)
                total_market_value += current_value
                total_invested += cost_basis
        
        total_gain_loss = total_market_value - total_invested
        
        result = {
            "total_market_value": total_market_value,
            "total_invested": total_invested,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": (total_gain_loss / total_invested * 100) if total_invested > 0 else 0,
            "stocks": stock_details
        }
        
        print(f"[CHART] Portfolio Summary: Invested ${total_invested:.2f}, Value ${total_market_value:.2f}, Gain/Loss ${total_gain_loss:+.2f}")
        return result
    
    def _get_portfolio_market_value_from_csv(self, df: pd.DataFrame) -> Dict:
        """Fallback method using CSV data (legacy)"""
        if df is None or df.empty:
            return {"total_market_value": 0, "total_gain_loss": 0, "stocks": []}
        
        # Get latest holdings for each ticker
        latest_holdings = df.groupby("Ticker").agg({
            "Amount Invested": "sum",
            "Company": "last"
        }).reset_index()
        
        total_market_value = 0
        total_invested = latest_holdings["Amount Invested"].sum()
        stock_details = []
        
        for _, row in latest_holdings.iterrows():
            ticker = row["Ticker"]
            invested = row["Amount Invested"]
            
            # Get current market data
            quote_data = self.market_provider.get_stock_quote(ticker)
            if quote_data:
                # Estimate shares owned (using average cost basis)
                estimated_shares = invested / quote_data["price"] if quote_data["price"] > 0 else 0
                current_value = estimated_shares * quote_data["price"]
                gain_loss = current_value - invested
                
                stock_details.append({
                    "ticker": ticker,
                    "invested": invested,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "current_price": quote_data["price"],
                    "change_percent": quote_data["change_percent"]
                })
                
                total_market_value += current_value
        
        return {
            "total_market_value": total_market_value,
            "total_invested": total_invested,
            "total_gain_loss": total_market_value - total_invested,
            "stocks": stock_details
        }