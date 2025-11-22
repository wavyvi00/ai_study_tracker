import webview
import threading
import time
import sys
from app import app

def start_server():
    """Starts the Flask server in a background thread"""
    # Run on a different port to be safe, or same if we kill previous
    app.run(port=5002, use_reloader=False)

def main():
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Give it a second to start
    time.sleep(1)
    
    # Create the native window pointing to the Flask app
    webview.create_window(
        "AI Study Tracker", 
        "http://127.0.0.1:5002",
        width=480,
        height=700,
        resizable=True
    )
    
    # Start the webview (this blocks until window is closed)
    webview.start()

if __name__ == '__main__':
    main()
