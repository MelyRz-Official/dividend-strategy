#!/usr/bin/env python3
"""
Clean Unicode characters from Python files for PyInstaller compatibility
"""

import os
import re
from pathlib import Path

# Map Unicode characters to ASCII alternatives
UNICODE_REPLACEMENTS = {
    # Emojis to text
    '📡': '[API]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '📊': '[DATA]',
    '🚀': '[LAUNCH]',
    '💰': '[MONEY]',
    '📈': '[CHART]',
    '🔄': '[REFRESH]',
    '💾': '[SAVE]',
    '🌐': '[WEB]',
    '🎯': '[TARGET]',
    '📋': '[LIST]',
    '🧮': '[CALC]',
    '⏰': '[TIME]',
    '🔒': '[SECURE]',
    '🎉': '[SUCCESS]',
    
    # Check marks and X's
    '✓': '[OK]',
    '✗': '[FAIL]',
    '×': 'x',
    
    # Arrows and symbols
    '→': '->',
    '←': '<-',
    '↑': '^',
    '↓': 'v',
    '•': '*',
    '–': '-',
    '—': '--',
    '"': '"',
    '"': '"',
    ''': "'",
    ''': "'",
}

def clean_unicode_in_file(file_path):
    """Remove Unicode characters from a Python file"""
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace Unicode characters
        for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
            content = content.replace(unicode_char, replacement)
        
        # Check if any changes were made
        if content != original_content:
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Cleaned Unicode in {file_path} (backup: {backup_path})")
            return True
        else:
            print(f"- No Unicode found in {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def clean_all_python_files():
    """Clean Unicode from all Python files in current directory"""
    python_files = [
        'dividend_gui.py',
        'yahoo_finance_provider.py',
        'portfolio_manager.py',
        'chart_generator.py',
        'data_processor.py',
        'utils.py'
    ]
    
    cleaned_files = 0
    for file_path in python_files:
        if os.path.exists(file_path):
            if clean_unicode_in_file(file_path):
                cleaned_files += 1
        else:
            print(f"- File not found: {file_path}")
    
    print(f"\nCleaned {cleaned_files} files")
    return cleaned_files > 0

def restore_backups():
    """Restore files from backups"""
    backup_files = list(Path('.').glob('*.py.backup'))
    
    if not backup_files:
        print("No backup files found")
        return
    
    for backup_file in backup_files:
        original_file = str(backup_file).replace('.backup', '')
        try:
            # Restore from backup
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(original_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Remove backup
            backup_file.unlink()
            print(f"✓ Restored {original_file}")
            
        except Exception as e:
            print(f"✗ Error restoring {original_file}: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        restore_backups()
    else:
        print("Cleaning Unicode characters for PyInstaller compatibility...")
        clean_all_python_files()
        print("\nTo restore original files: python clean_unicode.py --restore")