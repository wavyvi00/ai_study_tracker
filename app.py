from flask import Flask, render_template, jsonify
from tracker import WindowTracker
from gamification import GamificationEngine
import threading
import time
import os

app = Flask(__name__)

# Initialize Core Logic
tracker = WindowTracker()
game_engine = GamificationEngine()

# Global State
current_state = {
    "app_name": "Initializing...",
    "window_title": "...",
    "is_studying": False,
    "xp": 0,
    "level": 1,
    "health": 100,
    "time_formatted": "00:00:00",
    "has_permissions": True
}

def update_loop():
    """Background thread to update game state every second"""
    while True:
        try:
            # 1. Get Active Window
            app_name, window_title, has_permissions = tracker.get_active_window()
            
            # 2. Check if Studying
            is_studying = tracker.is_study_app(app_name, window_title)
            
            # 3. Update Game Engine
            game_engine.update(is_studying)
            
            # 4. Update Global State
            current_state["app_name"] = app_name
            current_state["window_title"] = window_title
            current_state["is_studying"] = is_studying
            current_state["xp"] = game_engine.xp
            current_state["level"] = game_engine.level
            current_state["health"] = game_engine.health
            current_state["time_formatted"] = game_engine.get_formatted_time()
            current_state["has_permissions"] = has_permissions
            
        except Exception as e:
            print(f"Error in update loop: {e}")
            
        time.sleep(1)

# Start background thread
update_thread = threading.Thread(target=update_loop, daemon=True)
update_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify(current_state)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
