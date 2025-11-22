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
        
        self.data_file = "study_data.json"
        self.load_data()
        
    def update(self, is_studying):
        if is_studying:
            self.total_study_seconds += 1
            self.xp += 1  # 1 XP per second of study
            
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
            "total_study_seconds": self.total_study_seconds
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
            except Exception as e:
                print(f"Error loading data: {e}")
