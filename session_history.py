import json
import os
from datetime import datetime

class SessionHistory:
    def __init__(self):
        self.history_file = "session_history.json"
        self.sessions = self.load_history()
    
    def load_history(self):
        """Load session history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return data.get("sessions", [])
            except Exception as e:
                print(f"Error loading session history: {e}")
                return []
        return []
    
    def save_history(self):
        """Save session history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({"sessions": self.sessions}, f, indent=2)
        except Exception as e:
            print(f"Error saving session history: {e}")
    
    def add_session(self, course, mode, duration_seconds, xp_earned, start_time, end_time):
        """Add a completed session to history"""
        session = {
            "course": course,
            "mode": mode,
            "duration_seconds": duration_seconds,
            "xp_earned": xp_earned,
            "start_time": start_time,
            "end_time": end_time,
            "date": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
        }
        self.sessions.append(session)
        self.save_history()
        print(f"Session saved: {course} - {duration_seconds}s")
    
    def get_recent_sessions(self, limit=10):
        """Get most recent sessions"""
        return self.sessions[-limit:] if len(self.sessions) > limit else self.sessions
    
    def get_total_sessions(self):
        """Get total number of sessions"""
        return len(self.sessions)
