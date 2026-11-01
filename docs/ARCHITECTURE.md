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

### Tier 1: Cgroup v2 Socket Freezer
In Android 14 and 15, Google enabled the `cached_apps_freezer` natively in Android Framework. On Chinese ROMs with aggressive kernel heuristics, GMS (`com.google.android.gms`) is treated as an idle cached process when screen turns off. 

**Remediation:**
```bash
device_config put activity_manager_native_boot use_freezer false
setprop persist.sys.freezer false
setprop sys.use_freezer false
```
This forces the Android runtime to respect socket state over aggressive freezing.

---

### Tier 2: Xiaomi MILLET Subsystem
Xiaomi's proprietary `MILLET` (Mobile Intelligent Lifecycle & Longevity Enhancement Technology) monitors app sockets at the binder driver level.
- Framework Key: `Settings.System.MILLET_NO_RESTRICT_APP`
- Vulnerability: Whenever an app receives an update via Google Play Store, MIUI/HyperOS system daemon strips the package from this key.

**Remediation:**
1. Atomic injection of all messaging packages into `MILLET_NO_RESTRICT_APP`.
2. Running `millet_watchdog.sh` daemon to continuously poll and recover stripped keys without user intervention.

---

### Tier 3: Vendor-Specific AppOps Mapping

| Brand | AppOp Code | Name | Behavioral Impact |
| :--- | :--- | :--- | :--- |
| **Xiaomi** | `10008` | `OP_AUTO_START` | Blocks broadcast receiver wakeup from cold boot |
| **Xiaomi** | `10021` | `OP_SHOW_WHEN_LOCKED` | Suppresses heads-up floating banner when locked |
| **Vivo** | `10008` | `OP_AUTO_START` | Allows background daemon re-invocation |
| **Oppo** | `10` | `RUN_IN_BACKGROUND` | Prevents Athena quick freeze after 3 min |
| **Universal**| `40` | `WAKE_LOCK` | Guarantees CPU cycle allocation during push |

---

### Tier 4: Background Netpolicy
Even when an app is permitted to run, Android's network policy manager can restrict background socket reads on metered connections.

**Remediation:**
```bash
cmd netpolicy add restrict-background-whitelist <UID>
dumpsys deviceidle whitelist +<PACKAGE>
```
This guarantees bidirectional traffic routing to Google FCM and messaging push endpoints.

