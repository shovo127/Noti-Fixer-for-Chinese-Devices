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
echo   [1] Full Automated 1-Click Notification Fix (Recommended)
echo   [2] Live Diagnostic Audit (FCM Socket, Android Doze, Kernel Freezer)
echo   [3] Device Fingerprint & Hardware/ROM Profile
echo   [4] Push & Start HyperOS MILLET Watchdog Daemon
echo   [5] Wireless ADB Port Scanner (Find new port after reboot)
echo   [6] Setup Circle to Search Companion (MiCTS Integration)
echo   [7] Revert Changes (Master 100%% Safe Rollback)
echo   [8] Exit
echo.
echo ==============================================================================
set /p choice="Enter choice [1-8]: "

if "%choice%"=="1" goto FIX
if "%choice%"=="2" goto AUDIT
if "%choice%"=="3" goto DETECT
if "%choice%"=="4" goto WATCHDOG
if "%choice%"=="5" goto SCAN
if "%choice%"=="6" goto CTS
if "%choice%"=="7" goto ROLLBACK
if "%choice%"=="8" exit /b 0

echo Invalid choice. Try again.
pause
goto MENU

:FIX
cls
echo [*] Checking ADB connection...
adb devices
echo.
echo [*] Applying Comprehensive Notification Fix...
python "%~dp0apply_notification_fix.py" --dns-adguard
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

:CTS
cls
call "%~dp0..\CircleToSearch\setup_cts.bat"
goto MENU

:ROLLBACK
cls
call "%~dp0..\templates\master_restore_template.bat"
goto MENU
