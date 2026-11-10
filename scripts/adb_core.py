#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Centralized Universal ADB Core & Device Interrogation Engine
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
from typing import List, Optional, Dict, Set, Tuple

# Ensure safe UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import safety guard
try:
    from safety_guard import assert_command_safe, SecurityViolationError
except ImportError:
    try:
        from scripts.safety_guard import assert_command_safe, SecurityViolationError
    except ImportError:
        def assert_command_safe(cmd: List[str], approved: Optional[List[str]] = None) -> bool:
            return True
        class SecurityViolationError(Exception):
            pass

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

_connected_serials: Set[str] = set()

def run_adb(cmd: List[str], serial: Optional[str] = None, timeout: int = 20, check_safety: bool = True) -> subprocess.CompletedProcess:
    """
    Executes an ADB command with:
    - Pre-execution non-destructive safety validation
    - Seamless wireless IP:PORT auto-connection
    - Automatic error recovery and timeout containment
    """
    if check_safety:
        assert_command_safe(cmd)

    base = ["adb"]
    if serial:
        if ":" in serial and serial not in _connected_serials:
            subprocess.run(["adb", "connect", serial], capture_output=True, text=True, check=False)
            _connected_serials.add(serial)
        base.extend(["-s", serial])
    base.extend(cmd)

    try:
        res = subprocess.run(base, capture_output=True, text=True, timeout=timeout, check=False)
        # Handle wireless drops on the fly
        if serial and ":" in serial and ("not found" in (res.stderr or "").lower() or "device offline" in (res.stderr or "").lower()):
            subprocess.run(["adb", "connect", serial], capture_output=True, text=True, check=False)
            res = subprocess.run(base, capture_output=True, text=True, timeout=timeout, check=False)
        return res
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(base, returncode=-1, stdout="", stderr="Error: ADB command timed out")
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: 'adb' executable was not found in your system PATH.{Colors.RESET}", file=sys.stderr)
        print(f"    Please install Android Platform Tools or add adb to PATH.", file=sys.stderr)
        return subprocess.CompletedProcess(base, returncode=127, stdout="", stderr="adb not found in PATH")

def is_device_connected(serial: Optional[str] = None) -> bool:
    """Checks whether the target device or any device is currently connected and authorized."""
    res = run_adb(["get-state"], serial=serial, check_safety=False)
    return res.returncode == 0 and "device" in res.stdout.strip().lower()

def get_device_props(serial: Optional[str] = None) -> Dict[str, str]:
    """Retrieves critical device metadata (brand, model, SDK, OS version) safely."""
    res = run_adb(["shell", "getprop"], serial=serial, check_safety=False)
    props: Dict[str, str] = {}
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("[") and "]: [" in line:
                key, val = line.split("]: [", 1)
                key = key.lstrip("[").strip()
                val = val.rstrip("]").strip()
                props[key] = val
    return props

def get_installed_packages(serial: Optional[str] = None, user: Optional[int] = 0, uninstalled: bool = False) -> Set[str]:
    """Returns set of package names currently installed on the target device."""
    cmd = ["shell", "pm", "list", "packages"]
    if uninstalled:
        cmd.append("-u")
    if user is not None:
        cmd.extend(["--user", str(user)])

    res = run_adb(cmd, serial=serial, check_safety=False)
    packages: Set[str] = set()
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                pkg = line.replace("package:", "").strip()
                if pkg:
                    packages.add(pkg)
    return packages

def get_package_uid(pkg: str, serial: Optional[str] = None) -> Optional[int]:
    """Retrieves the integer Linux UID of an installed application."""
    if not pkg:
        return None
    res = run_adb(["shell", f"dumpsys package {pkg} | grep userId="], serial=serial, check_safety=False)
    for line in res.stdout.splitlines():
        if "userId=" in line:
            parts = line.split("userId=")
            if len(parts) > 1:
                uid_str = parts[1].strip().split()[0]
                try:
                    return int(uid_str)
                except ValueError:
                    pass
    return None
