#!/usr/bin/env python3
"""
GTK4 GUI application for Goalin
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

from goalin.database import ActivityDatabase
from goalin.config import ensure_directories

logger = logging.getLogger(__name__)


class GoalinWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.db = ActivityDatabase()
        self.current_date = datetime.now().date()
        
        # Window setup
        self.set_title("Goalin - Productivity Tracker")
        self.set_default_size(900, 600)
        
        # Create header bar
        header = Adw.HeaderBar()
        
        # Date navigation buttons
        prev_button = Gtk.Button(icon_name="go-previous-symbolic")
        prev_button.connect("clicked", self.on_prev_day)
        header.pack_start(prev_button)
        
        next_button = Gtk.Button(icon_name="go-next-symbolic")
        next_button.connect("clicked", self.on_next_day)
        header.pack_start(next_button)
        
        today_button = Gtk.Button(label="Today")
        today_button.connect("clicked", self.on_today)
        header.pack_start(today_button)
        
        # Menu button
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu = Gio.Menu()
        menu.append("Generate Report", "app.generate_report")
        menu.append("Open Reports Folder", "app.open_reports")
        menu.append("About", "app.about")
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        # Main content
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Toolbar box with header
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        
        # Content area - use Adwaita Clamp for better centering
        content_clamp = Adw.Clamp()
        content_clamp.set_maximum_size(1200)
        content_clamp.set_tightening_threshold(800)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        
        # Date label with better styling
        date_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.date_label = Gtk.Label()
        self.date_label.add_css_class("title-1")
        self.date_label.set_xalign(0)
        date_box.append(self.date_label)
        
        # Subtitle for context
        self.subtitle_label = Gtk.Label()
        self.subtitle_label.add_css_class("dim-label")
        self.subtitle_label.set_xalign(0)
        date_box.append(self.subtitle_label)
        
        content_box.append(date_box)
        
        # Stats cards with better spacing
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.stats_box.set_homogeneous(True)
        content_box.append(self.stats_box)
        
        # Notebook for tabs with modern styling
        notebook = Gtk.Notebook()
        notebook.set_vexpand(True)
        notebook.set_margin_top(8)
        
        # Category list tab
        category_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        category_container.set_margin_start(16)
        category_container.set_margin_end(16)
        category_container.set_margin_top(16)
        category_container.set_margin_bottom(16)
        
        # Category header
        category_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        category_header.set_margin_bottom(12)
        
        category_title = Gtk.Label(label="Time by Category")
        category_title.add_css_class("title-3")
        category_title.set_xalign(0)
        category_title.set_hexpand(True)
        category_header.append(category_title)
        
        category_container.append(category_header)
        
        # Category list with better styling
        self.category_list = Gtk.ListBox()
        self.category_list.add_css_class("boxed-list")
        self.category_list.set_selection_mode(Gtk.SelectionMode.NONE)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.category_list)
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        category_container.append(scrolled)
        notebook.append_page(category_container, Gtk.Label(label="📊 Categories"))
        
        # Browser history tab
        browser_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        browser_container.set_margin_start(16)
        browser_container.set_margin_end(16)
        browser_container.set_margin_top(16)
        browser_container.set_margin_bottom(16)
        
        # Browser header
        browser_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        browser_header.set_margin_bottom(12)
        
        browser_title = Gtk.Label(label="Firefox Activity")
        browser_title.add_css_class("title-3")
        browser_title.set_xalign(0)
        browser_title.set_hexpand(True)
        browser_header.append(browser_title)
        
        browser_container.append(browser_header)
        
        # Browser list with better styling
        self.browser_list = Gtk.ListBox()
        self.browser_list.add_css_class("boxed-list")
        self.browser_list.set_selection_mode(Gtk.SelectionMode.NONE)
        
        browser_scrolled = Gtk.ScrolledWindow()
        browser_scrolled.set_child(self.browser_list)
        browser_scrolled.set_vexpand(True)
        browser_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        browser_container.append(browser_scrolled)
        notebook.append_page(browser_container, Gtk.Label(label="🦊 Firefox"))
        
        content_box.append(notebook)
        content_clamp.set_child(content_box)
        
        toolbar.set_content(content_clamp)
        self.set_content(toolbar)
        
        # Load initial data
        self.update_display()
    
    def create_stat_card(self, title: str, value: str, icon: str = None) -> Gtk.Box:
        """Create a statistics card with modern styling"""
        # Use Adwaita PreferencesGroup for better card styling
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("card")
        
        inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inner_box.set_margin_start(20)
        inner_box.set_margin_end(20)
        inner_box.set_margin_top(20)
        inner_box.set_margin_bottom(20)
        
        # Icon if provided
        if icon:
            icon_label = Gtk.Label(label=icon)
            icon_label.add_css_class("title-1")
            icon_label.set_xalign(0.5)
            inner_box.append(icon_label)
        
        # Value with larger, bold text
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("title-1")
        value_label.set_xalign(0.5)
        inner_box.append(value_label)
        
        # Title with dimmed text
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("caption")
        title_label.add_css_class("dim-label")
        title_label.set_xalign(0.5)
        inner_box.append(title_label)
        
        card.append(inner_box)
        return card
    
    def format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_display(self):
        """Update the display with current date data"""
        # Update date label
        date_str = self.current_date.strftime('%A, %B %d, %Y')
        self.date_label.set_text(date_str)
        
        # Update subtitle
        today = datetime.now().date()
        if self.current_date == today:
            self.subtitle_label.set_text("Today's Activity")
        elif self.current_date == today - timedelta(days=1):
            self.subtitle_label.set_text("Yesterday's Activity")
        else:
            days_diff = (today - self.current_date).days
            if days_diff > 0:
                self.subtitle_label.set_text(f"{days_diff} days ago")
            else:
                self.subtitle_label.set_text(f"In {abs(days_diff)} days")
        
        # Get summary data
        summary = self.db.get_summary_by_date(self.current_date)
        
        # Clear stats box
        while self.stats_box.get_first_child():
            self.stats_box.remove(self.stats_box.get_first_child())
        
        # Add stat cards with icons
        active_time = self.format_duration(summary['total_active_time'])
        idle_time = self.format_duration(summary['total_idle_time'])
        most_used = summary['most_used_app']
        
        self.stats_box.append(self.create_stat_card("Active Time", active_time, "⏱️"))
        self.stats_box.append(self.create_stat_card("Idle Time", idle_time, "💤"))
        self.stats_box.append(self.create_stat_card("Most Used", most_used, "⭐"))
        
        # Update category list
        while self.category_list.get_first_child():
            self.category_list.remove(self.category_list.get_first_child())
        
        # Sort categories by time
        sorted_categories = sorted(
            summary['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_active = summary['total_active_time']
        # Category icons
        category_icons = {
            'Development': '💻',
            'Browser': '🌐',
            'Communication': '💬',
            'Media': '🎵',
            'Office': '📄',
            'Gaming': '🎮',
            'System': '⚙️',
            'Idle': '💤',
            'Other': '📦'
        }
        
        for category, duration in sorted_categories:
            row = Gtk.ListBoxRow()
            
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            
            # Category icon
            icon = category_icons.get(category, '📦')
            icon_label = Gtk.Label(label=icon)
            icon_label.set_width_chars(2)
            box.append(icon_label)
            
            # Category name and details
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            info_box.set_hexpand(True)
            
            cat_label = Gtk.Label(label=category)
            cat_label.set_xalign(0)
            cat_label.add_css_class("heading")
            info_box.append(cat_label)
            
            # Duration and percentage on same line
            detail_label = Gtk.Label()
            detail_label.set_xalign(0)
            detail_label.add_css_class("caption")
            detail_label.add_css_class("dim-label")
            
            if total_active > 0:
                percentage = (duration / total_active) * 100
                detail_label.set_markup(f"{self.format_duration(duration)} <span alpha='60%'>•</span> {percentage:.1f}%")
            else:
                detail_label.set_text(self.format_duration(duration))
            
            info_box.append(detail_label)
            box.append(info_box)
            
            # Progress indicator (visual bar)
            if total_active > 0:
                percentage = (duration / total_active) * 100
                progress = Gtk.ProgressBar()
                progress.set_fraction(percentage / 100)
                progress.set_valign(Gtk.Align.CENTER)
                progress.set_size_request(80, -1)
                box.append(progress)
            
            row.set_child(box)
            self.category_list.append(row)
        
        # Update browser history list
        self.update_browser_display()
    
    def update_browser_display(self):
        """Update the browser history display"""
        # Clear browser list
        while self.browser_list.get_first_child():
            self.browser_list.remove(self.browser_list.get_first_child())
        
        # Get browser summary
        browser_summary = self.db.get_browser_summary_by_date(self.current_date)
        
        if browser_summary['total_visits'] == 0:
            # Show empty state with status page
            row = Gtk.ListBoxRow()
            row.set_selectable(False)
            
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            empty_box.set_margin_top(60)
            empty_box.set_margin_bottom(60)
            empty_box.set_margin_start(20)
            empty_box.set_margin_end(20)
            
            # Icon
            icon_label = Gtk.Label(label="🦊")
            icon_label.add_css_class("title-1")
            empty_box.append(icon_label)
            
            # Message
            message_label = Gtk.Label(label="No Firefox Activity")
            message_label.add_css_class("title-3")
            empty_box.append(message_label)
            
            # Subtitle
            subtitle = Gtk.Label(label="Browse the web to see your activity here")
            subtitle.add_css_class("dim-label")
            empty_box.append(subtitle)
            
            row.set_child(empty_box)
            self.browser_list.append(row)
            return
        
        # Add header with total visits
        header_row = Gtk.ListBoxRow()
        header_row.set_selectable(False)
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_box.set_margin_start(16)
        header_box.set_margin_end(16)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(12)
        
        header_label = Gtk.Label(label=f"{browser_summary['total_visits']} Total Visits")
        header_label.add_css_class("title-2")
        header_label.set_xalign(0)
        header_box.append(header_label)
        
        subheader = Gtk.Label(label="Activity breakdown by category")
        subheader.add_css_class("caption")
        subheader.add_css_class("dim-label")
        subheader.set_xalign(0)
        header_box.append(subheader)
        
        header_row.set_child(header_box)
        self.browser_list.append(header_row)
        
        # Add category breakdown
        emoji_map = {
            'Development': '💻',
            'Learning': '📚',
            'Social Media': '📱',
            'Entertainment': '🎮',
            'News': '📰',
            'Shopping': '🛒',
            'Email': '📧',
            'Productivity': '📊',
            'Other': '🌐'
        }
        
        for category, count in sorted(browser_summary['categories'].items(), 
                                      key=lambda x: x[1], reverse=True):
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            
            # Category emoji/icon
            emoji = emoji_map.get(category, '🌐')
            emoji_label = Gtk.Label(label=emoji)
            emoji_label.set_width_chars(2)
            box.append(emoji_label)
            
            # Category info
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            info_box.set_hexpand(True)
            
            cat_label = Gtk.Label(label=category)
            cat_label.set_xalign(0)
            cat_label.add_css_class("heading")
            info_box.append(cat_label)
            
            # Visit count and percentage
            if browser_summary['total_visits'] > 0:
                percentage = (count / browser_summary['total_visits']) * 100
                detail_label = Gtk.Label()
                detail_label.set_xalign(0)
                detail_label.add_css_class("caption")
                detail_label.add_css_class("dim-label")
                detail_label.set_markup(f"{count} visits <span alpha='60%'>•</span> {percentage:.1f}%")
                info_box.append(detail_label)
            
            box.append(info_box)
            
            # Progress bar
            if browser_summary['total_visits'] > 0:
                percentage = (count / browser_summary['total_visits']) * 100
                progress = Gtk.ProgressBar()
                progress.set_fraction(percentage / 100)
                progress.set_valign(Gtk.Align.CENTER)
                progress.set_size_request(80, -1)
                box.append(progress)
            
            row.set_child(box)
            self.browser_list.append(row)
        
        # Add separator
        separator_row = Gtk.ListBoxRow()
        separator_row.set_selectable(False)
        separator = Gtk.Separator()
        separator.set_margin_top(16)
        separator.set_margin_bottom(16)
        separator_row.set_child(separator)
        self.browser_list.append(separator_row)
        
        # Add top domains header
        domain_header = Gtk.ListBoxRow()
        domain_header.set_selectable(False)
        domain_header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        domain_header_box.set_margin_start(16)
        domain_header_box.set_margin_end(16)
        domain_header_box.set_margin_top(8)
        domain_header_box.set_margin_bottom(8)
        
        domain_header_label = Gtk.Label(label="Top Websites")
        domain_header_label.add_css_class("title-3")
        domain_header_label.set_xalign(0)
        domain_header_box.append(domain_header_label)
        
        domain_subheader = Gtk.Label(label="Most visited domains")
        domain_subheader.add_css_class("caption")
        domain_subheader.add_css_class("dim-label")
        domain_subheader.set_xalign(0)
        domain_header_box.append(domain_subheader)
        
        domain_header.set_child(domain_header_box)
        self.browser_list.append(domain_header)
        
        for idx, domain_data in enumerate(browser_summary['domains'][:10], 1):
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            box.set_margin_top(10)
            box.set_margin_bottom(10)
            
            # Rank number
            rank_label = Gtk.Label(label=f"#{idx}")
            rank_label.add_css_class("monospace")
            rank_label.add_css_class("dim-label")
            rank_label.set_width_chars(3)
            rank_label.set_xalign(1)
            box.append(rank_label)
            
            # Domain info
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            info_box.set_hexpand(True)
            
            # Domain name
            domain_label = Gtk.Label(label=domain_data['domain'])
            domain_label.set_xalign(0)
            domain_label.add_css_class("heading")
            domain_label.set_ellipsize(3)  # ELLIPSIZE_END
            info_box.append(domain_label)
            
            # Category and visits
            detail_label = Gtk.Label()
            detail_label.set_xalign(0)
            detail_label.add_css_class("caption")
            detail_label.add_css_class("dim-label")
            
            emoji = emoji_map.get(domain_data['category'], '🌐')
            detail_label.set_markup(f"{emoji} {domain_data['category']} <span alpha='60%'>•</span> {domain_data['visits']} visits")
            info_box.append(detail_label)
            
            box.append(info_box)
            row.set_child(box)
            self.browser_list.append(row)
    
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
        self.create_action('about', self.on_about)
        self.create_action('quit', self.on_quit)
    
    def do_activate(self):
        """Called when the application is activated"""
        win = self.props.active_window
        if not win:
            win = GoalinWindow(application=self)
        win.present()
    
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
            
            # Show success dialog
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
        from goalin.config import REPORT_DIR
        import subprocess
        
        subprocess.Popen(['xdg-open', str(REPORT_DIR)])
    
    def on_about(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(
            application_name="Goalin",
            application_icon="org.gnome.Calendar",
            developer_name="YadavYashvant",
            version="0.1.0",
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
