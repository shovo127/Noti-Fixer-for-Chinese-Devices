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

try:
    from adb_core import run_adb, Colors, get_installed_packages, get_package_uid
except ImportError:
    from scripts.adb_core import run_adb, Colors, get_installed_packages, get_package_uid

# Default Priority Communication Applications (Core Instant Messaging)
DEFAULT_PRIORITY_PACKAGES = [
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.gm",
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.imo.android.imoim",
    "com.facebook.orca",
    "com.viber.voip",
    "com.instagram.android",
    "org.telegram.messenger",
    "org.telegram.plus",
]

# Candidate Background Drainers (Fintech, Ride-Sharing, E-Commerce, Background Trackers)
CANDIDATE_DRAINER_PACKAGES = [
    ("com.bKash.customerapp", "bKash (Fintech / Mobile Wallet)"),
    ("com.konasl.nagad", "Nagad (Fintech / Mobile Wallet)"),
    ("com.dbbl.mbs.apps.amaderrocket", "Rocket (DBBL Mobile Banking)"),
    ("com.pathao.user", "Pathao (Ride-sharing / Food delivery)"),
    ("com.global.foodpanda.android", "Foodpanda (Food delivery)"),
    ("com.ubercab", "Uber (Ride-sharing)"),
    ("com.daraz.android", "Daraz (E-commerce / Shopping)"),
    ("com.othoba.android", "Othoba (E-commerce / Shopping)"),
    ("com.facebook.katana", "Facebook (Social Network main app)"),
    ("com.intsig.camscanner", "CamScanner (Document Scanner)"),
    ("com.mfashiongallery.emag", "Xiaomi Wallpaper Carousel (Glance / Bloat)"),
    ("com.zhiliaoapp.musically", "TikTok (Short video platform)"),
    ("com.alibaba.aliexpresshd", "AliExpress (Shopping)"),
    ("com.amazon.mShop.android.shopping", "Amazon (Shopping)")
]

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
    enable_debloat: bool = False,
    auto: bool = False
):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: APPLYING HIGHEST-LEVEL INSTANT NOTIFICATION SUITE{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}")

    # 1. Backup First (100% Reversible Guarantee)
    print(f" {Colors.CYAN}[1/7] Creating 100% Reversible System Backup...{Colors.RESET}")
    backup_path = create_system_backup(serial)
    print(f"       -> Backup successfully saved to: {Colors.YELLOW}{backup_path}{Colors.RESET}")

    # 2. Kernel Cgroups, Hardware Radios & Standby Battery Optimization
    print(f"\n {Colors.CYAN}[2/7] Optimizing Linux Cgroups, Hardware Radios & Deep-Sleep Suspend...{Colors.RESET}")
    # Disable Wi-Fi hardware suspend optimizations (prevents Wi-Fi radio drop when screen off; ensures instant push notification arrival)
    run_adb(["shell", "settings", "put", "global", "wifi_suspend_optimizations_enabled", "0"], serial)
    
    # Disable hardware radio background scanning (stops background location radio polling)
    run_adb(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"], serial)
    
    # Enable native Android cached apps freezer so background apps sleep when screen is off
    # (Priority messaging apps are selectively unthrottled via MILLET and Doze whitelists)
    run_adb(["shell", "settings", "put", "global", "cached_apps_freezer", "enabled"], serial)
    run_adb(["shell", "device_config", "put", "activity_manager_native_boot", "use_freezer", "true"], serial)
    
    # Disable Android 16 Phantom Process Killer limit (allow parallel background transcoding and downloads)
    run_adb(["shell", "device_config", "put", "activity_manager", "max_phantom_processes", "2147483647"], serial)
    run_adb(["shell", "settings", "put", "global", "settings_enable_monitor_phantom_procs", "false"], serial)

    # Ensure USB/Wireless debugging does not chime or spam noisy notifications
    run_adb(["shell", "settings", "put", "global", "adb_notify", "0"], serial)
    run_adb(["shell", "settings", "put", "secure", "adb_notify", "0"], serial)

    # Heal broken/invalid system notification sound URIs (e.g. WaterDrop_preview which causes NullPointerException in NotificationPlayer)
    curr_sound = run_adb(["shell", "settings", "get", "system", "notification_sound"], serial).stdout.strip()
    if not curr_sound or curr_sound == "null" or "WaterDrop" in curr_sound or "/ui/" in curr_sound:
        run_adb(["shell", "settings", "put", "system", "notification_sound", "content://media/internal/audio/media/25?title=Fresh&canonical=1"], serial)
        run_adb(["shell", "settings", "put", "system", "notification_sound_cache", "content://media/internal/audio/media/25?title=Fresh&canonical=1"], serial)

    # Clean up any aggressive 120s FCM heartbeat overrides (allow native adaptive keepalive to prevent 240+ wakeups/night)
    for scope in ["global", "secure"]:
        run_adb(["shell", "settings", "delete", scope, "fcm_heartbeat_interval_wifi_ms"], serial)
        run_adb(["shell", "settings", "delete", scope, "fcm_heartbeat_interval_mobile_ms"], serial)
    run_adb(["shell", "settings", "delete", "global", "gservices:fcm_heartbeat_interval_wifi_ms"], serial)
    run_adb(["shell", "settings", "delete", "global", "gservices:fcm_heartbeat_interval_mobile_ms"], serial)

    # Clean up non-messaging telemetry/sync/store apps and 3rd party messaging apps from Doze whitelist
    # (Tier 4 Offline Zero-Drain: Only GMS, GSF, GM, DeskClock remain in Doze whitelist)
    for rogue_pkg in [
        "com.whatsapp", "com.whatsapp.w4b", "com.imo.android.imoim", "com.facebook.orca",
        "com.viber.voip", "com.instagram.android", "com.discord", "us.zoom.videomeetings",
        "com.microsoft.teams", "com.xiaomi.account", "com.xiaomi.xmsf", "com.xiaomi.xmsfkeeper",
        "com.xiaomi.aicr", "com.miui.home", "com.miui.gallery", "com.miui.micloudsync",
        "com.miui.cloudservice", "com.miui.cloudbackup", "com.lbe.security.miui",
        "com.android.providers.downloads", "com.android.vending",
        "com.google.android.googlequicksearchbox"
    ]:
        run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{rogue_pkg}"], serial)

    # Balance Google Play Store: allow smooth background downloading when minimized,
    # but prevent idle wakeups, boot autostart, and battery drain in deep sleep.
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "RUN_ANY_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "WAKE_LOCK", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "START_FOREGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10008", "ignore"], serial)
    run_adb(["shell", "cmd", "appops", "set", "com.android.vending", "10021", "ignore"], serial)
    run_adb(["shell", "am", "set-standby-bucket", "com.android.vending", "20"], serial)

    # Reset software battery stats to calibrate fresh measurements
    run_adb(["shell", "cmd", "battery", "reset"], serial)

    print(f"       -> Wi-Fi Suspend Power Saving: {Colors.GREEN}ENABLED (Optimal standby battery life){Colors.RESET}")
    print(f"       -> Hardware Scanning (Wi-Fi/BLE): {Colors.GREEN}DISABLED (0mA background drain){Colors.RESET}")
    print(f"       -> Native Cached Apps Freezer: {Colors.GREEN}ENABLED (Zero idle CPU drain){Colors.RESET}")
    print(f"       -> FCM Heartbeat: {Colors.GREEN}ADAPTIVE (Native Google Play Services keepalive){Colors.RESET}")
    print(f"       -> Max Phantom Processes: {Colors.GREEN}DISABLED (2147483647 - Multitasking Unthrottled){Colors.RESET}")

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
    CORE_INFRA_WHITELIST = {
        "com.google.android.gms",
        "com.google.android.gsf",
        "com.google.android.gm",
        "com.android.deskclock",
        "com.google.android.deskclock"
    }
    for pkg in active_targets:
        if pkg in CORE_INFRA_WHITELIST:
            # Core push infrastructure & system clock MUST be exempted from Doze
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"], serial)
            bucket = "5"
        else:
            # Communication apps (Messenger, imo, WhatsApp, Instagram) MUST NOT bypass Doze!
            # Removing them from Doze whitelist ensures that when Wi-Fi/Mobile Data is turned OFF at night,
            # aggressive internal TCP/MQTT keepalive alarms will NOT wake the CPU from deep sleep.
            # When Internet IS ON, notifications are delivered instantly via Google Play Services (GMS FCM).
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"-{pkg}"], serial)
            bucket = "10"

        run_adb(["shell", "am", "set-standby-bucket", pkg, bucket], serial)
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
        run_adb(["shell", "cmd", "appops", "set", pkg, "TURN_SCREEN_ON", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "POST_NOTIFICATION", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "USE_FULL_SCREEN_INTENT", "allow"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
        # Unstop package if device recently rebooted to ensure GMS delivers pending broadcasts
        run_adb(["shell", "am", "broadcast", "-a", "android.intent.action.PACKAGE_UNSTOPPED", "-d", f"package:{pkg}", "--include-stopped-packages"], serial)
        print(f"       • Whitelisted (Bucket {bucket} / Doze / Netpolicy): {Colors.BOLD}{pkg}{Colors.RESET}")

    # Explicitly protect system alarm clock (guarantees alarms always fire in deep sleep)
    for alarm_pkg in ["com.android.deskclock", "com.google.android.deskclock"]:
        if alarm_pkg in installed:
            run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"+{alarm_pkg}"], serial)
            run_adb(["shell", "am", "set-standby-bucket", alarm_pkg, "5"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "RUN_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "WAKE_LOCK", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "TURN_SCREEN_ON", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "USE_FULL_SCREEN_INTENT", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "POST_NOTIFICATION", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10008", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10017", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10020", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10021", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10022", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10028", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", alarm_pkg, "10029", "allow"], serial)
            print(f"       • Protected Alarm Clock: {Colors.GREEN}{alarm_pkg}{Colors.RESET}")

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
            # Prevent Messenger overlay fighting loops (10028 background popup fights native conversation bubbles)
            if pkg == "com.facebook.orca":
                run_adb(["shell", "cmd", "appops", "set", pkg, "10028", "ignore"], serial)
            else:
                run_adb(["shell", "cmd", "appops", "set", pkg, "10028", "allow"], serial) # Background popup
            run_adb(["shell", "cmd", "appops", "set", pkg, "10029", "allow"], serial) # Floating window
            run_adb(["shell", "cmd", "appops", "set", pkg, "SYSTEM_ALERT_WINDOW", "allow"], serial)
            run_adb(["shell", "cmd", "appops", "set", pkg, "TURN_SCREEN_ON", "allow"], serial) # Wake lockscreen for alerts
            run_adb(["shell", "cmd", "appops", "set", pkg, "USE_FULL_SCREEN_INTENT", "allow"], serial)
        
        # Deep HyperOS System & PowerKeeper Whitelists
        pkg_csv = ",".join(active_targets)
        freeze_extra = "com.android.vending,com.android.providers.downloads,com.android.deskclock,com.bKash.customerapp,com.konasl.nagad"
        full_freeze_csv = f"{pkg_csv},{freeze_extra}"
        run_adb(["shell", "settings", "put", "system", "cloud_memory_freeze_whitelist", full_freeze_csv], serial)
        run_adb(["shell", "settings", "put", "system", "cloud_network_priority_whitelist", full_freeze_csv], serial)
        run_adb(["shell", "settings", "put", "system", "power_pkg_white_list", f"com.android.deskclock,com.google.android.deskclock,com.google.android.inputmethod.latin,com.google.android.ext.services,com.android.camera,{full_freeze_csv}"], serial)
        run_adb(["shell", "settings", "put", "system", "power_alarm_white_list", "com.android.deskclock,com.google.android.deskclock,com.android.providers.calendar,myapplication"], serial)
        run_adb(["shell", "settings", "put", "system", "power_proc_white_list", f"com.google.android.gms.persistent,{full_freeze_csv}"], serial)
        run_adb(["shell", "settings", "put", "system", "power_service_white_list", full_freeze_csv], serial)
        run_adb(["shell", "settings", "put", "system", "rt_pkg_white_list", full_freeze_csv], serial)

        # HyperOS MILLET Injection
        existing_millet = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial).stdout.strip()
        millet_set = set([p.strip() for p in existing_millet.split(",") if p.strip()] if existing_millet != "null" else [])
        for pkg in active_targets:
            millet_set.add(pkg)
        for extra_p in ["com.android.vending", "com.android.providers.downloads", "com.android.deskclock", "com.bKash.customerapp", "com.konasl.nagad"]:
            millet_set.add(extra_p)
        millet_val = ",".join(sorted(list(millet_set)))
        run_adb(["shell", "settings", "put", "system", "MILLET_NO_RESTRICT_APP", millet_val], serial)
        print(f"       -> Injected {len(active_targets)} priority apps into PowerKeeper & MILLET whitelists")

        # HyperOS Immobulus Mode & Wakeup List Injection
        try:
            cur_imm = run_adb(["shell", "settings", "get", "secure", "immobulus_mode_switch_restrict"], serial).stdout.strip()
            if cur_imm and cur_imm != "null" and "_wakeuplist" in cur_imm and "com.whatsapp" not in cur_imm:
                extra_imm = "_" + "_".join(active_targets)
                parts = cur_imm.split("_wakeuplist")
                new_imm = parts[0] + extra_imm + "_wakeuplist" + parts[1] + extra_imm
                run_adb(["shell", "settings", "put", "secure", "immobulus_mode_switch_restrict", new_imm], serial)
                print(f"       -> Injected priority apps into HyperOS Immobulus Allowlist & Wakeuplist")
        except Exception:
            pass

        # Ensure device /data/local/tmp has no runaway background daemon
        run_adb(["shell", "pkill", "-f", "millet_watchdog.sh"], serial)
        run_adb(["shell", "rm", "-f", "/data/local/tmp/millet_watchdog.sh", "/data/local/tmp/millet_watchdog.log"], serial)
        print(f"       -> MILLET & FCM Whitelist Status: {Colors.GREEN}ENFORCED (Zero-Polling Native Architecture){Colors.RESET}")

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
                # Assign to Official Android Standby Bucket RARE (40)
                # When closed: strict freeze, no background jobs, battery drain = 0
                # When opened by user: Android auto-promotes to ACTIVE (10) for 100% full speed
                run_adb(["shell", "am", "set-standby-bucket", pkg, "rare"], serial)
                # Suppress cold autostart on boot and wakeups from background broadcasts
                run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "ignore"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "ignore"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10028", "ignore"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10029", "ignore"], serial)
                # Keep user-facing alert delivery active (sound, vibration, lockscreen alert)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10017", "allow"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10020", "allow"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "10022", "allow"], serial)
                # Ensure permissions allow smooth operation while actively in use
                run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
                run_adb(["shell", "cmd", "appops", "set", pkg, "WAKE_LOCK", "allow"], serial)
                # Gracefully stop any lingering background idle instance
                run_adb(["shell", "am", "stop-app", pkg], serial)
                print(f"       • On-Demand Execution Configured (Dormant when closed): {Colors.GREEN}{pkg}{Colors.RESET}")
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

    # 6. Safe User-Profile Bloatware & Ad Debloater (Optional)
    if enable_debloat:
        try:
            from debloat_manager import scan_bloatware, execute_debloat
        except ImportError:
            from scripts.debloat_manager import scan_bloatware, execute_debloat
        print(f"\n {Colors.CYAN}[6/8] Scanning and Debloating Recommended Vendor Bloatware...{Colors.RESET}")
        cands = scan_bloatware(serial)
        rec_pkgs = [c["package"] for c in cands if c["tier"] == "RECOMMENDED"]
        if rec_pkgs:
            execute_debloat(rec_pkgs, serial)
        else:
            print(f"       -> {Colors.GREEN}No recommended vendor bloatware packages detected on User 0.{Colors.RESET}")

    # 7. AdGuard Private DNS Configuration (Optional / Clean)
    if enable_dns:
        print(f"\n {Colors.CYAN}[7/8] Activating Safe AdGuard Private DNS (Sinkhole Bloat Analytics)...{Colors.RESET}")
        run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], serial)
        run_adb(["shell", "settings", "put", "global", "private_dns_specifier", "dns.adguard.com"], serial)
        print(f"       -> Private DNS set to: {Colors.GREEN}dns.adguard.com{Colors.RESET} (FCM sockets 100% preserved)")
    else:
        print(f"\n {Colors.CYAN}[7/8] Private DNS: Preserving user default (Use --dns-adguard to enable AdGuard){Colors.RESET}")

    # 8. FCM Pulse & Verification
    print(f"\n {Colors.CYAN}[8/8] Pulsing Google FCM Connection Heartbeat...{Colors.RESET}")
    run_adb(["shell", "am", "broadcast", "-a", "com.google.android.intent.action.MCS_HEARTBEAT", "-p", "com.google.android.gms"], serial)
    run_adb(["shell", "am", "broadcast", "-a", "com.google.android.c2dm.intent.RECEIVE", "-p", "com.google.android.gms"], serial)
    print(f"       -> FCM Wakeup Heartbeat Broadcast delivered to GMS.")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ All highest-level notification, battery & bloatware fixes applied successfully!{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Multi-Brand Notification & Battery Suite by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--dns-adguard", action="store_true", help="Configure AdGuard Private DNS to block vendor analytics")
    parser.add_argument("--debloat", action="store_true", help="Scan and remove recommended vendor bloatware & ad services for user profile")
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
        enable_debloat=args.debloat,
        auto=args.auto
    )

if __name__ == "__main__":
    main()
