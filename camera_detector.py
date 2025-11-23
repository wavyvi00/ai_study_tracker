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
        self.debug_frame = None  # Store latest frame for dev mode
        self.lock = threading.Lock()  # Thread safety for frame access
        
        # Smoothing variables
        self.smoothed_score = 0
        self.alpha = 0.2  # Smoothing factor (lower = smoother)
        
        # Load Haar Cascade for basic face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize MediaPipe if available
        if HAS_MEDIAPIPE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_pose = mp.solutions.pose
            self.mp_hands = mp.solutions.hands
            
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
            
            self.hands = self.mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        else:
            self.face_mesh = None
            self.pose = None
            self.hands = None
        
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
            
        # Store frame for debug view (thread-safe)
        with self.lock:
            self.debug_frame = frame.copy()
        
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
        hand_results = self.hands.process(rgb_frame)
        
        # Calculate attention score with head pose
        attention_score, phone_detected, head_pose = self._calculate_attention_score(face_results, pose_results, hand_results, frame.shape)
        
        # Apply smoothing
        self.smoothed_score = (self.alpha * attention_score) + ((1 - self.alpha) * self.smoothed_score)
        final_score = int(self.smoothed_score)
        
        # Determine if looking at screen
        looking_at_screen = final_score > 60
        
        # Check presence
        present = face_results.multi_face_landmarks is not None
        
        # Get landmarks if present
        face_landmarks = face_results.multi_face_landmarks[0] if present else None
        pose_landmarks = pose_results.pose_landmarks if pose_results else None
        
        # Draw debug info on the stored frame
        if self.debug_frame is not None:
            self._draw_debug_info(self.debug_frame, face_landmarks, pose_landmarks, head_pose, final_score, phone_detected)
        
        return {
            'present': present,
            'face_count': 1 if present else 0,
            'attention_score': final_score,
            'looking_at_screen': looking_at_screen,
            'head_facing_forward': self._is_facing_forward_3d(head_pose) if head_pose else False,
            'good_posture': self._has_good_posture(pose_landmarks),
            'phone_detected': phone_detected,
            'head_pose': head_pose,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.9 if present else 0.1,
            'method': 'advanced'
        }
    
    def _calculate_attention_score(self, face_results, pose_results, hand_results, img_shape):
        """Calculate attention score from 0-100 using 3D head pose"""
        score = 0
        phone_detected = False
        head_pose = None
        
        # Face detected
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            
            # Calculate 3D Head Pose
            head_pose = self._get_head_pose(face_landmarks, img_shape)
            
            if head_pose:
                pitch, yaw, roll = head_pose
                
                # Check if looking at screen (Pitch: -10 to 10, Yaw: -20 to 20)
                if -15 < pitch < 15 and -20 < yaw < 20:
                    score += 50
                # Penalty for looking down (Pitch < -15)
                elif pitch < -15:
                    score = max(0, score - 20)
                # Penalty for looking sideways (Yaw > 20 or < -20)
                elif abs(yaw) > 20:
                    score = max(0, score - 20)
            else:
                # Fallback to simple check if pose calculation fails
                if self._is_facing_forward(face_landmarks):
                    score += 50
        
        # Good posture (30 points)
        if pose_results.pose_landmarks:
            if self._has_good_posture(pose_results.pose_landmarks):
                score += 30
        
        # Eyes visible (20 points)
        if face_results.multi_face_landmarks:
            score += 20
            
        # Check for phone usage (hands near face)
        if hand_results.multi_hand_landmarks and face_results.multi_face_landmarks:
            if self._is_using_phone(hand_results.multi_hand_landmarks, face_results.multi_face_landmarks[0]):
                score = max(0, score - 50)  # Penalty for phone usage
                phone_detected = True
        
        return min(100, score), phone_detected, head_pose
    
    def _is_facing_forward(self, face_landmarks):
        """Check if face is oriented toward screen"""
        if not face_landmarks:
            return False
        
        # Use nose tip and check if centered
        nose = face_landmarks.landmark[1]
        
        # Check if nose is roughly centered (x between 0.3 and 0.7)
        return 0.3 < nose.x < 0.7
    
    def _has_good_posture(self, pose_landmarks):
        """Check if user has good sitting posture"""
        if not pose_landmarks:
            return False
        
        try:
            # pose_landmarks is already the landmark list, not the results object
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
        except Exception as e:
            # Silently handle any landmark access errors
            return False
            
    def _is_using_phone(self, hand_landmarks_list, face_landmarks):
        """Check if hands are near face (potential phone usage)"""
        try:
            # Get face bounding box (approximate)
            face_x = [lm.x for lm in face_landmarks.landmark]
            face_y = [lm.y for lm in face_landmarks.landmark]
            min_x, max_x = min(face_x), max(face_x)
            min_y, max_y = min(face_y), max(face_y)
            
            # Expand bounding box slightly
            margin = 0.1
            min_x -= margin
            max_x += margin
            min_y -= margin
            max_y += margin
            
            for hand_landmarks in hand_landmarks_list:
                # Check if any finger tip is inside the face bounding box
                # Tips: 4 (thumb), 8 (index), 12 (middle), 16 (ring), 20 (pinky)
                finger_tips = [4, 8, 12, 16, 20]
                
                for tip_id in finger_tips:
                    tip = hand_landmarks.landmark[tip_id]
                    if min_x < tip.x < max_x and min_y < tip.y < max_y:
                        return True
                        
            return False
        except Exception:
            return False
            
    def _get_head_pose(self, face_landmarks, img_shape):
        """Calculate 3D head pose (Pitch, Yaw, Roll)"""
        try:
            h, w, _ = img_shape
            
            # 3D model points (generic face)
            model_points = np.array([
                (0.0, 0.0, 0.0),             # Nose tip
                (0.0, -330.0, -65.0),        # Chin
                (-225.0, 170.0, -135.0),     # Left eye left corner
                (225.0, 170.0, -135.0),      # Right eye right corner
                (-150.0, -150.0, -125.0),    # Left Mouth corner
                (150.0, -150.0, -125.0)      # Right mouth corner
            ])
            
            # 2D image points from landmarks
            # Nose tip (1), Chin (152), Left Eye Left (33), Right Eye Right (263), Left Mouth (61), Right Mouth (291)
            image_points = np.array([
                (face_landmarks.landmark[1].x * w, face_landmarks.landmark[1].y * h),
                (face_landmarks.landmark[152].x * w, face_landmarks.landmark[152].y * h),
                (face_landmarks.landmark[33].x * w, face_landmarks.landmark[33].y * h),
                (face_landmarks.landmark[263].x * w, face_landmarks.landmark[263].y * h),
                (face_landmarks.landmark[61].x * w, face_landmarks.landmark[61].y * h),
                (face_landmarks.landmark[291].x * w, face_landmarks.landmark[291].y * h)
            ], dtype="double")
            
            # Camera internals
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")
            
            dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs
            )
            
            if not success:
                return None
                
            # Convert rotation vector to angles
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            proj_matrix = np.hstack((rotation_matrix, translation_vector))
            eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6]
            
            pitch, yaw, roll = [float(x) for x in eulerAngles]
            
            return pitch, yaw, roll
            
        except Exception:
            return None

    def _is_facing_forward_3d(self, head_pose):
        """Check if facing forward using 3D angles"""
        if not head_pose:
            return False
        pitch, yaw, roll = head_pose
        return -15 < pitch < 15 and -20 < yaw < 20

    def _draw_debug_info(self, frame, face_landmarks, pose_landmarks, head_pose, score, phone_detected):
        """Draw debug overlays on frame"""
        try:
            # Draw Face Mesh
            if face_landmarks:
                self.mp_drawing = mp.solutions.drawing_utils
                self.mp_drawing_styles = mp.solutions.drawing_styles
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
            
            # Draw Head Pose
            if head_pose:
                pitch, yaw, roll = head_pose
                cv2.putText(frame, f"Pitch: {int(pitch)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Yaw: {int(yaw)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Roll: {int(roll)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw Score
            color = (0, 255, 0) if score > 60 else (0, 0, 255)
            cv2.putText(frame, f"Score: {score}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Draw Phone Status
            if phone_detected:
                cv2.putText(frame, "PHONE DETECTED", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                
        except Exception as e:
            print(f"Debug draw error: {e}")

    def generate_frames(self):
        """Generator for video streaming"""
        while True:
            with self.lock:
                if self.debug_frame is None:
                    time.sleep(0.1)
                    continue
                
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', self.debug_frame)
                frame = buffer.tobytes()
            
            # Yield frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Limit FPS to ~30 to save resources
            time.sleep(0.033)
    
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
            'method': self.last_detection.get('method', 'basic'),
            'phone_detected': self.last_detection.get('phone_detected', False),
            'message': self._get_status_message(self.last_detection)
        }
    
    def _get_status_message(self, detection):
        """Generate human-readable status message"""
        if not detection['present']:
            return 'User away'
            
        if detection.get('phone_detected', False):
            return '📱 Phone detected'
        
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
