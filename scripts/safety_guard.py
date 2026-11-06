#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Strict Non-Destructive Safety Guard & Command Interceptor
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
from typing import List

# Ensure safe UTF-8 output on all operating systems and CI environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

class SecurityViolationError(Exception):
    """Raised when an unsafe or destructive ADB/system command is intercepted."""
    pass

# Hard prohibited tokens and commands that NO script or AI agent is ever allowed to execute
# Strict Zero-Reset, Zero-Wipe, Zero-Root, and Zero-Destruction Policy
PROHIBITED_COMMAND_PATTERNS = [
    # Factory reset / Master clear / Wipe / Format / Erase commands
    "master_clear",
    "masterclear",
    "android.intent.action.master_clear",
    "factory_reset",
    "factory-reset",
    "wipe_data",
    "--wipe_data",
    "cmd recovery",
    "recovery",
    "wipe",
    "format",
    "erase",
    "locksettings clear",
    "locksettings set-pin",
    "locksettings set-password",
    "reset-screen",
    "reset_phone",
    "reset phone",

    # Destructive package commands
    "uninstall",
    "pm clear",
    "disable-user",
    "pm disable",

    # Bootloader / Fastboot / Recovery / Download mode
    "reboot bootloader",
    "reboot-bootloader",
    "reboot recovery",
    "reboot fastboot",
    "reboot sideload",
    "reboot download",
    "reboot edl",
    "fastboot",
    "oem unlock",
    "flashing unlock",

    # Filesystem destruction
    "rm -rf /",
    "rm -rf /data",
    "rm -rf /system",
    "rm -rf /sdcard",
    "blockdev",
    "dd if=",
    "flash ",

    # Root & privilege escalation
    "su -c",
    "su ",
    "magisk",
    "kernelsu",
    "supersu",
    "setenforce 0"
]

# Protected system packages that must NEVER be restricted or disabled under any circumstances
PROTECTED_SYSTEM_PACKAGES = {
    "android",
    "com.android.systemui",
    "com.android.phone",
    "com.android.server.telecom",
    "com.android.providers.telephony",
    "com.android.settings",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
    "com.android.permissioncontroller",
    "com.google.android.permissioncontroller",
    "com.google.android.gms",          # Core Google Play Services framework
    "com.google.android.gsf",          # Google Services Framework
    "com.google.android.apps.adm",     # Google Find My Device
    "com.android.vending",             # Google Play Store (App updates & background downloads)
    "com.android.providers.downloads", # Android Download Manager
    "us.zoom.videomeetings",           # Zoom Meetings (Video conferencing & background call audio)
    "com.android.emergency",
    "com.android.dialer",
    "com.google.android.dialer",
    "com.android.mms",
    "com.google.android.apps.messaging",
    "com.google.android.inputmethod.latin", # Gboard
    "com.sohu.inputmethod.sogou",      # Chinese keyboards
    "com.baidu.input",
    "com.miui.home",                   # MIUI / HyperOS launcher
    "com.android.launcher",
    "com.android.launcher3",
    "com.oppo.launcher",
    "com.vivo.launcher",
    "com.huawei.android.launcher"
}

def is_package_protected(pkg: str) -> bool:
    """Returns True if the package is a critical system service that must never be restricted."""
    return pkg in PROTECTED_SYSTEM_PACKAGES

def assert_command_safe(cmd_tokens: List[str]) -> bool:
    """
    Inspects an ADB command before execution to guarantee:
    1. Zero root / privilege escalations
    2. Zero factory reset or data loss
    3. Zero uninstalls or deletions of user/system packages
    """
    full_cmd_str = " ".join(cmd_tokens).lower().strip()

    for pattern in PROHIBITED_COMMAND_PATTERNS:
        if pattern in full_cmd_str:
            error_msg = (
                f"\n\033[91m[SECURITY INTERCEPTOR TRIGGERED]\033[0m\n"
                f"Blocked dangerous command containing: '{pattern}'\n"
                f"Command attempted: adb {full_cmd_str}\n"
                f"Reason: Noti-Fixer strictly forbids root, uninstalls, data wipes, or destructive modifications.\n"
            )
            print(error_msg, file=sys.stderr)
            raise SecurityViolationError(f"Prohibited destructive action: '{pattern}'")

    return True

if __name__ == "__main__":
    # Self-test safety engine
    test_safe = ["shell", "dumpsys", "deviceidle", "whitelist", "+com.whatsapp"]
    test_unsafe_uninstall = ["shell", "pm", "uninstall", "-k", "--user", "0", "com.google.android.gms"]
    test_unsafe_root = ["shell", "su", "-c", "id"]
    test_unsafe_reset = ["shell", "am", "broadcast", "-a", "android.intent.action.MASTER_CLEAR"]
    test_unsafe_recovery = ["reboot", "recovery"]

    assert assert_command_safe(test_safe) is True

    try:
        assert_command_safe(test_unsafe_uninstall)
        print("FAIL: Should have blocked uninstall")
        sys.exit(1)
    except SecurityViolationError:
        pass

    try:
        assert_command_safe(test_unsafe_root)
        print("FAIL: Should have blocked root attempt")
        sys.exit(1)
    except SecurityViolationError:
        pass

    try:
        assert_command_safe(test_unsafe_reset)
        print("FAIL: Should have blocked factory reset")
        sys.exit(1)
    except SecurityViolationError:
        pass

    try:
        assert_command_safe(test_unsafe_recovery)
        print("FAIL: Should have blocked reboot recovery")
        sys.exit(1)
    except SecurityViolationError:
        pass

    print("[PASS] Safety Guard self-test passed: All destructive patterns intercepted successfully.")

