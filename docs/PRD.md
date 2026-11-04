# #01 — PRD.md: Product Requirements Document

**Project Name:** Noti-Fixer for Chinese Devices  
**Repository:** `https://github.com/shovo127/Noti-Fixer-for-Chinese-Devices`  
**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)  
**License:** MIT License (Copyright (c) 2026)  
**Document Version:** 2.0.0 (Blueprint Lock Standard)  

---

## 1. Executive Summary & Problem Statement

### 1.1 The Problem
Android smartphones manufactured by Chinese OEMs (Xiaomi HyperOS / MIUI, Vivo OriginOS / FuntouchOS, Oppo ColorOS / RealmeUI, Huawei/Honor HarmonyOS) enforce draconian background process termination and socket-freezing algorithms. 

These aggressive vendor engines:
1. **Freeze Network Sockets:** Kernel Cgroup v2 (`cached_apps_freezer`) freezes TCP sockets of background messaging apps, causing Google FCM push notifications to fail or arrive only when the screen is turned on.
2. **Suppress Display & Alerts:** Proprietary AppOps (e.g., Xiaomi's `10017` Floating Notification and `10022` Sound/Vibration) default to `ignore`, suppressing heads-up banners and ring/vibration alerts even when push packets arrive.
3. **Wipe Whitelists on Boot:** Proprietary power daemons (e.g., Xiaomi `com.miui.powerkeeper`) wipe user power whitelists and MILLET tables on every system reboot.
4. **Permit Severe Bloatware Drain:** While punishing third-party communication apps, vendor firmware permits preloaded bloatware (e.g., Wallpaper Carousel/Glance `com.mfashiongallery.emag`, system analytics) and unrestricted apps to drain battery and RAM freely.

### 1.2 The Solution
**Noti-Fixer** is an open-source, non-destructive universal remediation suite and AI Agent Skill. It bridges the gap between stock Chinese firmware and native Android AOSP push standards without root, without unlocking the bootloader, and without installing unauthorized third-party apps.

---

## 2. Product Objectives & Target Audience

### 2.1 Core Objectives
1. **Instant Notifications:** Guarantee native Phone/SMS-tier delivery speed for high-priority apps (Gmail, WhatsApp, Messenger, imo, Telegram, Instagram).
2. **Intelligent Battery Preservation:** Silence and restrict background bloatware, e-commerce syncs, heavy apps (bKash, Nagad, Othoba, Zoom, Wallpaper Carousel), and Google Play Store background auto-checks while maintaining 100% full speed when opened by the user.
3. **100% Reversibility & Zero-Risk:** Zero data loss, zero uninstalls of core frameworks, zero bricking risk. Every action can be rolled back in 1 click.
4. **Universal AI Agent Skill:** Any AI agent (Antigravity, Claude Code, Cursor) fed this repository can autonomously diagnose, explain, and execute remediations without distraction.

### 2.2 Target Devices & Supported Ecosystems
* **Xiaomi / Redmi / POCO:** HyperOS 1.0, 2.0, 3.0 (Android 14, 15, 16) & MIUI 12–14.
* **Vivo / iQOO:** OriginOS 3, 4, 5 & FuntouchOS (Android 13–16).
* **Oppo / Realme / OnePlus:** ColorOS 13, 14, 15 & RealmeUI.
* **Huawei / Honor:** HarmonyOS & MagicOS.

---

## 3. Functional Requirements

### 3.1 Device Connection & Pairing Engine
* **FR-1.1:** Support wireless pairing wizard (`adb pair`) via 6-digit Wi-Fi pairing code.
* **FR-1.2:** Auto-scan dynamic wireless ADB ports (`30000–49999`) across local subnets after phone reboots.
* **FR-1.3:** Support standard wired USB debugging (`adb devices`).

### 3.2 Diagnostic & Audit Engine
* **FR-2.1:** Detect device brand, model, SoC, ROM build, and Android API version.
* **FR-2.2:** Verify live Google FCM socket connectivity (`mtalk.google.com:5228`).
* **FR-2.3:** Inspect Android Doze whitelist, standby buckets, and vendor powerkeeper whitelists.
* **FR-2.4:** Quantify battery drainers by mAh, top CPU processes, and active wakelocks.

### 3.3 Notification Remediation Engine
* **FR-3.1:** Disable kernel Cgroup freezer (`cached_apps_freezer disabled`, `use_freezer false`).
* **FR-3.2:** Whitelist priority packages in Android Doze and promote to Standby Bucket 5 (`EXEMPTED`).
* **FR-3.3:** Enable unmetered background data via `netpolicy restrict-background-whitelist`.
* **FR-3.4:** Inject Xiaomi-specific AppOps: Autostart (`10008`), Secondary Autostart (`10021`), Heads-Up Float (`10017`), Lockscreen (`10020`), and Alert Sound (`10022`).
* **FR-3.5:** Inject packages into PowerKeeper system tables (`cloud_memory_freeze_whitelist`, `power_pkg_white_list`).

### 3.4 Battery Optimization Engine
* **FR-4.1:** Restrict heavy background apps (e-commerce, ride-sharing, banking, video conferencing) to Standby Bucket 45 (`RESTRICTED`).
* **FR-4.2:** Restrict Google Play Store (`com.android.vending`) background auto-checks and cancel queued background jobs while preserving 100% foreground speed.
* **FR-4.3:** Disable lockscreen Wallpaper Carousel / Glance (`com.mfashiongallery.emag`).
* **FR-4.4:** Optimize Google Chrome for deep sleep when screen is off without losing tabs or foreground speed.

### 3.5 Persistence & Self-Healing Watchdog
* **FR-5.1:** Lightweight, standalone shell daemon (`millet_watchdog.sh`) running under shell UID.
* **FR-5.2:** Periodically detects PowerKeeper resets and re-injects whitelists.
* **FR-5.3:** Pulses periodic FCM keepalive heartbeats (`MCS_HEARTBEAT`).

---

## 4. Non-Functional Requirements & Safety Boundaries

* **NFR-1 (Zero Privilege Escalation):** No `su`, Magisk, KernelSU, or root requirements.
* **NFR-2 (Zero Data Destruction):** No `factory_reset`, `format`, `wipe`, `pm clear`, or uninstalls of system apps.
* **NFR-3 (Strict Command Interception):** All shell commands must be vetted by `safety_guard.py` before execution.
* **NFR-4 (Idempotent Execution):** Scripts can be rerun multiple times safely without duplicate entries or state corruption.

