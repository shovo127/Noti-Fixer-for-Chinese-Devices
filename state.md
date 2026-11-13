# Current Active State

## Current Phase: Clean Revert Verified & Complete
- **Current Window Token Depth:** High
- **Active Focus:** Clean revert of Notification Sound System verified live on Xiaomi 13 (`192.168.1.160:39035`).

## Live Verified Outcomes
1. **Messaging Apps Restored to Doze Whitelist:**
   - `com.whatsapp`: Verified in `dumpsys deviceidle whitelist`
   - `com.whatsapp.w4b`: Verified in `dumpsys deviceidle whitelist`
   - `com.facebook.orca`: Verified in `dumpsys deviceidle whitelist`
   - `com.imo.android.imoim`: Verified in `dumpsys deviceidle whitelist`
   - `com.android.mms`: Verified in `dumpsys deviceidle whitelist`
2. **Notification Sound URIs Restored:**
   - `system.notification_sound`: Set cleanly to `content://media/internal/audio/media/25?title=Fresh`
   - `system.notification_sound_cache`: Set cleanly
   - `sms_received_sound`: Set cleanly
3. **Screen Wake on Incoming Notifications:**
   - `system.wakeup_for_keyguard_notification = 1` (Live verified)
4. **Zero Collateral Changes:**
   - No debloat, no system apps, no user data, no security settings modified.
