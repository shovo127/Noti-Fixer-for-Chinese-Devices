#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Zero-Latency Safe Ad-Blocker & Local Loopback Optimizer
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

RETHINK_PKG = "com.celzero.bravedns"

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

def get_current_dns(serial: Optional[str] = None) -> (str, str):
    mode = run_adb(["shell", "settings", "get", "global", "private_dns_mode"], serial).stdout.strip()
    spec = run_adb(["shell", "settings", "get", "global", "private_dns_specifier"], serial).stdout.strip()
    return mode or "off", spec or ""

def disable_slow_dns(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}[*] Disabling Slow Remote Private DNS...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "private_dns_mode", "off"], serial)
    run_adb(["shell", "settings", "put", "global", "private_dns_specifier", ""], serial)
    print(f"    {Colors.GREEN}✔ Remote Private DNS disabled. Phone restored to ultra-fast native ISP / Local latency (3-8ms).{Colors.RESET}")

def set_edge_dns(specifier: str, serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}[*] Configuring Ultra-Low Latency Anycast Edge DNS ({specifier})...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], serial)
    run_adb(["shell", "settings", "put", "global", "private_dns_specifier", specifier], serial)
    print(f"    {Colors.GREEN}✔ Private DNS set to: {specifier}{Colors.RESET}")

def open_rethink_in_store(serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}[*] Launching Google Play Store to install RethinkDNS (Zero-Latency Loopback)...{Colors.RESET}")
    res = run_adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"market://details?id={RETHINK_PKG}", "com.android.vending"], serial)
    if res.returncode == 0:
        print(f"    {Colors.GREEN}✔ Opened Google Play Store page on your phone.{Colors.RESET}")
        print(f"    {Colors.YELLOW}👉 Please tap 'Install' on your phone screen.{Colors.RESET}")
    else:
        print(f"    {Colors.YELLOW}[i] Play store intent returned: {res.stderr or res.stdout}{Colors.RESET}")

def optimize_rethink_service(serial: Optional[str] = None):
    installed_res = run_adb(["shell", "pm", "list", "packages", RETHINK_PKG], serial)
    if RETHINK_PKG not in installed_res.stdout:
        print(f"\n{Colors.YELLOW}[!] RethinkDNS ({RETHINK_PKG}) is not yet installed on the phone.{Colors.RESET}")
        print(f"    Install it from Google Play Store or F-Droid first, then re-run this command.")
        return

    print(f"\n{Colors.CYAN}[*] Whitelisting RethinkDNS Local Loopback Daemon against OS Killing...{Colors.RESET}")
    # 1. Doze whitelist
    run_adb(["shell", "dumpsys", "deviceidle", "whitelist", f"+{RETHINK_PKG}"], serial)
    # 2. Standby bucket 5 (Exempted)
    run_adb(["shell", "am", "set-standby-bucket", RETHINK_PKG, "5"], serial)
    # 3. AppOps
    run_adb(["shell", "cmd", "appops", "set", RETHINK_PKG, "10008", "allow"], serial) # Autostart
    run_adb(["shell", "cmd", "appops", "set", RETHINK_PKG, "10021", "allow"], serial) # Secondary autostart
    run_adb(["shell", "cmd", "appops", "set", RETHINK_PKG, "RUN_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", RETHINK_PKG, "RUN_ANY_IN_BACKGROUND", "allow"], serial)
    run_adb(["shell", "cmd", "appops", "set", RETHINK_PKG, "WAKE_LOCK", "allow"], serial)

    # 4. In HyperOS MILLET whitelist
    millet = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial).stdout.strip()
    if RETHINK_PKG not in millet and millet != "null":
        new_millet = f"{millet},{RETHINK_PKG}"
        run_adb(["shell", "settings", "put", "system", "MILLET_NO_RESTRICT_APP", new_millet], serial)

    print(f"    {Colors.GREEN}✔ RethinkDNS daemon successfully optimized (Bucket 5 / Doze Exempted / Autostart Granted).{Colors.RESET}")

def print_status(serial: Optional[str] = None):
    mode, spec = get_current_dns(serial)
    rethink_check = run_adb(["shell", "pm", "list", "packages", RETHINK_PKG], serial).stdout
    rethink_installed = RETHINK_PKG in rethink_check

    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: ZERO-LATENCY AD-BLOCKER & DNS STATUS{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f" Current Private DNS Mode      : {Colors.BOLD}{mode}{Colors.RESET}")
    print(f" Current Private DNS Specifier : {Colors.BOLD}{spec or '(None - Using Native ISP/Wi-Fi)'}{Colors.RESET}")
    print(f" RethinkDNS On-Device Filter   : {Colors.GREEN if rethink_installed else Colors.YELLOW}{'INSTALLED' if rethink_installed else 'NOT INSTALLED'}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Zero-Latency Safe Ad-Blocker Manager by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--status", action="store_true", help="Display current DNS & on-device adblocker status")
    parser.add_argument("--disable-slow-dns", action="store_true", help="Disable slow remote Private DNS (restore 3-8ms ISP speed)")
    parser.add_argument("--install-rethink", action="store_true", help="Open Google Play Store to install RethinkDNS")
    parser.add_argument("--optimize-rethink", action="store_true", help="Whitelist RethinkDNS against Android battery killing")
    parser.add_argument("--set-edge-dns", help="Configure low-latency edge DoT hostname (e.g. p2.freedns.controld.com)", default=None)
    args = parser.parse_args()

    if args.disable_slow_dns:
        disable_slow_dns(args.serial)
    elif args.install_rethink:
        open_rethink_in_store(args.serial)
    elif args.optimize_rethink:
        optimize_rethink_service(args.serial)
    elif args.set_edge_dns:
        set_edge_dns(args.set_edge_dns, args.serial)
    else:
        print_status(args.serial)

if __name__ == "__main__":
    main()
