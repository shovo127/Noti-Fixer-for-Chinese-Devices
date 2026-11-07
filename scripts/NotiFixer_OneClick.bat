@echo off
chcp 65001 >nul
title Noti-Fixer for Chinese Devices - by Shovo
color 0B

:MENU
cls
echo ==============================================================================
echo        NOTI-FIXER FOR CHINESE DEVICES - PRODUCTION REPAIR SUITE
echo             Architect: Mohammed Thuhidul Islam Shovo (shovo127)
echo                         Open-Source MIT License
echo ==============================================================================
echo.
echo   Targeting: Xiaomi HyperOS / MIUI | Vivo OriginOS | Oppo ColorOS | HarmonyOS
echo.
echo   [1] ⚡ Simple Wireless Wi-Fi Connect & Fix (No Cable Needed - Recommended)
echo   [2] 🔌 USB Cable 1-Click Notification & Battery Fix
echo   [3] 🔍 Live Diagnostic Audit (FCM Socket, Android Doze, Kernel Freezer)
echo   [4] 📱 Device Fingerprint & Hardware/ROM Profile
echo   [5] 🔋 Battery Drain Analysis & Culprit Inspector
echo   [6] 🛡️ Push & Start HyperOS MILLET Watchdog Daemon
echo   [7] 🔄 Wireless ADB Port Scanner (Find new port after reboot)
echo   [8] 🛠️ Fix Background App Freezing & Network Stalls (Play Store & Apps)
echo   [9] 🧹 Safe Bloatware & Ad Debloater (User-Profile Only - 100%% Reversible)
echo   [10] 🛡️ Zero-Latency Ad-Blocker Manager (Local Loopback & DNS Optimizer)
echo   [11] ⏪ Revert Changes (Master 100%% Safe Rollback & Reinstaller)
echo   [12] ❌ Exit
echo.
==============================================================================
set /p choice="Enter choice [1-12]: "

if "%choice%"=="1" goto WIRELESS
if "%choice%"=="2" goto FIX
if "%choice%"=="3" goto AUDIT
if "%choice%"=="4" goto DETECT
if "%choice%"=="5" goto BATTERY
if "%choice%"=="6" goto WATCHDOG
if "%choice%"=="7" goto SCAN
if "%choice%"=="8" goto UNFREEZE
if "%choice%"=="9" goto DEBLOAT
if "%choice%"=="10" goto ADBLOCK
if "%choice%"=="11" goto ROLLBACK
if "%choice%"=="12" exit /b 0

echo Invalid choice. Try again.
pause
goto MENU

:WIRELESS
cls
python "%~dp0connect_phone.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:FIX
cls
echo [*] Checking ADB connection...
adb devices
echo.
echo [*] Applying Comprehensive Notification Fix...
python "%~dp0apply_notification_fix.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:AUDIT
cls
echo [*] Running FCM Socket & Doze Audit...
python "%~dp0audit_fcm_doze.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:DETECT
cls
echo [*] Detecting Device Profile & ROM Subsystem...
python "%~dp0detect_device.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:BATTERY
cls
echo [*] Analyzing Live Battery Drain & Wakelocks...
python "%~dp0inspect_battery.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:WATCHDOG
cls
echo [*] Pushing millet_watchdog.sh to device /data/local/tmp/...
adb push "%~dp0millet_watchdog.sh" /data/local/tmp/millet_watchdog.sh
adb shell chmod +x /data/local/tmp/millet_watchdog.sh
echo [*] Starting daemon in background...
adb shell "nohup /data/local/tmp/millet_watchdog.sh >/dev/null 2>&1 &"
echo [✔] Daemon active! Monitoring MILLET resets every 15 seconds.
echo Press any key to return to menu...
pause >nul
goto MENU

:SCAN
cls
set /p target_ip="Enter your phone's Wi-Fi IP address (or press ENTER to auto-discover): "
if "%target_ip%"=="" (
    python "%~dp0scan_ports.py"
) else (
    python "%~dp0scan_ports.py" -ip %target_ip%
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:UNFREEZE
cls
echo [*] Restoring background app health and unblocking network...
python "%~dp0restore_background_health.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:DEBLOAT
cls
echo [*] Launching Safe User-Profile Bloatware & Ad Debloater...
python "%~dp0debloat_manager.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:ADBLOCK
cls
echo [*] Launching Zero-Latency Ad-Blocker & DNS Manager...
python "%~dp0adblock_manager.py" --status
echo.
echo Options:
echo   [1] Open Google Play Store to install RethinkDNS (0ms Local Loopback)
echo   [2] Optimize RethinkDNS Daemon (Grant Bucket 5 & Autostart)
echo   [3] Disable Slow Remote Private DNS (Restore 3-8ms ISP speed)
echo   [4] Return to Main Menu
echo.
set /p ad_choice="Enter choice [1-4]: "
if "%ad_choice%"=="1" python "%~dp0adblock_manager.py" --install-rethink
if "%ad_choice%"=="2" python "%~dp0adblock_manager.py" --optimize-rethink
if "%ad_choice%"=="3" python "%~dp0adblock_manager.py" --disable-slow-dns
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:ROLLBACK
cls
echo [*] Executing Master 100% Safe System Rollback & Package Restoration...
python "%~dp0restore_backup.py"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU
