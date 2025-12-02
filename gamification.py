import time
import json
import os
from datetime import datetime, timedelta

class GamificationEngine:
    def __init__(self):
        self.data_file = "study_data.json"
        self.data = {} # Initialize data dictionary
        self.load_data()
        
        # Core stats
        self.xp = self.data.get("xp", 0)
        self.level = self.data.get("level", 1)
        self.health = self.data.get("health", 100)
        self.total_study_seconds = self.data.get("total_study_seconds", 0)
        
        # Streak tracking
        self.current_streak = self.data.get("current_streak", 0)
        self.best_streak = self.data.get("best_streak", 0)
        self.last_study_date = self.data.get("last_study_date", None) # Stored as string, converted to datetime when used
        
        # Session state
        self.session_active = False
        self.session_mode = None  # "normal" or "challenge"
        self.challenge_duration = 0  # Duration in seconds for challenge mode
        self.session_start_time = None  # Timestamp when session started
        self.current_course = None  # Current course being studied
        
        # Session-specific tracking (resets each session)
        self.session_study_seconds = 0  # Time studied in current session
        self.session_xp_earned = 0  # XP earned in current session
        self.session_attention_scores = []  # Track attention scores for analytics
        self.session_paused = False  # Track if session is paused (user away)
        
        self.data_file = "study_data.json"
        self.load_data()
        
    def update(self, is_studying, attention_multiplier=1.0, user_present=True):
        """Update game state with attention-based XP
        
        Args:
            is_studying: Whether user is on a study app
            attention_multiplier: XP multiplier based on attention (0.5-1.0)
            user_present: Whether user is present at desk (for auto-pause)
        """
        # Only track if a session is active
        if not self.session_active:
            return
            
        print(f"DEBUG: Update - Focused: {is_studying}, Present: {user_present}, Health: {self.health}") # Debug log
        
        # If user is away, treat as not studying (distracted)
        # Treat None as True (assume present if camera disabled/initializing)
        if user_present is False:
            is_studying = False
            self.session_paused = False # Ensure not paused
        else:
            self.session_paused = False
            
        if is_studying:
            self.total_study_seconds += 1
            self.session_study_seconds += 1  # Track session time
            
            # Track XP with attention multiplier (but DON'T add to total yet)
            xp_this_second = 1.0 * attention_multiplier
            self.session_xp_earned += xp_this_second
            
            # Track attention score for analytics
            # Convert multiplier back to score (approximate)
            attention_score = self._multiplier_to_score(attention_multiplier)
            self.session_attention_scores.append(attention_score)
            
            # Regenerate health slowly if studying
            if self.health < 100:
                self.health = min(100, self.health + 0.1)
                
        else:
            # Not studying (Distracted)
            self.decrease_health(5.0) # Lose 5 health per second (increased for testing)
            
        self.save_data()
        
    def _multiplier_to_score(self, multiplier: float) -> float:
        """Convert attention multiplier back to approximate score for analytics"""
        if multiplier >= 1.0:
            return 90.0
        elif multiplier >= 0.85:
            return 70.0
        elif multiplier >= 0.7:
            return 50.0
        elif multiplier >= 0.6:
            return 30.0
        else:
            return 10.0
    
    def decrease_health(self, amount):
        old_health = self.health
        self.health = float(self.health) - amount
        if self.health <= 0:
            self.health = 0
            print(f"DEBUG: Health depleted! {old_health} -> {self.health}")
            return True  # Health depleted
            
        print(f"DEBUG: Decreasing health: {old_health} -> {self.health} (Amount: {amount})")
        return False
    
    def is_health_depleted(self):
        """Check if health has reached 0"""
        return self.health <= 0
    
    def check_and_update_streak(self):
        """Check and update daily streak"""
        today = datetime.now().date().isoformat()
        
        if self.last_study_date is None:
            # First ever session
            self.current_streak = 1
            self.last_study_date = today
        elif self.last_study_date == today:
            # Already studied today, streak unchanged
            pass
        else:
            # Check if it's the next day
            last_date = datetime.fromisoformat(self.last_study_date).date()
            today_date = datetime.now().date()
            days_diff = (today_date - last_date).days
            
            if days_diff == 1:
                # Consecutive day! Increment streak
                self.current_streak += 1
                self.last_study_date = today
            else:
                # Missed a day, reset streak
                self.current_streak = 1
                self.last_study_date = today
        
        # Update best streak
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
        
        self.save_data()
        return self.current_streak
    
    def start_session(self, mode="normal", course=None, duration=0):
        """Start a new study session"""
        import time as time_module
        start_time = time_module.time()
        
        # Check and update streak
        streak_before = self.current_streak
        current_streak = self.check_and_update_streak()
        streak_increased = current_streak > streak_before
        print(f"⏱️ Streak check took: {(time_module.time() - start_time)*1000:.2f}ms")
        
        # Reset health to 100 for new session
        self.health = 100
        
        self.session_active = True
        self.session_mode = mode
        self.session_start_time = time.time()
        self.challenge_duration = duration
        self.current_course = course
        
        # Reset session-specific counters
        self.session_study_seconds = 0
        self.session_xp_earned = 0
        self.session_attention_scores = []
        self.session_paused = False
        
        save_start = time_module.time()
        self.save_data()
        print(f"⏱️ Save data took: {(time_module.time() - save_start)*1000:.2f}ms")
        print(f"⏱️ Total start_session took: {(time_module.time() - start_time)*1000:.2f}ms")
        
        return {
            "streak": current_streak,
            "streak_increased": streak_increased
        }
    
    def stop_session(self):
        """Stop the current session and return session data for history"""
        if not self.session_active:
            return None
        
        # Check if health depleted (failed session)
        health_failed = self.health <= 0
        
        # Check if challenge mode was completed
        challenge_failed = False
        if self.session_mode == "challenge":
            # Check if challenge was completed (time ran out naturally)
            elapsed_time = self.session_study_seconds
            if elapsed_time < self.challenge_duration:
                challenge_failed = True
        
        # Capture stats BEFORE awarding XP
        old_level = self.level
        old_xp = self.xp
        
        # Only award XP if challenge wasn't failed AND health not depleted
        if not challenge_failed and not health_failed:
            # Calculate streak bonus (10% bonus per streak day)
            base_xp = self.session_xp_earned
            streak_bonus = int(base_xp * (self.current_streak * 0.10))
            total_xp = base_xp + streak_bonus
            
            # Award XP earned during session + streak bonus
            self.xp += total_xp
            
            # Calculate level-ups
            levels_gained = 0
            while self.xp >= self.level * 100:
                self.level += 1
                levels_gained += 1
        else:
            # Challenge or health failed - no XP awarded
            levels_gained = 0
            base_xp = 0
            streak_bonus = 0
            total_xp = 0
        
        new_level = self.level
        new_xp = self.xp
        
        # Calculate average attention score
        avg_attention = sum(self.session_attention_scores) / len(self.session_attention_scores) if self.session_attention_scores else 0.0
        
        # Prepare session data for history and results
        session_data = {
            "course": self.current_course,
            "mode": self.session_mode,
            "duration_seconds": self.session_study_seconds,
            "xp_earned": 0 if (challenge_failed or health_failed) else total_xp,
            "base_xp": 0 if (challenge_failed or health_failed) else base_xp,
            "streak_bonus": 0 if (challenge_failed or health_failed) else streak_bonus,
            "start_time": self.session_start_time,
            "end_time": time.time(),
            # Results screen data
            "old_level": old_level,
            "new_level": new_level,
            "old_xp": old_xp,
            "new_xp": new_xp,
            "levels_gained": levels_gained,
            "challenge_failed": challenge_failed,
            "health_failed": health_failed,
            "challenge_duration": self.challenge_duration if self.session_mode == "challenge" else 0,
            # Streak data
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            # Camera analytics
            "average_attention_score": round(avg_attention, 2)
        }
        
        # Reset session state
        self.session_active = False
        self.session_mode = None
        self.session_start_time = None
        self.challenge_duration = 0
        self.current_course = None
        self.session_study_seconds = 0
        self.session_xp_earned = 0
        self.session_attention_scores = []
        self.session_paused = False
        
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
        """Save current state to JSON file"""
        data = {
            "xp": self.xp,
            "level": self.level,
            "health": self.health,
            "total_study_seconds": self.total_study_seconds,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "last_study_date": self.last_study_date,
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
