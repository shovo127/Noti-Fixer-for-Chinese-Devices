#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Safe User-Profile Bloatware & Ad-Service Debloater
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import json
import subprocess
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from safety_guard import assert_command_safe, is_package_protected, get_restore_command_for_package
except ImportError:
    from scripts.safety_guard import assert_command_safe, is_package_protected, get_restore_command_for_package

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Curated catalog of non-critical bloatware across Chinese OEM ROMs
# Each package has a safety level (RECOMMENDED or OPTIONAL) and reason
DEBLOAT_CATALOG: Dict[str, Dict[str, Any]] = {
    # --- Xiaomi / POCO / Redmi (HyperOS / MIUI) ---
    "com.miui.analytics": {
        "brand": "Xiaomi",
        "name": "MIUI Analytics",
        "tier": "RECOMMENDED",
        "reason": "Background telemetry and behavioral ad tracking"
    },
    "com.miui.personalassistant": {
        "brand": "Xiaomi",
        "name": "MIUI App Vault",
        "tier": "RECOMMENDED",
        "reason": "Redundant minus-one screen feed and widget consumer"
    },
    "com.android.quicksearchbox": {
        "brand": "Xiaomi",
        "name": "MIUI Quick Search Box",
        "tier": "RECOMMENDED",
        "reason": "Redundant search widget and background memory consumer"
    },
    "com.miui.systemAdSolution": {
        "brand": "Xiaomi",
        "name": "MSA (MIUI System Ads)",
        "tier": "RECOMMENDED",
        "reason": "System-wide push ads across native Xiaomi apps"
    },
    "com.mfashiongallery.emag": {
        "brand": "Xiaomi",
        "name": "Wallpaper Carousel / Glance",
        "tier": "RECOMMENDED",
        "reason": "Lockscreen sponsored ads and background data drain"
    },
    "com.xiaomi.mipicks": {
        "brand": "Xiaomi",
        "name": "GetApps (Mi Picks)",
        "tier": "RECOMMENDED",
        "reason": "Redundant third-party app store with aggressive push notifications"
    },
    "com.miui.cleanmaster": {
        "brand": "Xiaomi",
        "name": "Cleaner Engine (Clean Master)",
        "tier": "RECOMMENDED",
        "reason": "Cheetah Mobile third-party advertising and cleaning definition engine"
    },
    "com.xiaomi.ab": {
        "brand": "Xiaomi",
        "name": "MAB (Xiaomi Store & Push Telemetry)",
        "tier": "RECOMMENDED",
        "reason": "Xiaomi marketing, A/B push and ad campaign subsystem"
    },
    "com.android.htmlviewer": {
        "brand": "Xiaomi",
        "name": "HTMLViewer (China Daemon)",
        "tier": "RECOMMENDED",
        "reason": "Legacy China ROM background HTML viewer daemon"
    },
    "com.mobiletools.systemhelper": {
        "brand": "Xiaomi",
        "name": "SystemHelper (Carrier Telemetry)",
        "tier": "RECOMMENDED",
        "reason": "China ROM carrier telemetry and diagnostic helper"
    },
    "com.bsp.catchlog": {
        "brand": "Xiaomi",
        "name": "CatchLog Telemetry",
        "tier": "RECOMMENDED",
        "reason": "Xiaomi background log catcher and telemetry daemon"
    },
    "com.miui.miservice": {
        "brand": "Xiaomi",
        "name": "Services & Feedback",
        "tier": "RECOMMENDED",
        "reason": "Diagnostic and feedback reporting background telemetry"
    },
    "com.miui.hybrid": {
        "brand": "Xiaomi",
        "name": "Quick Apps Framework",
        "tier": "RECOMMENDED",
        "reason": "Ad delivery engine and web app container"
    },
    "com.miui.bugreport": {
        "brand": "Xiaomi",
        "name": "Miui Bug Report",
        "tier": "RECOMMENDED",
        "reason": "Continuous background crash and log telemetry"
    },
    "com.miui.yellowpage": {
        "brand": "Xiaomi",
        "name": "MIUI Yellow Pages",
        "tier": "OPTIONAL",
        "reason": "Commercial caller directory and promotional banners"
    },
    "com.mi.globalbrowser": {
        "brand": "Xiaomi",
        "name": "Mi Browser",
        "tier": "OPTIONAL",
        "reason": "Redundant browser with integrated news ads"
    },
    "com.miui.videoplayer": {
        "brand": "Xiaomi",
        "name": "Mi Video Player",
        "tier": "OPTIONAL",
        "reason": "Media player with integrated online streaming ads"
    },
    "com.miui.player": {
        "brand": "Xiaomi",
        "name": "Mi Music Player",
        "tier": "OPTIONAL",
        "reason": "Music player with promotional banners"
    },
    "com.xiaomi.joyose": {
        "brand": "Xiaomi",
        "name": "Joyose Telemetry",
        "tier": "OPTIONAL",
        "reason": "Gaming service that enforces aggressive thermal throttling"
    },

    # --- Vivo / iQOO (OriginOS / FuntouchOS) ---
    "com.vivo.appstore": {
        "brand": "Vivo",
        "name": "V-Appstore",
        "tier": "RECOMMENDED",
        "reason": "Redundant proprietary app store with notification promotions"
    },
    "com.vivo.browser": {
        "brand": "Vivo",
        "name": "Vivo Browser",
        "tier": "OPTIONAL",
        "reason": "Redundant browser with ad feed"
    },
    "com.vivo.magazine": {
        "brand": "Vivo",
        "name": "Lockscreen Magazine",
        "tier": "RECOMMENDED",
        "reason": "Lockscreen sponsored promotional wallpapers"
    },

    # --- Oppo / OnePlus / Realme (ColorOS / RealmeUI / OxygenOS) ---
    "com.heytap.market": {
        "brand": "Oppo",
        "name": "HeyTap App Market",
        "tier": "RECOMMENDED",
        "reason": "Redundant app store with promotional push ads"
    },
    "com.heytap.browser": {
        "brand": "Oppo",
        "name": "HeyTap Browser",
        "tier": "OPTIONAL",
        "reason": "Proprietary browser with promotional content"
    },
    "com.heytap.pictorial": {
        "brand": "Oppo",
        "name": "Lockscreen Magazine Pictorial",
        "tier": "RECOMMENDED",
        "reason": "Lockscreen news and sponsored wallpapers"
    },

    # --- Huawei / Honor (HarmonyOS / MagicOS) ---
    "com.huawei.appmarket": {
        "brand": "Huawei",
        "name": "Huawei AppGallery",
        "tier": "OPTIONAL",
        "reason": "Proprietary app store with promotional notifications"
    },
    "com.huawei.browser": {
        "brand": "Huawei",
        "name": "Huawei Browser",
        "tier": "OPTIONAL",
        "reason": "Proprietary browser with news feed"
    },
    "com.huawei.magazine": {
        "brand": "Huawei",
        "name": "Lockscreen Magazine",
        "tier": "RECOMMENDED",
        "reason": "Lockscreen promotional wallpapers and background data"
    }
}

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

def get_installed_packages(serial: Optional[str] = None) -> List[str]:
    res = run_adb(["shell", "pm", "list", "packages", "--user", "0"], serial)
    packages = []
    for line in res.stdout.splitlines():
        if line.startswith("package:"):
            packages.append(line.replace("package:", "").strip())
    return packages

def scan_bloatware(serial: Optional[str] = None) -> List[Dict[str, Any]]:
    installed = set(get_installed_packages(serial))
    found: List[Dict[str, Any]] = []

    for pkg, info in DEBLOAT_CATALOG.items():
        if pkg in installed and not is_package_protected(pkg):
            found.append({
                "package": pkg,
                "name": info["name"],
                "brand": info["brand"],
                "tier": info["tier"],
                "reason": info["reason"]
            })
    return found

def execute_debloat(packages_to_remove: List[str], serial: Optional[str] = None) -> List[str]:
    removed: List[str] = []
    if not packages_to_remove:
        return removed

    # Create timestamped plan backup
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(repo_root, "backups", f"debloat_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    plan_data = {
        "timestamp": timestamp,
        "action": "safe_user_profile_debloat",
        "method": "pm uninstall -k --user 0",
        "debloated_packages": packages_to_remove,
        "restore_command": "python scripts/restore_backup.py -b " + backup_dir
    }

    with open(os.path.join(backup_dir, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2)

    # Generate single-click restore script in backup folder
    bat_content = f"""@echo off
echo [*] Reinstalling debloated packages...
"""
    for pkg in packages_to_remove:
        bat_content += f"adb shell cmd package install-existing --user 0 {pkg}\n"
    bat_content += "echo [✔] Restoration complete!\npause\n"

    with open(os.path.join(backup_dir, "restore.bat"), "w", encoding="utf-8") as f:
        f.write(bat_content)

    print(f"\n {Colors.CYAN}[*] Applying User-Profile Debloat (Reversible via cmd package install-existing):{Colors.RESET}")
    for pkg in packages_to_remove:
        if is_package_protected(pkg):
            print(f"       -> {Colors.RED}SKIPPED (Protected System Package): {pkg}{Colors.RESET}")
            continue

        cmd = ["shell", "pm", "uninstall", "-k", "--user", "0", pkg]
        res = run_adb(cmd, serial)
        if "success" in (res.stdout or "").lower() or res.returncode == 0:
            removed.append(pkg)
            print(f"       -> {Colors.GREEN}Debloated for User 0:{Colors.RESET} {pkg}")
        else:
            print(f"       -> {Colors.YELLOW}Could not debloat {pkg}:{Colors.RESET} {res.stdout.strip() or res.stderr.strip()}")

    print(f"\n {Colors.GREEN}[✔] Debloat complete! {len(removed)} packages safely uninstalled for User 0.{Colors.RESET}")
    print(f"     Backup saved to: {Colors.CYAN}{backup_dir}{Colors.RESET}")
    return removed

def manage_debloat(serial: Optional[str] = None, auto: bool = False, specific_apps: Optional[List[str]] = None):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: SAFE USER-PROFILE BLOATWARE & AD DEBLOATER{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

    if specific_apps:
        execute_debloat(specific_apps, serial)
        return

    print(f" {Colors.CYAN}[*] Scanning device for vendor bloatware & ad services...{Colors.RESET}")
    candidates = scan_bloatware(serial)

    if not candidates:
        print(f"\n {Colors.GREEN}[✔] Clean device! No known vendor bloatware or ad services found on User 0.{Colors.RESET}\n")
        return

    print(f"\n {Colors.YELLOW}Found {len(candidates)} Bloatware & Ad Candidates on Device:{Colors.RESET}\n")
    print(f"  {'#':<3} | {'Brand':<8} | {'Safety Tier':<12} | {'App Name / Package':<40}")
    print(f"  {'-'*3} | {'-'*8} | {'-'*12} | {'-'*40}")
    for idx, c in enumerate(candidates, 1):
        tier_color = Colors.GREEN if c["tier"] == "RECOMMENDED" else Colors.YELLOW
        print(f"  [{idx:<1}] | {c['brand']:<8} | {tier_color}{c['tier']:<12}{Colors.RESET} | {c['name']} ({c['package']})")
        print(f"      └─ Reason: {c['reason']}")

    recommended = [c["package"] for c in candidates if c["tier"] == "RECOMMENDED"]
    all_found = [c["package"] for c in candidates]

    if auto:
        print(f"\n {Colors.CYAN}[*] Running in non-interactive mode: Debloating RECOMMENDED packages...{Colors.RESET}")
        execute_debloat(recommended, serial)
        return

    print(f"\n {Colors.BOLD}Options:{Colors.RESET}")
    print(f"   [1] Debloat ALL RECOMMENDED bloatware ({len(recommended)} packages - Safest)")
    print(f"   [2] Debloat ALL detected bloatware ({len(all_found)} packages - Includes optional browsers/players)")
    print(f"   [3] Select specific packages to debloat by number")
    print(f"   [4] Skip debloating and exit")

    try:
        choice = input(f"\n {Colors.BOLD}Enter choice [1-4] (default: 1): {Colors.RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return

    if choice == "2":
        execute_debloat(all_found, serial)
    elif choice == "3":
        sel_nums = input(f" {Colors.BOLD}Enter numbers separated by commas (e.g. 1, 3, 5): {Colors.RESET}").strip()
        chosen_pkgs = []
        for part in sel_nums.split(","):
            part = part.strip()
            if part.isdigit():
                num = int(part)
                if 1 <= num <= len(candidates):
                    chosen_pkgs.append(candidates[num - 1]["package"])
        if chosen_pkgs:
            execute_debloat(chosen_pkgs, serial)
        else:
            print("No valid packages selected.")
    elif choice == "4":
        print("Debloating skipped by user.")
    else:
        execute_debloat(recommended, serial)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Noti-Fixer Safe User-Profile Bloatware Debloater")
    parser.add_argument("-s", "--serial", help="Target ADB device serial")
    parser.add_argument("--auto", action="store_true", help="Automatically remove all recommended bloatware")
    parser.add_argument("--apps", nargs="+", help="Specific packages to debloat")
    parser.add_argument("--scan-only", action="store_true", help="Only scan and display found bloatware without removing")
    args = parser.parse_args()

    if args.scan_only:
        found = scan_bloatware(args.serial)
        print(json.dumps(found, indent=2))
    else:
        manage_debloat(serial=args.serial, auto=args.auto, specific_apps=args.apps)

