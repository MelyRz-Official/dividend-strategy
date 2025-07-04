# # -*- coding: utf-8 -*-
# """
# Main GUI application for the Dividend Strategy Calculator
# """

# import tkinter as tk
# from tkinter import ttk, messagebox
# import pandas as pd
# import sv_ttk
# import os
# from datetime import datetime
# from tkinter import StringVar
# from tkinter.ttk import Notebook
# import threading
# from concurrent.futures import ThreadPoolExecutor
# from typing import List, Dict, Optional

# # Import our custom modules
# from yahoo_finance_provider import YahooFinanceProvider
# from data_processor import DataProcessor
# from chart_generator import ChartGenerator
# from portfolio_manager import PortfolioManager
# from utils import (
#     open_plot_in_window, format_currency, format_percentage, 
#     validate_investment_amount, get_default_csv_path
# )

# # Import configuration
# try:
#     import config
#     DIVIDEND_STOCKS = config.DIVIDEND_STOCKS
#     CSV_FILENAME = config.CSV_FILENAME
# except ImportError:
#     # Fallback configuration
#     DIVIDEND_STOCKS = (
#         {"ticker": "O", "name": "Realty Income", "yield": 0.055, "allocation": 0.20},
#         {"ticker": "TROW", "name": "T. Rowe Price", "yield": 0.043, "allocation": 0.15},
#         {"ticker": "SCHD", "name": "SCHD", "yield": 0.038, "allocation": 0.15},
#         {"ticker": "HDV", "name": "HDV", "yield": 0.038, "allocation": 0.10},
#         {"ticker": "MO", "name": "Altria", "yield": 0.08, "allocation": 0.10},
#         {"ticker": "APLE", "name": "Apple Hospitality REIT", "yield": 0.06, "allocation": 0.10},
#         {"ticker": "ABBV", "name": "AbbVie", "yield": 0.04, "allocation": 0.10},
#         {"ticker": "VZ", "name": "Verizon", "yield": 0.066, "allocation": 0.10},
#     )
#     CSV_FILENAME = get_default_csv_path()


# class DividendApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("💸 Real-Time Dividend Strategy Calculator")
#         self.root.geometry("1700x900")
        
#         # Initialize market data provider and related components
#         self.market_provider = YahooFinanceProvider()
#         self.data_processor = DataProcessor(self.market_provider)
#         self.portfolio_manager = PortfolioManager(self.market_provider)
        
#         # Initialize data structures
#         self.data: List[Dict] = []
#         self.latest_investment: float = 0.0
#         self.total_dividend: float = 0.0
#         self._cached_csv_data: Optional[pd.DataFrame] = None
#         self._csv_last_modified: float = 0.0
#         self.use_live_data = tk.BooleanVar(value=False)
        
#         # Load portfolio holdings on startup
#         self.portfolio_manager.load_portfolio_holdings()
        
#         # Thread pool for background operations
#         self.executor = ThreadPoolExecutor(max_workers=3)
        
#         # Apply dark theme
#         sv_ttk.set_theme("dark")
#         self._setup_ui()

#     def _get_csv_data(self) -> Optional[pd.DataFrame]:
#         """Get CSV data with caching for better performance"""
#         if not os.path.exists(CSV_FILENAME):
#             return None
            
#         try:
#             current_modified = os.path.getmtime(CSV_FILENAME)
            
#             # Use cached data if file hasn't changed
#             if (self._cached_csv_data is not None and 
#                 current_modified == self._csv_last_modified):
#                 return self._cached_csv_data
            
#             # Load and cache new data
#             self._cached_csv_data = pd.read_csv(CSV_FILENAME)
#             self._csv_last_modified = current_modified
            
#             return self._cached_csv_data
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to load CSV data: {str(e)}")
#             return None

#     def _setup_ui(self):
#         """Initialize the enhanced user interface"""
#         # Main layout with better proportions
#         main_frame = ttk.Frame(self.root)
#         main_frame.pack(fill="both", expand=True, padx=10, pady=10)

#         left_panel = ttk.Frame(main_frame)
#         left_panel.pack(side="left", fill="y", expand=False, padx=(0, 15))

#         right_panel = ttk.Frame(main_frame)
#         right_panel.pack(side="right", fill="both", expand=True)

#         self._setup_left_panel(left_panel)
#         self._setup_right_panel(right_panel)

#     def _setup_left_panel(self, parent):
#         """Setup enhanced left panel with market data controls"""
#         # Market Data Status section
#         status_frame = ttk.LabelFrame(parent, text="[LAUNCH] Market Data Status", padding=10)
#         status_frame.pack(pady=(0, 10), fill="x")
        
#         # Status indicator
#         ttk.Label(status_frame, text="Provider:", font=("Segoe UI", 9)).pack(side="left")
#         ttk.Label(status_frame, text="Yahoo Finance (No limits!)", 
#                  font=("Segoe UI", 9, "bold"), foreground="green").pack(side="left", padx=(5, 0))
        
#         # Live data toggle
#         live_data_frame = ttk.Frame(status_frame)
#         live_data_frame.pack(fill="x", pady=(5, 0))
#         ttk.Checkbutton(live_data_frame, text="Use Live Market Data", 
#                        variable=self.use_live_data,
#                        command=self.on_live_data_toggle).pack(side="left")

#         # Input section
#         input_frame = ttk.LabelFrame(parent, text="[MONEY] Investment Calculator", padding=10)
#         input_frame.pack(pady=(0, 10), fill="x")
        
#         entry_frame = ttk.Frame(input_frame)
#         entry_frame.pack(fill="x")
#         ttk.Label(entry_frame, text="Amount ($):").pack(side="left", padx=(0, 5))
#         self.amount_entry = ttk.Entry(entry_frame, width=15)
#         self.amount_entry.pack(side="left", padx=(0, 5))
#         self.amount_entry.insert(0, "100.00")
#         self.amount_entry.bind("<Return>", lambda e: self.calculate())
#         ttk.Button(entry_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        
#         # Portfolio stats section (enhanced)
#         stats_frame = ttk.LabelFrame(parent, text="[DATA] Portfolio Statistics", padding=10)
#         stats_frame.pack(pady=(0, 10), fill="x")
        
#         self.stats_labels = {}
#         stats_info = [
#             ("total_invested", "Total Invested:"),
#             ("total_dividend", "Annual Dividend:"),
#             ("monthly_income", "Monthly Income:"),
#             ("avg_yield", "Portfolio Yield:"),
#             ("market_value", "Market Value:"),
#             ("total_gain_loss", "Total Gain/Loss:"),
#             ("investment_count", "Investments Made:")
#         ]
        
#         for key, label in stats_info:
#             frame = ttk.Frame(stats_frame)
#             frame.pack(fill="x", pady=2)
#             ttk.Label(frame, text=label).pack(side="left")
#             self.stats_labels[key] = ttk.Label(frame, text="$0.00", font=("Segoe UI", 9, "bold"))
#             self.stats_labels[key].pack(side="right")

#         # Current calculation results
#         calc_frame = ttk.LabelFrame(parent, text="[CALC] Current Calculation", padding=10)
#         calc_frame.pack(pady=(0, 10), fill="both", expand=True)

#         self.tree = ttk.Treeview(
#             calc_frame,
#             columns=("Ticker", "Amount", "Yield", "Monthly", "Annual", "Live"),
#             show="headings", height=8
#         )
#         headers = {
#             "Ticker": ("Ticker", 60),
#             "Amount": ("Allocation $", 90),
#             "Yield": ("Yield (%)", 70),
#             "Monthly": ("Monthly", 80),
#             "Annual": ("Annual", 80),
#             "Live": ("Live", 50)
#         }
#         for col, (label, width) in headers.items():
#             self.tree.heading(col, text=label)
#             self.tree.column(col, anchor="center", width=width)

#         self.tree.tag_configure("evenrow", background="#1e1e1e")
#         self.tree.tag_configure("oddrow", background="#2a2a2a")
#         self.tree.tag_configure("live_data", background="#1a4a1a")  # Green tint for live data
#         self.tree.pack(fill="both", expand=True, pady=(0, 10))

#         self.total_label = ttk.Label(calc_frame, text="", font=("Segoe UI", 10, "bold"))
#         self.total_label.pack()

#         # Action buttons
#         button_frame = ttk.Frame(calc_frame)
#         button_frame.pack(pady=(10, 0), fill="x")
#         ttk.Button(button_frame, text="[SAVE] Save to History", command=self.save_csv).pack(side="left", padx=(0, 5))
#         ttk.Button(button_frame, text="[REFRESH] Refresh Dashboard", command=self.refresh_dashboard).pack(side="left")

#     def _setup_right_panel(self, parent):
#         """Setup enhanced right panel with market data features"""
#         self.tab_notebook = Notebook(parent)
#         self.tab_notebook.pack(fill="both", expand=True)

#         # Growth Charts Tab
#         growth_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(growth_tab, text="[CHART] Growth Charts")

#         # View mode selector (auto-updates charts)
#         control_frame = ttk.Frame(growth_tab)
#         control_frame.pack(pady=10)
#         ttk.Label(control_frame, text="View Mode:").pack(side="left", padx=(0, 5))
#         self.view_mode = StringVar(value="Annual")
#         mode_combo = ttk.Combobox(
#             control_frame,
#             textvariable=self.view_mode,
#             values=["Annual", "Monthly"],
#             state="readonly", width=10
#         )
#         mode_combo.pack(side="left")
#         mode_combo.bind("<<ComboboxSelected>>", lambda e: self.generate_growth_tabs())

#         self.stock_tabs = Notebook(growth_tab)
#         self.stock_tabs.pack(fill="both", expand=True, pady=5)

#         # Portfolio Analysis Tab (Enhanced)
#         analysis_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(analysis_tab, text="[DATA] Portfolio Analysis")
        
#         analysis_buttons = ttk.Frame(analysis_tab)
#         analysis_buttons.pack(pady=20)
        
#         ttk.Button(analysis_buttons, text="[DATA] Allocation Pie Chart", 
#                   command=self.show_allocation_chart).pack(side="left", padx=5)
#         ttk.Button(analysis_buttons, text="[CHART] Yield Comparison (Live)", 
#                   command=self.show_yield_chart).pack(side="left", padx=5)
#         ttk.Button(analysis_buttons, text="[TIME] Investment Timeline", 
#                   command=self.show_timeline_chart).pack(side="left", padx=5)
#         ttk.Button(analysis_buttons, text="[MONEY] Portfolio Performance", 
#                   command=self.show_performance_chart).pack(side="left", padx=5)

#         # Market Data Tab (New)
#         market_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(market_tab, text="[WEB] Live Market Data")
        
#         # Market data display
#         market_info_frame = ttk.LabelFrame(market_tab, text="[DATA] Current Stock Prices", padding=10)
#         market_info_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
#         self.market_tree = ttk.Treeview(
#             market_info_frame,
#             columns=("Ticker", "Price", "Change", "Change%", "Yield", "ExDiv"),
#             show="headings", height=10
#         )
        
#         market_headers = {
#             "Ticker": ("Ticker", 80),
#             "Price": ("Price ($)", 100),
#             "Change": ("Change ($)", 100),
#             "Change%": ("Change (%)", 100),
#             "Yield": ("Div Yield (%)", 120),
#             "ExDiv": ("Ex-Div Date", 120)
#         }
        
#         for col, (label, width) in market_headers.items():
#             self.market_tree.heading(col, text=label)
#             self.market_tree.column(col, anchor="center", width=width)
        
#         self.market_tree.pack(fill="both", expand=True, pady=(0, 10))
        
#         market_button_frame = ttk.Frame(market_info_frame)
#         market_button_frame.pack(fill="x")
#         ttk.Button(market_button_frame, text="[REFRESH] Refresh Market Data", 
#                   command=self.refresh_market_data).pack(side="left", padx=5)
#         ttk.Button(market_button_frame, text="[LIST] Export Market Data", 
#                   command=self.export_market_data).pack(side="left", padx=5)

#         # Strategy Comparison Tab
#         comparison_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(comparison_tab, text="[TARGET] Strategy Comparison")
#         ttk.Button(comparison_tab, text="Open Strategy Comparison Chart", 
#                   command=self.show_comparison_chart).pack(pady=20)

#         # Initialize dashboard
#         self.refresh_dashboard()

#     def on_live_data_toggle(self):
#         """Handle live data toggle"""
#         if self.use_live_data.get():
#             messagebox.showinfo(
#                 "Live Data Enabled", 
#                 "[OK] Yahoo Finance live data enabled!\n\n"
#                 "✨ Unlimited requests - no rate limits!\n"
#                 "[DATA] Real-time stock prices and dividends\n"
#                 "[LAUNCH] Fast and reliable data\n\n"
#                 "Next calculation will use live market data."
#             )
#         else:
#             messagebox.showinfo("Live Data Disabled", 
#                               "Using static dividend yields from configuration.")
    
#     def update_api_key(self):
#         """This method is no longer needed with Yahoo Finance"""
#         messagebox.showinfo("Info", 
#                           "Yahoo Finance doesn't require an API key!\n"
#                           "Enjoy unlimited real-time data! [SUCCESS]")

#     def calculate(self):
#         """Enhanced calculation with optional live market data"""
#         try:
#             amount = validate_investment_amount(self.amount_entry.get())
#             self.latest_investment = amount
#             self.data.clear()
#             self.tree.delete(*self.tree.get_children())

#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             total_dividend = 0.0
            
#             # Show progress if using live data
#             progress_window = None
#             if self.use_live_data.get():
#                 progress_window = self._show_progress_window("Fetching live market data...")

#             def calculate_with_progress():
#                 try:
#                     # Process each stock
#                     for i, stock in enumerate(DIVIDEND_STOCKS):
#                         if progress_window:
#                             progress_text = f"Fetching data for {stock['ticker']}... ({i+1}/{len(DIVIDEND_STOCKS)})"
#                             self.root.after(0, lambda text=progress_text: self._update_progress(progress_window, text))
                        
#                         # Use enhanced calculation with optional live data
#                         calc_result = self.data_processor.calculate_dividends(
#                             amount, stock["ticker"], stock["name"], 
#                             stock["yield"], stock["allocation"], 
#                             use_live_data=self.use_live_data.get()
#                         )
                        
#                         # Update UI in main thread
#                         self.root.after(0, lambda result=calc_result, index=i: self._update_tree_row(result, index))
                        
#                         # Build data for CSV
#                         data_entry = {
#                             "Timestamp": timestamp,
#                             "Ticker": calc_result["ticker"],
#                             "Company": calc_result["name"],
#                             "Amount Invested": calc_result["allocated"],
#                             "Yield (%)": calc_result["yield_percent"],
#                             "Monthly Dividend": calc_result["monthly_dividend"],
#                             "Estimated Annual Dividend": calc_result["annual_dividend"],
#                             "Total Investment": amount,
#                             "Current Price": calc_result.get("current_price"),
#                             "Live Data": calc_result.get("is_live_data", False)
#                         }
#                         self.data.append(data_entry)
                        
#                         nonlocal total_dividend
#                         total_dividend += calc_result["annual_dividend"]
                    
#                     # Update total in main thread
#                     self.root.after(0, lambda: self._update_total_label(total_dividend))
                    
#                 finally:
#                     if progress_window:
#                         self.root.after(0, lambda: progress_window.destroy())

#             if self.use_live_data.get():
#                 # Run in background thread
#                 self.executor.submit(calculate_with_progress)
#             else:
#                 # Run synchronously for static data
#                 calculate_with_progress()

#         except ValueError as e:
#             messagebox.showerror("Invalid Input", str(e))

#     def _show_progress_window(self, initial_text: str):
#         """Show progress window for long operations"""
#         progress_window = tk.Toplevel(self.root)
#         progress_window.title("Loading...")
#         progress_window.geometry("300x100")
#         progress_window.transient(self.root)
#         progress_window.grab_set()
        
#         # Center the window
#         progress_window.geometry("+{}+{}".format(
#             self.root.winfo_rootx() + 50,
#             self.root.winfo_rooty() + 50
#         ))
        
#         ttk.Label(progress_window, text="Loading Market Data", font=("Segoe UI", 12, "bold")).pack(pady=10)
#         progress_window.progress_label = ttk.Label(progress_window, text=initial_text)
#         progress_window.progress_label.pack(pady=5)
        
#         progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
#         progress_bar.pack(pady=10, padx=20, fill="x")
#         progress_bar.start()
        
#         return progress_window

#     def _update_progress(self, progress_window, text: str):
#         """Update progress window text"""
#         if progress_window and hasattr(progress_window, 'progress_label'):
#             progress_window.progress_label.config(text=text)

#     def _update_tree_row(self, calc_result: Dict, index: int):
#         """Update tree view with calculation result"""
#         tag = "evenrow" if index % 2 == 0 else "oddrow"
#         if calc_result.get("is_live_data"):
#             tag = "live_data"
        
#         live_indicator = "[OK]" if calc_result.get("is_live_data") else "[ERROR]"
        
#         self.tree.insert("", "end", values=(
#             calc_result["ticker"],
#             format_currency(calc_result['allocated']),
#             format_percentage(calc_result['yield_percent']),
#             format_currency(calc_result['monthly_dividend']),
#             format_currency(calc_result['annual_dividend']),
#             live_indicator
#         ), tags=(tag,))

#     def _update_total_label(self, total_dividend: float):
#         """Update total dividend label"""
#         self.total_dividend = total_dividend
#         self.total_label.config(text=f"Total Estimated Annual Dividend: {format_currency(total_dividend)}")

#     def save_csv(self):
#         """Enhanced save with automatic portfolio tracking using live market data"""
#         try:
#             if not self.data:
#                 messagebox.showwarning("No Data", "Please calculate first before saving.")
#                 return
            
#             df = pd.DataFrame(self.data)
            
#             # Ensure directory exists
#             os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)
            
#             file_exists = os.path.exists(CSV_FILENAME)
#             df.to_csv(CSV_FILENAME, mode='a', header=not file_exists, index=False)
            
#             # Update portfolio holdings automatically
#             success = self.portfolio_manager.update_portfolio_from_calculation(
#                 self.data, self.use_live_data.get()
#             )
            
#             # Clear cache and refresh dashboard
#             self._cached_csv_data = None
#             self.refresh_dashboard()
            
#             if success:
#                 messagebox.showinfo("Saved", 
#                     f"Investment data saved to CSV\n"
#                     f"Portfolio holdings updated automatically\n"
#                     f"Total invested: {format_currency(self.portfolio_manager.total_invested_from_holdings)}")
#             else:
#                 messagebox.showinfo("Saved", 
#                     f"Investment data saved to CSV\n"
#                     f"Portfolio update had some issues (check console)")
                
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def refresh_dashboard(self):
#         """Enhanced dashboard refresh with market data"""
#         df = self._get_csv_data()
#         if df is not None and not df.empty:
#             stats = DataProcessor.calculate_portfolio_stats(df)
            
#             # Get market data if live data is enabled
#             if self.use_live_data.get():
#                 def update_with_market_data():
#                     try:
#                         market_data = self.data_processor.get_portfolio_market_value(df)
#                         stats.update({
#                             "market_value": market_data.get("total_market_value", 0),
#                             "total_gain_loss": market_data.get("total_gain_loss", 0)
#                         })
#                         self.root.after(0, lambda: self._update_stats_display(stats))
#                     except Exception as e:
#                         print(f"Error fetching market data: {e}")
#                         self.root.after(0, lambda: self._update_stats_display(stats))
                
#                 self.executor.submit(update_with_market_data)
#             else:
#                 self._update_stats_display(stats)
            
#             self.generate_growth_tabs()
#         else:
#             # Clear stats if no data
#             for key, label in self.stats_labels.items():
#                 if key in ["market_value", "total_gain_loss"]:
#                     label.config(text="Enable Live Data")
#                 else:
#                     label.config(text="$0.00")

#     def _update_stats_display(self, stats: Dict):
#         """Enhanced stats display with portfolio data"""
#         if not stats:
#             return
        
#         # Use portfolio holdings total if available
#         if hasattr(self.portfolio_manager, 'total_invested_from_holdings') and self.portfolio_manager.total_invested_from_holdings > 0:
#             total_invested = self.portfolio_manager.total_invested_from_holdings
#         else:
#             total_invested = stats.get('total_invested', 0)
            
#         self.stats_labels["total_invested"].config(text=format_currency(total_invested))
#         self.stats_labels["total_dividend"].config(text=format_currency(stats.get('total_annual_dividend', 0)))
#         self.stats_labels["monthly_income"].config(text=format_currency(stats.get('monthly_income', 0)))
#         self.stats_labels["avg_yield"].config(text=format_percentage(stats.get('portfolio_yield', 0)))
#         self.stats_labels["investment_count"].config(text=f"{stats.get('investment_count', 0)}")
        
#         # Market data (if available)
#         market_value = stats.get('market_value', 0)
#         total_gain_loss = stats.get('total_gain_loss', 0)
        
#         if market_value > 0:
#             self.stats_labels["market_value"].config(text=format_currency(market_value))
#             color = "green" if total_gain_loss >= 0 else "red"
#             self.stats_labels["total_gain_loss"].config(
#                 text=format_currency(total_gain_loss, show_sign=True),
#                 foreground=color
#             )
#         else:
#             self.stats_labels["market_value"].config(text="Enable Live Data")
#             self.stats_labels["total_gain_loss"].config(text="Enable Live Data")

#     def refresh_market_data(self):
#         """Refresh live market data display"""
#         def fetch_market_data():
#             try:
#                 # Clear existing data
#                 self.root.after(0, lambda: self.market_tree.delete(*self.market_tree.get_children()))
                
#                 for i, stock in enumerate(DIVIDEND_STOCKS):
#                     ticker = stock["ticker"]
                    
#                     # Get quote data
#                     quote_data = self.market_provider.get_stock_quote(ticker)
#                     dividend_data = self.market_provider.get_dividend_data(ticker)
#                     overview_data = self.market_provider.get_company_overview(ticker)
                    
#                     # Prepare row data
#                     price = quote_data.get("price", 0) if quote_data else 0
#                     change = quote_data.get("change", 0) if quote_data else 0
#                     change_percent = quote_data.get("change_percent", "0") if quote_data else "0"
#                     div_yield = dividend_data.get("dividend_yield", 0) * 100 if dividend_data else stock["yield"] * 100
#                     ex_div_date = overview_data.get("ex_dividend_date", "N/A") if overview_data else "N/A"
                    
#                     row_data = (
#                         ticker,
#                         format_currency(price) if price > 0 else "N/A",
#                         format_currency(change, show_sign=True) if change != 0 else "N/A",
#                         f"{change_percent}%" if change_percent != "0" else "N/A",
#                         format_percentage(div_yield) if div_yield > 0 else "N/A",
#                         ex_div_date
#                     )
                    
#                     # Update in main thread
#                     tag = "evenrow" if i % 2 == 0 else "oddrow"
#                     self.root.after(0, lambda data=row_data, t=tag: self.market_tree.insert("", "end", values=data, tags=(t,)))
                
#                 self.root.after(0, lambda: messagebox.showinfo("Success", "Market data refreshed!"))
                
#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh market data: {str(e)}"))

#         # Show progress and run in background
#         progress_window = self._show_progress_window("Refreshing market data...")
        
#         def run_with_progress():
#             try:
#                 fetch_market_data()
#             finally:
#                 if progress_window:
#                     self.root.after(0, lambda: progress_window.destroy())
        
#         self.executor.submit(run_with_progress)

#     def export_market_data(self):
#         """Export current market data to CSV"""
#         try:
#             market_data = []
#             for item in self.market_tree.get_children():
#                 values = self.market_tree.item(item)["values"]
#                 market_data.append({
#                     "Ticker": values[0],
#                     "Price": values[1],
#                     "Change": values[2],
#                     "Change%": values[3],
#                     "Dividend Yield": values[4],
#                     "Ex-Dividend Date": values[5],
#                     "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 })
            
#             if market_data:
#                 df = pd.DataFrame(market_data)
#                 filename = os.path.join(os.path.expanduser("~"), "Documents", "market_data_export.csv")
#                 df.to_csv(filename, index=False)
#                 messagebox.showinfo("Exported", f"Market data exported to {filename}")
#             else:
#                 messagebox.showwarning("No Data", "No market data to export. Refresh data first.")
                
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to export data: {str(e)}")

#     # Chart methods
#     def show_allocation_chart(self):
#         """Show portfolio allocation pie chart"""
#         stats = {}  # We don't need stats for allocation chart
#         fig = ChartGenerator.create_allocation_pie_chart(stats)
#         open_plot_in_window(fig, "Portfolio Allocation")

#     def show_yield_chart(self):
#         """Show enhanced yield comparison chart with live data"""
#         def generate_chart():
#             try:
#                 fig = ChartGenerator.create_yield_comparison_chart(self.market_provider)
#                 self.root.after(0, lambda: open_plot_in_window(fig, "Yield Comparison"))
#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
#         self.executor.submit(generate_chart)

#     def show_timeline_chart(self):
#         """Show investment timeline chart"""
#         df = self._get_csv_data()
#         if df is not None and not df.empty:
#             fig = ChartGenerator.create_investment_timeline(df)
#             open_plot_in_window(fig, "Investment Timeline")
#         else:
#             messagebox.showwarning("No Data", "No investment history found.")

#     def show_performance_chart(self):
#         """Show portfolio performance chart with gains/losses"""
#         def generate_chart():
#             try:
#                 df = self._get_csv_data()
#                 if df is None or df.empty:
#                     self.root.after(0, lambda: messagebox.showwarning("No Data", "No investment history found."))
#                     return
                
#                 market_data = self.data_processor.get_portfolio_market_value(df)
#                 if not market_data.get("stocks"):
#                     self.root.after(0, lambda: messagebox.showwarning("No Data", "Unable to fetch current market values."))
#                     return
                
#                 fig = ChartGenerator.create_portfolio_performance_chart(market_data)
#                 self.root.after(0, lambda: open_plot_in_window(fig, "Portfolio Performance"))
                
#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
#         self.executor.submit(generate_chart)

#     def show_comparison_chart(self):
#         """Show strategy comparison chart using plotly offline"""
#         def _generate_chart():
#             try:
#                 df = self._get_csv_data()
#                 if df is None:
#                     self.root.after(0, lambda: messagebox.showwarning("No History", f"No file found: {CSV_FILENAME}"))
#                     return

#                 if not {"Timestamp", "Amount Invested"}.issubset(df.columns):
#                     self.root.after(0, lambda: messagebox.showerror("Data Error", "CSV missing required columns."))
#                     return

#                 df["Timestamp"] = pd.to_datetime(df["Timestamp"])
#                 df["Year"] = df["Timestamp"].dt.year

#                 # Group by year efficiently
#                 actual_invest = df.groupby("Year")["Amount Invested"].sum().reset_index()

#                 # Strategy data
#                 strategy_years = list(range(1, 11))
#                 portfolio_22k = [22500, 47500, 71700, 98600, 127270, 157400, 192800, 228400, 264200, 300800]
#                 portfolio_30k = [30600, 64300, 99600, 136800, 177800, 221400, 267600, 315600, 365400, 429700]

#                 import plotly.graph_objects as go
#                 fig = go.Figure()

#                 # Strategy lines
#                 fig.add_trace(go.Scatter(
#                     x=strategy_years, y=portfolio_22k,
#                     name="Portfolio (22K/yr)", mode="lines+markers", yaxis="y2"
#                 ))
#                 fig.add_trace(go.Scatter(
#                     x=strategy_years, y=portfolio_30k,
#                     name="Portfolio (30K/yr)", mode="lines+markers", yaxis="y2"
#                 ))

#                 # Add actual data if available
#                 if not actual_invest.empty:
#                     actual_years = actual_invest["Year"] - actual_invest["Year"].min() + 1
#                     fig.add_trace(go.Scatter(
#                         x=actual_years,
#                         y=actual_invest["Amount Invested"],
#                         name="Actual Portfolio Value",
#                         mode="lines+markers",
#                         yaxis="y2"
#                     ))

#                 fig.update_layout(
#                     title="[DATA] Strategy Comparison: Portfolio Value",
#                     xaxis_title="Year (Relative)",
#                     yaxis=dict(title="(unused)", visible=False),
#                     yaxis2=dict(title="Portfolio Value ($)", overlaying="y", side="right"),
#                     legend=dict(x=0.01, y=0.99),
#                     template="plotly_dark"
#                 )

#                 # Show chart using plotly offline + webview approach
#                 self.root.after(0, lambda: open_plot_in_window(fig, "Strategy Comparison"))

#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

#         # Run in background thread
#         self.executor.submit(_generate_chart)

#     def generate_growth_tabs(self):
#         """Generate growth tabs with optimized data processing"""
#         def _generate_tabs():
#             try:
#                 df = self._get_csv_data()
#                 if df is None or df.empty:
#                     return

#                 mode = self.view_mode.get()
#                 pivoted_cumsum, y_label = DataProcessor.process_csv_data(df, mode)

#                 # Update UI in main thread
#                 self.root.after(0, lambda: self._update_growth_tabs(pivoted_cumsum, mode, y_label))

#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

#         # Run in background thread
#         self.executor.submit(_generate_tabs)

#     def _update_growth_tabs(self, pivoted_cumsum: pd.DataFrame, mode: str, y_label: str):
#         """Update growth tabs in main thread"""
#         try:
#             # Clear existing tabs
#             for tab_id in self.stock_tabs.tabs():
#                 self.stock_tabs.forget(tab_id)

#             # Create total overview tab
#             tab_total = ttk.Frame(self.stock_tabs)
#             self.stock_tabs.add(tab_total, text="[DATA] All Stocks + Total")

#             fig_total = ChartGenerator.create_growth_chart(pivoted_cumsum, mode, y_label)
#             ttk.Button(
#                 tab_total, 
#                 text="Open Interactive Chart", 
#                 command=lambda: open_plot_in_window(fig_total, f"Cumulative {mode} Growth")
#             ).pack(pady=20)

#             # Create individual stock tabs
#             for ticker in pivoted_cumsum.columns[:-1]:  # Exclude 'Total'
#                 tab = ttk.Frame(self.stock_tabs)
#                 self.stock_tabs.add(tab, text=ticker)

#                 fig = ChartGenerator.create_individual_chart(pivoted_cumsum, ticker, mode, y_label)
#                 ttk.Button(
#                     tab, 
#                     text="Open Interactive Chart", 
#                     command=lambda f=fig, t=ticker: open_plot_in_window(f, f"{t} Growth")
#                 ).pack(pady=20)

#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to update tabs: {str(e)}")

#     def __del__(self):
#         """Cleanup resources"""
#         if hasattr(self, 'executor'):
#             self.executor.shutdown(wait=False)


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = DividendApp(root)
#     root.mainloop()

# -*- coding: utf-8 -*-
"""
Main GUI application for the Dividend Strategy Calculator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sv_ttk
import os
from datetime import datetime
from tkinter import StringVar
from tkinter.ttk import Notebook
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

# Import our custom modules
from yahoo_finance_provider import YahooFinanceProvider
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from portfolio_manager import PortfolioManager
from utils import (
    open_plot_in_window, format_currency, format_percentage, 
    validate_investment_amount, get_default_csv_path
)

# Import configuration
try:
    import config
    DIVIDEND_STOCKS = config.DIVIDEND_STOCKS
    CSV_FILENAME = config.CSV_FILENAME
except ImportError:
    # Fallback configuration
    DIVIDEND_STOCKS = (
        {"ticker": "O", "name": "Realty Income", "yield": 0.055, "allocation": 0.20},
        {"ticker": "TROW", "name": "T. Rowe Price", "yield": 0.043, "allocation": 0.15},
        {"ticker": "SCHD", "name": "SCHD", "yield": 0.038, "allocation": 0.15},
        {"ticker": "HDV", "name": "HDV", "yield": 0.038, "allocation": 0.10},
        {"ticker": "MO", "name": "Altria", "yield": 0.08, "allocation": 0.10},
        {"ticker": "APLE", "name": "Apple Hospitality REIT", "yield": 0.06, "allocation": 0.10},
        {"ticker": "ABBV", "name": "AbbVie", "yield": 0.04, "allocation": 0.10},
        {"ticker": "VZ", "name": "Verizon", "yield": 0.066, "allocation": 0.10},
    )
    CSV_FILENAME = get_default_csv_path()


class DividendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Real-Time Dividend Strategy Calculator")
        self.root.geometry("1700x900")
        
        # Initialize market data provider and related components
        self.market_provider = YahooFinanceProvider()
        self.data_processor = DataProcessor(self.market_provider)
        self.portfolio_manager = PortfolioManager(self.market_provider)
        
        # Link portfolio manager to data processor for better market value calculations
        self.data_processor._portfolio_manager = self.portfolio_manager
        
        # Initialize data structures
        self.data: List[Dict] = []
        self.latest_investment: float = 0.0
        self.total_dividend: float = 0.0
        self._cached_csv_data: Optional[pd.DataFrame] = None
        self._csv_last_modified: float = 0.0
        self.use_live_data = tk.BooleanVar(value=False)
        
        # Load portfolio holdings on startup
        self.portfolio_manager.load_portfolio_holdings()
        
        # Thread pool for background operations
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Apply dark theme
        sv_ttk.set_theme("dark")
        self._setup_ui()

    def _get_csv_data(self) -> Optional[pd.DataFrame]:
        """Get CSV data with caching for better performance"""
        if not os.path.exists(CSV_FILENAME):
            return None
            
        try:
            current_modified = os.path.getmtime(CSV_FILENAME)
            
            # Use cached data if file hasn't changed
            if (self._cached_csv_data is not None and 
                current_modified == self._csv_last_modified):
                return self._cached_csv_data
            
            # Load and cache new data
            self._cached_csv_data = pd.read_csv(CSV_FILENAME)
            self._csv_last_modified = current_modified
            
            return self._cached_csv_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV data: {str(e)}")
            return None

    def _setup_ui(self):
        """Initialize the enhanced user interface"""
        # Main layout with better proportions
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="y", expand=False, padx=(0, 15))

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        self._setup_left_panel(left_panel)
        self._setup_right_panel(right_panel)

    def _setup_left_panel(self, parent):
        """Setup enhanced left panel with market data controls"""
        # Market Data Status section
        status_frame = ttk.LabelFrame(parent, text="[LAUNCH] Market Data Status", padding=10)
        status_frame.pack(pady=(0, 10), fill="x")
        
        # Status indicator
        ttk.Label(status_frame, text="Provider:", font=("Segoe UI", 9)).pack(side="left")
        ttk.Label(status_frame, text="Yahoo Finance (No limits!)", 
                 font=("Segoe UI", 9, "bold"), foreground="green").pack(side="left", padx=(5, 0))
        
        # Live data toggle
        live_data_frame = ttk.Frame(status_frame)
        live_data_frame.pack(fill="x", pady=(5, 0))
        ttk.Checkbutton(live_data_frame, text="Use Live Market Data", 
                       variable=self.use_live_data,
                       command=self.on_live_data_toggle).pack(side="left")

        # Input section
        input_frame = ttk.LabelFrame(parent, text="[MONEY] Investment Calculator", padding=10)
        input_frame.pack(pady=(0, 10), fill="x")
        
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill="x")
        ttk.Label(entry_frame, text="Amount ($):").pack(side="left", padx=(0, 5))
        self.amount_entry = ttk.Entry(entry_frame, width=15)
        self.amount_entry.pack(side="left", padx=(0, 5))
        self.amount_entry.insert(0, "100.00")
        self.amount_entry.bind("<Return>", lambda e: self.calculate())
        ttk.Button(entry_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        
        # Portfolio stats section (enhanced)
        stats_frame = ttk.LabelFrame(parent, text="[DATA] Portfolio Statistics", padding=10)
        stats_frame.pack(pady=(0, 10), fill="x")
        
        self.stats_labels = {}
        stats_info = [
            ("total_invested", "Total Invested:"),
            ("total_dividend", "Annual Dividend:"),
            ("monthly_income", "Monthly Income:"),
            ("avg_yield", "Portfolio Yield:"),
            ("market_value", "Market Value:"),
            ("total_gain_loss", "Total Gain/Loss:"),
            ("investment_count", "Investments Made:")
        ]
        
        for key, label in stats_info:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=label).pack(side="left")
            self.stats_labels[key] = ttk.Label(frame, text="$0.00", font=("Segoe UI", 9, "bold"))
            self.stats_labels[key].pack(side="right")

        # Current calculation results
        calc_frame = ttk.LabelFrame(parent, text="[CALC] Current Calculation", padding=10)
        calc_frame.pack(pady=(0, 10), fill="both", expand=True)

        self.tree = ttk.Treeview(
            calc_frame,
            columns=("Ticker", "Amount", "Yield", "Monthly", "Annual", "Live"),
            show="headings", height=8
        )
        headers = {
            "Ticker": ("Ticker", 60),
            "Amount": ("Allocation $", 90),
            "Yield": ("Yield (%)", 70),
            "Monthly": ("Monthly", 80),
            "Annual": ("Annual", 80),
            "Live": ("Live", 50)
        }
        for col, (label, width) in headers.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, anchor="center", width=width)

        self.tree.tag_configure("evenrow", background="#1e1e1e")
        self.tree.tag_configure("oddrow", background="#2a2a2a")
        self.tree.tag_configure("live_data", background="#1a4a1a")  # Green tint for live data
        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        self.total_label = ttk.Label(calc_frame, text="", font=("Segoe UI", 10, "bold"))
        self.total_label.pack()

        # Action buttons
        button_frame = ttk.Frame(calc_frame)
        button_frame.pack(pady=(10, 0), fill="x")
        ttk.Button(button_frame, text="[SAVE] Save to History", command=self.save_csv).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="[REFRESH] Refresh Dashboard", command=self.refresh_dashboard).pack(side="left")

    def _setup_right_panel(self, parent):
        """Setup enhanced right panel with market data features"""
        self.tab_notebook = Notebook(parent)
        self.tab_notebook.pack(fill="both", expand=True)

        # Growth Charts Tab
        growth_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(growth_tab, text="[CHART] Growth Charts")

        # View mode selector (auto-updates charts)
        control_frame = ttk.Frame(growth_tab)
        control_frame.pack(pady=10)
        ttk.Label(control_frame, text="View Mode:").pack(side="left", padx=(0, 5))
        self.view_mode = StringVar(value="Annual")
        mode_combo = ttk.Combobox(
            control_frame,
            textvariable=self.view_mode,
            values=["Annual", "Monthly"],
            state="readonly", width=10
        )
        mode_combo.pack(side="left")
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self.generate_growth_tabs())

        self.stock_tabs = Notebook(growth_tab)
        self.stock_tabs.pack(fill="both", expand=True, pady=5)

        # Portfolio Analysis Tab (Enhanced)
        analysis_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(analysis_tab, text="[DATA] Portfolio Analysis")
        
        analysis_buttons = ttk.Frame(analysis_tab)
        analysis_buttons.pack(pady=20)
        
        ttk.Button(analysis_buttons, text="[DATA] Allocation Pie Chart", 
                  command=self.show_allocation_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="[CHART] Yield Comparison (Live)", 
                  command=self.show_yield_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="[TIME] Investment Timeline", 
                  command=self.show_timeline_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="[MONEY] Portfolio Performance", 
                  command=self.show_performance_chart).pack(side="left", padx=5)

        # Market Data Tab (New)
        market_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(market_tab, text="[WEB] Live Market Data")
        
        # Market data display
        market_info_frame = ttk.LabelFrame(market_tab, text="[DATA] Current Stock Prices", padding=10)
        market_info_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.market_tree = ttk.Treeview(
            market_info_frame,
            columns=("Ticker", "Price", "Change", "Change%", "Yield", "ExDiv"),
            show="headings", height=10
        )
        
        market_headers = {
            "Ticker": ("Ticker", 80),
            "Price": ("Price ($)", 100),
            "Change": ("Change ($)", 100),
            "Change%": ("Change (%)", 100),
            "Yield": ("Div Yield (%)", 120),
            "ExDiv": ("Ex-Div Date", 120)
        }
        
        for col, (label, width) in market_headers.items():
            self.market_tree.heading(col, text=label)
            self.market_tree.column(col, anchor="center", width=width)
        
        self.market_tree.pack(fill="both", expand=True, pady=(0, 10))
        
        market_button_frame = ttk.Frame(market_info_frame)
        market_button_frame.pack(fill="x")
        ttk.Button(market_button_frame, text="[REFRESH] Refresh Market Data", 
                  command=self.refresh_market_data).pack(side="left", padx=5)
        ttk.Button(market_button_frame, text="[LIST] Export Market Data", 
                  command=self.export_market_data).pack(side="left", padx=5)

        # Strategy Comparison Tab
        comparison_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(comparison_tab, text="[TARGET] Strategy Comparison")
        ttk.Button(comparison_tab, text="Open Strategy Comparison Chart", 
                  command=self.show_comparison_chart).pack(pady=20)

        # Initialize dashboard
        self.refresh_dashboard()

    def on_live_data_toggle(self):
        """Handle live data toggle"""
        if self.use_live_data.get():
            messagebox.showinfo(
                "Live Data Enabled", 
                "[OK] Yahoo Finance live data enabled!\n\n"
                "✨ Unlimited requests - no rate limits!\n"
                "[DATA] Real-time stock prices and dividends\n"
                "[LAUNCH] Fast and reliable data\n\n"
                "Next calculation will use live market data."
            )
        else:
            messagebox.showinfo("Live Data Disabled", 
                              "Using static dividend yields from configuration.")
    
    def update_api_key(self):
        """This method is no longer needed with Yahoo Finance"""
        messagebox.showinfo("Info", 
                          "Yahoo Finance doesn't require an API key!\n"
                          "Enjoy unlimited real-time data! [SUCCESS]")

    def calculate(self):
        """Enhanced calculation with optional live market data"""
        try:
            amount = validate_investment_amount(self.amount_entry.get())
            self.latest_investment = amount
            self.data.clear()
            self.tree.delete(*self.tree.get_children())

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_dividend = 0.0
            
            # Show progress if using live data
            progress_window = None
            if self.use_live_data.get():
                progress_window = self._show_progress_window("Fetching live market data...")

            def calculate_with_progress():
                try:
                    # Process each stock
                    for i, stock in enumerate(DIVIDEND_STOCKS):
                        if progress_window:
                            progress_text = f"Fetching data for {stock['ticker']}... ({i+1}/{len(DIVIDEND_STOCKS)})"
                            self.root.after(0, lambda text=progress_text: self._update_progress(progress_window, text))
                        
                        # Use enhanced calculation with optional live data
                        calc_result = self.data_processor.calculate_dividends(
                            amount, stock["ticker"], stock["name"], 
                            stock["yield"], stock["allocation"], 
                            use_live_data=self.use_live_data.get()
                        )
                        
                        # Update UI in main thread
                        self.root.after(0, lambda result=calc_result, index=i: self._update_tree_row(result, index))
                        
                        # Build data for CSV
                        data_entry = {
                            "Timestamp": timestamp,
                            "Ticker": calc_result["ticker"],
                            "Company": calc_result["name"],
                            "Amount Invested": calc_result["allocated"],
                            "Yield (%)": calc_result["yield_percent"],
                            "Monthly Dividend": calc_result["monthly_dividend"],
                            "Estimated Annual Dividend": calc_result["annual_dividend"],
                            "Total Investment": amount,
                            "Current Price": calc_result.get("current_price"),
                            "Live Data": calc_result.get("is_live_data", False)
                        }
                        self.data.append(data_entry)
                        
                        nonlocal total_dividend
                        total_dividend += calc_result["annual_dividend"]
                    
                    # Update total in main thread
                    self.root.after(0, lambda: self._update_total_label(total_dividend))
                    
                finally:
                    if progress_window:
                        self.root.after(0, lambda: progress_window.destroy())

            if self.use_live_data.get():
                # Run in background thread
                self.executor.submit(calculate_with_progress)
            else:
                # Run synchronously for static data
                calculate_with_progress()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def _show_progress_window(self, initial_text: str):
        """Show progress window for long operations"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Loading...")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center the window
        progress_window.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        ttk.Label(progress_window, text="Loading Market Data", font=("Segoe UI", 12, "bold")).pack(pady=10)
        progress_window.progress_label = ttk.Label(progress_window, text=initial_text)
        progress_window.progress_label.pack(pady=5)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill="x")
        progress_bar.start()
        
        return progress_window

    def _update_progress(self, progress_window, text: str):
        """Update progress window text"""
        if progress_window and hasattr(progress_window, 'progress_label'):
            progress_window.progress_label.config(text=text)

    def _update_tree_row(self, calc_result: Dict, index: int):
        """Update tree view with calculation result"""
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        if calc_result.get("is_live_data"):
            tag = "live_data"
        
        live_indicator = "[OK]" if calc_result.get("is_live_data") else "[ERROR]"
        
        self.tree.insert("", "end", values=(
            calc_result["ticker"],
            format_currency(calc_result['allocated']),
            format_percentage(calc_result['yield_percent']),
            format_currency(calc_result['monthly_dividend']),
            format_currency(calc_result['annual_dividend']),
            live_indicator
        ), tags=(tag,))

    def _update_total_label(self, total_dividend: float):
        """Update total dividend label"""
        self.total_dividend = total_dividend
        self.total_label.config(text=f"Total Estimated Annual Dividend: {format_currency(total_dividend)}")

    def save_csv(self):
        """Enhanced save with automatic portfolio tracking using live market data"""
        try:
            if not self.data:
                messagebox.showwarning("No Data", "Please calculate first before saving.")
                return
            
            df = pd.DataFrame(self.data)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)
            
            file_exists = os.path.exists(CSV_FILENAME)
            df.to_csv(CSV_FILENAME, mode='a', header=not file_exists, index=False)
            
            # Update portfolio holdings automatically
            success = self.portfolio_manager.update_portfolio_from_calculation(
                self.data, self.use_live_data.get()
            )
            
            # Clear cache and refresh dashboard
            self._cached_csv_data = None
            self.refresh_dashboard()
            
            if success:
                messagebox.showinfo("Saved", 
                    f"Investment data saved to CSV\n"
                    f"Portfolio holdings updated automatically\n"
                    f"Total invested: {format_currency(self.portfolio_manager.total_invested_from_holdings)}")
            else:
                messagebox.showinfo("Saved", 
                    f"Investment data saved to CSV\n"
                    f"Portfolio update had some issues (check console)")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_dashboard(self):
        """Enhanced dashboard refresh with market data"""
        df = self._get_csv_data()
        if df is not None and not df.empty:
            stats = DataProcessor.calculate_portfolio_stats(df)
            
            # Get market data if live data is enabled
            if self.use_live_data.get():
                def update_with_market_data():
                    try:
                        # Use the enhanced market value calculation
                        market_data = self.data_processor.get_portfolio_market_value()
                        stats.update({
                            "market_value": market_data.get("total_market_value", 0),
                            "total_gain_loss": market_data.get("total_gain_loss", 0),
                            "total_gain_loss_percent": market_data.get("total_gain_loss_percent", 0)
                        })
                        self.root.after(0, lambda: self._update_stats_display(stats))
                    except Exception as e:
                        print(f"Error fetching market data: {e}")
                        self.root.after(0, lambda: self._update_stats_display(stats))
                
                self.executor.submit(update_with_market_data)
            else:
                self._update_stats_display(stats)
            
            self.generate_growth_tabs()
        else:
            # Clear stats if no data
            for key, label in self.stats_labels.items():
                if key in ["market_value", "total_gain_loss"]:
                    label.config(text="Enable Live Data")
                else:
                    label.config(text="$0.00")

    def _update_stats_display(self, stats: Dict):
        """Enhanced stats display with portfolio data"""
        if not stats:
            return
        
        # Use portfolio holdings total if available
        if hasattr(self.portfolio_manager, 'total_invested_from_holdings') and self.portfolio_manager.total_invested_from_holdings > 0:
            total_invested = self.portfolio_manager.total_invested_from_holdings
        else:
            total_invested = stats.get('total_invested', 0)
            
        self.stats_labels["total_invested"].config(text=format_currency(total_invested))
        self.stats_labels["total_dividend"].config(text=format_currency(stats.get('total_annual_dividend', 0)))
        self.stats_labels["monthly_income"].config(text=format_currency(stats.get('monthly_income', 0)))
        self.stats_labels["avg_yield"].config(text=format_percentage(stats.get('portfolio_yield', 0)))
        self.stats_labels["investment_count"].config(text=f"{stats.get('investment_count', 0)}")
        
        # Market data (if available)
        market_value = stats.get('market_value', 0)
        total_gain_loss = stats.get('total_gain_loss', 0)
        gain_loss_percent = stats.get('total_gain_loss_percent', 0)
        
        if market_value > 0:
            self.stats_labels["market_value"].config(text=format_currency(market_value))
            color = "green" if total_gain_loss >= 0 else "red"
            gain_loss_text = f"{format_currency(total_gain_loss, show_sign=True)} ({gain_loss_percent:+.2f}%)"
            self.stats_labels["total_gain_loss"].config(
                text=gain_loss_text,
                foreground=color
            )
        else:
            self.stats_labels["market_value"].config(text="Enable Live Data")
            self.stats_labels["total_gain_loss"].config(text="Enable Live Data")

    def refresh_market_data(self):
        """Refresh live market data display"""
        def fetch_market_data():
            try:
                # Clear existing data
                self.root.after(0, lambda: self.market_tree.delete(*self.market_tree.get_children()))
                
                for i, stock in enumerate(DIVIDEND_STOCKS):
                    ticker = stock["ticker"]
                    
                    # Get quote data
                    quote_data = self.market_provider.get_stock_quote(ticker)
                    dividend_data = self.market_provider.get_dividend_data(ticker)
                    overview_data = self.market_provider.get_company_overview(ticker)
                    
                    # Prepare row data
                    price = quote_data.get("price", 0) if quote_data else 0
                    change = quote_data.get("change", 0) if quote_data else 0
                    change_percent = quote_data.get("change_percent", "0") if quote_data else "0"
                    div_yield = dividend_data.get("dividend_yield", 0) * 100 if dividend_data else stock["yield"] * 100
                    ex_div_date = overview_data.get("ex_dividend_date", "N/A") if overview_data else "N/A"
                    
                    row_data = (
                        ticker,
                        format_currency(price) if price > 0 else "N/A",
                        format_currency(change, show_sign=True) if change != 0 else "N/A",
                        f"{change_percent}%" if change_percent != "0" else "N/A",
                        format_percentage(div_yield) if div_yield > 0 else "N/A",
                        ex_div_date
                    )
                    
                    # Update in main thread
                    tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.root.after(0, lambda data=row_data, t=tag: self.market_tree.insert("", "end", values=data, tags=(t,)))
                
                self.root.after(0, lambda: messagebox.showinfo("Success", "Market data refreshed!"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh market data: {str(e)}"))

        # Show progress and run in background
        progress_window = self._show_progress_window("Refreshing market data...")
        
        def run_with_progress():
            try:
                fetch_market_data()
            finally:
                if progress_window:
                    self.root.after(0, lambda: progress_window.destroy())
        
        self.executor.submit(run_with_progress)

    def export_market_data(self):
        """Export current market data to CSV"""
        try:
            market_data = []
            for item in self.market_tree.get_children():
                values = self.market_tree.item(item)["values"]
                market_data.append({
                    "Ticker": values[0],
                    "Price": values[1],
                    "Change": values[2],
                    "Change%": values[3],
                    "Dividend Yield": values[4],
                    "Ex-Dividend Date": values[5],
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            if market_data:
                df = pd.DataFrame(market_data)
                filename = os.path.join(os.path.expanduser("~"), "Documents", "market_data_export.csv")
                df.to_csv(filename, index=False)
                messagebox.showinfo("Exported", f"Market data exported to {filename}")
            else:
                messagebox.showwarning("No Data", "No market data to export. Refresh data first.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    # Chart methods
    def show_allocation_chart(self):
        """Show portfolio allocation pie chart"""
        stats = {}  # We don't need stats for allocation chart
        fig = ChartGenerator.create_allocation_pie_chart(stats)
        open_plot_in_window(fig, "Portfolio Allocation")

    def show_yield_chart(self):
        """Show enhanced yield comparison chart with live data"""
        def generate_chart():
            try:
                fig = ChartGenerator.create_yield_comparison_chart(self.market_provider)
                self.root.after(0, lambda: open_plot_in_window(fig, "Yield Comparison"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        self.executor.submit(generate_chart)

    def show_timeline_chart(self):
        """Show investment timeline chart"""
        df = self._get_csv_data()
        if df is not None and not df.empty:
            fig = ChartGenerator.create_investment_timeline(df)
            open_plot_in_window(fig, "Investment Timeline")
        else:
            messagebox.showwarning("No Data", "No investment history found.")

    def show_performance_chart(self):
        """Show portfolio performance chart with gains/losses"""
        def generate_chart():
            try:
                # Use the enhanced market data calculation
                market_data = self.data_processor.get_portfolio_market_value()
                if not market_data.get("stocks"):
                    self.root.after(0, lambda: messagebox.showwarning("No Data", "Unable to fetch current market values."))
                    return
                
                fig = ChartGenerator.create_portfolio_performance_chart(market_data)
                self.root.after(0, lambda: open_plot_in_window(fig, "Portfolio Performance"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        self.executor.submit(generate_chart)

    def show_comparison_chart(self):
        """Show strategy comparison chart using plotly offline"""
        def _generate_chart():
            try:
                df = self._get_csv_data()
                if df is None:
                    self.root.after(0, lambda: messagebox.showwarning("No History", f"No file found: {CSV_FILENAME}"))
                    return

                if not {"Timestamp", "Amount Invested"}.issubset(df.columns):
                    self.root.after(0, lambda: messagebox.showerror("Data Error", "CSV missing required columns."))
                    return

                df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                df["Year"] = df["Timestamp"].dt.year

                # Group by year efficiently
                actual_invest = df.groupby("Year")["Amount Invested"].sum().reset_index()

                # Strategy data
                strategy_years = list(range(1, 11))
                portfolio_22k = [22500, 47500, 71700, 98600, 127270, 157400, 192800, 228400, 264200, 300800]
                portfolio_30k = [30600, 64300, 99600, 136800, 177800, 221400, 267600, 315600, 365400, 429700]

                import plotly.graph_objects as go
                fig = go.Figure()

                # Strategy lines
                fig.add_trace(go.Scatter(
                    x=strategy_years, y=portfolio_22k,
                    name="Portfolio (22K/yr)", mode="lines+markers", yaxis="y2"
                ))
                fig.add_trace(go.Scatter(
                    x=strategy_years, y=portfolio_30k,
                    name="Portfolio (30K/yr)", mode="lines+markers", yaxis="y2"
                ))

                # Add actual data if available
                if not actual_invest.empty:
                    actual_years = actual_invest["Year"] - actual_invest["Year"].min() + 1
                    fig.add_trace(go.Scatter(
                        x=actual_years,
                        y=actual_invest["Amount Invested"],
                        name="Actual Portfolio Value",
                        mode="lines+markers",
                        yaxis="y2"
                    ))

                fig.update_layout(
                    title="[DATA] Strategy Comparison: Portfolio Value",
                    xaxis_title="Year (Relative)",
                    yaxis=dict(title="(unused)", visible=False),
                    yaxis2=dict(title="Portfolio Value ($)", overlaying="y", side="right"),
                    legend=dict(x=0.01, y=0.99),
                    template="plotly_dark"
                )

                # Show chart using plotly offline + webview approach
                self.root.after(0, lambda: open_plot_in_window(fig, "Strategy Comparison"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        # Run in background thread
        self.executor.submit(_generate_chart)

    def generate_growth_tabs(self):
        """Generate growth tabs with optimized data processing"""
        def _generate_tabs():
            try:
                df = self._get_csv_data()
                if df is None or df.empty:
                    return

                mode = self.view_mode.get()
                pivoted_cumsum, y_label = DataProcessor.process_csv_data(df, mode)

                # Update UI in main thread
                self.root.after(0, lambda: self._update_growth_tabs(pivoted_cumsum, mode, y_label))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        # Run in background thread
        self.executor.submit(_generate_tabs)

    def _update_growth_tabs(self, pivoted_cumsum: pd.DataFrame, mode: str, y_label: str):
        """Update growth tabs in main thread"""
        try:
            # Clear existing tabs
            for tab_id in self.stock_tabs.tabs():
                self.stock_tabs.forget(tab_id)

            # Create total overview tab
            tab_total = ttk.Frame(self.stock_tabs)
            self.stock_tabs.add(tab_total, text="[DATA] All Stocks + Total")

            fig_total = ChartGenerator.create_growth_chart(pivoted_cumsum, mode, y_label)
            ttk.Button(
                tab_total, 
                text="Open Interactive Chart", 
                command=lambda: open_plot_in_window(fig_total, f"Cumulative {mode} Growth")
            ).pack(pady=20)

            # Create individual stock tabs
            for ticker in pivoted_cumsum.columns[:-1]:  # Exclude 'Total'
                tab = ttk.Frame(self.stock_tabs)
                self.stock_tabs.add(tab, text=ticker)

                fig = ChartGenerator.create_individual_chart(pivoted_cumsum, ticker, mode, y_label)
                ttk.Button(
                    tab, 
                    text="Open Interactive Chart", 
                    command=lambda f=fig, t=ticker: open_plot_in_window(f, f"{t} Growth")
                ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update tabs: {str(e)}")

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


if __name__ == "__main__":
    root = tk.Tk()
    app = DividendApp(root)
    root.mainloop()