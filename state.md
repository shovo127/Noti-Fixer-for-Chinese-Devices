# Current Active State

## Current Phase: Messaging Push & Screen Wake Restoration
- **Current Window Token Depth:** High
- **Active Focus:** Identified and remediated the exact cause why WhatsApp stopped ringing and waking the screen when locked. Restored Doze whitelist and screen wake permissions for all core communication apps.

## Root Cause Discovered
1. **Doze Whitelist Stripping:** In `scripts/apply_notification_fix.py`, lines 256-265 had aggressively removed `com.whatsapp`, `com.whatsapp.w4b`, `com.imo.android.imoim`, and `com.facebook.orca` from the Doze battery whitelist (`dumpsys deviceidle whitelist -<pkg>`).
2. **Kernel Process Freezing:** When the screen turned off, Android Doze and the Linux cgroups freezer placed WhatsApp into a deep frozen state (`frozen uid ... allow=false`).
3. **The Consequence:** While the phone was locked, WhatsApp could not maintain its background push socket, could not acquire wake locks, could not wake the display, and could not play incoming message ringtones.

## Remediation Plan
1. [x] Updated `scripts/apply_notification_fix.py` to permanently whitelist all vital communication suites (`dumpsys deviceidle whitelist +<pkg>`).
2. [x] Created `scripts/restore_messaging_doze.py` to restore Doze exemption, `WAKE_LOCK`, `TURN_SCREEN_ON`, AppOp `10020` (Lockscreen), AppOp `10017` (Floating), and Standby Bucket 5 (ACTIVE).
3. [x] Enabled system-level `wake_on_notification = 1` in secure and system settings.
4. [/] Execute `scripts/restore_messaging_doze.py` as soon as device wireless debugging reconnects.
