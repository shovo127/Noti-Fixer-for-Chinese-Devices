#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Universal Battery Consumption & Process Wakelock Inspector
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
import re
import argparse
from typing import Dict, Any, List, Optional, Tuple

try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

try:
    from adb_core import run_adb, Colors
except ImportError:
    from scripts.adb_core import run_adb, Colors

# Ensure safe UTF-8 output across all environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_uid_package_map(serial: Optional[str] = None) -> Dict[str, str]:
    res = run_adb(["shell", "pm", "list", "packages", "-U"], serial)
    uid_map = {}
    for line in res.stdout.splitlines():
        if "package:" in line and "uid:" in line:
            parts = line.split()
            pkg = parts[0].replace("package:", "").strip()
            uid = parts[1].replace("uid:", "").strip()
            uid_map[uid] = pkg
    return uid_map

def inspect_battery(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: LIVE BATTERY DRAIN & WAKELOCK INSPECTOR{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

    # 1. Battery Health & Capacity
    res_batt = run_adb(["shell", "dumpsys", "battery"], serial)
    level = "Unknown"
    temp = "Unknown"
    health = "Unknown"
    for line in res_batt.stdout.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("level:"):
            level = line_clean.split("level:")[1].strip() + "%"
        elif line_clean.startswith("temperature:"):
            try:
                t_val = int(line_clean.split("temperature:")[1].strip())
                temp = f"{t_val / 10:.1f}°C"
            except Exception:
                pass
        elif line_clean.startswith("health:"):
            health_code = line_clean.split("health:")[1].strip()
            health = "Good" if health_code == "2" else f"Code {health_code}"

    print(f" {Colors.CYAN}Battery Status:{Colors.RESET} Level: {Colors.BOLD}{level}{Colors.RESET} | Health: {Colors.GREEN}{health}{Colors.RESET} | Temp: {Colors.YELLOW}{temp}{Colors.RESET}")

    # 2. Parse Batterystats Estimated Drain
    print(f"\n {Colors.CYAN}Analyzing Android Estimated Power Drain (dumpsys batterystats)...{Colors.RESET}")
    bs_res = run_adb(["shell", "dumpsys", "batterystats", "--charged"], serial)
    if not bs_res.stdout or "Estimated power use" not in bs_res.stdout:
        bs_res = run_adb(["shell", "dumpsys", "batterystats"], serial)

    uid_map = get_uid_package_map(serial)
    drain_entries: List[Tuple[float, str, str]] = []

    lines = bs_res.stdout.splitlines()
    for line in lines:
        line_clean = line.strip()
        if line_clean.startswith("UID u0a") or line_clean.startswith("UID 10"):
            m = re.search(r"UID\s+(?:u0a|)(\d+):\s+([\d\.]+)", line_clean)
            if m:
                uid_raw = m.group(1)
                full_uid = str(10000 + int(uid_raw)) if int(uid_raw) < 1000 else uid_raw
                mah = float(m.group(2))
                pkg_name = uid_map.get(full_uid, f"UID {full_uid}")
                if full_uid == "1000":
                    pkg_name = "Android System / Core Services"
                drain_entries.append((mah, full_uid, pkg_name))

    drain_entries.sort(key=lambda x: x[0], reverse=True)

    # 3. Print Top Battery Drainers
    print(f"\n {Colors.BOLD}{'Rank':<6} {'Drain':<12} {'Package / Component':<40} {'UID':<10}{Colors.RESET}")
    print(f" {'-'*68}")
    
    seen_pkgs = set()
    rank = 1
    for mah, uid, pkg in drain_entries:
        if pkg in seen_pkgs:
            continue
        seen_pkgs.add(pkg)
        color = Colors.RED if mah >= 20.0 else (Colors.YELLOW if mah >= 5.0 else Colors.GREEN)
        print(f" #{rank:<5} {color}{mah:6.2f} mAh{Colors.RESET}   {pkg:<40} {uid:<10}")
        rank += 1
        if rank > 15:
            break

    # 4. Active Background Wakelocks Check
    print(f"\n {Colors.CYAN}Inspecting Active Background Wakelocks (PowerManagerService)...{Colors.RESET}")
    pwr_res = run_adb(["shell", "dumpsys", "power"], serial)
    active_locks = []
    idx = pwr_res.stdout.find("Wake Locks: size=")
    if idx != -1:
        snippet = pwr_res.stdout[idx:idx+1500]
        for l in snippet.splitlines()[1:]:
            if "PARTIAL_WAKE_LOCK" in l or "DOZE_WAKE_LOCK" in l:
                clean_l = l.strip()
                if "DISABLED" not in clean_l:
                    active_locks.append(clean_l)

    if active_locks:
        for al in active_locks[:5]:
            print(f"   {Colors.YELLOW}•{Colors.RESET} {al[:80]}")
    else:
        print(f"   {Colors.GREEN}✔ Zero rogue wakelocks detected. Deep sleep is healthy.{Colors.RESET}")

    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Battery Consumption & Wakelock Inspector by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    args = parser.parse_args()

    inspect_battery(args.serial)

if __name__ == "__main__":
    main()
