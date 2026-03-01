#!/bin/bash
# Google Colab Build Script for Clash AI Trainer APK

# 1. Install dependencies
pip install --upgrade pip
pip install buildozer
pip install cython==0.29.33

# 2. Install Android SDK/NDK dependencies
sudo apt-get install -y \
    build-essential \
    libffi-dev \
    gettext \
    libltdl-dev \
    libtool \
    pkg-config \
    zlib1g-dev \
    git \
    python3-dev \
    python3-setuptools \
    libncurses5 \
    libstdc++6 \
    libtinfo5 \
    cmake \
    ant \
    openjdk-11-jdk

# 3. Build the APK
# Note: You will need to accept the Android SDK licenses during the first run.
# This command will take 15-30 minutes.
buildozer android debug

# 4. (Optional) Download the APK
# from google.colab import files
# files.download('bin/*.apk')
