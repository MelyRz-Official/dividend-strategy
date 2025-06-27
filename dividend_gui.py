# import tkinter as tk
# from tkinter import ttk, messagebox
# import pandas as pd
# import sv_ttk
# import os
# from datetime import datetime
# import plotly.graph_objects as go
# from tkinter import StringVar
# from tkinter.ttk import Notebook
# from plotly.offline import plot
# import tempfile
# import webbrowser
# from functools import lru_cache
# from typing import List, Dict, Optional, Tuple
# import threading
# from concurrent.futures import ThreadPoolExecutor

# # Try to import pywebview, fallback to browser if not available
# try:
#     import webview
#     WEBVIEW_AVAILABLE = True
# except ImportError:
#     WEBVIEW_AVAILABLE = False
#     print("pywebview not available, charts will open in default browser")

# # Constants
# CSV_FILENAME = os.path.join(os.path.expanduser("~"), "Documents", "dividend_history.csv")

# # Immutable configuration using tuple for better memory efficiency
# DIVIDEND_STOCKS = (
#     {"ticker": "O", "name": "Realty Income", "yield": 0.055, "allocation": 0.20},
#     {"ticker": "TROW", "name": "T. Rowe Price", "yield": 0.043, "allocation": 0.15},
#     {"ticker": "SCHD", "name": "SCHD", "yield": 0.038, "allocation": 0.15},
#     {"ticker": "HDV", "name": "HDV", "yield": 0.038, "allocation": 0.10},
#     {"ticker": "MO", "name": "Altria", "yield": 0.08, "allocation": 0.10},
#     {"ticker": "APLE", "name": "Apple Hospitality REIT", "yield": 0.06, "allocation": 0.10},
#     {"ticker": "ABBV", "name": "AbbVie", "yield": 0.04, "allocation": 0.10},
#     {"ticker": "VZ", "name": "Verizon", "yield": 0.066, "allocation": 0.10},
# )

# # Validate allocations sum to 1.0
# _total_allocation = sum(stock["allocation"] for stock in DIVIDEND_STOCKS)
# if abs(_total_allocation - 1.0) > 0.001:
#     raise ValueError(f"Stock allocations must sum to 1.0, got {_total_allocation}")

# class DataProcessor:
#     """Separate class for data processing logic - Single Responsibility Principle"""
    
#     @staticmethod
#     @lru_cache(maxsize=128)
#     def calculate_dividends(amount: float, stock_ticker: str, stock_name: str, 
#                            stock_yield: float, stock_allocation: float) -> Dict:
#         """Calculate dividends for a single stock with caching"""
#         allocated = amount * stock_allocation
#         annual_dividend = allocated * stock_yield
#         monthly_dividend = annual_dividend / 12
        
#         return {
#             "ticker": stock_ticker,
#             "name": stock_name,
#             "allocated": round(allocated, 2),
#             "annual_dividend": round(annual_dividend, 2),
#             "monthly_dividend": round(monthly_dividend, 2),
#             "yield_percent": round(stock_yield * 100, 2)
#         }
    
#     @staticmethod
#     def process_csv_data(df: pd.DataFrame, mode: str) -> Tuple[pd.DataFrame, str]:
#         """Process CSV data for chart generation"""
#         if df.empty:
#             raise ValueError("DataFrame is empty")
            
#         required_cols = {"Timestamp", "Ticker", "Estimated Annual Dividend", "Monthly Dividend"}
#         if not required_cols.issubset(df.columns):
#             raise ValueError(f"CSV missing required columns: {required_cols - set(df.columns)}")
        
#         df["Timestamp"] = pd.to_datetime(df["Timestamp"])
#         y_col = "Estimated Annual Dividend" if mode == "Annual" else "Monthly Dividend"
#         y_label = f"{mode} Dividend ($)"
        
#         # Optimize grouping and pivoting
#         grouped = df.groupby(["Timestamp", "Ticker"], as_index=False)[y_col].sum()
#         pivoted = grouped.pivot(index="Timestamp", columns="Ticker", values=y_col).fillna(0)
        
#         # ✅ Calculate cumulative sum for proper growth tracking
#         pivoted_cumsum = pivoted.cumsum()
#         pivoted_cumsum["Total"] = pivoted_cumsum.sum(axis=1)
        
#         return pivoted_cumsum, y_label
    
#     @staticmethod
#     def calculate_portfolio_stats(df: pd.DataFrame) -> Dict:
#         """Calculate portfolio statistics"""
#         if df.empty:
#             return {}
            
#         df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        
#         # ✅ FIX: Get unique total investments by timestamp (avoid double counting)
#         unique_investments = df.groupby("Timestamp")["Total Investment"].first()
#         total_invested = unique_investments.sum()
        
#         # Get cumulative data for current portfolio
#         latest_data = df.groupby("Ticker").last().reset_index()
#         total_annual_dividend = latest_data["Estimated Annual Dividend"].sum()
        
#         # Calculate weighted average yield
#         total_amount_invested = latest_data["Amount Invested"].sum()
#         avg_yield = (latest_data["Yield (%)"] * latest_data["Amount Invested"]).sum() / total_amount_invested if total_amount_invested > 0 else 0
        
#         # Calculate investment frequency
#         investment_count = len(unique_investments)
#         date_range = (df["Timestamp"].max() - df["Timestamp"].min()).days
#         investments_per_month = (investment_count / (date_range / 30.44)) if date_range > 0 else 0
        
#         return {
#             "total_invested": total_invested,
#             "total_annual_dividend": total_annual_dividend,
#             "avg_yield": avg_yield,
#             "investment_count": investment_count,
#             "investments_per_month": investments_per_month,
#             "portfolio_yield": (total_annual_dividend / total_invested * 100) if total_invested > 0 else 0,
#             "monthly_income": total_annual_dividend / 12
#         }

# class ChartGenerator:
#     """Separate class for chart generation using plotly offline"""
    
#     @staticmethod
#     def create_growth_chart(pivoted_cumsum: pd.DataFrame, mode: str, y_label: str) -> go.Figure:
#         """Create growth chart with optimized trace creation"""
#         fig = go.Figure()
        
#         # Add stock traces
#         for ticker in pivoted_cumsum.columns[:-1]:  # skip Total
#             fig.add_trace(go.Scatter(
#                 x=pivoted_cumsum.index,
#                 y=pivoted_cumsum[ticker],
#                 mode="lines+markers",
#                 name=ticker,
#                 hovertemplate=f"{ticker}: %{{y:.2f}}<extra></extra>"
#             ))
        
#         # Add total line with dashed white line
#         fig.add_trace(go.Scatter(
#             x=pivoted_cumsum.index,
#             y=pivoted_cumsum["Total"],
#             mode="lines+markers",
#             name="Total",
#             line=dict(color="white", width=3, dash="dash"),
#             hovertemplate="Total: %{y:.2f}<extra></extra>"
#         ))

#         fig.update_layout(
#             title=f"Cumulative {mode} Dividend Growth Over Time",
#             xaxis_title="Date",
#             yaxis_title=f"Cumulative {y_label}",
#             template="plotly_dark",
#             hovermode="x unified"
#         )
        
#         return fig
    
#     @staticmethod
#     def create_individual_chart(pivoted_cumsum: pd.DataFrame, ticker: str, mode: str, y_label: str) -> go.Figure:
#         """Create individual stock chart"""
#         fig = go.Figure()
#         fig.add_trace(go.Scatter(
#             x=pivoted_cumsum.index,
#             y=pivoted_cumsum[ticker],
#             mode="lines+markers",
#             name=ticker,
#             hovertemplate=f"{ticker}: %{{y:.2f}}<extra></extra>"
#         ))
        
#         fig.update_layout(
#             title=f"{ticker} - Cumulative {mode} Dividend Growth",
#             xaxis_title="Date",
#             yaxis_title=f"Cumulative {y_label}",
#             template="plotly_dark"
#         )
        
#         return fig
    
#     @staticmethod
#     def create_allocation_pie_chart(stats: Dict) -> go.Figure:
#         """Create portfolio allocation pie chart"""
#         fig = go.Figure()
        
#         # Get allocation data
#         labels = [stock["ticker"] for stock in DIVIDEND_STOCKS]
#         values = [stock["allocation"] * 100 for stock in DIVIDEND_STOCKS]
        
#         fig.add_trace(go.Pie(
#             labels=labels,
#             values=values,
#             hovertemplate="<b>%{label}</b><br>Allocation: %{value:.1f}%<extra></extra>",
#             textinfo='label+percent',
#             textposition='inside'
#         ))
        
#         fig.update_layout(
#             title="Portfolio Allocation by Stock",
#             template="plotly_dark",
#             showlegend=True
#         )
        
#         return fig
    
#     @staticmethod
#     def create_yield_comparison_chart() -> go.Figure:
#         """Create yield comparison bar chart"""
#         fig = go.Figure()
        
#         tickers = [stock["ticker"] for stock in DIVIDEND_STOCKS]
#         yields = [stock["yield"] * 100 for stock in DIVIDEND_STOCKS]
        
#         fig.add_trace(go.Bar(
#             x=tickers,
#             y=yields,
#             text=[f"{y:.1f}%" for y in yields],
#             textposition='auto',
#             hovertemplate="<b>%{x}</b><br>Yield: %{y:.2f}%<extra></extra>",
#             marker=dict(color=yields, colorscale='RdYlBu_r', showscale=True)
#         ))
        
#         fig.update_layout(
#             title="Dividend Yield by Stock",
#             xaxis_title="Stock Ticker",
#             yaxis_title="Dividend Yield (%)",
#             template="plotly_dark"
#         )
        
#         return fig
    
#     @staticmethod
#     def create_investment_timeline(df: pd.DataFrame) -> go.Figure:
#         """Create investment timeline chart"""
#         if df.empty:
#             return go.Figure()
            
#         df["Timestamp"] = pd.to_datetime(df["Timestamp"])
#         timeline_data = df.groupby("Timestamp")["Total Investment"].first().reset_index()
#         timeline_data["Cumulative"] = timeline_data["Total Investment"].cumsum()
        
#         fig = go.Figure()
        
#         # Individual investments
#         fig.add_trace(go.Scatter(
#             x=timeline_data["Timestamp"],
#             y=timeline_data["Total Investment"],
#             mode="markers",
#             name="Individual Investments",
#             marker=dict(size=10, color="lightblue"),
#             hovertemplate="<b>Investment</b><br>Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>"
#         ))
        
#         # Cumulative line
#         fig.add_trace(go.Scatter(
#             x=timeline_data["Timestamp"],
#             y=timeline_data["Cumulative"],
#             mode="lines+markers",
#             name="Cumulative Investment",
#             line=dict(color="orange", width=3),
#             hovertemplate="<b>Total Invested</b><br>Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>"
#         ))
        
#         fig.update_layout(
#             title="Investment Timeline",
#             xaxis_title="Date",
#             yaxis_title="Investment Amount ($)",
#             template="plotly_dark",
#             hovermode="x unified"
#         )
        
#         return fig

# class DividendApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("💸 Dividend Strategy Calculator")
#         self.root.geometry("1600x800")  # Increased size for dashboard
        
#         # Initialize data structures
#         self.data: List[Dict] = []
#         self.latest_investment: float = 0.0
#         self.total_dividend: float = 0.0
#         self._cached_csv_data: Optional[pd.DataFrame] = None
#         self._csv_last_modified: float = 0.0
        
#         # Thread pool for background operations
#         self.executor = ThreadPoolExecutor(max_workers=2)
        
#         sv_ttk.set_theme("dark")
#         self._setup_ui()

#     def _setup_ui(self):
#         """Initialize the user interface"""
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
#         """Setup left panel with inputs, stats, and table"""
#         # Input section
#         input_frame = ttk.LabelFrame(parent, text="💰 Investment Calculator", padding=10)
#         input_frame.pack(pady=(0, 10), fill="x")
        
#         entry_frame = ttk.Frame(input_frame)
#         entry_frame.pack(fill="x")
#         ttk.Label(entry_frame, text="Amount ($):").pack(side="left", padx=(0, 5))
#         self.amount_entry = ttk.Entry(entry_frame, width=15)
#         self.amount_entry.pack(side="left", padx=(0, 5))
#         self.amount_entry.insert(0, "100.00")
#         self.amount_entry.bind("<Return>", lambda e: self.calculate())
#         ttk.Button(entry_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        
#         # Portfolio stats section
#         stats_frame = ttk.LabelFrame(parent, text="📊 Portfolio Statistics", padding=10)
#         stats_frame.pack(pady=(0, 10), fill="x")
        
#         self.stats_labels = {}
#         stats_info = [
#             ("total_invested", "Total Invested:"),
#             ("total_dividend", "Annual Dividend:"),
#             ("monthly_income", "Monthly Income:"),
#             ("avg_yield", "Portfolio Yield:"),
#             ("investment_count", "Investments Made:")
#         ]
        
#         for key, label in stats_info:
#             frame = ttk.Frame(stats_frame)
#             frame.pack(fill="x", pady=2)
#             ttk.Label(frame, text=label).pack(side="left")
#             self.stats_labels[key] = ttk.Label(frame, text="$0.00", font=("Segoe UI", 9, "bold"))
#             self.stats_labels[key].pack(side="right")

#         # Current calculation results
#         calc_frame = ttk.LabelFrame(parent, text="🧮 Current Calculation", padding=10)
#         calc_frame.pack(pady=(0, 10), fill="both", expand=True)

#         self.tree = ttk.Treeview(
#             calc_frame,
#             columns=("Ticker", "Amount", "Yield", "Monthly", "Annual"),
#             show="headings", height=8
#         )
#         headers = {
#             "Ticker": ("Ticker", 80),
#             "Amount": ("Allocation $", 100),
#             "Yield": ("Yield (%)", 80),
#             "Monthly": ("Monthly Div", 90),
#             "Annual": ("Annual Div", 90)
#         }
#         for col, (label, width) in headers.items():
#             self.tree.heading(col, text=label)
#             self.tree.column(col, anchor="center", width=width)

#         self.tree.tag_configure("evenrow", background="#1e1e1e")
#         self.tree.tag_configure("oddrow", background="#2a2a2a")
#         self.tree.pack(fill="both", expand=True, pady=(0, 10))

#         self.total_label = ttk.Label(calc_frame, text="", font=("Segoe UI", 10, "bold"))
#         self.total_label.pack()

#         # Action buttons
#         button_frame = ttk.Frame(calc_frame)
#         button_frame.pack(pady=(10, 0), fill="x")
#         ttk.Button(button_frame, text="💾 Save to History", command=self.save_csv).pack(side="left", padx=(0, 5))
#         ttk.Button(button_frame, text="🔄 Refresh Dashboard", command=self.refresh_dashboard).pack(side="left")

#     def _setup_right_panel(self, parent):
#         """Setup right panel with enhanced dashboard tabs"""
#         self.tab_notebook = Notebook(parent)
#         self.tab_notebook.pack(fill="both", expand=True)

#         # Growth Charts Tab
#         growth_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(growth_tab, text="📈 Growth Charts")

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

#         # Portfolio Analysis Tab
#         analysis_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(analysis_tab, text="📊 Portfolio Analysis")
        
#         analysis_buttons = ttk.Frame(analysis_tab)
#         analysis_buttons.pack(pady=20)
        
#         ttk.Button(analysis_buttons, text="📊 Allocation Pie Chart", 
#                   command=self.show_allocation_chart).pack(side="left", padx=5)
#         ttk.Button(analysis_buttons, text="📈 Yield Comparison", 
#                   command=self.show_yield_chart).pack(side="left", padx=5)
#         ttk.Button(analysis_buttons, text="⏰ Investment Timeline", 
#                   command=self.show_timeline_chart).pack(side="left", padx=5)

#         # Strategy Comparison Tab
#         comparison_tab = ttk.Frame(self.tab_notebook)
#         self.tab_notebook.add(comparison_tab, text="🎯 Strategy Comparison")
#         ttk.Button(comparison_tab, text="Open Strategy Comparison Chart", 
#                   command=self.show_comparison_chart).pack(pady=20)

#         # Initialize dashboard
#         self.refresh_dashboard()

#     def calculate(self):
#         """Calculate dividend allocations with improved performance"""
#         try:
#             amount = float(self.amount_entry.get().replace("$", "").replace(",", ""))
#             if amount <= 0:
#                 raise ValueError("Amount must be positive")
                
#             self.latest_investment = amount
#             self.data.clear()
#             self.tree.delete(*self.tree.get_children())

#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             total_dividend = 0.0

#             # Process each stock efficiently
#             for i, stock in enumerate(DIVIDEND_STOCKS):
#                 # Use optimized calculation with caching
#                 calc_result = DataProcessor.calculate_dividends(
#                     amount, stock["ticker"], stock["name"], 
#                     stock["yield"], stock["allocation"]
#                 )
                
#                 # Update tree view
#                 tag = "evenrow" if i % 2 == 0 else "oddrow"
#                 self.tree.insert("", "end", values=(
#                     calc_result["ticker"],
#                     f"${calc_result['allocated']:.2f}",
#                     f"{calc_result['yield_percent']:.2f}%",
#                     f"${calc_result['monthly_dividend']:.2f}",
#                     f"${calc_result['annual_dividend']:.2f}"
#                 ), tags=(tag,))

#                 # Build data for CSV
#                 self.data.append({
#                     "Timestamp": timestamp,
#                     "Ticker": calc_result["ticker"],
#                     "Company": calc_result["name"],
#                     "Amount Invested": calc_result["allocated"],
#                     "Yield (%)": calc_result["yield_percent"],
#                     "Monthly Dividend": calc_result["monthly_dividend"],
#                     "Estimated Annual Dividend": calc_result["annual_dividend"],
#                     "Total Investment": amount
#                 })
                
#                 total_dividend += calc_result["annual_dividend"]

#             self.total_dividend = total_dividend
#             self.total_label.config(text=f"Total Estimated Annual Dividend: ${total_dividend:.2f}")

#         except ValueError as e:
#             messagebox.showerror("Invalid Input", f"Please enter a valid dollar amount: {str(e)}")

#     def save_csv(self):
#         """Save data to CSV with improved error handling"""
#         try:
#             if not self.data:
#                 messagebox.showwarning("No Data", "Please calculate first before saving.")
#                 return
                
#             df = pd.DataFrame(self.data)
            
#             # Ensure directory exists
#             os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)
            
#             file_exists = os.path.exists(CSV_FILENAME)
#             df.to_csv(CSV_FILENAME, mode='a', header=not file_exists, index=False)
            
#             # Clear cache and refresh dashboard
#             self._cached_csv_data = None
#             self.refresh_dashboard()
            
#             messagebox.showinfo("Saved", f"Data saved and dashboard updated!")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def refresh_dashboard(self):
#         """Refresh all dashboard statistics and charts"""
#         df = self._get_csv_data()
#         if df is not None and not df.empty:
#             stats = DataProcessor.calculate_portfolio_stats(df)
#             self._update_stats_display(stats)
#             self.generate_growth_tabs()
#         else:
#             # Clear stats if no data
#             for label in self.stats_labels.values():
#                 label.config(text="$0.00")

#     def _update_stats_display(self, stats: Dict):
#         """Update the statistics display"""
#         if not stats:
#             return
            
#         self.stats_labels["total_invested"].config(text=f"${stats.get('total_invested', 0):.2f}")
#         self.stats_labels["total_dividend"].config(text=f"${stats.get('total_annual_dividend', 0):.2f}")
#         self.stats_labels["monthly_income"].config(text=f"${stats.get('monthly_income', 0):.2f}")
#         self.stats_labels["avg_yield"].config(text=f"{stats.get('portfolio_yield', 0):.2f}%")
#         self.stats_labels["investment_count"].config(text=f"{stats.get('investment_count', 0)}")

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

#     def show_allocation_chart(self):
#         """Show portfolio allocation pie chart"""
#         stats = {}  # We don't need stats for allocation chart
#         fig = ChartGenerator.create_allocation_pie_chart(stats)
#         self.open_plot_in_window(fig, "Portfolio Allocation")

#     def show_yield_chart(self):
#         """Show yield comparison chart"""
#         fig = ChartGenerator.create_yield_comparison_chart()
#         self.open_plot_in_window(fig, "Yield Comparison")

#     def show_timeline_chart(self):
#         """Show investment timeline chart"""
#         df = self._get_csv_data()
#         if df is not None and not df.empty:
#             fig = ChartGenerator.create_investment_timeline(df)
#             self.open_plot_in_window(fig, "Investment Timeline")
#         else:
#             messagebox.showwarning("No Data", "No investment history found.")

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
#                     title="📊 Strategy Comparison: Portfolio Value",
#                     xaxis_title="Year (Relative)",
#                     yaxis=dict(title="(unused)", visible=False),
#                     yaxis2=dict(title="Portfolio Value ($)", overlaying="y", side="right"),
#                     legend=dict(x=0.01, y=0.99),
#                     template="plotly_dark"
#                 )

#                 # Show chart using plotly offline + webview approach
#                 self.root.after(0, lambda: self.open_plot_in_window(fig, "Strategy Comparison"))

#             except Exception as e:
#                 self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

#         # Run in background thread
#         self.executor.submit(_generate_chart)

#     def open_plot_in_window(self, fig, title="Chart"):
#         """Open plot in embedded window using pywebview or fallback to browser"""
#         try:
#             # Create a temp HTML file using plotly offline
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
#                 plot(fig, filename=temp_file.name, auto_open=False, include_plotlyjs='cdn')
                
#                 if WEBVIEW_AVAILABLE:
#                     # Open in embedded window using pywebview (preferred)
#                     webview.create_window(title, temp_file.name, width=1000, height=700)
#                     webview.start()
#                 else:
#                     # Fallback: open in default browser
#                     webbrowser.open(f'file://{temp_file.name}')
                    
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to open chart: {str(e)}")

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
#             self.stock_tabs.add(tab_total, text="📊 All Stocks + Total")

#             fig_total = ChartGenerator.create_growth_chart(pivoted_cumsum, mode, y_label)
#             ttk.Button(
#                 tab_total, 
#                 text="Open Interactive Chart", 
#                 command=lambda: self.open_plot_in_window(fig_total, f"Cumulative {mode} Growth")
#             ).pack(pady=20)

#             # Create individual stock tabs
#             for ticker in pivoted_cumsum.columns[:-1]:  # Exclude 'Total'
#                 tab = ttk.Frame(self.stock_tabs)
#                 self.stock_tabs.add(tab, text=ticker)

#                 fig = ChartGenerator.create_individual_chart(pivoted_cumsum, ticker, mode, y_label)
#                 ttk.Button(
#                     tab, 
#                     text="Open Interactive Chart", 
#                     command=lambda f=fig, t=ticker: self.open_plot_in_window(f, f"{t} Growth")
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

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sv_ttk
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from tkinter import StringVar
from tkinter.ttk import Notebook
from plotly.offline import plot
import tempfile
import webbrowser
from functools import lru_cache
from typing import List, Dict, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import time

# Secure configuration loading
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

# Try to import pywebview, fallback to browser if not available
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("pywebview not available, charts will open in default browser")

# Constants
CSV_FILENAME = os.path.join(os.path.expanduser("~"), "Documents", "dividend_history.csv")
CACHE_FILENAME = os.path.join(os.path.expanduser("~"), "Documents", "market_data_cache.json")

# Load configuration
ALPHA_VANTAGE_API_KEY = load_api_key()
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Load other config values if config file exists
try:
    import config
    API_CALL_DELAY = getattr(config, 'API_CALL_DELAY', 12)
    CACHE_DURATION_HOURS = getattr(config, 'CACHE_DURATION_HOURS', 1)
except ImportError:
    API_CALL_DELAY = 12
    CACHE_DURATION_HOURS = 1

# Immutable configuration - now we'll update yields from API
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

# Validate allocations sum to 1.0
_total_allocation = sum(stock["allocation"] for stock in DIVIDEND_STOCKS)
if abs(_total_allocation - 1.0) > 0.001:
    raise ValueError(f"Stock allocations must sum to 1.0, got {_total_allocation}")

class MarketDataProvider:
    """Handles all market data API interactions"""
    
    def __init__(self, api_key: str = ALPHA_VANTAGE_API_KEY):
        self.api_key = api_key
        self.cache = self._load_cache()
        self.last_api_call = 0
        self.api_call_delay = API_CALL_DELAY  # From config file
        
        # Check if cache is still valid
        cache_valid_hours = CACHE_DURATION_HOURS

    def _load_cache(self) -> Dict:
        """Load cached market data"""
        try:
            if os.path.exists(CACHE_FILENAME):
                with open(CACHE_FILENAME, 'r') as f:
                    cache_data = json.load(f)
                    # Check if cache is less than configured hours old
                    cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                    if datetime.now() - cache_time < timedelta(hours=cache_valid_hours):
                        return cache_data.get('data', {})
            return {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}

    def _save_cache(self):
        """Save market data to cache"""
        try:
            os.makedirs(os.path.dirname(CACHE_FILENAME), exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': self.cache
            }
            with open(CACHE_FILENAME, 'w') as f:
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
            
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
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
            
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
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
            
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
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

    def get_portfolio_market_value(self, df: pd.DataFrame) -> Dict:
        """Calculate current market value of portfolio"""
        if df.empty:
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

class ChartGenerator:
    """Enhanced chart generation with market data"""
    
    @staticmethod
    def create_growth_chart(pivoted_cumsum: pd.DataFrame, mode: str, y_label: str) -> go.Figure:
        """Create growth chart with optimized trace creation"""
        fig = go.Figure()
        
        # Add stock traces
        for ticker in pivoted_cumsum.columns[:-1]:  # skip Total
            fig.add_trace(go.Scatter(
                x=pivoted_cumsum.index,
                y=pivoted_cumsum[ticker],
                mode="lines+markers",
                name=ticker,
                hovertemplate=f"{ticker}: %{{y:.2f}}<extra></extra>"
            ))
        
        # Add total line with dashed white line
        fig.add_trace(go.Scatter(
            x=pivoted_cumsum.index,
            y=pivoted_cumsum["Total"],
            mode="lines+markers",
            name="Total",
            line=dict(color="white", width=3, dash="dash"),
            hovertemplate="Total: %{y:.2f}<extra></extra>"
        ))

        fig.update_layout(
            title=f"Cumulative {mode} Dividend Growth Over Time",
            xaxis_title="Date",
            yaxis_title=f"Cumulative {y_label}",
            template="plotly_dark",
            hovermode="x unified"
        )
        
        return fig
    
    @staticmethod
    def create_individual_chart(pivoted_cumsum: pd.DataFrame, ticker: str, mode: str, y_label: str) -> go.Figure:
        """Create individual stock chart"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pivoted_cumsum.index,
            y=pivoted_cumsum[ticker],
            mode="lines+markers",
            name=ticker,
            hovertemplate=f"{ticker}: %{{y:.2f}}<extra></extra>"
        ))
        
        fig.update_layout(
            title=f"{ticker} - Cumulative {mode} Dividend Growth",
            xaxis_title="Date",
            yaxis_title=f"Cumulative {y_label}",
            template="plotly_dark"
        )
        
        return fig
    
    @staticmethod
    def create_allocation_pie_chart(stats: Dict) -> go.Figure:
        """Create portfolio allocation pie chart"""
        fig = go.Figure()
        
        # Get allocation data
        labels = [stock["ticker"] for stock in DIVIDEND_STOCKS]
        values = [stock["allocation"] * 100 for stock in DIVIDEND_STOCKS]
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hovertemplate="<b>%{label}</b><br>Allocation: %{value:.1f}%<extra></extra>",
            textinfo='label+percent',
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Portfolio Allocation by Stock",
            template="plotly_dark",
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_yield_comparison_chart(market_provider: MarketDataProvider) -> go.Figure:
        """Create yield comparison bar chart with live data"""
        fig = go.Figure()
        
        tickers = []
        static_yields = []
        live_yields = []
        
        for stock in DIVIDEND_STOCKS:
            tickers.append(stock["ticker"])
            static_yields.append(stock["yield"] * 100)
            
            # Try to get live yield
            dividend_data = market_provider.get_dividend_data(stock["ticker"])
            if dividend_data and dividend_data['dividend_yield'] > 0:
                live_yields.append(dividend_data['dividend_yield'] * 100)
            else:
                live_yields.append(stock["yield"] * 100)  # Fallback to static
        
        # Static yields
        fig.add_trace(go.Bar(
            x=tickers,
            y=static_yields,
            name="Static Yields",
            text=[f"{y:.1f}%" for y in static_yields],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Static Yield: %{y:.2f}%<extra></extra>",
            marker=dict(color='lightblue', opacity=0.7)
        ))
        
        # Live yields
        fig.add_trace(go.Bar(
            x=tickers,
            y=live_yields,
            name="Live Yields",
            text=[f"{y:.1f}%" for y in live_yields],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Live Yield: %{y:.2f}%<extra></extra>",
            marker=dict(color='orange')
        ))
        
        fig.update_layout(
            title="Dividend Yield Comparison: Static vs Live Data",
            xaxis_title="Stock Ticker",
            yaxis_title="Dividend Yield (%)",
            template="plotly_dark",
            barmode='group'
        )
        
        return fig
    
    @staticmethod
    def create_investment_timeline(df: pd.DataFrame) -> go.Figure:
        """Create investment timeline chart"""
        if df.empty:
            return go.Figure()
            
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        timeline_data = df.groupby("Timestamp")["Total Investment"].first().reset_index()
        timeline_data["Cumulative"] = timeline_data["Total Investment"].cumsum()
        
        fig = go.Figure()
        
        # Individual investments
        fig.add_trace(go.Scatter(
            x=timeline_data["Timestamp"],
            y=timeline_data["Total Investment"],
            mode="markers",
            name="Individual Investments",
            marker=dict(size=10, color="lightblue"),
            hovertemplate="<b>Investment</b><br>Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>"
        ))
        
        # Cumulative line
        fig.add_trace(go.Scatter(
            x=timeline_data["Timestamp"],
            y=timeline_data["Cumulative"],
            mode="lines+markers",
            name="Cumulative Investment",
            line=dict(color="orange", width=3),
            hovertemplate="<b>Total Invested</b><br>Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Investment Timeline",
            xaxis_title="Date",
            yaxis_title="Investment Amount ($)",
            template="plotly_dark",
            hovermode="x unified"
        )
        
        return fig

    @staticmethod
    def create_portfolio_performance_chart(market_data: Dict) -> go.Figure:
        """Create portfolio performance chart showing gains/losses"""
        if not market_data.get("stocks"):
            return go.Figure()
        
        stocks = market_data["stocks"]
        tickers = [stock["ticker"] for stock in stocks]
        invested_amounts = [stock["invested"] for stock in stocks]
        current_values = [stock["current_value"] for stock in stocks]
        gains_losses = [stock["gain_loss"] for stock in stocks]
        
        fig = go.Figure()
        
        # Invested amounts
        fig.add_trace(go.Bar(
            x=tickers,
            y=invested_amounts,
            name="Amount Invested",
            marker=dict(color='lightblue'),
            hovertemplate="<b>%{x}</b><br>Invested: $%{y:.2f}<extra></extra>"
        ))
        
        # Current values
        fig.add_trace(go.Bar(
            x=tickers,
            y=current_values,
            name="Current Value",
            marker=dict(color='orange'),
            hovertemplate="<b>%{x}</b><br>Current Value: $%{y:.2f}<extra></extra>"
        ))
        
        # Gains/Losses as line
        fig.add_trace(go.Scatter(
            x=tickers,
            y=gains_losses,
            mode="lines+markers",
            name="Gain/Loss",
            line=dict(color='white', width=3),
            marker=dict(size=8),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Gain/Loss: $%{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Portfolio Performance: Invested vs Current Value",
            xaxis_title="Stock Ticker",
            yaxis_title="Amount ($)",
            yaxis2=dict(title="Gain/Loss ($)", overlaying="y", side="right"),
            template="plotly_dark",
            barmode='group'
        )
        
        return fig

class DividendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Real-Time Dividend Strategy Calculator")
        self.root.geometry("1700x900")  # Slightly larger for new features
        
        # Initialize market data provider
        self.market_provider = MarketDataProvider()
        self.data_processor = DataProcessor(self.market_provider)
        
        # Initialize data structures
        self.data: List[Dict] = []
        self.latest_investment: float = 0.0
        self.total_dividend: float = 0.0
        self._cached_csv_data: Optional[pd.DataFrame] = None
        self._csv_last_modified: float = 0.0
        self.use_live_data = tk.BooleanVar(value=False)
        
        # Thread pool for background operations
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        sv_ttk.set_theme("dark")
        self._setup_ui()

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
        # API Configuration section
        api_frame = ttk.LabelFrame(parent, text="🌐 Market Data Settings", padding=10)
        api_frame.pack(pady=(0, 10), fill="x")
        
        # API key entry with secure handling
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(key_frame, text="Alpha Vantage API Key:").pack(side="left")
        self.api_key_entry = ttk.Entry(key_frame, width=20, show="*")
        self.api_key_entry.pack(side="left", padx=(5, 0))
        
        # Show masked version of current key
        current_key = self.market_provider.api_key
        if current_key and current_key != 'demo':
            masked_key = current_key[:4] + '*' * (len(current_key) - 8) + current_key[-4:] if len(current_key) > 8 else '*' * len(current_key)
            self.api_key_entry.insert(0, masked_key)
        else:
            self.api_key_entry.insert(0, current_key)
        
        # Live data toggle
        live_data_frame = ttk.Frame(api_frame)
        live_data_frame.pack(fill="x")
        ttk.Checkbutton(live_data_frame, text="Use Live Market Data", 
                       variable=self.use_live_data,
                       command=self.on_live_data_toggle).pack(side="left")
        ttk.Button(live_data_frame, text="🔄 Update API Key", 
                  command=self.update_api_key).pack(side="right")

        # Input section
        input_frame = ttk.LabelFrame(parent, text="💰 Investment Calculator", padding=10)
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
        stats_frame = ttk.LabelFrame(parent, text="📊 Portfolio Statistics", padding=10)
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
        calc_frame = ttk.LabelFrame(parent, text="🧮 Current Calculation", padding=10)
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
        ttk.Button(button_frame, text="💾 Save to History", command=self.save_csv).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="🔄 Refresh Dashboard", command=self.refresh_dashboard).pack(side="left")

    def _setup_right_panel(self, parent):
        """Setup enhanced right panel with market data features"""
        self.tab_notebook = Notebook(parent)
        self.tab_notebook.pack(fill="both", expand=True)

        # Growth Charts Tab
        growth_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(growth_tab, text="📈 Growth Charts")

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
        self.tab_notebook.add(analysis_tab, text="📊 Portfolio Analysis")
        
        analysis_buttons = ttk.Frame(analysis_tab)
        analysis_buttons.pack(pady=20)
        
        ttk.Button(analysis_buttons, text="📊 Allocation Pie Chart", 
                  command=self.show_allocation_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="📈 Yield Comparison (Live)", 
                  command=self.show_yield_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="⏰ Investment Timeline", 
                  command=self.show_timeline_chart).pack(side="left", padx=5)
        ttk.Button(analysis_buttons, text="💰 Portfolio Performance", 
                  command=self.show_performance_chart).pack(side="left", padx=5)

        # Market Data Tab (New)
        market_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(market_tab, text="🌐 Live Market Data")
        
        # Market data display
        market_info_frame = ttk.LabelFrame(market_tab, text="📊 Current Stock Prices", padding=10)
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
        ttk.Button(market_button_frame, text="🔄 Refresh Market Data", 
                  command=self.refresh_market_data).pack(side="left", padx=5)
        ttk.Button(market_button_frame, text="📋 Export Market Data", 
                  command=self.export_market_data).pack(side="left", padx=5)

        # Strategy Comparison Tab
        comparison_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(comparison_tab, text="🎯 Strategy Comparison")
        ttk.Button(comparison_tab, text="Open Strategy Comparison Chart", 
                  command=self.show_comparison_chart).pack(pady=20)

        # Initialize dashboard
        self.refresh_dashboard()

    def update_api_key(self):
        """Update the API key for market data"""
        new_key = self.api_key_entry.get().strip()
        
        # Don't update if it's just the masked display
        if '*' in new_key:
            messagebox.showinfo("Info", "Please enter your full API key to update.")
            return
            
        if new_key and len(new_key) > 5:  # Basic validation
            self.market_provider.api_key = new_key
            # Clear cache to force fresh data with new key
            self.market_provider.cache = {}
            
            # Update display with masked version
            if len(new_key) > 8:
                masked_key = new_key[:4] + '*' * (len(new_key) - 8) + new_key[-4:]
            else:
                masked_key = '*' * len(new_key)
            
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, masked_key)
            
            messagebox.showinfo("API Key Updated", 
                              "API key updated successfully!\n"
                              "Tip: Save your key in config.py to avoid re-entering it.")
        else:
            messagebox.showwarning("Invalid Key", 
                                 "Please enter a valid API key.\n"
                                 "Get one free at: alphavantage.co/support/#api-key")

    def on_live_data_toggle(self):
        """Handle live data toggle"""
        if self.use_live_data.get():
            # Check if we have a valid API key
            current_key = self.market_provider.api_key
            if current_key == "demo" or not current_key:
                response = messagebox.askyesno(
                    "Setup API Key", 
                    "To use live data, you need a free Alpha Vantage API key.\n\n"
                    "Options:\n"
                    "1. Get free key at alphavantage.co/support/#api-key\n"
                    "2. Use demo key (AAPL stock only)\n\n"
                    "Continue with demo key for now?"
                )
                if not response:
                    self.use_live_data.set(False)
                    return
            
            messagebox.showinfo(
                "Live Data Enabled", 
                "✅ Live market data enabled!\n\n"
                "Next calculation will use real-time data.\n"
                "Note: API calls are rate limited (5 per minute).\n\n"
                "💡 Tip: Save your API key in config.py to avoid re-entering."
            )
        else:
            messagebox.showinfo("Live Data Disabled", "Using static dividend yields.")

    def calculate(self):
        """Enhanced calculation with optional live market data"""
        try:
            amount = float(self.amount_entry.get().replace("$", "").replace(",", ""))
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
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
            messagebox.showerror("Invalid Input", f"Please enter a valid dollar amount: {str(e)}")

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
        
        live_indicator = "✅" if calc_result.get("is_live_data") else "❌"
        
        self.tree.insert("", "end", values=(
            calc_result["ticker"],
            f"${calc_result['allocated']:.2f}",
            f"{calc_result['yield_percent']:.2f}%",
            f"${calc_result['monthly_dividend']:.2f}",
            f"${calc_result['annual_dividend']:.2f}",
            live_indicator
        ), tags=(tag,))

    def _update_total_label(self, total_dividend: float):
        """Update total dividend label"""
        self.total_dividend = total_dividend
        self.total_label.config(text=f"Total Estimated Annual Dividend: ${total_dividend:.2f}")

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
                        f"${price:.2f}" if price > 0 else "N/A",
                        f"${change:.2f}" if change != 0 else "N/A",
                        f"{change_percent}%" if change_percent != "0" else "N/A",
                        f"{div_yield:.2f}%" if div_yield > 0 else "N/A",
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

    def show_performance_chart(self):
        """Show portfolio performance chart with gains/losses"""
        def generate_chart():
            try:
                df = self._get_csv_data()
                if df is None or df.empty:
                    self.root.after(0, lambda: messagebox.showwarning("No Data", "No investment history found."))
                    return
                
                market_data = self.data_processor.get_portfolio_market_value(df)
                if not market_data.get("stocks"):
                    self.root.after(0, lambda: messagebox.showwarning("No Data", "Unable to fetch current market values."))
                    return
                
                fig = ChartGenerator.create_portfolio_performance_chart(market_data)
                self.root.after(0, lambda: self.open_plot_in_window(fig, "Portfolio Performance"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        self.executor.submit(generate_chart)

    def save_csv(self):
        """Enhanced save with market data"""
        try:
            if not self.data:
                messagebox.showwarning("No Data", "Please calculate first before saving.")
                return
                
            df = pd.DataFrame(self.data)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)
            
            file_exists = os.path.exists(CSV_FILENAME)
            df.to_csv(CSV_FILENAME, mode='a', header=not file_exists, index=False)
            
            # Clear cache and refresh dashboard
            self._cached_csv_data = None
            self.refresh_dashboard()
            
            messagebox.showinfo("Saved", f"Data saved with market information!")
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
                        market_data = self.data_processor.get_portfolio_market_value(df)
                        stats.update({
                            "market_value": market_data.get("total_market_value", 0),
                            "total_gain_loss": market_data.get("total_gain_loss", 0)
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
        """Enhanced stats display with market data"""
        if not stats:
            return
            
        self.stats_labels["total_invested"].config(text=f"${stats.get('total_invested', 0):.2f}")
        self.stats_labels["total_dividend"].config(text=f"${stats.get('total_annual_dividend', 0):.2f}")
        self.stats_labels["monthly_income"].config(text=f"${stats.get('monthly_income', 0):.2f}")
        self.stats_labels["avg_yield"].config(text=f"{stats.get('portfolio_yield', 0):.2f}%")
        self.stats_labels["investment_count"].config(text=f"{stats.get('investment_count', 0)}")
        
        # Market data (if available)
        market_value = stats.get('market_value', 0)
        total_gain_loss = stats.get('total_gain_loss', 0)
        
        if market_value > 0:
            self.stats_labels["market_value"].config(text=f"${market_value:.2f}")
            color = "green" if total_gain_loss >= 0 else "red"
            sign = "+" if total_gain_loss >= 0 else ""
            self.stats_labels["total_gain_loss"].config(
                text=f"{sign}${total_gain_loss:.2f}",
                foreground=color
            )
        else:
            self.stats_labels["market_value"].config(text="Enable Live Data")
            self.stats_labels["total_gain_loss"].config(text="Enable Live Data")

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

    def show_allocation_chart(self):
        """Show portfolio allocation pie chart"""
        stats = {}  # We don't need stats for allocation chart
        fig = ChartGenerator.create_allocation_pie_chart(stats)
        self.open_plot_in_window(fig, "Portfolio Allocation")

    def show_yield_chart(self):
        """Show enhanced yield comparison chart with live data"""
        def generate_chart():
            try:
                fig = ChartGenerator.create_yield_comparison_chart(self.market_provider)
                self.root.after(0, lambda: self.open_plot_in_window(fig, "Yield Comparison"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        self.executor.submit(generate_chart)

    def show_timeline_chart(self):
        """Show investment timeline chart"""
        df = self._get_csv_data()
        if df is not None and not df.empty:
            fig = ChartGenerator.create_investment_timeline(df)
            self.open_plot_in_window(fig, "Investment Timeline")
        else:
            messagebox.showwarning("No Data", "No investment history found.")

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
                    title="📊 Strategy Comparison: Portfolio Value",
                    xaxis_title="Year (Relative)",
                    yaxis=dict(title="(unused)", visible=False),
                    yaxis2=dict(title="Portfolio Value ($)", overlaying="y", side="right"),
                    legend=dict(x=0.01, y=0.99),
                    template="plotly_dark"
                )

                # Show chart using plotly offline + webview approach
                self.root.after(0, lambda: self.open_plot_in_window(fig, "Strategy Comparison"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        # Run in background thread
        self.executor.submit(_generate_chart)

    def open_plot_in_window(self, fig, title="Chart"):
        """Open plot in embedded window using pywebview or fallback to browser"""
        try:
            # Create a temp HTML file using plotly offline
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
                plot(fig, filename=temp_file.name, auto_open=False, include_plotlyjs='cdn')
                
                if WEBVIEW_AVAILABLE:
                    # Open in embedded window using pywebview (preferred)
                    webview.create_window(title, temp_file.name, width=1000, height=700)
                    webview.start()
                else:
                    # Fallback: open in default browser
                    webbrowser.open(f'file://{temp_file.name}')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open chart: {str(e)}")

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
            self.stock_tabs.add(tab_total, text="📊 All Stocks + Total")

            fig_total = ChartGenerator.create_growth_chart(pivoted_cumsum, mode, y_label)
            ttk.Button(
                tab_total, 
                text="Open Interactive Chart", 
                command=lambda: self.open_plot_in_window(fig_total, f"Cumulative {mode} Growth")
            ).pack(pady=20)

            # Create individual stock tabs
            for ticker in pivoted_cumsum.columns[:-1]:  # Exclude 'Total'
                tab = ttk.Frame(self.stock_tabs)
                self.stock_tabs.add(tab, text=ticker)

                fig = ChartGenerator.create_individual_chart(pivoted_cumsum, ticker, mode, y_label)
                ttk.Button(
                    tab, 
                    text="Open Interactive Chart", 
                    command=lambda f=fig, t=ticker: self.open_plot_in_window(f, f"{t} Growth")
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