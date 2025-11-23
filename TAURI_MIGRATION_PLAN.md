# Tauri Migration Plan

## Overview
Migrate AI Study Tracker from PWA to Tauri for a true native macOS app experience.

## Why Tauri?
- **Small bundle size**: ~10MB vs 700MB (PyInstaller)
- **Native permissions**: Proper camera/mic dialogs
- **Modern**: Built with Rust, extremely fast
- **Python-friendly**: Easy IPC with Flask backend

## Migration Steps

### Phase 1: Setup (Week 1)
1. Install Tauri CLI
   ```bash
   cargo install tauri-cli
   ```

2. Initialize Tauri project
   ```bash
   cd ai_study_tracker
   cargo tauri init
   ```

3. Configure `tauri.conf.json`:
   - Set app name, identifier
   - Add camera/mic permissions
   - Configure window size (480x700)
   - Enable always-on-top

### Phase 2: Integration (Week 2)
1. Keep existing Flask backend (no changes needed!)
2. Update frontend to use Tauri APIs:
   - Replace Web Speech API with Tauri's native speech recognition
   - Use Tauri's window management for HUD features

3. Configure IPC:
   - Tauri frontend ↔ Python Flask backend
   - Use localhost communication (same as now)

### Phase 3: Build & Test (Week 3)
1. Build macOS app:
   ```bash
   cargo tauri build
   ```

2. Test permissions flow
3. Test all features (camera, voice, tracking)

### Phase 4: Distribution
1. Code sign the app (optional, for distribution)
2. Create DMG installer
3. Distribute to users

## Estimated Timeline
- **Total**: 3-4 weeks
- **Complexity**: Medium (mostly configuration)
- **Benefit**: Professional, distributable macOS app

## Resources
- [Tauri Docs](https://tauri.app)
- [Tauri + Python Guide](https://tauri.app/v1/guides/getting-started/setup/sidecar)
