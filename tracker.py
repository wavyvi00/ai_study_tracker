import platform
import time

# Platform-specific imports
if platform.system() == "Darwin":  # macOS
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        from Cocoa import NSWorkspace
        HAS_MACOS_APIS = True
    except ImportError:
        HAS_MACOS_APIS = False
        print("⚠️ macOS APIs not available")
elif platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        import psutil
        HAS_WINDOWS_APIS = True
    except ImportError:
        HAS_WINDOWS_APIS = False
        print("⚠️ Windows APIs not available - install pywin32 and psutil")
else:
    HAS_MACOS_APIS = False
    HAS_WINDOWS_APIS = False

class WindowTracker:
    def __init__(self):
        self.platform = platform.system()
        self.study_keywords = ['code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', 'obsidian', 'cursor', 'xcode', 'intellij', 'pycharm']
        self.distraction_keywords = ['youtube', 'twitter', 'reddit', 'facebook', 'instagram', 'netflix', 'game']
        
    def get_active_window(self):
        """Returns (app_name, window_title, has_permissions)"""
        if self.platform == "Darwin":
            return self._get_active_window_macos()
        elif self.platform == "Windows":
            return self._get_active_window_windows()
        else:
            return ("Unknown", "Unsupported OS", False)
    
    def _get_active_window_macos(self):
        """Get active window on macOS"""
        if not HAS_MACOS_APIS:
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
                return ("Mock App", "Mock Window - VS Code", False)
                    
            return (app_name, window_title, True)
            
        except Exception as e:
            print(f"Error tracking window: {e}")
            # Fallback on error
            return ("Mock App", "Mock Window - VS Code", False)

    def is_study_app(self, app_name, window_title):
        """Check if the current app/window is study-related"""
        combined = f"{app_name} {window_title}".lower()
        
        # Check for study keywords
        for keyword in self.study_keywords:
            if keyword in combined:
                return True
        
        # Check for distraction keywords
        for keyword in self.distraction_keywords:
            if keyword in combined:
                return False
        
        # Default to studying if no match
        return True

    def _get_active_window_windows(self):
        """Get active window on Windows"""
        if not HAS_WINDOWS_APIS:
            return ("Mock App", "Mock Window - VS Code", False)
        
        try:
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                app_name = process.name().replace('.exe', '')
            except:
                app_name = "Unknown"
            
            # Skip our own app
            if app_name.lower() in ["python", "pythonw", "focuswin"]:
                return self._get_next_window_windows(hwnd)
            
            return (app_name, window_title, True)
            
        except Exception as e:
            print(f"Error tracking window: {e}")
            return ("Mock App", "Mock Window - VS Code", False)
    
    def _get_next_window_windows(self, current_hwnd):
        """Get next visible window on Windows"""
        try:
            # Enumerate windows to find next one
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and hwnd != current_hwnd:
                    windows.append(hwnd)
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                hwnd = windows[0]
                window_title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    app_name = process.name().replace('.exe', '')
                    return (app_name, window_title, True)
                except:
                    pass
        except:
            pass
        
        return ("Unknown", "", False)
