# -*- coding: utf-8 -*-
"""
Utility functions for the dividend tracker application
"""

import os
import tempfile
import webbrowser
from pathlib import Path

# Try to import pywebview, fallback to browser if not available
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("pywebview not available, charts will open in default browser")


def open_plot_in_window(fig, title="Chart"):
    """Open plot in embedded window using pywebview or fallback to browser"""
    try:
        from plotly.offline import plot
        
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
        raise Exception(f"Failed to open chart: {str(e)}")


def ensure_directory_exists(file_path: str):
    """Ensure the directory for a file path exists"""
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def format_currency(amount: float, show_sign: bool = False) -> str:
    """Format a number as currency"""
    if show_sign and amount >= 0:
        return f"+${amount:,.2f}"
    return f"${amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format a number as percentage"""
    return f"{value:.{decimal_places}f}%"


def mask_api_key(api_key: str) -> str:
    """Mask an API key for display purposes"""
    if not api_key or api_key == 'demo':
        return api_key
    
    if len(api_key) > 8:
        return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
    else:
        return '*' * len(api_key)


def validate_investment_amount(amount_str: str) -> float:
    """Validate and parse investment amount string"""
    try:
        # Remove currency symbols and commas
        cleaned = amount_str.replace("$", "").replace(",", "").strip()
        amount = float(cleaned)
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        return amount
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError("Please enter a valid dollar amount")
        raise e


def get_documents_path() -> str:
    """Get the user's Documents directory path"""
    return os.path.join(os.path.expanduser("~"), "Documents")


def get_default_csv_path() -> str:
    """Get the default CSV file path"""
    return os.path.join(get_documents_path(), "dividend_history.csv")


def get_default_cache_path() -> str:
    """Get the default cache file path"""
    return os.path.join(get_documents_path(), "market_data_cache.json")


class ProgressTracker:
    """Simple progress tracking for long operations"""
    
    def __init__(self, total_steps: int, callback=None):
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
    
    def update(self, step_name: str = ""):
        """Update progress"""
        self.current_step += 1
        if self.callback:
            progress_percent = (self.current_step / self.total_steps) * 100
            self.callback(self.current_step, self.total_steps, step_name, progress_percent)
    
    def is_complete(self) -> bool:
        """Check if progress is complete"""
        return self.current_step >= self.total_steps


def safe_float_conversion(value, default: float = 0.0) -> float:
    """Safely convert a value to float with fallback"""
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int_conversion(value, default: int = 0) -> int:
    """Safely convert a value to int with fallback"""
    try:
        if value is None or value == '':
            return default
        return int(float(value))  # Handle string floats like "123.0"
    except (ValueError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def create_backup_filename(original_filename: str) -> str:
    """Create a backup filename with timestamp"""
    from datetime import datetime
    
    path = Path(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    
    return str(path.parent / backup_name)