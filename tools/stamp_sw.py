#!/usr/bin/env python3
"""نسخهٔ Service Worker را از روی هش محتوای فایل‌های برنامه می‌سازد.
هر بار قبل از انتشار اجرا کنید:  python3 tools/stamp_sw.py
(اگر هیچ فایلی عوض نشده باشد، نسخه تغییر نمی‌کند و کاربران بی‌دلیل به‌روزرسانی نمی‌شوند.)"""
import hashlib, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
sw = (R / "sw.js").read_text(encoding="utf-8")
files = re.findall(r'"\./([^"]+)"', re.search(r"const PRECACHE = \[(.*?)\];", sw, re.S).group(1))
h = hashlib.sha256()
for f in sorted(set(files)):
    p = R / f
    if p.is_file(): h.update(f.encode()); h.update(p.read_bytes())
ver = "5." + h.hexdigest()[:10]
sw2 = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{ver}";', sw, count=1)
(R / "sw.js").write_text(sw2, encoding="utf-8")
print("SW VERSION =", ver, f"({len(files)} files)")
