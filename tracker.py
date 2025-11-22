import platform
import time

# Try to import Quartz for macOS window tracking
try:
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    from Cocoa import NSWorkspace
    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False

class WindowTracker:
    def __init__(self):
        self.study_keywords = ['code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', 'obsidian', 'cursor', 'xcode', 'intellij', 'pycharm']
        self.distraction_keywords = ['youtube', 'twitter', 'reddit', 'facebook', 'instagram', 'netflix', 'game']
        
    def get_active_window(self):
        """Returns (app_name, window_title, has_permissions)"""
        if not HAS_QUARTZ:
            return ("Mock App", "Mock Window - VS Code", False)
            
        try:
            # Method 1: NSWorkspace (Simpler, gets active app)
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()
            app_name = active_app.localizedName() if active_app else "Unknown"
            
            # IGNORE THE TRACKER APP ITSELF - look for the next window
            # If the tracker is the active app, find the next visible app
            if app_name and app_name.lower() in ["python", "antigravity", "ai study tracker"]:
                # Get all running apps and find the next one
                running_apps = workspace.runningApplications()
                for app in running_apps:
                    candidate_name = app.localizedName()
                    if candidate_name and candidate_name.lower() not in ["python", "antigravity", "ai study tracker", "finder"]:
                        app_name = candidate_name
                        break
            
            # Method 2: Quartz (More detailed, gets window title)
            # Note: This requires Screen Recording permissions on macOS
            options = kCGWindowListOptionOnScreenOnly
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            
            window_title = ""
            has_permissions = True
            
            found_window = False
            for window in window_list:
                owner_name = window.get('kCGWindowOwnerName', '')
                # Skip our own app windows
                if owner_name.lower() in ["python", "antigravity", "ai study tracker"]:
                    continue
                if owner_name == app_name:
                    window_title = window.get('kCGWindowName', '')
                    found_window = True
                    break
            
            # Fallback if app_name is unknown or empty (likely permission issue)
            if not app_name or app_name == "Unknown":
                print("DEBUG: Quartz returned empty app name. Using fallback.")
                return ("Mock App", "Mock Window - VS Code", False)
                    
            return (app_name, window_title, True)
            
        except Exception as e:
            print(f"Error tracking window: {e}")
            # Fallback on error
            return ("Mock App", "Mock Window - VS Code", False)

    def is_study_app(self, app_name, window_title):
        full_text = (app_name + " " + window_title).lower()
        
        print(f"DEBUG: Checking '{full_text}'")
        
        # Check distractions first
        for keyword in self.distraction_keywords:
            if keyword in full_text:
                print(f"DEBUG: DISTRACTION detected (keyword: '{keyword}')")
                return False
                
        # Check study keywords
        for keyword in self.study_keywords:
            if keyword in full_text:
                print(f"DEBUG: STUDY detected (keyword: '{keyword}')")
                return True
                
        # Default to neutral/study if not explicitly distracted? 
        # Or default to distraction? Let's default to distraction for strictness, 
        # or Study if it's a known tool.
        # For now, let's assume if it's not a distraction, it's study time 
        # (or maybe we need a whitelist).
        # Let's use a simple heuristic: if it's not a distraction, it's study.
        print(f"DEBUG: No match, defaulting to STUDY")
        return True
