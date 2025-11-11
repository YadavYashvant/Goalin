# Goalin

<div align="center">

**A productivity tracking service for Linux**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GTK Version](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)

</div>

## 📖 Overview

Goalin is a productivity tracking service for Linux that monitors your application usage and generates daily reports. Track how you spend your time, identify patterns, and make informed decisions about your workflow.

Now includes optional AI-powered insights using Google Gemini for smart categorization and productivity analysis.

## 🤖 AI Features

Optional AI integration using Google Gemini:

- **Smart Categorization**: Automatically categorizes installed applications
- **Productivity Analysis**: Context-aware scoring beyond simple time tracking
- **Daily Insights**: Observations about your work patterns and focus time
- **Recommendations**: Personalized suggestions to improve productivity
- **Fast & Responsive**: Async loading with caching prevents UI freezing

Setup is optional - the app works fine without AI. If enabled, you'll need your own (free) Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## 📸 Screenshots

<!-- TODO: Add screenshots -->

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/3ea5ef56-99e4-445d-9ff3-5ee3655124fa" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6bd715d6-8d19-4f60-bfc0-61a031e7c292" />



### ✨ Features

- **🤖 AI-Powered Analysis** (Optional)
  - Smart app categorization
  - Productivity scoring with insights
  - Personalized recommendations
  - Async loading with caching
  
- **🎨 Modern UI**
  - Stack-based navigation
  - Circular progress indicators
  - Activity heatmaps
  - Card-based layout
  
- **📊 Dashboard**
  - Circular progress stats
  - 24-hour activity heatmap
  - Top 8 applications with categories
  - Time breakdown by category
  
- **⏰ Timeline View**
  - Hourly breakdown with color coding
  - Top apps per hour
  - Window titles and durations
  
- **🔍 Insights & Analytics**
  - Browser activity (Firefox)
  - Top websites visited
  - Productivity scoring
  
- **Core Features**
  - Automatic activity tracking
  - Daily reports (text, JSON, HTML)
  - Idle time detection
  - Local SQLite database
  - Systemd integration
  - X11 & Wayland support
  
- **⏰ Detailed Timeline View**
  - Hourly breakdown with productivity color coding (green/yellow/red)
  - Top 3 apps per hour with window titles
  - Duration and activity count per time block
  - Visual progress bars for each application
  
- **� Insights & Analytics**
  - **Browser Activity**: Firefox integration with category breakdown
  - **Top Websites**: Ranked list of most-visited domains
  - **Productivity Score**: Calculated based on development vs. leisure time
  - **Time Breakdown**: Development, browser, and communication time analysis
  
- **📄 Integrated Report Viewer**
  - HTML reports display directly in the app
  - No external browser needed
  - Beautiful empty states with gradient backgrounds
  
- **🔍 Automatic Activity Tracking**: Monitors active windows and applications in real-time
- **🤖 AI Setup Wizard**: First-run configuration guide for API key setup
- **📈 Daily Reports**: Automatically generates detailed reports with AI insights at the end of each day
- **📁 Smart Categorization**: AI intelligently categorizes applications (Development, Browser, Communication, etc.)
- **⚡ Performance Optimized**: Multi-tier caching system (config, app categories, AI insights)
- **⏱️ Idle Detection**: Distinguishes between active usage and idle time
- **🗄️ Local SQLite Database**: All your data stays on your machine - complete privacy
- **📄 Multiple Report Formats**: Generate reports in Text, JSON, and HTML formats with AI insights
- **🐧 Systemd Integration**: Runs as a background service that starts automatically
- **🎯 X11 & Wayland Support**: Works with both display servers (including Hyprland)

## 🚀 Installation

### From AUR (Arch Linux)

```bash

yay -S goalin

```

### From Source

```bash
# Clone the repository
git clone https://github.com/YadavYashvant/Goalin.git
cd Goalin

# Install dependencies
pip install -r requirements.txt

# Install the package
python setup.py install --user

# Install systemd service
mkdir -p ~/.config/systemd/user/
cp goalin.service ~/.config/systemd/user/

# Install desktop file
mkdir -p ~/.local/share/applications/
cp goalin.desktop ~/.local/share/applications/

# Optional: Run setup wizard for AI features
goalin-setup
```

### Quick Start

```bash
# 1. Start the tracking daemon
systemctl --user enable --now goalin.service

# 2. Run the AI setup wizard (optional but recommended)
goalin-setup

# 3. Launch the GUI
goalin-gui
```

## 📋 Dependencies

- Python 3.9+
- PyGObject, GTK4, libadwaita
- python-xlib (for X11)
- pytz
- google-generativeai (optional, for AI features)

Get a free API key at [Google AI Studio](https://makersuite.google.com/app/apikey) to enable AI features.

## 🎮 Usage

### Starting the Tracking Service

```bash
# Enable and start the systemd service
systemctl --user enable goalin.service
systemctl --user start goalin.service

# Check service status
systemctl --user status goalin.service

# View logs
journalctl --user -u goalin.service -f
```

### Opening the GUI

```bash
goalin-gui
# Or find "Goalin" in your application launcher
```

On first launch, the setup wizard will help you configure AI features (optional).

### Generating Reports Manually

```bash
# Generate report for yesterday (default)
goalin-report

# Generate report for a specific date
goalin-report --date 2025-10-25

# Generate only HTML report
goalin-report --format html

# Generate all formats (text, json, html)
goalin-report --format all
```

## 📂 File Locations

- **Configuration**: `~/.config/goalin/`
  - `config.json` - General settings
  - `ai_config.json` - AI API key (encrypted storage recommended)
- **Database**: `~/.local/share/goalin/activity.db`
- **Reports**: `~/.local/share/goalin/reports/`
- **Logs**: `~/.local/share/goalin/logs/`
- **Cache**: `~/.local/share/goalin/`
  - `app_categories.json` - Cached app categorizations
  - `ai_insights_cache.json` - Cached daily AI analysis

## ⚙️ Configuration

Edit `src/goalin/config.py` to customize:

```python
POLL_INTERVAL = 5  # seconds between activity checks
IDLE_THRESHOLD = 300  # seconds before considering idle
REPORT_TIME = "20:00"  # daily report generation time
```

For AI features, run `goalin-setup` or edit `~/.config/goalin/ai_config.json`.

## 📊 Report Examples

### Text Report
```
============================================================
GOALIN - Daily Productivity Report
Date: Saturday, October 26, 2025
============================================================

OVERVIEW
------------------------------------------------------------
Total Active Time:    5h 23m
Total Idle Time:      2h 15m
Total Tracked Time:   7h 38m
Most Used App:        VSCode

TIME BY CATEGORY
------------------------------------------------------------
Development................... 3h 15m (60.3%)
Browser....................... 1h 30m (27.9%)
Communication................. 0h 38m (11.8%)
```

### HTML Report
Beautiful responsive reports with charts and visualizations. Includes AI insights when enabled.

### JSON Report
Machine-readable format for integrations.

## 🔒 Privacy

All data stays on your machine:
- Local SQLite database
- No telemetry or tracking
- Open source - audit the code
- Your control over data

When AI is enabled, only anonymized usage stats (time spent, categories, app names) are sent to Google Gemini. Your API key is stored locally.

## 🛠️ Development

### Project Structure

```
Goalin/
├── src/goalin/
│   ├── __init__.py
│   ├── config.py        # Configuration and constants
│   ├── database.py      # SQLite database management
│   ├── tracker.py       # Activity tracking logic
│   ├── daemon.py        # Background service daemon
│   ├── report.py        # Report generation with AI
│   ├── ai_assistant.py  # AI integration (Gemini API)
│   ├── setup_wizard.py  # First-run AI setup wizard
│   └── gui.py           # GTK4 GUI application
├── setup.py             # Python package setup
├── PKGBUILD            # Arch Linux package build script
├── goalin.service      # Systemd user service
├── goalin.desktop      # Desktop application entry
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🤝 Contributing

Contributions welcome! Open an issue or submit a pull request.

## 🐛 Known Issues

- Limited Wayland support (works best on Sway)
- Some apps may not expose window titles
- AI rate limits on free tier (see Google AI Studio for details)

## 📝 TODO

- [x] AI-powered productivity analysis
- [x] Smart application categorization
- [x] Performance optimization with caching
- [ ] Weekly and monthly reports
- [ ] Productivity goals
- [ ] Data export/import
- [ ] Configuration GUI

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**YadavYashvant**  
GitHub: [@YadavYashvant](https://github.com/YadavYashvant)

---

Made with ❤️ for the Linux community
