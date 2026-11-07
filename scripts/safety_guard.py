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
    "com.android.updater",             # HyperOS / MIUI System Updater
    "com.xiaomi.market",               # Xiaomi App Store (System App updates & Widgets)
    "com.miui.personalassistant",      # Xiaomi App Vault & System Widgets
    "com.android.htmlviewer",          # Essential: Contains CloudSettingsProvider required by SecurityCenter
    "us.zoom.videomeetings",           # Zoom Meetings (Video conferencing & background call audio)
    "com.google.android.webview",      # Android System WebView
    "com.android.webview",
    "com.android.camera",              # System Camera
    "com.google.android.GoogleCamera",
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
    """Returns True if the package is a critical system service that must never be restricted or uninstalled."""
    if not pkg:
        return False
    pkg_clean = pkg.lower().strip()
    return pkg_clean in PROTECTED_SYSTEM_PACKAGES

def get_restore_command_for_package(pkg: str) -> List[str]:
    """Returns the ADB command tokens required to restore a user-profile debloated package."""
    return ["shell", "cmd", "package", "install-existing", "--user", "0", pkg.strip()]

def assert_command_safe(cmd_tokens: List[str], approved_plan_packages: List[str] = None) -> bool:
    """
    Inspects an ADB command before execution to guarantee:
    1. Zero root / privilege escalations
    2. Zero factory reset or data loss
    3. Zero blind uninstalls (strictly permits 'pm uninstall -k --user 0 <pkg>' for vetted packages)
    4. Zero disabling of critical system frameworks
    """
    full_cmd_str = " ".join(cmd_tokens).lower().strip()

    # 1. Check for hard prohibited reset, wipe, bootloader, recovery, and root patterns
    for pattern in PROHIBITED_COMMAND_PATTERNS:
        if pattern == "uninstall":
            continue  # Handled with precision check below
        if pattern in full_cmd_str:
            error_msg = (
                f"\n\033[91m[SECURITY INTERCEPTOR TRIGGERED]\033[0m\n"
                f"Blocked dangerous command containing: '{pattern}'\n"
                f"Command attempted: adb {full_cmd_str}\n"
                f"Reason: Noti-Fixer strictly forbids root, uninstalls, data wipes, or destructive modifications.\n"
            )
            print(error_msg, file=sys.stderr)
            raise SecurityViolationError(f"Prohibited destructive action: '{pattern}'")

    # 2. Precision check for uninstalls
    if "uninstall" in full_cmd_str:
        # Permitted ONLY in the exact user-profile debloat form: pm uninstall -k --user 0 <pkg>
        # Reversible via: cmd package install-existing --user 0 <pkg>
        tokens_lower = [t.lower().strip() for t in cmd_tokens]
        
        # Verify mandatory safe flags
        has_pm = "pm" in tokens_lower
        has_uninstall = "uninstall" in tokens_lower
        has_k = "-k" in tokens_lower
        has_user = "--user" in tokens_lower
        has_zero = "0" in tokens_lower

        if not (has_pm and has_uninstall and has_k and has_user and has_zero):
            error_msg = (
                f"\n\033[91m[SECURITY INTERCEPTOR TRIGGERED]\033[0m\n"
                f"Blocked non-standard uninstall command: adb {full_cmd_str}\n"
                f"Reason: Noti-Fixer permits debloat ONLY via the safe, reversible user-profile format:\n"
                f"        'pm uninstall -k --user 0 <package_name>'\n"
            )
            print(error_msg, file=sys.stderr)
            raise SecurityViolationError("Non-standard uninstall syntax prohibited")

        # Extract target package name (last token or argument after '0')
        try:
            user_idx = tokens_lower.index("--user")
            if user_idx + 2 < len(cmd_tokens):
                target_pkg = cmd_tokens[user_idx + 2].strip()
            else:
                target_pkg = cmd_tokens[-1].strip()
        except Exception:
            target_pkg = cmd_tokens[-1].strip()

        # Check if the target package is protected
        if is_package_protected(target_pkg):
            error_msg = (
                f"\n\033[91m[SECURITY INTERCEPTOR TRIGGERED]\033[0m\n"
                f"Blocked uninstall of protected system package: '{target_pkg}'\n"
                f"Reason: Package is vital for Android system integrity, Google Play framework, or core communications.\n"
            )
            print(error_msg, file=sys.stderr)
            raise SecurityViolationError(f"Attempted uninstall of protected package '{target_pkg}'")

        # If an approved plan package list is provided, enforce it
        if approved_plan_packages is not None:
            approved_lower = [p.lower().strip() for p in approved_plan_packages]
            if target_pkg.lower() not in approved_lower:
                error_msg = (
                    f"\n\033[91m[SECURITY INTERCEPTOR TRIGGERED]\033[0m\n"
                    f"Blocked uninstall of unapproved package: '{target_pkg}'\n"
                    f"Reason: Package was not confirmed in the user-approved debloat list (List A).\n"
                )
                print(error_msg, file=sys.stderr)
                raise SecurityViolationError(f"Package '{target_pkg}' not in approved plan")

    return True

if __name__ == "__main__":
    # Self-test safety engine
    test_safe = ["shell", "dumpsys", "deviceidle", "whitelist", "+com.whatsapp"]
    test_safe_debloat = ["shell", "pm", "uninstall", "-k", "--user", "0", "com.miui.analytics"]
    test_unsafe_protected_debloat = ["shell", "pm", "uninstall", "-k", "--user", "0", "com.google.android.gms"]
    test_unsafe_blind_uninstall = ["shell", "pm", "uninstall", "com.miui.analytics"]
    test_unsafe_disable = ["shell", "pm", "disable-user", "--user", "0", "com.miui.analytics"]
    test_unsafe_clear = ["shell", "pm", "clear", "com.miui.analytics"]
    test_unsafe_root = ["shell", "su", "-c", "id"]
    test_unsafe_reset = ["shell", "am", "broadcast", "-a", "android.intent.action.MASTER_CLEAR"]
    test_unsafe_recovery = ["reboot", "recovery"]

    # 1. Safe commands must pass
    assert assert_command_safe(test_safe) is True
    assert assert_command_safe(test_safe_debloat) is True

    # 2. Protected system package uninstall must be blocked
    try:
        assert_command_safe(test_unsafe_protected_debloat)
        print("FAIL: Should have blocked protected package uninstall")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 3. Blind / non-standard uninstalls must be blocked
    try:
        assert_command_safe(test_unsafe_blind_uninstall)
        print("FAIL: Should have blocked blind uninstall")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 4. Package disablings and clearing must be blocked
    try:
        assert_command_safe(test_unsafe_disable)
        print("FAIL: Should have blocked pm disable-user")
        sys.exit(1)
    except SecurityViolationError:
        pass

    try:
        assert_command_safe(test_unsafe_clear)
        print("FAIL: Should have blocked pm clear")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 5. Root attempt must be blocked
    try:
        assert_command_safe(test_unsafe_root)
        print("FAIL: Should have blocked root attempt")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 6. Factory reset attempt must be blocked
    try:
        assert_command_safe(test_unsafe_reset)
        print("FAIL: Should have blocked factory reset")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 7. Recovery reboot attempt must be blocked
    try:
        assert_command_safe(test_unsafe_recovery)
        print("FAIL: Should have blocked reboot recovery")
        sys.exit(1)
    except SecurityViolationError:
        pass

    # 8. Test restore command generator
    restore_cmd = get_restore_command_for_package("com.miui.analytics")
    assert restore_cmd == ["shell", "cmd", "package", "install-existing", "--user", "0", "com.miui.analytics"]

    print("[PASS] Safety Guard self-test passed: All destructive patterns intercepted successfully.")

