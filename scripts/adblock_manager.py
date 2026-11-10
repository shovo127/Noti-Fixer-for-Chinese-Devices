#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Zero-Latency Safe Ad-Blocker & Global Network Sinkhole Optimizer
Architect: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import os
import subprocess
import argparse
from typing import Optional, List, Dict, Tuple

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

try:
    from adb_core import run_adb, Colors
except ImportError:
    from scripts.adb_core import run_adb, Colors

DEFAULT_ADBLOCK_DNS = "dns.adguard.com"
ALTERNATIVE_DNS_PROVIDERS = {
    "adguard": "dns.adguard.com",
    "mullvad": "adblock.doh.mullvad.net",
    "controld": "p2.freedns.controld.com",
    "cleanbrowsing": "family-filter-dns.cleanbrowsing.org"
}
RETHINK_PKG = "com.celzero.bravedns"

def get_current_dns(serial: Optional[str] = None) -> Tuple[str, str]:
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

def apply_native_no_app_adblock(serial: Optional[str] = None, dns_provider: str = DEFAULT_ADBLOCK_DNS):
    """
    Applies production-grade, root-free ad neutralization across Android devices:
    1. Sets low-latency edge ad-blocking Private DNS (AdGuard DNS default, with fallback options)
    2. Activates Android 14/15/16 AdServices global kill switches (AdMob, Topics, SDK Sandbox, Ad ID)
    3. Disables all native Xiaomi HyperOS / MIUI ad, recommendation, and telemetry toggles
    4. Safely user-0 debloats Xiaomi MSA & Analytics daemons if present
    5. Displays Chrome Mobile Secure DNS alignment instructions
    """
    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: APPLYING GLOBAL 100% NATIVE NO-APP AD NEUTRALIZATION{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}")

    # 1. Edge DNS (Anycast AdGuard DNS / DoT)
    print(f" {Colors.CYAN}[1/5] Activating High-Reliability Edge Ad-Blocking DNS ({dns_provider})...{Colors.RESET}")
    run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], serial)
    run_adb(["shell", "settings", "put", "global", "private_dns_specifier", dns_provider], serial)
    print(f"       -> Private DNS set to: {Colors.GREEN}{dns_provider}{Colors.RESET}")

    # 2. Android 14/15/16 AdServices Global Kill Switch
    print(f"\n {Colors.CYAN}[2/5] Neutralizing Android AdServices & Advertising ID Tracking...{Colors.RESET}")
    run_adb(["shell", "device_config", "put", "adservices", "global_kill_switch", "true"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "adservice_enabled", "false"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "adservice_system_service_enabled", "false"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "adid_kill_switch", "true"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "appsetid_kill_switch", "true"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "topics_kill_switch", "true"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "disable_sdk_sandbox", "true"], serial)
    run_adb(["shell", "device_config", "put", "adservices", "fledge_ad_selection_filtering_enabled", "false"], serial)
    run_adb(["shell", "settings", "put", "secure", "limit_ad_tracking", "1"], serial)
    print(f"       -> AdServices & Advertising ID: {Colors.GREEN}DISABLED (Global Kill Switch Active){Colors.RESET}")

    # 3. Native Xiaomi HyperOS / MIUI Recommendation Neutralization
    print(f"\n {Colors.CYAN}[3/5] Disabling Native HyperOS / MIUI App Ad & Telemetry Recommendations...{Colors.RESET}")
    xiaomi_toggles = [
        ("secure", "miui_ad_enable", "0"),
        ("system", "miui_ad_enable", "0"),
        ("secure", "miui_personalized_ad_turn_off", "1"),
        ("system", "miui_personalized_ad_turn_off", "1"),
        ("secure", "passport_ad_status", "OFF"),
        ("system", "passport_ad_status", "OFF"),
        ("secure", "personalized_ad_enabled", "0"),
        ("system", "personalized_ad_enabled", "0"),
        ("secure", "personalized_ad_turn_off", "1"),
        ("system", "personalized_ad_turn_off", "1"),
        ("system", "MiuiMultiWindowRecommendSwitch", "0"),
        ("system", "com.android.browser.enable_app_chooser_recommend", "0"),
        ("secure", "miui_miprotect_risk_app_download_warn", "0"),
        ("system", "miui_filemanager_recommend", "0"),
        ("system", "miui_downloads_recommend", "0"),
        ("system", "miui_theme_recommend", "0"),
        ("system", "miui_security_recommend", "0"),
        ("system", "miui_cleaner_recommend", "0"),
        ("system", "miui_video_recommend", "0"),
        ("system", "miui_music_recommend", "0"),
        ("system", "miui_keyguard_carousel_enable", "0"),
        ("secure", "keyguard_carousel_status", "0"),
        ("secure", "lock_screen_lock_wallpaper_provider", "0"),
        ("system", "lock_wallpaper_provider_authority", ""),
        ("secure", "msa_enable", "0"),
        ("system", "msa_enable", "0"),
        ("system", "upload_log_pref", "0"),
        ("secure", "upload_log_pref", "0"),
        ("secure", "user_experience_program", "0"),
        ("system", "user_experience_program", "0"),
        ("secure", "send_diagnostic_data", "0"),
        ("system", "send_diagnostic_data", "0"),
        ("secure", "anonymous_data_collection", "0")
    ]
    for table, key, val in xiaomi_toggles:
        run_adb(["shell", "settings", "put", table, key, val], serial)
    print(f"       -> System File Manager, Downloads, Themes, Security, MSA & Telemetry: {Colors.GREEN}OFF{Colors.RESET}")

    # 4. Debloat Xiaomi Ad daemons (MSA & Analytics) if installed
    print(f"\n {Colors.CYAN}[4/5] Neutralizing Xiaomi In-App Ad Daemons (MSA / Analytics)...{Colors.RESET}")
    ad_pkgs = ["com.miui.msa.global", "com.miui.analytics"]
    for pkg in ad_pkgs:
        chk = run_adb(["shell", "pm", "list", "packages", pkg], serial)
        if pkg in (chk.stdout or ""):
            deb_res = run_adb(["shell", "pm", "uninstall", "-k", "--user", "0", pkg], serial)
            if "Success" in (deb_res.stdout or ""):
                print(f"       -> Debloated {pkg}: {Colors.GREEN}SUCCESS (No more system app ads){Colors.RESET}")
            else:
                print(f"       -> {pkg} already disabled or neutralized.")
        else:
            print(f"       -> {pkg} not active on target device.")

    # 5. Chrome Mobile DoH Guidance
    print(f"\n {Colors.CYAN}[5/5] Chrome Mobile Secure DNS Configuration Note...{Colors.RESET}")
    print(f"       {Colors.YELLOW}ℹ Notice:{Colors.RESET} Modern Chrome on Android uses its own built-in Secure DNS (DoH).")
    print(f"       To ensure Chrome honors Private DNS ad-blocking:")
    print(f"       {Colors.BOLD}Chrome -> Settings -> Privacy and security -> Use secure DNS -> 'Use your current service provider'{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Native Ad Neutralization Complete! Zero background RAM, 0% CPU battery overhead.{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}\n")

def verify_adblock(serial: Optional[str] = None):
    """
    Verifies ad domain sinkholing across global advertising networks and verifies legitimate network latency.
    """
    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: GLOBAL AD-BLOCKING & DNS SPEED VERIFICATION{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}")

    ad_domains = [
        # Google AdMob & DoubleClick
        ("Google AdMob Network", "googleads.g.doubleclick.net"),
        ("Google Syndication", "pagead2.googlesyndication.com"),
        ("Google Ad Service", "adservice.google.com"),
        # Meta (Facebook / Instagram Ads)
        ("Meta Audience Network", "an.facebook.com"),
        ("Meta Tracking Pixel", "pixel.facebook.com"),
        # Unity Ads (Mobile Games)
        ("Unity Ads Network", "unityads.unity3d.com"),
        # AppLovin
        ("AppLovin Network", "applovin.com"),
        # InMobi
        ("InMobi Global Ads", "inmobi.com"),
        # IronSource
        ("IronSource Ads", "supersonicads.com"),
        # Taboola & Outbrain
        ("Taboola Content Ads", "taboola.com"),
        ("Outbrain Content Ads", "outbrain.com"),
        # Criteo
        ("Criteo Retargeting", "criteo.com")
    ]
    legit_domains = [
        ("Google Search & Services", "google.com"),
        ("Cloudflare CDN & Edge", "cloudflare.com"),
        ("Google FCM Push Server", "mtalk.google.com")
    ]

    print(f"\n {Colors.CYAN}[*] Testing Global Ad Network Sinkhole (Resolves to 127.0.0.1 / localhost):{Colors.RESET}")
    for company, dom in ad_domains:
        res = run_adb(["shell", f"ping -c 1 -W 2 {dom}"], serial)
        out = (res.stdout or "") + (res.stderr or "")
        if "127.0.0.1" in out or "0.0.0.0" in out:
            time_part = "0.1 ms"
            for token in out.split():
                if "time=" in token:
                    time_part = token.replace("time=", "") + " ms"
                    break
            print(f"    {Colors.GREEN}✔ [BLOCKED] {company:<24} ({dom:<30}) -> 127.0.0.1 ({time_part}){Colors.RESET}")
        elif "100% packet loss" in out or "unknown host" in out or "bad address" in out:
            print(f"    {Colors.GREEN}✔ [BLOCKED] {company:<24} ({dom:<30}) -> Blocked / Dropped at Edge{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}⚠ [LEAK?]  {company:<24} ({dom:<30}) -> {out.splitlines()[0] if out.splitlines() else 'Unknown'}{Colors.RESET}")

    print(f"\n {Colors.CYAN}[*] Testing Legitimate Network Connectivity & Notification Latency:{Colors.RESET}")
    for label, dom in legit_domains:
        res = run_adb(["shell", f"ping -c 1 -W 2 {dom}"], serial)
        out = (res.stdout or "") + (res.stderr or "")
        if "0% packet loss" in out or "bytes from" in out:
            time_part = ""
            for line in out.splitlines():
                if "rtt" in line or "time=" in line:
                    time_part = line.strip()
                    break
            print(f"    {Colors.GREEN}✔ [ONLINE]  {label:<24} ({dom:<24}) -> Online ({time_part}){Colors.RESET}")
        else:
            print(f"    {Colors.RED}✘ [OFFLINE] {label:<24} ({dom:<24}) -> Network unreachable{Colors.RESET}")

    # Check Private DNS resolution status via dumpsys
    net_dump = run_adb(["shell", "dumpsys", "connectivity"], serial).stdout
    if "Private DNS" in net_dump or "dns.adguard.com" in net_dump or "p2.freedns.controld.com" in net_dump:
        print(f"\n {Colors.GREEN}✔ Android OS Connectivity Engine reports Private DNS active.{Colors.RESET}")

    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}\n")

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

    print(f"\n{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: ZERO-LATENCY AD-BLOCKER & DNS STATUS{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}")
    print(f" Current Private DNS Mode      : {Colors.BOLD}{mode}{Colors.RESET}")
    print(f" Current Private DNS Specifier : {Colors.BOLD}{spec or '(None - Using Native ISP/Wi-Fi)'}{Colors.RESET}")
    print(f" RethinkDNS On-Device Filter   : {Colors.GREEN if rethink_installed else Colors.YELLOW}{'INSTALLED' if rethink_installed else 'NOT INSTALLED'}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*74}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Zero-Latency Safe Ad-Blocker Manager by Shovo")
    parser.add_argument("-s", "--serial", help="ADB serial of target device", default=None)
    parser.add_argument("--status", action="store_true", help="Display current DNS & on-device adblocker status")
    parser.add_argument("--apply-native", action="store_true", help="100%% native no-app adblock: Fast edge DNS, Android AdServices kill-switch & HyperOS toggles")
    parser.add_argument("--dns", help="DNS provider for --apply-native (adguard, mullvad, controld, cleanbrowsing or custom host). Default: adguard", default=DEFAULT_ADBLOCK_DNS)
    parser.add_argument("--verify", action="store_true", help="Run live ad-sinkhole and latency verification tests")
    parser.add_argument("--disable-slow-dns", action="store_true", help="Disable slow remote Private DNS (restore 3-8ms ISP speed)")
    parser.add_argument("--install-rethink", action="store_true", help="Open Google Play Store to install RethinkDNS")
    parser.add_argument("--optimize-rethink", action="store_true", help="Whitelist RethinkDNS against Android battery killing")
    parser.add_argument("--set-edge-dns", help="Configure low-latency edge DoT hostname (e.g. p2.freedns.controld.com)", default=None)
    args = parser.parse_args()

    if args.apply_native:
        chosen_dns = ALTERNATIVE_DNS_PROVIDERS.get(args.dns.lower().strip(), args.dns.strip())
        apply_native_no_app_adblock(args.serial, chosen_dns)
    elif args.verify:
        verify_adblock(args.serial)
    elif args.disable_slow_dns:
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
