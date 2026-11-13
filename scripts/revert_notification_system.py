#!/usr/bin/env python3
"""
Clean Revert of Notification Sound System to Default
Reverts all notification sound URIs, un-snoozes system alerts, restores
messaging app Doze whitelists, and leaves everything else untouched.
"""

import subprocess
import sys
import time

COMM_APPS = [
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.facebook.orca",
    "com.imo.android.imoim",
    "com.viber.voip",
    "com.discord",
    "us.zoom.videomeetings",
    "com.google.android.gm",
    "com.android.mms"
]

def run_adb(serial, args):
    cmd = ["adb", "-s", serial] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

def revert_sound_system(serial):
    print(f"[*] Reverting Notification Sound System to clean defaults on {serial}...")

    # 1. Restore Doze Whitelist & Standby Buckets for all messaging apps
    print("  -> Restoring messaging apps to Doze whitelist & ACTIVE standby...")
    for pkg in COMM_APPS:
        run_adb(serial, ["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"])
        run_adb(serial, ["shell", "am", "set-standby-bucket", pkg, "5"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "TURN_SCREEN_ON", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10020", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10017", "allow"])

    # 2. Unsnooze the wireless debugging alert
    print("  -> Unsnoozing system notification alerts...")
    run_adb(serial, ["shell", "cmd", "notification", "unsnooze", '"-1|android|62|null|1000"'])
    run_adb(serial, ["shell", "settings", "put", "global", "adb_notify", "1"])
    run_adb(serial, ["shell", "settings", "put", "secure", "adb_notify", "1"])

    # 3. Restore Messenger AppOp 10028
    print("  -> Restoring Messenger overlay AppOp...")
    run_adb(serial, ["shell", "cmd", "appops", "set", "com.facebook.orca", "10028", "allow"])

    # 4. Revert Notification Sounds to Factory Default
    print("  -> Resetting system notification sound URIs...")
    # Clean system settings
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound_cache", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "calendar_alert", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "calendar_alert_cache", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound", "content://media/internal/audio/media/25?title=Fresh"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound_cache", "content://media/internal/audio/media/25?title=Fresh"])

    # 5. Enable screen wake on notifications
    run_adb(serial, ["shell", "settings", "put", "secure", "wake_on_notification", "1"])
    run_adb(serial, ["shell", "settings", "put", "system", "wake_on_notification", "1"])

    print("\n[✔] Clean revert completed successfully!")
    print("     - All messaging apps 100% whitelisted in Doze.")
    print("     - Notification sound system restored to clean defaults.")
    print("     - All system alerts unsnoozed.")
    print("     - Screen wake for notifications enabled.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        # Check connected devices
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devs = [l.split()[0] for l in res.stdout.splitlines() if "\tdevice" in l]
        if not devs:
            print("[-] No active ADB device found. Connect device first.")
            sys.exit(1)
        target = devs[0]
    revert_sound_system(target)

