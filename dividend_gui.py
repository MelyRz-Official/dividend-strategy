import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sv_ttk
import os
from datetime import datetime
import plotly.graph_objects as go
from tkinter import StringVar
from tkinter.ttk import Notebook
from plotly.offline import plot
import webview
import tempfile
from plotly.offline import plot
import os

CSV_FILENAME = os.path.join(os.path.expanduser("~"), "Documents", "dividend_history.csv")


DIVIDEND_STOCKS = [
    {"ticker": "O", "name": "Realty Income", "yield": 0.055, "allocation": 0.20},
    {"ticker": "TROW", "name": "T. Rowe Price", "yield": 0.043, "allocation": 0.15},
    {"ticker": "SCHD", "name": "SCHD", "yield": 0.038, "allocation": 0.15},
    {"ticker": "HDV", "name": "HDV", "yield": 0.038, "allocation": 0.10},
    {"ticker": "MO", "name": "Altria", "yield": 0.08, "allocation": 0.10},
    {"ticker": "APLE", "name": "Apple Hospitality REIT", "yield": 0.06, "allocation": 0.10},
    {"ticker": "ABBV", "name": "AbbVie", "yield": 0.04, "allocation": 0.10},
    {"ticker": "VZ", "name": "Verizon", "yield": 0.066, "allocation": 0.10},
]

class DividendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Dividend Strategy Calculator")
        self.root.geometry("1400x400")
        self.data = []
        sv_ttk.set_theme("dark")

        # --- Layout Split: LEFT (inputs/table) + RIGHT (charts) ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="y", expand=False, padx=(0, 15))

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        # LEFT PANEL CONTENT ------------------------------
        input_frame = ttk.Frame(left_panel)
        input_frame.pack(pady=5)
        ttk.Label(input_frame, text="Enter Investment Amount ($):").pack(side="left", padx=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.pack(side="left", padx=5)
        self.amount_entry.insert(0, "100.00")
        ttk.Button(input_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            left_panel,
            columns=("Ticker", "Amount", "Yield", "Monthly", "Annual"),
            show="headings", height=8
        )
        headers = {
            "Ticker": "Ticker",
            "Amount": "Allocation $",
            "Yield": "Yield (%)",
            "Monthly": "Monthly Dividend",
            "Annual": "Annual Dividend"
        }
        for col, label in headers.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, anchor="center", width=130)

        self.tree.tag_configure("evenrow", background="#1e1e1e")
        self.tree.tag_configure("oddrow", background="#2a2a2a")
        self.tree.pack(pady=10)

        self.total_label = ttk.Label(left_panel, text="", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(pady=5)

        button_frame = ttk.Frame(left_panel)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="\U0001F4BE Save to History", command=self.save_csv).pack(side="left", padx=5)

        # RIGHT PANEL CONTENT ------------------------------
        self.tab_notebook = Notebook(right_panel)
        self.tab_notebook.pack(fill="both", expand=True)

        # Growth Charts Tab
        growth_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(growth_tab, text="\U0001F4C8 Growth Charts")

        self.view_mode = StringVar(value="Annual")
        ttk.Label(growth_tab, text="View Mode:").pack(pady=5)
        ttk.Combobox(
            growth_tab,
            textvariable=self.view_mode,
            values=["Annual", "Monthly"],
            state="readonly", width=10
        ).pack(pady=5)

        ttk.Button(growth_tab, text="Generate Charts", command=self.generate_growth_tabs).pack(pady=5)

        self.stock_tabs = Notebook(growth_tab)
        self.stock_tabs.pack(fill="both", expand=True, pady=5)

        # Strategy Comparison Tab
        comparison_tab = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(comparison_tab, text="\U0001F4CA Strategy Comparison")
        ttk.Button(comparison_tab, text="Open Strategy Chart", command=self.show_comparison_chart).pack(pady=20)

    def calculate(self):
        try:
            amount = float(self.amount_entry.get())
            self.latest_investment = amount
            self.data = []
            self.tree.delete(*self.tree.get_children())

            for i, stock in enumerate(DIVIDEND_STOCKS):
                allocated = amount * stock["allocation"]
                annual_dividend = allocated * stock["yield"]
                monthly_dividend = annual_dividend / 12
                tag = "evenrow" if i % 2 == 0 else "oddrow"

                self.tree.insert("", "end", values=(
                    stock["ticker"],
                    f"${allocated:.2f}",
                    f"{stock['yield'] * 100:.2f}%",
                    f"${monthly_dividend:.2f}",
                    f"${annual_dividend:.2f}"
                ), tags=(tag,))

                self.data.append({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ticker": stock["ticker"],
                    "Company": stock["name"],
                    "Amount Invested": round(allocated, 2),
                    "Yield (%)": round(stock["yield"] * 100, 2),
                    "Monthly Dividend": round(monthly_dividend, 2),
                    "Estimated Annual Dividend": round(annual_dividend, 2),
                    "Total Investment": round(amount, 2)
                })

            total_dividend = sum(item["Estimated Annual Dividend"] for item in self.data)
            self.total_dividend = total_dividend
            self.total_label.config(text=f"Total Estimated Annual Dividend: ${total_dividend:.2f}")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid dollar amount.")

    def save_csv(self):
        try:
            if not self.data:
                messagebox.showwarning("No Data", "Please calculate first before saving.")
                return
            df = pd.DataFrame(self.data)
            file_exists = os.path.exists(CSV_FILENAME)
            df.to_csv(CSV_FILENAME, mode='a', header=not file_exists, index=False)
            messagebox.showinfo("Saved", f"Appended to {CSV_FILENAME}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_growth_chart(self):
        try:
            if not os.path.exists(CSV_FILENAME):
                messagebox.showwarning("No History", f"No file named {CSV_FILENAME} found.")
                return

            df = pd.read_csv(CSV_FILENAME)
            if not {"Timestamp", "Ticker", "Estimated Annual Dividend"}.issubset(df.columns):
                messagebox.showerror("Data Error", "CSV missing necessary columns.")
                return

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])

            # Group by timestamp and ticker to get stock-by-stock growth
            grouped = df.groupby(["Timestamp", "Ticker"])["Estimated Annual Dividend"].sum().reset_index()

            # Pivot so we have columns for each stock's dividend over time
            pivoted = grouped.pivot(index="Timestamp", columns="Ticker", values="Estimated Annual Dividend").fillna(0)

            # Calculate total
            pivoted["Total"] = pivoted.sum(axis=1)

            # Create the plot
            fig = go.Figure()

            # Add one line per ticker
            for ticker in pivoted.columns[:-1]:  # Exclude "Total"
                fig.add_trace(go.Scatter(
                    x=pivoted.index,
                    y=pivoted[ticker],
                    mode="lines+markers",
                    name=f"{ticker} Dividend"
                ))

            # Add total line
            fig.add_trace(go.Scatter(
                x=pivoted.index,
                y=pivoted["Total"],
                mode="lines+markers",
                name="Total Dividend",
                line=dict(color="white", width=3, dash="dash")
            ))

            fig.update_layout(
                title="📈 Individual Stock & Total Dividend Growth",
                xaxis_title="Date",
                yaxis_title="Annual Dividend ($)",
                legend=dict(x=0.01, y=0.99),
                template="plotly_dark"
            )

            fig.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_comparison_chart(self):
        try:
            if not os.path.exists(CSV_FILENAME):
                messagebox.showwarning("No History", f"No file named {CSV_FILENAME} found.")
                return

            df = pd.read_csv(CSV_FILENAME)
            if not {"Timestamp", "Amount Invested"}.issubset(df.columns):
                messagebox.showerror("Data Error", "CSV missing required columns.")
                return

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            df["Year"] = df["Timestamp"].dt.year

            # ✅ Group by year, summing the *actual* individual amounts invested
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

            # Normalize actual data to match year index (e.g. first year is 1)
            actual_years = actual_invest["Year"] - actual_invest["Year"].min() + 1
            fig.add_trace(go.Scatter(
                x=actual_years,
                y=actual_invest["Amount Invested"],
                name="Actual Portfolio Value",
                mode="lines+markers",
                yaxis="y2"
            ))

            fig.update_layout(
                title="📊 Strategy Comparison: Portfolio Value Only",
                xaxis_title="Year (Relative)",
                yaxis=dict(title="(unused)", visible=False),
                yaxis2=dict(title="Portfolio Value ($)", overlaying="y", side="right"),
                legend=dict(x=0.01, y=0.99),
                template="plotly_dark"
            )

            # Show it via embedded window
            html_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            plot(fig, filename=html_path.name, auto_open=False, include_plotlyjs='cdn')
            webview.create_window("Strategy Comparison", html_path.name, width=900, height=600)
            webview.start()

        except Exception as e:
            messagebox.showerror("Error", str(e))



    def open_plot_in_window(self, fig, title="Chart"):
        try:
            # Create a temp HTML file
            html_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            plot(fig, filename=html_path.name, auto_open=False, include_plotlyjs='cdn')
            # Open in embedded window
            webview.create_window(title, html_path.name, width=800, height=600)
            webview.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_growth_tabs(self):
        try:
            if not os.path.exists(CSV_FILENAME):
                messagebox.showwarning("No History", "No dividend_history.csv found.")
                return

            df = pd.read_csv(CSV_FILENAME)
            if not {"Timestamp", "Ticker", "Estimated Annual Dividend", "Monthly Dividend"}.issubset(df.columns):
                messagebox.showerror("Data Error", "CSV missing required columns.")
                return

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            mode = self.view_mode.get()
            y_col = "Estimated Annual Dividend" if mode == "Annual" else "Monthly Dividend"
            y_label = f"{mode} Dividend ($)"

            # Clear old tabs
            for tab_id in self.stock_tabs.tabs():
                self.stock_tabs.forget(self.stock_tabs.nametowidget(tab_id))

            # Prepare data
            grouped = df.groupby(["Timestamp", "Ticker"])[y_col].sum().reset_index()
            pivoted = grouped.pivot(index="Timestamp", columns="Ticker", values=y_col).fillna(0)
            pivoted["Total"] = pivoted.sum(axis=1)

            # Total + All Stocks Tab
            tab_total = ttk.Frame(self.stock_tabs)
            self.stock_tabs.add(tab_total, text="📊 All Stocks + Total")

            fig_total = go.Figure()
            for ticker in pivoted.columns[:-1]:  # skip Total
                fig_total.add_trace(go.Scatter(
                    x=pivoted.index,
                    y=pivoted[ticker],
                    mode="lines+markers",
                    name=f"{ticker}"
                ))
            fig_total.add_trace(go.Scatter(
                x=pivoted.index,
                y=pivoted["Total"],
                mode="lines+markers",
                name="Total",
                line=dict(color="white", width=3, dash="dash")
            ))

            fig_total.update_layout(
                title=f"{mode} Dividend Growth Over Time",
                xaxis_title="Date",
                yaxis_title=y_label,
                template="plotly_dark"
            )

            ttk.Button(tab_total, text="Open Interactive Chart", command=lambda: self.open_plot_in_window(fig_total)).pack(pady=10)

            # Per-Stock Tabs
            for ticker in pivoted.columns[:-1]:
                tab = ttk.Frame(self.stock_tabs)
                self.stock_tabs.add(tab, text=ticker)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pivoted.index,
                    y=pivoted[ticker],
                    mode="lines+markers",
                    name=ticker
                ))
                fig.update_layout(
                    title=f"{ticker} - {mode} Dividend Growth",
                    xaxis_title="Date",
                    yaxis_title=y_label,
                    template="plotly_dark"
                )

                ttk.Button(tab, text="Open Interactive Chart", command=lambda f=fig: self.open_plot_in_window(f)).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DividendApp(root)
    root.mainloop()
