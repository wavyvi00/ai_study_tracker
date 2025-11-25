import platform
import subprocess
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
        self.study_keywords = ['code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', 'obsidian', 'cursor', 'xcode', 'intellij', 'pycharm', 'safari', 'calendar']
        self.distraction_keywords = ['youtube', 'twitter', 'reddit', 'facebook', 'instagram', 'netflix', 'game']
        
        # Educational keywords that can override distractions (e.g., educational YouTube videos)
        self.educational_keywords = [
            # Academic subjects
            'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics',
            'physics', 'chemistry', 'biology', 'science',
            'history', 'geography', 'economics', 'psychology',
            # Programming & Tech
            'programming', 'coding', 'python', 'javascript', 'java', 'c++',
            'tutorial', 'course', 'lesson', 'lecture', 'learn', 'learning',
            'education', 'educational', 'study', 'studying',
            # Educational platforms
            'khan academy', 'coursera', 'udemy', 'edx', 'mit opencourseware',
            '3blue1brown', 'crash course', 'ted-ed', 'veritasium',
            # General learning
            'how to', 'guide', 'explained', 'introduction to', 'basics of',
            'workshop', 'seminar', 'training', 'certification'
        ]
        self.accessibility_permission_checked = False
        self.has_accessibility_permission = False
    
    def check_accessibility_permissions(self):
        """
        Check if Accessibility permissions are granted.
        Returns (has_permission, error_message)
        """
        if self.platform != "Darwin":
            return (True, None)  # Only needed on macOS
        
        try:
            # Try to get window title - this requires Accessibility permissions
            script = 'tell application "System Events" to get name of window 1 of (first application process whose frontmost is true)'
            subprocess.check_output(['osascript', '-e', script], stderr=subprocess.PIPE)
            self.has_accessibility_permission = True
            return (True, None)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            if 'not allowed assistive access' in error_msg:
                self.has_accessibility_permission = False
                return (False, "accessibility")
            return (True, None)  # Other errors don't indicate permission issues
        except Exception:
            return (True, None)  # Assume permission is granted if we can't check
    
    def prompt_for_accessibility_permissions(self):
        """
        Display a message prompting the user to grant Accessibility permissions
        and optionally open System Settings.
        """
        print("\n" + "="*70)
        print("⚠️  ACCESSIBILITY PERMISSIONS REQUIRED")
        print("="*70)
        print("\nThe AI Study Tracker needs Accessibility permissions to detect")
        print("which apps and websites you're using (e.g., YouTube, Instagram).")
        print("\n📋 HOW TO GRANT PERMISSIONS:")
        print("   1. Open System Settings → Privacy & Security → Accessibility")
        print("   2. Click the '+' button")
        print("   3. Add 'Terminal' (or your Python app)")
        print("   4. Restart this application")
        print("\n💡 TIP: I can open System Settings for you!")
        print("="*70)
        
        try:
            response = input("\nOpen System Settings now? (y/n): ").strip().lower()
            if response == 'y':
                # Open System Settings to Privacy & Security
                subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
                print("\n✅ Opening System Settings...")
                print("   After granting permissions, please restart this app.\n")
                return True
        except KeyboardInterrupt:
            print("\n")
        except Exception as e:
            print(f"\n⚠️  Could not open System Settings: {e}")
        
        return False
        
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
            result = subprocess.check_output(['osascript', '-e', script], stderr=subprocess.PIPE).decode('utf-8').strip()
            return result
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            if 'not allowed assistive access' in error_msg:
                print("⚠️  PERMISSION ERROR: Terminal/Python needs Accessibility permissions!")
                print("   Go to: System Settings → Privacy & Security → Accessibility")
                print("   Add Terminal (or your Python app) to the allowed list.")
            else:
                print(f"Error getting window title: {error_msg}")
            return None
        except Exception as e:
            print(f"Unexpected error getting window title: {e}")
            return None

    def _get_active_app_name_macos(self):
        """Get the name of the active application on macOS"""
        try:
            # Use AppleScript to get the name of the frontmost app
            # This is more reliable than NSWorkspace for some things
            script = 'tell application "System Events" to get name of (first application process whose frontmost is true)'
            result = subprocess.check_output(['osascript', '-e', script], stderr=subprocess.PIPE).decode('utf-8').strip()
            
            # Filter out our own app wrapper
            if result in ["Python", "antigravity", "AI Study Tracker", "StudyWin", "FocusWin"]:
                # Try to get the window title to see if it's more descriptive
                win_title = self._get_active_window_title_macos()
                if win_title:
                    return win_title
            
            return result
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            if 'not allowed assistive access' in error_msg:
                print("⚠️  PERMISSION ERROR: Terminal/Python needs Accessibility permissions!")
                print("   Go to: System Settings → Privacy & Security → Accessibility")
                print("   Add Terminal (or your Python app) to the allowed list.")
            else:
                print(f"Error getting app name: {error_msg}")
            return None
        except Exception as e:
            print(f"Unexpected error getting app name: {e}")
            return None

    def is_study_app(self, app_name, window_title):
        """Check if the current app/window is study-related with smart educational detection"""
        combined = f"{app_name} {window_title}".lower()
        app_name_lower = app_name.lower()
        window_title_lower = window_title.lower() if window_title else ""
        
        # Filter out our own app windows (HUD, main app, etc.)
        # Only check the app name, not the window title
        # Return None to indicate "ignore this window completely"
        if app_name_lower in ['focuswin', 'studywin']:
            print(f"DEBUG: Ignoring own app window: {app_name}")
            return None  # None = ignore, don't update health
        
        # Check for distraction keywords
        distraction_detected = False
        matched_distraction = None
        for keyword in self.distraction_keywords:
            if keyword in combined:
                distraction_detected = True
                matched_distraction = keyword
                break
        
        # If distraction detected, check if it's educational content
        if distraction_detected:
            # Check window title for educational keywords
            for edu_keyword in self.educational_keywords:
                if edu_keyword in window_title_lower:
                    print(f"DEBUG: Educational content detected on {matched_distraction}: '{edu_keyword}' in title")
                    return True  # Override distraction - it's educational!
            
            # No educational keywords found - it's a real distraction
            print(f"DEBUG: Distraction detected: {matched_distraction} in {combined}")
            return False
        
        # Check for study keywords
        for keyword in self.study_keywords:
            if keyword in combined:
                print(f"DEBUG: Study keyword matched: {keyword} in {combined}")
                return True
                
        # Default to False if no keywords matched (strict mode)
        # This prevents random apps from being counted as studying
        print(f"DEBUG: No keywords matched, defaulting to False (distraction) for: {combined}")
        return False

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
