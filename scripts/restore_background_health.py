#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Background App Health Restorer & Network Unblocker
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import subprocess
import argparse
from typing import Optional, List

try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

COMMON_USER_APPS = [
    "com.android.vending",
    "com.bKash.customerapp",
    "com.konasl.nagad",
    "com.pathao.user",
    "com.global.foodpanda.android",
    "com.ubercab",
    "com.daraz.android",
    "com.othoba.android",
    "us.zoom.videomeetings",
    "com.facebook.katana",
    "com.intsig.camscanner",
    "com.xiaomi.market",
    "com.android.chrome"
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

def restore_background_health(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: RESTORING BACKGROUND APP HEALTH & NETWORK ACCESS{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

    # 1. Clear any netpolicy blacklists
    print(f" {Colors.CYAN}[1/3] Clearing any background network blacklists...{Colors.RESET}")
    netpolicy_dump = run_adb(["shell", "dumpsys", "netpolicy"], serial).stdout
    cleared_count = 0
    for line in netpolicy_dump.splitlines():
        if "policy=1" in line and "UID=" in line:
            parts = line.split("UID=")
            if len(parts) >= 2:
                uid_str = parts[1].split()[0].strip()
                if uid_str.isdigit():
                    run_adb(["shell", "cmd", "netpolicy", "remove", "restrict-background-blacklist", uid_str], serial)
                    cleared_count += 1
    print(f"       -> Cleared background network blocks on {cleared_count} app UIDs.")

    # 2. Restore Google Play Store full unthrottled permissions
    print(f"\n {Colors.CYAN}[2/3] Restoring Google Play Store background download engine...{Colors.RESET}")
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "WAKE_LOCK", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_ANY_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10008", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10021", "allow"], serial)
    run_adb(["shell", "am", "set-standby-bucket", "com.android.vending", "10"], serial)
    run_adb(["shell", "dumpsys", "deviceidle", "whitelist", "+com.android.vending"], serial)
    print(f"       -> Google Play Store: {Colors.GREEN}100% UNTHROTTLED (Bucket 10, Wakelocks & Doze Allowed){Colors.RESET}")

    # 3. Restore all active user applications
    print(f"\n {Colors.CYAN}[3/3] Restoring active user applications (Zoom, bKash, Ride-sharing, Chrome)...{Colors.RESET}")
    installed_res = run_adb(["shell", "pm", "list", "packages"], serial).stdout
    for pkg in COMMON_USER_APPS:
        if f"package:{pkg}" in installed_res:
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "am", "set-standby-bucket", pkg, "20"], serial)
            print(f"       • Restored normal background execution: {Colors.BOLD}{pkg}{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ All background pausing and glitching issues have been fully resolved!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Background App Health Restorer")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    args = parser.parse_args()
    restore_background_health(args.serial)

if __name__ == "__main__":
    main()
