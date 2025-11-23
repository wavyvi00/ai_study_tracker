#!/bin/bash
# Create a simple .app wrapper

APP_NAME="AI Study Tracker"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean up old app if exists
rm -rf "$APP_DIR"

# Create directory structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy the launcher script
cp launch.sh "$MACOS_DIR/$APP_NAME"
chmod +x "$MACOS_DIR/$APP_NAME"

# Copy all project files to Resources
cp -r static templates *.py *.json *.pt "$RESOURCES_DIR/" 2>/dev/null || true

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>AI Study Tracker</string>
    <key>CFBundleDisplayName</key>
    <string>AI Study Tracker</string>
    <key>CFBundleIdentifier</key>
    <string>com.focuswin.aistudytracker</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>AI Study Tracker</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>AI Study Tracker uses your microphone to listen to voice commands.</string>
    <key>NSCameraUsageDescription</key>
    <string>AI Study Tracker uses your camera to detect focus and distractions.</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Update the launcher to use Resources directory
cat > "$MACOS_DIR/$APP_NAME" << 'EOF'
#!/bin/bash
RESOURCES="$(dirname "$0")/../Resources"
cd "$RESOURCES"
python3 desktop_app.py
EOF

chmod +x "$MACOS_DIR/$APP_NAME"

echo "✅ Created $APP_DIR"
echo "You can now double-click it to launch!"
