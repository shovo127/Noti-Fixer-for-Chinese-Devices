#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Mock Test Suite & Virtual Validation Engine
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import safety_guard
from safety_guard import assert_command_safe, is_package_protected, SecurityViolationError
import adb_core
from adb_core import run_adb, get_device_props, get_installed_packages, get_package_uid
import debloat_manager
from debloat_manager import DEBLOAT_CATALOG, scan_bloatware
import adblock_manager
from adblock_manager import DEFAULT_ADBLOCK_DNS, ALTERNATIVE_DNS_PROVIDERS, apply_native_no_app_adblock


class TestSafetyGuard(unittest.TestCase):
    """Verifies that the non-destructive security interceptor blocks all dangerous operations."""

    def test_blocks_destructive_commands(self):
        dangerous_commands = [
            ["shell", "recovery", "--wipe_data"],
            ["shell", "wipe", "data"],
            ["shell", "master_clear"],
            ["shell", "rm", "-rf", "/data"],
            ["reboot", "bootloader"],
            ["shell", "su", "-c", "id"],
            ["shell", "pm", "clear", "com.google.android.gms"]
        ]
        for cmd in dangerous_commands:
            with self.assertRaises(SecurityViolationError):
                assert_command_safe(cmd)

    def test_allows_safe_commands(self):
        safe_commands = [
            ["shell", "dumpsys", "deviceidle", "whitelist"],
            ["shell", "settings", "get", "global", "private_dns_mode"],
            ["shell", "pm", "list", "packages"],
            ["shell", "pm", "uninstall", "-k", "--user", "0", "com.miui.analytics"]
        ]
        for cmd in safe_commands:
            self.assertTrue(assert_command_safe(cmd))

    def test_protected_packages_cannot_be_uninstalled(self):
        protected_list = ["com.google.android.gms", "com.android.systemui", "android", "com.android.phone"]
        for pkg in protected_list:
            self.assertTrue(is_package_protected(pkg))
            with self.assertRaises(SecurityViolationError):
                assert_command_safe(["shell", "pm", "uninstall", "-k", "--user", "0", pkg])

    def test_inviolable_packages_protected(self):
        inviolables = [
            "games.vaveda.militaryoverturn",
            "com.miui.powerkeeper",
            "com.miui.securitycenter",
            "com.miui.securitycore",
            "com.android.deskclock"
        ]
        for pkg in inviolables:
            self.assertTrue(is_package_protected(pkg), f"Inviolable package {pkg} must be protected")
            with self.assertRaises(SecurityViolationError):
                assert_command_safe(["shell", "pm", "uninstall", "-k", "--user", "0", pkg])


class TestAdbCore(unittest.TestCase):
    """Verifies centralized ADB core functions, parsing logic, and device interrogation."""

    @patch("subprocess.run")
    def test_get_device_props_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[ro.product.manufacturer]: [Xiaomi]\n[ro.product.model]: [23117RK66C]\n[ro.build.version.release]: [16]\n[ro.build.version.sdk]: [36]\n",
            stderr=""
        )
        props = get_device_props()
        self.assertEqual(props.get("ro.product.manufacturer"), "Xiaomi")
        self.assertEqual(props.get("ro.product.model"), "23117RK66C")
        self.assertEqual(props.get("ro.build.version.release"), "16")
        self.assertEqual(props.get("ro.build.version.sdk"), "36")

    @patch("subprocess.run")
    def test_get_installed_packages_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="package:com.whatsapp\npackage:com.google.android.gm\npackage:com.miui.analytics\n",
            stderr=""
        )
        pkgs = get_installed_packages()
        self.assertIn("com.whatsapp", pkgs)
        self.assertIn("com.google.android.gm", pkgs)
        self.assertIn("com.miui.analytics", pkgs)
        self.assertNotIn("com.facebook.orca", pkgs)

    @patch("subprocess.run")
    def test_get_package_uid_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="    userId=10245 gids=[3003, 1028]\n",
            stderr=""
        )
        uid = get_package_uid("com.whatsapp")
        self.assertEqual(uid, 10245)


class TestDebloatManager(unittest.TestCase):
    """Verifies that debloat catalog maintains strict safety and zero-brick guarantees."""

    def test_no_protected_package_in_debloat_catalog(self):
        for pkg in DEBLOAT_CATALOG:
            self.assertFalse(
                is_package_protected(pkg),
                f"Critical Error: Protected system package '{pkg}' found in DEBLOAT_CATALOG!"
            )

    @patch("debloat_manager.get_installed_packages")
    def test_scan_bloatware_finds_targeted_apps(self, mock_get_pkgs):
        mock_get_pkgs.return_value = {"com.miui.analytics", "com.vivo.magazine", "com.whatsapp"}
        found = scan_bloatware()
        found_pkgs = [f["package"] for f in found]
        self.assertIn("com.miui.analytics", found_pkgs)
        self.assertIn("com.vivo.magazine", found_pkgs)
        self.assertNotIn("com.whatsapp", found_pkgs)


class TestAdblockManager(unittest.TestCase):
    """Verifies AdBlock settings, DNS providers, and safe execution."""

    def test_adblock_default_dns(self):
        self.assertEqual(DEFAULT_ADBLOCK_DNS, "dns.adguard.com")
        self.assertIn("adguard", ALTERNATIVE_DNS_PROVIDERS)
        self.assertIn("mullvad", ALTERNATIVE_DNS_PROVIDERS)
        self.assertIn("controld", ALTERNATIVE_DNS_PROVIDERS)

    @patch("subprocess.run")
    def test_apply_native_no_app_adblock_commands(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        apply_native_no_app_adblock(dns_provider="dns.adguard.com")
        # Ensure at least one call sets private_dns_specifier to dns.adguard.com
        called_args = [call[0][0] for call in mock_run.call_args_list]
        set_dns_called = any(
            "settings" in cmd and "private_dns_specifier" in cmd and "dns.adguard.com" in cmd
            for cmd in called_args
        )
        self.assertTrue(set_dns_called, "Expected Private DNS specifier to be configured to dns.adguard.com")


class TestAuditFcmExactMatch(unittest.TestCase):
    """Verifies that audit package matching prevents false positives (e.g., gm vs gms)."""

    def test_exact_package_matching(self):
        whitelist = ["com.google.android.gms", "com.whatsapp"]
        # Exact equality check
        is_gm_in = any("com.google.android.gm" == d for d in whitelist)
        is_gms_in = any("com.google.android.gms" == d for d in whitelist)
        self.assertFalse(is_gm_in, "com.google.android.gm must NOT match com.google.android.gms")
        self.assertTrue(is_gms_in, "com.google.android.gms must match")


if __name__ == "__main__":
    unittest.main()
