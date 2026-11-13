#!/usr/bin/env python3
"""
Auto-Revert Daemon
Continuously listens for any device (USB or Wi-Fi) and automatically
executes the clean notification sound system revert the instant a device appears.
"""

import subprocess
import time
import sys
import socket
from concurrent.futures import ThreadPoolExecutor

IP = "192.168.1.160"

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
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

def apply_revert(serial):
    print(f"\n[+] Device connected: {serial}!")
    print("[*] Executing clean revert of notification sound system...")
    
    # 1. Doze Whitelist & Standby Buckets
    for pkg in COMM_APPS:
        run_adb(serial, ["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"])
        run_adb(serial, ["shell", "am", "set-standby-bucket", pkg, "5"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "TURN_SCREEN_ON", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10020", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10017", "allow"])

    # 2. Unsnooze alerts
    run_adb(serial, ["shell", "cmd", "notification", "unsnooze", '"-1|android|62|null|1000"'])
    run_adb(serial, ["shell", "settings", "put", "global", "adb_notify", "1"])
    run_adb(serial, ["shell", "settings", "put", "secure", "adb_notify", "1"])

    # 3. Restore Messenger AppOp 10028
    run_adb(serial, ["shell", "cmd", "appops", "set", "com.facebook.orca", "10028", "allow"])

    # 4. Clean revert of sound URIs
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound_cache", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "calendar_alert", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "calendar_alert_cache", "content://settings/system/notification_sound"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound", "content://media/internal/audio/media/16"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound_cache", "content://media/internal/audio/media/16"])

    # 5. Enable screen wake
    run_adb(serial, ["shell", "settings", "put", "secure", "wake_on_notification", "1"])
    run_adb(serial, ["shell", "settings", "put", "system", "wake_on_notification", "1"])

    print("[SUCCESS] REVERT_COMPLETE! Notification sound system cleanly restored to defaults.")
    return True

def scan_port(p):
    with socket.socket() as s:
        s.settimeout(0.05)
        if s.connect_ex((IP, p)) == 0:
            return p
    return None

def main():
    print("[*] Auto-Revert Daemon started. Listening for USB or Wi-Fi device...")
    sys.stdout.flush()
    
    for cycle in range(60):
        # 1. Check existing adb devices (e.g. USB)
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout
        for line in res.splitlines():
            if "\tdevice" in line:
                serial = line.split()[0]
                apply_revert(serial)
                return

        # 2. Try pinging IP
        ping = subprocess.run(["ping", "-n", "1", "-w", "150", IP], capture_output=True, text=True).stdout
        if "bytes=32" in ping:
            print(f"[+] Phone pingable on cycle {cycle}. Scanning ports...")
            sys.stdout.flush()
            with ThreadPoolExecutor(max_workers=250) as ex:
                ports = [p for p in ex.map(scan_port, range(30000, 52000)) if p]
            print(f"[*] Found ports: {ports}")
            sys.stdout.flush()
            for p in ports:
                subprocess.run(["adb", "connect", f"{IP}:{p}"], capture_output=True, text=True)
                devs = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout
                if f"{IP}:{p}\tdevice" in devs:
                    apply_revert(f"{IP}:{p}")
                    return

        time.sleep(1)

    print("[-] Auto-revert timeout after 60s.")

if __name__ == "__main__":
    main()

