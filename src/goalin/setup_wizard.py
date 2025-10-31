#!/usr/bin/env python3
"""
Initial Setup Wizard for Goalin
Handles first-time configuration including AI setup
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import logging
import threading

from .ai_assistant import AIAssistant
from .config import ensure_directories

logger = logging.getLogger(__name__)


class SetupWizard(Adw.ApplicationWindow):
    """Setup wizard for first-time Goalin configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_title("Goalin Setup")
        self.set_default_size(700, 600)
        self.set_modal(True)
        
        self.ai_assistant = None
        self.setup_complete = False
        
        # Create main box with header
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)
        
        # Create stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        
        # Create pages
        self.create_welcome_page()
        self.create_ai_setup_page()
        self.create_categorization_page()
        self.create_complete_page()
        
        main_box.append(self.stack)
        
        self.set_content(main_box)
        
        self.apply_custom_css()
    
    def apply_custom_css(self):
        """Apply custom styling"""
        css = b"""
        .setup-title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .setup-subtitle {
            font-size: 16px;
            opacity: 0.7;
            margin-bottom: 30px;
        }
        
        .setup-content {
            padding: 40px;
        }
        
        .feature-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
        }
        
        .api-key-entry {
            font-family: monospace;
            font-size: 14px;
        }
        
        .progress-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        """
        
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def create_welcome_page(self):
        """Create welcome page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_valign(Gtk.Align.CENTER)
        page.set_halign(Gtk.Align.CENTER)
        page.add_css_class('setup-content')
        
        # Icon
        icon = Gtk.Label(label="🎯")
        icon.set_css_classes(['setup-title'])
        icon.get_style_context().add_class('dim-label')
        page.append(icon)
        
        # Title
        title = Gtk.Label(label="Welcome to Goalin")
        title.set_css_classes(['setup-title'])
        page.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(
            label="Your AI-powered productivity tracking assistant"
        )
        subtitle.set_css_classes(['setup-subtitle'])
        page.append(subtitle)
        
        # Features
        features = [
            ("🤖", "AI-Powered Categorization", "Automatically categorize all your apps intelligently"),
            ("📊", "Smart Analytics", "Get AI-driven insights about your productivity"),
            ("🔒", "Privacy First", "Your API key, your data, your control"),
            ("⚡", "Real-time Tracking", "Monitor your activity as it happens")
        ]
        
        for emoji, title_text, desc in features:
            feature_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
            feature_box.add_css_class('feature-box')
            
            emoji_label = Gtk.Label(label=emoji)
            emoji_label.set_size_request(40, -1)
            feature_box.append(emoji_label)
            
            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            
            feature_title = Gtk.Label(label=title_text)
            feature_title.set_halign(Gtk.Align.START)
            feature_title.set_markup(f"<b>{title_text}</b>")
            text_box.append(feature_title)
            
            feature_desc = Gtk.Label(label=desc)
            feature_desc.set_halign(Gtk.Align.START)
            feature_desc.set_wrap(True)
            feature_desc.set_opacity(0.7)
            text_box.append(feature_desc)
            
            feature_box.append(text_box)
            page.append(feature_box)
        
        # Button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(30)
        
        next_btn = Gtk.Button(label="Get Started")
        next_btn.add_css_class('suggested-action')
        next_btn.add_css_class('pill')
        next_btn.set_size_request(200, 50)
        next_btn.connect('clicked', lambda b: self.stack.set_visible_child_name('ai-setup'))
        button_box.append(next_btn)
        
        page.append(button_box)
        
        self.stack.add_named(page, 'welcome')
    
    def create_ai_setup_page(self):
        """Create AI setup page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_valign(Gtk.Align.CENTER)
        page.set_halign(Gtk.Align.CENTER)
        page.add_css_class('setup-content')
        
        # Title
        title = Gtk.Label(label="🤖 AI Configuration")
        title.set_css_classes(['setup-title'])
        page.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(
            label="Enter your Google Gemini API key for AI features"
        )
        subtitle.set_css_classes(['setup-subtitle'])
        subtitle.set_wrap(True)
        page.append(subtitle)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        info_box.add_css_class('feature-box')
        info_box.set_margin_bottom(20)
        
        info_text = Gtk.Label()
        info_text.set_markup(
            "<b>How to get a Gemini API key:</b>\n"
            "1. Visit: https://aistudio.google.com/app/apikey\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Create API Key'\n"
            "4. Copy the key and paste it below\n\n"
            "<i>Note: The free tier includes 60 requests per minute</i>"
        )
        info_text.set_halign(Gtk.Align.START)
        info_text.set_wrap(True)
        info_box.append(info_text)
        page.append(info_box)
        
        # API Key entry
        entry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        entry_box.set_size_request(500, -1)
        
        entry_label = Gtk.Label(label="Gemini API Key:")
        entry_label.set_halign(Gtk.Align.START)
        entry_box.append(entry_label)
        
        self.api_key_entry = Gtk.Entry()
        self.api_key_entry.set_placeholder_text("AIza...")
        self.api_key_entry.add_css_class('api-key-entry')
        self.api_key_entry.set_visibility(False)
        self.api_key_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        entry_box.append(self.api_key_entry)
        
        # Show/Hide button
        show_btn = Gtk.CheckButton(label="Show API Key")
        show_btn.connect('toggled', lambda b: self.api_key_entry.set_visibility(b.get_active()))
        entry_box.append(show_btn)
        
        page.append(entry_box)
        
        # Status label
        self.api_status_label = Gtk.Label()
        self.api_status_label.set_margin_top(10)
        page.append(self.api_status_label)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(30)
        
        skip_btn = Gtk.Button(label="Skip (Use Basic Mode)")
        skip_btn.connect('clicked', self.on_skip_ai_setup)
        button_box.append(skip_btn)
        
        validate_btn = Gtk.Button(label="Validate & Continue")
        validate_btn.add_css_class('suggested-action')
        validate_btn.add_css_class('pill')
        validate_btn.connect('clicked', self.on_validate_api_key)
        button_box.append(validate_btn)
        
        page.append(button_box)
        
        self.stack.add_named(page, 'ai-setup')
    
    def create_categorization_page(self):
        """Create app categorization page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_valign(Gtk.Align.CENTER)
        page.set_halign(Gtk.Align.CENTER)
        page.add_css_class('setup-content')
        
        # Title
        title = Gtk.Label(label="📦 Categorizing Applications")
        title.set_css_classes(['setup-title'])
        page.append(title)
        
        # Subtitle
        self.cat_subtitle = Gtk.Label(label="Detecting installed applications...")
        self.cat_subtitle.set_css_classes(['setup-subtitle'])
        page.append(self.cat_subtitle)
        
        # Progress box
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        progress_box.add_css_class('progress-box')
        progress_box.set_size_request(500, -1)
        
        self.cat_progress_label = Gtk.Label(label="Initializing...")
        self.cat_progress_label.set_halign(Gtk.Align.START)
        progress_box.append(self.cat_progress_label)
        
        self.cat_progress_bar = Gtk.ProgressBar()
        self.cat_progress_bar.set_show_text(True)
        progress_box.append(self.cat_progress_bar)
        
        self.cat_current_app = Gtk.Label(label="")
        self.cat_current_app.set_halign(Gtk.Align.START)
        self.cat_current_app.set_opacity(0.7)
        progress_box.append(self.cat_current_app)
        
        page.append(progress_box)
        
        # Continue button (initially hidden)
        self.cat_continue_btn = Gtk.Button(label="Continue")
        self.cat_continue_btn.add_css_class('suggested-action')
        self.cat_continue_btn.add_css_class('pill')
        self.cat_continue_btn.set_margin_top(30)
        self.cat_continue_btn.set_visible(False)
        self.cat_continue_btn.connect('clicked', lambda b: self.stack.set_visible_child_name('complete'))
        page.append(self.cat_continue_btn)
        
        self.stack.add_named(page, 'categorization')
    
    def create_complete_page(self):
        """Create completion page"""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_valign(Gtk.Align.CENTER)
        page.set_halign(Gtk.Align.CENTER)
        page.add_css_class('setup-content')
        
        # Icon
        icon = Gtk.Label(label="✅")
        icon.set_css_classes(['setup-title'])
        page.append(icon)
        
        # Title
        title = Gtk.Label(label="Setup Complete!")
        title.set_css_classes(['setup-title'])
        page.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(label="You're all set to track your productivity")
        subtitle.set_css_classes(['setup-subtitle'])
        page.append(subtitle)
        
        # Summary
        summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        summary_box.add_css_class('feature-box')
        
        self.summary_label = Gtk.Label()
        self.summary_label.set_wrap(True)
        summary_box.append(self.summary_label)
        
        page.append(summary_box)
        
        # Button
        finish_btn = Gtk.Button(label="Start Using Goalin")
        finish_btn.add_css_class('suggested-action')
        finish_btn.add_css_class('pill')
        finish_btn.set_size_request(200, 50)
        finish_btn.set_margin_top(30)
        finish_btn.connect('clicked', self.on_finish)
        page.append(finish_btn)
        
        self.stack.add_named(page, 'complete')
    
    def on_validate_api_key(self, button):
        """Validate API key"""
        api_key = self.api_key_entry.get_text().strip()
        
        if not api_key:
            self.api_status_label.set_markup(
                '<span foreground="red">⚠️ Please enter an API key</span>'
            )
            return
        
        # Show loading
        self.api_status_label.set_text("🔄 Validating...")
        button.set_sensitive(False)
        
        def validate():
            try:
                self.ai_assistant = AIAssistant(api_key)
                
                if self.ai_assistant.is_configured():
                    # Save the API key
                    self.ai_assistant.save_api_key(api_key)
                    
                    GLib.idle_add(lambda: self.on_api_key_validated(True))
                else:
                    GLib.idle_add(lambda: self.on_api_key_validated(False))
                    
            except Exception as e:
                logger.error(f"API key validation failed: {e}")
                GLib.idle_add(lambda: self.on_api_key_validated(False))
        
        thread = threading.Thread(target=validate, daemon=True)
        thread.start()
    
    def on_api_key_validated(self, success):
        """Handle API key validation result"""
        if success:
            self.api_status_label.set_markup(
                '<span foreground="green">✅ API key is valid!</span>'
            )
            # Move to categorization
            GLib.timeout_add(1000, lambda: self.start_categorization())
        else:
            self.api_status_label.set_markup(
                '<span foreground="red">⚠️ Invalid API key. Please check and try again.</span>'
            )
    
    def on_skip_ai_setup(self, button):
        """Skip AI setup"""
        self.ai_assistant = None
        self.update_summary(ai_enabled=False)
        self.stack.set_visible_child_name('complete')
    
    def start_categorization(self):
        """Start app categorization process"""
        self.stack.set_visible_child_name('categorization')
        
        def categorize():
            # Detect apps
            GLib.idle_add(lambda: self.cat_subtitle.set_text("Detecting installed applications..."))
            apps = self.ai_assistant.detect_installed_apps()
            
            total = len(apps)
            GLib.idle_add(lambda: self.cat_subtitle.set_text(f"Found {total} applications. Categorizing..."))
            
            def progress_callback(current, total, app_name):
                fraction = current / total if total > 0 else 0
                GLib.idle_add(lambda: self.cat_progress_bar.set_fraction(fraction))
                GLib.idle_add(lambda: self.cat_progress_bar.set_text(f"{current}/{total}"))
                GLib.idle_add(lambda: self.cat_current_app.set_text(f"Categorizing: {app_name}"))
                GLib.idle_add(lambda: self.cat_progress_label.set_text(f"Progress: {current}/{total} apps"))
            
            # Categorize apps
            self.ai_assistant.categorize_apps(apps, progress_callback)
            
            # Complete
            GLib.idle_add(lambda: self.cat_subtitle.set_text("Categorization complete!"))
            GLib.idle_add(lambda: self.cat_progress_label.set_text(f"Successfully categorized {total} applications"))
            GLib.idle_add(lambda: self.cat_current_app.set_text("✅ All done!"))
            GLib.idle_add(lambda: self.cat_continue_btn.set_visible(True))
            GLib.idle_add(lambda: self.update_summary(ai_enabled=True, app_count=total))
        
        thread = threading.Thread(target=categorize, daemon=True)
        thread.start()
    
    def update_summary(self, ai_enabled: bool, app_count: int = 0):
        """Update completion summary"""
        if ai_enabled:
            summary_text = (
                f"<b>✅ AI Features Enabled</b>\n\n"
                f"• {app_count} applications categorized\n"
                f"• Smart productivity analysis enabled\n"
                f"• AI-powered insights ready\n\n"
                f"<i>You can reconfigure AI settings anytime in the app preferences.</i>"
            )
        else:
            summary_text = (
                f"<b>📋 Basic Mode</b>\n\n"
                f"• Using predefined categories\n"
                f"• Basic productivity metrics\n"
                f"• You can enable AI features later in settings\n\n"
                f"<i>To enable AI features, add your Gemini API key in settings.</i>"
            )
        
        self.summary_label.set_markup(summary_text)
    
    def on_finish(self, button):
        """Finish setup"""
        self.setup_complete = True
        
        # Mark setup as complete
        ensure_directories()
        from .config import CONFIG_DIR
        setup_file = CONFIG_DIR / '.setup_complete'
        setup_file.touch()
        
        self.close()


class SetupWizardApp(Adw.Application):
    """Application wrapper for setup wizard"""
    
    def __init__(self):
        super().__init__(application_id='com.goalin.setup')
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        self.win = SetupWizard(application=app)
        self.win.present()


def run_setup_wizard():
    """Run the setup wizard"""
    ensure_directories()
    app = SetupWizardApp()
    app.run(None)


if __name__ == '__main__':
    run_setup_wizard()
