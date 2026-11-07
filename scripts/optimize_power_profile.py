#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Intelligent Power & Battery Optimizer (Deep-Sleep Payment & Infrequent Apps)
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

# Curated list of payment, banking, ride, food, and heavy utility apps
# These apps are used on-demand; their background daemons are unnecessary
# and drain battery if left active in the background.
SLEEP_CANDIDATES = [
    # Mobile Financial Services & Banking
    ("bKash", "com.bKash.customerapp"),
    ("Nagad", "com.konasl.nagad"),
    ("Pubali Bank (PBL)", "com.cibl.pbl"),
    ("NexusPay DBBL", "com.dbbl.mbs.apps.main"),
    # Telecom Self-Care Apps
    ("MyGP", "com.portonics.mygp"),
    ("MyAirtel", "com.myairtelapp"),
    ("MyTeletalk", "teletalk.teletalkcustomerapp"),
    # Rides, Food & Travel
    ("Foodpanda", "com.global.foodpanda.android"),
    ("Pathao", "com.pathao.user"),
    ("Uber", "com.ubercab"),
    ("GoZayaan", "com.gozayaan.app"),
    ("MakeMyTrip", "com.makemytrip"),
    ("Skyscanner", "net.skyscanner.android.main"),
    ("ixigo", "com.ixigo"),
    ("Shohoz", "com.shohoz.dtrainpwa"),
    # Heavy Utilities & Games
    ("WPS Office Lite", "cn.wps.moffice_eng.xiaomi.lite"),
    ("CamScanner", "com.intsig.camscanner"),
    ("eSound", "com.esound"),
    ("Military Overturn", "games.vaveda.militaryoverturn"),
    ("Duolingo", "com.duolingo")
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

def apply_deep_sleep_rules(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: ENFORCING DEEP SLEEP ON PAYMENT & INFREQUENT APPS{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}")

    # Check installed packages
    pkg_list_res = run_adb(["shell", "pm", "list", "packages"], serial).stdout or ""
    
    applied_count = 0
    for name, pkg in SLEEP_CANDIDATES:
        if f"package:{pkg}" in pkg_list_res:
            applied_count += 1
            # 1. Standby Bucket 45 (Restricted - OS freezes process when in background)
            run_adb(["shell", "am", "set-standby-bucket", pkg, "45"], serial)
            # 2. Prevent background autostart
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
            # 3. Disallow background CPU execution & wakelocks
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "ignore"], serial)
            # 4. Remove from Doze battery optimization whitelist
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"], serial)
            # 5. Force-stop active lingering background process
            run_adb(["shell", "am", "force-stop", pkg], serial)
            print(f"    {Colors.GREEN}✔ [DEEP SLEEP] {name:<22} ({pkg:<32}) -> Bucket 45 (Restricted){Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Successfully applied deep sleeping rules to {applied_count} apps!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}\n")

def optimize_hardware_radios(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}[*] Disabling continuous background Wi-Fi and Bluetooth scanning...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"], serial)
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

    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: DEVICE THERMAL & BATTERY SNAPSHOT{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f" Battery Level       : {Colors.BOLD}{level}{Colors.RESET}")
    print(f" Battery Temperature : {Colors.BOLD}{temp}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Intelligent Power & Battery Optimizer by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--sleep-apps", action="store_true", help="Put infrequent banking, payment and utility apps to deep sleep")
    parser.add_argument("--optimize-radios", action="store_true", help="Disable background Wi-Fi and Bluetooth location scanning")
    parser.add_argument("--status", action="store_true", help="Check battery temperature and charging status")
    args = parser.parse_args()

    if args.sleep_apps:
        apply_deep_sleep_rules(args.serial)
    elif args.optimize_radios:
        optimize_hardware_radios(args.serial)
    elif args.status:
        print_thermal_status(args.serial)
    else:
        # Default run: Apply all optimizations
        optimize_hardware_radios(args.serial)
        apply_deep_sleep_rules(args.serial)
        print_thermal_status(args.serial)

if __name__ == "__main__":
    main()
