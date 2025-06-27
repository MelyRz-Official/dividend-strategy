# PowerShell script to build Dividend Tracker executable
# Fixes Unicode and network issues

Write-Host "Building Dividend Tracker (Fixed Version)..." -ForegroundColor Green

# Step 1: Clean Unicode characters
Write-Host "Step 1: Cleaning Unicode characters..." -ForegroundColor Yellow
python clean_unicode.py

# Step 2: Set encoding environment
Write-Host "Step 2: Setting UTF-8 encoding..." -ForegroundColor Yellow
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Step 3: Clean previous builds
Write-Host "Step 3: Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }

# Step 4: Build executable with all necessary modules
Write-Host "Step 4: Building executable..." -ForegroundColor Yellow
pyinstaller `
  --onefile `
  --windowed `
  --collect-all plotly `
  --collect-all yfinance `
  --collect-all pandas `
  --collect-all requests `
  --hidden-import sv_ttk `
  --hidden-import tkinter `
  --hidden-import tkinter.ttk `
  --hidden-import json `
  --hidden-import datetime `
  --hidden-import pathlib `
  --hidden-import concurrent.futures `
  --hidden-import threading `
  --hidden-import tempfile `
  --hidden-import webbrowser `
  --hidden-import urllib3 `
  --hidden-import certifi `
  --clean `
  --noconfirm `
  --name="DividendTracker" `
  dividend_gui.py

# Step 5: Check if build was successful
if (Test-Path "dist\DividendTracker.exe") {
    $size = (Get-Item "dist\DividendTracker.exe").Length / 1MB
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Executable: dist\DividendTracker.exe ($([math]::Round($size, 1)) MB)" -ForegroundColor Green
    
    # Step 6: Restore original files
    Write-Host "Step 6: Restoring original files..." -ForegroundColor Yellow
    python clean_unicode.py --restore
    
    Write-Host "Ready to distribute! The executable should now work properly." -ForegroundColor Cyan
} else {
    Write-Host "BUILD FAILED! Check error messages above." -ForegroundColor Red
}