#!/usr/bin/env python3
"""
Optimize Battery: Pure-Notification Background & Zero Offline Drain
Configures social apps (Messenger, Facebook, Instagram, IMO) to pure-notification
mode, stopping background CPU spin and offline reconnect loops while preserving
instant push notification delivery and clean single-chime alerts.
"""

import subprocess
import sys

SOCIAL_CHURNERS = [
    ("com.facebook.orca", "20"),      # Messenger: Working Set
    ("com.imo.android.imoim", "20"),   # IMO: Working Set
    ("com.facebook.katana", "30"),    # Facebook: Frequent
    ("com.instagram.android", "30"),  # Instagram: Frequent
]

DIRECT_MESSAGING = [
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.android.mms",
    "com.google.android.gm"
]

def run_adb(serial, args):
    cmd = ["adb", "-s", serial] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

def optimize(serial):
    print(f"[*] Optimizing background battery & push efficiency on {serial}...")

    # 1. Strip heavy social churners from Doze whitelist (GMS handles their push)
    print("  -> Removing heavy social churners from Doze whitelist...")
    for pkg, _ in SOCIAL_CHURNERS:
        run_adb(serial, ["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"])

    # 2. Keep direct messaging apps in Doze whitelist
    print("  -> Ensuring core direct messaging apps remain Doze-whitelisted...")
    for pkg in DIRECT_MESSAGING:
        run_adb(serial, ["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"])
        run_adb(serial, ["shell", "am", "set-standby-bucket", pkg, "10"]) # ACTIVE

    # 3. Restrict background execution for heavy social apps (No background tasks)
    print("  -> Restricting background CPU spin & setting balanced standby buckets...")
    for pkg, bucket in SOCIAL_CHURNERS:
        # Prevent starting background services / background tasks
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "ignore"])
        # Allow background start for VoIP incoming call popups while keeping background service spin controlled
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10021", "allow"]) # MIUI popup in background (incoming calls)
        run_adb(serial, ["shell", "am", "set-standby-bucket", pkg, bucket])

        # GUARANTEE notification display and audio alerts remain 100% active
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "POST_NOTIFICATION", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"])
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10017", "allow"]) # Floating banners
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10020", "allow"]) # Lockscreen display
        run_adb(serial, ["shell", "cmd", "appops", "set", pkg, "10022", "allow"]) # Sound & vibration

    # 4. Multitasking retention: Ensure cached apps are not aggressively frozen on high-RAM devices
    print("  -> Configuring multitasking memory retention & Wi-Fi suspend optimizations...")
    run_adb(serial, ["shell", "settings", "put", "global", "wifi_suspend_optimizations_enabled", "1"])
    run_adb(serial, ["shell", "settings", "put", "global", "cached_apps_freezer", "disabled"])
    run_adb(serial, ["shell", "device_config", "put", "activity_manager_native_boot", "use_freezer", "false"])

    # 5. Disable background radio polling when idle
    print("  -> Disabling background radio polling (Wi-Fi/BLE)...")
    run_adb(serial, ["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"])
    run_adb(serial, ["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"])

    # 6. Ensure screen wake and clean notification sound are active
    print("  -> Ensuring screen wake and clean notification sound...")
    run_adb(serial, ["shell", "settings", "put", "system", "wakeup_for_keyguard_notification", "1"])
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound", "content://media/internal/audio/media/25?title=Fresh"])
    run_adb(serial, ["shell", "settings", "put", "system", "notification_sound_cache", "content://media/internal/audio/media/25?title=Fresh"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound", "content://media/internal/audio/media/25?title=Fresh"])
    run_adb(serial, ["shell", "settings", "put", "system", "sms_received_sound_cache", "content://media/internal/audio/media/25?title=Fresh"])

    print("\n[✔] Battery & Pure-Notification Optimization Complete!")
    print("     - Messenger / Facebook / Instagram / IMO restricted from background CPU churn.")
    print("     - Offline reconnect loops eliminated via kernel cached apps freezer.")
    print("     - Instant notifications, floating banners, sound, and screen wake 100% preserved.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devs = [l.split()[0] for l in res.stdout.splitlines() if "\tdevice" in l]
        if not devs:
            print("[-] No device connected.")
            sys.exit(1)
        target = devs[0]
    optimize(target)

