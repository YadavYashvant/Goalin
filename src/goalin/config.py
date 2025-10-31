#!/usr/bin/env python3
"""
Configuration management for Goalin
"""

import os
from pathlib import Path

# Application directories
CONFIG_DIR = Path.home() / '.config' / 'goalin'
DATA_DIR = Path.home() / '.local' / 'share' / 'goalin'
CACHE_DIR = Path.home() / '.cache' / 'goalin'

# Database path
DB_PATH = DATA_DIR / 'activity.db'

# Tracking settings
POLL_INTERVAL = 5  # seconds between activity checks
IDLE_THRESHOLD = 300  # seconds before considering user idle

# Report settings
REPORT_TIME = "20:00"  # Time to generate daily report (24-hour format)
REPORT_DIR = DATA_DIR / 'reports'

# Categories for application classification
APP_CATEGORIES = {
    'Development': [
        'code', 'vscode', 'vim', 'emacs', 'jetbrains', 'pycharm', 'intellij',
        'eclipse', 'netbeans', 'atom', 'sublime', 'gedit', 'kate', 'terminal',
        'konsole', 'gnome-terminal', 'kitty', 'alacritty', 'tilix'
    ],
    'Browser': [
        'firefox', 'chrome', 'chromium', 'brave', 'edge', 'safari', 'opera',
        'vivaldi', 'qutebrowser', 'epiphany'
    ],
    'Communication': [
        'slack', 'discord', 'teams', 'zoom', 'telegram', 'signal', 'whatsapp',
        'skype', 'element', 'thunderbird', 'evolution', 'geary'
    ],
    'Media': [
        'vlc', 'mpv', 'spotify', 'rhythmbox', 'clementine', 'audacious',
        'gimp', 'inkscape', 'blender', 'kdenlive', 'obs'
    ],
    'Office': [
        'libreoffice', 'writer', 'calc', 'impress', 'okular', 'evince',
        'pdf', 'document'
    ],
    'Gaming': [
        'steam', 'game', 'minecraft', 'lutris', 'playonlinux', 'wine'
    ],
    'System': [
        'settings', 'systemsettings', 'nautilus', 'dolphin', 'thunar',
        'nemo', 'pcmanfm', 'filemanager'
    ],
}

def ensure_directories():
    """Create necessary directories if they don't exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

def get_category(app_name: str) -> str:
    """
    Determine the category of an application based on its name
    Uses AI categorization if available, fallback to keyword matching
    
    Args:
        app_name: Name of the application
        
    Returns:
        Category name or 'Other'
    """
    # Try AI categorization first
    try:
        from .ai_assistant import AIAssistant
        ai = AIAssistant()
        if ai.is_configured():
            return ai.get_app_category(app_name)
    except Exception:
        pass  # Fallback to keyword matching
    
    # Fallback: keyword matching
    app_name_lower = app_name.lower()
    
    for category, keywords in APP_CATEGORIES.items():
        if any(keyword in app_name_lower for keyword in keywords):
            return category
    
    return 'Other'

def is_setup_complete() -> bool:
    """Check if initial setup has been completed"""
    setup_file = CONFIG_DIR / '.setup_complete'
    return setup_file.exists()
