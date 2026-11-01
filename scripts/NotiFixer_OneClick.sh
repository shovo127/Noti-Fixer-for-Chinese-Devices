#!/usr/bin/env bash
# ==============================================================================
# Noti-Fixer for Chinese Devices - Interactive Terminal Suite (macOS / Linux)
# Architect: Mohammed Thuhidul Islam Shovo (shovo127)
# Open-Source MIT License (Copyright (c) 2026)
# ==============================================================================

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_menu() {
    clear
    echo -e "${CYAN}==============================================================================${NC}"
    echo -e "${GREEN}${BOLD}        NOTI-FIXER FOR CHINESE DEVICES - PRODUCTION REPAIR SUITE${NC}"
    echo -e "             Architect: Mohammed Thuhidul Islam Shovo (shovo127)"
    echo -e "                         Open-Source MIT License"
    echo -e "${CYAN}==============================================================================${NC}"
    echo ""
    echo -e "  Targeting: Xiaomi HyperOS / MIUI | Vivo OriginOS | Oppo ColorOS | HarmonyOS"
    echo ""
    echo -e "  [1] Full Automated 1-Click Notification Fix (${GREEN}Recommended${NC})"
    echo -e "  [2] Live Diagnostic Audit (FCM Socket, Android Doze, Kernel Freezer)"
    echo -e "  [3] Device Fingerprint & Hardware/ROM Profile"
    echo -e "  [4] Push & Start HyperOS MILLET Watchdog Daemon"
    echo -e "  [5] Wireless ADB Port Scanner (Find new port after reboot)"
    echo -e "  [6] Circle to Search Companion Setup Info"
    echo -e "  [7] Revert Changes (Master 100% Safe Rollback)"
    echo -e "  [8] Exit"
    echo ""
    echo -e "${CYAN}==============================================================================${NC}"
    echo -n "Enter choice [1-8]: "
}

while true; do
    show_menu
    read -r choice
    case "$choice" in
        1)
            clear
            echo -e "${CYAN}[*] Checking ADB connection...${NC}"
            adb devices
            echo ""
            echo -e "${CYAN}[*] Applying Comprehensive Notification Fix...${NC}"
            python3 "$SCRIPT_DIR/apply_notification_fix.py" --dns-adguard
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        2)
            clear
            echo -e "${CYAN}[*] Running FCM Socket & Doze Audit...${NC}"
            python3 "$SCRIPT_DIR/audit_fcm_doze.py"
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        3)
            clear
            echo -e "${CYAN}[*] Detecting Device Profile & ROM Subsystem...${NC}"
            python3 "$SCRIPT_DIR/detect_device.py"
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        4)
            clear
            echo -e "${CYAN}[*] Pushing millet_watchdog.sh to device /data/local/tmp/...${NC}"
            adb push "$SCRIPT_DIR/millet_watchdog.sh" /data/local/tmp/millet_watchdog.sh
            adb shell chmod +x /data/local/tmp/millet_watchdog.sh
            echo -e "${CYAN}[*] Starting daemon in background...${NC}"
            adb shell "nohup /data/local/tmp/millet_watchdog.sh >/dev/null 2>&1 &"
            echo -e "${GREEN}[✔] Daemon active! Monitoring MILLET resets every 15 seconds.${NC}"
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        5)
            clear
            echo -n "Enter your phone's Wi-Fi IP address (or leave empty to auto-discover): "
            read -r target_ip
            if [ -z "$target_ip" ]; then
                python3 "$SCRIPT_DIR/scan_ports.py"
            else
                python3 "$SCRIPT_DIR/scan_ports.py" -ip "$target_ip"
            fi
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        6)
            clear
            echo -e "${CYAN}=== Circle to Search (Omnient) Setup ===${NC}"
            adb shell settings put secure assistant com.google.android.googlequicksearchbox/com.google.android.apps.search.assistant.surfaces.voice.OmnientActivity 2>/dev/null
            echo -e "${GREEN}[✔] Default assistant set to Google Omnient Search.${NC}"
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        7)
            clear
            echo -e "${YELLOW}Reverting all optimizations back to stock defaults...${NC}"
            adb shell device_config put activity_manager_native_boot use_freezer true
            adb shell setprop persist.sys.freezer true
            adb shell settings put global private_dns_mode opportunistic
            adb shell settings delete global private_dns_specifier
            adb shell settings put system MILLET_NO_RESTRICT_APP '""'
            echo -e "${GREEN}[✔] System settings restored to stock defaults!${NC}"
            echo ""
            echo -e "${YELLOW}Press [Enter] to return to menu...${NC}"
            read -r
            ;;
        8)
            echo "Exiting Noti-Fixer. Have a great day!"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            sleep 1
            ;;
    esac
done
