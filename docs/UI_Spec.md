# #03 — UI_Spec.md: User Interface & CLI Specifications

**Project Name:** Noti-Fixer for Chinese Devices  
**Repository:** `https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices`  
**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Document Version:** 2.0.0 (Blueprint Lock Standard)  

---

## 1. Design Principles & Brand Tone

* **Simplicity:** Any non-technical user must be able to resolve their issue by pressing `1` or `2`.
* **Zero Guesswork:** Always display clear ANSI color-coded statuses:
  * Green (`\033[92m`): `PASS`, `ACTIVE`, `WHITLELISTED`, `EXEMPTED`.
  * Red (`\033[91m`): `FAIL`, `BLOCKED`, `FROZEN`, `RESTRICTED`.
  * Yellow (`\033[93m`): `WARNING`, `ATTENTION REQUIRED`, `THROTTLED`.
  * Cyan (`\033[96m`): `SECTION HEADERS`, `INFO`, `PROMPTS`.
* **Cross-Platform Compatibility:** Guaranteed UTF-8 rendering across Windows PowerShell, Windows Command Prompt (`chcp 65001`), Linux Bash, and macOS Terminal.

---

## 2. Interactive Menu Layout

```text
==============================================================================
       NOTI-FIXER FOR CHINESE DEVICES - PRODUCTION REPAIR SUITE
            Architect: Mohammed Thuhidul Islam Shovo (shovo127)
                        Open-Source MIT License
==============================================================================

  Targeting: Xiaomi HyperOS / MIUI | Vivo OriginOS | Oppo ColorOS | HarmonyOS

  [1] ⚡ Simple Wireless Wi-Fi Connect & Fix (No Cable Needed - Recommended)
  [2] 🔌 USB Cable 1-Click Notification & Battery Fix
  [3] 🔍 Live Diagnostic Audit (FCM Socket, Android Doze, Kernel Freezer)
  [4] 📱 Device Fingerprint & Hardware/ROM Profile
  [5] 🔋 Battery Drain Analysis & Culprit Inspector
  [6] 🛡️ Push & Start HyperOS MILLET Watchdog Daemon
  [7] 🔄 Wireless ADB Port Scanner (Find new port after reboot)
  [8] ⏪ Revert Changes (Master 100% Safe Rollback)
  [9] ❌ Exit

==============================================================================
Enter choice [1-9]: 
```

---

## 3. Step-by-Step CLI Visual Feedback

### 3.1 Interactive User Consultation Screens

Before applying changes, the engine prompts the user interactively (unless `--auto` flag is passed):

```text
==============================================================================
⚡ [USER CONSULTATION] INSTANT NOTIFICATION PRIORITY SUITE
==============================================================================
 Detected communication apps on your phone:
   [ 1] com.google.android.gms
   [ 2] com.google.android.gm
   [ 3] com.whatsapp
   [ 4] com.whatsapp.w4b
   [ 5] com.imo.android.imoim
   [ 6] com.facebook.orca
   [ 7] com.instagram.android

 Options:
   [Y] Prioritize ALL detected apps (Recommended - Instant notifications)
   [A] Add custom packages

 Enter choice [Y/a] (Default: Y):

==============================================================================
🔋 [USER CONSULTATION] CUSTOM BATTERY DRAIN RESTRICTOR
==============================================================================
 Noti-Fixer will NEVER restrict apps without your consent.
 The following background drainers were detected on your phone:

   [ 1] bKash (Fintech / Mobile Wallet)               (com.bKash.customerapp)
   [ 2] Nagad (Fintech / Mobile Wallet)               (com.konasl.nagad)
   [ 3] Pathao (Ride-sharing / Food delivery)         (com.pathao.user)
   [ 4] Foodpanda (Food delivery)                     (com.global.foodpanda.android)
   [ 5] Uber (Ride-sharing)                           (com.ubercab)
   [ 6] Daraz (E-commerce / Shopping)                 (com.daraz.android)
   [ 7] Othoba (E-commerce / Shopping)                (com.othoba.android)
   [ 8] Zoom (Video Conferencing)                     (us.zoom.videomeetings)
   [ 9] Google Play Store (Idle self-check throttling)(com.android.vending)
   [10] Xiaomi Wallpaper Carousel (Glance / Bloat)    (com.mfashiongallery.emag)

 Options:
   [A] Restrict ALL listed drainers (Recommended - Maximum battery life)
   [C] Custom select by number (e.g., 1, 2, 5, 8)
   [S] Skip battery restrictions (Keep phone default)

 Enter choice [A/c/s] (Default: A):
```

### 3.2 Automated Execution Progress Stream

When confirmed, the engine renders a standardized 7-step progress stream:

```text
========================================================================
   NOTI-FIXER: APPLYING HIGHEST-LEVEL INSTANT NOTIFICATION SUITE
========================================================================
 [1/7] Creating 100% Reversible System Backup...
       -> Backup successfully saved to: backups\backup_192_168_0_105_38473_1793808402.json

 [2/7] Disabling Kernel Cgroup Socket Freezer & Cached Freezer...
       -> Cached apps & ActivityManager socket freezer: DISABLED

 [3/7] Whitelisting Android Doze, Standby Buckets & Netpolicy...
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.google.android.gms
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.google.android.gm
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.whatsapp
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.whatsapp.w4b
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.imo.android.imoim
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.facebook.orca
       • Whitelisted (Bucket 5 / Doze / Netpolicy): com.instagram.android

 [4/7] Applying Vendor-Specific Engine Injections & Display AppOps...
       -> Detected: Xiaomi HyperOS / MIUI Platform
       -> Configuring Autostart (10008), Heads-up Float (10017), Lockscreen (10020), Sound (10022)...
       -> Injected 11 priority apps into PowerKeeper & MILLET whitelists

 [5/7] Restricting Heavy Background Apps (Preserving RAM & Battery)...
       • Restricted Background Execution: com.android.vending
       • Restricted Background Execution: com.bKash.customerapp
       • Restricted Background Execution: com.konasl.nagad
       • Restricted Background Execution: com.pathao.user
       • Restricted Background Execution: com.global.foodpanda.android
       • Restricted Background Execution: com.ubercab
       • Restricted Background Execution: com.othoba.android
       • Restricted Background Execution: us.zoom.videomeetings
       • Restricted Background Execution: com.facebook.katana
       • Restricted Background Execution: com.mfashiongallery.emag
       • Optimized Chrome: Safe background sleep, 100% foreground speed

 [6/7] Private DNS: Preserving user default (Use --dns-adguard to enable AdGuard)

 [7/7] Pulsing Google FCM Connection Heartbeat...
       -> FCM Wakeup Heartbeat Broadcast delivered to GMS.

✔ All highest-level notification fixes applied successfully!
========================================================================
```

---

## 4. Verification Output Table Specification

Upon completion, the diagnostic report must format findings in a clean Markdown/terminal table:

| Application | Category | Standby Bucket | Heads-Up (10017) | Lock Screen (10020) | Sound/Vibe (10022) | Background Net |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gmail** | Priority | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **WhatsApp / WA Business** | Priority | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **imo** | Priority | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **Messenger** | Priority | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **Instagram** | Priority | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **Google Play Services** | Backbone | `5` (Exempted) | `allow` | `allow` | `allow` | Whitelisted |
| **bKash / Nagad / Othoba** | Restricted | `45` (Restricted) | — | — | — | Blacklisted |
| **Zoom / Facebook App** | Restricted | `45` (Restricted) | — | — | — | Blacklisted |
| **Google Play Store** | Restricted | `45` (Restricted) | — | — | — | Blacklisted |

