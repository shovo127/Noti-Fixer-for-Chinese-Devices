# #05 — Schema.md: Data Schemas & App Categorization Dictionary

**Project Name:** Noti-Fixer for Chinese Devices  
**Repository:** `https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices`  
**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Document Version:** 2.0.0 (Blueprint Lock Standard)  

---

## 1. Package Categorization Dictionary

Noti-Fixer classifies packages into three deterministic tiers:

### Tier 1: Priority Communication Packages (Instant Push Required)
These packages receive full Doze exemptions, Bucket 5 elevation, and all heads-up AppOps:

```json
{
  "tier": 1,
  "category": "PRIORITY_COMMUNICATION",
  "policy": {
    "standby_bucket": 5,
    "doze_whitelist": true,
    "netpolicy_unrestricted": true,
    "appops": {
      "RUN_IN_BACKGROUND": "allow",
      "RUN_ANY_IN_BACKGROUND": "allow",
      "WAKE_LOCK": "allow",
      "10008": "allow",
      "10017": "allow",
      "10020": "allow",
      "10021": "allow",
      "10022": "allow",
      "10028": "allow",
      "10029": "allow"
    }
  },
  "packages": [
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.gm",
    "com.whatsapp",
    "com.whatsapp.w4b",
    "com.imo.android.imoim",
    "com.facebook.orca",
    "com.facebook.katana",
    "com.instagram.android",
    "org.telegram.messenger",
    "org.telegram.plus",
    "org.thoughtcrime.securesms",
    "com.tencent.mm",
    "com.discord",
    "com.microsoft.office.outlook",
    "com.Slack",
    "com.viber.voip",
    "com.skype.raider"
  ]
}
```

---

### Tier 2: Non-Destructive Background Optimization (Idle Suppressed)
These user-approved packages have cold autostart suppressed (`10008 ignore`, `10021 ignore`), but preserve active background networking, wakelocks, and normal execution so tasks (calls, downloads, tracking) never stall:

```json
{
  "tier": 2,
  "category": "SAFE_BACKGROUND_DRAINERS",
  "policy": {
    "standby_bucket": 20,
    "doze_whitelist": false,
    "netpolicy_blacklist": false,
    "appops": {
      "RUN_IN_BACKGROUND": "allow",
      "RUN_ANY_IN_BACKGROUND": "allow",
      "WAKE_LOCK": "allow",
      "10008": "ignore",
      "10021": "ignore"
    }
  },
  "packages": [
    "com.bKash.customerapp",
    "com.konasl.nagad",
    "com.pathao.user",
    "com.global.foodpanda.android",
    "com.ubercab",
    "com.daraz.android",
    "com.othoba.android",
    "us.zoom.videomeetings",
    "com.facebook.katana",
    "com.mfashiongallery.emag"
  ]
}
```

---

### Tier 3: Core System Frameworks (Read-Only / Protected)
These packages must NEVER be restricted, blacklisted, or modified:

```json
{
  "tier": 3,
  "category": "PROTECTED_SYSTEM_FRAMEWORKS",
  "policy": {
    "immutable": true,
    "never_uninstall": true,
    "never_force_stop": true,
    "never_blacklist_network": true
  },
  "packages": [
    "android",
    "com.android.systemui",
    "com.android.vending",
    "com.miui.home",
    "com.android.settings",
    "com.android.phone",
    "com.android.server.telecom",
    "com.android.providers.contacts",
    "com.miui.securitycenter",
    "com.android.packageinstaller",
    "com.miui.packageinstaller",
    "com.google.android.webview",
    "com.xiaomi.xmsf"
  ]
}
```

---

## 2. Reversible Backup Schema (`backups/backup_*.json`)

Every execution of `apply_notification_fix.py` produces a standard JSON backup schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SystemBackupSnapshot",
  "type": "object",
  "properties": {
    "timestamp": { "type": "integer" },
    "serial": { "type": "string" },
    "device_fingerprint": {
      "type": "object",
      "properties": {
        "model": { "type": "string" },
        "brand": { "type": "string" },
        "rom_version": { "type": "string" },
        "android_api": { "type": "integer" }
      }
    },
    "activity_manager_native_boot_use_freezer": { "type": "string" },
    "cached_apps_freezer": { "type": "string" },
    "private_dns_mode": { "type": "string" },
    "private_dns_specifier": { "type": "string" },
    "MILLET_NO_RESTRICT_APP": { "type": "string" },
    "doze_whitelist": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["timestamp", "serial", "doze_whitelist"]
}
```

