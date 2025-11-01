# Goalin

<div align="center">

**A productivity tracking service for Linux**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GTK Version](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)

</div>

## 📖 Overview

Goalin is a locally-run productivity tracking service for Linux that monitors your application usage and generates comprehensive daily reports. It helps you understand how you spend your time on your computer, identify productivity patterns, and make data-driven decisions to improve your workflow.

**NEW: Now with AI-powered insights!** Goalin integrates with Google Gemini to provide intelligent productivity analysis, smart app categorization, and personalized recommendations—all while keeping your data local and private.

## 🤖 AI Features

Goalin leverages Google's Gemini AI to supercharge your productivity tracking:

- **🎯 Smart App Categorization**: Automatically categorizes all installed applications into meaningful groups (Development, Communication, Entertainment, etc.)
- **📊 AI Productivity Scoring**: Advanced analysis that goes beyond simple time tracking, considering context and work patterns
- **💡 Intelligent Insights**: Daily observations about your productivity patterns, focus time, and work habits
- **🚀 Personalized Recommendations**: Actionable suggestions tailored to your specific usage patterns
- **⚡ Performance Optimized**: 
  - Async loading keeps UI responsive
  - Multi-tier caching (config → app categories → daily insights)
  - Batch processing reduces API calls
  - Loading indicators for smooth UX
- **🔒 Privacy First**: Your API key, your data, your control

### How It Works

1. **Setup**: Run the setup wizard to configure your Google Gemini API key (free tier available)
2. **Categorization**: AI scans and categorizes your installed applications (one-time process)
3. **Daily Analysis**: As you work, Goalin tracks your activity and generates AI insights at day's end
4. **Smart Caching**: Insights are cached per day—instant loading when revisiting previous days
5. **View & Learn**: Beautiful dashboard shows your productivity score, key insights, and recommendations

## 📸 Screenshots

<!-- TODO: Add screenshots here -->
- Dashboard with AI productivity score
- Timeline view with categorized apps
- Insights page with AI recommendations
- HTML report with AI analysis

### ✨ Features

- **🤖 AI-Powered Productivity Analysis**: Intelligent insights using Google Gemini
  - **Smart App Categorization**: AI automatically categorizes installed applications
  - **Productivity Scoring**: Advanced AI analysis of daily productivity patterns
  - **Personalized Insights**: AI-generated observations about your work habits
  - **Actionable Recommendations**: AI suggests improvements to boost productivity
  - **Performance Optimized**: Async loading with caching for smooth, responsive UI
  - **Privacy First**: Your own API key, all data stays local
  
- **🎨 Modern Dashboard UI**: Completely redesigned interface with professional aesthetics
  - Stack-based navigation (Overview, Timeline, Insights, Report)
  - Custom circular progress bars and activity heatmaps
  - Color-coded productivity levels and visual indicators
  - Gradient stat cards with smooth animations
  - Card-based layout with proper spacing and shadows
  - Loading spinners for async operations
  
- **📊 Rich Overview Dashboard**
  - **AI Productivity Score**: ML-powered analysis with contextual insights
  - **Circular Progress Stats**: Active time, idle time, app count, and most-used app
  - **Activity Heatmap**: 24-hour visual representation of activity intensity
  - **Top Applications**: Your 8 most-used apps with icons, AI categories, and progress bars
  - **Category Grid**: Visual breakdown of time spent in each category
  - **Key Insights**: AI-generated observations displayed prominently
  - **Smart Recommendations**: Actionable tips to improve productivity
  
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

### From AUR (Arch Linux) (Yet to be published!)

```bash
# Using yay
yay -S goalin

# Using paru
paru -S goalin

# Manual installation with makepkg
git clone https://aur.archlinux.org/goalin.git
cd goalin
makepkg -si
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
- PyGObject (python-gobject)
- GTK4
- libadwaita
- python-xlib (for X11 support)
- pytz
- google-generativeai (for AI features)

### AI Features (Optional)

To use AI-powered productivity analysis, you'll need:
- A Google Gemini API key (free tier available at [Google AI Studio](https://makersuite.google.com/app/apikey))
- The app will guide you through setup on first launch with the setup wizard

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
# Launch from terminal
goalin-gui

# Or find "Goalin" in your application launcher

# First launch: Setup wizard will guide you through AI configuration
# - Enter your Google Gemini API key (optional but recommended)
# - AI will categorize your installed applications
# - Start tracking with intelligent insights!
```

### Configuring AI Features

```bash
# Run the setup wizard anytime
goalin-setup

# The wizard will:
# 1. Prompt for your Google Gemini API key
# 2. Scan and categorize installed applications
# 3. Configure AI-powered productivity analysis
```

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

Configuration can be customized by editing `src/goalin/config.py`:

```python
# Tracking settings
POLL_INTERVAL = 5  # seconds between activity checks
IDLE_THRESHOLD = 300  # seconds before considering user idle

# Report settings
REPORT_TIME = "20:00"  # Time to generate daily report (24-hour format)
```

### AI Configuration

AI features are configured through the setup wizard or `~/.config/goalin/ai_config.json`:

```json
{
  "api_key": "your-gemini-api-key",
  "model": "gemini-2.0-flash",
  "enabled": true
}
```

**Getting an API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key (free tier available)
4. Run `goalin-setup` and paste your key

**Privacy Note:** Your API key is stored locally and only used for AI analysis. All data remains on your machine.

### Application Categories

Application categories are now intelligently managed by AI, but you can still customize them in `config.py`:

```python
APP_CATEGORIES = {
    'Development': ['code', 'vscode', 'vim', 'pycharm', ...],
    'Browser': ['firefox', 'chrome', 'brave', ...],
    'Communication': ['slack', 'discord', 'telegram', ...],
    # Add your own categories...
    # AI will learn and categorize new apps automatically
}
```

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
Beautiful, responsive HTML reports with charts, visualizations, and AI-powered insights including:
- AI Productivity Score with detailed breakdown
- Key insights about your work patterns
- Personalized recommendations for improvement
- Smart categorization of applications

### JSON Report
Machine-readable format for integration with other tools and services, including AI analysis data.

## 🔒 Privacy

Goalin takes your privacy seriously:

- ✅ **100% Local**: All data is stored locally on your machine
- ✅ **No Cloud Storage**: Database and reports never leave your computer
- ✅ **Your Own API Key**: AI features use your personal Google Gemini key
- ✅ **Minimal API Calls**: Smart caching reduces API usage (one call per day analyzed)
- ✅ **No Tracking**: We don't track your usage or collect analytics
- ✅ **Open Source**: Full transparency - audit the code yourself
- ✅ **Your Control**: Delete or export your data anytime
- ✅ **Secure Storage**: API keys stored locally in config files

**AI Privacy:** When AI features are enabled, only anonymized usage statistics (time spent, categories, app names) are sent to Google Gemini for analysis. No personal information, file contents, or sensitive data is transmitted.

## ⚡ Performance

Goalin is designed to be lightweight and responsive:

- **Minimal Resource Usage**: Background daemon uses < 50MB RAM
- **Efficient Tracking**: Polling-based system with configurable intervals (default: 5s)
- **Smart Caching**: Three-tier cache system prevents redundant API calls
  - Configuration cache (persistent)
  - App categorization cache (on-demand)
  - Daily insights cache (24-hour validity)
- **Async UI**: AI analysis runs in background threads—UI never freezes
- **Loading Indicators**: Smooth spinners and progress feedback
- **Optimized Database**: Indexed SQLite database for fast queries
- **Batch Processing**: AI processes multiple apps per API call (20 at a time)

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

### Building for AUR

```bash
# Update version in setup.py, PKGBUILD, and src/goalin/__init__.py
# Create a git tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Generate checksums
makepkg --geninteg

# Update PKGBUILD with new checksums
# Test the build
makepkg -si

# Submit to AUR
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues & Limitations

- **Wayland Support**: Window tracking on Wayland is limited due to security restrictions. Works best on Sway compositor.
- **Idle Detection**: Wayland idle detection is basic and may not be as accurate as X11.
- **Window Titles**: Some applications may not expose window titles properly.
- **AI Rate Limits**: Free tier of Google Gemini has rate limits (check [Google AI Studio](https://makersuite.google.com/app/apikey) for details)
- **First AI Analysis**: First-time categorization of many apps may take a few minutes

## 📝 TODO

- [x] Add AI-powered productivity analysis
- [x] Implement smart application categorization
- [x] Add insights and recommendations
- [x] Optimize performance with caching
- [ ] Add support for more Wayland compositors
- [ ] Implement weekly and monthly report views with AI summaries
- [ ] Add productivity goals and AI-powered tracking
- [ ] Create notification system for productivity reminders
- [ ] Add data export/import functionality
- [ ] Implement application blocklist/allowlist with AI suggestions
- [ ] Add statistics and trend analysis with ML predictions
- [ ] Create a configuration GUI
- [ ] Add support for other AI providers (OpenAI, Claude, etc.)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**YadavYashvant**

- GitHub: [@YadavYashvant](https://github.com/YadavYashvant)
- Repository: [Goalin](https://github.com/YadavYashvant/Goalin)

## 🙏 Acknowledgments

- GTK and GNOME teams for the amazing toolkit
- Python community for excellent libraries
- Arch Linux community for the AUR

---

<div align="center">
Made with ❤️ for the Linux community
</div>
