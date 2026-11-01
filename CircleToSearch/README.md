# Circle to Search (CTS) Companion for Chinese ROMs

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**Target:** Xiaomi HyperOS, Vivo OriginOS, Oppo ColorOS, Meizu Flyme

---

## Overview

Chinese OEM ROMs often restrict or omit Google's native Circle to Search (Omnient) launcher integration. This companion engine provisions the necessary `WRITE_SECURE_SETTINGS`, voice interaction services, and intent shortcuts so you can trigger Circle to Search anywhere on your screen.

### Capabilities
- **Quick Settings Tile:** Toggle or trigger full screen capture and search from notification shade.
- **Gesture Trigger:** Long press home button or bottom gesture pill to launch Google Omnient activity.
- **Zero Root Required:** Functions entirely through ADB permissions.

### Setup Instructions
1. Run `setup_cts.bat` on your PC with your phone connected via ADB.
2. Ensure the official **Google** app is installed from the Play Store.
3. If using `MiCTS_2.6.apk`, grant all on-screen permissions on first launch.
