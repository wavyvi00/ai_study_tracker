# 🧠 AI Study Tracker

A gamified productivity tracker that monitors your computer activity and rewards you for staying focused. Built with Flask, Python, and native macOS integration.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.8+-green)

## ✨ Features

- **🎮 Gamification System**: Earn XP, level up, and maintain your health by staying focused
- **📊 Real-time Activity Tracking**: Automatically detects what application you're using
- **💚 Health System**: Your health decreases when distracted and regenerates while studying
- **⏱️ Study Timer**: Tracks total study time with a clean, formatted display
- **🖥️ Native Desktop App**: Beautiful native window using pywebview
- **🎨 Modern UI**: Sleek dark mode interface with smooth animations
- **🔒 Privacy-First**: All data stored locally in `study_data.json`

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

### Rewards System
- **+1 XP per second** of studying
- **Level up** every 100 XP
- **Health regenerates** slowly while studying (+0.1/sec)
- **Health decreases** when distracted (-0.5/sec)

## ⚡ Quick Start (No Python Required)

### For Users - Download & Run

1. **Download the standalone app** (when available)
   - Get `AI Study Tracker.app` from releases

2. **First launch**
   - Double-click `AI Study Tracker.app`
   - If macOS blocks it: Right-click → Open
   - Or: System Settings → Privacy & Security → "Open Anyway"

3. **Grant permissions**
   - System Settings → Privacy & Security → Screen Recording
   - Enable Terminal or Python
   - Restart the app

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
- Install all dependencies
- Set up the development environment

Then run:
```bash
source venv/bin/activate
python3 desktop_app.py
```

---

## 🚀 Getting Started (Manual Installation)

### Prerequisites

- macOS (uses Quartz for window tracking)
- Python 3.8 or higher
- Screen Recording permissions (required for window tracking)

### Installation

**Option A: Automated Setup (Recommended)**

```bash
./setup.sh
```

**Option B: Manual Setup**

1. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Grant Screen Recording permissions**
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
ai_study_tracker/
├── app.py              # Flask application and API routes
├── desktop_app.py      # Native desktop window launcher
├── tracker.py          # Window tracking and activity classification
├── gamification.py     # XP, leveling, and health system
├── requirements.txt    # Python dependencies
├── setup.sh            # Development setup script
├── build.sh            # Standalone app build script
├── study_data.json     # Persistent user data (gitignored)
├── templates/
│   └── index.html      # Main UI template
├── static/
│   ├── style.css       # Modern dark theme styling
│   └── script.js       # Real-time UI updates
├── dist/               # Built standalone app (gitignored)
│   └── AI Study Tracker.app
└── venv/               # Virtual environment (gitignored)
```

## 🔧 Configuration

### Customizing Study/Distraction Keywords

Edit `tracker.py` to modify what counts as studying:

```python
self.study_keywords = ['code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', ...]
self.distraction_keywords = ['youtube', 'twitter', 'reddit', 'facebook', ...]
```

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

Then open `http://127.0.0.1:5001` in your browser.

### API Endpoints

- `GET /` - Main application UI
- `GET /api/status` - Returns current tracking state (JSON)

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
  "has_permissions": true
}
```

## 📝 Future Enhancements

Potential features to add:
- [ ] Daily/weekly statistics dashboard
- [ ] Streak tracking and rewards
- [ ] Custom study goals and milestones
- [ ] Break reminders and Pomodoro integration
- [ ] Export data to CSV/JSON
- [ ] Multi-platform support (Windows, Linux)
- [ ] Achievements and badges system
- [ ] Focus mode with website blocking

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for personal use.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Native window via [pywebview](https://pywebview.flowrl.com/)
- macOS integration using [PyObjC](https://pyobjc.readthedocs.io/)
- UI fonts: [Inter](https://rsms.me/inter/) & [JetBrains Mono](https://www.jetbrains.com/lp/mono/)

---

**Stay focused, level up, and achieve your goals! 🚀**
