#!/system/bin/sh
# ==============================================================================
# Noti-Fixer for Chinese Devices
# HyperOS / MIUI MILLET, AppOps & Alarm Protection Persistent Watchdog Daemon
# Author: Mohammed Thuhidul Islam Shovo (shovo127)
# License: MIT License (Copyright (c) 2026)
# ==============================================================================

# Detach completely from parent terminal/ADB session signals
trap '' HUP INT TERM CHLD PIPE

LOG_FILE="/data/local/tmp/millet_watchdog.log"
MAX_LOG_LINES=500
POLL_INTERVAL=60

# Core communication and alarm packages required to never freeze and never drop alerts
COMM_PACKAGES="com.google.android.gms,com.google.android.gsf,com.google.android.gm,com.android.vending,com.android.providers.downloads,com.whatsapp,com.whatsapp.w4b,com.imo.android.imoim,com.facebook.orca,com.instagram.android,org.telegram.messenger,org.telegram.plus,org.thoughtcrime.securesms,com.tencent.mm,com.discord,com.microsoft.office.outlook,com.viber.voip,com.skype.raider"
ALARM_PACKAGES="com.android.deskclock,com.google.android.deskclock,com.android.providers.calendar"

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
log_msg "Noti-Fixer MILLET & Alarm Watchdog Started [PID: $$]"
log_msg "Safe mode: Hardware suspend preserved, 0% idle battery drain"
log_msg "========================================================="

# 1. Enforce optimal hardware radios & deep sleep (prevents overnight battery drain)
settings put global wifi_suspend_optimizations_enabled 1 2>/dev/null
settings put global cached_apps_freezer enabled 2>/dev/null
device_config put activity_manager_native_boot use_freezer true 2>/dev/null
device_config put activity_manager max_phantom_processes 32 2>/dev/null

# Clean up any aggressive 120s FCM heartbeat overrides (allow native adaptive keepalive)
settings delete global fcm_heartbeat_interval_wifi_ms 2>/dev/null
settings delete global fcm_heartbeat_interval_mobile_ms 2>/dev/null
settings delete secure fcm_heartbeat_interval_wifi_ms 2>/dev/null
settings delete secure fcm_heartbeat_interval_mobile_ms 2>/dev/null
settings delete global gservices:fcm_heartbeat_interval_wifi_ms 2>/dev/null
settings delete global gservices:fcm_heartbeat_interval_mobile_ms 2>/dev/null

while true; do
    # 1. Inspect current MILLET whitelist for communication apps
    current_millet=$(settings get system MILLET_NO_RESTRICT_APP 2>/dev/null)
    
    case "$current_millet" in
        *"com.google.android.gms"*com.whatsapp*)
            ;;
        *)
            log_msg "[ALERT] MILLET_NO_RESTRICT_APP was wiped or reset by HyperOS PowerKeeper!"
            if [ -z "$current_millet" ] || [ "$current_millet" = "null" ]; then
                new_millet="$COMM_PACKAGES"
            else
                new_millet="${current_millet},${COMM_PACKAGES}"
            fi
            settings put system MILLET_NO_RESTRICT_APP "$new_millet" 2>/dev/null
            settings put system cloud_memory_freeze_whitelist "$COMM_PACKAGES" 2>/dev/null
            settings put system cloud_network_priority_whitelist "$COMM_PACKAGES" 2>/dev/null
            log_msg "[RESTORED] Re-injected messaging apps into MILLET & cloud whitelists."
            ;;
    esac

    # 2. Inspect PowerKeeper Alarm Whitelist (Crucial: prevents alarm failure in deep sleep)
    current_alarms=$(settings get system power_alarm_white_list 2>/dev/null)
    case "$current_alarms" in
        *"com.android.deskclock"*)
            ;;
        *)
            log_msg "[ALERT] power_alarm_white_list missing deskclock! Re-protecting alarm clock..."
            settings put system power_alarm_white_list "$ALARM_PACKAGES,myapplication,$COMM_PACKAGES" 2>/dev/null
            settings put system power_pkg_white_list "$ALARM_PACKAGES,com.google.android.inputmethod.latin,com.google.android.ext.services,com.android.camera,$COMM_PACKAGES" 2>/dev/null
            log_msg "[RESTORED] Alarm clock successfully whitelisted in PowerKeeper."
            ;;
    esac

    sleep $POLL_INTERVAL
done
