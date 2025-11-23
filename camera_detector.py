import cv2
import numpy as np
from datetime import datetime
import threading
import time

# MediaPipe for advanced detection
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False
    print("⚠️ MediaPipe not installed - using basic face detection only")

class CameraDetector:
    """Advanced camera-based detection with pose and gaze tracking"""
    
    def __init__(self):
        self.camera = None
        self.enabled = False
        self.last_detection = None
        self.detection_thread = None
        self.running = False
        
        # Load Haar Cascade for basic face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize MediaPipe if available
        if HAS_MEDIAPIPE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_pose = mp.solutions.pose
            
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        else:
            self.face_mesh = None
            self.pose = None
        
    def start(self):
        """Start camera capture in background thread"""
        if self.enabled:
            return
            
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
                
            self.enabled = True
            self.running = True
            
            # Start detection in background thread
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            
            print("✅ Camera started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting camera: {e}")
            self.enabled = False
            return False
    
    def stop(self):
        """Stop camera and release resources"""
        self.running = False
        self.enabled = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        print("🛑 Camera stopped")
    
    def _detection_loop(self):
        """Background thread for continuous detection"""
        while self.running:
            try:
                detection = self._detect_once()
                if detection:
                    self.last_detection = detection
                time.sleep(0.5)  # Check twice per second
            except Exception as e:
                print(f"Detection error: {e}")
                time.sleep(1)
    
    def _detect_once(self):
        """Single detection frame with advanced analysis"""
        if not self.camera or not self.camera.isOpened():
            return None
            
        ret, frame = self.camera.read()
        if not ret:
            return None
        
        # Use MediaPipe if available, otherwise fall back to basic detection
        if HAS_MEDIAPIPE and self.face_mesh and self.pose:
            return self._advanced_detection(frame)
        else:
            return self._basic_detection(frame)
    
    def _basic_detection(self, frame):
        """Basic face detection fallback"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return {
            'present': len(faces) > 0,
            'face_count': len(faces),
            'attention_score': 50 if len(faces) > 0 else 0,
            'looking_at_screen': len(faces) > 0,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.6 if len(faces) > 0 else 0.2,
            'method': 'basic'
        }
    
    def _advanced_detection(self, frame):
        """Advanced detection with MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with face mesh and pose
        face_results = self.face_mesh.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        
        # Calculate attention score
        attention_score = self._calculate_attention_score(face_results, pose_results)
        
        # Determine if looking at screen
        looking_at_screen = attention_score > 60
        
        # Check presence
        present = face_results.multi_face_landmarks is not None
        
        return {
            'present': present,
            'face_count': 1 if present else 0,
            'attention_score': attention_score,
            'looking_at_screen': looking_at_screen,
            'head_facing_forward': self._is_facing_forward(face_results) if present else False,
            'good_posture': self._has_good_posture(pose_results),
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.9 if present else 0.1,
            'method': 'advanced'
        }
    
    def _calculate_attention_score(self, face_results, pose_results):
        """Calculate attention score from 0-100"""
        score = 0
        
        # Face detected and facing forward (50 points)
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            
            if self._is_facing_forward(face_landmarks):
                score += 50
        
        # Good posture (30 points)
        if pose_results.pose_landmarks:
            if self._has_good_posture(pose_results.pose_landmarks):
                score += 30
        
        # Eyes visible (20 points)
        if face_results.multi_face_landmarks:
            score += 20
        
        return min(100, score)
    
    def _is_facing_forward(self, face_landmarks):
        """Check if face is oriented toward screen"""
        if not face_landmarks:
            return False
        
        # Use nose tip and check if centered
        nose = face_landmarks.landmark[1]
        
        # Check if nose is roughly centered (x between 0.3 and 0.7)
        return 0.3 < nose.x < 0.7
    
    def _has_good_posture(self, pose_results):
        """Check if user has good sitting posture"""
        if not pose_results or not pose_results.pose_landmarks:
            return False
        
        try:
            pose_landmarks = pose_results.pose_landmarks
            # Check shoulder alignment
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # Shoulders should be roughly level
            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            
            # Check if shoulders are above hips (basic posture check)
            left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            shoulders_above_hips = (left_shoulder.y < left_hip.y) and (right_shoulder.y < right_hip.y)
            
            return (shoulder_diff < 0.1) and shoulders_above_hips
        except Exception:
            return False
    
    def get_status(self):
        """Get current detection status"""
        if not self.enabled:
            return {
                'enabled': False,
                'present': None,
                'attention_score': 0,
                'message': 'Camera disabled'
            }
        
        if not self.last_detection:
            return {
                'enabled': True,
                'present': None,
                'attention_score': 0,
                'message': 'Initializing...'
            }
        
        return {
            'enabled': True,
            'present': self.last_detection['present'],
            'face_count': self.last_detection['face_count'],
            'attention_score': self.last_detection.get('attention_score', 0),
            'looking_at_screen': self.last_detection.get('looking_at_screen', False),
            'head_facing_forward': self.last_detection.get('head_facing_forward', False),
            'good_posture': self.last_detection.get('good_posture', False),
            'confidence': self.last_detection['confidence'],
            'timestamp': self.last_detection['timestamp'],
            'method': self.last_detection.get('method', 'basic'),
            'message': self._get_status_message(self.last_detection)
        }
    
    def _get_status_message(self, detection):
        """Generate human-readable status message"""
        if not detection['present']:
            return 'User away'
        
        score = detection.get('attention_score', 0)
        
        if score >= 80:
            return '✅ Fully focused'
        elif score >= 60:
            return '👀 Paying attention'
        elif score >= 40:
            return '⚠️ Somewhat distracted'
        else:
            return '❌ Distracted'
    
    def is_user_present(self):
        """Simple check if user is present"""
        if not self.enabled or not self.last_detection:
            return None
        return self.last_detection['present']
