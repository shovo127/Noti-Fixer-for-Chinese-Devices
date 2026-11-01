@echo off
chcp 65001 >nul
title Circle to Search Setup Companion - by Shovo
color 0A

cls
echo ==============================================================================
echo        CIRCLE TO SEARCH (CTS) COMPANION CONFIGURATOR FOR CHINESE ROMS
echo             Architect: Mohammed Thuhidul Islam Shovo (shovo127)
echo ==============================================================================
echo.
echo   This companion sets up Google Circle to Search / Lens trigger on Xiaomi,
echo   Vivo, Oppo, and OnePlus devices that lack native Pixel/Samsung CTS gestures.
echo.
echo   Requirements:
echo    1. Google App installed and updated from Google Play Store.
echo    2. Device connected via ADB.
echo.
echo ==============================================================================
set /p confirm="Proceed with Circle to Search configuration? (Y/N): "
if /i not "%confirm%"=="Y" exit /b 0

echo.
echo [*] Checking connected ADB device...
adb get-state >nul 2>&1
if errorlevel 1 (
    echo [!] No device detected. Connect via USB or Wireless ADB and retry.
    pause
    exit /b 1
)

echo [*] Granting Secure Settings permissions to Google Assistant & MiCTS...
adb shell pm grant com.google.android.googlequicksearchbox android.permission.BIND_VOICE_INTERACTION 2>nul
adb shell pm grant com.google.android.googlequicksearchbox android.permission.CAPTURE_AUDIO_HOTWORD 2>nul

if exist "%~dp0MiCTS_2.6.apk" (
    echo [*] Installing MiCTS Companion Engine...
    adb install -r -d "%~dp0MiCTS_2.6.apk"
    adb shell pm grant com.parallelcc.micts android.permission.WRITE_SECURE_SETTINGS 2>nul
    adb shell pm grant com.parallelcc.micts android.permission.DUMP 2>nul
    adb shell cmd appops set com.parallelcc.micts SYSTEM_ALERT_WINDOW allow 2>nul
    adb shell cmd appops set com.parallelcc.micts 10008 allow 2>nul
    adb shell cmd appops set com.parallelcc.micts 10021 allow 2>nul
) else (
    echo [i] MiCTS binary helper: Optional companion APK can be staged directly in this folder.
)

echo [*] Configuring Default Assist App to Google Omnient Voice / Search...
adb shell settings put secure assistant com.google.android.googlequicksearchbox/com.google.android.apps.search.assistant.surfaces.voice.OmnientActivity 2>nul
adb shell settings put secure voice_interaction_service com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService 2>nul

echo.
echo ==============================================================================
echo [✔] CIRCLE TO SEARCH CONFIGURED!
echo.
echo  Usage on HyperOS / OriginOS / ColorOS:
echo   • Long-press Home button or Navigation Bar pill to trigger Omnient Search.
echo   • Add the "Circle to Search" tile to your Quick Settings pull-down.
echo ==============================================================================
echo.
pause
