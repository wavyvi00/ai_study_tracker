import platform
import subprocess
import time

class WindowProvider:
    """Abstract base class for window providers"""
    def get_active_window(self):
        """Returns (app_name, window_title, has_permissions)"""
        raise NotImplementedError

class MacOSWindowProvider(WindowProvider):
    """macOS implementation using AppleScript/Quartz"""
    def __init__(self):
        self.has_permissions = False
        self.check_permissions()

    def check_permissions(self):
        try:
            # Try to get window title - this requires Accessibility permissions
            script = 'tell application "System Events" to get name of window 1 of (first application process whose frontmost is true)'
            subprocess.check_output(['osascript', '-e', script], stderr=subprocess.PIPE)
            self.has_permissions = True
            return True
        except subprocess.CalledProcessError:
            self.has_permissions = False
            return False
        except Exception:
            return False

    def get_active_window(self):
        try:
            # Get App Name
            script_app = 'tell application "System Events" to get name of (first application process whose frontmost is true)'
            app_name = subprocess.check_output(['osascript', '-e', script_app], stderr=subprocess.PIPE).decode('utf-8').strip()
            
            # Get Window Title
            script_title = 'tell application "System Events" to get name of window 1 of (first application process whose frontmost is true)'
            window_title = subprocess.check_output(['osascript', '-e', script_title], stderr=subprocess.PIPE).decode('utf-8').strip()
            
            # Filter out our own app wrapper
            if app_name in ["Python", "antigravity", "AI Study Tracker", "StudyWin", "FocusWin"]:
                return ("FocusWin", "FocusWin", True)

            return (app_name, window_title, True)
            
        except subprocess.CalledProcessError:
            # Likely permission error or no window active
            return ("Unknown", "Unknown", False)
        except Exception as e:
            print(f"Error getting window: {e}")
            return ("Unknown", "Error", False)

class WindowsWindowProvider(WindowProvider):
    """Windows implementation (Placeholder for future)"""
    def get_active_window(self):
        return ("Windows Support", "Coming Soon", True)

def get_window_provider():
    """Factory function to get the correct provider for the current OS"""
    system = platform.system()
    if system == "Darwin":
        return MacOSWindowProvider()
    elif system == "Windows":
        return WindowsWindowProvider()
    else:
        raise NotImplementedError(f"OS {system} not supported")
