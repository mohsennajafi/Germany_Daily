#!/usr/bin/env python3
"""ساخت index.html (صفحهٔ معرفی) از tools/landing.template.html + vendor/qrcode.min.js"""
from pathlib import Path
R = Path(__file__).resolve().parent.parent
t = (R / "tools/landing.template.html").read_text(encoding="utf-8")
q = (R / "vendor/qrcode.min.js").read_text(encoding="utf-8")
assert "/*QRLIB*/" in t
(R / "index.html").write_text(t.replace("/*QRLIB*/", q), encoding="utf-8")
print("index.html written", (R / "index.html").stat().st_size, "bytes")
