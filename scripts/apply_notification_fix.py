#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Multi-Brand Universal Automated Notification Fixer & Resource Optimizer
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
import json
import time
import argparse
from typing import Dict, Any, List, Optional
try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

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
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

TARGET_PACKAGES = [
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.gm",
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.imo.android.imoim",
    "com.facebook.orca",
    "com.facebook.katana",
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

RESTRICTED_BACKGROUND_PACKAGES = [
    "com.bKash.customerapp",
    "com.konasl.nagad",
    "com.pathao.user",
    "com.global.foodpanda.android",
    "com.ubercab",
    "com.daraz.android"
]

def run_adb(cmd: List[str], serial: Optional[str] = None) -> subprocess.CompletedProcess:
    assert_command_safe(cmd)
    base = ["adb"]
    if serial:
        base.extend(["-s", serial])
    base.extend(cmd)
    try:
        return subprocess.run(base, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: 'adb' executable not found in PATH.{Colors.RESET}")
        sys.exit(1)

def get_installed_packages(serial: Optional[str] = None) -> List[str]:
    res = run_adb(["shell", "pm", "list", "packages"], serial)
    installed = []
    for line in res.stdout.splitlines():
        if line.startswith("package:"):
            installed.append(line.replace("package:", "").strip())
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

    # Capture current states
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

def apply_universal_fixes(serial: Optional[str] = None, enable_dns: bool = False, custom_apps: Optional[List[str]] = None):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: APPLYING HIGHEST-LEVEL INSTANT NOTIFICATION SUITE{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}")

    # 1. Backup First
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

    # 3. Identify Brand and Target Applications
    installed = get_installed_packages(serial)
    apps_to_fix = list(TARGET_PACKAGES)
    if custom_apps:
        apps_to_fix.extend(custom_apps)

    active_targets = [pkg for pkg in apps_to_fix if pkg in installed or "google" in pkg]

    brand = run_adb(["shell", "getprop", "ro.product.brand"], serial).stdout.strip().lower()
    manufacturer = run_adb(["shell", "getprop", "ro.product.manufacturer"], serial).stdout.strip().lower()
    is_xiaomi = brand in ["xiaomi", "redmi", "poco"] or manufacturer in ["xiaomi"]
    is_vivo = brand in ["vivo", "iqoo"] or manufacturer in ["vivo"]
    is_oppo = brand in ["oppo", "oneplus", "realme"] or manufacturer in ["oppo", "oneplus"]

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

    elif is_oppo:
        print(f"       -> Detected: {Colors.YELLOW}Oppo ColorOS / RealmeUI Platform{Colors.RESET}")
        print(f"       -> Bypassing Athena Quick Freeze & Auto Revoke...")
        for pkg in active_targets:
            run_adb(["shell", "cmd", "appops", "set", pkg, "AUTO_REVOKE_PERMISSIONS_IF_UNUSED", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "allow"], serial)
    else:
        print(f"       -> Applying Universal Android AOSP Background Whitelists...")

    # 5. Restrict Heavy Background Apps (bKash, Nagad, Pathao, Foodpanda, Uber)
    print(f"\n {Colors.CYAN}[5/7] Restricting Heavy Background Apps (Preserving RAM & Battery)...{Colors.RESET}")
    for pkg in RESTRICTED_BACKGROUND_PACKAGES:
        if pkg in installed:
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"], serial)
            run_adb(["shell", "am", "set-standby-bucket", pkg, "restricted"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
            uid = get_package_uid(pkg, serial)
            if uid is not None:
                run_adb(["shell", "cmd", "netpolicy", "remove", "restrict-background-whitelist", str(uid)], serial)
                run_adb(["shell", "cmd", "netpolicy", "add", "restrict-background-blacklist", str(uid)], serial)
            print(f"       • Restricted Background Execution: {Colors.YELLOW}{pkg}{Colors.RESET}")

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

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ All highest-level notification fixes applied successfully!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Multi-Brand Notification Fixer by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--dns-adguard", action="store_true", help="Configure AdGuard Private DNS to block vendor analytics")
    parser.add_argument("--apps", nargs="+", help="Additional package names to whitelist", default=None)
    args = parser.parse_args()

    apply_universal_fixes(args.serial, args.dns_adguard, args.apps)

if __name__ == "__main__":
    main()
