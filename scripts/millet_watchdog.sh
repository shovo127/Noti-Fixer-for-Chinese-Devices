#!/system/bin/sh
# ==============================================================================
# Noti-Fixer for Chinese Devices
# HyperOS / MIUI MILLET, AppOps & FCM Persistent Watchdog Daemon
# Author: Mohammed Thuhidul Islam Shovo (shovo127)
# License: MIT License (Copyright (c) 2026)
# ==============================================================================

# Detach completely from parent terminal/ADB session signals
trap '' HUP INT TERM CHLD PIPE

LOG_FILE="/data/local/tmp/millet_watchdog.log"
MAX_LOG_LINES=500
POLL_INTERVAL=20

# Core packages required to never freeze and never drop alerts
CRITICAL_PACKAGES="com.google.android.gms,com.google.android.gsf,com.google.android.gm,com.android.vending,com.android.providers.downloads,us.zoom.videomeetings,com.whatsapp,com.whatsapp.w4b,com.imo.android.imoim,com.facebook.orca,com.instagram.android,org.telegram.messenger,org.telegram.plus,org.thoughtcrime.securesms,com.tencent.mm,com.discord,com.microsoft.office.outlook,com.bKash.customerapp,com.konasl.nagad"

log_msg() {
    timestamp=$(date "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "uptime:$(cat /proc/uptime 2>/dev/null)")
    echo "[$timestamp] $1" >> "$LOG_FILE"
    
    # Rotate log if too big
    lines_count=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$lines_count" -gt "$MAX_LOG_LINES" ]; then
        tail -n 200 "$LOG_FILE" > "${LOG_FILE}.tmp" 2>/dev/null && mv "${LOG_FILE}.tmp" "$LOG_FILE" 2>/dev/null
    fi
}

log_msg "========================================================="
log_msg "Noti-Fixer MILLET & FCM Persistent Daemon Started [PID: $$]"
log_msg "Targeting socket preservation, AppOps & FCM NAT keepalive"
log_msg "========================================================="

# Initial socket freezer kill & FCM NAT interval enforcement
settings put global cached_apps_freezer disabled 2>/dev/null
device_config put activity_manager_native_boot use_freezer false 2>/dev/null
setprop persist.sys.freezer false 2>/dev/null
setprop sys.use_freezer false 2>/dev/null

settings put global fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
settings put global fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
settings put secure fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
settings put secure fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
settings put global gservices:fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
settings put global gservices:fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
settings put global wifi_suspend_optimizations_enabled 0 2>/dev/null
device_config put activity_manager max_phantom_processes 2147483647 2>/dev/null

counter=0

while true; do
    # 1. Inspect current MILLET whitelist
    current_millet=$(settings get system MILLET_NO_RESTRICT_APP 2>/dev/null)
    
    # Check if Google Play Services, Play Store or target apps are missing
    case "$current_millet" in
        *"com.google.android.gms"*com.android.vending*)
            ;;
        *)
            log_msg "[ALERT] MILLET_NO_RESTRICT_APP was wiped or reset by HyperOS PowerKeeper!"
            if [ -z "$current_millet" ] || [ "$current_millet" = "null" ]; then
                new_millet="$CRITICAL_PACKAGES"
            else
                new_millet="${current_millet},${CRITICAL_PACKAGES}"
            fi
            settings put system MILLET_NO_RESTRICT_APP "$new_millet" 2>/dev/null
            settings put system cloud_memory_freeze_whitelist "$CRITICAL_PACKAGES" 2>/dev/null
            settings put system cloud_network_priority_whitelist "$CRITICAL_PACKAGES" 2>/dev/null
            settings put system power_pkg_white_list "com.google.android.inputmethod.latin,com.google.android.ext.services,com.android.camera,$CRITICAL_PACKAGES" 2>/dev/null
            log_msg "[RESTORED] Re-injected critical packages into MILLET & PowerKeeper whitelists."
            ;;
    esac

    # 2. Every 2 minutes (6 loops of 20s), enforce FCM Heartbeat, Wi-Fi suspend, and pulse keepalive
    counter=$((counter + 1))
    if [ $counter -ge 6 ]; then
        counter=0
        settings put global cached_apps_freezer disabled 2>/dev/null
        device_config put activity_manager_native_boot use_freezer false 2>/dev/null
        
        settings put global fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
        settings put global fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
        settings put secure fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
        settings put secure fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
        settings put global gservices:fcm_heartbeat_interval_wifi_ms 120000 2>/dev/null
        settings put global gservices:fcm_heartbeat_interval_mobile_ms 120000 2>/dev/null
        settings put global wifi_suspend_optimizations_enabled 0 2>/dev/null
device_config put activity_manager max_phantom_processes 2147483647 2>/dev/null

        # Send FCM keepalive heartbeat broadcasts
        am broadcast -a com.google.android.intent.action.MCS_HEARTBEAT -p com.google.android.gms >/dev/null 2>&1
        am broadcast -a com.google.android.c2dm.intent.RECEIVE -p com.google.android.gms >/dev/null 2>&1
        log_msg "[HEARTBEAT] FCM Keepalive broadcast pulsed to Google Play Services."
    fi

    sleep $POLL_INTERVAL
done
