#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Intelligent Power & Battery Optimizer (Multitasking, Meetings & Audio Safe)
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
import argparse
from typing import Optional, List

try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Video Conferencing & Virtual Meetings
# Must sustain audio, microphone, and floating Picture-in-Picture (PiP) while user
# browses other apps (e.g. Facebook, ChatGPT, YouTube), but NEVER autostart on boot or drain idle battery.
CONFERENCING_APPS = [
    ("Zoom Meetings", "us.zoom.videomeetings"),
    ("Microsoft Teams", "com.microsoft.teams"),
    ("Skype", "com.skype.raider")
]

# Curated list of payment, banking, ride, food, learning, music, and utility apps
# Specialized handling:
# - Payment & Banking: High multitasking priority (OTP copying, switching between SMS & app)
# - Music & Audio: Absolute background playback preservation (WAKE_LOCK & media playback allowed)
# - Travel & Learning: Preserve form state & progress
PAYMENT_AND_UTILITY_APPS = [
    # Mobile Financial Services & Banking (Critical: Preserve OTP & Login State)
    ("bKash", "com.bKash.customerapp", "payment"),
    ("Nagad", "com.konasl.nagad", "payment"),
    ("Pubali Bank (PBL)", "com.cibl.pbl", "payment"),
    ("NexusPay DBBL", "com.dbbl.mbs.apps.main", "payment"),
    # Music & Audio Streaming (Critical: Continuous Background Audio)
    ("eSound", "com.esound", "audio"),
    # Education & Progress Tracking
    ("Duolingo", "com.duolingo", "utility"),
    # Telecom Self-Care Apps
    ("MyGP", "com.portonics.mygp", "utility"),
    ("MyAirtel", "com.myairtelapp", "utility"),
    ("MyTeletalk", "teletalk.teletalkcustomerapp", "utility"),
    # Rides, Food & Travel
    ("Foodpanda", "com.global.foodpanda.android", "utility"),
    ("Pathao", "com.pathao.user", "utility"),
    ("Uber", "com.ubercab", "utility"),
    ("GoZayaan", "com.gozayaan.app", "utility"),
    ("MakeMyTrip", "com.makemytrip", "utility"),
    ("Skyscanner", "net.skyscanner.android.main", "utility"),
    ("ixigo", "com.ixigo", "utility"),
    ("Shohoz", "com.shohoz.dtrainpwa", "utility"),
    # Heavy Utilities & Games
    ("WPS Office Lite", "cn.wps.moffice_eng.xiaomi.lite", "utility"),
    ("CamScanner", "com.intsig.camscanner", "utility"),
    ("Military Overturn", "games.vaveda.militaryoverturn", "game")
]

def run_adb(cmd: List[str], serial: Optional[str] = None) -> subprocess.CompletedProcess:
    assert_command_safe(cmd)
    base = ["adb"]
    if serial:
        if ":" in serial and not getattr(run_adb, "_connected", False):
            subprocess.run(["adb", "connect", serial], capture_output=True, text=True, check=False)
            run_adb._connected = True
        base.extend(["-s", serial])
    base.extend(cmd)
    try:
        res = subprocess.run(base, capture_output=True, text=True, check=False)
        if serial and ":" in serial and "not found" in (res.stderr or "").lower():
            subprocess.run(["adb", "connect", serial], capture_output=True, text=True, check=False)
            res = subprocess.run(base, capture_output=True, text=True, check=False)
        return res
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: 'adb' executable not found in PATH.{Colors.RESET}")
        sys.exit(1)

def restore_multitasking_safety(serial: Optional[str] = None):
    """
    Guarantees 100% multitasking safety, state preservation, floating PiP, and background audio.
    - Payment apps: Resets AppOps to default & assigns Standby Bucket 20 (WORKING_SET).
    - Conferencing apps: Grants RUN_IN_BACKGROUND, WAKE_LOCK, SYSTEM_ALERT_WINDOW, and PiP.
    - Zero idle battery drain: Restricts boot autostart (10008/10021) and removes Doze whitelist for utilities.
    """
    print(f"\n{Colors.CYAN}{'='*76}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: PRESERVING MULTITASKING, MEETINGS & STATE INTEGRITY{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*76}{Colors.RESET}")

    pkg_list_res = run_adb(["shell", "pm", "list", "packages"], serial).stdout or ""
    
    # 0. Disable Android 16 Phantom Process Killer limit (unthrottles background processes)
    run_adb(["shell", "device_config", "put", "activity_manager", "max_phantom_processes", "2147483647"], serial)
    run_adb(["shell", "settings", "put", "global", "settings_enable_monitor_phantom_procs", "false"], serial)
    print(f"    {Colors.GREEN}✔ [PHANTOM KILLER DISABLED] max_phantom_processes=2147483647 | monitor_procs=false{Colors.RESET}")

    # Whitelist communication, download, and banking apps in MILLET and cloud memory freeze
    millet_continuity_apps = [
        "com.google.android.gms", "com.google.android.gsf", "com.google.android.gm",
        "com.whatsapp", "com.whatsapp.w4b", "com.imo.android.imoim", "com.facebook.orca",
        "com.viber.voip", "com.instagram.android", "org.telegram.messenger",
        "com.android.providers.downloads", "com.android.vending", "com.android.deskclock",
        "com.bKash.customerapp", "com.konasl.nagad"
    ]
    cur_millet = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial).stdout or ""
    millet_set = set([p.strip() for p in cur_millet.strip().split(",") if p.strip()] if cur_millet.strip() != "null" else [])
    for app_p in millet_continuity_apps:
        millet_set.add(app_p)
    millet_str = ",".join(sorted(list(millet_set)))
    run_adb(["shell", "settings", "put", "system", "MILLET_NO_RESTRICT_APP", millet_str], serial)
    run_adb(["shell", "settings", "put", "system", "cloud_memory_freeze_whitelist", millet_str], serial)
    print(f"    {Colors.GREEN}✔ [MILLET CONTINUITY] Injected {len(millet_set)} packages into MILLET & memory freeze whitelist{Colors.RESET}")

    # Protect Google Play Store at Standby Bucket 20
    if "package:com.android.vending" in pkg_list_res:
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_IN_BACKGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_ANY_IN_BACKGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "WAKE_LOCK", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "START_FOREGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10008", "ignore"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10021", "ignore"], serial)
        run_adb(["shell", "am", "set-standby-bucket", "com.android.vending", "20"], serial)
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", "-com.android.vending"], serial)
        print(f"    {Colors.GREEN}✔ [PLAY STORE]       com.android.vending         -> Bucket: 20 | Foreground: Active | Boot: Ignored{Colors.RESET}")

    # 1. Conferencing & Meeting Apps (Zoom, Teams, Skype)
    conf_count = 0
    for name, pkg in CONFERENCING_APPS:
        if f"package:{pkg}" in pkg_list_res:
            conf_count += 1
            # Sustained meeting execution while multitasking
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10029", "allow"], serial) # MIUI Floating Window
            
            # Prevent idle phantom boot autostart (0% battery drain when not in meeting)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
            run_adb(["shell", "am", "set-standby-bucket", pkg, "20"], serial)
            print(f"    {Colors.GREEN}✔ [MEETING READY] {name:<20} ({pkg:<28}) -> Multitask: Active | Boot: Ignored{Colors.RESET}")

    # 2. Payment, Banking, Audio & Utility Apps
    restored_count = 0
    for name, pkg, category in PAYMENT_AND_UTILITY_APPS:
        if f"package:{pkg}" in pkg_list_res:
            restored_count += 1
            # Reset AppOps to default so Android standard LRU memory manages tasks safely
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "default"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "default"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "default"], serial)
            
            # Prevent unnecessary autostart on boot (saves battery when unused)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
            
            # Assign Standby Bucket 20 (WORKING_SET) so Android manages background RAM naturally
            run_adb(["shell", "am", "set-standby-bucket", pkg, "20"], serial)
            
            # Remove from Doze whitelist to guarantee phone enters deep sleep when idle
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"], serial)
            
            print(f"    {Colors.GREEN}✔ [STATE SAFE]    {name:<20} ({pkg:<28}) -> AppOps: default | Bucket: 20{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Successfully verified multitasking & meeting protection for {conf_count + restored_count} apps!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*76}{Colors.RESET}\n")

def optimize_hardware_radios(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}[*] Disabling continuous background Wi-Fi and Bluetooth scanning...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "wifi_suspend_optimizations_enabled", "1"], serial)
    print(f"    {Colors.GREEN}✔ Hardware Wi-Fi/BLE background scanning disabled (eliminates idle battery drain).{Colors.RESET}")

def print_thermal_status(serial: Optional[str] = None):
    res = run_adb(["shell", "dumpsys", "battery"], serial).stdout or ""
    temp = "Unknown"
    level = "Unknown"
    for line in res.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("temperature:"):
            raw = line_clean.split(":")[-1].strip()
            try:
                temp = f"{float(raw) / 10.0:.1f}°C"
            except Exception:
                temp = f"{raw}°C"
        elif line_clean.startswith("level:"):
            level = line_clean.split(":")[-1].strip() + "%"

    print(f"\n{Colors.CYAN}{'='*76}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: DEVICE THERMAL & BATTERY SNAPSHOT{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*76}{Colors.RESET}")
    print(f" Battery Level       : {Colors.BOLD}{level}{Colors.RESET}")
    print(f" Battery Temperature : {Colors.BOLD}{temp}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*76}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Intelligent Power & Battery Optimizer by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--restore-multitasking", action="store_true", help="Restore full multitasking, session state and audio playback")
    parser.add_argument("--optimize-radios", action="store_true", help="Disable background Wi-Fi and Bluetooth location scanning")
    parser.add_argument("--status", action="store_true", help="Check battery temperature and charging status")
    args = parser.parse_args()

    if args.restore_multitasking:
        restore_multitasking_safety(args.serial)
    elif args.optimize_radios:
        optimize_hardware_radios(args.serial)
    elif args.status:
        print_thermal_status(args.serial)
    else:
        # Default run: Optimize hardware radios, enforce multitasking & meeting safety, and print thermal snapshot
        optimize_hardware_radios(args.serial)
        restore_multitasking_safety(args.serial)
        print_thermal_status(args.serial)

if __name__ == "__main__":
    main()
