import subprocess

serial = '192.168.1.160:40495'
subprocess.run(['adb', 'connect', serial], capture_output=True, text=True)

res = subprocess.run(['adb', '-s', serial, 'logcat', '-d', '-T', '11-13 21:35:00.000'], capture_output=True, text=True)
print("=== AUDIO & NOTIFICATION EVENTS SINCE 21:35 ===")
for l in res.stdout.splitlines():
    if any(k in l for k in ['RingtonePlayer', 'buzzBeep', 'AudioTrack: start', 'MiuiBubble', 'enqueueNotification', 'Bubble']):
        print(l[:140])

