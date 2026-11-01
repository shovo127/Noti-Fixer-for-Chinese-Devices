# Xiaomi HyperOS & MIUI: PowerKeeper & MILLET Architecture

**Author:** Mohammed Thuhidul Islam Shovo (shovo127)  
**System Scope:** Xiaomi HyperOS 1.0/2.0, MIUI 12/13/14 (Android 12 to 16)

---

## 1. The Core Mechanism of Notification Suppression

Xiaomi's process governance operates on three distinct, layered defense mechanisms designed to minimize idle battery consumption at the expense of real-time push notifications:

```
[Screen Off] 
     │
     ▼
[Layer 1: PowerKeeper Daemon (com.miui.powerkeeper)]
     │ ── Evaluates app score & screen state
     ▼
[Layer 2: MILLET Framework (System Key: MILLET_NO_RESTRICT_APP)]
     │ ── Checks if package is present in kernel/framework whitelist
     ▼
[Layer 3: Cgroup v2 cached_apps_freezer]
     │ ── Freezes process threads and drops TCP socket to mtalk.google.com:5228
     ▼
[Notification Deadlock (Delayed until screen unlocked)]
```

---

## 2. Deep Dive: `com.miui.powerkeeper`

`PowerKeeper` is the privileged background system service responsible for:
- Enforcing MIUI/HyperOS "Smart Battery" modes.
- Restricting network access for background apps when screen turns off.
- Overriding standard Android Doze rules unless explicitly forced via AppOps and MILLET.
- Periodically scrubbing `Settings.System.MILLET_NO_RESTRICT_APP` during app updates and battery optimizer sweeps.

---

## 3. The MILLET Engine (`MILLET_NO_RESTRICT_APP`)

MILLET is Xiaomi's kernel-integrated process monitor. It holds a comma-delimited string in the Android `system` settings table:

```bash
settings get system MILLET_NO_RESTRICT_APP
```

### Problem Behavior:
Whenever an app is updated from Google Play Store or APK install, HyperOS removes the app from `MILLET_NO_RESTRICT_APP`, re-enabling aggressive freezing!

### The Remediation:
1. Inject all critical packages (`com.google.android.gms`, `com.whatsapp`, etc.) into `MILLET_NO_RESTRICT_APP`.
2. Run `scripts/millet_watchdog.sh` or use NotiGuard to detect and re-inject cleared packages automatically.

---

## 4. Vendor-Specific AppOps

Xiaomi defines custom AppOps codes that override standard Android permissions:

| AppOp Code | Name | Function in HyperOS / MIUI |
|------------|------|-----------------------------|
| `10008` | `OP_AUTO_START` | Allows application to autostart upon boot and intent triggers |
| `10021` | `OP_SHOW_WHEN_LOCKED` | Allows secondary background popup and lock screen activity launch |
| `SYSTEM_ALERT_WINDOW` | Overlay | Ensures heads-up floating notification delivery |

Command to grant:
```bash
cmd appops set <package> 10008 allow
cmd appops set <package> 10021 allow
```

---

## 5. Linux Cgroup v2 Socket Freezer (`use_freezer`)

In Android 14, 15, and 16, Google introduced aggressive `cached_apps_freezer`. On HyperOS, this freezes the Linux socket descriptor for `mtalk.google.com:5228`. 

When a socket is frozen at the kernel level, Google Play Services cannot receive TCP SYN/ACK or push packets. To remediate:

```bash
device_config put activity_manager_native_boot use_freezer false
setprop persist.sys.freezer false
```

---

## 6. The NotiGuard Legacy Architecture (Target SDK 22)

Android introduced strict runtime permission checks in API 23 (Android 6.0 Marshmallow) for `android.permission.WRITE_SETTINGS`.
However, apps compiled with `targetSdkVersion 22`:
1. Inherit the legacy permission contract where `WRITE_SETTINGS` can be granted without requiring Root or Shizuku.
2. Can persist `Settings.System.MILLET_NO_RESTRICT_APP` across device reboots directly from an on-device service.
