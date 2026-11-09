#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: FCM Socket, Android Doze & Vendor AppOps Auditor
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import subprocess
import json
import argparse
import re
from typing import Dict, Any, List, Optional
try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

KEY_PACKAGES = [
    {"name": "Google Play Services", "pkg": "com.google.android.gms", "critical": True},
    {"name": "Google Services Framework", "pkg": "com.google.android.gsf", "critical": True},
    {"name": "System Alarm Clock", "pkg": "com.android.deskclock", "critical": True},
    {"name": "WhatsApp", "pkg": "com.whatsapp", "critical": False},
    {"name": "WhatsApp Business", "pkg": "com.whatsapp.w4b", "critical": False},
    {"name": "imo", "pkg": "com.imo.android.imoim", "critical": False},
    {"name": "Telegram", "pkg": "org.telegram.messenger", "critical": False},
    {"name": "Facebook Messenger", "pkg": "com.facebook.orca", "critical": False},
    {"name": "Gmail", "pkg": "com.google.android.gm", "critical": True},
    {"name": "Signal", "pkg": "org.thoughtcrime.securesms", "critical": False},
    {"name": "WeChat", "pkg": "com.tencent.mm", "critical": False},
    {"name": "Instagram", "pkg": "com.instagram.android", "critical": False},
    {"name": "Discord", "pkg": "com.discord", "critical": False},
    {"name": "Microsoft Outlook", "pkg": "com.microsoft.office.outlook", "critical": False},
    {"name": "Viber", "pkg": "com.viber.voip", "critical": False},
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

def check_installed_packages(serial: Optional[str] = None) -> List[str]:
    res = run_adb(["shell", "pm", "list", "packages"], serial)
    installed = []
    for line in res.stdout.splitlines():
        if line.startswith("package:"):
            installed.append(line.replace("package:", "").strip())
    return installed

def check_fcm_socket(serial: Optional[str] = None) -> Dict[str, Any]:
    # Check Google Gms GcmService or netstat socket to mtalk.google.com:5228
    gms_res = run_adb(["shell", "dumpsys", "activity", "service", "com.google.android.gms/.gcm.GcmService"], serial)
    output = gms_res.stdout
    
    connected = False
    details = "Socket info unreachable"

    if "connected" in output.lower():
        # Match connection patterns
        if "is client connected: true" in output.lower() or "connection state: connected" in output.lower() or "connected: true" in output.lower():
            connected = True
            details = "FCM client actively connected to Google Push Service (mtalk.google.com)"
        else:
            details = "FCM Service registered, checking socket tables..."

    if not connected:
        # Check /proc/net/tcp or netstat for port 5228 (0x146C)
        netstat_res = run_adb(["shell", "cat", "/proc/net/tcp", "/proc/net/tcp6"], serial)
        # Port 5228 in hex is 146C
        if ":146C" in netstat_res.stdout or ":5228" in netstat_res.stdout:
            connected = True
            details = "Active TCP socket established to Google FCM port 5228"
        else:
            details = "FCM socket DEAD or disconnected. Notifications will be frozen until app is opened!"

    return {
        "connected": connected,
        "details": details
    }

def check_doze_whitelist(serial: Optional[str] = None) -> List[str]:
    res = run_adb(["shell", "dumpsys", "deviceidle", "whitelist"], serial)
    whitelisted = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.startswith("system,") or line.startswith("user,") or line.startswith("whitelist,"):
            parts = line.split(",")
            if len(parts) >= 2:
                whitelisted.append(parts[1].strip())
        elif line:
            whitelisted.append(line)
    return whitelisted

def check_cached_freezer(serial: Optional[str] = None) -> Dict[str, Any]:
    res = run_adb(["shell", "device_config", "get", "activity_manager_native_boot", "use_freezer"], serial)
    val = res.stdout.strip()
    is_frozen = (val == "true" or val == "") # Default Android 14+ behavior freezes sockets
    return {
        "raw_value": val or "default (kernel enabled)",
        "is_freezing_sockets": is_frozen,
        "recommendation": "Optimal (MILLET protected, zero idle CPU drain)" if is_frozen else "Freezer disabled (Risk of higher standby battery drain)"
    }

def check_wifi_suspend(serial: Optional[str] = None) -> bool:
    res = run_adb(["shell", "settings", "get", "global", "wifi_suspend_optimizations_enabled"], serial)
    val = res.stdout.strip()
    return val != "0" # True if enabled or unset (safe), False if explicitly disabled (100mA drain)

def check_alarm_protection(serial: Optional[str] = None) -> bool:
    res = run_adb(["shell", "settings", "get", "system", "power_alarm_white_list"], serial)
    val = res.stdout.strip()
    return "com.android.deskclock" in val or "deskclock" in val

def check_millet_whitelist(serial: Optional[str] = None) -> List[str]:
    res = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial)
    val = res.stdout.strip()
    if val and val != "null":
        return [p.strip() for p in val.split(",") if p.strip()]
    return []

def check_appops_for_package(pkg: str, serial: Optional[str] = None) -> Dict[str, Any]:
    # Check 10008 (Xiaomi autostart / Vivo autostart)
    # Check 10021 (Xiaomi background popup)
    # Check RUN_IN_BACKGROUND
    res_run = run_adb(["shell", "cmd", "appops", "get", pkg, "RUN_IN_BACKGROUND"], serial)
    res_10008 = run_adb(["shell", "cmd", "appops", "get", pkg, "10008"], serial)
    res_10021 = run_adb(["shell", "cmd", "appops", "get", pkg, "10021"], serial)
    
    return {
        "run_in_background": "allow" in res_run.stdout.lower() or "default" in res_run.stdout.lower(),
        "autostart_10008": "allow" in res_10008.stdout.lower(),
        "bg_popup_10021": "allow" in res_10021.stdout.lower()
    }

def audit_device(serial: Optional[str] = None) -> Dict[str, Any]:
    installed = check_installed_packages(serial)
    fcm_status = check_fcm_socket(serial)
    doze_whitelist = check_doze_whitelist(serial)
    freezer_status = check_cached_freezer(serial)
    millet_list = check_millet_whitelist(serial)
    
    package_audits = []
    total_score = 100
    deductions = []

    # Check FCM socket
    if not fcm_status["connected"]:
        total_score -= 35
        deductions.append("FCM Push Socket is disconnected or sleeping (-35 pts)")

    # Check Kernel Freezer
    # On HyperOS / MIUI, if MILLET whitelist has priority apps, socket freezing is safely bypassed for them
    # while allowing deep hardware sleep and stopping 80% idle battery drain for non-messaging apps.
    if freezer_status["is_freezing_sockets"] and len(millet_list) < 3:
        total_score -= 20
        deductions.append("Linux Cgroup cached_apps_freezer is active without MILLET socket protection (-20 pts)")

    # Check Wi-Fi Suspend Power Saving
    if not check_wifi_suspend(serial):
        total_score -= 15
        deductions.append("Wi-Fi Suspend Optimizations are DISABLED (Critical: 100mA continuous radio drain) (-15 pts)")

    # Check Alarm Clock Protection
    if not check_alarm_protection(serial):
        total_score -= 10
        deductions.append("DeskClock Alarm missing from PowerKeeper whitelist (Risk of alarms silenced in deep sleep) (-10 pts)")

    # Audit each relevant app installed
    for item in KEY_PACKAGES:
        pkg = item["pkg"]
        name = item["name"]
        is_critical = item.get("critical", False)
        if pkg in installed or is_critical:
            in_doze = any(pkg == d for d in doze_whitelist)
            in_millet = pkg in millet_list
            ops = check_appops_for_package(pkg, serial)

            if is_critical:
                if not in_doze:
                    total_score -= 8
                    deductions.append(f"Critical Infrastructure '{name}' missing from Doze Whitelist (-8 pts)")
            else:
                # For communication apps:
                # 1. Autostart MUST be allowed so incoming FCM broadcasts wake the app
                if not ops["autostart_10008"]:
                    total_score -= 4
                    deductions.append(f"'{name}' Autostart (10008) is NOT allowed (-4 pts)")
                # 2. Communication apps SHOULD NOT be in Doze Whitelist to prevent offline keepalive alarms (e.g. MQTT_Wakeup)
                # from draining battery at night when Wi-Fi/Data is turned off.
            
            package_audits.append({
                "name": name,
                "package": pkg,
                "installed": pkg in installed,
                "critical": is_critical,
                "doze_whitelisted": in_doze,
                "millet_whitelisted": in_millet if millet_list else "N/A",
                "appops": ops
            })

    total_score = max(0, min(100, total_score))

    return {
        "status": "success",
        "serial": serial,
        "health_score": total_score,
        "fcm_status": fcm_status,
        "freezer_status": freezer_status,
        "wifi_suspend": check_wifi_suspend(serial),
        "alarm_protected": check_alarm_protection(serial),
        "millet_configured": len(millet_list) > 0,
        "millet_entries_count": len(millet_list),
        "deductions": deductions,
        "apps_audited": package_audits
    }

def print_audit_report(audit: Dict[str, Any]):
    print(f"\n{Colors.CYAN}{'='*68}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: LIVE FCM, DOZE & PROCESS AUDIT REPORT{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*68}{Colors.RESET}")
    
    score = audit["health_score"]
    score_color = Colors.GREEN if score >= 80 else (Colors.YELLOW if score >= 50 else Colors.RED)
    print(f" {Colors.BOLD}System Notification Health Score :{Colors.RESET} {score_color}{Colors.BOLD}{score} / 100%{Colors.RESET}")
    
    fcm = audit["fcm_status"]
    fcm_icon = f"{Colors.GREEN}CONNECTED (LIVE){Colors.RESET}" if fcm["connected"] else f"{Colors.RED}FROZEN / DISCONNECTED{Colors.RESET}"
    print(f" {Colors.BOLD}Google FCM Socket (mtalk:5228)   :{Colors.RESET} {fcm_icon}")
    print(f"   -> Details: {fcm['details']}")

    freezer = audit["freezer_status"]
    if audit.get("millet_configured") and audit['millet_entries_count'] >= 3:
        freezer_icon = f"{Colors.GREEN}ENFORCED & MILLET PROTECTED (OPTIMAL BATTERY){Colors.RESET}"
    elif freezer["is_freezing_sockets"]:
        freezer_icon = f"{Colors.RED}ACTIVE (DANGEROUS WITHOUT MILLET){Colors.RESET}"
    else:
        freezer_icon = f"{Colors.YELLOW}DISABLED{Colors.RESET}"
    print(f" {Colors.BOLD}Kernel Cgroup Socket Freezer     :{Colors.RESET} {freezer_icon}")

    if audit.get("millet_configured"):
        print(f" {Colors.BOLD}Xiaomi HyperOS MILLET Whitelist  :{Colors.RESET} {Colors.GREEN}{audit['millet_entries_count']} Apps Whitelisted{Colors.RESET}")
    
    wifi_suspend_ok = audit.get("wifi_suspend", True)
    wifi_icon = f"{Colors.GREEN}ENABLED (Optimal Standby){Colors.RESET}" if wifi_suspend_ok else f"{Colors.RED}DISABLED (High Idle Drain){Colors.RESET}"
    print(f" {Colors.BOLD}Wi-Fi Hardware Suspend           :{Colors.RESET} {wifi_icon}")

    alarm_ok = audit.get("alarm_protected", True)
    alarm_icon = f"{Colors.GREEN}PROTECTED (PowerKeeper Whitelisted){Colors.RESET}" if alarm_ok else f"{Colors.RED}VULNERABLE (Missing from Whitelist){Colors.RESET}"
    print(f" {Colors.BOLD}Hardware DeskClock Alarm         :{Colors.RESET} {alarm_icon}")
    
    if audit["deductions"]:
        print(f"\n {Colors.BOLD}{Colors.RED}Identified Bottlenecks & Suppressions:{Colors.RESET}")
        for d in audit["deductions"]:
            print(f"   • {d}")

    print(f"\n {Colors.BOLD}Applications & Core Services Status:{Colors.RESET}")
    print(f" {'App Name':<24} | {'Doze Policy':<18} | {'Autostart':<12} | {'Status'}")
    print(f" {'-'*24}-+-{'-'*18}-+-{'-'*12}-+-{'-'*20}")
    
    for app in audit["apps_audited"]:
        is_crit = app.get("critical", False)
        if is_crit:
            doze_str = f"{Colors.GREEN}YES (Whitelisted){Colors.RESET}" if app["doze_whitelisted"] else f"{Colors.RED}NO (Vulnerable){Colors.RESET}"
            auto_str = f"{Colors.GREEN}SYSTEM{Colors.RESET}"
            status_str = f"{Colors.GREEN}CORE ACTIVE{Colors.RESET}" if app["doze_whitelisted"] else f"{Colors.RED}ACTION NEEDED{Colors.RESET}"
        else:
            # For messaging apps, NO in Doze is optimal (prevents offline keepalive drain while GMS handles push)
            doze_str = f"{Colors.YELLOW}YES (Drain Risk){Colors.RESET}" if app["doze_whitelisted"] else f"{Colors.GREEN}NO (Zero-Drain){Colors.RESET}"
            auto_str = f"{Colors.GREEN}ALLOWED{Colors.RESET}" if app["appops"]["autostart_10008"] else f"{Colors.YELLOW}DEFAULT{Colors.RESET}"
            status_str = f"{Colors.GREEN}FCM READY{Colors.RESET}" if app["appops"]["autostart_10008"] else f"{Colors.YELLOW}RESTRICTED{Colors.RESET}"

        print(f" {app['name']:<24} | {doze_str:<27} | {auto_str:<21} | {status_str}")

    print(f"{Colors.CYAN}{'='*68}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer FCM and Doze Diagnostic Auditor by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of the target device", default=None)
    parser.add_argument("--json", action="store_true", help="Print audit in raw JSON format")
    args = parser.parse_args()

    audit = audit_device(args.serial)
    if args.json:
        print(json.dumps(audit, indent=2))
    else:
        print_report = print_audit_report(audit)

if __name__ == "__main__":
    main()
