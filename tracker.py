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
            app_name = self._get_active_app_name_macos()
            window_title = self._get_active_window_title_macos()
            
            if not app_name or app_name == "Unknown":
                return ("Mock App", "Mock Window - VS Code", False)
                    
            return (app_name, window_title, True)
            
        except Exception as e:
            print(f"Error tracking window: {e}")
            # Fallback on error
            return ("Mock App", "Mock Window - VS Code", False)

    def _get_active_window_title_macos(self):
        """Get the title of the active window on macOS"""
        try:
            # Use AppleScript to get the window title of the frontmost app
            script = 'tell application "System Events" to get name of window 1 of (first application process whose frontmost is true)'
            result = subprocess.check_output(['osascript', '-e', script], stderr=subprocess.DEVNULL).decode('utf-8').strip()
            return result
        except:
            return None

    def _get_active_app_name_macos(self):
        """Get the name of the active application on macOS"""
        try:
            # Use AppleScript to get the name of the frontmost app
            # This is more reliable than NSWorkspace for some things
            script = 'tell application "System Events" to get name of (first application process whose frontmost is true)'
            result = subprocess.check_output(['osascript', '-e', script], stderr=subprocess.DEVNULL).decode('utf-8').strip()
            
            # Filter out our own app wrapper
            if result in ["Python", "antigravity", "AI Study Tracker", "StudyWin"]:
                # Try to get the window title to see if it's more descriptive
                win_title = self._get_active_window_title_macos()
                if win_title:
                    return win_title
            
            return result
        except:
            return None

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
