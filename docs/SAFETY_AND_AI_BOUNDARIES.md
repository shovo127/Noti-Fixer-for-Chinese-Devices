# 🛡️ Safety Architecture & AI Agent Hard Boundaries

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Security Standard:** Strict Non-Destructive Operation (ISO/IEC Zero-Harm Compliance)

---

## 🔒 The 4 Immutable Safety Guarantees

Noti-Fixer is engineered for everyday users, enterprises, and mission-critical devices. It contains programmatic hard barriers that make accidental damage mathematically and architecturally impossible.

### 1. 🚫 Zero Root / Zero Bootloader Modification
- **No `su` binaries:** Noti-Fixer never requires, searches for, or executes root permissions.
- **No Bootloader Unlock:** Your bootloader stays 100% locked.
- **No Security Downgrade:** Google Play Integrity API, SafetyNet, Samsung Knox (if applicable), and Widevine L1 Netflix HD/4K DRM remain 100% untampered and certified.

### 2. 🚫 Zero Factory Reset or Data Wipe
- **No data loss risk:** The commands `factory_reset`, `wipe`, `format`, `erase`, and `reboot recovery` are blocked by `scripts/safety_guard.py`.
- Your photos, chats, settings, contacts, and personal files are **never touched**.

### 3. 🛡️ User-Profile Debloat Only (Never System Deletion)
- Noti-Fixer **never** deletes apps from the read-only `/system` partition.
- When the user explicitly requests debloating of vendor ads or analytics bloatware from List A, removal is executed strictly via `pm uninstall -k --user 0 <pkg>`. This removes the package **only for the current user profile (User 0)** while keeping system binaries intact.
- Critical system services, communication apps, and banking packages (List C) are permanently protected and denied.
- Every uninstalled package is logged in `backups/<timestamp>/plan.json` and can be restored at any time via `cmd package install-existing --user 0 <pkg>`.
- Destructive commands like `pm clear`, `pm disable`, `disable-user`, or blanket uninstalls without user consent remain strictly blocked.

### 4. 🔄 100% Reversible with One Click
- Every single setting, AppOps rule, and debloated package has a matching recovery script in `backups/<timestamp>/restore.bat` (and `restore.sh`).
- Restoring packages restores user-profile installations via `cmd package install-existing --user 0 <pkg>`.
- Before applying any change, `apply_notification_fix.py` saves a timestamped JSON snapshot to `backups/`.

---

## 🤖 Strict Boundaries for AI Agents (Antigravity, Cursor, Claude)

When this project is used in AI-paired environments, AI agents MUST obey these hard constraints:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   AI AGENT SECURITY DIRECTIVES                         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. NEVER suggest or run factory reset, wipe, format, or recovery       │
│ 2. NEVER suggest or run `adb shell pm disable` or `disable-user`       │
│ 3. NEVER suggest or run `adb reboot bootloader` or `fastboot`          │
│ 4. NEVER ask the user to unlock their bootloader or install root       │
│ 5. ONLY allow `pm uninstall -k --user 0 <pkg>` for user-approved List A│
│ 6. NEVER touch or uninstall critical system packages (List C)          │
│ 7. ALWAYS route all ADB commands through scripts/safety_guard.py       │
│ 8. ALWAYS verify FCM socket alive before completing any task           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Programmatic Command Interceptor (`scripts/safety_guard.py`)

All ADB commands executed across the Python engine pass through `assert_command_safe()`. If any dangerous pattern is detected:

```text
[SECURITY INTERCEPTOR TRIGGERED]
Blocked dangerous command containing: 'uninstall'
Reason: Noti-Fixer strictly forbids root, uninstalls, data wipes, or destructive modifications.
```

The process halts immediately, protecting your phone before the command can even reach the ADB daemon.

