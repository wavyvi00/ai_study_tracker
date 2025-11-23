import subprocess
import threading
import time
import random

class VoiceAssistant:
    def __init__(self):
        self.last_speech_time = 0
        self.distracted_start_time = None
        self.focused_start_time = None
        self.cooldown = 60  # Minimum seconds between messages
        
        # Messages
        self.distracted_messages = [
            "Please put the phone away.",
            "Focus, you can do this.",
            "Get back to work.",
            "Distraction detected.",
            "Stay focused on your goal."
        ]
        
        self.focused_messages = [
            "You are doing great!",
            "Excellent focus, keep it up.",
            "You're on fire!",
            "Great work session.",
            "Proud of your focus."
        ]

    def speak(self, text):
        """Speak text using macOS 'say' command in background"""
        def _speak():
            try:
                print(f"🗣️ DEBUG: Attempting to say '{text}'")
                # Use Popen for truly non-blocking execution
                # -v Alex forces the default voice, usually reliable
                subprocess.Popen(['say', '-v', 'Alex', text])
                print(f"✅ Voice command sent to background")
            except Exception as e:
                print(f"❌ Voice exception: {e}")
        
        # No need for thread if using Popen, but keeping it safe
        _speak()

    def check_status(self, is_distracted, is_studying):
        """Check status and trigger voice feedback if needed"""
        current_time = time.time()
        
        # Don't speak if in cooldown
        if current_time - self.last_speech_time < self.cooldown:
            return

        # Distraction Logic
        if is_distracted:
            if self.distracted_start_time is None:
                self.distracted_start_time = current_time
            
            # If distracted for > 5 seconds (lowered for testing)
            elif current_time - self.distracted_start_time > 5:
                print(f"🗣️ Speaking: Distracted message")
                self.speak(random.choice(self.distracted_messages))
                self.last_speech_time = current_time
                self.distracted_start_time = None  # Reset to avoid spam
                self.focused_start_time = None
        else:
            self.distracted_start_time = None
            
            # Focus Logic (only if actually studying)
            if is_studying:
                if self.focused_start_time is None:
                    self.focused_start_time = current_time
                
                # If focused for > 15 minutes (900s) - simplified to 5 mins (300s) for testing
                elif current_time - self.focused_start_time > 300:
                    # 20% chance to speak to not be annoying
                    if random.random() < 0.2:
                        self.speak(random.choice(self.focused_messages))
                        self.last_speech_time = current_time
                        self.focused_start_time = current_time # Reset timer
