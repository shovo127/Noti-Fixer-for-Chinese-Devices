#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Device Detection & Fingerprinting Specialist
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import subprocess
import json
import argparse
from typing import Dict, Any, Optional, List

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def run_adb(cmd: List[str], serial: Optional[str] = None) -> subprocess.CompletedProcess:
    base = ["adb"]
    if serial:
        base.extend(["-s", serial])
    base.extend(cmd)
    try:
        return subprocess.run(base, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: 'adb' executable was not found in system PATH.{Colors.RESET}")
        print(f"    Please install Android Platform Tools and add 'adb' to PATH.")
        sys.exit(1)

def get_connected_devices() -> List[Dict[str, str]]:
    result = run_adb(["devices", "-l"])
    devices = []
    lines = result.stdout.strip().splitlines()
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 2:
            serial, state = parts[0], parts[1]
            extra = " ".join(parts[2:]) if len(parts) > 2 else ""
            devices.append({"serial": serial, "state": state, "info": extra})
    return devices

def get_prop(prop_name: str, serial: Optional[str] = None) -> str:
    res = run_adb(["shell", "getprop", prop_name], serial)
    return res.stdout.strip()

def detect_device_profile(serial: Optional[str] = None) -> Dict[str, Any]:
    devices = get_connected_devices()
    if not devices:
        return {"error": "No Android devices connected via ADB."}
    
    device_obj = None
    if serial:
        matched = [d for d in devices if d["serial"] == serial]
        if not matched:
            return {"error": f"Device with serial '{serial}' not found."}
        device_obj = matched[0]
    else:
        # Default to first authorized device
        authorized = [d for d in devices if d["state"] == "device"]
        if not authorized:
            return {
                "error": "Device found but unauthorized or offline. Please accept the USB/Wireless debugging prompt on your phone screen.",
                "devices": devices
            }
        device_obj = authorized[0]
        serial = device_obj["serial"]

    brand = get_prop("ro.product.brand", serial).lower()
    manufacturer = get_prop("ro.product.manufacturer", serial).lower()
    model = get_prop("ro.product.model", serial)
    name = get_prop("ro.product.name", serial)
    android_version = get_prop("ro.build.version.release", serial)
    sdk_version = get_prop("ro.build.version.sdk", serial)
    build_id = get_prop("ro.build.display.id", serial)
    
    # Specific ROM Fingerprinting
    hyperos_ver = get_prop("ro.mi.os.version.incremental", serial)
    miui_ver = get_prop("ro.miui.ui.version.name", serial)
    vivo_os = get_prop("ro.vivo.os.build.display.id", serial) or get_prop("ro.vivo.rom.version", serial)
    coloros_ver = get_prop("ro.build.version.oplusrom", serial) or get_prop("ro.build.version.opporom", serial)
    harmony_ver = get_prop("ro.build.version.emui", serial) or get_prop("ro.huawei.build.version.incremental", serial)
    
    rom_family = "AOSP / Stock Android"
    rom_detail = "Standard Android"

    if hyperos_ver or "hyperos" in build_id.lower():
        rom_family = "Xiaomi HyperOS"
        rom_detail = f"HyperOS {hyperos_ver or build_id}"
    elif miui_ver or brand in ["xiaomi", "redmi", "poco"]:
        rom_family = "Xiaomi HyperOS / MIUI"
        rom_detail = f"MIUI {miui_ver} ({build_id})"
    elif vivo_os or brand in ["vivo", "iqoo"]:
        rom_family = "Vivo OriginOS / FuntouchOS"
        rom_detail = f"OriginOS/Funtouch {vivo_os or build_id}"
    elif coloros_ver or brand in ["oppo", "oneplus", "realme"]:
        rom_family = "Oppo ColorOS / OxygenOS / RealmeUI"
        rom_detail = f"ColorOS/RealmeUI {coloros_ver or build_id}"
    elif harmony_ver or brand in ["huawei", "honor"]:
        rom_family = "Huawei HarmonyOS / MagicOS"
        rom_detail = f"HarmonyOS/MagicOS {harmony_ver or build_id}"

    # Kernel & Subsystem Checks
    freezer_res = run_adb(["shell", "device_config", "get", "activity_manager_native_boot", "use_freezer"], serial)
    freezer_state = freezer_res.stdout.strip() or "unset"
    
    millet_res = run_adb(["shell", "settings", "get", "system", "MILLET_NO_RESTRICT_APP"], serial)
    millet_val = millet_res.stdout.strip()
    millet_supported = bool(millet_val and millet_val != "null")

    return {
        "status": "success",
        "serial": serial,
        "brand": brand,
        "manufacturer": manufacturer,
        "model": model,
        "name": name,
        "android_version": android_version,
        "sdk_version": int(sdk_version) if sdk_version.isdigit() else sdk_version,
        "rom_family": rom_family,
        "rom_detail": rom_detail,
        "cached_apps_freezer": freezer_state,
        "millet_installed": millet_supported,
        "millet_sample": millet_val if millet_supported else "N/A"
    }

def print_profile(profile: Dict[str, Any]):
    if profile.get("status") != "success":
        print(f"\n{Colors.RED}[!] Detection Failed:{Colors.RESET} {profile.get('error')}")
        return

    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: DEVICE FINGERPRINT DIAGNOSIS{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f" {Colors.BOLD}Device Serial     :{Colors.RESET} {profile['serial']}")
    print(f" {Colors.BOLD}Manufacturer/Brand:{Colors.RESET} {profile['manufacturer'].upper()} / {profile['brand'].upper()}")
    print(f" {Colors.BOLD}Model Name        :{Colors.RESET} {profile['model']} ({profile['name']})")
    print(f" {Colors.BOLD}Android Version   :{Colors.RESET} Android {profile['android_version']} (API {profile['sdk_version']})")
    print(f" {Colors.BOLD}System ROM Family :{Colors.RESET} {Colors.YELLOW}{profile['rom_family']}{Colors.RESET}")
    print(f" {Colors.BOLD}OS Incremental    :{Colors.RESET} {profile['rom_detail']}")
    print(f" {Colors.BOLD}Cgroup v2 Freezer :{Colors.RESET} {profile['cached_apps_freezer']} (Kernel Socket Freeze Status)")
    if "Xiaomi" in profile['rom_family']:
        print(f" {Colors.BOLD}Xiaomi MILLET     :{Colors.RESET} {'Detected' if profile['millet_installed'] else 'Standard System'}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Noti-Fixer Device Detection Specialist by Shovo")
    parser.add_argument("-s", "--serial", help="Target specific ADB device serial", default=None)
    parser.add_argument("--json", action="store_true", help="Output raw JSON data")
    args = parser.parse_args()

    profile = detect_device_profile(args.serial)
    if args.json:
        print(json.dumps(profile, indent=2))
    else:
        print_profile(profile)

if __name__ == "__main__":
    main()
