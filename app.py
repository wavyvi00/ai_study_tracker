from flask import Flask, render_template, jsonify, request
from tracker import WindowTracker
from gamification import GamificationEngine
from courses import CourseManager
from session_history import SessionHistory
import threading
import time
import os
import logging

# Disable Flask request logging for cleaner console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Initialize Core Logic
tracker = WindowTracker()
game_engine = GamificationEngine()
course_manager = CourseManager()
session_history = SessionHistory()

# Global State
current_state = {
    "app_name": "Initializing...",
    "window_title": "...",
    "is_studying": False,
    "xp": 0,
    "level": 1,
    "health": 100,
    "time_formatted": "00:00:00",
    "session_time_formatted": "00:00:00",
    "has_permissions": True,
    # Session state
    "session_active": False,
    "session_mode": None,
    "challenge_duration": 0,
    "time_remaining": 0,
    "session_elapsed": 0,
    "current_course": None,
    "courses": [],
    "total_sessions": 0
}

def update_loop():
    """Background thread to update game state every second"""
    while True:
        try:
            # Only track window activity if session is active
            if game_engine.session_active:
                # 1. Get Active Window
                app_name, window_title, has_permissions = tracker.get_active_window()
                
                # 2. Check if Studying
                is_studying = tracker.is_study_app(app_name, window_title)
                
                # 3. Update gamification
                game_engine.update(is_studying)
                
                # 4. Check if health depleted (auto-fail session)
                if game_engine.is_health_depleted():
                    print("Health depleted! Session failed.")
                    game_engine.stop_session()
                
                # 5. Check if challenge mode session is complete
                if game_engine.is_session_complete():
                    print("Challenge mode session complete! Auto-stopping.")
                    game_engine.stop_session()
                
                # 6. Update Global State
                current_state["app_name"] = app_name
                current_state["window_title"] = window_title
                current_state["is_studying"] = is_studying
                current_state["has_permissions"] = has_permissions
            else:
                # No active session - set default values
                current_state["app_name"] = "No active session"
                current_state["window_title"] = ""
                current_state["is_studying"] = False
                current_state["has_permissions"] = True
            
            # Always update these regardless of session state
            current_state["xp"] = game_engine.xp
            current_state["level"] = game_engine.level
            current_state["health"] = game_engine.health
            current_state["time_formatted"] = game_engine.get_formatted_time()
            current_state["session_time_formatted"] = game_engine.get_session_formatted_time()
            
            # Session state
            current_state["session_active"] = game_engine.session_active
            current_state["session_mode"] = game_engine.session_mode
            current_state["challenge_duration"] = game_engine.challenge_duration
            current_state["time_remaining"] = game_engine.get_session_time_remaining()
            current_state["session_elapsed"] = game_engine.get_session_elapsed_time()
            current_state["current_course"] = game_engine.current_course
            current_state["courses"] = course_manager.get_courses()
            current_state["total_sessions"] = session_history.get_total_sessions()
            current_state["current_streak"] = game_engine.current_streak
            current_state["best_streak"] = game_engine.best_streak
            
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

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new study session"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        duration = data.get('duration')  # in seconds
        course = data.get('course', '').strip()
        
        if mode not in ['normal', 'challenge']:
            return jsonify({"error": "Invalid mode"}), 400
        
        if mode == 'challenge' and not duration:
            return jsonify({"error": "Duration required for challenge mode"}), 400
        
        # Add course if provided
        if course:
            course_manager.add_course(course)
        
        # Start session with correct parameter order: mode, course, duration
        game_engine.start_session(mode=mode, course=course, duration=duration)
        return jsonify({"success": True, "mode": mode, "duration": duration, "course": course})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current session"""
    try:
        # Get session data before stopping
        session_data = game_engine.stop_session()
        
        # Save to history if session data exists
        if session_data and session_data['course']:
            session_history.add_session(
                course=session_data['course'],
                mode=session_data['mode'],
                duration_seconds=session_data['duration_seconds'],
                xp_earned=session_data['xp_earned'],
                start_time=session_data['start_time'],
                end_time=session_data['end_time']
            )
        
        # Return session results for results screen
        return jsonify({
            "success": True,
            "results": session_data if session_data else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get session history"""
    try:
        sessions = session_history.get_recent_sessions(limit=20)
        total_sessions = session_history.get_total_sessions()
        return jsonify({
            "sessions": sessions,
            "total_sessions": total_sessions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
