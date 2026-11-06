---
name: noti-fixer
description: Autonomous push notification healer, background battery optimizer, and safe user-profile debloater for Chinese Android ROMs (Xiaomi HyperOS, Vivo OriginOS, Oppo ColorOS, Huawei HarmonyOS, Meizu Flyme).
---

# Noti-Fixer: Master AI Agent Skill for Chinese Android Devices

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**License:** MIT License (Copyright (c) 2026)

This skill equips Antigravity, Cursor, Claude Code, GitHub Copilot, and LLM pairing agents with deterministic intelligence to diagnose, repair, and maintain push notifications and battery life across Chinese ROMs without root, without bootloader unlocking, and with 100% reversibility.

---

## 1. Operating Rules & Strict Safety Boundaries (Zero-Mistake Architecture)

> **CRITICAL AI SAFETY DIRECTIVE:** AI pairing agents MUST NEVER execute or recommend destructive commands. The programmatic security interceptor (`scripts/safety_guard.py`) will automatically terminate any prohibited operations.

1. **Zero Factory Reset or Data Wiping:** Never suggest or run `factory_reset`, `master_clear`, `wipe`, `format`, `erase`, `locksettings clear`, or `reboot recovery`. User data, accounts, photos, and chats must remain 100% untouched.
2. **Zero Root / Zero Bootloader Unlock:** Never suggest or execute `su`, `magisk`, `kernelsu`, bootloader unlocking, or custom ROM flashing. All optimizations operate strictly through Android's sanctioned ADB AppOps/Doze whitelist APIs.
3. **Reversible User-Profile Debloat Only:** Never run `pm disable`, `disable-user`, `pm clear`, or unvetted uninstalls. The only permitted removal command is `pm uninstall -k --user 0 <pkg>` applied strictly to packages explicitly confirmed in **List A**, and NEVER to packages in **List C** (Protected Frameworks).
4. **Always Route ADB Through Safety Guard:** All operations run through `scripts/safety_guard.py` which intercepts dangerous tokens before they can be sent to the device.
5. **Always Backup First:** Every execution automatically generates a timestamped recovery snapshot and rollback script in `backups/<timestamp>/`.
6. **Mandatory User Confirmation Gates:** Never apply changes or debloat apps without explicitly presenting the diagnosis and the 3 editable lists (A, B, C) and waiting for user confirmation.
7. **Mandatory Post-Verification:** Never declare success until `scripts/audit_fcm_doze.py` confirms that the FCM socket (`mtalk.google.com:5228`) is connected and healthy.
*(Full security reference: [docs/SAFETY_AND_AI_BOUNDARIES.md](docs/SAFETY_AND_AI_BOUNDARIES.md))*

---

## 2. Deterministic 8-Phase AI Workflow

```text
[Phase 0: Collect] ──────► [Phase 1: Connect] ──────► [Phase 2: Safe Scan]
                                                             │
[Phase 5: Backup]  ◄───── [Phase 4: Propose Lists] ◄── [Phase 3: Diagnose + Confirm]
       │
       ▼
[Phase 6: Apply]   ──────► [Phase 7: Verify]
```

### Phase 0: Collect
Prompt the user for connection parameters if not already provided:
- `PHONE_IP`: Device Wi-Fi IP address (e.g., `192.168.1.160`)
- `PAIRING_PORT`: Port shown on the "Pair device with pairing code" popup (e.g., `40261`)
- `PAIRING_CODE`: 6-digit Wi-Fi pairing code (e.g., `849201`)
- `CONNECT_PORT`: Port shown on the main Wireless Debugging screen (e.g., `39845`)
*If any value is missing, ask once in a single concise message.*

### Phase 1: Connect
Connect to the phone using the collected parameters:
```bash
adb pair <PHONE_IP>:<PAIRING_PORT> <PAIRING_CODE>
adb connect <PHONE_IP>:<CONNECT_PORT>
```
*Instruct the user in plain language:*
- Keep phone screen ON and stay on the "Pair device with pairing code" popup until pairing succeeds.
- Once paired, approve any "Always allow from this computer" prompt.

### Phase 2: Safe Scan (READ-ONLY)
Audit the device state without executing any modifications:
```bash
python scripts/detect_device.py
python scripts/audit_fcm_doze.py
python scripts/inspect_battery.py
```
Gather: Brand, Model, Android OS / API, ROM family, Kernel cgroup freezer status, Google FCM socket status (`mtalk.google.com:5228`), and top battery drainers.

### Phase 3: Diagnose & Ask for Confirmation
Present the findings clearly in a short table.
**Ask the user:**
> *"Do you confirm this diagnosis and wish to proceed with the remediation plan? (yes/edit)"*
*Wait for user confirmation before proceeding to Phase 4.*

### Phase 4: Propose 3 Editable Lists
Present three structured lists to the user:
- **List A (Debloat Candidates):** Pre-installed vendor bloatware/analytics safe to uninstall for user profile (`pm uninstall -k --user 0`). Include package name, app label, and safety tier.
- **List B (Background-Restrict Candidates):** High-drain user apps (ride-sharing, food delivery, shopping, secondary social media) to put in On-Demand Standby (Bucket `40 / RARE` with autostart `10008` & `10021` set to `ignore`). When opened by the user, they run at 100% full speed.
- **List C (Protected / Never Touched):** Core system frameworks, Google Play Services, Google Play Store (`com.android.vending`), Download Manager (`com.android.providers.downloads`), Zoom (`us.zoom.videomeetings`), SystemUI, Phone, Dialer, SMS, Keyboards, Launchers, and user-marked critical banking/messaging apps.
Save the plan to `backups/<timestamp>/plan.json`.
**Ask the user:**
> *"Would you like to add or remove any apps from List A or List B? Reply 'proceed' when ready."*
*Iterate until the user approves.*

### Phase 5: Backup
Snapshot current system settings, AppOps states, Standby Buckets, and uninstalled packages into `backups/<timestamp>/` and generate a single-click `restore.bat` / `restore.sh`.

### Phase 6: Apply
1. Debloat approved List A packages via:
   `adb shell pm uninstall -k --user 0 <package>`
2. Configure approved List B packages into On-Demand Standby:
   `adb shell cmd appops set <package> 10008 ignore`
   `adb shell cmd appops set <package> 10021 ignore`
   `adb shell am set-standby-bucket <package> rare`
3. Execute notification remediation:
   `python scripts/apply_notification_fix.py`
4. Deploy the watchdog daemon on HyperOS devices:
   `adb push scripts/millet_watchdog.sh /data/local/tmp/millet_watchdog.sh`
   `adb shell chmod +x /data/local/tmp/millet_watchdog.sh`
   `adb shell "nohup /data/local/tmp/millet_watchdog.sh >/dev/null 2>&1 &"`

### Phase 7: Verify & Report
1. Re-run live FCM socket audit:
   `python scripts/audit_fcm_doze.py`
2. Deliver a clean before-and-after verification table.
3. Show the user the exact 1-click rollback command:
   `python scripts/restore_backup.py` (or Option `[9]` in `scripts/NotiFixer_OneClick.bat`).
