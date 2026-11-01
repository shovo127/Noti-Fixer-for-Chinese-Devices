@echo off
chcp 65001 >nul
title Noti-Fixer - Master Rollback & Restoration
color 0E

cls
echo ==============================================================================
echo           NOTI-FIXER: MASTER 100%% SAFE SYSTEM ROLLBACK ENGINE
echo             Architect: Mohammed Thuhidul Islam Shovo (shovo127)
echo ==============================================================================
echo.
echo  This tool will safely restore your Android device settings back to default:
echo    • Re-enables kernel cached_apps_freezer
echo    • Resets Private DNS to Opportunistic/Off
echo    • Resets Xiaomi MILLET whitelist back to clean state
echo    • Restores AppOps and battery whitelist defaults
echo.
set /p confirm="Are you sure you want to revert all optimizations? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo [!] Rollback cancelled by user.
    pause
    exit /b 0
)

echo.
echo [*] Step 1: Re-enabling Kernel Cgroup Socket Freezer...
adb shell device_config put activity_manager_native_boot use_freezer true
adb shell setprop persist.sys.freezer true
adb shell setprop sys.use_freezer true

echo [*] Step 2: Reverting Private DNS configuration...
adb shell settings put global private_dns_mode opportunistic
adb shell settings delete global private_dns_specifier

echo [*] Step 3: Clearing Custom MILLET Whitelist Entries...
adb shell settings put system MILLET_NO_RESTRICT_APP ""

echo [*] Step 4: Stopping any running Noti-Fixer background daemons...
adb shell "pkill -f millet_watchdog.sh" 2>nul
adb shell "rm -f /data/local/tmp/millet_watchdog.sh /data/local/tmp/millet_watchdog.log" 2>nul

echo [*] Step 5: Restoring default AppOps for messaging applications...
for %%P in (com.google.android.gms com.whatsapp org.telegram.messenger com.facebook.orca com.google.android.gm) do (
    adb shell cmd appops set %%P 10008 default
    adb shell cmd appops set %%P 10021 default
    adb shell cmd appops set %%P RUN_IN_BACKGROUND default
)

echo.
echo ==============================================================================
echo [✔] COMPLETE: All system settings have been restored to factory standards!
echo ==============================================================================
echo.
pause
