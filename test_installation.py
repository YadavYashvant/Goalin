#!/usr/bin/env python3
"""
Simple test script to verify Goalin installation and basic functionality
"""

import sys
import os


def check_imports():
    """Check if all required imports are available"""
    print("Checking imports...")
    
    try:
        import goalin
        print("✓ goalin package found")
        print(f"  Version: {goalin.__version__}")
    except ImportError as e:
        print(f"✗ goalin package not found: {e}")
        return False
    
    try:
        from goalin.config import ensure_directories
        print("✓ goalin.config imported")
    except ImportError as e:
        print(f"✗ Failed to import goalin.config: {e}")
        return False
    
    try:
        from goalin.database import ActivityDatabase
        print("✓ goalin.database imported")
    except ImportError as e:
        print(f"✗ Failed to import goalin.database: {e}")
        return False
    
    try:
        from goalin.tracker import ActivityTracker
        print("✓ goalin.tracker imported")
    except ImportError as e:
        print(f"✗ Failed to import goalin.tracker: {e}")
        return False
    
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_version('Adw', '1')
        from gi.repository import Gtk, Adw
        print("✓ GTK4 and libadwaita available")
    except (ImportError, ValueError) as e:
        print(f"⚠ GTK4/libadwaita not available: {e}")
        print("  GUI will not work, but daemon should be fine")
    
    return True


def check_directories():
    """Check if directories are created properly"""
    print("\nChecking directories...")
    
    from goalin.config import CONFIG_DIR, DATA_DIR, CACHE_DIR, REPORT_DIR, ensure_directories
    
    ensure_directories()
    
    dirs = [
        ("Config", CONFIG_DIR),
        ("Data", DATA_DIR),
        ("Cache", CACHE_DIR),
        ("Reports", REPORT_DIR),
    ]
    
    all_ok = True
    for name, path in dirs:
        if path.exists():
            print(f"✓ {name} directory exists: {path}")
        else:
            print(f"✗ {name} directory missing: {path}")
            all_ok = False
    
    return all_ok


def check_database():
    """Test database creation and basic operations"""
    print("\nTesting database...")
    
    try:
        from goalin.database import ActivityDatabase
        
        db = ActivityDatabase()
        print("✓ Database initialized")
        
        # Test logging activity
        db.log_activity(
            window_title="Test Window",
            application="TestApp",
            category="Testing",
            duration=5,
            is_idle=False
        )
        print("✓ Activity logged successfully")
        
        # Test getting summary
        summary = db.get_today_summary()
        print("✓ Summary retrieved successfully")
        print(f"  Total active time: {summary['total_active_time']}s")
        
        db.close()
        print("✓ Database closed")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_tracker():
    """Test activity tracker"""
    print("\nTesting activity tracker...")
    
    try:
        from goalin.tracker import ActivityTracker
        
        tracker = ActivityTracker()
        print(f"✓ Tracker initialized (Display server: {tracker.display_server})")
        
        # Test getting active window
        title, app = tracker.get_active_window()
        if title or app:
            print(f"✓ Active window detected: {app} - {title}")
        else:
            print("⚠ Could not detect active window (may be normal on some systems)")
        
        # Test idle detection
        idle_time = tracker.get_idle_time()
        print(f"✓ Idle time detection working: {idle_time}s")
        
        return True
    except Exception as e:
        print(f"✗ Tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_report():
    """Test report generation"""
    print("\nTesting report generation...")
    
    try:
        from goalin.database import ActivityDatabase
        from goalin.report import ReportGenerator
        from datetime import datetime, timedelta
        
        db = ActivityDatabase()
        generator = ReportGenerator(db)
        
        # Generate a test report for yesterday
        yesterday = (datetime.now() - timedelta(days=1)).date()
        report_path = generator.generate_report(yesterday, format='text')
        
        print(f"✓ Report generated: {report_path}")
        
        if report_path.exists():
            print("✓ Report file exists")
            size = report_path.stat().st_size
            print(f"  File size: {size} bytes")
        else:
            print("⚠ Report file not found")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Report test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Goalin Installation Test")
    print("=" * 60)
    
    tests = [
        ("Import Check", check_imports),
        ("Directory Check", check_directories),
        ("Database Test", check_database),
        ("Tracker Test", check_tracker),
        ("Report Test", check_report),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Goalin is ready to use.")
        print("\nNext steps:")
        print("  1. Start the daemon: systemctl --user start goalin.service")
        print("  2. Enable on boot: systemctl --user enable goalin.service")
        print("  3. Launch GUI: goalin-gui")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
