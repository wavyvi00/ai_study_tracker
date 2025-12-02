from flask import Flask, render_template, jsonify, request, Response
from focus_detector import FocusDetector
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
import threading
import time
import os
import logging
import json
import signal
import atexit

# Disable Flask request logging for cleaner console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Initialize Core Logic
focus_detector = FocusDetector()
game_engine = GamificationEngine()
course_manager = CourseManager()
session_history = SessionHistory()
camera_detector = CameraDetector()

# Initialize camera integration components
posture_monitor = PostureMonitor(warning_interval_minutes=10)
break_reminder = BreakReminder(break_interval_minutes=20)
camera_analytics = CameraAnalytics()

# Global State
current_state = {
    "app_name": "Ready",
    "window_title": "Waiting for session...",
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
    "session_paused": False,
    # Auto-stop results (for health depletion or challenge completion)
    "auto_stop_results": None,
    # AI Debug Info
    "ai_debug_info": {
        "source": "Waiting...",
        "confidence": 0,
        "raw_state": "unknown",
        "reason": "",
        "grace_period_active": False,
        "grace_period_remaining": 0
    }
}

def update_loop():
    """Background thread to update game state every second"""
    while True:
        try:
            # Get camera status if enabled
            camera_status = camera_detector.get_status()
            user_present = True  # Default to present (assume user is there unless proven otherwise)
            attention_multiplier = 1.0  # Default multiplier
            
            if camera_status['enabled']:
                # Only mark as away if camera explicitly detects absence
                # If camera can't detect (low light, etc.), assume present
                detected_present = camera_status.get('present')
                if detected_present is False:  # Explicitly False, not None
                    user_present = False
                else:
                    user_present = True  # Default to present if detection is uncertain
                    
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
                print(f"🔍 SESSION ACTIVE - Starting window check")
                
                try:
                    # Fall back to window tracking (New AI System)
                    # 1. Get Focus State
                    focus_result = focus_detector.get_focus_state()
                    
                    app_name = focus_result['app_name']
                    window_title = focus_result['window_title']
                    has_permissions = focus_result['has_permissions']
                    state = focus_result['state']
                    reason = focus_result['reason']
                    
                    print(f"DEBUG: Focus Check - State: {state}, App: {app_name}, Title: {window_title}, Reason: {reason}")
                    
                    # Update AI Debug Info (with safe attribute access)
                    grace_remaining = 0
                    if hasattr(focus_detector, 'in_grace_period') and focus_detector.in_grace_period:
                        if hasattr(focus_detector, 'grace_period_start') and focus_detector.grace_period_start:
                            grace_remaining = int(focus_detector.grace_period_duration - (time.time() - focus_detector.grace_period_start))
                    
                    current_state["ai_debug_info"] = {
                        "source": focus_result.get('source', 'Unknown'),
                        "confidence": int(focus_result.get('confidence', 0) * 100),
                        "raw_state": state,
                        "reason": reason,
                        "grace_period_active": getattr(focus_detector, 'in_grace_period', False),
                        "grace_period_remaining": max(0, grace_remaining)
                    }
                except Exception as e:
                    print(f"❌ ERROR in focus detection: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fallback to safe defaults
                    app_name = "Error"
                    window_title = "Focus detection failed"
                    has_permissions = True
                    state = "unknown"
                    reason = f"Error: {str(e)}"
                    is_studying = False

                # 2. Map state to is_studying
                if state == "focused":
                    is_studying = True
                elif state == "searching":
                    is_studying = True # Treat searching as studying (or neutral)
                    print(f"🔍 User is searching/researching - allowing grace period")
                elif state == "distracted":
                    is_studying = False
                else:
                    is_studying = False # Default to distracted if unknown
                
                # Skip update if window should be ignored (None = FocusWin HUD, etc.)
                # Note: FocusDetector returns "unknown" or handles this? 
                # We need to check if it's our own app.
                if app_name in ["FocusWin", "StudyWin"]:
                     is_studying = None # Trigger the ignore logic below

                
                # Skip update if window should be ignored (None = FocusWin HUD, etc.)
                if is_studying is None:
                    print(f"DEBUG: Ignored window active - Updating UI but skipping game stats")
                    # Treat as studying for UI purposes (so it shows "Focused" instead of "Distracted")
                    is_studying = True
                    
                    # Update global state so UI reflects current app
                    current_state["app_name"] = app_name
                    current_state["window_title"] = window_title
                    current_state["is_studying"] = True
                    current_state["user_present"] = user_present
                    
                    # IMPORTANT: Do NOT call game_engine.update()
                    # This prevents gaining XP/Health but also prevents losing it
                    
                    # Still update other state variables below...
                else:
                    # Override if phone detected by camera
                    if camera_status.get('phone_detected', False):
                        is_studying = False
                        user_present = True # Force present so we penalize instead of pausing
                    
                    # 3. Update gamification with camera data
                    game_engine.update(is_studying, attention_multiplier, user_present)
                
                # 4. Check if health depleted (auto-fail session)
                
                # 4. Check if health depleted (auto-fail session)
                if game_engine.is_health_depleted():
                    print("Health depleted! Session failed.")
                    session_data = game_engine.stop_session()
                    # Store results for frontend to retrieve
                    current_state["auto_stop_results"] = session_data
                
                # 5. Check if challenge mode session is complete
                if game_engine.is_session_complete():
                    print("Challenge mode session complete! Auto-stopping.")
                    session_data = game_engine.stop_session()
                    # Store results for frontend to retrieve
                    current_state["auto_stop_results"] = session_data
                
                # 6. Update Global State
                current_state["app_name"] = app_name
                current_state["window_title"] = window_title
                current_state["is_studying"] = is_studying
                current_state["user_present"] = user_present # Add this line
                
                # 7. Voice Assistant Feedback
                # Distracted if: Not studying OR (Camera enabled AND (Phone detected OR Low attention))
                is_distracted = not is_studying
                if camera_status['enabled']:
                    if camera_status.get('phone_detected', False):
                        is_distracted = True
                    elif camera_status.get('attention_score', 100) < 40:
                        is_distracted = True
                
                current_state["has_permissions"] = has_permissions
                current_state["session_paused"] = game_engine.session_paused
            else:
                # No active session - set default values
                current_state["app_name"] = "Ready"
                current_state["window_title"] = "Waiting for session..."
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

# Cleanup function
def cleanup():
    """Clean up resources on exit"""
    print("\n🧹 Cleaning up resources...")
    try:
        camera_detector.stop()
    except Exception as e:
        print(f"Error stopping camera: {e}")
    print("✅ Cleanup complete")
    # Force exit to prevent hanging
    import sys
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup)

# Start background thread
update_thread = threading.Thread(target=update_loop, daemon=True)
update_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    # print(f"API STATUS - Active: {current_state.get('session_active')}, Health: {current_state.get('health')}")
    
    # Force sync critical session state from game engine to ensure UI is snappy
    current_state["session_active"] = game_engine.session_active
    current_state["session_mode"] = game_engine.session_mode
    current_state["current_course"] = game_engine.current_course
    current_state["time_remaining"] = game_engine.get_session_time_remaining()
    current_state["session_elapsed"] = game_engine.get_session_elapsed_time()
    
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
        
        # Immediately update global state to reflect active session
        current_state["session_active"] = True
        current_state["session_mode"] = mode
        current_state["current_course"] = course
        current_state["app_name"] = "Ready" # Reset app name
        current_state["window_title"] = "Session Started"
        
        return jsonify({"success": True, "mode": mode, "duration": duration, "course": course})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current session"""
    try:
        # Clear any pending auto-stop results
        current_state["auto_stop_results"] = None
        
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

def generate_frames():
    """Generator function for video streaming"""
    while True:
        frame_bytes = camera_detector.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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





@app.route('/dev_mode')
def dev_mode():
    """Dev mode page with live camera feed"""
    return render_template('dev_mode.html')

@app.route('/hud')
@app.route('/hud.html')
def hud():
    """HUD overlay page"""
    return render_template('hud.html')

if __name__ == '__main__':
    # Check for Accessibility permissions on macOS
    print("\n🚀 Starting AI Study Tracker...")
    # Use the new provider to check permissions
    provider = focus_detector.window_provider
    has_permission = False
    if hasattr(provider, 'check_permissions'):
        has_permission = provider.check_permissions()
    
    if not has_permission:
        print("\n⚠️  Starting app with limited functionality...")
        print("   Window detection will not work until permissions are granted.\n")
        print("   Please grant Accessibility permissions to Terminal/Python in System Settings.\n")
    else:
        print("✅ Accessibility permissions: Granted")
    
    # Load camera config
    try:
        with open('camera_config.json', 'r') as f:
            camera_config = json.load(f)
    except FileNotFoundError:
        camera_config = {"enabled": False}

    # Start camera if enabled in config
    if camera_config.get('enabled', False):
        camera_detector.start()
    
    print(f"🌐 Server running on http://localhost:5002")
    print(f"📊 HUD available at http://localhost:5002/hud")
    print(f"🎥 Dev Mode at http://localhost:5002/dev_mode\n")
        
    app.run(port=5002, debug=True, use_reloader=False)
