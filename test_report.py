#!/usr/bin/env python3
"""Test script to generate and view the new HTML report"""

from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/mobotronst/Codes/Goalin/src')

from goalin.database import ActivityDatabase
from goalin.report import ReportGenerator

# Generate report for yesterday
db = ActivityDatabase()
generator = ReportGenerator(db)

yesterday = (datetime.now() - timedelta(days=1)).date()
print(f"Generating report for {yesterday}...")

report_path = generator.generate_report(yesterday, 'html')
print(f"\nReport generated: {report_path}")
print(f"Open it in a browser to see the new design!")

db.close()
