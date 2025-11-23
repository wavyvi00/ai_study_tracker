import webview
import threading
import time
import sys
from app import app

def start_server():
    """Starts the Flask server in a background thread"""
    app.run(port=5002, use_reloader=False, debug=False)

def main():
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Give it time to start
    time.sleep(2)
    
    # Create the native window pointing to the Flask app
    window = webview.create_window(
        "AI Study Tracker", 
        "http://127.0.0.1:5002",
        width=480,
        height=700,
        resizable=True,
        on_top=True,  # Always on top
        frameless=False
    )
    
    # Start the webview (this blocks until window is closed)
    webview.start(debug=False)

if __name__ == '__main__':
    main()
