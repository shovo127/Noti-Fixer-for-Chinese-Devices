# Safe Debloating & Ecosystem Integration Guide

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)

Many users combine **Noti-Fixer** with community debloating solutions to remove unwanted vendor apps. However, aggressive or uninformed debloating frequently breaks the Android notification subsystem by removing critical IPC bridges.

This guide outlines safe debloating practices audited against top open-source repositories:
- [Universal Android Debloater Next Generation (UAD-NG)](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation)
- [MuntashirAkon Android Debloat List](https://github.com/MuntashirAkon/android-debloat-list)
- [Canta (Shizuku-powered debloater)](https://github.com/samolego/Canta)

---

## ⚠️ The Dangerous Trap: Bloat vs. FCM Infrastructure

Many naive debloat lists remove packages that appear to be bloatware but actually host the system's push notification bridges:

| Package | Common Mistake | True System Role |
| :--- | :--- | :--- |
| `com.google.android.gms` | Removed by "de-googlers" | **Hosts Firebase Cloud Messaging (FCM). Removing breaks 99% of app notifications.** |
| `com.google.android.gsf` | Removed as telemetry | **Google Services Framework. Required for FCM token exchange.** |
| `com.miui.powerkeeper` | Completely uninstalled | **Can cause bootloops or broken brightness/thermal curves on HyperOS 1.0/2.0.** Tune with Noti-Fixer instead of deleting. |
| `com.vivo.pem` / `com.vivo.abe` | Uninstalled via ADB | **Can cause battery calibration crashes on OriginOS.** |

---

## 🛡️ Safe Debloating Principles with Noti-Fixer

1. **Fix First, Debloat Second:**  
   Always run `NotiFixer_OneClick.bat` first and verify with `audit_fcm_doze.py` that your FCM push socket (`mtalk.google.com:5228`) is connected.
2. **Safe Packages to Remove:**
   - Vendor App Stores (`com.xiaomi.mipicks`, `com.heytap.market`, `com.vivo.appstore`)
   - Vendor Browsers (`com.mi.globalbrowser`, `com.heytap.browser`)
   - Vendor Video & Music Players (`com.miui.videoplayer`, `com.miui.player`)
   - Analytics sinks (use Noti-Fixer's `--dns-adguard` flag to neutralize without removing system dependencies)
3. **If You Use Canta or UAD-NG:**
   - Always choose **Recommended** or **Advanced** presets with caution. Never use **Expert** without checking package dependencies.
   - If push notifications stop working after debloating, run:
     ```bash
     python scripts/audit_fcm_doze.py
     ```
     Noti-Fixer will immediately diagnose whether `com.google.android.gms` or your messaging app's push socket was severed.
4. **The 3-List Architecture (Mandatory AI Consultation Gate):**
   Before removing or restricting any application, AI pairing agents must present three editable lists:
   - **List A (Debloat Candidates):** Explicit non-critical vendor bloatware (e.g. `com.miui.analytics`, `com.mfashiongallery.emag`, `com.xiaomi.mipicks`).
     - Executed safely via: `adb shell pm uninstall -k --user 0 <package>`
     - Reversible via: `adb shell cmd package install-existing --user 0 <package>`
   - **List B (Background-Restrict Candidates):** Applications the user uses occasionally (e.g. food delivery, ride-sharing, e-commerce, secondary social media).
     - Applied via: `cmd appops set <pkg> 10008 ignore`, `cmd appops set <pkg> 10021 ignore`, and Standby Bucket `40 (RARE)`.
     - When opened by the user, the app runs at 100% full speed with active foreground permissions.
   - **List C (Protected System Frameworks):** Critical packages that must NEVER be touched (SystemUI, Telephony, Settings, Keyboards, Google Play Services, Google Play Store, Download Manager, Zoom, and user banking/messaging applications). Any attempt to uninstall or restrict List C triggers an automatic abort via `safety_guard.py`.


