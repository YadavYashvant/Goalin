#!/usr/bin/env python3
"""
Report generation module for creating daily productivity reports
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
import json

from goalin.config import REPORT_DIR
from goalin.database import ActivityDatabase

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates activity reports"""
    
    def __init__(self, db: ActivityDatabase):
        self.db = db
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _format_percentage(self, part: int, total: int) -> str:
        """Calculate and format percentage"""
        if total == 0:
            return "0%"
        percentage = (part / total) * 100
        return f"{percentage:.1f}%"
    
    def generate_text_report(self, summary: Dict) -> str:
        """
        Generate a text-based report
        
        Args:
            summary: Summary dictionary from database
            
        Returns:
            Formatted text report
        """
        date = summary['date']
        total_active = summary['total_active_time']
        total_idle = summary['total_idle_time']
        most_used = summary['most_used_app']
        categories = summary['categories']
        
        total_tracked = total_active + total_idle
        
        lines = [
            "=" * 60,
            f"GOALIN - Daily Productivity Report",
            f"Date: {date.strftime('%A, %B %d, %Y')}",
            "=" * 60,
            "",
            "OVERVIEW",
            "-" * 60,
            f"Total Active Time:    {self._format_duration(total_active)}",
            f"Total Idle Time:      {self._format_duration(total_idle)}",
            f"Total Tracked Time:   {self._format_duration(total_tracked)}",
            f"Most Used App:        {most_used}",
            "",
            "TIME BY CATEGORY",
            "-" * 60,
        ]
        
        # Sort categories by time spent
        sorted_categories = sorted(
            categories.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for category, duration in sorted_categories:
            percentage = self._format_percentage(duration, total_active)
            lines.append(
                f"{category:.<30} {self._format_duration(duration):>10} ({percentage:>6})"
            )
        
        lines.extend([
            "",
            "=" * 60,
            f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def generate_json_report(self, summary: Dict) -> str:
        """
        Generate a JSON report
        
        Args:
            summary: Summary dictionary from database
            
        Returns:
            JSON string
        """
        report = {
            'date': summary['date'].isoformat(),
            'total_active_time_seconds': summary['total_active_time'],
            'total_active_time_formatted': self._format_duration(summary['total_active_time']),
            'total_idle_time_seconds': summary['total_idle_time'],
            'total_idle_time_formatted': self._format_duration(summary['total_idle_time']),
            'most_used_app': summary['most_used_app'],
            'categories': {},
            'generated_at': datetime.now().isoformat()
        }
        
        # Add category data
        total_active = summary['total_active_time']
        for category, duration in summary['categories'].items():
            report['categories'][category] = {
                'seconds': duration,
                'formatted': self._format_duration(duration),
                'percentage': float(self._format_percentage(duration, total_active).rstrip('%'))
            }
        
        return json.dumps(report, indent=2)
    
    def generate_html_report(self, summary: Dict) -> str:
        """
        Generate a modern, comprehensive HTML report
        
        Args:
            summary: Summary dictionary from database
            
        Returns:
            HTML string
        """
        date = summary['date']
        total_active = summary['total_active_time']
        total_idle = summary['total_idle_time']
        most_used = summary['most_used_app']
        categories = summary['categories']
        
        total_tracked = total_active + total_idle
        
        # Get detailed activity data
        activities = self.db.get_activities_by_date(date)
        
        # Analyze hourly patterns
        from collections import defaultdict
        hourly_data = defaultdict(int)
        app_durations = defaultdict(int)
        app_windows = defaultdict(list)
        
        for activity in activities:
            timestamp_str = activity[1]
            try:
                if '.' in timestamp_str:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                from pytz import timezone, utc
                local_tz = timezone('Asia/Kolkata')
                dt_utc = utc.localize(dt)
                dt_local = dt_utc.astimezone(local_tz)
                
                hour = dt_local.hour
                app = activity[3]
                window = activity[2]
                duration = activity[5]
                
                hourly_data[hour] += duration
                app_durations[app] += duration
                if window and window != 'Unknown':
                    app_windows[app].append(window)
            except:
                continue
        
        # Sort apps by usage
        sorted_apps = sorted(app_durations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Sort categories
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate productivity metrics
        productive_categories = ['Development', 'Office', 'Productivity']
        productive_time = sum(categories.get(cat, 0) for cat in productive_categories)
        productivity_score = (productive_time / total_active * 100) if total_active > 0 else 0
        
        # Get browser data
        browser_summary = self.db.get_browser_summary_by_date(date)
        
        # Build hourly chart data
        hourly_chart_data = []
        max_hour_duration = max(hourly_data.values()) if hourly_data else 1
        for hour in range(24):
            duration = hourly_data.get(hour, 0)
            height_percent = (duration / max_hour_duration * 100) if max_hour_duration > 0 else 0
            hourly_chart_data.append(f'{{"hour": {hour}, "duration": {duration}, "height": {height_percent:.1f}}}')
        
        # Build category chart data
        category_chart_data = []
        for category, duration in sorted_categories:
            percentage = (duration / total_active * 100) if total_active > 0 else 0
            category_chart_data.append(f'{{"category": "{category}", "duration": {duration}, "percentage": {percentage:.1f}}}')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goalin Report - {date.strftime('%Y-%m-%d')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #2d3748;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        
        .header h1 {{
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            font-size: 20px;
            color: #718096;
            font-weight: 500;
        }}
        
        .productivity-score {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-size: 18px;
            font-weight: 700;
            margin-top: 15px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }}
        
        .stat-icon {{
            font-size: 40px;
            margin-bottom: 15px;
        }}
        
        .stat-label {{
            color: #718096;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: 800;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .stat-subtext {{
            color: #a0aec0;
            font-size: 13px;
        }}
        
        .section {{
            background: white;
            border-radius: 16px;
            padding: 35px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .section h2 {{
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .section h2::before {{
            content: '';
            width: 5px;
            height: 30px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
        }}
        
        .hourly-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 200px;
            gap: 3px;
            padding: 20px 0;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .hour-bar {{
            flex: 1;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px 4px 0 0;
            position: relative;
            min-height: 2px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .hour-bar:hover {{
            opacity: 0.8;
            transform: scaleY(1.05);
        }}
        
        .hour-label {{
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 11px;
            color: #718096;
        }}
        
        .app-list {{
            display: grid;
            gap: 15px;
        }}
        
        .app-item {{
            display: flex;
            align-items: center;
            padding: 20px;
            background: #f7fafc;
            border-radius: 12px;
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }}
        
        .app-item:hover {{
            background: #edf2f7;
            border-left-color: #667eea;
            transform: translateX(5px);
        }}
        
        .app-rank {{
            font-size: 24px;
            font-weight: 800;
            color: #cbd5e0;
            width: 50px;
            text-align: center;
        }}
        
        .app-icon {{
            font-size: 32px;
            margin-right: 20px;
        }}
        
        .app-info {{
            flex: 1;
        }}
        
        .app-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .app-windows {{
            font-size: 13px;
            color: #718096;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .app-duration {{
            text-align: right;
        }}
        
        .app-time {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }}
        
        .app-percentage {{
            font-size: 13px;
            color: #a0aec0;
        }}
        
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .category-card {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .category-card:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
        }}
        
        .category-icon {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .category-name {{
            font-size: 16px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        
        .category-time {{
            font-size: 20px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .category-percent {{
            font-size: 13px;
            color: #718096;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        
        .browser-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .browser-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
        }}
        
        .browser-stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .browser-stat:last-child {{
            border-bottom: none;
        }}
        
        .browser-label {{
            font-size: 14px;
            color: #4a5568;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .browser-value {{
            font-size: 16px;
            font-weight: 600;
            color: #667eea;
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .insight-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .insight-icon {{
            font-size: 40px;
            margin-bottom: 15px;
        }}
        
        .insight-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        
        .insight-value {{
            font-size: 28px;
            font-weight: 800;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .hourly-chart {{
                height: 150px;
            }}
            
            .header h1 {{
                font-size: 32px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Daily Productivity Report</h1>
            <div class="date">{date.strftime('%A, %B %d, %Y')}</div>
            <div class="productivity-score">
                🎯 Productivity Score: {productivity_score:.1f}%
            </div>
        </div>
        
        <!-- Main Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">⏱️</div>
                <div class="stat-label">Active Time</div>
                <div class="stat-value">{self._format_duration(total_active)}</div>
                <div class="stat-subtext">{(total_active / total_tracked * 100) if total_tracked > 0 else 0:.1f}% of tracked time</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">💤</div>
                <div class="stat-label">Idle Time</div>
                <div class="stat-value">{self._format_duration(total_idle)}</div>
                <div class="stat-subtext">{(total_idle / total_tracked * 100) if total_tracked > 0 else 0:.1f}% of tracked time</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-label">Most Used App</div>
                <div class="stat-value" style="font-size: 24px;">{most_used}</div>
                <div class="stat-subtext">{self._format_duration(app_durations.get(most_used, 0))} spent</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">📦</div>
                <div class="stat-label">Total Apps Used</div>
                <div class="stat-value">{len(app_durations)}</div>
                <div class="stat-subtext">{len(categories)} categories</div>
            </div>
        </div>
        
        <!-- Hourly Activity Chart -->
        <div class="section">
            <h2>Activity Throughout the Day</h2>
            <div class="hourly-chart">
                {''.join(f'<div class="hour-bar" style="height: {(hourly_data.get(h, 0) / max_hour_duration * 100) if max_hour_duration > 0 else 0}%;" title="{h:02d}:00 - {self._format_duration(hourly_data.get(h, 0))}"></div>' for h in range(24))}
            </div>
            <div class="hour-label">
                <span>00:00</span>
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>23:59</span>
            </div>
        </div>
        
        <!-- Top Applications -->
        <div class="section">
            <h2>Top Applications</h2>
            <div class="app-list">
                {''.join(f'''<div class="app-item">
                    <div class="app-rank">#{i+1}</div>
                    <div class="app-icon">{'🦊' if 'firefox' in app.lower() else '💻' if any(x in app.lower() for x in ['code', 'vim']) else '⚡' if 'terminal' in app.lower() else '🎵' if 'spotify' in app.lower() else '💬' if any(x in app.lower() for x in ['discord', 'slack']) else '📦'}</div>
                    <div class="app-info">
                        <div class="app-name">{app.title()}</div>
                        <div class="app-windows">{', '.join(list(set(app_windows.get(app, ['No windows recorded'])))[:3])}</div>
                    </div>
                    <div class="app-duration">
                        <div class="app-time">{self._format_duration(dur)}</div>
                        <div class="app-percentage">{(dur / total_active * 100) if total_active > 0 else 0:.1f}%</div>
                    </div>
                </div>''' for i, (app, dur) in enumerate(sorted_apps))}
            </div>
        </div>
        
        <!-- Category Breakdown -->
        <div class="section">
            <h2>Time by Category</h2>
            <div class="category-grid">
                {''.join(f'''<div class="category-card">
                    <div class="category-icon">{'💻' if cat == 'Development' else '🌐' if cat == 'Browser' else '💬' if cat == 'Communication' else '🎵' if cat == 'Media' else '📄' if cat == 'Office' else '🎮' if cat == 'Gaming' else '⚙️' if cat == 'System' else '📦'}</div>
                    <div class="category-name">{cat}</div>
                    <div class="category-time">{self._format_duration(dur)}</div>
                    <div class="category-percent">{(dur / total_active * 100) if total_active > 0 else 0:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(dur / total_active * 100) if total_active > 0 else 0}%"></div>
                    </div>
                </div>''' for cat, dur in sorted_categories)}
            </div>
        </div>
        
        <!-- Browser Activity -->
        {'<div class="section"><h2>🦊 Browser Activity</h2><div class="browser-section">' if browser_summary['total_visits'] > 0 else ''}
        {'<div class="browser-card"><h3 style="margin-bottom: 15px; color: #2d3748;">Summary</h3>' + ''.join(f'<div class="browser-stat"><span class="browser-label">Total Visits</span><span class="browser-value">{browser_summary["total_visits"]}</span></div>') + '</div>' if browser_summary['total_visits'] > 0 else ''}
        {'<div class="browser-card"><h3 style="margin-bottom: 15px; color: #2d3748;">Top Categories</h3>' + ''.join(f'<div class="browser-stat"><span class="browser-label">{'💻' if cat == 'Development' else '📚' if cat == 'Learning' else '📱' if cat == 'Social Media' else '🎮' if cat == 'Entertainment' else '📰' if cat == 'News' else '🌐'} {cat}</span><span class="browser-value">{count} visits</span></div>' for cat, count in sorted(browser_summary['categories'].items(), key=lambda x: x[1], reverse=True)[:5]) + '</div>' if browser_summary['total_visits'] > 0 else ''}
        {'<div class="browser-card"><h3 style="margin-bottom: 15px; color: #2d3748;">Top Websites</h3>' + ''.join(f'<div class="browser-stat"><span class="browser-label">{i+1}. {domain["domain"][:30]}</span><span class="browser-value">{domain["visits"]}</span></div>' for i, domain in enumerate(browser_summary['domains'][:5])) + '</div>' if browser_summary['total_visits'] > 0 and browser_summary['domains'] else ''}
        {'</div></div>' if browser_summary['total_visits'] > 0 else ''}
        
        <!-- Insights -->
        <div class="section">
            <h2>Key Insights</h2>
            <div class="insights-grid">
                <div class="insight-card">
                    <div class="insight-icon">🌅</div>
                    <div class="insight-title">Most Active Hour</div>
                    <div class="insight-value">{max(hourly_data, key=hourly_data.get) if hourly_data else 0:02d}:00</div>
                </div>
                
                <div class="insight-card">
                    <div class="insight-icon">💪</div>
                    <div class="insight-title">Productive Time</div>
                    <div class="insight-value">{self._format_duration(productive_time)}</div>
                </div>
                
                <div class="insight-card">
                    <div class="insight-icon">🎯</div>
                    <div class="insight-title">Focus Sessions</div>
                    <div class="insight-value">{len([h for h, d in hourly_data.items() if d > 1800])}</div>
                </div>
                
                <div class="insight-card">
                    <div class="insight-icon">⚡</div>
                    <div class="insight-title">App Switches</div>
                    <div class="insight-value">{len(activities)}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by Goalin • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def generate_report(self, date: datetime.date = None, 
                       format: str = 'all') -> Path:
        """
        Generate activity report for a specific date
        
        Args:
            date: Date to generate report for (default: yesterday)
            format: Report format ('text', 'json', 'html', or 'all')
            
        Returns:
            Path to the generated report(s)
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).date()
        
        # Get summary data
        summary = self.db.get_summary_by_date(date)
        
        # Save summary to database
        self.db.save_daily_summary(date, summary)
        
        # Generate reports
        date_str = date.strftime('%Y-%m-%d')
        report_dir = REPORT_DIR / str(date.year) / f"{date.month:02d}"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        if format in ['text', 'all']:
            text_report = self.generate_text_report(summary)
            text_path = report_dir / f"report_{date_str}.txt"
            text_path.write_text(text_report)
            generated_files.append(text_path)
            logger.info(f"Generated text report: {text_path}")
        
        if format in ['json', 'all']:
            json_report = self.generate_json_report(summary)
            json_path = report_dir / f"report_{date_str}.json"
            json_path.write_text(json_report)
            generated_files.append(json_path)
            logger.info(f"Generated JSON report: {json_path}")
        
        if format in ['html', 'all']:
            html_report = self.generate_html_report(summary)
            html_path = report_dir / f"report_{date_str}.html"
            html_path.write_text(html_report)
            generated_files.append(html_path)
            logger.info(f"Generated HTML report: {html_path}")
        
        return generated_files[0] if generated_files else None


def main():
    """CLI entry point for report generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Goalin activity reports')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (default: yesterday)')
    parser.add_argument('--format', choices=['text', 'json', 'html', 'all'], 
                       default='all', help='Report format')
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        report_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        report_date = (datetime.now() - timedelta(days=1)).date()
    
    # Generate report
    db = ActivityDatabase()
    generator = ReportGenerator(db)
    
    try:
        report_path = generator.generate_report(report_date, args.format)
        print(f"Report generated: {report_path}")
    finally:
        db.close()


if __name__ == '__main__':
    main()
