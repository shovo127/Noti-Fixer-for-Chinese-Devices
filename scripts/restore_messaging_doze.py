#!/usr/bin/env python3
"""
Restore Messaging Apps Doze Whitelist & Screen Wake
Restores full background push socket reception, screen wake, and audible notification chimes
for WhatsApp, Messenger, IMO, Gmail, and SMS.
"""

import subprocess
import sys

COMM_PKGS = [
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

def get_device():
    res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip() and not l.startswith("*") and not l.startswith("List")]
    for l in lines:
        parts = l.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None

def run_cmd(serial, args):
    cmd = ["adb", "-s", serial] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def apply_fix(serial):
    print(f"[*] Applying messaging push & wake fix to device: {serial}")
    
    # 1. Screen Wake for Notifications
    print("  -> Enabling wake screen for notifications in system & secure settings...")
    run_cmd(serial, ["shell", "settings", "put", "secure", "wake_on_notification", "1"])
    run_cmd(serial, ["shell", "settings", "put", "system", "wake_on_notification", "1"])
    run_cmd(serial, ["shell", "settings", "put", "global", "wake_on_notification", "1"])

    # 2. Whitelist every communication app in Android Doze
    for pkg in COMM_PKGS:
        print(f"  -> Whitelisting {pkg} from Doze & enabling wake permissions...")
        run_cmd(serial, ["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"])
        run_cmd(serial, ["shell", "am", "set-standby-bucket", pkg, "5"]) # Bucket 5 = ACTIVE
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"])
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"])
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"])
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "TURN_SCREEN_ON", "allow"])
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "10020", "allow"]) # Lockscreen display
        run_cmd(serial, ["shell", "cmd", "appops", "set", pkg, "10017", "allow"]) # Floating notifications

    # 3. Ensure valid notification sound URI is set
    run_cmd(serial, ["shell", "settings", "put", "system", "notification_sound", "content://media/internal/audio/media/25?title=Fresh&canonical=1"])
    run_cmd(serial, ["shell", "settings", "put", "system", "notification_sound_cache", "content://media/internal/audio/media/25?title=Fresh&canonical=1"])

    print("[+] All messaging suites are now fully whitelisted, unthrottled, and allowed to wake screen and play sound!")

if __name__ == "__main__":
    serial = sys.argv[1] if len(sys.argv) > 1 else get_device()
    if not serial:
        print("[-] No device connected. Please provide serial or connect via adb connect <IP>:<PORT>")
        sys.exit(1)
    apply_fix(serial)

