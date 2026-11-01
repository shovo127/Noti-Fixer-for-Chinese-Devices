# Vivo OriginOS & iQOO: Jovi & Background Whitelist Architecture

**Author:** Mohammed Thuhidul Islam Shovo (shovo127)  
**System Scope:** Vivo OriginOS 3/4/5, FuntouchOS 13/14/15

---

## 1. Vivo Process Management Architecture

Vivo devices (Vivo X/V/Y series and iQOO series) use a dual-tier battery restriction model:
1. **PEM (Power & Energy Management - `com.vivo.pem`):** Enforces per-app standby policies and controls whether an app can run in the background when battery level drops.
2. **ABE (Application Behavior Engine - `com.vivo.abe`):** Analyzes process heuristics and silences background sync adapters if the user hasn't interacted with the app recently.

---

## 2. High Background Power Consumption Restriction

By default, OriginOS limits all user apps to "Smart Background Control", which restricts background CPU cycles after 5 minutes of screen off.

### Remediation via ADB:
Grant unrestricted background execution:
```bash
# Allow Run in Background
cmd appops set <package> RUN_IN_BACKGROUND allow
cmd appops set <package> RUN_ANY_IN_BACKGROUND allow

# Grant Vivo Autostart (Op 10008)
cmd appops set <package> 10008 allow

# Whitelist from Android Doze
dumpsys deviceidle whitelist +<package>

# Grant Unmetered Data in Background
cmd netpolicy add restrict-background-whitelist <UID>
```

---

## 3. Persistent FCM Socket Preservation

On OriginOS, Google Play Services (`com.google.android.gms`) must be explicitly whitelisted in battery optimization. When done:
- GMS maintains uninterrupted TCP connection to `mtalk.google.com:5228`.
- Incoming calls on WhatsApp, Telegram, and WeChat ring in real-time even with screen off and Always-On-Display inactive.
