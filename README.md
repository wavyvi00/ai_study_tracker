# StudyWin 🎯

A gamified productivity tracker that helps you stay focused and level up your study sessions with RPG-style mechanics.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.8+-green)

## ✨ Features

- **Gamification System**: Earn XP, level up, and maintain health based on your focus
- **Daily Streaks**: Build consecutive study days with bonus XP rewards
- **Challenge Mode**: Set timed focus challenges with specific durations
- **💚 Health System**: Your health decreases when distracted and regenerates while studying
- **⏱️ Study Timer**: Tracks total study time with a clean, formatted display
- **📹 Camera Detection**: AI-powered attention tracking using computer vision
- **👀 3D Head Pose**: Tracks Pitch, Yaw, and Roll to detect looking down/away
- **📱 Phone Detection**: Detects if you are using your phone (hands near face)
- **🧍 Posture Analysis**: Monitors sitting posture for better focus
- **🎥 Live Camera Feed**: Real-time video preview with detection overlays
- **🖥️ Native Desktop App**: Beautiful native macOS window powered by Tauri
- **🎨 Modern UI**: Sleek dark mode interface with smooth animations
- **🔒 Privacy-First**: All processing is local; no video leaves your device

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
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
- **Auto-Pause**: Session pauses automatically when you leave your desk
- **Phone Penalty**: **-50 points** to attention score if phone usage is detected
- **Posture Warnings**: Get notified if you slouch for too long

### Rewards System
- **+1 XP per second** of studying (multiplied by attention score)
- **Level up** every 100 XP
- **Health regenerates** slowly while studying (+0.1/sec)
- **Health decreases** when distracted (-0.5/sec)
   - System Settings → Privacy & Security → Screen Recording
   - Enable Terminal or Python
   - Restart the app

4. **Enable Camera (Optional)**
   - Click the camera icon in the UI to enable AI tracking
   - Grant Camera permissions if prompted

That's it! No Python installation needed.

---

## 🛠️ For Developers

### Building the Standalone App

Want to build the app yourself? Use the automated build script:

```bash
./build.sh
```

This will create `dist/AI Study Tracker.app` - a standalone application bundle.

### Development Setup

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies (including MediaPipe, OpenCV)
- Set up the development environment

Then run:
```bash
source venv/bin/activate
python3 desktop_app.py
```

### 🎥 Dev Mode (Live Feed)

Want to see what the AI sees?

1. Start the application
2. Open your browser to: `http://127.0.0.1:5002/dev_mode`
3. You will see:
   - Live video feed
   - Face Mesh overlays
   - Head Pose angles (Pitch/Yaw/Roll)
   - Real-time attention score
   - Phone detection status

---

## 🚀 Getting Started (Manual Installation)

### Prerequisites

**macOS:**
- macOS 10.14 or higher
- Python 3.8 or higher
- Screen Recording permissions (for window tracking)
- Camera permissions (for attention tracking)

**Windows:**
- Windows 10 or higher
- Python 3.8 or higher
- No special permissions required

### Installation

**Option A: Automated Setup (Recommended)**

**macOS:**
```bash
./setup.sh
```

**Windows:**
```batch
setup-windows.bat
```

**Option B: Manual Setup**

1. **Create and activate virtual environment**
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Windows:**
   ```batch
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. **Install dependencies**
   
   **macOS:**
   ```bash
   pip install -r requirements-macos.txt
   ```
   
   **Windows:**
   ```batch
   pip install -r requirements-windows.txt
   ```

3. **Grant permissions (macOS only)**
   - Open **System Settings**
   - Go to **Privacy & Security** → **Screen Recording**
   - Enable **Terminal** or **Python**
   - Restart the app after granting permissions

### Running the App

```bash
source venv/bin/activate
python3 desktop_app.py
```

The app will launch in a native window at `http://127.0.0.1:5002`

## 📁 Project Structure

```
focuswin/
├── app.py                    # Flask application and API routes
├── desktop_app.py            # Native desktop window launcher
├── tracker.py                # Cross-platform window tracking
├── gamification.py           # XP, leveling, and health system
├── camera_detector.py        # Camera-based attention detection (MediaPipe)
├── camera_integration.py     # Camera logic helper (Posture, Breaks)
├── courses.py                # Course management
├── session_history.py        # Session tracking
├── requirements.txt          # Common dependencies
├── requirements-macos.txt    # macOS-specific dependencies
├── requirements-windows.txt  # Windows-specific dependencies
├── setup.sh                  # macOS setup script
├── setup-windows.bat         # Windows setup script
├── build.sh                  # macOS build script
├── build-windows.bat         # Windows build script
├── camera_config.json        # Camera settings (gitignored)
├── study_data.json           # Persistent user data (gitignored)
├── templates/
│   ├── index.html            # Main UI template
│   └── dev_mode.html         # Camera debug UI
├── static/
│   ├── style.css             # Earthy theme styling
│   └── script.js             # Real-time UI updates
├── dist/                     # Built apps (gitignored)
│   ├── FocusWin.app          # macOS app
│   └── FocusWin/             # Windows app folder
│       └── FocusWin.exe
└── venv/                     # Virtual environment (gitignored)
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
- `auto_pause_enabled`: Pause session when away
- `posture_warnings_enabled`: Enable/disable posture alerts
- `break_interval_minutes`: Time between break reminders

### Adjusting Rewards

Edit `gamification.py` to change XP and health rates:

```python
self.xp += 1  # XP per second of studying
self.health = min(100, self.health + 0.1)  # Health regen rate
self.decrease_health(0.5)  # Health loss rate when distracted
```

### Level Up Formula

Currently: **100 XP per level**

```python
if self.xp >= self.level * 100:
    self.level += 1
```

## 🎨 UI Components

The interface features:
- **Timer Display**: Shows total study time in HH:MM:SS format
- **Status Badge**: Real-time studying/distracted indicator
- **Health Bar**: Visual health indicator with color coding
  - Green (>50%)
  - Orange (20-50%)
  - Red (<20%)
- **Level Circle**: Displays current level with gradient background
- **XP Counter**: Shows accumulated experience points
- **Active Window Display**: Shows currently tracked app and window

## 🔐 Privacy & Data

All tracking data is stored locally in `study_data.json`:

```json
{
  "xp": 4170,
  "level": 42,
  "health": 100,
  "total_study_seconds": 4470
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

### Data not persisting
- **Cause**: Permission issues with `study_data.json`
- **Fix**: Check file permissions and ensure write access

### macOS blocks the standalone app (Gatekeeper)
- **Cause**: App is not code-signed
- **Fix**: Right-click the app → Open (instead of double-clicking)
- **Alternative**: System Settings → Privacy & Security → Click "Open Anyway"
- **Note**: This only needs to be done once per app

## 🛠️ Development

### Running in Debug Mode

For web-only testing without the native window:

```bash
python3 app.py
```

Then open `http://127.0.0.1:5002` in your browser.

### API Endpoints

- `GET /` - Main application UI
- `GET /api/status` - Returns current tracking state (JSON)
- `GET /api/camera/status` - Returns camera tracking state (JSON)
- `GET /video_feed` - MJPEG stream of camera feed (Dev Mode)

### Response Format

```json
{
  "app_name": "Cursor",
  "window_title": "tracker.py",
  "is_studying": true,
  "xp": 4170,
  "level": 42,
  "health": 100,
  "time_formatted": "01:14:30",
  "has_permissions": true,
  "camera": {
      "enabled": true,
      "attention_score": 85,
      "phone_detected": false,
      "message": "✅ Fully focused"
  }
}
```

## 📝 Future Enhancements

**Completed:**
- [x] Daily streak tracking and rewards
- [x] Multi-platform support (macOS and Windows)
- [x] Camera-based attention detection
- [x] Pose and gaze tracking
- [x] Phone detection (MediaPipe Hands)
- [x] 3D Head Pose Estimation
- [x] Dev Mode with live video feed

**Planned:**
- [ ] Daily/weekly statistics dashboard
- [ ] Custom study goals and milestones
- [ ] Break reminders and Pomodoro integration
- [ ] Export data to CSV/JSON
- [ ] Achievements and badges system
- [ ] Focus mode with website blocking
- [ ] ML-based personalized learning

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for personal use.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Native window via [pywebview](https://pywebview.flowrl.com/)
- macOS integration using [PyObjC](https://pyobjc.readthedocs.io/)
- Windows integration using [pywin32](https://github.com/mhammond/pywin32)
- Computer vision with [OpenCV](https://opencv.org/)
- Pose/gaze tracking with [MediaPipe](https://mediapipe.dev/)
- UI fonts: [Inter](https://rsms.me/inter/) & [JetBrains Mono](https://www.jetbrains.com/lp/mono/)

---

**Stay focused, level up, and achieve your goals! 🚀**
```
