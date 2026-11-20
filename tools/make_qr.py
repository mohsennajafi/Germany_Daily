#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ساخت QR Code (PNG و SVG) برای آدرس نهایی برنامه — بدون نیاز به مرورگر.
اجرا:   python3 tools/make_qr.py https://YOUR-DOMAIN/german-daily/
خروجی:  qr/german-daily-qr.png  و  qr/german-daily-qr.svg   (برای چاپ روی پوستر/کارت)
نیازمند:  pip install segno
(صفحهٔ index.html هم همین QR را در مرورگر می‌سازد؛ این اسکریپت برای چاپ آفلاین است.)"""
import sys
from pathlib import Path
try:
    import segno
except ImportError:
    sys.exit("ابتدا نصب کنید:  pip install segno")
if len(sys.argv) != 2 or not sys.argv[1].startswith(("http://", "https://")):
    sys.exit("استفاده:  python3 tools/make_qr.py https://YOUR-DOMAIN/german-daily/")
url = sys.argv[1]
out = Path(__file__).resolve().parent.parent / "qr"; out.mkdir(exist_ok=True)
qr = segno.make(url, error="m")
qr.save(out / "german-daily-qr.png", scale=16, border=4, dark="#0f172a", light="#ffffff")
qr.save(out / "german-daily-qr.svg", scale=8, border=4, dark="#0f172a", light="#ffffff")
print("ساخته شد:", out / "german-daily-qr.png", "و", out / "german-daily-qr.svg", "→", url)
