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

class SecurityViolationError(Exception):
    """Raised when an unsafe or destructive ADB/system command is intercepted."""
    pass

# Hard prohibited tokens and commands that NO script or AI agent is ever allowed to execute
PROHIBITED_COMMAND_PATTERNS = [
    "uninstall",
    "pm clear",
    "disable-user",
    "pm disable",
    "reboot bootloader",
    "reboot recovery",
    "reboot fastboot",
    "fastboot",
    "recovery",
    "factory_reset",
    "wipe",
    "format",
    "erase",
    "rm -rf /",
    "rm -rf /data",
    "rm -rf /system",
    "su -c",
    "su ",
    "magisk",
    "kernelsu",
    "supersu",
    "blockdev",
    "dd if=",
    "flash ",
    "setenforce 0"
]

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

    print("✔ Safety Guard self-test passed: All destructive patterns intercepted successfully.")
