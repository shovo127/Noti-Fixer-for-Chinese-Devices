#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noti-Fixer for Chinese Devices
Module: Wireless ADB Port Scanner & Auto-Reconnect Engine
Author: Mohammed Thuhidul Islam Shovo (shovo127)
License: MIT License (Copyright (c) 2026)
"""

import socket
import subprocess
import concurrent.futures
import argparse
import sys
import re
from typing import Optional, List

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def get_local_ip_candidates() -> List[str]:
    candidates = []
    try:
        # Run arp -a to get active IPs on subnet
        res = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=False)
        for line in res.stdout.splitlines():
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if ip_match:
                ip = ip_match.group(1)
                if not ip.startswith("255.") and not ip.startswith("224.") and not ip.endswith(".255"):
                    candidates.append(ip)
    except Exception:
        pass
    return list(set(candidates))

def test_port(ip: str, port: int, timeout: float = 0.3) -> Optional[int]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            res = s.connect_ex((ip, port))
            if res == 0:
                return port
        except Exception:
            pass
    return None

def scan_device_ports(ip: str, start_port: int = 30000, end_port: int = 49000, max_threads: int = 150) -> List[int]:
    print(f"{Colors.CYAN}[*] Scanning target {ip} for active Wireless ADB ports ({start_port}-{end_port})...{Colors.RESET}")
    open_ports = []
    
    # Check 5555 first (standard fixed port)
    if test_port(ip, 5555, timeout=0.5):
        open_ports.append(5555)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_port = {executor.submit(test_port, ip, p): p for p in range(start_port, end_port + 1)}
        for future in concurrent.futures.as_completed(future_to_port):
            p = future.result()
            if p:
                open_ports.append(p)
                print(f"{Colors.GREEN}[+] Found open candidate port: {p}{Colors.RESET}")
    return open_ports

def try_adb_connect(ip: str, port: int) -> bool:
    target = f"{ip}:{port}"
    print(f"[*] Attempting ADB connection to {target}...")
    res = subprocess.run(["adb", "connect", target], capture_output=True, text=True)
    if "connected" in res.stdout.lower() and "cannot" not in res.stdout.lower():
        print(f"{Colors.GREEN}{Colors.BOLD}✔ Successfully connected to {target}!{Colors.RESET}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Wireless ADB Port Discovery by Shovo")
    parser.add_argument("-ip", "--ip-address", help="Device IP address to scan (e.g. 192.168.1.50)")
    parser.add_argument("--start", type=int, default=30000, help="Start port range (default: 30000)")
    parser.add_argument("--end", type=int, default=49999, help="End port range (default: 49999)")
    args = parser.parse_args()

    ip = args.ip_address
    if not ip:
        print(f"{Colors.YELLOW}[?] No IP specified. Finding active subnet devices...{Colors.RESET}")
        candidates = get_local_ip_candidates()
        if not candidates:
            print(f"{Colors.RED}[!] Could not auto-detect IP. Please specify with: python scan_ports.py -ip <Phone_IP>{Colors.RESET}")
            sys.exit(1)
        print(f"Discovered local IP candidates: {', '.join(candidates)}")
        ip = candidates[0]
        print(f"Selecting candidate: {ip}")

    open_ports = scan_device_ports(ip, args.start, args.end)
    if not open_ports:
        print(f"{Colors.RED}[!] No open Wireless Debugging ports found on {ip}. Ensure Wireless Debugging is toggled ON on your phone.{Colors.RESET}")
        sys.exit(1)

    for p in open_ports:
        if try_adb_connect(ip, p):
            sys.exit(0)

    print(f"{Colors.YELLOW}[!] Ports open but ADB connection refused. Re-pair device or accept authorization prompt.{Colors.RESET}")

if __name__ == "__main__":
    main()
