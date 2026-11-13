# Current Active State

## Current Phase: Clean Revert of Notification Sound System
- **Current Window Token Depth:** High
- **Active Focus:** Clean revert of notification sound system to factory default per user request.

## Planned Actions (Surgical Revert Only)
1. [x] Authored `scripts/revert_notification_system.py` to:
   - Restore all messaging suites (`com.whatsapp`, `com.whatsapp.w4b`, `com.facebook.orca`, `com.imo.android.imoim`, `com.google.android.gm`, `com.android.mms`) to Doze whitelist (`dumpsys deviceidle whitelist +<pkg>`).
   - Restore Standby Bucket 5 (ACTIVE).
   - Revert `notification_sound`, `notification_sound_cache`, `calendar_alert`, `sms_received_sound` to clean system defaults.
   - Unsnooze system notification alerts (`cmd notification unsnooze`).
   - Enable screen wake for notifications (`wake_on_notification = 1`).
   - Restore Messenger AppOp 10028 to allow.
2. [/] Awaiting active Wireless Debugging port (or USB) from user to apply execution.
