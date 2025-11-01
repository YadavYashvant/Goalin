# Goalin

<div align="center">

**A productivity tracking service for Linux**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GTK Version](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)

</div>

## 📖 Overview

Goalin is a locally-run productivity tracking service for Linux that monitors your application usage and generates comprehensive daily reports. It helps you understand how you spend your time on your computer, identify productivity patterns, and make data-driven decisions to improve your workflow.

### ✨ Features

- **🎨 Modern Dashboard UI**: Completely redesigned interface with professional aesthetics
  - Stack-based navigation (Overview, Timeline, Insights, Report)
  - Custom circular progress bars and activity heatmaps
  - Color-coded productivity levels and visual indicators
  - Gradient stat cards with smooth animations
  - Card-based layout with proper spacing and shadows
  
- **📊 Rich Overview Dashboard**
  - **Circular Progress Stats**: Active time, idle time, app count, and most-used app
  - **Activity Heatmap**: 24-hour visual representation of activity intensity
  - **Top Applications**: Your 8 most-used apps with icons, categories, and progress bars
  - **Category Grid**: Visual breakdown of time spent in each category
  - **Productivity Score**: At-a-glance percentage of productive time
  
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
- **📈 Daily Reports**: Automatically generates detailed reports at the end of each day
- **📁 Category Classification**: Intelligently categorizes applications (Development, Browser, Communication, etc.)
- **⏱️ Idle Detection**: Distinguishes between active usage and idle time
- **🗄️ Local SQLite Database**: All your data stays on your machine - complete privacy
- **📄 Multiple Report Formats**: Generate reports in Text, JSON, and HTML formats
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
```

## 📋 Dependencies

- Python 3.9+
- PyGObject (python-gobject)
- GTK4
- libadwaita
- python-xlib (for X11 support)
- pytz

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
- **Database**: `~/.local/share/goalin/activity.db`
- **Reports**: `~/.local/share/goalin/reports/`
- **Logs**: `~/.local/share/goalin/logs/`
- **Cache**: `~/.cache/goalin/`

## ⚙️ Configuration

Configuration can be customized by editing `src/goalin/config.py`:

```python
# Tracking settings
POLL_INTERVAL = 5  # seconds between activity checks
IDLE_THRESHOLD = 300  # seconds before considering user idle

# Report settings
REPORT_TIME = "20:00"  # Time to generate daily report (24-hour format)
```

### Application Categories

You can customize application categories in `config.py`:

```python
APP_CATEGORIES = {
    'Development': ['code', 'vscode', 'vim', 'pycharm', ...],
    'Browser': ['firefox', 'chrome', 'brave', ...],
    'Communication': ['slack', 'discord', 'telegram', ...],
    # Add your own categories...
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
Beautiful, responsive HTML reports with charts and visualizations.

### JSON Report
Machine-readable format for integration with other tools and services.

## 🔒 Privacy

Goalin takes your privacy seriously:

- ✅ **100% Local**: All data is stored locally on your machine
- ✅ **No Cloud**: No data is ever sent to external servers
- ✅ **Open Source**: Full transparency - audit the code yourself
- ✅ **Your Control**: Delete or export your data anytime

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
│   ├── report.py        # Report generation
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

## 📝 TODO

- [ ] Add support for more Wayland compositors
- [ ] Implement weekly and monthly report views
- [ ] Add productivity goals and targets
- [ ] Create notification system for productivity reminders
- [ ] Add data export/import functionality
- [ ] Implement application blocklist/allowlist
- [ ] Add statistics and trend analysis
- [ ] Create a configuration GUI

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
