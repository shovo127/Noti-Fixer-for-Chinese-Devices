# #06 — Plan.md: Phased Execution & Safety Verification Plan

**Project Name:** Noti-Fixer for Chinese Devices  
**Repository:** `https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices`  
**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Document Version:** 2.0.0 (Blueprint Lock Standard)  

---

## 1. Phased Execution Roadmap

```
[Phase 1: Environment & Port Discovery]
   ├── Check existing wireless ADB connection (e.g. 192.168.1.160:PORT)
   └── If offline, run scan_ports.py across local IP to acquire active port
             │
[Phase 2: Pre-Flight Audit & Snapshot]
   ├── Detect device brand, build, and API version (detect_device.py)
   ├── Capture reversible snapshot into backups/ (create_system_backup)
   └── Run non-invasive diagnostic check (audit_fcm_doze.py, inspect_battery.py)
             │
[Phase 3: Core Notification & Process Remediation]
   ├── Disable Cgroup v2 socket freezer (cached_apps_freezer disabled)
   ├── Elevate Priority Communication Apps to Bucket 5 (STANDBY_BUCKET_EXEMPTED)
   ├── Grant Heads-up (10017), Lockscreen (10020), Sound (10022), Autostart (10008)
   └── Inject PowerKeeper & MILLET system table whitelists
             │
[Phase 4: Battery Optimization & Drainer Suppression]
   ├── Demote Heavy Background Drainers to Bucket 45 (STANDBY_BUCKET_RESTRICTED)
   ├── Set RUN_IN_BACKGROUND ignore, WAKE_LOCK ignore, 10008 ignore
   ├── Restrict Google Play Store (com.android.vending) background auto-checks
   ├── Disable Wallpaper Carousel (com.mfashiongallery.emag) lockscreen service
   └── Put Google Chrome into safe background sleep mode (preserve 100% foreground speed)
             │
[Phase 5: Self-Healing Watchdog Deployment]
   ├── Push millet_watchdog.sh to /data/local/tmp/millet_watchdog.sh
   ├── Grant execution permissions (chmod +x)
   └── Start asynchronous daemon via nohup under shell UID
             │
[Phase 6: Live Verification & Empirical Proof]
   ├── Verify Google FCM push socket is CONNECTED (mtalk.google.com:5228)
   ├── Verify watchdog process is actively running in background
   └── Deliver structured Markdown verification summary to user
```

---

## 2. Strict Safety Boundaries & Interceptor Rules

Every ADB shell command MUST pass `safety_guard.py` before execution.

### 2.1 Hard Prohibited Command Patterns (Immediate Abort)
```python
PROHIBITED_COMMAND_PATTERNS = [
    "uninstall",
    "pm clear",
    "disable-user",
    "pm disable",
    "reboot bootloader",
    "reboot recovery",
    "reboot fastboot",
    "fastboot",
    "recovery",
    "factory_reset",
    "wipe",
    "format",
    "erase",
    "rm -rf /",
    "rm -rf /data",
    "rm -rf /system",
    "su -c",
    "su ",
    "magisk",
    "kernelsu",
    "supersu",
    "blockdev",
    "dd if=",
    "flash ",
    "setenforce 0"
]
```

---

## 3. CI/CD & Automated Regression Testing

GitHub Actions CI (`.github/workflows/ci.yml`) runs across Python 3.8–3.12 and Ubuntu/Windows:
1. **Compilation Check:** Compiles all `.py` scripts via `python -m py_compile`.
2. **Safety Guard Self-Test:** Executes `scripts/safety_guard.py` to verify that destructive tokens are intercepted.
3. **CLI Help Flag Check:** Validates that `--help` flags return exit code 0 across all CLI modules.
4. **ShellCheck:** Validates `millet_watchdog.sh` and `NotiFixer_OneClick.sh` for POSIX compliance.
