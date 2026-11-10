# Deep Architecture & Scientific Remediation

**Author:** Mohammed Thuhidul Islam Shovo (shovo127)  
**System Scope:** Android 12, 13, 14, 15, 16 (AOSP, HyperOS, OriginOS, ColorOS, HarmonyOS)

---

## 1. Problem Topology: The Multi-Layer Suppression Cascade

Traditional Android push notifications rely on Google's Firebase Cloud Messaging (FCM). In stock Android (AOSP / Pixel), Google Play Services maintains a single long-lived TCP connection to `mtalk.google.com:5228`. When an event occurs, Google pushes a minimal wake packet over this socket, prompting the system to grant a temporary wake lock so the receiving app can process the notification.

Chinese OEM ROMs disrupt this pipeline at four distinct architectural tiers:

```
[Incoming Internet Push]
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. KERNEL LEVEL: Linux Cgroup v2 (cached_apps_freezer)      │
│    Freezes processes in SIGSTOP state; drops TCP sockets.   │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. VENDOR FRAMEWORK: Xiaomi MILLET / Vivo PEM / Oppo Athena │
│    Enforces custom process whitelists, ignoring Doze.       │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PERMISSION LAYER: Custom Vendor AppOps (10008 & 10021)   │
│    Blocks secondary launches, background popups & autostart.│
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. NETWORK POLICY: Android Netpolicy (Metered Restrictions) │
│    Blocks background sync adapters over cellular/Wi-Fi.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Scientific Remediation Specifications

### Tier 1: Cgroup v2 Socket Freezer & RAM Multitasking
In Android 12 through 16, Google enabled the `cached_apps_freezer` natively in Android Framework. 
- **The Pitfall of Disabling the Freezer:** Disabling the freezer forces cached apps to execute background threads continuously, leading to severe battery drain (80-120mA idle draw).
- **The Optimal Balance:** Noti-Fixer explicitly keeps `cached_apps_freezer` ENABLED. It freezes cached app processes in RAM (preserving exact chat screens, banking OTP sessions, and form data in memory) while using 0% background CPU. When prioritized messaging apps receive a push, Android kernel unfreezes them instantaneously.

**Configuration:**
```bash
settings put global cached_apps_freezer enabled
device_config put activity_manager_native_boot use_freezer true
device_config put activity_manager max_phantom_processes 32
```

---

### Tier 2: Xiaomi MILLET Subsystem & Immobulus Allowlist
Xiaomi's proprietary `MILLET` (Mobile Intelligent Lifecycle & Longevity Enhancement Technology) monitors app sockets at the binder driver level.
- Framework Key: `Settings.System.MILLET_NO_RESTRICT_APP`
- Vulnerability: Whenever an app receives an update via Google Play Store, MIUI/HyperOS system daemon strips the package from this key.

**Remediation:**
1. Atomic injection of all messaging packages into `MILLET_NO_RESTRICT_APP`.
2. Running `millet_watchdog.sh` daemon to continuously poll and recover stripped keys without user intervention.
3. Whitelisting messaging packages in HyperOS `power_pkg_white_list`, `power_service_white_list`, and Immobulus restrict wakeuplist.

---

### Tier 3: Vendor-Specific AppOps Mapping

| Brand | AppOp Code | Name | Behavioral Impact |
| :--- | :--- | :--- | :--- |
| **Xiaomi** | `10008` | `OP_AUTO_START` | Allows GMS broadcast receiver to wake the app from cold state |
| **Xiaomi** | `10021` | `OP_SECONDARY_AUTOSTART` | Allows secondary background invocation from incoming intents |
| **Xiaomi** | `10017` | `OP_FLOAT_NOTIFICATION` | Enables floating heads-up notifications |
| **Xiaomi** | `10020` | `OP_SHOW_WHEN_LOCKED` | Displays incoming alerts on the lockscreen |
| **Xiaomi** | `10022` | `OP_SOUND_VIBRATE` | Ensures ringtone and vibration trigger on incoming alerts |
| **Vivo** | `10008` | `OP_AUTO_START` | Allows background daemon re-invocation |
| **Oppo** | `10` | `RUN_IN_BACKGROUND` | Prevents Athena quick freeze after 3 min |
| **Universal**| `40` | `WAKE_LOCK` | Guarantees CPU cycle allocation during push delivery |

---

### Tier 4: FCM Push vs. Doze Whitelist (The Offline Zero-Drain Breakthrough)

A common mistake in Android optimization is forcing third-party messaging apps (e.g., Messenger, WhatsApp, imo) into `dumpsys deviceidle whitelist` (Battery Optimization: Unrestricted).

#### ❌ The Offline Drain Failure Mode:
When an app like Facebook Messenger or imo is in Doze Whitelist, Android Doze is completely bypassed for its alarms (`device_idle=--`). When a user turns off Wi-Fi and Mobile Data before going to bed:
1. Messenger's internal MQTT keepalive client (`Mqtt_Wakeup`) and imo's keepalive (`AlarmJobScheduler`) fire RTC wakeup alarms every few minutes.
2. Because the app is exempt from Doze, the alarm wakes the CPU from Deep Sleep (Suspend).
3. The app attempts to connect to its offline server, fails due to lack of network, and immediately reschedules another wakeup.
4. Over a 7-hour night, this causes **120+ unnecessary CPU wakeups**, draining 4–8% of the battery for zero notifications.

#### ✔️ The Noti-Fixer Scientific Architecture:
1. **Google Play Services (`com.google.android.gms`) is Doze Whitelisted:** GMS maintains the single unified push socket (`mtalk.google.com:5228`).
2. **Third-Party Messaging Apps are NOT Doze Whitelisted:** They are assigned to **Standby Bucket 10 (ACTIVE)** with full Autostart (`10008`) and Alert permissions (`10017`, `10020`, `10022`).
3. **Behavior When Online:** When an incoming message arrives, GMS receives the FCM push and grants a temporary high-priority wakelock to the target app. The app wakes up instantly, vibrates, rings, and displays the alert.
4. **Behavior When Offline:** When Wi-Fi/Mobile Data is turned OFF, Android Doze naturally defers the app's internal self-wakeups. The phone remains in undisturbed Deep Sleep (suspend), achieving true zero-drain (<0.1%/hr).

---

### Tier 5: Morning Alarm Clock Triple Protection
To guarantee that the user's morning wake-up alarm NEVER fails or gets silenced in deep sleep:
1. `com.android.deskclock` and `com.google.android.deskclock` are placed in the OS Doze Whitelist (`dumpsys deviceidle whitelist +<pkg>`).
2. Assigned to `STANDBY_BUCKET_EXEMPTED` (Bucket 5).
3. Injected into Xiaomi HyperOS `power_alarm_white_list`.
4. Messaging apps are strictly EXCLUDED from `power_alarm_white_list` so only real clock alarms have hardware RTC wake privileges.

---

### Tier 6: Centralized ADB Core & Non-Destructive Interceptor
To eliminate code duplication and maintain ironclad safety across all 12 modules:
1. **Unified ADB Engine (`scripts/adb_core.py`):** Provides DRY command execution, automatic wireless IP:PORT re-connection, device property querying, and timeout containment.
2. **Deterministic Interception (`scripts/safety_guard.py`):** Intercepts all destructive commands (`recovery`, `master_clear`, `wipe`, `format`, `erase`, `su`, `root`, `pm clear`, non-standard uninstalls) and protects 34+ critical system packages against uninstallation or freezing.

---

### Tier 7: Edge Ad-Blocking & Native System Ad Neutralization
Provides 0% RAM and 0% CPU ad-blocking without third-party VPN loopbacks:
1. **AdGuard Anycast Edge DNS:** Configures Android Private DNS to `dns.adguard.com` (with fallback to Mullvad/Control D), sinkholing global ad domains with zero latency.
2. **Android 14–16 AdServices Global Kill Switches:** Neutralizes AdMob SDK sandbox, Topics API, and Cross-App Advertising ID at the platform level.
3. **Xiaomi System Ad Daemons Neutralization:** Reversibly debloats `com.miui.msa.global` and `com.miui.analytics` for user 0 while disabling in-app recommendation toggles across File Manager, Themes, and Downloads.


