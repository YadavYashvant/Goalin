#!/usr/bin/env python3
"""
Browser history integration for detailed activity tracking
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urlparse
import shutil

logger = logging.getLogger(__name__)


class BrowserHistoryTracker:
    """Tracks and analyzes browser history"""
    
    def __init__(self):
        self.firefox_profiles = self._find_firefox_profiles()
    
    def _find_firefox_profiles(self) -> List[Path]:
        """Find Firefox profile directories"""
        profiles = []
        
        # Firefox profile location
        firefox_dir = Path.home() / '.mozilla' / 'firefox'
        
        if not firefox_dir.exists():
            logger.warning("Firefox directory not found")
            return profiles
        
        # Find all profile directories (they end with .default or .default-release)
        for profile_dir in firefox_dir.iterdir():
            if profile_dir.is_dir() and not profile_dir.name.endswith('.ini'):
                places_db = profile_dir / 'places.sqlite'
                if places_db.exists():
                    profiles.append(profile_dir)
                    logger.info(f"Found Firefox profile: {profile_dir.name}")
        
        return profiles
    
    def _get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain or url
        except Exception:
            return url
    
    def _categorize_url(self, url: str, title: str) -> str:
        """Categorize URL based on domain and title"""
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        
        # Development/Programming
        if any(x in url_lower for x in ['github.com', 'stackoverflow.com', 'gitlab.com', 
                                         'docs.python.org', 'developer.mozilla.org',
                                         'reddit.com/r/programming', 'hackernews',
                                         'dev.to', 'medium.com/tag/programming']):
            return 'Development'
        
        # Learning/Documentation
        if any(x in url_lower for x in ['youtube.com/watch', 'udemy.com', 'coursera.org',
                                         'edx.org', 'pluralsight.com', 'freecodecamp.org',
                                         'khanacademy.org', 'w3schools.com', 'tutorial']):
            return 'Learning'
        
        # Social Media
        if any(x in url_lower for x in ['twitter.com', 'facebook.com', 'instagram.com',
                                         'linkedin.com', 'reddit.com', 'discord.com',
                                         'telegram.org', 'whatsapp.com']):
            return 'Social Media'
        
        # Entertainment
        if any(x in url_lower for x in ['youtube.com', 'netflix.com', 'spotify.com',
                                         'twitch.tv', 'primevideo.com', 'disneyplus.com']):
            return 'Entertainment'
        
        # News
        if any(x in url_lower for x in ['news', 'bbc.com', 'cnn.com', 'theguardian.com',
                                         'nytimes.com', 'reuters.com', 'techcrunch.com']):
            return 'News'
        
        # Shopping
        if any(x in url_lower for x in ['amazon.', 'ebay.com', 'flipkart.com',
                                         'shop', 'store', 'cart', 'checkout']):
            return 'Shopping'
        
        # Email
        if any(x in url_lower for x in ['mail.google.com', 'outlook.com', 'yahoo.com/mail',
                                         'protonmail.com']):
            return 'Email'
        
        # Productivity
        if any(x in url_lower for x in ['notion.so', 'trello.com', 'asana.com',
                                         'todoist.com', 'evernote.com', 'docs.google.com']):
            return 'Productivity'
        
        return 'Other'
    
    def get_history_for_period(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get browser history for a time period
        
        Args:
            start_time: Start of time period
            end_time: End of time period
            
        Returns:
            List of history entries with metadata
        """
        all_history = []
        
        for profile_dir in self.firefox_profiles:
            places_db = profile_dir / 'places.sqlite'
            
            # Copy database to avoid locking issues
            temp_db = Path('/tmp') / f'places_copy_{profile_dir.name}.sqlite'
            try:
                shutil.copy2(places_db, temp_db)
                
                conn = sqlite3.connect(str(temp_db))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Firefox stores timestamps in microseconds since epoch
                start_timestamp = int(start_time.timestamp() * 1000000)
                end_timestamp = int(end_time.timestamp() * 1000000)
                
                # Query history with visit times
                query = """
                    SELECT 
                        moz_places.url,
                        moz_places.title,
                        moz_historyvisits.visit_date,
                        moz_historyvisits.visit_type
                    FROM moz_historyvisits
                    JOIN moz_places ON moz_historyvisits.place_id = moz_places.id
                    WHERE moz_historyvisits.visit_date BETWEEN ? AND ?
                    ORDER BY moz_historyvisits.visit_date DESC
                """
                
                cursor.execute(query, (start_timestamp, end_timestamp))
                
                for row in cursor.fetchall():
                    url = row['url']
                    title = row['title'] or url
                    visit_date = datetime.fromtimestamp(row['visit_date'] / 1000000)
                    
                    all_history.append({
                        'url': url,
                        'title': title,
                        'domain': self._get_domain_from_url(url),
                        'category': self._categorize_url(url, title),
                        'timestamp': visit_date,
                        'profile': profile_dir.name
                    })
                
                conn.close()
                temp_db.unlink()
                
            except Exception as e:
                logger.error(f"Error reading Firefox history: {e}")
                if temp_db.exists():
                    temp_db.unlink()
        
        return all_history
    
    def get_today_history(self) -> List[Dict]:
        """Get today's browser history"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now()
        return self.get_history_for_period(today_start, today_end)
    
    def get_history_summary(self, history: List[Dict]) -> Dict:
        """
        Generate summary statistics from history
        
        Args:
            history: List of history entries
            
        Returns:
            Summary dict with statistics
        """
        if not history:
            return {
                'total_visits': 0,
                'unique_domains': 0,
                'categories': {},
                'top_domains': [],
                'top_sites': []
            }
        
        # Count by category
        categories = {}
        for entry in history:
            cat = entry['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        # Count by domain
        domain_counts = {}
        for entry in history:
            domain = entry['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Top domains
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top sites (with titles)
        site_counts = {}
        site_titles = {}
        for entry in history:
            url = entry['url']
            if url not in site_counts:
                site_counts[url] = 0
                site_titles[url] = entry['title']
            site_counts[url] += 1
        
        top_sites = [
            {'url': url, 'title': site_titles[url], 'visits': count}
            for url, count in sorted(site_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return {
            'total_visits': len(history),
            'unique_domains': len(domain_counts),
            'categories': categories,
            'top_domains': top_domains,
            'top_sites': top_sites
        }
    
    def get_timeline(self, history: List[Dict], interval_minutes: int = 30) -> List[Dict]:
        """
        Create a timeline of browser activity
        
        Args:
            history: List of history entries
            interval_minutes: Time interval for grouping
            
        Returns:
            Timeline with activity in each interval
        """
        if not history:
            return []
        
        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x['timestamp'])
        
        # Group by time intervals
        timeline = []
        current_interval_start = None
        current_interval = []
        
        for entry in sorted_history:
            timestamp = entry['timestamp']
            
            if current_interval_start is None:
                current_interval_start = timestamp.replace(second=0, microsecond=0)
            
            # Check if we're still in the same interval
            time_diff = (timestamp - current_interval_start).total_seconds() / 60
            
            if time_diff < interval_minutes:
                current_interval.append(entry)
            else:
                # Save current interval and start new one
                if current_interval:
                    timeline.append({
                        'start_time': current_interval_start,
                        'end_time': current_interval_start + timedelta(minutes=interval_minutes),
                        'visits': len(current_interval),
                        'domains': list(set(e['domain'] for e in current_interval)),
                        'categories': list(set(e['category'] for e in current_interval))
                    })
                
                current_interval_start = timestamp.replace(second=0, microsecond=0)
                current_interval = [entry]
        
        # Add last interval
        if current_interval:
            timeline.append({
                'start_time': current_interval_start,
                'end_time': current_interval_start + timedelta(minutes=interval_minutes),
                'visits': len(current_interval),
                'domains': list(set(e['domain'] for e in current_interval)),
                'categories': list(set(e['category'] for e in current_interval))
            })
        
        return timeline
