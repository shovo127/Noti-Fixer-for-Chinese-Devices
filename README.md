<div align="center">

# ⚡ Noti-Fixer for Chinese Devices
### The Production-Grade Push Notification, FCM Socket & Process Keeper Suite for Chinese Android ROMs

[![CI Validation](https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices/actions/workflows/ci.yml/badge.svg)](https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Android Compatibility](https://img.shields.io/badge/Android-12%20%7C%2013%20%7C%2014%20%7C%2015%20%7C%2016-green.svg?logo=android&logoColor=white)](https://developer.android.com)
[![Platform Support](https://img.shields.io/badge/Supported-HyperOS%20%7C%20OriginOS%20%7C%20ColorOS%20%7C%20HarmonyOS-orange.svg)](#-supported-brands--systems)
[![Root Required](https://img.shields.io/badge/Root-NOT%20Required-brightgreen.svg)](#-safety--trust-guarantees)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Architect](https://img.shields.io/badge/Architect-Mohammed%20Thuhidul%20Islam%20Shovo-blueviolet.svg)](https://github.com/shovo127)

<p align="center">
  <b>Tired of missed WhatsApp/Telegram calls, delayed Gmail notifications, and frozen background apps on Xiaomi, Vivo, Oppo, or Huawei?</b><br>
  Noti-Fixer solves the root cause scientifically — repairing Android Doze, vendor freeze engines (MILLET, Athena, Jovi), and Linux cgroup socket kills automatically.
</p>

[Quick Start](#-super-simple-wireless-wi-fi-pairing-no-cable-needed) • [Wireless Guide](docs/WIRELESS_DEBUGGING_GUIDE.md) • [Architecture Guide](docs/ARCHITECTURE.md) • [Supported Devices](docs/SUPPORTED_DEVICES.md) • [Debloat Guide](docs/DEBLOAT_INTEGRATION.md) • [Safety & Trust](#-safety--trust-guarantees) • [FAQ](#-frequently-asked-questions)

</div>

---

## 🖥️ Terminal Interface Preview

```text
==============================================================================
        NOTI-FIXER FOR CHINESE DEVICES - PRODUCTION REPAIR SUITE
             Architect: Mohammed Thuhidul Islam Shovo (shovo127)
                         Open-Source MIT License
==============================================================================

  Targeting: Xiaomi HyperOS / MIUI | Vivo OriginOS | Oppo ColorOS | HarmonyOS

  [1] Full Automated 1-Click Notification Fix (Recommended)
  [2] Live Diagnostic Audit (FCM Socket, Android Doze, Kernel Freezer)
  [3] Device Fingerprint & Hardware/ROM Profile
  [4] Push & Start HyperOS MILLET Watchdog Daemon
  [5] Wireless ADB Port Scanner (Find new port after reboot)
  [6] Setup Circle to Search Companion (MiCTS Integration)
  [7] Revert Changes (Master 100% Safe Rollback)
  [8] Exit

==============================================================================
Enter choice [1-8]: 1
```

---

## 🛡️ Safety & Trust Guarantees

Your smartphone holds your personal data, bank apps, and memories. Noti-Fixer is engineered with strict non-destructive enterprise safety standards:

- **100% Root-Free:** Does NOT require Magisk, KernelSU, or SuperSU.
- **No Bootloader Unlock Needed:** Keeps Widevine L1, Google Pay / Wallet, and Knox intact.
- **100% Reversible:** Every operation creates a timestamped snapshot in `backups/`. Revert instantly with one click.
- **Zero Dependencies:** Runs on pure Python standard library. No pip installs, no bloat.
- **Zero Telemetry / 100% Local:** All scripts run entirely on your local machine and your phone. No internet tracking.
- **Non-Destructive:** Does not uninstall apps or delete system services blindly.

---

## 🔬 The Science Behind the Fix

Chinese ROMs implement aggressive power management layers that silently kill Google Firebase Cloud Messaging (FCM) TCP sockets:

```text
[Screen Off / Standby]
         │
         ▼
[Vendor Power Daemon] (Xiaomi PowerKeeper / Oppo Athena / Vivo Jovi)
         │  ❌ Silently drops TCP socket: mtalk.google.com:5228
         ▼
[Kernel Cgroup v2 Freezer] (cached_apps_freezer)
         │  ❌ Halts background threads & drops socket polling
         ▼
[Android Doze & Netpolicy]
         │  ❌ Cuts background metered data sync
         ▼
[RESULT: Notifications Delayed 30-60 min OR Never Arrive Until Phone Woken Up!]
```

### The Noti-Fixer Scientific Remediation Pipeline

```text
  ┌────────────────────────────────────────────────────────┐
  │              NOTI-FIXER REMEDIATION SUITE              │
  ├────────────────────────────────────────────────────────┤
  │ 1. Kernel Cgroup Freezer: DISABLED via device_config   │
  │ 2. FCM Push Sockets: Actively guarded via mtalk:5228   │
  │ 3. Vendor Injections: MILLET_NO_RESTRICT_APP populated │
  │ 4. System AppOps: 10008 (Autostart) & 10021 Granted    │
  │ 5. Network Policy: Exempted from restrict-background   │
  │ 6. Watchdog Daemon: Self-healing against system resets │
  └────────────────────────────────────────────────────────┘
                             │
                             ▼
  [RESULT: Instant <100ms Push Notifications 24/7, Exactly Like Stock Android!]
```

*(For in-depth kernel analysis, read our full [Architecture Guide](docs/ARCHITECTURE.md))*

---

## 📊 Before & After Benchmark

| Metric | Stock Chinese ROM | After Noti-Fixer |
| :--- | :--- | :--- |
| **WhatsApp / Telegram Calls** | Often silent until unlocked | **Rings instantly on lock screen** |
| **FCM Socket (mtalk.google.com:5228)** | Drops after 3–5 min | **100% Persistent & Keepalive** |
| **Gmail / Outlook Sync** | 30 to 60 minute delay | **Real-time instant push (<1 sec)** |
| **System Cgroup Freezer** | Freezes background messaging | **Intelligently exempted** |
| **Reboot Persistence** | Settings wiped on reboot | **Auto-restored / Watchdog guarded** |
| **Banking / DRM Security** | Intact | **100% Intact (Passes Play Integrity)** |

---

## 🚀 Supported Brands & Systems

| Brand | System Versions | Key Technologies Handled |
| :--- | :--- | :--- |
| **Xiaomi / POCO / Redmi** | HyperOS 1.0, 2.0 / MIUI 12, 13, 14 | MILLET framework, PowerKeeper, Op 10008/10021 |
| **Vivo / iQOO** | OriginOS 3, 4, 5 / FuntouchOS 13, 14, 15 | PEM, Jovi Engine, High background consumption |
| **Oppo / OnePlus / Realme** | ColorOS 12–15 / OxygenOS 12–15 / RealmeUI | Athena daemon, GuardElf, Quick Freeze |
| **Huawei / Honor** | HarmonyOS 2, 3, 4, NEXT / MagicOS 7, 8 | PowerGenie, Deep Sleep Whitelist |
| **Google / Samsung / Moto** | Stock Android 12, 13, 14, 15, 16 | Doze whitelist, cached_apps_freezer bypass |

*(See full model compatibility in [Supported Devices](docs/SUPPORTED_DEVICES.md))*

---

## ⚡ Super Simple Wireless Wi-Fi Pairing (No Cable Needed)

Connect your phone and computer to the **same Wi-Fi network**, then follow this 30-second flow:

```text
  ┌─────────────────────────┐     ┌────────────────────────┐     ┌───────────────────────┐
  │  1. Phone Settings      │     │  2. Run 1 Command      │     │  3. Enter 3 Things    │
  │     Enable Wireless     │ ──► │     python scripts/    │ ──► │     • IP & Port       │
  │     Debugging           │     │     connect_phone.py   │     │     • 6-Digit Code    │
  │     Tap "Pair with code"│     │                        │     │     • Done! Auto-Fix! │
  └─────────────────────────┘     └────────────────────────┘     └───────────────────────┘
```

### Step 1: Open Wireless Debugging on Phone
1. Go to **Settings** ➜ **About Phone** ➜ Tap **Build Number** 7 times to enable Developer Options.
2. Go to **Settings** ➜ **Developer Options** ➜ Turn **ON** **Wireless Debugging**:
   - *(Xiaomi/POCO/Redmi users: also turn ON "USB Debugging (Security settings)")*.
3. Tap the words **"Wireless Debugging"**, then tap **"Pair device with pairing code"**.
4. You will see a popup with:
   - **IP address & Port** (e.g. `192.168.1.50:39481`)
   - **6-Digit Pairing Code** (e.g. `849201`)

### Step 2: Run the Connection Wizard
Run this command on your computer (or choose `[1]` in `NotiFixer_OneClick.bat` / `.sh`):

```bash
python scripts/connect_phone.py
```

### Step 3: Enter the IP, Port & Code
Type the 3 values shown on your phone screen when prompted:
```text
👉 Enter IP & Pairing Port: 192.168.1.50:39481
👉 Enter the 6-Digit Pairing Code: 849201
👉 Enter connect port (or press ENTER): [Press ENTER]
```

**That's it!** Noti-Fixer automatically connects to your phone, prints your device model, and applies the full notification fix in seconds!

*(For full illustrated details, see [Wireless Debugging Guide](docs/WIRELESS_DEBUGGING_GUIDE.md))*

---

## 🔌 Or Connect via Standard USB Cable

If you prefer using a USB cable:
1. Connect phone with USB cable, select **File Transfer**, and accept the USB Debugging prompt on your screen.
2. Run:
   - **Windows:** Double-click `scripts/NotiFixer_OneClick.bat` and select `[2]`.
   - **macOS / Linux:** Run `./scripts/NotiFixer_OneClick.sh` and select `[2]`.
   - **Python CLI:** `python scripts/apply_notification_fix.py --dns-adguard`

---

## 🔄 Dynamic Wireless ADB Port Scanner

When using Wireless Debugging without a cable, Android dynamically assigns a new random port every time the phone restarts (e.g., `34891`, `42195`).

Simply run:
```bash
python scripts/scan_ports.py -ip <PHONE_IP_ADDRESS>
```
It will automatically scan and reconnect ADB without needing to plug in a cable!

---

## 🔍 Circle to Search Companion (MiCTS)

Missing Google's native Circle to Search on your Xiaomi, Vivo, or Oppo?  
Noti-Fixer bundles the audited **CircleToSearch** trigger companion:

1. Run `CircleToSearch/setup_cts.bat` (or use option 6 in the interactive menu).
2. Configure the Quick Settings tile or gesture shortcut.
3. Circle anything on your screen to search with Google Lens instantly.

---

## 🤖 Antigravity & AI Agent Skill Integration

Noti-Fixer includes a complete native AI skill for **Antigravity**, **Cursor**, and **Claude Code**:

- Skill location: `.gemini/skills/noti-fixer/SKILL.md`
- Just ask your AI:
  > *"My Xiaomi 14 on HyperOS isn't receiving WhatsApp messages on time. Can you fix it using Noti-Fixer?"*

Your AI agent will automatically pair, detect your device, run the audit, apply the fixes, and verify the live FCM socket connection autonomously.

---

## 🔄 Emergency Rollback (100% Reversible)

Need to revert all changes before selling your phone or claiming warranty?
Simply run:
```bat
call templates/master_restore_template.bat
```
*(Or choose Option `[7]` in the 1-Click Interactive Menu)*. All system properties, DNS, and AppOps settings will instantly revert to factory stock.

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>Does this drain more battery?</b></summary>
No. Noti-Fixer does not prevent your phone from sleeping; it only prevents the <i>freezing of the Google FCM notification socket</i> (which uses minimal micro-amperes of power) and ensures your messaging apps are woken when a push arrives.
</details>

<details>
<summary><b>Will this void my warranty or trip Knox / SafetyNet?</b></summary>
No. Because this operates strictly through Android's sanctioned ADB subsystem and requires zero root or bootloader unlocking, SafetyNet and Play Integrity pass 100%.
</details>

<details>
<summary><b>What happens when my phone reboots?</b></summary>
Core system configs (like `device_config` and `settings put system MILLET_NO_RESTRICT_APP`) persist across reboots. On HyperOS, we also provide <code>scripts/millet_watchdog.sh</code> to guard against vendor resets during app updates.
</details>

---

## 📜 License & Copyright

Designed and developed by **Mohammed Thuhidul Islam Shovo (shovo127)**.  
Licensed under the open-source [MIT License](LICENSE). Copyright (c) 2026.
