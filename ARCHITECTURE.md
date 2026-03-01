# Clash AI Overlay Architecture Summary

## 1. Frontend (main.py)
- **Framework**: Kivy with `ScreenManager`.
- **Tutorial**: Multi-screen introduction to guide the user through permissions and service activation.
- **Auto-Fetch**: Automatically downloads `cards.json` from RoyaleAPI on startup if not present locally.
- **Permissions**: Requests `SYSTEM_ALERT_WINDOW` (Overlay) and `MediaProjection` (Screen Capture) via Android Intents (using `pyjnius`).

## 2. Background Service (service.py)
- **Type**: Android Foreground Service to prevent being killed by the OS.
- **Overlay**: Uses `pyjnius` to access `WindowManager` and create a `FLAG_NOT_TOUCHABLE` native overlay.
- **Vision**: Uses OpenCV for lightweight template matching on the screen capture stream (from `MediaProjection`).
- **Logic**: Integrates `UtilityBrain` to evaluate detected threats against the current hand and elixir.
- **Rendering**: Draws Kivy Canvas shapes (Green Zones) on the transparent overlay to guide the user.

## 3. Evaluation Engine (utility_brain.py)
- **Utility-Based AI**: Scores cards based on:
    - **Elixir Trade**: Favoring positive trades.
    - **Type Matching**: Air vs Ground, etc.
    - **Trait Counters**: Swarm vs Single Target, Splash vs Swarm.
- **Placement Zones**: Returns abstract zones (`CENTER_KITE`, `BRIDGE_BLOCK`, etc.) which are mapped to screen coordinates by the UI layer.

## 4. Compilation (Buildozer)
- **Target**: Android APK.
- **Requirements**: Python 3, Kivy, Pyjnius, OpenCV-headless.
- **Build Environment**: Recommended to use the provided Google Colab script for a clean environment.
