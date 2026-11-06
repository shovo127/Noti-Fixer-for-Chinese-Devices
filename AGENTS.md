# AI Agent Instructions for Noti-Fixer

> **Target Audience:** Antigravity IDE, Cursor, Claude Code, GitHub Copilot Workspace, Cline, Roo Code, or any LLM-powered coding assistant operating in this repository workspace.

Welcome, AI Agent! You are acting as the autonomous pairing engineer for **Noti-Fixer for Chinese Devices**.

Before performing any action or executing any command, you **MUST** read and adhere to the master blueprints:
1. [`.gemini/skills/noti-fixer/SKILL.md`](.gemini/skills/noti-fixer/SKILL.md) — Complete 8-phase operational workflow and command mappings.
2. [`docs/SAFETY_AND_AI_BOUNDARIES.md`](docs/SAFETY_AND_AI_BOUNDARIES.md) — Hard safety barriers and command prohibitions.
3. [`docs/DEBLOAT_INTEGRATION.md`](docs/DEBLOAT_INTEGRATION.md) — User-profile debloat rules and protected system package boundaries.

---

## 🚫 Hard Safety Directives (Zero Exceptions)

1. **NO FACTORY RESET OR WIPE:** You are strictly forbidden from running `factory_reset`, `master_clear`, `wipe`, `format`, `erase`, `locksettings clear`, or `reboot recovery`. This is a non-destructive user-space configuration tool; personal data, photos, chats, banking apps, and OS settings must remain 100% untouched.
2. **NO ROOT / NO BOOTLOADER UNLOCK:** Never suggest or execute `su`, `magisk`, `kernelsu`, `fastboot`, or bootloader unlocking.
3. **NO PACKAGE DISABLING / NO BLIND UNINSTALLS:** Never run `pm disable`, `disable-user`, or `pm clear`. The only permitted uninstall command is `pm uninstall -k --user 0 <pkg>` for packages explicitly approved by the user in List A, and NEVER for critical packages in List C.
4. **ALWAYS ROUTE ADB COMMANDS THROUGH SAFETY GUARD:** All commands must pass `scripts/safety_guard.py`.
5. **MANDATORY USER CONFIRMATION GATES:** Never apply changes or debloat apps without explicitly showing the diagnosis and 3 editable lists (A, B, C) and receiving user approval.

---

## 🧭 Deterministic 8-Phase Execution Protocol

Follow these phases sequentially:

### Phase 0: Collect
Request or parse the target device parameters from the user:
- `PHONE_IP` (e.g. `192.168.0.105`)
- `PAIRING_PORT` (e.g. `41259` from the "Pair device with pairing code" popup)
- `PAIRING_CODE` (e.g. `123456`)
- `CONNECT_PORT` (e.g. `38473` from the main Wireless Debugging screen)
*If any are missing, ask once in a single concise message.*

### Phase 1: Connect
Run pairing and connection via `scripts/connect_phone.py` or standard ADB:
```bash
adb pair <PHONE_IP>:<PAIRING_PORT> <PAIRING_CODE>
adb connect <PHONE_IP>:<CONNECT_PORT>
```
*Instruct the user to keep the phone screen ON and stay inside the pairing popup dialog until paired.*

### Phase 2: Safe Scan (READ-ONLY)
Gather device architecture and current state without modifying anything:
```bash
python scripts/detect_device.py
python scripts/audit_fcm_doze.py
python scripts/inspect_battery.py
```

### Phase 3: Diagnose + Confirm
Summarize findings to the user (Brand, ROM, Android API, Kernel freezer state, FCM socket status, active drainers).  
**Ask:** *"Do you confirm this diagnosis and wish to proceed with the remediation plan? (yes/edit)"*  
*Apply nothing until the user confirms.*

### Phase 4: Propose 3 Editable Lists
Present 3 clear Markdown tables:
- **List A (Debloat Candidates):** Vendor bloatware/telemetry safe to remove for user 0 (`pm uninstall -k --user 0`).
- **List B (Background-Restrict Candidates):** High-drain apps (e.g., e-commerce, secondary social) to place in On-Demand Standby (Bucket 40 / RARE) with autostart suppressed. They work normally when opened.
- **List C (Protected / Never Touched):** Critical system framework, Google Play Services, Google Play Store, Download Manager, Zoom, dialers, SMS, keyboards, and banking/messaging apps.
Save the proposal to `backups/<timestamp>/plan.json`. Ask the user to approve or modify.

### Phase 5: Backup
Snapshot current system settings and generate a timestamped rollback script before executing modifications.

### Phase 6: Apply
1. Debloat approved List A packages via `pm uninstall -k --user 0 <pkg>`.
2. Restrict approved List B packages via Standby Bucket 40 and AppOps 10008/10021 ignore.
3. Apply brand-specific notification fixes:
```bash
python scripts/apply_notification_fix.py
```
4. Push and start watchdog daemon:
```bash
adb push scripts/millet_watchdog.sh /data/local/tmp/millet_watchdog.sh
adb shell chmod +x /data/local/tmp/millet_watchdog.sh
adb shell "nohup /data/local/tmp/millet_watchdog.sh >/dev/null 2>&1 &"
```

### Phase 7: Verify & Document
1. Audit FCM push socket:
```bash
python scripts/audit_fcm_doze.py
```
2. Deliver a clean before-and-after summary table.
3. Provide the exact rollback command:
```bash
python scripts/restore_backup.py
```
*(or run Option `[9]` in `scripts/NotiFixer_OneClick.bat` / `.sh`)*.

