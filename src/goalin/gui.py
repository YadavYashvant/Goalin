#!/usr/bin/env python3
"""
Redesigned GTK4 GUI application for Goalin with modern, engaging UI
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Adw, GLib, Gio, WebKit, Gdk
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from pytz import timezone, utc
import math

from goalin.database import ActivityDatabase
from goalin.config import ensure_directories, REPORT_DIR, is_setup_complete

logger = logging.getLogger(__name__)


class CircularProgressBar(Gtk.DrawingArea):
    """Custom circular progress bar widget"""
    
    def __init__(self, fraction=0.0, color=(0.2, 0.6, 1.0)):
        super().__init__()
        self.fraction = fraction
        self.color = color
        self.set_content_width(80)
        self.set_content_height(80)
        self.set_draw_func(self.draw_circular_progress)
    
    def set_fraction(self, fraction):
        self.fraction = max(0.0, min(1.0, fraction))
        self.queue_draw()
    
    def draw_circular_progress(self, area, cr, width, height):
        # Center and radius
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 5
        line_width = 8
        
        # Background circle
        cr.set_source_rgba(0.9, 0.9, 0.9, 0.3)
        cr.set_line_width(line_width)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()
        
        # Progress arc
        if self.fraction > 0:
            cr.set_source_rgba(*self.color, 1.0)
            cr.set_line_width(line_width)
            cr.set_line_cap(1)  # Round cap
            start_angle = -math.pi / 2  # Start from top
            end_angle = start_angle + (2 * math.pi * self.fraction)
            cr.arc(cx, cy, radius, start_angle, end_angle)
            cr.stroke()


class ActivityHeatmap(Gtk.DrawingArea):
    """Visual heatmap showing activity intensity throughout the day"""
    
    def __init__(self):
        super().__init__()
        self.hourly_data = {}  # hour -> duration in seconds
        self.set_content_height(120)
        self.set_vexpand(False)
        self.set_hexpand(True)
        self.set_draw_func(self.draw_heatmap)
    
    def set_data(self, hourly_data):
        self.hourly_data = hourly_data
        self.queue_draw()
    
    def draw_heatmap(self, area, cr, width, height):
        if not self.hourly_data:
            return
        
        # Calculate dimensions
        hours = 24
        cell_width = width / hours
        cell_height = height - 40  # Leave space for labels
        max_duration = max(self.hourly_data.values()) if self.hourly_data else 1
        
        # Draw cells
        for hour in range(24):
            duration = self.hourly_data.get(hour, 0)
            intensity = duration / max_duration if max_duration > 0 else 0
            
            # Color gradient from light blue to dark blue
            r = 0.2 + (1 - intensity) * 0.7
            g = 0.6 + (1 - intensity) * 0.3
            b = 1.0
            cr.set_source_rgba(r, g, b, 0.3 + intensity * 0.7)
            
            x = hour * cell_width
            cr.rectangle(x + 2, 20, cell_width - 4, cell_height)
            cr.fill()
            
            # Draw hour labels for selected hours
            if hour % 3 == 0:
                cr.set_source_rgba(0.5, 0.5, 0.5, 1.0)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(10)
                text = f"{hour:02d}"
                extents = cr.text_extents(text)
                cr.move_to(x + cell_width/2 - extents.width/2, 15)
                cr.show_text(text)
                
                # Bottom label too
                cr.move_to(x + cell_width/2 - extents.width/2, height - 5)
                cr.show_text(text)


class GoalinWindow(Adw.ApplicationWindow):
    """Main application window with redesigned UI"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.db = ActivityDatabase()
        self.current_date = datetime.now().date()
        
        # Window setup
        self.set_title("Goalin - Productivity Tracker")
        self.set_default_size(1100, 700)
        
        # Apply custom CSS
        self.apply_custom_css()
        
        # Create header bar
        header = Adw.HeaderBar()
        header.add_css_class("flat")
        
        # Date navigation in a box
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        nav_box.add_css_class("linked")
        
        prev_button = Gtk.Button(icon_name="go-previous-symbolic")
        prev_button.connect("clicked", self.on_prev_day)
        nav_box.append(prev_button)
        
        self.date_button = Gtk.Button(label="Today")
        self.date_button.set_size_request(180, -1)
        self.date_button.connect("clicked", self.on_today)
        nav_box.append(self.date_button)
        
        next_button = Gtk.Button(icon_name="go-next-symbolic")
        next_button.connect("clicked", self.on_next_day)
        nav_box.append(next_button)
        
        header.set_title_widget(nav_box)
        
        # View switcher for different views
        view_switcher = Gtk.StackSwitcher()
        view_switcher.add_css_class("raised")
        header.pack_start(view_switcher)
        
        # Menu button
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu = Gio.Menu()
        menu.append("Generate Report", "app.generate_report")
        menu.append("Open Reports Folder", "app.open_reports")
        menu.append("Preferences", "app.preferences")
        menu.append("About", "app.about")
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        # Main content with stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)
        view_switcher.set_stack(self.stack)
        
        # Create views
        self.create_overview_view()
        self.create_timeline_view()
        self.create_insights_view()
        self.create_report_view()
        
        # Toolbar with content
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(self.stack)
        
        self.set_content(toolbar)
        
        # Load initial data
        self.update_display()
    
    def apply_custom_css(self):
        """Apply custom CSS for better styling"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .stat-card {
                background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(155, 89, 182, 0.1) 100%);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            
            .stat-value {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 4px;
            }
            
            .stat-label {
                font-size: 13px;
                opacity: 0.7;
            }
            
            .section-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 16px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }
            
            .section-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
            }
            
            .app-item {
                border-radius: 10px;
                padding: 12px 16px;
                margin-bottom: 8px;
                background: rgba(255, 255, 255, 0.03);
                transition: all 200ms;
            }
            
            .app-item:hover {
                background: rgba(52, 152, 219, 0.1);
                transform: translateX(4px);
            }
            
            .category-badge {
                background: rgba(52, 152, 219, 0.25);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
                color: rgba(100, 181, 246, 1);
            }
            
            .time-badge {
                background: rgba(46, 204, 113, 0.25);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 600;
                color: rgba(129, 212, 150, 1);
            }
            
            .productivity-high {
                background: linear-gradient(135deg, rgba(46, 204, 113, 0.2) 0%, rgba(39, 174, 96, 0.2) 100%);
            }
            
            .productivity-medium {
                background: linear-gradient(135deg, rgba(241, 196, 15, 0.2) 0%, rgba(243, 156, 18, 0.2) 100%);
            }
            
            .productivity-low {
                background: linear-gradient(135deg, rgba(231, 76, 60, 0.2) 0%, rgba(192, 57, 43, 0.2) 100%);
            }
        """)
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def create_overview_view(self):
        """Create the main overview dashboard"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.set_margin_start(32)
        main_box.set_margin_end(32)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        
        # Hero section with date and quick stats
        hero_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        hero_box.set_margin_bottom(24)
        
        self.overview_date_label = Gtk.Label()
        self.overview_date_label.add_css_class("title-1")
        self.overview_date_label.set_xalign(0)
        hero_box.append(self.overview_date_label)
        
        self.overview_subtitle = Gtk.Label()
        self.overview_subtitle.add_css_class("title-3")
        self.overview_subtitle.add_css_class("dim-label")
        self.overview_subtitle.set_xalign(0)
        hero_box.append(self.overview_subtitle)
        
        main_box.append(hero_box)
        
        # Stats grid with circular progress bars
        stats_grid = Gtk.Grid()
        stats_grid.set_row_spacing(16)
        stats_grid.set_column_spacing(16)
        stats_grid.set_column_homogeneous(True)
        stats_grid.set_margin_bottom(24)
        
        self.overview_stats = []
        for i in range(4):
            card = self.create_modern_stat_card()
            self.overview_stats.append(card)
            stats_grid.attach(card, i % 2, i // 2, 1, 1)
        
        main_box.append(stats_grid)
        
        # Activity heatmap
        heatmap_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        heatmap_card.add_css_class("section-card")
        
        heatmap_title = Gtk.Label(label="Activity Throughout the Day")
        heatmap_title.add_css_class("section-title")
        heatmap_title.set_xalign(0)
        heatmap_card.append(heatmap_title)
        
        self.heatmap = ActivityHeatmap()
        heatmap_card.append(self.heatmap)
        
        main_box.append(heatmap_card)
        
        # Top applications section
        apps_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        apps_card.add_css_class("section-card")
        
        apps_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        apps_title = Gtk.Label(label="Top Applications")
        apps_title.add_css_class("section-title")
        apps_title.set_xalign(0)
        apps_title.set_hexpand(True)
        apps_header.append(apps_title)
        
        apps_card.append(apps_header)
        
        self.top_apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        apps_card.append(self.top_apps_box)
        
        main_box.append(apps_card)
        
        # Category breakdown
        category_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        category_card.add_css_class("section-card")
        
        cat_title = Gtk.Label(label="Category Breakdown")
        cat_title.add_css_class("section-title")
        cat_title.set_xalign(0)
        category_card.append(cat_title)
        
        self.category_grid = Gtk.Grid()
        self.category_grid.set_row_spacing(12)
        self.category_grid.set_column_spacing(12)
        self.category_grid.set_column_homogeneous(True)
        category_card.append(self.category_grid)
        
        main_box.append(category_card)
        
        scrolled.set_child(main_box)
        self.stack.add_titled(scrolled, "overview", "📊 Overview")
    
    def create_modern_stat_card(self):
        """Create a modern stat card with circular progress"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.add_css_class("stat-card")
        card.set_size_request(200, 140)
        
        # Circular progress
        progress_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        progress_box.set_halign(Gtk.Align.CENTER)
        
        circular_progress = CircularProgressBar()
        progress_box.append(circular_progress)
        card.append(progress_box)
        
        # Value label
        value_label = Gtk.Label()
        value_label.add_css_class("stat-value")
        card.append(value_label)
        
        # Title label
        title_label = Gtk.Label()
        title_label.add_css_class("stat-label")
        card.append(title_label)
        
        # Store references
        card.circular_progress = circular_progress
        card.value_label = value_label
        card.title_label = title_label
        
        return card
    
    def create_timeline_view(self):
        """Create detailed timeline view"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.timeline_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.timeline_box.set_margin_start(32)
        self.timeline_box.set_margin_end(32)
        self.timeline_box.set_margin_top(24)
        self.timeline_box.set_margin_bottom(24)
        
        scrolled.set_child(self.timeline_box)
        self.stack.add_titled(scrolled, "timeline", "⏰ Timeline")
    
    def create_insights_view(self):
        """Create insights and analytics view"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        insights_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        insights_box.set_margin_start(32)
        insights_box.set_margin_end(32)
        insights_box.set_margin_top(24)
        insights_box.set_margin_bottom(24)
        
        # Browser activity section
        browser_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        browser_card.add_css_class("section-card")
        
        browser_title = Gtk.Label(label="🦊 Browser Activity")
        browser_title.add_css_class("section-title")
        browser_title.set_xalign(0)
        browser_card.append(browser_title)
        
        self.browser_insights_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        browser_card.append(self.browser_insights_box)
        
        insights_box.append(browser_card)
        
        # Productivity insights
        productivity_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        productivity_card.add_css_class("section-card")
        
        prod_title = Gtk.Label(label="📈 Productivity Insights")
        prod_title.add_css_class("section-title")
        prod_title.set_xalign(0)
        productivity_card.append(prod_title)
        
        self.productivity_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        productivity_card.append(self.productivity_box)
        
        insights_box.append(productivity_card)
        
        scrolled.set_child(insights_box)
        self.stack.add_titled(scrolled, "insights", "💡 Insights")
    
    def create_report_view(self):
        """Create report view with WebKit"""
        report_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.report_webview = WebKit.WebView()
        self.report_webview.set_vexpand(True)
        self.report_webview.set_hexpand(True)
        
        settings = self.report_webview.get_settings()
        settings.set_enable_developer_extras(False)
        
        report_scrolled = Gtk.ScrolledWindow()
        report_scrolled.set_child(self.report_webview)
        
        report_box.append(report_scrolled)
        
        self.stack.add_titled(report_box, "report", "📄 Report")
    
    def format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_display(self):
        """Update all views with current date data"""
        # Update date button
        date_str = self.current_date.strftime('%B %d, %Y')
        today = datetime.now().date()
        
        if self.current_date == today:
            self.date_button.set_label("Today")
        elif self.current_date == today - timedelta(days=1):
            self.date_button.set_label("Yesterday")
        else:
            days_diff = (today - self.current_date).days
            if days_diff > 0:
                self.date_button.set_label(f"{days_diff} days ago")
            else:
                self.date_button.set_label(f"In {abs(days_diff)} days")
        
        # Get summary data
        summary = self.db.get_summary_by_date(self.current_date)
        
        # Update overview
        self.update_overview(summary)
        
        # Update timeline
        self.update_timeline()
        
        # Update insights
        self.update_insights(summary)
        
        # Update report
        self.update_report()
    
    def update_overview(self, summary):
        """Update the overview dashboard"""
        # Update date labels
        date_str = self.current_date.strftime('%A, %B %d, %Y')
        self.overview_date_label.set_text(date_str)
        
        total_time = summary['total_active_time'] + summary['total_idle_time']
        if total_time > 0:
            active_percent = (summary['total_active_time'] / total_time) * 100
            self.overview_subtitle.set_text(f"{active_percent:.1f}% productive time")
        else:
            self.overview_subtitle.set_text("No activity recorded yet")
        
        # Update stat cards
        stats = [
            ("Active Time", summary['total_active_time'], (0.2, 0.7, 0.3)),
            ("Idle Time", summary['total_idle_time'], (0.9, 0.6, 0.2)),
            ("Total Apps", len(summary['categories']), (0.4, 0.5, 0.9)),
            ("Most Used", summary['most_used_app'], (0.8, 0.3, 0.5))
        ]
        
        max_time = max(summary['total_active_time'], summary['total_idle_time'], 1)
        
        for i, (title, value, color) in enumerate(stats):
            card = self.overview_stats[i]
            card.title_label.set_text(title)
            
            if isinstance(value, int) and title != "Total Apps":
                card.value_label.set_text(self.format_duration(value))
                fraction = value / max_time
                card.circular_progress.color = color
                card.circular_progress.set_fraction(fraction)
            elif title == "Total Apps":
                card.value_label.set_text(str(value))
                card.circular_progress.set_fraction(min(value / 10, 1.0))
                card.circular_progress.color = color
            else:
                card.value_label.set_text(value if value else "None")
                card.circular_progress.set_fraction(0.5)
                card.circular_progress.color = color
        
        # Update heatmap
        activities = self.db.get_activities_by_date(self.current_date)
        hourly_data = self.get_hourly_activity_data(activities)
        self.heatmap.set_data(hourly_data)
        
        # Update top apps
        self.update_top_apps(summary)
        
        # Update category grid
        self.update_category_grid(summary)
    
    def get_hourly_activity_data(self, activities):
        """Convert activities to hourly duration data"""
        hourly_data = defaultdict(int)
        
        for activity in activities:
            timestamp_str = activity[1]
            try:
                if '.' in timestamp_str:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                local_tz = timezone('Asia/Kolkata')
                dt_utc = utc.localize(dt)
                dt_local = dt_utc.astimezone(local_tz)
                
                hour = dt_local.hour
                hourly_data[hour] += activity[5]  # duration
            except Exception as e:
                continue
        
        return dict(hourly_data)
    
    def update_top_apps(self, summary):
        """Update top applications list"""
        # Clear existing
        while child := self.top_apps_box.get_first_child():
            self.top_apps_box.remove(child)
        
        # Get app durations
        activities = self.db.get_activities_by_date(self.current_date)
        app_durations = defaultdict(int)
        app_categories = {}
        
        for activity in activities:
            app = activity[3]
            duration = activity[5]
            category = activity[4]
            app_durations[app] += duration
            app_categories[app] = category
        
        # Sort and show top 8
        sorted_apps = sorted(app_durations.items(), key=lambda x: x[1], reverse=True)[:8]
        max_duration = sorted_apps[0][1] if sorted_apps else 1
        
        app_icons = {
            'firefox': '🦊', 'chrome': '🌐', 'code': '💻', 'terminal': '⚡',
            'spotify': '🎵', 'discord': '💬', 'slack': '💬', 'vim': '📝'
        }
        
        for app, duration in sorted_apps:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add_css_class("app-item")
            
            # Icon
            icon_label = Gtk.Label(label=app_icons.get(app.lower(), '📦'))
            icon_label.set_width_chars(3)
            row.append(icon_label)
            
            # App info
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            info_box.set_hexpand(True)
            
            app_label = Gtk.Label(label=app.title())
            app_label.set_xalign(0)
            app_label.add_css_class("heading")
            info_box.append(app_label)
            
            # Category badge
            category = app_categories.get(app, 'Other')
            cat_badge = Gtk.Label(label=category)
            cat_badge.add_css_class("category-badge")
            cat_badge.set_xalign(0)
            info_box.append(cat_badge)
            
            row.append(info_box)
            
            # Duration badge
            time_badge = Gtk.Label(label=self.format_duration(duration))
            time_badge.add_css_class("time-badge")
            row.append(time_badge)
            
            # Progress bar
            progress = Gtk.ProgressBar()
            progress.set_fraction(duration / max_duration)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(100, -1)
            row.append(progress)
            
            self.top_apps_box.append(row)
    
    def update_category_grid(self, summary):
        """Update category breakdown grid"""
        # Clear existing
        while child := self.category_grid.get_first_child():
            self.category_grid.remove(child)
        
        sorted_categories = sorted(
            summary['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_active = summary['total_active_time']
        
        category_icons = {
            'Development': '💻', 'Browser': '🌐', 'Communication': '💬',
            'Media': '🎵', 'Office': '📄', 'Gaming': '🎮',
            'System': '⚙️', 'Idle': '💤', 'Other': '📦'
        }
        
        category_colors = {
            'Development': (0.2, 0.7, 0.3), 'Browser': (0.2, 0.6, 1.0),
            'Communication': (0.6, 0.4, 0.9), 'Media': (1.0, 0.5, 0.2),
            'Office': (0.2, 0.5, 0.8), 'Gaming': (0.9, 0.3, 0.5),
            'System': (0.5, 0.5, 0.5), 'Idle': (0.8, 0.8, 0.2), 'Other': (0.6, 0.6, 0.6)
        }
        
        for idx, (category, duration) in enumerate(sorted_categories[:6]):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.add_css_class("stat-card")
            card.set_size_request(150, 120)
            
            # Circular progress
            progress_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            progress_box.set_halign(Gtk.Align.CENTER)
            
            color = category_colors.get(category, (0.5, 0.5, 0.5))
            circular = CircularProgressBar(
                fraction=duration/total_active if total_active > 0 else 0,
                color=color
            )
            progress_box.append(circular)
            card.append(progress_box)
            
            # Icon and name
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            header.set_halign(Gtk.Align.CENTER)
            
            icon = Gtk.Label(label=category_icons.get(category, '📦'))
            header.append(icon)
            
            name = Gtk.Label(label=category)
            name.add_css_class("heading")
            header.append(name)
            
            card.append(header)
            
            # Duration
            duration_label = Gtk.Label(label=self.format_duration(duration))
            duration_label.add_css_class("dim-label")
            card.append(duration_label)
            
            self.category_grid.attach(card, idx % 3, idx // 3, 1, 1)
    
    def update_timeline(self):
        """Update timeline view"""
        # Clear existing
        while child := self.timeline_box.get_first_child():
            self.timeline_box.remove(child)
        
        # Add header
        header = Gtk.Label(label="Activity Timeline")
        header.add_css_class("title-2")
        header.set_margin_bottom(24)
        header.set_xalign(0)
        self.timeline_box.append(header)
        
        activities = self.db.get_activities_by_date(self.current_date)
        
        if not activities:
            empty_state = self.create_empty_state("⏰", "No Activity", "Start using your computer to see your timeline")
            self.timeline_box.append(empty_state)
            return
        
        # Group by hour
        hourly_activities = defaultdict(list)
        
        for activity in activities:
            timestamp_str = activity[1]
            try:
                if '.' in timestamp_str:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                local_tz = timezone('Asia/Kolkata')
                dt_utc = utc.localize(dt)
                dt_local = dt_utc.astimezone(local_tz)
                
                hour = dt_local.hour
                hourly_activities[hour].append({
                    'app': activity[3],
                    'window': activity[2],
                    'duration': activity[5],
                    'time': dt_local
                })
            except:
                continue
        
        # Create timeline cards
        for hour in sorted(hourly_activities.keys()):
            hour_card = self.create_timeline_hour_card(hour, hourly_activities[hour])
            self.timeline_box.append(hour_card)
    
    def create_timeline_hour_card(self, hour, activities):
        """Create a card for one hour of activity"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.add_css_class("section-card")
        
        # Calculate stats
        app_durations = defaultdict(int)
        for act in activities:
            app_durations[act['app'].lower()] += act['duration']
        
        total_duration = sum(app_durations.values())
        top_apps = sorted(app_durations.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Determine productivity level
        dev_apps = ['code', 'vim', 'terminal', 'pycharm', 'vscode']
        productive_time = sum(d for app, d in app_durations.items() if any(da in app for da in dev_apps))
        productivity_ratio = productive_time / total_duration if total_duration > 0 else 0
        
        if productivity_ratio > 0.6:
            card.add_css_class("productivity-high")
        elif productivity_ratio > 0.3:
            card.add_css_class("productivity-medium")
        else:
            card.add_css_class("productivity-low")
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        time_label = Gtk.Label(label=f"{hour:02d}:00 - {hour:02d}:59")
        time_label.add_css_class("title-3")
        header.append(time_label)
        
        duration_badge = Gtk.Label(label=self.format_duration(total_duration))
        duration_badge.add_css_class("time-badge")
        header.append(duration_badge)
        
        activity_count = Gtk.Label(label=f"{len(activities)} activities")
        activity_count.add_css_class("dim-label")
        activity_count.set_hexpand(True)
        activity_count.set_xalign(1)
        header.append(activity_count)
        
        card.append(header)
        
        # Apps list
        apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        app_icons = {
            'firefox': '🦊', 'chrome': '🌐', 'code': '💻', 'terminal': '⚡',
            'spotify': '🎵', 'discord': '💬'
        }
        
        for app, duration in top_apps:
            app_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            icon = Gtk.Label(label=app_icons.get(app, '📦'))
            icon.set_width_chars(3)
            app_row.append(icon)
            
            info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            info.set_hexpand(True)
            
            name = Gtk.Label(label=app.title())
            name.set_xalign(0)
            name.add_css_class("heading")
            info.append(name)
            
            # Most recent window
            app_activities = [a for a in activities if a['app'].lower() == app]
            if app_activities and app_activities[0]['window']:
                window_title = app_activities[0]['window'][:50]
                window_label = Gtk.Label(label=window_title)
                window_label.set_xalign(0)
                window_label.add_css_class("caption")
                window_label.add_css_class("dim-label")
                window_label.set_ellipsize(3)
                info.append(window_label)
            
            app_row.append(info)
            
            # Duration and percentage
            percentage = (duration / total_duration) * 100
            stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            stats_box.set_valign(Gtk.Align.CENTER)
            
            dur_label = Gtk.Label(label=self.format_duration(duration))
            dur_label.add_css_class("heading")
            stats_box.append(dur_label)
            
            pct_label = Gtk.Label(label=f"{percentage:.0f}%")
            pct_label.add_css_class("caption")
            pct_label.add_css_class("dim-label")
            stats_box.append(pct_label)
            
            app_row.append(stats_box)
            
            # Progress
            progress = Gtk.ProgressBar()
            progress.set_fraction(percentage / 100)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(60, -1)
            app_row.append(progress)
            
            apps_box.append(app_row)
        
        card.append(apps_box)
        
        return card
    
    def update_insights(self, summary):
        """Update insights view"""
        # Clear browser insights
        while child := self.browser_insights_box.get_first_child():
            self.browser_insights_box.remove(child)
        
        # Get browser summary
        browser_summary = self.db.get_browser_summary_by_date(self.current_date)
        
        if browser_summary['total_visits'] > 0:
            # Total visits
            total_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            total_row.set_margin_bottom(12)
            
            visits_label = Gtk.Label(label=f"{browser_summary['total_visits']} Total Visits")
            visits_label.add_css_class("title-2")
            visits_label.set_xalign(0)
            visits_label.set_hexpand(True)
            total_row.append(visits_label)
            
            self.browser_insights_box.append(total_row)
            
            # Category breakdown
            cat_grid = Gtk.Grid()
            cat_grid.set_row_spacing(8)
            cat_grid.set_column_spacing(8)
            cat_grid.set_column_homogeneous(True)
            
            emoji_map = {
                'Development': '💻', 'Learning': '📚', 'Social Media': '📱',
                'Entertainment': '🎮', 'News': '📰', 'Shopping': '🛒',
                'Email': '📧', 'Productivity': '📊', 'Other': '🌐'
            }
            
            for idx, (category, count) in enumerate(sorted(browser_summary['categories'].items(), key=lambda x: x[1], reverse=True)[:6]):
                cat_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                cat_card.add_css_class("app-item")
                
                emoji = Gtk.Label(label=emoji_map.get(category, '🌐'))
                cat_card.append(emoji)
                
                info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                info.set_hexpand(True)
                
                name = Gtk.Label(label=category)
                name.set_xalign(0)
                name.add_css_class("heading")
                info.append(name)
                
                visits = Gtk.Label(label=f"{count} visits")
                visits.set_xalign(0)
                visits.add_css_class("caption")
                visits.add_css_class("dim-label")
                info.append(visits)
                
                cat_card.append(info)
                
                cat_grid.attach(cat_card, idx % 2, idx // 2, 1, 1)
            
            self.browser_insights_box.append(cat_grid)
            
            # Top domains
            if browser_summary['domains']:
                domains_label = Gtk.Label(label="Top Websites")
                domains_label.add_css_class("title-3")
                domains_label.set_xalign(0)
                domains_label.set_margin_top(16)
                domains_label.set_margin_bottom(8)
                self.browser_insights_box.append(domains_label)
                
                for idx, domain_data in enumerate(browser_summary['domains'][:5], 1):
                    domain_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    domain_row.add_css_class("app-item")
                    
                    rank = Gtk.Label(label=f"#{idx}")
                    rank.add_css_class("monospace")
                    rank.set_width_chars(3)
                    domain_row.append(rank)
                    
                    info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                    info.set_hexpand(True)
                    
                    domain = Gtk.Label(label=domain_data['domain'])
                    domain.set_xalign(0)
                    domain.add_css_class("heading")
                    domain.set_ellipsize(3)
                    info.append(domain)
                    
                    cat_visits = Gtk.Label(label=f"{emoji_map.get(domain_data['category'], '🌐')} {domain_data['category']} • {domain_data['visits']} visits")
                    cat_visits.set_xalign(0)
                    cat_visits.add_css_class("caption")
                    cat_visits.add_css_class("dim-label")
                    info.append(cat_visits)
                    
                    domain_row.append(info)
                    
                    self.browser_insights_box.append(domain_row)
        else:
            empty = self.create_empty_state("🦊", "No Browser Activity", "Browse the web to see insights here")
            self.browser_insights_box.append(empty)
        
        # Clear productivity insights
        while child := self.productivity_box.get_first_child():
            self.productivity_box.remove(child)
        
        # Calculate productivity metrics with AI
        total_time = summary['total_active_time']
        if total_time > 0:
            # Show loading state first
            loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            loading_box.set_valign(Gtk.Align.CENTER)
            loading_box.set_vexpand(True)
            
            spinner = Gtk.Spinner()
            spinner.set_size_request(48, 48)
            spinner.start()
            loading_box.append(spinner)
            
            loading_label = Gtk.Label(label="🤖 Analyzing productivity with AI...")
            loading_label.add_css_class("title-4")
            loading_label.add_css_class("dim-label")
            loading_box.append(loading_label)
            
            self.productivity_box.append(loading_box)
            
            # Load AI insights asynchronously
            def load_ai_insights():
                ai_insights = None
                try:
                    from goalin.ai_assistant import AIAssistant
                    ai = AIAssistant()
                    if ai.is_configured():
                        # Get activity data for AI analysis
                        activities = self.db.get_activities_by_date(self.current_date)
                        from collections import defaultdict
                        hourly_data = defaultdict(int)
                        app_durations = defaultdict(int)
                        
                        for activity in activities:
                            try:
                                hour = datetime.strptime(activity[1], '%Y-%m-%d %H:%M:%S.%f').hour if '.' in activity[1] else datetime.strptime(activity[1], '%Y-%m-%d %H:%M:%S').hour
                                app = activity[3]
                                duration = activity[5]
                                hourly_data[hour] += duration
                                app_durations[app] += duration
                            except:
                                continue
                        
                        day_data = {
                            'total_active_time': total_time,
                            'categories': summary['categories'],
                            'apps': dict(app_durations),
                            'hourly_pattern': dict(hourly_data)
                        }
                        # Pass date_key for caching
                        date_key = self.current_date.strftime('%Y-%m-%d')
                        ai_insights = ai.analyze_productivity(day_data, date_key=date_key)
                except Exception as e:
                    logger.warning(f"AI analysis not available: {e}")
                
                # Update UI on main thread
                GLib.idle_add(lambda: self._update_productivity_ui(summary, ai_insights, total_time))
            
            # Run in thread to avoid blocking
            import threading
            thread = threading.Thread(target=load_ai_insights, daemon=True)
            thread.start()
        else:
            empty = self.create_empty_state("📈", "No Data", "Start working to see productivity insights")
            self.productivity_box.append(empty)
    
    def _update_productivity_ui(self, summary, ai_insights, total_time):
        """Update productivity UI after AI analysis completes"""
        # Clear loading state
        while child := self.productivity_box.get_first_child():
            self.productivity_box.remove(child)
        
        # Use AI score if available, otherwise calculate basic score
        if ai_insights and 'productivity_score' in ai_insights:
            prod_score = ai_insights['productivity_score']
            prod_level = ai_insights.get('productivity_level', 'Medium')
        else:
            dev_time = summary['categories'].get('Development', 0)
            office_time = summary['categories'].get('Office', 0)
            prod_time = summary['categories'].get('Productivity', 0)
            total_productive = dev_time + office_time + prod_time
            prod_score = (total_productive / total_time * 100) if total_time > 0 else 0
            prod_level = 'High' if prod_score >= 80 else 'Medium' if prod_score >= 50 else 'Low'
        
        # Productivity score header
        score_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        score_box.set_margin_bottom(16)
        
        score_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        score_label_box.set_hexpand(True)
        
        score_label = Gtk.Label(label="🤖 AI Productivity Score" if ai_insights else "Productivity Score")
        score_label.add_css_class("title-3")
        score_label.set_xalign(0)
        score_label_box.append(score_label)
        
        level_label = Gtk.Label(label=f"Level: {prod_level}")
        level_label.set_xalign(0)
        level_label.add_css_class("caption")
        level_label.add_css_class("dim-label")
        score_label_box.append(level_label)
        
        score_box.append(score_label_box)
        
        score_value = Gtk.Label(label=f"{prod_score:.0f}%")
        score_value.add_css_class("title-1")
        score_box.append(score_value)
        
        self.productivity_box.append(score_box)
        
        # Progress bar with color based on level
        progress = Gtk.ProgressBar()
        progress.set_fraction(prod_score / 100)
        progress.set_margin_bottom(16)
        self.productivity_box.append(progress)
        
        # AI Insights section
        if ai_insights:
            # Insights
            insights_header = Gtk.Label(label="💡 Key Insights")
            insights_header.add_css_class("title-4")
            insights_header.set_xalign(0)
            insights_header.set_margin_top(12)
            insights_header.set_margin_bottom(8)
            self.productivity_box.append(insights_header)
            
            for insight in ai_insights.get('insights', [])[:3]:
                insight_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                insight_row.add_css_class("app-item")
                insight_row.set_margin_bottom(4)
                
                bullet = Gtk.Label(label="•")
                bullet.set_width_chars(2)
                bullet.add_css_class("dim-label")
                insight_row.append(bullet)
                
                insight_label = Gtk.Label(label=insight)
                insight_label.set_wrap(True)
                insight_label.set_xalign(0)
                insight_label.set_hexpand(True)
                insight_row.append(insight_label)
                
                self.productivity_box.append(insight_row)
            
            # Recommendations
            recs_header = Gtk.Label(label="🚀 Recommendations")
            recs_header.add_css_class("title-4")
            recs_header.set_xalign(0)
            recs_header.set_margin_top(16)
            recs_header.set_margin_bottom(8)
            self.productivity_box.append(recs_header)
            
            for rec in ai_insights.get('recommendations', [])[:3]:
                rec_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                rec_row.add_css_class("app-item")
                rec_row.set_margin_bottom(4)
                
                arrow = Gtk.Label(label="→")
                arrow.set_width_chars(2)
                arrow.add_css_class("dim-label")
                rec_row.append(arrow)
                
                rec_label = Gtk.Label(label=rec)
                rec_label.set_wrap(True)
                rec_label.set_xalign(0)
                rec_label.set_hexpand(True)
                rec_row.append(rec_label)
                
                self.productivity_box.append(rec_row)
        else:
            # Basic breakdown without AI
            dev_time = summary['categories'].get('Development', 0)
            browser_time = summary['categories'].get('Browser', 0)
            comm_time = summary['categories'].get('Communication', 0)
            
            breakdown = [
                ("Development Time", dev_time, "💻"),
                ("Browser Time", browser_time, "🌐"),
                ("Communication Time", comm_time, "💬"),
            ]
            
            for label, time, icon in breakdown:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row.add_css_class("app-item")
                
                icon_label = Gtk.Label(label=icon)
                icon_label.set_width_chars(3)
                row.append(icon_label)
                
                name_label = Gtk.Label(label=label)
                name_label.set_xalign(0)
                name_label.set_hexpand(True)
                name_label.add_css_class("heading")
                row.append(name_label)
                
                time_label = Gtk.Label(label=self.format_duration(time))
                time_label.add_css_class("time-badge")
                row.append(time_label)
                
                self.productivity_box.append(row)
    
    def update_report(self):
        """Update report view"""
        year = self.current_date.year
        month = f"{self.current_date.month:02d}"
        date_str = self.current_date.strftime('%Y-%m-%d')
        report_file = REPORT_DIR / str(year) / month / f"report_{date_str}.html"
        
        if report_file.exists():
            report_uri = report_file.as_uri()
            self.report_webview.load_uri(report_uri)
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                        padding: 40px;
                    }}
                    .icon {{ font-size: 96px; margin-bottom: 32px; animation: float 3s ease-in-out infinite; }}
                    @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-20px); }} }}
                    h1 {{ font-size: 48px; font-weight: 700; margin: 0 0 16px 0; }}
                    p {{ font-size: 20px; opacity: 0.9; max-width: 600px; line-height: 1.8; }}
                    .date {{ font-weight: 600; background: rgba(255,255,255,0.2); padding: 12px 24px; border-radius: 24px; display: inline-block; margin-top: 32px; font-size: 18px; }}
                </style>
            </head>
            <body>
                <div class="icon">📄</div>
                <h1>Report Not Available</h1>
                <p>The daily report for this date hasn't been generated yet. Reports are automatically created at midnight for the previous day.</p>
                <div class="date">{self.current_date.strftime('%B %d, %Y')}</div>
            </body>
            </html>
            """
            self.report_webview.load_html(html_content, None)
    
    def create_empty_state(self, icon, title, subtitle):
        """Create an empty state widget"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(60)
        box.set_margin_bottom(60)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("title-1")
        box.append(icon_label)
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("title-2")
        box.append(title_label)
        
        subtitle_label = Gtk.Label(label=subtitle)
        subtitle_label.add_css_class("dim-label")
        box.append(subtitle_label)
        
        return box
    
    def on_prev_day(self, button):
        """Navigate to previous day"""
        self.current_date -= timedelta(days=1)
        self.update_display()
    
    def on_next_day(self, button):
        """Navigate to next day"""
        self.current_date += timedelta(days=1)
        self.update_display()
    
    def on_today(self, button):
        """Navigate to today"""
        self.current_date = datetime.now().date()
        self.update_display()


class GoalinApplication(Adw.Application):
    """Main application class"""
    
    def __init__(self):
        super().__init__(application_id='com.github.goalin',
                        flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        # Add actions
        self.create_action('generate_report', self.on_generate_report)
        self.create_action('open_reports', self.on_open_reports)
        self.create_action('preferences', self.on_preferences)
        self.create_action('about', self.on_about)
        self.create_action('quit', self.on_quit)
    
    def do_activate(self):
        """Called when the application is activated"""
        # Check if setup is complete
        if not is_setup_complete():
            self.run_setup_wizard()
            return
        
        win = self.props.active_window
        if not win:
            win = GoalinWindow(application=self)
        win.present()
    
    def run_setup_wizard(self):
        """Run the initial setup wizard"""
        try:
            from goalin.setup_wizard import SetupWizard
            wizard = SetupWizard(application=self)
            wizard.connect('close-request', self.on_setup_complete)
            wizard.present()
        except Exception as e:
            logger.error(f"Failed to run setup wizard: {e}")
            # Continue with main app even if setup fails
            self.do_activate()
    
    def on_setup_complete(self, wizard):
        """Called when setup wizard is closed"""
        if wizard.setup_complete:
            # Setup was completed, now show main window
            win = GoalinWindow(application=self)
            win.present()
        else:
            # Setup was cancelled, quit
            self.quit()
        return False
    
    def create_action(self, name, callback):
        """Create an application action"""
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
    
    def on_generate_report(self, action, param):
        """Generate a report for the current date"""
        from goalin.report import ReportGenerator
        
        db = ActivityDatabase()
        generator = ReportGenerator(db)
        
        try:
            yesterday = (datetime.now() - timedelta(days=1)).date()
            report_path = generator.generate_report(yesterday)
            
            dialog = Adw.MessageDialog.new(self.props.active_window)
            dialog.set_heading("Report Generated")
            dialog.set_body(f"Report saved to:\n{report_path}")
            dialog.add_response("ok", "OK")
            dialog.present()
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            
            dialog = Adw.MessageDialog.new(self.props.active_window)
            dialog.set_heading("Error")
            dialog.set_body(f"Failed to generate report: {e}")
            dialog.add_response("ok", "OK")
            dialog.present()
        finally:
            db.close()
    
    def on_open_reports(self, action, param):
        """Open the reports folder"""
        import subprocess
        subprocess.Popen(['xdg-open', str(REPORT_DIR)])
    
    def on_preferences(self, action, param):
        """Show preferences dialog"""
        dialog = Adw.MessageDialog.new(self.props.active_window)
        dialog.set_heading("Preferences")
        dialog.set_body("Preferences dialog coming soon!")
        dialog.add_response("ok", "OK")
        dialog.present()
    
    def on_about(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(
            application_name="Goalin",
            application_icon="org.gnome.Calendar",
            developer_name="YadavYashvant",
            version="0.2.0",
            website="https://github.com/YadavYashvant/Goalin",
            issue_url="https://github.com/YadavYashvant/Goalin/issues",
            license_type=Gtk.License.MIT_X11,
            developers=["YadavYashvant"],
            copyright="© 2025 YadavYashvant"
        )
        about.set_transient_for(self.props.active_window)
        about.present()
    
    def on_quit(self, action, param):
        """Quit the application"""
        self.quit()


def main():
    """Entry point for GUI application"""
    ensure_directories()
    app = GoalinApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    main()
