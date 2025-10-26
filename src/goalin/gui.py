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
        
        # Content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        
        # Date label
        self.date_label = Gtk.Label()
        self.date_label.add_css_class("title-1")
        content_box.append(self.date_label)
        
        # Stats cards
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.stats_box.set_homogeneous(True)
        content_box.append(self.stats_box)
        
        # Notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_vexpand(True)
        
        # Category list tab
        category_frame = Gtk.Frame()
        
        self.category_list = Gtk.ListBox()
        self.category_list.add_css_class("boxed-list")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.category_list)
        scrolled.set_vexpand(True)
        
        category_frame.set_child(scrolled)
        notebook.append_page(category_frame, Gtk.Label(label="Categories"))
        
        # Browser history tab
        browser_frame = Gtk.Frame()
        
        self.browser_list = Gtk.ListBox()
        self.browser_list.add_css_class("boxed-list")
        
        browser_scrolled = Gtk.ScrolledWindow()
        browser_scrolled.set_child(self.browser_list)
        browser_scrolled.set_vexpand(True)
        
        browser_frame.set_child(browser_scrolled)
        notebook.append_page(browser_frame, Gtk.Label(label="Firefox Activity"))
        
        content_box.append(notebook)
        
        toolbar.set_content(content_box)
        self.set_content(toolbar)
        
        # Load initial data
        self.update_display()
    
    def create_stat_card(self, title: str, value: str, icon: str = None) -> Gtk.Box:
        """Create a statistics card"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class("card")
        card.set_margin_start(6)
        card.set_margin_end(6)
        card.set_margin_top(6)
        card.set_margin_bottom(6)
        
        inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        inner_box.set_margin_start(16)
        inner_box.set_margin_end(16)
        inner_box.set_margin_top(16)
        inner_box.set_margin_bottom(16)
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("dim-label")
        inner_box.append(title_label)
        
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("title-2")
        inner_box.append(value_label)
        
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
        
        # Get summary data
        summary = self.db.get_summary_by_date(self.current_date)
        
        # Clear stats box
        while self.stats_box.get_first_child():
            self.stats_box.remove(self.stats_box.get_first_child())
        
        # Add stat cards
        active_time = self.format_duration(summary['total_active_time'])
        idle_time = self.format_duration(summary['total_idle_time'])
        most_used = summary['most_used_app']
        
        self.stats_box.append(self.create_stat_card("Active Time", active_time))
        self.stats_box.append(self.create_stat_card("Idle Time", idle_time))
        self.stats_box.append(self.create_stat_card("Most Used App", most_used))
        
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
        for category, duration in sorted_categories:
            row = Gtk.ListBoxRow()
            
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            
            # Category name
            label = Gtk.Label(label=category)
            label.set_xalign(0)
            label.set_hexpand(True)
            box.append(label)
            
            # Duration
            duration_label = Gtk.Label(label=self.format_duration(duration))
            duration_label.add_css_class("dim-label")
            box.append(duration_label)
            
            # Percentage
            if total_active > 0:
                percentage = (duration / total_active) * 100
                percent_label = Gtk.Label(label=f"{percentage:.1f}%")
                percent_label.add_css_class("dim-label")
                box.append(percent_label)
            
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
            # Show empty state
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label="No Firefox activity recorded for this day")
            label.add_css_class("dim-label")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            row.set_child(label)
            self.browser_list.append(row)
            return
        
        # Add header with total visits
        header_row = Gtk.ListBoxRow()
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(12)
        
        header_label = Gtk.Label(label=f"Total Firefox Visits: {browser_summary['total_visits']}")
        header_label.add_css_class("title-4")
        header_label.set_xalign(0)
        header_box.append(header_label)
        
        header_row.set_child(header_box)
        self.browser_list.append(header_row)
        
        # Add category breakdown
        for category, count in sorted(browser_summary['categories'].items(), 
                                      key=lambda x: x[1], reverse=True):
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            
            # Category emoji/icon
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
            emoji = emoji_map.get(category, '🌐')
            
            emoji_label = Gtk.Label(label=emoji)
            box.append(emoji_label)
            
            # Category name
            label = Gtk.Label(label=category)
            label.set_xalign(0)
            label.set_hexpand(True)
            box.append(label)
            
            # Visit count
            count_label = Gtk.Label(label=f"{count} visits")
            count_label.add_css_class("dim-label")
            box.append(count_label)
            
            # Percentage
            if browser_summary['total_visits'] > 0:
                percentage = (count / browser_summary['total_visits']) * 100
                percent_label = Gtk.Label(label=f"{percentage:.1f}%")
                percent_label.add_css_class("dim-label")
                box.append(percent_label)
            
            row.set_child(box)
            self.browser_list.append(row)
        
        # Add separator
        separator_row = Gtk.ListBoxRow()
        separator_row.set_selectable(False)
        separator = Gtk.Separator()
        separator.set_margin_top(8)
        separator.set_margin_bottom(8)
        separator_row.set_child(separator)
        self.browser_list.append(separator_row)
        
        # Add top domains
        domain_header = Gtk.ListBoxRow()
        domain_header_label = Gtk.Label(label="Top Websites")
        domain_header_label.add_css_class("title-4")
        domain_header_label.set_xalign(0)
        domain_header_label.set_margin_start(12)
        domain_header_label.set_margin_top(8)
        domain_header.set_child(domain_header_label)
        self.browser_list.append(domain_header)
        
        for domain_data in browser_summary['domains'][:10]:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            
            # Domain name
            domain_label = Gtk.Label(label=domain_data['domain'])
            domain_label.set_xalign(0)
            domain_label.add_css_class("title-5")
            box.append(domain_label)
            
            # Category and visits
            info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            cat_label = Gtk.Label(label=domain_data['category'])
            cat_label.add_css_class("dim-label")
            cat_label.set_xalign(0)
            info_box.append(cat_label)
            
            visits_label = Gtk.Label(label=f"• {domain_data['visits']} visits")
            visits_label.add_css_class("dim-label")
            info_box.append(visits_label)
            
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
