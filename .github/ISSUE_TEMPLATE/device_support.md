---
name: Device Compatibility Request
about: Report a new tested device or request support for an unlisted ROM
title: '[DEVICE] Support Request: <Brand> <Model>'
labels: ['device-support', 'enhancement']
assignees: 'shovo127'
---

### Device Profile
- **Manufacturer / Brand:** (e.g. Meizu, Honor, ZTE Nubia, Xiaomi)
- **Model Name:** (e.g. Nubia Z60 Ultra, Meizu 21 Pro)
- **Stock ROM Name & Build ID:** (e.g. MyOS 14, Flyme 10.5)
- **Android Version:** (e.g. Android 14)

### Fingerprint Output
Please run:
```bash
python scripts/detect_device.py --json
```
And paste the JSON block below:

```json
{
  "paste": "json here"
}
```

### Observed Notification Behavior
- Are notifications delayed with screen off? (Yes / No)
- Does Google Play Services drop FCM socket `5228`? (Yes / No)
- Any vendor battery saver messages?
