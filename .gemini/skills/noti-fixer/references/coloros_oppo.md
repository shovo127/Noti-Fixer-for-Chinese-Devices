# Oppo, OnePlus & Realme: ColorOS Process & Athena Architecture

**Author:** Mohammed Thuhidul Islam Shovo (shovo127)  
**System Scope:** ColorOS 12/13/14/15, OxygenOS 12/13/14/15, Realme UI 3/4/5/6

---

## 1. ColorOS Process Suspension System

Oppo, OnePlus, and Realme devices enforce three core governors:
1. **Athena Engine (`com.oplus.athena` / `com.coloros.athena`):** The primary process killer and resource allocator. It automatically freezes any app not declared in the system foreground whitelist.
2. **GuardElf (`com.coloros.oppoguardelf`):** Monitors battery draw and isolates apps that trigger frequent wake locks.
3. **Quick Freeze (Deep Sleep):** Puts idle applications into a suspended Linux cgroup where all socket activity is queued or dropped.

---

## 2. Preventing Silent Socket Drops

To prevent ColorOS from cutting the push notification pipeline:

### 1. Disable Cgroup Socket Freezer
```bash
device_config put activity_manager_native_boot use_freezer false
setprop persist.sys.freezer false
```

### 2. Bypass Athena & Quick Freeze
```bash
# Allow app to run unrestricted in background
cmd appops set <package> RUN_IN_BACKGROUND allow
cmd appops set <package> 10008 allow

# Prevent system from automatically revoking permissions
cmd appops set <package> AUTO_REVOKE_PERMISSIONS_IF_UNUSED ignore

# Whitelist in DeviceIdle
dumpsys deviceidle whitelist +<package>
```

### 3. Google Play Services Protection
Ensuring `com.google.android.gms` and `com.google.android.gsf` are added to `dumpsys deviceidle whitelist` ensures continuous `mtalk.google.com:5228` socket connectivity.
