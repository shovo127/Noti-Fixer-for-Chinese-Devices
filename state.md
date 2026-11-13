# Current Active State

## Current Phase: Mi 13 Sound & Repeating Bubbles Remediation Completed & Verified
- **Current Window Token Depth:** Low
- **Active Focus:** Remediated both core issues on Xiaomi 13 (Mi 13). Live verified sound engine playback and suppressed repeating bubble/sound loops.

## Root Cause & Remediation Summary (100% Empirically Verified)
1. **Silent Notification Sounds on Other Apps (RESOLVED):**
   - **Root Cause:** `system.notification_sound` was set to `content://media/internal/audio/media/260?title=WaterDrop_preview&canonical=1`. Because `260` was in `ui/` rather than `notifications/`, `NotificationPlayer` threw `java.lang.NullPointerException: uri` & `FileNotFoundException` whenever WhatsApp, Gmail, SMS, or system apps attempted to play a notification sound. Messenger bypassed this because it used its own internal sound resource (`android.resource://com.facebook.orca/raw/new_message`).
   - **Remediation:** Repaired `system.notification_sound` and `system.notification_sound_cache` to the valid built-in sound `content://media/internal/audio/media/25?title=Fresh`. Tested via `cmd notification post`; confirmed in logcat that `AlertCoordinator: onViewBound, buzzBeep` executed with zero `MediaPlayer` crashes.
2. **Repeating Sound & Bubbles 15-16 Times (RESOLVED):**
   - **Root Cause 1 (Wireless Debugging Chime Loop):** Notification channel `DEVELOPER_IMPORTANT` (`-1|android|62|null|1000` - "Wireless debugging connected") was firing high-priority alerts with sound on every ADB handshake/reconnect.
   - **Root Cause 2 (Messenger Floating Window vs Bubbles Conflict):** AppOp `10028` (Show pop-up window while running in background) allowed Facebook Messenger to draw legacy floating chat heads while Android native conversation bubbles were also active (`notification_bubbles: 1`), creating window detachment and re-alert loops.
   - **Remediation:** 
     - Set `adb_notify` to `0` in global and secure settings to silence wireless debugging re-connection chimes.
     - Configured `com.facebook.orca` AppOp `10028` to `ignore`, eliminating duplicate overlay fighting while preserving normal heads-up and conversation bubbles.
     - Restored `com.android.mms` to the system Doze whitelist so text messages arrive instantly.

## Milestones & Status
- [x] Phase 1: Device Reconnection (`192.168.1.160:40495`)
- [x] Phase 2: Forensic Logcat & Dumpsys Diagnostics
- [x] Phase 3: Fix Broken System Notification Sound (`Fresh.ogg`)
- [x] Phase 4: Suppress Messenger Overlay Conflict (AppOp 10028) & ADB Connection Chimes
- [x] Phase 5: Empirical Live Verification of Audio Playback
- [x] Phase 6: Codebase Hardening in `apply_notification_fix.py`
- [x] Phase 7: Git Commit & Push

## Immediate Atomic Next Steps
1. [x] Run git commit and push changes to remote repository.
2. [x] Deliver detailed, clear Bengali explanation of root causes and fixes to the user.
