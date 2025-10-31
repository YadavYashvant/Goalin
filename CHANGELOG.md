# Changelog

All notable changes to Goalin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Completely Redesigned UI/UX** 🎨
  - Modern dashboard-style interface with better visual hierarchy
  - Stack-based navigation instead of tabs (Overview, Timeline, Insights, Report)
  - Custom circular progress bars showing progress at a glance
  - Interactive activity heatmap visualization for hourly activity intensity
  - Gradient stat cards with animated floating elements
  - Color-coded productivity levels (high/medium/low)
  - Modern badges and tags for categories and time durations
  - Smooth transitions and hover effects
  - Responsive grid layouts for better space utilization
  
- **Enhanced Overview Dashboard**
  - 4 stat cards with circular progress indicators (Active Time, Idle Time, Total Apps, Most Used)
  - Visual activity heatmap showing intensity throughout the 24-hour day
  - Top 8 applications with icons, categories, and progress bars
  - Category breakdown grid with circular progress and color coding
  - At-a-glance productivity percentage
  
- **Improved Timeline View**
  - Hourly activity cards with productivity color coding
  - Visual indicators for productive (green), moderate (yellow), low (red) hours
  - Top 3 apps per hour with detailed window titles
  - Better spacing and card-based design
  - Activity count and total duration per hour
  
- **New Insights View** 💡
  - Dedicated browser activity section with category breakdown
  - Top 5 visited websites with rankings
  - Productivity score calculation and visualization
  - Time breakdown by activity type (Development, Browser, Communication)
  - Smart empty states with helpful messages
  
- **Visual Enhancements**
  - Custom CSS styling for modern look and feel
  - Gradient backgrounds on stat cards
  - Rounded corners and soft shadows
  - Icon-based visual language (emojis for quick recognition)
  - Consistent color palette and typography
  - Professional card-based layout
  - **True dark mode throughout the entire app**
    - Semi-transparent card backgrounds instead of white
    - Brighter badge colors for better contrast
    - Visible borders adapted for dark mode
    - Consistent layering with proper depth
  
### Changed
- Replaced tab-based navigation with stack switcher for cleaner navigation
- Moved date navigation to header for always-accessible controls
- Redesigned all data visualizations for better clarity
- Improved spacing and margins throughout the app
  
### Previous Features
- **Timeline View**: Hourly activity breakdown showing what you did throughout the day
- **Integrated Report Viewer**: Daily reports display directly in the GUI (📄 Report tab)
  - HTML reports rendered inline using WebKit
  - No need to open external browser
  - Automatic loading based on selected date
  - Beautiful gradient empty state for dates without reports

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
