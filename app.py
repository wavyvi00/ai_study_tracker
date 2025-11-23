from flask import Flask, render_template, jsonify, request, Response
from tracker import WindowTracker
from gamification import GamificationEngine
from courses import CourseManager
from session_history import SessionHistory
from camera_detector import CameraDetector
from camera_integration import (
    calculate_attention_multiplier,
    PostureMonitor,
    BreakReminder,
    CameraAnalytics
)
from voice_assistant import VoiceAssistant
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
camera_detector = CameraDetector()
voice_assistant = VoiceAssistant()

# Initialize camera integration components
posture_monitor = PostureMonitor(warning_interval_minutes=10)
break_reminder = BreakReminder(break_interval_minutes=20)
camera_analytics = CameraAnalytics()

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
    "total_sessions": 0,
    # Camera state
    "camera_enabled": False,
    "camera_present": None,
    "camera_attention_score": 0,
    "camera_attention_multiplier": 1.0,
    "camera_looking_at_screen": False,
    "camera_good_posture": False,
    "camera_message": "Camera disabled",
    "posture_warning": False,
    "break_reminder": False,
    "time_until_break": 0,
    "session_paused": False
}

def update_loop():
    """Background thread to update game state every second"""
    while True:
        try:
            # Get camera status if enabled
            camera_status = camera_detector.get_status()
            user_present = True  # Default to present
            attention_multiplier = 1.0  # Default multiplier
            
            if camera_status['enabled']:
                user_present = camera_status.get('present', True)
                attention_score = camera_status.get('attention_score', 0)
                attention_multiplier = calculate_attention_multiplier(attention_score)
                
                # Update camera analytics if session active
                if game_engine.session_active and user_present:
                    camera_analytics.record_attention(attention_score)
                    camera_analytics.record_posture(camera_status.get('good_posture', False))
                    camera_analytics.record_presence(user_present)
                    
                    # Check posture warnings
                    if posture_monitor.update(camera_status.get('good_posture', False)):
                        current_state['posture_warning'] = True
                    else:
                        current_state['posture_warning'] = False
                    
                    # Check break reminders
                    if break_reminder.check_break_needed():
                        current_state['break_reminder'] = True
                    else:
                        current_state['break_reminder'] = False
                    
                    current_state['time_until_break'] = break_reminder.get_time_until_break()
                
                # Update camera state
                current_state['camera_enabled'] = True
                current_state['camera_present'] = user_present
                current_state['camera_attention_score'] = attention_score
                current_state['camera_attention_multiplier'] = round(attention_multiplier, 2)
                current_state['camera_looking_at_screen'] = camera_status.get('looking_at_screen', False)
                current_state['camera_good_posture'] = camera_status.get('good_posture', False)
                current_state['camera_message'] = camera_status.get('message', '')
            else:
                current_state['camera_enabled'] = False
                current_state['camera_message'] = 'Camera disabled'
            
            # Only track window activity if session is active
            if game_engine.session_active:
                # 1. Get Active Window
                app_name, window_title, has_permissions = tracker.get_active_window()
                
                # 2. Check if Studying
                is_studying = tracker.is_study_app(app_name, window_title)
                
                # Override if phone detected by camera
                if camera_status.get('phone_detected', False):
                    is_studying = False
                
                # 3. Update gamification with camera data
                game_engine.update(is_studying, attention_multiplier, user_present)
                
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
                
                # 7. Voice Assistant Feedback
                # Distracted if: Not studying OR (Camera enabled AND (Phone detected OR Low attention))
                is_distracted = not is_studying
                if camera_status['enabled']:
                    if camera_status.get('phone_detected', False):
                        is_distracted = True
                    elif camera_status.get('attention_score', 100) < 40:
                        is_distracted = True
                
                voice_assistant.check_status(is_distracted, is_studying)
                current_state["has_permissions"] = has_permissions
                current_state["session_paused"] = game_engine.session_paused
            else:
                # No active session - set default values
                current_state["app_name"] = "No active session"
                current_state["window_title"] = ""
                current_state["is_studying"] = False
                current_state["has_permissions"] = True
                current_state["session_paused"] = False
            
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
        
        # Reset camera analytics and monitors for new session
        camera_analytics.reset()
        posture_monitor.reset()
        break_reminder.start_session()
        
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
        
        # Add camera analytics to session data if available
        if session_data and camera_detector.enabled:
            camera_summary = camera_analytics.get_session_summary()
            session_data.update(camera_summary)
        
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

@app.route('/api/camera/toggle', methods=['POST'])
def toggle_camera():
    """Toggle camera on/off"""
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        if enabled:
            success = camera_detector.start()
        else:
            camera_detector.stop()
            success = True
        
        return jsonify({
            'success': success,
            'enabled': camera_detector.enabled
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/status')
def camera_status():
    """Get current camera status"""
    return jsonify(camera_detector.get_status())

@app.route('/api/camera/calibrate', methods=['POST'])
def calibrate_camera():
    """Calibrate camera baseline"""
    try:
        success, message = camera_detector.calibrate()
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    """Trigger voice assistant to speak text"""
    try:
        data = request.json
        text = data.get('text', '')
        if text:
            voice_assistant.speak(text)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listen', methods=['POST'])
def listen():
    """Process voice commands from frontend"""
    try:
        data = request.json
        text = data.get('text', '').lower()
        response_text = "I didn't catch that."
        
        if 'start' in text:
            if not game_engine.session_active:
                # Start normal session
                course_manager.add_course("Voice Session")
                game_engine.start_session(mode='normal', course="Voice Session")
                response_text = "Starting a new study session. Good luck!"
            else:
                response_text = "A session is already active."
                
        elif 'stop' in text:
            if game_engine.session_active:
                game_engine.stop_session()
                response_text = "Session stopped. Great work!"
            else:
                response_text = "No active session to stop."
                
        elif 'status' in text or 'doing' in text:
            xp = game_engine.state['xp']
            level = game_engine.state['level']
            response_text = f"You are level {level} with {xp} XP. Keep it up!"
            
        elif 'hello' in text or 'hi' in text:
            response_text = "Hello there! Ready to focus?"
            
        # Speak the response
        voice_assistant.speak(response_text)
        
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(camera_detector.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dev_mode')
def dev_mode():
    """Dev mode page with live camera feed"""
    return render_template('dev_mode.html')

if __name__ == '__main__':
    # Start camera if enabled in config
    if camera_config.get('enabled', False):
        camera_detector.start()
        
    app.run(port=5002, debug=True, use_reloader=False)
