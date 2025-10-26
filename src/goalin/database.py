#!/usr/bin/env python3
"""
Database management for activity tracking
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from goalin.config import DB_PATH, ensure_directories

logger = logging.getLogger(__name__)


class ActivityDatabase:
    """Manages the SQLite database for activity tracking"""
    
    def __init__(self, db_path: Path = DB_PATH):
        ensure_directories()
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Activity records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                window_title TEXT,
                application TEXT,
                category TEXT,
                duration INTEGER DEFAULT 0,
                is_idle BOOLEAN DEFAULT 0
            )
        ''')
        
        # Daily summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_active_time INTEGER,
                total_idle_time INTEGER,
                most_used_app TEXT,
                report_generated BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Category time table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_time (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                category TEXT,
                total_seconds INTEGER,
                UNIQUE(date, category)
            )
        ''')
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def log_activity(self, window_title: str, application: str, 
                    category: str, duration: int = 5, is_idle: bool = False):
        """
        Log an activity record
        
        Args:
            window_title: Title of the active window
            application: Name of the application
            category: Category of the application
            duration: Duration in seconds
            is_idle: Whether the user was idle
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO activities (window_title, application, category, duration, is_idle)
            VALUES (?, ?, ?, ?, ?)
        ''', (window_title, application, category, duration, is_idle))
        self.conn.commit()
    
    def get_today_activities(self) -> List[sqlite3.Row]:
        """Get all activities for today"""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT * FROM activities
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        ''', (today,))
        return cursor.fetchall()
    
    def get_activities_by_date(self, date: datetime.date) -> List[sqlite3.Row]:
        """Get all activities for a specific date"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        ''', (date,))
        return cursor.fetchall()
    
    def get_date_range_activities(self, start_date: datetime.date, 
                                  end_date: datetime.date) -> List[sqlite3.Row]:
        """Get activities within a date range"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities
            WHERE DATE(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))
        return cursor.fetchall()
    
    def get_today_summary(self) -> Dict:
        """Get summary statistics for today"""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        # Total active time
        cursor.execute('''
            SELECT SUM(duration) as total_time
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
        ''', (today,))
        result = cursor.fetchone()
        total_active_time = result['total_time'] or 0
        
        # Total idle time
        cursor.execute('''
            SELECT SUM(duration) as idle_time
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 1
        ''', (today,))
        result = cursor.fetchone()
        total_idle_time = result['idle_time'] or 0
        
        # Most used application
        cursor.execute('''
            SELECT application, SUM(duration) as total_duration
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
            GROUP BY application
            ORDER BY total_duration DESC
            LIMIT 1
        ''', (today,))
        result = cursor.fetchone()
        most_used_app = result['application'] if result else 'None'
        
        # Time by category
        cursor.execute('''
            SELECT category, SUM(duration) as total_duration
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
            GROUP BY category
            ORDER BY total_duration DESC
        ''', (today,))
        categories = {row['category']: row['total_duration'] for row in cursor.fetchall()}
        
        return {
            'date': today,
            'total_active_time': total_active_time,
            'total_idle_time': total_idle_time,
            'most_used_app': most_used_app,
            'categories': categories
        }
    
    def get_summary_by_date(self, date: datetime.date) -> Dict:
        """Get summary statistics for a specific date"""
        cursor = self.conn.cursor()
        
        # Total active time
        cursor.execute('''
            SELECT SUM(duration) as total_time
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
        ''', (date,))
        result = cursor.fetchone()
        total_active_time = result['total_time'] or 0
        
        # Total idle time
        cursor.execute('''
            SELECT SUM(duration) as idle_time
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 1
        ''', (date,))
        result = cursor.fetchone()
        total_idle_time = result['idle_time'] or 0
        
        # Most used application
        cursor.execute('''
            SELECT application, SUM(duration) as total_duration
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
            GROUP BY application
            ORDER BY total_duration DESC
            LIMIT 1
        ''', (date,))
        result = cursor.fetchone()
        most_used_app = result['application'] if result else 'None'
        
        # Time by category
        cursor.execute('''
            SELECT category, SUM(duration) as total_duration
            FROM activities
            WHERE DATE(timestamp) = ? AND is_idle = 0
            GROUP BY category
            ORDER BY total_duration DESC
        ''', (date,))
        categories = {row['category']: row['total_duration'] for row in cursor.fetchall()}
        
        return {
            'date': date,
            'total_active_time': total_active_time,
            'total_idle_time': total_idle_time,
            'most_used_app': most_used_app,
            'categories': categories
        }
    
    def save_daily_summary(self, date: datetime.date, summary: Dict):
        """Save daily summary to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summary 
            (date, total_active_time, total_idle_time, most_used_app, report_generated)
            VALUES (?, ?, ?, ?, 1)
        ''', (date, summary['total_active_time'], summary['total_idle_time'], 
              summary['most_used_app']))
        
        # Save category times
        for category, duration in summary['categories'].items():
            cursor.execute('''
                INSERT OR REPLACE INTO category_time (date, category, total_seconds)
                VALUES (?, ?, ?)
            ''', (date, category, duration))
        
        self.conn.commit()
    
    def get_weekly_summary(self) -> List[Dict]:
        """Get summary for the past 7 days"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        summaries = []
        current_date = week_ago
        while current_date <= today:
            summary = self.get_summary_by_date(current_date)
            summaries.append(summary)
            current_date += timedelta(days=1)
        
        return summaries
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
