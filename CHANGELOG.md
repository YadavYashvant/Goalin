# Changelog

All notable changes to Goalin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Timeline View**: New interactive timeline tab showing hourly activity breakdown
  - Activities grouped by hour with visual progress bars
  - Top 3 applications per hour with duration and percentage
  - Recent window titles for context
  - Time range indicators (HH:00 - HH:59)
  - Empty state with helpful messages
- **Integrated Report Viewer**: Daily reports now display directly in the GUI (📄 Report tab)
  - HTML reports rendered inline using WebKit
  - No need to open external browser
  - Automatic loading based on selected date
  - Beautiful gradient empty state for dates without reports
  - Proper timezone handling (UTC to local time conversion)

### Planned
- Manual report generation button in GUI
- Weekly and monthly report views
- Productivity goals and targets
- Notification system
- Configuration GUI
- Data export/import
- Application blocklist/allowlist
- Statistics and trend analysis

## [0.1.0] - 2025-10-26

### Added
- Initial release
- Automatic activity tracking for X11 and Wayland
- Background daemon service with systemd integration
- GTK4 GUI application with libadwaita
- SQLite database for activity storage
- Daily report generation (Text, JSON, HTML formats)
- Application categorization system
- Idle time detection
- Desktop application launcher
- PKGBUILD for AUR packaging
- Comprehensive documentation

### Features
- Real-time window and application tracking
- Category-based time analysis
- Daily activity summaries
- Multiple report formats
- Privacy-focused (all data stored locally)
- Modern GTK4 interface
- Date navigation in GUI
- Manual report generation
- Systemd user service

[Unreleased]: https://github.com/YadavYashvant/Goalin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YadavYashvant/Goalin/releases/tag/v0.1.0
