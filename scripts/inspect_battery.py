import subprocess
import re

adb = r"C:\Users\SHOVO.DESKTOP-GA0MH8U\AppData\Local\Android\Sdk\platform-tools\adb.exe"
device = "192.168.1.160:42109"

subprocess.run([adb, "connect", device], capture_output=True)

res = subprocess.run([adb, "-s", device, "shell", "pm list packages -U"], capture_output=True, text=True)
uid_map = {}
for line in res.stdout.splitlines():
    if "package:" in line and "uid:" in line:
        parts = line.split()
        pkg = parts[0].replace("package:", "").strip()
        uid = parts[1].replace("uid:", "").strip()
        uid_map[uid] = pkg

uids = [
    ("1000", "System / MIUI Services", 262.0),
    ("10336", uid_map.get("10336", "Unknown"), 107.0),
    ("10332", uid_map.get("10332", "Unknown"), 75.8),
    ("10126", uid_map.get("10126", "Unknown"), 43.6),
    ("10352", uid_map.get("10352", "Unknown"), 26.9),
    ("10140", uid_map.get("10140", "Unknown"), 25.0),
    ("10139", uid_map.get("10139", "Unknown"), 23.8),
    ("1051", uid_map.get("1051", "Unknown"), 20.2),
    ("10294", uid_map.get("10294", "Unknown"), 19.3),
    ("10283", uid_map.get("10283", "Unknown"), 15.5),
    ("10180", uid_map.get("10180", "Unknown"), 14.5),
    ("10297", uid_map.get("10297", "Unknown"), 13.9),
    ("10330", uid_map.get("10330", "Unknown"), 13.4),
    ("10307", uid_map.get("10307", "Unknown"), 8.11),
    ("10123", uid_map.get("10123", "Unknown"), 7.59),
    ("10339", uid_map.get("10339", "Unknown"), 5.25),
    ("10342", uid_map.get("10342", "Unknown"), 4.78),
    ("10122", uid_map.get("10122", "Unknown"), 4.76),
    ("10204", uid_map.get("10204", "Unknown"), 4.52),
    ("10291", uid_map.get("10291", "Unknown"), 3.76)
]

print("=== ACCURATE BATTERY DRAINERS IDENTIFIED ===")
for uid, name, mah in uids:
    print(f"UID {uid:<6} | {mah:6.2f} mAh | {name}")
