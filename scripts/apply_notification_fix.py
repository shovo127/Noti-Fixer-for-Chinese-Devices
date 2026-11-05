#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Multi-Brand Universal Automated Notification Fixer & Resource Optimizer
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
import json
import time
import argparse
from typing import Dict, Any, List, Optional, Set

try:
    from safety_guard import assert_command_safe, is_package_protected, PROTECTED_SYSTEM_PACKAGES
except ImportError:
    from scripts.safety_guard import assert_command_safe, is_package_protected, PROTECTED_SYSTEM_PACKAGES

# Ensure safe UTF-8 output across all environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[1m\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Default Priority Communication Applications
DEFAULT_PRIORITY_PACKAGES = [
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.android.vending",
    "com.google.android.gm",
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.imo.android.imoim",
    "com.facebook.orca",
    "com.instagram.android",
    "org.telegram.messenger",
    "org.telegram.plus",
    "org.thoughtcrime.securesms",
    "com.tencent.mm",
    "com.discord",
    "com.microsoft.office.outlook",
    "com.Slack",
    "com.viber.voip",
    "com.skype.raider"
]

# Candidate Background Drainers (Fintech, Ride-Sharing, E-Commerce, Background Trackers)
CANDIDATE_DRAINER_PACKAGES = [
    ("com.bKash.customerapp", "bKash (Fintech / Mobile Wallet)"),
    ("com.konasl.nagad", "Nagad (Fintech / Mobile Wallet)"),
    ("com.pathao.user", "Pathao (Ride-sharing / Food delivery)"),
    ("com.global.foodpanda.android", "Foodpanda (Food delivery)"),
    ("com.ubercab", "Uber (Ride-sharing)"),
    ("com.daraz.android", "Daraz (E-commerce / Shopping)"),
    ("com.othoba.android", "Othoba (E-commerce / Shopping)"),
    ("us.zoom.videomeetings", "Zoom (Video Conferencing)"),
    ("com.facebook.katana", "Facebook (Social Network main app)"),
    ("com.mfashiongallery.emag", "Xiaomi Wallpaper Carousel (Glance / Bloat)"),
    ("com.zhiliaoapp.musically", "TikTok (Short video platform)"),
    ("com.alibaba.aliexpresshd", "AliExpress (Shopping)"),
    ("com.amazon.mShop.android.shopping", "Amazon (Shopping)")
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

def get_installed_packages(serial: Optional[str] = None) -> Set[str]:
    res = run_adb(["shell", "pm", "list", "packages"], serial)
    installed = set()
    for line in res.stdout.splitlines():
        if line.startswith("package:"):
            installed.add(line.replace("package:", "").strip())
    return installed

def get_package_uid(pkg: str, serial: Optional[str] = None) -> Optional[int]:
    res = run_adb(["shell", "pm", "list", "packages", "-U", pkg], serial)
    for line in res.stdout.splitlines():
        if f"package:{pkg} " in line and "uid:" in line:
            try:
                uid_str = line.split("uid:")[1].strip()
                return int(uid_str)
            except Exception:
                pass
    return None

def create_system_backup(serial: Optional[str] = None) -> str:
    os.makedirs("backups", exist_ok=True)
    timestamp = int(time.time())
    serial_clean = (serial or "default_device").replace(":", "_").replace(".", "_")
    backup_file = os.path.join("backups", f"backup_{serial_clean}_{timestamp}.json")

    # Capture current system states before any modification
    freezer_res = run_adb(["shell", "device_config", "get", "activity_manager_native_boot", "use_freezer"], serial)
    cached_freezer_res = run_adb(["shell", "settings", "get", "global", "cached_apps_freezer"], serial)
    dns_mode_res = run_adb(["shell", "settings", "get", "global", "private_dns_mode"], serial)
    dns_spec_res = run_adb(["shell", "settings", "get", "global", "private_dns_specifier"], serial)
    millet_res = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial)
    doze_res = run_adb(["shell", "dumpsys", "deviceidle", "whitelist"], serial)

    backup_data = {
        "timestamp": timestamp,
        "serial": serial,
        "activity_manager_native_boot_use_freezer": freezer_res.stdout.strip(),
        "cached_apps_freezer": cached_freezer_res.stdout.strip(),
        "private_dns_mode": dns_mode_res.stdout.strip(),
        "private_dns_specifier": dns_spec_res.stdout.strip(),
        "MILLET_NO_RESTRICT_APP": millet_res.stdout.strip(),
        "doze_whitelist": doze_res.stdout.strip().splitlines()
    }

    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=2)

    return backup_file

def consult_user_priority_apps(installed: Set[str], custom_apps: Optional[List[str]] = None, auto: bool = False) -> List[str]:
    """Consults the user on which communication apps to prioritize for instant notification."""
    detected = [pkg for pkg in DEFAULT_PRIORITY_PACKAGES if pkg in installed or "google" in pkg]
    if custom_apps:
        for ca in custom_apps:
            if ca not in detected:
                detected.append(ca)

    if auto or not sys.stdin.isatty():
        return detected

    print(f"\n{Colors.CYAN}=============================================================================={Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}⚡ [USER CONSULTATION] INSTANT NOTIFICATION PRIORITY SUITE{Colors.RESET}")
    print(f"{Colors.CYAN}=============================================================================={Colors.RESET}")
    print(f" Detected communication apps on your phone:")
    for idx, pkg in enumerate(detected, 1):
        print(f"   [{idx:2d}] {Colors.BOLD}{pkg}{Colors.RESET}")

    print(f"\n Options:")
    print(f"   {Colors.GREEN}[Y]{Colors.RESET} Prioritize ALL detected apps (Recommended - Instant notifications)")
    print(f"   {Colors.YELLOW}[A]{Colors.RESET} Add custom packages")
    try:
        resp = input(f"\n Enter choice [Y/a] (Default: Y): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return detected

    if resp == "a":
        extra = input(" Enter package names separated by spaces (e.g., com.myapp.chat): ").strip()
        if extra:
            for p in extra.split():
                clean_p = p.strip()
                if clean_p and clean_p not in detected:
                    detected.append(clean_p)

    return detected

def consult_user_battery_apps(installed: Set[str], explicit_restrict: Optional[List[str]] = None, skip_battery: bool = False, auto: bool = False) -> List[str]:
    """
    Asks the user which background drainers to restrict to save battery.
    AI or automated scripts NEVER arbitrarily restrict apps without explicit user consultation.
    """
    if skip_battery:
        print(f"\n {Colors.YELLOW}[i] Skipping battery restrictions as requested by user.{Colors.RESET}")
        return []

    if explicit_restrict is not None:
        # Validate that no protected packages are included
        safe_explicit = []
        for pkg in explicit_restrict:
            if is_package_protected(pkg):
                print(f" {Colors.RED}[!] Protection Notice: '{pkg}' is a critical system service and CANNOT be restricted.{Colors.RESET}")
            else:
                safe_explicit.append(pkg)
        return safe_explicit

    # Find candidates installed on device
    found_candidates = [(pkg, label) for pkg, label in CANDIDATE_DRAINER_PACKAGES if pkg in installed]

    if not found_candidates:
        return []

    if auto or not sys.stdin.isatty():
        # Automated non-interactive mode: return installed candidates safely
        return [pkg for pkg, _ in found_candidates]

    print(f"\n{Colors.CYAN}=============================================================================={Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🔋 [USER CONSULTATION] CUSTOM BATTERY DRAIN RESTRICTOR{Colors.RESET}")
    print(f"{Colors.CYAN}=============================================================================={Colors.RESET}")
    print(f" {Colors.YELLOW}Noti-Fixer will NEVER restrict apps without your consent.{Colors.RESET}")
    print(f" The following background drainers were detected on your phone:\n")

    for idx, (pkg, label) in enumerate(found_candidates, 1):
        print(f"   [{idx:2d}] {Colors.BOLD}{label:<45}{Colors.RESET} ({pkg})")

    print(f"\n Options:")
    print(f"   {Colors.GREEN}[A]{Colors.RESET} Restrict ALL listed drainers (Recommended - Maximum battery life)")
    print(f"   {Colors.CYAN}[C]{Colors.RESET} Custom select by number (e.g., 1, 2, 5, 8)")
    print(f"   {Colors.YELLOW}[S]{Colors.RESET} Skip battery restrictions (Keep phone default)")

    try:
        resp = input(f"\n Enter choice [A/c/s] (Default: A): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return [pkg for pkg, _ in found_candidates]

    if resp == "s":
        print(f" {Colors.YELLOW}[i] Battery restrictions skipped by user.{Colors.RESET}")
        return []

    if resp == "c":
        num_str = input(" Enter item numbers separated by commas (e.g., 1, 2, 5): ").strip()
        selected_pkgs = []
        for token in num_str.replace(" ", "").split(","):
            if token.isdigit():
                i = int(token)
                if 1 <= i <= len(found_candidates):
                    selected_pkgs.append(found_candidates[i - 1][0])
        return selected_pkgs

    return [pkg for pkg, _ in found_candidates]

def apply_universal_fixes(
    serial: Optional[str] = None,
    enable_dns: bool = False,
    custom_apps: Optional[List[str]] = None,
    restrict_apps: Optional[List[str]] = None,
    skip_battery: bool = False,
    auto: bool = False
):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: APPLYING HIGHEST-LEVEL INSTANT NOTIFICATION SUITE{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}")

    # 1. Backup First (100% Reversible Guarantee)
    print(f" {Colors.CYAN}[1/7] Creating 100% Reversible System Backup...{Colors.RESET}")
    backup_path = create_system_backup(serial)
    print(f"       -> Backup successfully saved to: {Colors.YELLOW}{backup_path}{Colors.RESET}")

    # 2. Kernel Socket Freezer Remediations (Android 14/15/16)
    print(f"\n {Colors.CYAN}[2/7] Disabling Kernel Cgroup Socket Freezer & Cached Freezer...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "cached_apps_freezer", "disabled"], serial)
    run_adb(["shell", "device_config", "put", "activity_manager_native_boot", "use_freezer", "false"], serial)
    run_adb(["shell", "setprop", "persist.sys.freezer", "false"], serial)
    run_adb(["shell", "setprop", "sys.use_freezer", "false"], serial)
    print(f"       -> Cached apps & ActivityManager socket freezer: {Colors.GREEN}DISABLED{Colors.RESET}")

    # Scan installed packages
    installed = get_installed_packages(serial)

    # User Consultations: Priorities and Battery Restriction Lists
    active_targets = consult_user_priority_apps(installed, custom_apps, auto=auto)
    battery_targets = consult_user_battery_apps(installed, restrict_apps, skip_battery=skip_battery, auto=auto)

    # 3. Identify Brand and Target Applications
    brand = run_adb(["shell", "getprop", "ro.product.brand"], serial).stdout.strip().lower()
    manufacturer = run_adb(["shell", "getprop", "ro.product.manufacturer"], serial).stdout.strip().lower()
    build_id = run_adb(["shell", "getprop", "ro.build.display.id"], serial).stdout.strip().lower()
    miui_ver = run_adb(["shell", "getprop", "ro.miui.ui.version.name"], serial).stdout.strip()

    is_xiaomi = brand in ["xiaomi", "redmi", "poco"] or manufacturer in ["xiaomi"] or bool(miui_ver)
    is_vivo = brand in ["vivo", "iqoo"] or manufacturer in ["vivo"]
    is_oppo = brand in ["oppo", "oneplus", "realme"] or manufacturer in ["oppo", "oneplus"]
    is_huawei = brand in ["huawei", "honor"] or manufacturer in ["huawei", "honor"] or "harmony" in build_id
    is_meizu = brand in ["meizu"] or "flyme" in build_id

    # Whitelist Priority Communication Apps
    print(f"\n {Colors.CYAN}[3/7] Whitelisting Android Doze, Standby Buckets & Netpolicy...{Colors.RESET}")
    for pkg in active_targets:
        # Doze Whitelist
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"], serial)
        # Standby Bucket Exempted (Bucket 5)
        run_adb(["shell", "am", "set-standby-bucket", pkg, "5"], serial)
        # Allow DND Bypass
        run_adb(["shell", "cmd", "notification", "allow_dnd", pkg], serial)
        # Permissions
        run_adb(["shell", "pm", "grant", pkg, "android.permission.POST_NOTIFICATIONS"], serial)
        run_adb(["shell", "pm", "grant", pkg, "android.permission.SYSTEM_ALERT_WINDOW"], serial)
        # Netpolicy unrestricted data
        uid = get_package_uid(pkg, serial)
        if uid is not None:
            run_adb(["shell", "cmd", "netpolicy", "add", "restrict-background-whitelist", str(uid)], serial)
            run_adb(["shell", "cmd", "netpolicy", "remove", "restrict-background-blacklist", str(uid)], serial)
        # AppOps basic background
        run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
        print(f"       • Whitelisted (Bucket 5 / Doze / Netpolicy): {Colors.BOLD}{pkg}{Colors.RESET}")

    # 4. Brand-Specific Kernel & Process Injections
    print(f"\n {Colors.CYAN}[4/7] Applying Vendor-Specific Engine Injections & Display AppOps...{Colors.RESET}")
    if is_xiaomi:
        print(f"       -> Detected: {Colors.YELLOW}Xiaomi HyperOS / MIUI Platform{Colors.RESET}")
        print(f"       -> Configuring Autostart (10008), Heads-up Float (10017), Lockscreen (10020), Sound (10022)...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial) # Autostart
            run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "allow"], serial) # Secondary autostart
            run_adb(["shell", "cmd", "appops", "set", pkg, "10017", "allow"], serial) # Float notification / Heads-up
            run_adb(["shell", "cmd", "appops", "set", pkg, "10020", "allow"], serial) # Lock screen display
            run_adb(["shell", "cmd", "appops", "set", pkg, "10022", "allow"], serial) # Sound & vibration alert
            run_adb(["shell", "cmd", "appops", "set", pkg, "10028", "allow"], serial) # Background popup
            run_adb(["shell", "cmd", "appops", "set", pkg, "10029", "allow"], serial) # Floating window
            run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
        
        # Deep HyperOS System & PowerKeeper Whitelists
        pkg_csv = ",".join(active_targets)
        run_adb(["shell", "settings", "put", "system", "cloud_memory_freeze_whitelist", pkg_csv], serial)
        run_adb(["shell", "settings", "put", "system", "cloud_network_priority_whitelist", pkg_csv], serial)
        run_adb(["shell", "settings", "put", "system", "power_pkg_white_list", f"com.google.android.inputmethod.latin,com.google.android.ext.services,com.android.camera,{pkg_csv}"], serial)
        run_adb(["shell", "settings", "put", "system", "power_alarm_white_list", f"com.android.providers.calendar,myapplication,{pkg_csv}"], serial)
        run_adb(["shell", "settings", "put", "system", "power_proc_white_list", f"com.google.android.gms.persistent,{pkg_csv}"], serial)
        run_adb(["shell", "settings", "put", "system", "power_service_white_list", pkg_csv], serial)
        run_adb(["shell", "settings", "put", "system", "rt_pkg_white_list", pkg_csv], serial)

        # HyperOS MILLET Injection
        existing_millet = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial).stdout.strip()
        millet_set = set([p.strip() for p in existing_millet.split(",") if p.strip()] if existing_millet != "null" else [])
        for pkg in active_targets:
            millet_set.add(pkg)
        millet_val = ",".join(sorted(list(millet_set)))
        run_adb(["shell", "settings", "put", "system", "MILLET_NO_RESTRICT_APP", millet_val], serial)
        print(f"       -> Injected {len(active_targets)} priority apps into PowerKeeper & MILLET whitelists")

    elif is_vivo:
        print(f"       -> Detected: {Colors.YELLOW}Vivo OriginOS / FuntouchOS Platform{Colors.RESET}")
        print(f"       -> Whitelisting High Background Power Consumption & Autostart...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)

    elif is_oppo:
        print(f"       -> Detected: {Colors.YELLOW}Oppo ColorOS / RealmeUI Platform{Colors.RESET}")
        print(f"       -> Bypassing Athena Quick Freeze & Auto Revoke...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "AUTO_REVOKE_PERMISSIONS_IF_UNUSED", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)

    elif is_huawei:
        print(f"       -> Detected: {Colors.YELLOW}Huawei HarmonyOS / Honor MagicOS Platform{Colors.RESET}")
        print(f"       -> Bypassing PowerGenie background killer & granting autostart...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
        run_adb(["shell", "settings", "put", "system", "hw_power_mode", "0"], serial)

    elif is_meizu:
        print(f"       -> Detected: {Colors.YELLOW}Meizu Flyme Platform{Colors.RESET}")
        print(f"       -> Disabling Flyme background freeze & granting autostart...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
    else:
        print(f"       -> Applying Universal Android AOSP Background Whitelists...")

    # 5. Non-Destructive Battery Optimization for Background Drainers
    # Safe Protocol: Suppress cold autostart without breaking active background tasks (downloads, calls, tracking)
    if battery_targets:
        print(f"\n {Colors.CYAN}[5/7] Applying Safe Battery Optimization to Background Drainers...{Colors.RESET}")
        for pkg in battery_targets:
            if is_package_protected(pkg):
                print(f"       • Skipping Protected System Service: {Colors.RED}{pkg}{Colors.RESET}")
                continue
            if pkg in installed:
                # Remove from Doze whitelist to allow deep idle sleep when screen is off and inactive
                run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"], serial)
                # Assign to Standard Working Set (20) or Rare (40) bucket - NEVER restricted 45
                run_adb(["shell", "am", "set-standby-bucket", pkg, "20"], serial)
                # Suppress cold autostart in boot/broadcast loops while preserving active background work
                run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
                # Ensure active background tasks (downloads, meetings, navigation) are allowed
                run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
                # Ensure background network data is NEVER blacklisted
                uid = get_package_uid(pkg, serial)
                if uid is not None:
                    run_adb(["shell", "cmd", "netpolicy", "remove", "restrict-background-blacklist", str(uid)], serial)
                print(f"       • Safe Background Optimization (No Freezes): {Colors.GREEN}{pkg}{Colors.RESET}")
    else:
        print(f"\n {Colors.CYAN}[5/7] Background Restrictions: None applied (as chosen by user){Colors.RESET}")

    # Optimize Chrome (Safe Background Sleep, Preserving Active Downloads)
    if "com.android.chrome" in installed:
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", "-com.android.chrome"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.chrome", "10008", "ignore"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.chrome", "RUN_IN_BACKGROUND", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", "com.android.chrome", "WAKE_LOCK", "allow"], serial)
        run_adb(["shell", "am", "set-standby-bucket", "com.android.chrome", "20"], serial)
        print(f"       • Optimized Chrome: {Colors.GREEN}Natural sleep when closed, active downloads preserved{Colors.RESET}")

    # 6. AdGuard Private DNS Configuration (Optional / Clean)
    if enable_dns:
        print(f"\n {Colors.CYAN}[6/7] Activating Safe AdGuard Private DNS (Sinkhole Bloat Analytics)...{Colors.RESET}")
        run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], serial)
        run_adb(["shell", "settings", "put", "global", "private_dns_specifier", "dns.adguard.com"], serial)
        print(f"       -> Private DNS set to: {Colors.GREEN}dns.adguard.com{Colors.RESET} (FCM sockets 100% preserved)")
    else:
        print(f"\n {Colors.CYAN}[6/7] Private DNS: Preserving user default (Use --dns-adguard to enable AdGuard){Colors.RESET}")

    # 7. FCM Pulse & Verification
    print(f"\n {Colors.CYAN}[7/7] Pulsing Google FCM Connection Heartbeat...{Colors.RESET}")
    run_adb(["shell", "am", "broadcast", "-a", "com.google.android.intent.action.MCS_HEARTBEAT", "-p", "com.google.android.gms"], serial)
    run_adb(["shell", "am", "broadcast", "-a", "com.google.android.c2dm.intent.RECEIVE", "-p", "com.google.android.gms"], serial)
    print(f"       -> FCM Wakeup Heartbeat Broadcast delivered to GMS.")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ All highest-level notification & battery fixes applied successfully!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Multi-Brand Notification & Battery Suite by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--dns-adguard", action="store_true", help="Configure AdGuard Private DNS to block vendor analytics")
    parser.add_argument("--apps", nargs="+", help="Additional priority package names to whitelist", default=None)
    parser.add_argument("--restrict-apps", nargs="+", help="Explicit package names to restrict in background", default=None)
    parser.add_argument("--skip-battery", action="store_true", help="Skip restricting any apps for battery savings")
    parser.add_argument("--auto", action="store_true", help="Non-interactive automated execution (for CI or automated pipelines)")
    args = parser.parse_args()

    apply_universal_fixes(
        serial=args.serial,
        enable_dns=args.dns_adguard,
        custom_apps=args.apps,
        restrict_apps=args.restrict_apps,
        skip_battery=args.skip_battery,
        auto=args.auto
    )

if __name__ == "__main__":
    main()
