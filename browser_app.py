import webbrowser
import threading
import time
from app import app

def start_server():
    """Starts the Flask server in a background thread"""
    app.run(port=5002, use_reloader=False)

def main():
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Give it a second to start
    time.sleep(2)
    
    # Open in default browser
    webbrowser.open('http://127.0.0.1:5002')
    
    # Keep the script running
    print("✅ AI Study Tracker is running at http://127.0.0.1:5002")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == '__main__':
    main()
