---
name: noti-fixer
description: Autonomous notification fixer and process optimization specialist for Chinese ROM devices (Xiaomi HyperOS, Vivo OriginOS, Oppo ColorOS, Huawei HarmonyOS). Resolves delayed notifications, aggressive background kills, and FCM socket freezes via ADB pairing.
---

# Noti-Fixer: Master AI Agent Skill for Chinese Android Devices

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**License:** MIT License (Copyright (c) 2026)

This skill equips Antigravity, Cursor, Claude, and AI pairing agents with full autonomous intelligence to diagnose, repair, and permanently maintain push notifications on any Chinese ROM device without root, without unlocking the bootloader, and with 100% reversibility.

---

## 1. Operating Rules & Strict Safety Boundaries

1. **Zero Root / Zero Bootloader Unlock:** Never ask the user to unlock the bootloader or flash custom ROMs. All repairs operate safely within Android's official ADB and AppOps subsystems.
2. **Never Debloat Blindly:** Never uninstall or disable critical system services without user confirmation.
3. **Always Backup First:** Every execution of `scripts/apply_notification_fix.py` automatically generates a timestamped recovery image in `backups/`.
4. **Mandatory Post-Verification:** Never declare success until `scripts/audit_fcm_doze.py` confirms that the FCM socket (`mtalk.google.com:5228`) is connected and healthy.

---

## 2. Interaction Protocol & Step-by-Step Workflow

```
[Phase 1: Pairing & Connection]
         │ ── USB Cable OR Wireless Debugging
         ▼
[Phase 2: Fingerprinting & Detection]
         │ ── Run detect_device.py
         ▼
[Phase 3: Live FCM & Doze Audit]
         │ ── Run audit_fcm_doze.py
         ▼
[Phase 4: Brand-Specific Remediation]
         │ ── Run apply_notification_fix.py
         ▼
[Phase 5: Verification & Watchdog Activation]
         │ ── Verify mtalk.google.com:5228 & deploy millet_watchdog.sh
```

---

### Step 1: Device Pairing & Setup Guidance

When a user mentions delayed notifications, missed WhatsApp/Telegram calls, or background app closures on a Chinese device, guide them:

#### A. Enable Developer Options & Debugging
1. Open phone **Settings** -> **About Phone**.
2. Tap **Build Number** (or **OS Version**) 7 times until you see *"You are now a developer!"*.
3. Go to **Settings** -> **System / Additional Settings** -> **Developer Options**.
4. Enable **USB Debugging** (and on Xiaomi devices, also enable **USB Debugging (Security settings)**).

#### B. Connection Mode (USB or Wireless ADB)
- **USB Cable:** Plug in cable, select *File Transfer*, and tap **Allow Always** on the USB debugging authorization popup.
- **Wireless Debugging (Wi-Fi):**
  1. Under Developer Options, enable **Wireless Debugging**.
  2. Tap **Pair device with pairing code**. Note the IP, pairing port, and 6-digit code.
  3. Run: `adb pair <IP>:<Pairing_Port> <Code>`
  4. Run: `adb connect <IP>:<Connect_Port>`

#### C. Post-Reboot Wireless Port Discovery
If the phone reboots and the Wireless Debugging port changes dynamically:
```bash
python scripts/scan_ports.py -ip <Device_IP>
```
The script will multi-thread scan ports `30000-49999` and automatically reconnect.

---

### Step 2: Device Fingerprinting

Identify the brand, Android OS version, and kernel freezer status:
```bash
python scripts/detect_device.py
```
Check:
- `rom_family`: Identifies if target is HyperOS, OriginOS, ColorOS, or HarmonyOS.
- `cached_apps_freezer`: Identifies if Android 14/15/16 kernel socket freezing is active.

---

### Step 3: Live FCM & Process Audit

Execute a non-invasive live audit:
```bash
python scripts/audit_fcm_doze.py
```
Evaluate:
- **FCM Socket Connection:** Must show `CONNECTED` to Google port `5228`.
- **Doze Whitelist:** Ensures WhatsApp, Telegram, Messenger, and GMS are exempted.
- **Vendor AppOps:** Checks if autostart (`10008`) is granted.

---

### Step 4: Automated Scientific Remediation

Run the universal fixer:
```bash
python scripts/apply_notification_fix.py --dns-adguard
```

#### What this accomplishes across brands:
1. **Universal Android Core:**
   - Disables kernel Cgroup `cached_apps_freezer` (`use_freezer false`).
   - Adds GMS and messaging apps to Android Doze whitelist (`dumpsys deviceidle whitelist +<pkg>`).
   - Exempts apps from metered background netpolicy (`cmd netpolicy add restrict-background-whitelist <UID>`).
2. **Xiaomi HyperOS / MIUI:**
   - Grants AppOp `10008` (`OP_AUTO_START`).
   - Grants AppOp `10021` (`OP_SHOW_WHEN_LOCKED` / secondary launch).
   - Injects apps into `Settings.System.MILLET_NO_RESTRICT_APP`.
   - Deploys `scripts/millet_watchdog.sh` into `/data/local/tmp` to prevent PowerKeeper from wiping the whitelist on app updates.
3. **Vivo OriginOS / FuntouchOS:**
   - Whitelists high background battery consumption.
   - Sets AppOp `10008` (Autostart).
   - Grants `RUN_ANY_IN_BACKGROUND`.
4. **Oppo ColorOS / Realme UI:**
   - Bypasses Athena Quick Freeze.
   - Sets `AUTO_REVOKE_PERMISSIONS_IF_UNUSED` to `ignore`.
5. **Safe AdGuard Private DNS:**
   - Configures `dns.adguard.com` to sinkhole vendor telemetry while preserving Google push sockets.

---

### Step 5: Verification & Testing

Verify that the socket is open and live:
```bash
python scripts/audit_fcm_doze.py
```
Ask the user to turn off the screen, wait 2 minutes, and send a message or test call to verify instantaneous delivery.

---

### Step 6: 100% Reversible Rollback

If the user ever sells the phone or wants to revert:
```bash
call templates/master_restore_template.bat
```
This safely restores default factory settings without modifying user data.
