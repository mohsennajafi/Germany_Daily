# German Daily — یادگیری روزانهٔ آلمانی (PWA)

برنامهٔ وب پیش‌رونده (PWA) برای یادگیری آلمانی به فارسی: **۲۱۴۶ واژه**، **۴۹ درس گرامر (A1 تا B2)**، لایتنر، مترجم و تحلیلگر متن، و کار کامل آفلاین.
روی اندروید، iOS و کامپیوتر نصب می‌شود؛ حساب کاربری ندارد و داده‌ها فقط روی دستگاه کاربر می‌مانند.

- نویسنده: **Mohsen Najafi** — mohsen.najafi.najafi@gmail.com — 00989177662400

## امکانات
| | |
|---|---|
| واژهٔ روزانه | تلفظ (IPA)، معنی، جمع اسم + جملهٔ مثال جمع، جملهٔ مثال آلمانی/فارسی |
| افعال | ۲۲۷ فعل با صرف کامل (Präsens … Konjunktiv) |
| گرامر | ۴۹ درس A1–B2 به فارسی با مثال و **آزمون کوتاه** (۳ سؤال) |
| لایتنر | ۵ جعبه (۱، ۲، ۴، ۸، ۱۶ روز)، مرور روزانه با مثال |
| متن | ترجمه (Google/MyMemory/AI/مترجم مرورگر) + هایلایت فعل، جمع اسم و گرامر (تا B2) با لینک به درس |
| آفلاین | پیش‌کش کامل با Service Worker؛ کش ترجمه‌ها؛ معنی کلمه‌به‌کلمه وقتی ترجمه ممکن نیست |
| نصب | صفحهٔ معرفی + راهنمای نصب + QR Code؛ دکمهٔ نصب داخل برنامه |

## ساختار پروژه
```
index.html              صفحهٔ معرفی، راهنمای نصب، QR (ساخته‌شده از tools/landing.template.html)
app.html                خود برنامه (HTML + CSS + JS یکپارچه)
sw.js                   Service Worker (پیش‌کش، به‌روزرسانی با تأیید کاربر، کش ترجمه)
manifest.webmanifest    تنظیمات PWA (آیکن‌ها، اسکرین‌شات‌ها، میان‌بُرها)
words.min.json / .csv   واژگان (۲۱۴۶)
grammar.json            درس‌های گرامر (A1–B2) + آزمون
icons/                  آیکن‌ها: Android (192/512 + maskable)، iOS (apple-touch-icon)، favicon
screenshots/            اسکرین‌شات‌های manifest و صفحهٔ معرفی
tools/                  ابزارهای ساخت (آیکن، اسکرین‌شات، QR، هش نسخهٔ SW، ساخت index.html)
tests/                  تست‌های Playwright
_headers                هدرهای امنیتی/کش برای Netlify و Cloudflare Pages
DEPLOY.md               راهنمای انتشار
docs/INSTALL-GUIDE.md   راهنمای نصب برای کاربران
```

## اجرای محلی
```bash
python3 -m http.server 8080      # سپس http://localhost:8080
```
(Service Worker فقط روی `https://` یا `localhost` کار می‌کند.)

## ساخت دوبارهٔ فایل‌ها
```bash
python3 tools/gen_icons.py          # آیکن‌ها (نیازمند playwright + pillow)
python3 tools/make_screenshots.py   # اسکرین‌شات‌ها
python3 tools/build_landing.py      # index.html از قالب + کتابخانهٔ QR
python3 tools/stamp_sw.py           # نسخهٔ SW از هش فایل‌ها — قبل از هر انتشار
python3 tools/make_qr.py https://YOUR-DOMAIN/german-daily/   # QR چاپی (PNG/SVG)
```

## حریم خصوصی
پیشرفت، لایتنر، واژه‌های شخصی و کلید API (اختیاری) فقط در `localStorage` همین دستگاه ذخیره می‌شوند. «حذف همهٔ داده‌ها» در تنظیمات همه را پاک می‌کند.
ترجمهٔ متن، جمله‌ها را برای Google Translate یا MyMemory می‌فرستد؛ تحلیل (فعل/گرامر) کاملاً محلی است.

## مجوز
هنوز مجوزی انتخاب نشده است (همهٔ حقوق برای نویسنده). پیش از انتشار عمومی، فایل `LICENSE` مناسب (مثلاً MIT) را اضافه کنید.
کتابخانهٔ `vendor/qrcode.min.js` تحت مجوز MIT است (qrcode-generator، Kazuhiko Arase).
