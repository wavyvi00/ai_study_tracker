# StudyWin 🎯

A gamified productivity tracker that helps you stay focused and level up your study sessions with RPG-style mechanics.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.9+-green)

## ✨ Features

- **Gamification System**: Earn XP, level up, and maintain health based on your focus
- **Daily Streaks**: Build consecutive study days with bonus XP rewards
- **Challenge Mode**: Set timed focus challenges with specific durations
- **💚 Health System**: Your health decreases when distracted and regenerates while studying
- **⏱️ Study Timer**: Tracks total study time with a clean, formatted display
- **📹 Camera Detection**: AI-powered attention tracking using computer vision
- **👀 3D Head Pose**: Tracks Pitch, Yaw, and Roll to detect looking down/away
- **📱 Phone Detection**: Detects if you are using your phone (YOLO-based detection)
- **🧍 Posture Analysis**: Monitors sitting posture for better focus
- **🎥 Live Camera Feed**: Real-time video preview with detection overlays (Dev Mode)
- **🖥️ Native Desktop App**: Beautiful native macOS window powered by Tauri
- **📊 Always-On-Top HUD**: Minimal overlay showing health, XP, and status
- **🎨 Modern UI**: Sleek dark mode interface with smooth animations
- **🔒 Privacy-First**: All processing is local; no video leaves your device

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Rust** (for Tauri): Install via [rustup](https://rustup.rs/)
- **Node.js** (for Tauri): Install via [Homebrew](https://brew.sh/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_study_tracker
   ```

2. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install Tauri CLI**
   ```bash
   cargo install tauri-cli
   ```

### Running the App

**Development Mode:**
```bash
cd src-tauri
cargo tauri dev
```

This will:
- Start the Flask backend on port 5002
- Launch the native macOS window
- Launch the always-on-top HUD overlay
- Request Camera permissions (if not already granted)

### First Launch

On first launch, macOS will prompt you for:
- **Camera Access**: Required for attention detection and posture monitoring
- **Screen Recording**: Required for tracking active applications

Grant these permissions in **System Settings > Privacy & Security**.

---

## 🎯 How It Works

The tracker monitors your active window and classifies your activity as either **studying** or **distracted**:

### Study Apps (Earn XP + Health)
- Code editors: VS Code, Cursor, Xcode, IntelliJ, PyCharm
- Learning platforms: Canvas, Notion, Obsidian
- Documentation: PDF viewers, docs
- Development tools: Terminal

### Distraction Apps (Lose Health)
- Social media: YouTube, Twitter, Reddit, Facebook, Instagram
- Entertainment: Netflix, games
- Other non-productive apps

### Camera Intelligence 🧠
- **Attention Score**: 0-100 score based on face orientation and gaze
- **XP Multiplier**: Earn up to **1.0x XP** when focused, drops to **0.5x** when distracted
- **User Away Detection**: Status shows "Away" when you leave your desk
- **Phone Penalty**: Attention score drops significantly if phone usage is detected
- **Posture Warnings**: Get notified if you slouch for too long

### Rewards System
- **+1 XP per second** of studying (multiplied by attention score)
- **Level up** every 100 XP
- **Health regenerates** slowly while studying (+0.1/sec)
- **Health decreases** when distracted or away (-5.0/sec)

---

## 🎥 Dev Mode (Live Feed)

Want to see what the AI sees?

1. Start the application
2. Enable camera in the main app
3. Open your browser to: `http://localhost:5002/dev_mode`
4. You will see:
   - Live video feed (mirrored)
   - Face Mesh overlays
   - Head Pose angles (Pitch/Yaw/Roll)
   - Real-time attention score
   - Phone detection status

---

## 📁 Project Structure

```
ai_study_tracker/
├── app.py                    # Flask application and API routes
├── tracker.py                # macOS window tracking (Quartz)
├── gamification.py           # XP, leveling, and health system
├── camera_detector.py        # Camera-based attention detection (MediaPipe + YOLO)
├── camera_integration.py     # Camera logic helper (Posture, Breaks)
├── courses.py                # Course management
├── session_history.py        # Session tracking
├── requirements.txt          # Python dependencies
├── camera_config.json        # Camera settings (gitignored)
├── study_data.json           # Persistent user data (gitignored)
├── src-tauri/                # Tauri native app
│   ├── src/main.rs           # Rust main entry point
│   ├── tauri.conf.json       # Tauri configuration
│   └── Cargo.toml            # Rust dependencies
├── templates/
│   ├── index.html            # Main UI template
│   ├── hud.html              # HUD overlay template
│   └── dev_mode.html         # Camera debug UI
├── static/
│   ├── style.css             # Main app styling
│   └── script.js             # Real-time UI updates
└── public/                   # Tauri public assets
    └── hud.html              # HUD copy for Tauri
```

## 🔧 Configuration

### Customizing Study/Distraction Keywords

Edit `tracker.py` to modify what counts as studying:

```python
self.study_keywords = ['code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', ...]
self.distraction_keywords = ['youtube', 'twitter', 'reddit', 'facebook', ...]
```

### Camera Settings

Edit `camera_config.json` (created after first run) to adjust:
- `enabled`: Enable/disable camera tracking
- Camera preferences are saved automatically

### Adjusting Rewards

Edit `gamification.py` to change XP and health rates:

```python
self.xp += 1  # XP per second of studying
self.health = min(100, self.health + 0.1)  # Health regen rate
self.decrease_health(5.0)  # Health loss rate when distracted/away
```

## 🎨 UI Components

The interface features:
- **Main Window**: Full study tracker with stats and controls
- **HUD Overlay**: Always-on-top minimal display showing:
  - Session timer
  - Health bar
  - XP progress
  - Current status (Studying/Distracted/Away)
- **Status Badge**: Real-time studying/distracted/away indicator
- **Health Bar**: Visual health indicator with color coding
- **Level Circle**: Displays current level with gradient background
- **XP Counter**: Shows accumulated experience points

## 🔐 Privacy & Data

All tracking data is stored locally in `study_data.json`:

```json
{
  "xp": 4170,
  "level": 42,
  "health": 100,
  "total_study_seconds": 4470,
  "current_streak": 5
}
```

This file is automatically excluded from version control via `.gitignore`.

## 🐛 Troubleshooting

### "loginwindow" appears constantly
- **Cause**: Missing Screen Recording permissions
- **Fix**: Grant permissions in System Settings → Privacy & Security → Screen Recording

### App doesn't track window titles
- **Cause**: Quartz requires Screen Recording permission
- **Fix**: Enable Terminal/Python in Screen Recording settings and restart

### Health keeps decreasing
- **Cause**: Current app not in study keywords list
- **Fix**: Add your app to `study_keywords` in `tracker.py`

### HUD not appearing
- **Cause**: Tauri window configuration issue
- **Fix**: Restart the app with `cargo tauri dev`

### Camera shows "Initializing..." or "Starting camera..."
- **Cause**: Camera not producing frames or MediaPipe initialization delay
- **Fix**: Wait a few seconds, or restart the app

### Dev Mode shows 403 Forbidden
- **Cause**: Port 5000 is used by macOS AirPlay
- **Fix**: Use port 5002 instead: `http://localhost:5002/dev_mode`

## 🛠️ Development

### Running in Debug Mode

For web-only testing without the native window:

```bash
python3 app.py
```

Then open `http://localhost:5002` in your browser.

### API Endpoints

- `GET /` - Main application UI
- `GET /hud` or `/hud.html` - HUD overlay
- `GET /dev_mode` - Camera debug view
- `GET /api/status` - Returns current tracking state (JSON)
- `GET /api/camera/status` - Returns camera tracking state (JSON)
- `GET /video_feed` - MJPEG stream of camera feed (Dev Mode)
- `POST /api/camera/toggle` - Enable/disable camera
- `POST /api/camera/calibrate` - Calibrate camera baseline

### Response Format

```json
{
  "app_name": "Cursor",
  "window_title": "tracker.py",
  "is_studying": true,
  "user_present": true,
  "xp": 4170,
  "level": 42,
  "health": 100,
  "time_formatted": "01:14:30",
  "session_active": true,
  "has_permissions": true,
  "camera_enabled": true,
  "camera_attention_score": 85,
  "camera_message": "Paying attention"
}
```

## 📝 Future Enhancements

**Completed:**
- [x] Daily streak tracking and rewards
- [x] Camera-based attention detection
- [x] Pose and gaze tracking
- [x] Phone detection (YOLO)
- [x] 3D Head Pose Estimation
- [x] Dev Mode with live video feed
- [x] Tauri native app
- [x] Always-on-top HUD overlay
- [x] User away detection

**Planned:**
- [ ] Daily/weekly statistics dashboard
- [ ] Custom study goals and milestones
- [ ] Break reminders and Pomodoro integration
- [ ] Export data to CSV/JSON
- [ ] Achievements and badges system
- [ ] Focus mode with website blocking
- [ ] ML-based personalized learning
- [ ] Windows support

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for personal use.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Native app via [Tauri](https://tauri.app/)
- macOS integration using [PyObjC](https://pyobjc.readthedocs.io/)
- Computer vision with [OpenCV](https://opencv.org/)
- Pose/gaze tracking with [MediaPipe](https://mediapipe.dev/)
- Object detection with [YOLOv8](https://github.com/ultralytics/ultralytics)
- UI fonts: [Inter](https://rsms.me/inter/) & [JetBrains Mono](https://www.jetbrains.com/lp/mono/)

---

**Stay focused, level up, and achieve your goals! 🚀**
