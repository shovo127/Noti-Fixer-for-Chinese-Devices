# Contributing to Noti-Fixer for Chinese Devices

Thank you for your interest in contributing to **Noti-Fixer for Chinese Devices**! This project is maintained by **Mohammed Thuhidul Islam Shovo (shovo127)** and open to the global Android developer community.

---

## 🛠️ Code Standards & Architecture Philosophy

1. **Zero External Dependencies:**
   - All core scripts must run using Python 3.8+ Standard Library (`subprocess`, `json`, `argparse`, `socket`, `re`, `concurrent.futures`). Do not add external pip packages unless strictly optional.
2. **Strict Non-Destructive Safety:**
   - Solutions must **never** require root, bootloader unlock, or blind deletion of vendor packages.
   - All system changes must be idempotent, safely retryable, and 100% reversible via the restore templates.
3. **Cross-Platform Compatibility:**
   - Scripts must operate reliably on Windows (Command Prompt & PowerShell), macOS (zsh), and Linux (bash).
4. **Tested Verification:**
   - Whenever introducing a new ROM fix, verify live FCM socket behavior (`dumpsys activity service com.google.android.gms/.gcm.GcmService` and `/proc/net/tcp` port 5228).

---

## 🚀 Development Workflow

1. **Fork the Repository:** Create your own feature branch:
   ```bash
   git checkout -b feature/my-rom-enhancement
   ```
2. **Make Changes:** Keep code clean, documented, and conformant with Python PEP 8.
3. **Validate Syntax:**
   ```bash
   python -m py_compile scripts/detect_device.py scripts/audit_fcm_doze.py scripts/apply_notification_fix.py scripts/scan_ports.py
   ```
4. **Open a Pull Request:** Describe your target device, tested Android SDK, and logs.

---

## 💬 Community Questions & Feedback
If you have questions, please open a GitHub Issue or reach out via [GitHub Discussions](https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices/issues).
