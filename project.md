# Project Overview
- **Core Goal:** Non-destructive push notification reliability engine & power/battery optimizer for aggressive OEM Chinese Android skins (Xiaomi/HyperOS, OPPO/ColorOS, Vivo/OriginOS, Huawei/HarmonyOS).
- **Target Audience:** Android power users and developers suffering from delayed or killed background notifications on OEM devices.

## Architecture & Tech Stack
- **Languages/Frameworks:** Python 3.10+, ADB (Android Debug Bridge), Bash shell scripts (`millet_watchdog.sh`), Windows Batch scripts.
- **Database/State Management:** JSON snapshots in `backups/` (timestamped pre-flight states, rollback scripts).
- **Tooling:** ADB wireless/USB debugging, Android AppOps, DeviceIdleController (Doze whitelist), Android Standby Buckets.

## High-Level Rules
- **Rule 1 (Safety First):** Strictly zero destructive operations (no root, no bootloader unlock, no `pm clear`, no factory reset).
- **Rule 2 (Empirical Verification):** Verify FCM sockets and wake locks via live dumpsys before declaring success.
- **Rule 3 (Strict Token Mitigation):** All changes must use localized diffs and maintain `state.md`.
