#!/bin/bash

# Android Lagger VPN - Google Colab Build Script
# This script installs the Android SDK, creates the project structure, and builds the APK.

echo "[1/4] Installing Android SDK and Build Tools..."
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk wget unzip
mkdir -p $HOME/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip -O cmdline-tools.zip
unzip cmdline-tools.zip -d $HOME/android-sdk/cmdline-tools
mv $HOME/android-sdk/cmdline-tools/cmdline-tools $HOME/android-sdk/cmdline-tools/latest

export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

echo "yes" | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

echo "[2/4] Initializing Gradle Wrapper..."
gradle wrapper --gradle-version 8.2.2

echo "[3/4] Building APK..."
chmod +x gradlew
./gradlew assembleRelease

echo "[4/4] Build Complete!"
APK_PATH=$(find . -name "*.apk" | grep release)
if [ -z "$APK_PATH" ]; then
    echo "Error: APK not found."
    exit 1
else
    echo "Final APK path: $APK_PATH"
fi
