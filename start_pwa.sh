#!/bin/bash
# AI Study Tracker - PWA Launcher with HTTPS

# Kill any existing Flask processes on port 5002
lsof -ti:5002 | xargs kill -9 2>/dev/null

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Generate self-signed certificate if it doesn't exist
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "🔐 Generating SSL certificate..."
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost" 2>/dev/null
fi

# Start Flask server with HTTPS
echo "🚀 Starting AI Study Tracker with HTTPS..."
echo "📱 Opening in your browser..."
python3 -c "
import webbrowser
import threading
import time
from app import app

def start_server():
    # Run with SSL context
    app.run(port=5002, use_reloader=False, debug=False, ssl_context=('cert.pem', 'key.pem'))

# Start Flask in background
t = threading.Thread(target=start_server, daemon=True)
t.start()

# Wait for server to start
time.sleep(2)

# Open browser
webbrowser.open('https://127.0.0.1:5002')

print('✅ AI Study Tracker is running at https://127.0.0.1:5002')
print('⚠️  You may see a security warning - click \"Advanced\" → \"Proceed\"')
print('📱 To install as an app:')
print('   Chrome: Click the install icon in the address bar')
print('   Safari: Share → Add to Dock')
print('')
print('Press Ctrl+C to stop')

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('\n👋 Shutting down...')
"
