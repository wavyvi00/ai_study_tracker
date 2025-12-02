import cv2
import time

print("Testing camera access...")

try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera (index 0)")
        exit(1)
        
    print("✅ Camera opened successfully")
    
    print("Attempting to read frame...")
    ret, frame = cap.read()
    
    if ret:
        print("✅ Frame read successfully")
        print(f"Frame shape: {frame.shape}")
    else:
        print("❌ Failed to read frame (ret=False)")
        
    cap.release()
    print("Camera released")
    
except Exception as e:
    print(f"❌ Error: {e}")
