#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Interactive Wireless Debugging Pairing & 1-Click Fix Wizard
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import sys
import subprocess
import time
import re
try:
    from safety_guard import assert_command_safe
except ImportError:
    from scripts.safety_guard import assert_command_safe

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    print(f"\n{Colors.CYAN}{'='*72}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}   NOTI-FIXER: SIMPLE WIRELESS PAIRING & NOTIFICATION FIX WIZARD{Colors.RESET}")
    print(f"       Architect: Mohammed Thuhidul Islam Shovo (shovo127) | MIT License")
    print(f"{Colors.CYAN}{'='*72}{Colors.RESET}\n")

def check_adb():
    try:
        res = subprocess.run(["adb", "version"], capture_output=True, text=True, check=False)
        if res.returncode != 0:
            print(f"{Colors.RED}[!] 'adb' found but returned an error.{Colors.RESET}")
            sys.exit(1)
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: 'adb' is not installed or not in your system PATH.{Colors.RESET}")
        print("    Please install Android Platform-Tools and add 'adb' to PATH.")
        sys.exit(1)

def show_phone_instructions():
    print(f"{Colors.YELLOW}{Colors.BOLD}📱 STEP 1: PREPARE YOUR PHONE (Only Takes 15 Seconds):{Colors.RESET}")
    print(" 1. Connect phone and computer to the SAME Wi-Fi network.")
    print(" 2. Open phone Settings -> About Phone -> Tap 'Build Number' 7 times to enable Developer Options.")
    print(" 3. Go to Settings -> Developer Options -> Turn ON 'Wireless Debugging'.")
    print("    (On Xiaomi/Poco: Also turn ON 'USB Debugging (Security settings)').")
    print(" 4. In Developer Options, tap the words 'Wireless Debugging' to open its screen.")
    print(" 5. Tap 'Pair device with pairing code'.")
    print(" -------------------------------------------------------------")
    print(" You will see a popup showing:")
    print("   • Wi-Fi pairing code: 6-digit number (e.g. 748291)")
    print("   • IP address & Port:  (e.g. 192.168.1.50:39481)")
    print(f"{'='*72}\n")

def interactive_wireless_pair():
    check_adb()
    print_banner()
    show_phone_instructions()

    # Input: IP and Port
    pair_input = input(f"{Colors.BOLD}👉 Enter IP & Pairing Port shown on popup (e.g. 192.168.1.50:39481): {Colors.RESET}").strip()
    if not pair_input:
        print(f"{Colors.RED}[!] No IP:Port entered. Aborting.{Colors.RESET}")
        return

    # Normalize input
    if ":" not in pair_input:
        ip = pair_input
        port = input(f"{Colors.BOLD}👉 Enter the Pairing Port (number after colon): {Colors.RESET}").strip()
        pair_target = f"{ip}:{port}"
    else:
        pair_target = pair_input
        ip = pair_target.split(":")[0]

    code = input(f"{Colors.BOLD}👉 Enter the 6-Digit Pairing Code (e.g. 748291): {Colors.RESET}").strip()
    if not code:
        print(f"{Colors.RED}[!] Pairing code cannot be empty. Aborting.{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}[*] Pairing with {pair_target} using code {code}...{Colors.RESET}")
    res = subprocess.run(["adb", "pair", pair_target, code], capture_output=True, text=True)
    print(res.stdout.strip())

    if "successfully paired" not in res.stdout.lower() and "paired" not in res.stdout.lower():
        print(f"\n{Colors.RED}[!] Pairing failed or timed out. Double check IP, port, and 6-digit code.{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Phone paired successfully!{Colors.RESET}")

    # Connect Step
    print(f"\n{Colors.YELLOW}{Colors.BOLD}📱 STEP 2: CONNECTING TO PHONE:{Colors.RESET}")
    print(" On your phone, close the pairing popup.")
    print(" Look at the main 'Wireless Debugging' screen under 'IP address & Port'.")
    print(f" (Note: Connection port is often different from pairing port, e.g. {ip}:41295)")
    
    connect_port_input = input(f"{Colors.BOLD}👉 Enter connect port (or press ENTER if it's the same port): {Colors.RESET}").strip()
    if connect_port_input:
        if ":" in connect_port_input:
            connect_target = connect_port_input
        else:
            connect_target = f"{ip}:{connect_port_input}"
    else:
        connect_target = pair_target

    print(f"\n{Colors.CYAN}[*] Connecting to {connect_target}...{Colors.RESET}")
    c_res = subprocess.run(["adb", "connect", connect_target], capture_output=True, text=True)
    print(c_res.stdout.strip())

    if "connected" not in c_res.stdout.lower() or "cannot" in c_res.stdout.lower():
        print(f"{Colors.YELLOW}[!] Connect pending. Trying auto-discovery on active ports...{Colors.RESET}")
        scan_res = subprocess.run([sys.executable, "scripts/scan_ports.py", "-ip", ip], capture_output=True, text=True)
        print(scan_res.stdout.strip())

    # Verify device state
    dev_res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if "device" not in dev_res.stdout:
        print(f"{Colors.RED}[!] No authorized device found. Please make sure phone is awake and connected.{Colors.RESET}")
        return

    # Step 3: Detect Model & Apply Fix
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*72}")
    print(f"   PHONE CONNECTED SUCCESSFULLY!")
    print(f"{'='*72}{Colors.RESET}")

    # Read Model & Brand
    brand = subprocess.run(["adb", "shell", "getprop", "ro.product.brand"], capture_output=True, text=True).stdout.strip().upper()
    model = subprocess.run(["adb", "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
    android_ver = subprocess.run(["adb", "shell", "getprop", "ro.build.version.release"], capture_output=True, text=True).stdout.strip()

    print(f" {Colors.BOLD}Model       :{Colors.RESET} {brand} {model}")
    print(f" {Colors.BOLD}Android OS  :{Colors.RESET} Android {android_ver}")
    print(f"{'='*72}\n")

    confirm = input(f"{Colors.BOLD}👉 Do you want to apply the Notification Fix now? [Y/n]: {Colors.RESET}").strip().lower()
    if confirm in ["", "y", "yes"]:
        print(f"\n{Colors.CYAN}[*] Launching Automated Notification Fixer...{Colors.RESET}")
        subprocess.run([sys.executable, "scripts/apply_notification_fix.py", "--dns-adguard"])
        
        print(f"\n{Colors.CYAN}[*] Running live verification audit...{Colors.RESET}")
        subprocess.run([sys.executable, "scripts/audit_fcm_doze.py"])

        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL DONE! Your phone is now fully optimized.{Colors.RESET}")
        print("Your notifications and calls will now arrive instantly without delay 24/7.")
    else:
        print("\nFix skipped. You can run 'python scripts/apply_notification_fix.py' whenever you are ready.")

if __name__ == "__main__":
    interactive_wireless_pair()

