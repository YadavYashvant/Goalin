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
        Generate an HTML report
        
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
        
        # Sort categories by time spent
        sorted_categories = sorted(
            categories.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Build category rows
        category_rows = ""
        for category, duration in sorted_categories:
            percentage = self._format_percentage(duration, total_active)
            category_rows += f"""
                <tr>
                    <td>{category}</td>
                    <td>{self._format_duration(duration)}</td>
                    <td>{percentage}</td>
                </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goalin Report - {date.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .stat-value {{
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 14px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Goalin - Daily Productivity Report</h1>
        <p><strong>Date:</strong> {date.strftime('%A, %B %d, %Y')}</p>
        
        <h2>Overview</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Active Time</div>
                <div class="stat-value">{self._format_duration(total_active)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Idle Time</div>
                <div class="stat-value">{self._format_duration(total_idle)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Most Used App</div>
                <div class="stat-value" style="font-size: 18px;">{most_used}</div>
            </div>
        </div>
        
        <h2>Time by Category</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Time Spent</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {category_rows}
            </tbody>
        </table>
        
        <div class="footer">
            Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
