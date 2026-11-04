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
    {"name": "WhatsApp", "pkg": "com.whatsapp", "critical": False},
    {"name": "WhatsApp Business", "pkg": "com.whatsapp.w4b", "critical": False},
    {"name": "imo", "pkg": "com.imo.android.imoim", "critical": False},
    {"name": "Telegram", "pkg": "org.telegram.messenger", "critical": False},
    {"name": "Facebook Messenger", "pkg": "com.facebook.orca", "critical": False},
    {"name": "Gmail", "pkg": "com.google.android.gm", "critical": False},
    {"name": "Signal", "pkg": "org.thoughtcrime.securesms", "critical": False},
    {"name": "WeChat", "pkg": "com.tencent.mm", "critical": False},
    {"name": "Instagram", "pkg": "com.instagram.android", "critical": False},
    {"name": "Discord", "pkg": "com.discord", "critical": False},
    {"name": "Microsoft Outlook", "pkg": "com.microsoft.office.outlook", "critical": False},
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
        "recommendation": "Disable cached_apps_freezer via device_config to prevent kernel socket kills." if is_frozen else "Optimal"
    }

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
    if freezer_status["is_freezing_sockets"]:
        total_score -= 20
        deductions.append("Linux Cgroup cached_apps_freezer is actively killing idle sockets (-20 pts)")

    # Audit each relevant app installed
    for item in KEY_PACKAGES:
        pkg = item["pkg"]
        name = item["name"]
        if pkg in installed or item["critical"]:
            in_doze = any(pkg in d for d in doze_whitelist)
            in_millet = pkg in millet_list
            ops = check_appops_for_package(pkg, serial)

            score_pkg = True
            if not in_doze:
                total_score -= 4
                score_pkg = False
            
            package_audits.append({
                "name": name,
                "package": pkg,
                "installed": pkg in installed,
                "doze_whitelisted": in_doze,
                "millet_whitelisted": in_millet if millet_list else "N/A",
                "appops": ops
            })

    total_score = max(0, min(100, total_score))

    return {
        "status": "success",
        "health_score": total_score,
        "fcm_status": fcm_status,
        "freezer_status": freezer_status,
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
    freezer_icon = f"{Colors.RED}ACTIVE (DANGEROUS FOR FCM){Colors.RESET}" if freezer["is_freezing_sockets"] else f"{Colors.GREEN}DISABLED (OPTIMAL){Colors.RESET}"
    print(f" {Colors.BOLD}Kernel Cgroup Socket Freezer     :{Colors.RESET} {freezer_icon}")

    if audit.get("millet_configured"):
        print(f" {Colors.BOLD}Xiaomi HyperOS MILLET Whitelist  :{Colors.RESET} {Colors.GREEN}{audit['millet_entries_count']} Apps Whitelisted{Colors.RESET}")
    
    if audit["deductions"]:
        print(f"\n {Colors.BOLD}{Colors.RED}Identified Bottlenecks & Suppressions:{Colors.RESET}")
        for d in audit["deductions"]:
            print(f"   • {d}")

    print(f"\n {Colors.BOLD}Messaging Applications Status:{Colors.RESET}")
    print(f" {'App Name':<22} | {'Doze Whitelist':<14} | {'Autostart':<10} | {'Status'}")
    print(f" {'-'*22}-+-{'-'*14}-+-{'-'*10}-+-{'-'*12}")
    
    for app in audit["apps_audited"]:
        doze_str = f"{Colors.GREEN}YES{Colors.RESET}" if app["doze_whitelisted"] else f"{Colors.RED}NO{Colors.RESET}"
        auto_str = f"{Colors.GREEN}ALLOWED{Colors.RESET}" if app["appops"]["autostart_10008"] else f"{Colors.YELLOW}DEFAULT{Colors.RESET}"
        
        status_str = f"{Colors.GREEN}OPTIMIZED{Colors.RESET}" if (app["doze_whitelisted"] and app["appops"]["autostart_10008"]) else f"{Colors.YELLOW}RESTRICTED{Colors.RESET}"
        print(f" {app['name']:<22} | {doze_str:<23} | {auto_str:<19} | {status_str}")

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
