# #04 — TRD.md: Technical Requirements & Architecture Document

**Project Name:** Noti-Fixer for Chinese Devices  
**Repository:** `https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices`  
**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Document Version:** 2.0.0 (Blueprint Lock Standard)  

---

## 1. Technical Architecture & Android Subsystems

Noti-Fixer operates across five core Android architectural layers:

```
┌────────────────────────────────────────────────────────┐
│  Application Layer (WhatsApp, Gmail, Play Store, etc.) │
├────────────────────────────────────────────────────────┤
│  AppOps & Notification Manager (MIUIOPs 10008-10029)   │
├────────────────────────────────────────────────────────┤
│  ActivityManager & Standby Buckets (Buckets 5 & 45)    │
├────────────────────────────────────────────────────────┤
│  NetworkPolicyManager & Doze (dumpsys deviceidle)      │
├────────────────────────────────────────────────────────┤
│  Kernel Cgroup v2 & Freezer (cached_apps_freezer)      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Low-Level Subsystem Breakdown

### 2.1 Kernel Cgroup v2 & Cached Apps Freezer (Android 14, 15, 16)
* **Mechanism:** Android 11+ introduced Cgroup v2 process freezing. When an app process moves to the background, Android freezes its threads and closes/freezes TCP socket listeners.
* **Failure Mode on Chinese ROMs:** Chinese firmware freezes GMS and messaging sockets within seconds of screen-off. When Google's `mtalk.google.com` server attempts to deliver a push packet, the socket does not acknowledge (TCP SYN/ACK fails), dropping push notifications.
* **Remediation Commands:**
  ```bash
  settings put global cached_apps_freezer disabled
  device_config put activity_manager_native_boot use_freezer false
  setprop persist.sys.freezer false
  setprop sys.use_freezer false
  ```

### 2.2 Android Standby Buckets (`ActivityManager`)
* **Values:**
  * `5` (`STANDBY_BUCKET_EXEMPTED`): Unrestricted network, jobs execute immediately, alarms unthrottled.
  * `10` (`STANDBY_BUCKET_ACTIVE`): Normal active foreground use.
  * `20` (`STANDBY_BUCKET_WORKING_SET`): Mild throttling when backgrounded.
  * `40` (`STANDBY_BUCKET_RARE`): Jobs delayed up to 24 hours.
  * `45` (`STANDBY_BUCKET_RESTRICTED`): Lowest non-cached tier. Background jobs blocked, no background network.
* **Remediation Commands:**
  * Priority apps promoted to Bucket 5: `am set-standby-bucket <pkg> 5`
  * Heavy drainers demoted to Bucket 45: `am set-standby-bucket <pkg> restricted`

### 2.3 Xiaomi HyperOS / MIUI Proprietary AppOps
Xiaomi wraps AOSP AppOps with custom OP codes inside `AppOpsService`:
* `OP_AUTO_START (10008)`: Controls whether an app can boot or autostart in the background.
* `OP_SHOW_WHEN_LOCKED (10020)`: Controls lockscreen notification display.
* `OP_FLOAT_NOTIFICATION (10017)`: Controls floating heads-up banner generation.
* `OP_NOTIFICATION_SOUND (10022)`: Controls notification ringtone and vibration.
* `OP_SECONDARY_AUTOSTART (10021)`: Controls waking up from third-party broadcasts.
* `OP_BACKGROUND_POPUP (10028)`: Controls full-screen incoming call wakeups.
* `OP_FLOATING_WINDOW (10029)`: Controls picture-in-picture and floating dialogs.
* **Remediation Command:**
  ```bash
  appops set <pkg> <OP_CODE> allow
  ```

### 2.4 Deep System Table Whitelists (PowerKeeper Subsystem)
Xiaomi's `com.miui.powerkeeper` reads directly from Android `Settings.System`:
* `cloud_memory_freeze_whitelist`: Prevents HyperOS memory killer from terminating cached sockets.
* `cloud_network_priority_whitelist`: Guarantees priority bandwidth on congested Wi-Fi/LTE.
* `power_pkg_white_list`: PowerCenter exemption list.
* `power_alarm_white_list`: AlarmManager wake-up allowance.
* `power_proc_white_list`: Background process exemption.
* `rt_pkg_white_list`: Real-time scheduling priority list.
* `MILLET_NO_RESTRICT_APP`: The core vendor process freeze exclusion list.

### 2.5 Background Network Policy & Doze
* **Doze Exemption:** `dumpsys deviceidle whitelist +<pkg>`
* **Netpolicy Unrestricted Background Data:** `cmd netpolicy add restrict-background-whitelist <UID>`
* **Background Data Blacklisting (Drainers):** `cmd netpolicy add restrict-background-blacklist <UID>`

---

## 3. Persistent Watchdog Daemon (`millet_watchdog.sh`)

### 3.1 Architecture
The watchdog is an asynchronous POSIX shell loop executing inside the device's native Linux shell environment:
* Path: `/data/local/tmp/millet_watchdog.sh`
* Executed via: `nohup sh /data/local/tmp/millet_watchdog.sh >/dev/null 2>&1 &`
* Memory Footprint: `< 4 MB RAM`.
* CPU Utilization: `0.0%` (sleeps for 15-second cycles).

### 3.2 Recovery Logic
1. Every 15 seconds, inspects `settings get system MILLET_NO_RESTRICT_APP`.
2. If `com.google.android.gms` or priority apps are stripped by PowerKeeper, it instantly re-injects the complete CSV string.
3. Every 2 minutes, re-asserts `cached_apps_freezer disabled` and sends `com.google.android.intent.action.MCS_HEARTBEAT` to GMS to keep the GCM TCP socket live.
