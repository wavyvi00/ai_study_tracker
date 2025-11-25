#!/usr/bin/env python3
"""
Quick test script to demonstrate the permission checking feature
"""

from tracker import WindowTracker

print("Testing Accessibility Permission Check...\n")

tracker = WindowTracker()
has_permission, error_type = tracker.check_accessibility_permissions()

if has_permission:
    print("✅ SUCCESS: Accessibility permissions are granted!")
    print("\nTesting window detection:")
    app_name, window_title, has_perms = tracker.get_active_window()
    print(f"  • App Name: {app_name}")
    print(f"  • Window Title: {window_title}")
    print(f"  • Has Permissions: {has_perms}")
    
    # Test distraction detection
    is_studying = tracker.is_study_app(app_name, window_title)
    print(f"\n  • Is Focused: {is_studying}")
    
else:
    print("❌ FAILED: Accessibility permissions are missing!")
    print(f"   Error Type: {error_type}")
    print("\nWould you like to grant permissions?")
    tracker.prompt_for_accessibility_permissions()
