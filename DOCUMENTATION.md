# Goalin - Project Documentation

## Overview

Goalin is a comprehensive productivity tracking solution for Linux that monitors your application usage and provides detailed insights into how you spend your computer time.

## Architecture

### Components

1. **Daemon (daemon.py)**: Background service that continuously tracks active windows
2. **Database (database.py)**: SQLite-based storage with efficient querying
3. **Tracker (tracker.py)**: Cross-platform window detection (X11/Wayland)
4. **Report Generator (report.py)**: Multi-format report creation
5. **GUI (gui.py)**: GTK4/libadwaita user interface
6. **Config (config.py)**: Centralized configuration management

### Data Flow

```
Active Window → Tracker → Daemon → Database
                                      ↓
                            Report Generator → Files
                                      ↓
                                    GUI ← User
```

### Technology Stack

- **Language**: Python 3.9+
- **GUI Framework**: GTK4 with libadwaita
- **Database**: SQLite3
- **Window Detection**: python-xlib (X11), swaymsg (Wayland)
- **Service Management**: systemd

## Database Schema

### activities table
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    window_title TEXT,
    application TEXT,
    category TEXT,
    duration INTEGER,
    is_idle BOOLEAN
)
```

### daily_summary table
```sql
CREATE TABLE daily_summary (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    total_active_time INTEGER,
    total_idle_time INTEGER,
    most_used_app TEXT,
    report_generated BOOLEAN,
    created_at DATETIME
)
```

### category_time table
```sql
CREATE TABLE category_time (
    id INTEGER PRIMARY KEY,
    date DATE,
    category TEXT,
    total_seconds INTEGER,
    UNIQUE(date, category)
)
```

## Configuration

### File Locations

| Type | Location |
|------|----------|
| Config | `~/.config/goalin/` |
| Database | `~/.local/share/goalin/activity.db` |
| Reports | `~/.local/share/goalin/reports/` |
| Logs | `~/.local/share/goalin/logs/` |
| Cache | `~/.cache/goalin/` |

### Settings

Edit `src/goalin/config.py`:

```python
POLL_INTERVAL = 5          # Activity check frequency (seconds)
IDLE_THRESHOLD = 300       # Idle time threshold (seconds)
REPORT_TIME = "20:00"      # Daily report generation time
```

### Application Categories

Categories are defined in `config.py`:

- Development
- Browser
- Communication
- Media
- Office
- Gaming
- System
- Other (default)

To add a category:

```python
APP_CATEGORIES = {
    'YourCategory': ['keyword1', 'keyword2', ...],
}
```

## API Reference

### Database API

```python
from goalin.database import ActivityDatabase

db = ActivityDatabase()

# Log activity
db.log_activity(
    window_title="Window Title",
    application="AppName",
    category="Category",
    duration=5,
    is_idle=False
)

# Get today's summary
summary = db.get_today_summary()
# Returns: {
#     'date': date,
#     'total_active_time': int,
#     'total_idle_time': int,
#     'most_used_app': str,
#     'categories': dict
# }

# Get activities by date
activities = db.get_activities_by_date(date)

db.close()
```

### Tracker API

```python
from goalin.tracker import ActivityTracker

tracker = ActivityTracker()

# Get active window
title, app = tracker.get_active_window()

# Check if user is idle
is_idle = tracker.is_idle(threshold=300)

# Get idle time in seconds
idle_seconds = tracker.get_idle_time()
```

### Report Generator API

```python
from goalin.report import ReportGenerator
from goalin.database import ActivityDatabase

db = ActivityDatabase()
generator = ReportGenerator(db)

# Generate report
report_path = generator.generate_report(
    date=date,              # Default: yesterday
    format='all'            # 'text', 'json', 'html', or 'all'
)

db.close()
```

## CLI Tools

### goalin-daemon
Background tracking daemon.

```bash
goalin-daemon  # Run in foreground
# Or use systemd service
systemctl --user start goalin.service
```

### goalin-gui
GTK4 graphical interface.

```bash
goalin-gui
```

### goalin-report
Manual report generation.

```bash
goalin-report [OPTIONS]

Options:
  --date DATE      Date in YYYY-MM-DD format (default: yesterday)
  --format FORMAT  Report format: text, json, html, all (default: all)
```

## Development

### Project Structure

```
Goalin/
├── src/goalin/           # Main package
│   ├── __init__.py
│   ├── config.py         # Configuration
│   ├── database.py       # Database operations
│   ├── tracker.py        # Activity tracking
│   ├── daemon.py         # Background daemon
│   ├── report.py         # Report generation
│   └── gui.py           # GTK GUI
├── setup.py             # Package setup
├── PKGBUILD            # Arch package
├── goalin.service      # Systemd service
├── goalin.desktop      # Desktop entry
├── requirements.txt    # Dependencies
├── Makefile           # Build automation
├── quick-start.sh     # Quick setup script
└── test_installation.py # Installation tests
```

### Development Workflow

1. **Setup Development Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   pip install pytest pylint black
   ```

2. **Make Changes**
   Edit source files in `src/goalin/`

3. **Test Changes**
   ```bash
   python3 test_installation.py
   ```

4. **Run Locally**
   ```bash
   python3 -m goalin.daemon     # Test daemon
   python3 -m goalin.gui        # Test GUI
   python3 -m goalin.report     # Test reports
   ```

5. **Code Quality**
   ```bash
   make lint    # Check code
   make format  # Format code
   ```

### Adding Features

#### New Application Category

1. Edit `src/goalin/config.py`
2. Add to `APP_CATEGORIES`:
   ```python
   'NewCategory': ['keyword1', 'keyword2']
   ```

#### New Report Format

1. Edit `src/goalin/report.py`
2. Add method:
   ```python
   def generate_xxx_report(self, summary: Dict) -> str:
       # Generate report
       return report_content
   ```
3. Update `generate_report()` method

#### New Display Server Support

1. Edit `src/goalin/tracker.py`
2. Add detection in `_detect_display_server()`
3. Implement `get_active_window_xxx()` method

### Testing

Run comprehensive tests:
```bash
python3 test_installation.py
```

Test specific component:
```bash
python3 -c "from goalin.tracker import ActivityTracker; t = ActivityTracker(); print(t.get_active_window())"
```

### Building for Release

1. Update version numbers:
   - `src/goalin/__init__.py`
   - `setup.py`
   - `PKGBUILD`

2. Update CHANGELOG.md

3. Build packages:
   ```bash
   make build
   ```

4. Create git tag:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```

5. Update AUR:
   ```bash
   cd /path/to/aur/goalin
   # Update PKGBUILD
   makepkg --printsrcinfo > .SRCINFO
   git commit -am "Update to v0.1.0"
   git push
   ```

## Performance Considerations

### Polling Interval
- Default: 5 seconds
- Lower = More accurate, higher CPU usage
- Higher = Less accurate, lower CPU usage
- Recommended: 5-10 seconds

### Database Optimization
- Automatic indexing on timestamp and date columns
- Periodic VACUUM recommended (monthly)
- Old data can be archived or deleted

### Memory Usage
- Typical: 20-40 MB (daemon)
- GUI: Additional 40-60 MB
- Database grows ~1-2 MB per month of tracking

## Security & Privacy

### Data Storage
- All data stored locally
- No network communication
- No telemetry or analytics

### Permissions Required
- Read X11/Wayland window information
- Write to user directories
- No root/sudo required

### Sensitive Data
- Window titles may contain sensitive information
- Consider excluding certain applications
- Database file should be secured with proper permissions

## Troubleshooting

### Common Issues

**Service won't start**
```bash
systemctl --user status goalin.service
journalctl --user -u goalin.service -n 50
```

**High CPU usage**
- Increase `POLL_INTERVAL` in config.py
- Check for infinite loops in logs

**Database locked**
- Close other instances
- Check file permissions
- Restart service

**GUI crashes**
- Verify GTK4/libadwaita installed
- Check with: `G_MESSAGES_DEBUG=all goalin-gui`

### Debug Mode

Enable verbose logging:
```python
# In daemon.py or other modules
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Web dashboard
- [ ] Productivity goals and alerts
- [ ] Application blocking/whitelisting
- [ ] Team/organization features
- [ ] Machine learning insights
- [ ] Browser extension integration
- [ ] Mobile companion app
- [ ] Export to CSV/Excel
- [ ] Customizable categories
- [ ] Focus session tracking

## License

MIT License - See LICENSE file for details

## Support

- Issues: https://github.com/YadavYashvant/Goalin/issues
- Discussions: https://github.com/YadavYashvant/Goalin/discussions
- Documentation: https://github.com/YadavYashvant/Goalin/wiki
