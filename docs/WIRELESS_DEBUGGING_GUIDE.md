# 📱 Super Simple Wireless Debugging & Pairing Guide

**Architect:** Mohammed Thuhidul Islam Shovo (shovo127)

No USB cable? No problem! You can fix all your notification issues completely over your Wi-Fi network in **under 30 seconds**.

---

## ⚡ 3-Step Quick Summary (The "Model - Port - Code" Flow)

```text
  ┌─────────────────────────┐     ┌────────────────────────┐     ┌───────────────────────┐
  │  1. Turn ON Wireless    │     │  2. Run 1 Command      │     │  3. Enter 3 Details   │
  │     Debugging on Phone  │ ──► │  python scripts/       │ ──► │     • IP & Port       │
  │     Tap "Pair with code"│     │  connect_phone.py      │     │     • 6-Digit Code    │
  │                         │     │                        │     │     • Done! Auto-Fix! │
  └─────────────────────────┘     └────────────────────────┘     └───────────────────────┘
```

---

## 🛠️ Detailed Step-by-Step Walkthrough

### Step 1: Open Developer Options on Your Phone
1. Go to **Settings** ➜ **About Phone**.
2. Tap **Build Number** (or **OS Version** on HyperOS/OriginOS) **7 times rapidly**.
3. You will see a popup: *"You are now a developer!"*.

---

### Step 2: Enable Wireless Debugging
1. Make sure your **phone and computer are connected to the SAME Wi-Fi**.
2. Go to **Settings** ➜ **System** (or **Additional Settings**) ➜ **Developer Options**.
3. Scroll down and toggle **ON** **Wireless Debugging**:
   - *On Xiaomi/POCO/Redmi:* Also toggle **ON** **"USB Debugging (Security settings)"**.
4. Now, tap directly on the words **"Wireless Debugging"** to enter its settings page.
5. Tap **"Pair device with pairing code"**.

A popup will immediately appear on your screen showing:
```text
┌───────────────────────────────────────────────┐
│ Pair with device                             │
│                                               │
│ Wi-Fi pairing code                            │
│ 8 4 9 2 0 1                                  │
│                                               │
│ IP address & Port                             │
│ 192.168.1.50:39481                           │
└───────────────────────────────────────────────┘
```

---

### Step 3: Run the 1-Click Wizard on Your Computer

Open your terminal or double-click `scripts/NotiFixer_OneClick.bat` and select `[1]`, or run:

```bash
python scripts/connect_phone.py
```

The script will ask you for 3 simple things:
1. **IP & Pairing Port:** Enter `192.168.1.50:39481` (from your phone popup).
2. **6-Digit Pairing Code:** Enter `123456` (from your phone popup).
3. **Connect Port:** Close the popup on your phone, glance at the main Wireless Debugging screen, and press **Enter**!

---

### Step 4: Automated Detection & Instant Fix!

The wizard will instantly print:
```text
========================================================================
   PHONE CONNECTED SUCCESSFULLY!
========================================================================
 Model       : XIAOMI 14 PRO (HyperOS 2.0)
 Android OS  : Android 15
========================================================================

👉 Do you want to apply the Notification Fix now? [Y/n]: Y
```

Type `Y` and press **Enter**.
Noti-Fixer will automatically:
- Whitelist all messaging apps (WhatsApp, Telegram, Gmail, etc.) in Android Doze.
- Disable the kernel cgroup freezer so Google FCM sockets never sleep.
- Inject Xiaomi MILLET keys or Vivo/Oppo battery exemptions.
- Verify that your FCM socket (`mtalk.google.com:5228`) is **100% LIVE**.

🎉 **You are DONE! Notifications and calls will now arrive instantly 24/7 without delays!**

---

## 🔄 What If Your Phone Reboots Later?

Whenever an Android phone reboots, it automatically assigns a new random wireless port (e.g., changes from `39481` to `42819`). 

You do **NOT** need to re-pair! Just run:
```bash
python scripts/scan_ports.py -ip 192.168.1.50
```
It will scan the open ports on your phone and re-establish the connection in 2 seconds automatically.

