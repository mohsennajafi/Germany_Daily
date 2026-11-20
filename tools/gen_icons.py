#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ساخت همهٔ آیکن‌ها (SVG + PNG برای Android/iOS/مرورگر + favicon.ico).
اجرا:  python3 tools/gen_icons.py      (نیازمند: pip install playwright pillow ؛ playwright install chromium)
"""
import os, sys, io
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"; OUT.mkdir(exist_ok=True)

def svg(mode):
    """mode: any (گوشهٔ گرد، شفاف) | full (مربع کامل؛ iOS) | maskable (مربع کامل + محتوای کوچک‌تر در ناحیهٔ امن)"""
    rx = 112 if mode == "any" else 0
    k = 0.78 if mode == "maskable" else 1.0
    t = 256 * (1 - k)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e3a8a"/><stop offset="1" stop-color="#3b82f6"/></linearGradient>
  <clipPath id="bub"><path d="M152 118h208a56 56 0 0 1 56 56v118a56 56 0 0 1-56 56H258l-86 62v-62h-20a56 56 0 0 1-56-56V174a56 56 0 0 1 56-56z"/></clipPath>
</defs>
<rect width="512" height="512" rx="{rx}" fill="url(#bg)"/>
<g transform="translate({t:.1f} {t:.1f}) scale({k})">
  <path d="M152 118h208a56 56 0 0 1 56 56v118a56 56 0 0 1-56 56H258l-86 62v-62h-20a56 56 0 0 1-56-56V174a56 56 0 0 1 56-56z" fill="#fff"/>
  <g clip-path="url(#bub)">
    <rect x="0" y="296" width="512" height="18" fill="#111827"/>
    <rect x="0" y="314" width="512" height="18" fill="#dd0000"/>
    <rect x="0" y="332" width="512" height="20" fill="#ffce00"/>
  </g>
  <g fill="none" stroke="#1e3a8a" stroke-width="26" stroke-linecap="round" stroke-linejoin="round">
    <path d="M150 168V268H186Q238 268 238 218Q238 168 186 168Z"/>
    <path d="M358 168H282V268H358M282 218H346"/>
  </g>
</g>
</svg>'''

def main():
    (OUT / "icon.svg").write_text(svg("any"), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    from PIL import Image
    jobs = [("icon-192.png", "any", 192), ("icon-512.png", "any", 512),
            ("maskable-192.png", "maskable", 192), ("maskable-512.png", "maskable", 512),
            ("apple-touch-icon.png", "full", 180), ("favicon-32.png", "any", 32), ("favicon-16.png", "any", 16),
            ("icon-1024.png", "any", 1024)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, mode, size in jobs:
            pg = b.new_page(viewport={"width": size, "height": size})
            pg.set_content(f'<html><body style="margin:0;background:transparent">{svg(mode).replace(chr(10), "").replace("width=\"512\" height=\"512\">", f"width=\"{size}\" height=\"{size}\">", 1)}</body></html>')
            pg.screenshot(path=str(OUT / name), omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})
            pg.close()
        b.close()
    # favicon.ico (16/32/48) از نسخهٔ بزرگ
    big = Image.open(OUT / "icon-512.png").convert("RGBA")
    big.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # آیکن iOS باید مات (بدون شفافیت) باشد
    a = Image.open(OUT / "apple-touch-icon.png").convert("RGBA")
    bgc = Image.new("RGB", a.size, (30, 58, 138)); bgc.paste(a, mask=a.split()[3]); bgc.save(OUT / "apple-touch-icon.png")
    print("icons:", sorted(x.name for x in OUT.iterdir()))

if __name__ == "__main__":
    main()
