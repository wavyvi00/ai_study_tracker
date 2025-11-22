import time
import json
import os

class GamificationEngine:
    def __init__(self):
        self.xp = 0
        self.level = 1
        self.health = 100  # New: Health attribute
        self.total_study_seconds = 0
        self.streak = 0
        self.last_study_date = None
        
        # Session management
        self.session_active = False
        self.session_mode = None  # "normal" or "challenge"
        self.challenge_duration = 0  # Duration in seconds for challenge mode
        self.session_start_time = None  # Timestamp when session started
        self.current_course = None  # Current course being studied
        
        # Session-specific tracking (resets each session)
        self.session_study_seconds = 0  # Time studied in current session
        self.session_xp_earned = 0  # XP earned in current session
        
        self.data_file = "study_data.json"
        self.load_data()
        
    def update(self, is_studying):
        # Only track if a session is active
        if not self.session_active:
            return
            
        if is_studying:
            self.total_study_seconds += 1
            self.session_study_seconds += 1  # Track session time
            
            self.xp += 1  # 1 XP per second of study
            self.session_xp_earned += 1  # Track session XP
            
            # Level up logic (simple: 100 XP per level)
            if self.xp >= self.level * 100:
                self.level += 1
                # self.xp = 0 # Keep accumulating XP
                
            # Regenerate health slowly if studying?
            if self.health < 100:
                self.health = min(100, self.health + 0.1)
                
        else:
            # Not studying (Distracted)
            self.decrease_health(0.5) # Lose 0.5 health per second
            
        self.save_data()
        
    def decrease_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            # Game Over logic could go here
    
    def start_session(self, mode, duration=None, course=None):
        """Start a new study session
        
        Args:
            mode: "normal" or "challenge"
            duration: Duration in seconds (required for challenge mode)
            course: Name of the course being studied
        """
        self.session_active = True
        self.session_mode = mode
        self.session_start_time = time.time()
        self.current_course = course
        
        # Reset session-specific counters
        self.session_study_seconds = 0
        self.session_xp_earned = 0
        
        if mode == "challenge":
            if duration is None:
                raise ValueError("Duration required for challenge mode")
            self.challenge_duration = duration
        else:
            self.challenge_duration = 0
            
        self.save_data()
    
    def stop_session(self):
        """Stop the current session and return session data for history"""
        if not self.session_active:
            return None
        
        # Prepare session data for history
        session_data = {
            "course": self.current_course,
            "mode": self.session_mode,
            "duration_seconds": self.session_study_seconds,
            "xp_earned": self.session_xp_earned,
            "start_time": self.session_start_time,
            "end_time": time.time()
        }
        
        # Reset session state
        self.session_active = False
        self.session_mode = None
        self.session_start_time = None
        self.challenge_duration = 0
        self.current_course = None
        self.session_study_seconds = 0
        self.session_xp_earned = 0
        
        self.save_data()
        
        return session_data
    
    def get_session_time_remaining(self):
        """Get remaining time for challenge mode in seconds"""
        if not self.session_active or self.session_mode != "challenge":
            return 0
        
        elapsed = time.time() - self.session_start_time
        remaining = self.challenge_duration - elapsed
        return max(0, int(remaining))
    
    def get_session_elapsed_time(self):
        """Get elapsed time in current session"""
        if not self.session_active or self.session_start_time is None:
            return 0
        return int(time.time() - self.session_start_time)
    
    def is_session_complete(self):
        """Check if challenge mode session is complete"""
        if not self.session_active or self.session_mode != "challenge":
            return False
        
        return self.get_session_time_remaining() <= 0
    
    def get_session_formatted_time(self):
        """Get formatted time for current session only"""
        hours = self.session_study_seconds // 3600
        minutes = (self.session_study_seconds % 3600) // 60
        seconds = self.session_study_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
            
    def get_formatted_time(self):
        hours = self.total_study_seconds // 3600
        minutes = (self.total_study_seconds % 3600) // 60
        seconds = self.total_study_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
        
    def save_data(self):
        data = {
            "xp": self.xp,
            "level": self.level,
            "health": self.health,
            "total_study_seconds": self.total_study_seconds,
            # Session state (will be reset on load)
            "session_active": self.session_active,
            "session_mode": self.session_mode,
            "challenge_duration": self.challenge_duration,
            "session_start_time": self.session_start_time
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
            
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.health = data.get("health", 100)
                    self.total_study_seconds = data.get("total_study_seconds", 0)
                    # Always reset session state on load (don't persist sessions)
                    self.session_active = False
                    self.session_mode = None
                    self.challenge_duration = 0
                    self.session_start_time = None
            except Exception as e:
                print(f"Error loading data: {e}")
