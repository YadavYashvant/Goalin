#!/usr/bin/env python3
"""
Background daemon for continuous activity tracking
"""

import time
import signal
import logging
import sys
from datetime import datetime, time as datetime_time
from pathlib import Path

from goalin.config import POLL_INTERVAL, IDLE_THRESHOLD, REPORT_TIME, get_category, ensure_directories
from goalin.database import ActivityDatabase
from goalin.tracker import ActivityTracker
from goalin.report import ReportGenerator
from goalin.browser_history import BrowserHistoryTracker

# Setup logging
LOG_DIR = Path.home() / '.local' / 'share' / 'goalin' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'daemon.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class GoalinDaemon:
    """Main daemon for activity tracking"""
    
    def __init__(self):
        self.running = True
        self.db = ActivityDatabase()
        self.tracker = ActivityTracker()
        self.browser_tracker = BrowserHistoryTracker()
        self.report_generator = ReportGenerator(self.db)
        self.last_report_date = None
        self.last_browser_sync = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("Goalin daemon initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _should_generate_report(self) -> bool:
        """Check if it's time to generate a daily report"""
        now = datetime.now()
        today = now.date()
        
        # Parse report time
        report_hour, report_minute = map(int, REPORT_TIME.split(':'))
        report_time = datetime_time(report_hour, report_minute)
        
        # Check if we've passed the report time today and haven't generated yet
        if (now.time() >= report_time and 
            self.last_report_date != today):
            return True
        
        return False
    
    def track_activity(self):
        """Track current activity"""
        try:
            # Check if user is idle
            is_idle = self.tracker.is_idle(IDLE_THRESHOLD)
            
            if is_idle:
                # Log idle time
                self.db.log_activity(
                    window_title="Idle",
                    application="System",
                    category="Idle",
                    duration=POLL_INTERVAL,
                    is_idle=True
                )
                logger.debug("User is idle")
            else:
                # Get active window information
                window_title, app_name = self.tracker.get_active_window()
                
                if window_title and app_name:
                    category = get_category(app_name)
                    
                    # Log activity
                    self.db.log_activity(
                        window_title=window_title,
                        application=app_name,
                        category=category,
                        duration=POLL_INTERVAL,
                        is_idle=False
                    )
                    
                    logger.info(f"Tracked: {app_name} - {window_title[:50]}")
                else:
                    logger.warning("Could not detect active window")
                    
        except Exception as e:
            logger.error(f"Error tracking activity: {e}", exc_info=True)
    
    def generate_daily_report(self):
        """Generate daily report"""
        try:
            logger.info("Generating daily report...")
            yesterday = (datetime.now().date() - 
                        __import__('datetime').timedelta(days=1))
            
            report_path = self.report_generator.generate_report(yesterday)
            logger.info(f"Daily report generated: {report_path}")
            
            self.last_report_date = datetime.now().date()
            
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
    
    def sync_browser_history(self):
        """Sync browser history to database"""
        try:
            now = datetime.now()
            
            # Sync every 5 minutes
            if self.last_browser_sync is None or \
               (now - self.last_browser_sync).total_seconds() >= 300:
                
                logger.debug("Syncing browser history...")
                
                # Get history since last sync (or last hour if first sync)
                if self.last_browser_sync:
                    start_time = self.last_browser_sync
                else:
                    start_time = now - __import__('datetime').timedelta(hours=1)
                
                history = self.browser_tracker.get_history_for_period(start_time, now)
                
                if history:
                    self.db.log_browser_history(history)
                    logger.info(f"Synced {len(history)} browser history entries")
                
                self.last_browser_sync = now
                
        except Exception as e:
            logger.error(f"Error syncing browser history: {e}", exc_info=True)
    
    def run(self):
        """Main daemon loop"""
        logger.info("Starting Goalin daemon...")
        
        while self.running:
            try:
                # Track current activity
                self.track_activity()
                
                # Sync browser history
                self.sync_browser_history()
                
                # Check if we should generate a daily report
                if self._should_generate_report():
                    self.generate_daily_report()
                
                # Sleep until next poll
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(POLL_INTERVAL)
        
        # Cleanup
        self.db.close()
        logger.info("Goalin daemon stopped")


def main():
    """Entry point for daemon"""
    ensure_directories()
    daemon = GoalinDaemon()
    daemon.run()


if __name__ == '__main__':
    main()
