#!/system/bin/sh
# ==============================================================================
# Noti-Fixer for Chinese Devices
# HyperOS / MIUI MILLET & FCM Persistent Watchdog Daemon
# Author: Mohammed Thuhidul Islam Shovo (shovo127)
# License: MIT License (Copyright (c) 2026)
# ==============================================================================

LOG_FILE="/data/local/tmp/millet_watchdog.log"
MAX_LOG_LINES=500
POLL_INTERVAL=15

# Core packages required to never freeze
CRITICAL_PACKAGES="com.google.android.gms,com.google.android.gsf,com.whatsapp,org.telegram.messenger,com.facebook.orca,com.google.android.gm,org.thoughtcrime.securesms,com.tencent.mm,com.instagram.android,com.discord,com.microsoft.office.outlook"

log_msg() {
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" >> "$LOG_FILE"
    
    # Rotate log if too big
    lines_count=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$lines_count" -gt "$MAX_LOG_LINES" ]; then
        tail -n 200 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
}

log_msg "========================================================="
log_msg "Noti-Fixer MILLET Watchdog Daemon Started [PID: $$]"
log_msg "Targeting persistent FCM & HyperOS socket preservation"
log_msg "========================================================="

# Initial socket freezer kill
device_config put activity_manager_native_boot use_freezer false 2>/dev/null
setprop persist.sys.freezer false 2>/dev/null

counter=0

while true; do
    # 1. Inspect current MILLET whitelist
    current_millet=$(settings get system MILLET_NO_RESTRICT_APP 2>/dev/null)
    
    # Check if Google Play Services is missing
    case "$current_millet" in
        *"com.google.android.gms"*)
            # Whitelist intact
            ;;
        *)
            log_msg "[ALERT] MILLET_NO_RESTRICT_APP was wiped or reset by HyperOS PowerKeeper!"
            # Merge and re-inject
            if [ -z "$current_millet" ] || [ "$current_millet" = "null" ]; then
                new_millet="$CRITICAL_PACKAGES"
            else
                new_millet="${current_millet},${CRITICAL_PACKAGES}"
            fi
            settings put system MILLET_NO_RESTRICT_APP "$new_millet" 2>/dev/null
            log_msg "[RESTORED] Re-injected critical packages into MILLET whitelist."
            ;;
    esac

    # 2. Every 2 minutes (8 loops of 15s), pulse FCM Heartbeat & verify freezer
    counter=$((counter + 1))
    if [ $counter -ge 8 ]; then
        counter=0
        # Re-enforce kernel freezer off
        freezer_state=$(device_config get activity_manager_native_boot use_freezer 2>/dev/null)
        if [ "$freezer_state" = "true" ]; then
            device_config put activity_manager_native_boot use_freezer false 2>/dev/null
            log_msg "[RE-APPLIED] Kernel Cgroup freezer was silently re-enabled; disabled it."
        fi

        # Send FCM keepalive heartbeat
        am broadcast -a com.google.android.intent.action.MCS_HEARTBEAT -p com.google.android.gms >/dev/null 2>&1
        log_msg "[HEARTBEAT] FCM Keepalive broadcast pulsed to Google Play Services."
    fi

    sleep $POLL_INTERVAL
done
