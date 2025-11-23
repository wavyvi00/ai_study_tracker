# AI Study Tracker - PWA Setup Guide

## Quick Start

### 1. Launch the App
```bash
cd /Users/victorrodriguez/Desktop/ai_study_tracker
./start_pwa.sh
```

This will:
- Start the Flask server
- Open your browser automatically
- Show installation instructions

### 2. Install as PWA

#### Chrome:
1. Look for the **install icon** (⊕) in the address bar
2. Click it and select **"Install"**
3. The app will open in its own window
4. You can now close the browser tab

#### Safari:
1. Click **Share** button
2. Select **"Add to Dock"**
3. The app icon will appear in your Dock

### 3. Using the Installed App

Once installed:
- ✅ **Runs in standalone window** (no browser UI)
- ✅ **Microphone permissions work** (browser handles it natively)
- ✅ **Can stay open in background**
- ✅ **Appears in Dock** like a native app
- ✅ **All features work** (camera, voice, tracking)

## Features

### Voice Commands
Click the Magic Ball and say:
- "Start session"
- "Stop session"
- "How am I doing?"
- "Hello"

### Camera Detection
- Automatically tracks focus
- Detects phone usage
- Monitors posture

## Troubleshooting

### If microphone doesn't work:
1. Browser will ask for permission - click **"Allow"**
2. If you accidentally denied it:
   - Chrome: Click the lock icon in address bar → Site settings → Microphone → Allow
   - Safari: Safari menu → Settings → Websites → Microphone → Allow

### If camera doesn't work:
Same steps as microphone, but for Camera permission.

## Next Steps: Tauri Migration

For a true native app experience, see `TAURI_MIGRATION_PLAN.md`.

The PWA is a working solution for now, and you can migrate to Tauri later for:
- Smaller app size
- Better native integration
- Professional distribution
