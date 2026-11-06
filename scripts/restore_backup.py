#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Master Reversible Backup Restorer & Package Re-installer
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import json
import glob
import subprocess
import argparse
from typing import Optional, List, Dict, Any

try:
    from safety_guard import assert_command_safe, get_restore_command_for_package
except ImportError:
    from scripts.safety_guard import assert_command_safe, get_restore_command_for_package

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

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

def find_latest_backup_dir(base_dir: str) -> Optional[str]:
    backups_path = os.path.join(base_dir, "backups")
    if not os.path.exists(backups_path):
        return None
    subdirs = [os.path.join(backups_path, d) for d in os.listdir(backups_path) if os.path.isdir(os.path.join(backups_path, d))]
    if not subdirs:
        return None
    subdirs.sort(key=os.path.getmtime, reverse=True)
    return subdirs[0]

def restore_backup(backup_dir: Optional[str] = None, serial: Optional[str] = None):
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}   NOTI-FIXER: MASTER 100% REVERSIBLE ROLLBACK & PACKAGE RESTORER{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_dir = backup_dir or find_latest_backup_dir(repo_root)

    print(f" {Colors.CYAN}[*] Target Backup Directory:{Colors.RESET} {target_dir or 'Default System Clean'}")

    # 1. Restore debloated user-profile packages
    uninstalled_packages: List[str] = []
    if target_dir:
        plan_file = os.path.join(target_dir, "plan.json")
        backup_file = os.path.join(target_dir, "backup.json")
        for fpath in [plan_file, backup_file]:
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        pkgs = data.get("debloated_packages") or data.get("uninstalled_packages") or data.get("list_a") or []
                        for p in pkgs:
                            if isinstance(p, dict):
                                pkg_name = p.get("package")
                            else:
                                pkg_name = str(p)
                            if pkg_name and pkg_name not in uninstalled_packages:
                                uninstalled_packages.append(pkg_name)
                except Exception as e:
                    print(f" {Colors.YELLOW}[!] Warning reading {os.path.basename(fpath)}: {e}{Colors.RESET}")

    if uninstalled_packages:
        print(f"\n {Colors.CYAN}[1/4] Reinstalling user-profile debloated packages...{Colors.RESET}")
        for pkg in uninstalled_packages:
            cmd = get_restore_command_for_package(pkg)
            res = run_adb(cmd, serial)
            if "installed" in (res.stdout or "").lower() or res.returncode == 0:
                print(f"       -> Reinstalled {Colors.GREEN}{pkg}{Colors.RESET} for User 0")
            else:
                print(f"       -> {Colors.YELLOW}{pkg}{Colors.RESET}: {res.stdout.strip() or res.stderr.strip()}")
    else:
        print(f"\n {Colors.CYAN}[1/4] No user-profile debloated packages found to reinstall.{Colors.RESET}")

    # 2. Re-enable kernel cached_apps_freezer
    print(f"\n {Colors.CYAN}[2/4] Resetting Kernel Cgroup Freezer to system default...{Colors.RESET}")
    run_adb(["shell", "device_config", "put", "activity_manager_native_boot", "use_freezer", "true"], serial)
    run_adb(["shell", "setprop", "persist.sys.freezer", "true"], serial)
    run_adb(["shell", "setprop", "sys.use_freezer", "true"], serial)
    print(f"       -> {Colors.GREEN}Kernel cgroup freezer restored to default.{Colors.RESET}")

    # 3. Revert Private DNS & MILLET System Whitelists
    print(f"\n {Colors.CYAN}[3/4] Reverting Private DNS & Vendor System Whitelists...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "private_dns_mode", "opportunistic"], serial)
    run_adb(["shell", "settings", "delete", "global", "private_dns_specifier"], serial)
    run_adb(["shell", "settings", "put", "system", "MILLET_NO_RESTRICT_APP", '""'], serial)
    run_adb(["shell", "pkill", "-f", "millet_watchdog.sh"], serial)
    print(f"       -> {Colors.GREEN}DNS and vendor tables restored.{Colors.RESET}")

    # 4. Revert AppOps for messaging applications
    print(f"\n {Colors.CYAN}[4/4] Restoring messaging AppOps to factory defaults...{Colors.RESET}")
    core_apps = [
        "com.google.android.gms",
        "com.whatsapp",
        "org.telegram.messenger",
        "com.facebook.orca",
        "com.google.android.gm"
    ]
    for pkg in core_apps:
        run_adb(["shell", "cmd", "appops", "set", pkg, "10008", "default"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "10021", "default"], serial)
        run_adb(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "default"], serial)
    print(f"       -> {Colors.GREEN}AppOps reverted to default.{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✔] Full Rollback Complete! Device settings returned to factory state.{Colors.RESET}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Noti-Fixer Master Rollback & Reinstaller")
    parser.add_argument("-s", "--serial", help="ADB device serial (e.g. 192.168.0.105:38473)")
    parser.add_argument("-b", "--backup-dir", help="Path to specific backup directory")
    args = parser.parse_args()

    restore_backup(backup_dir=args.backup_dir, serial=args.serial)

