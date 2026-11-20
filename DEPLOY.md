# راهنمای انتشار عمومی

نیازمندی‌ها: یک میزبان **HTTPS** برای فایل‌های ایستا (PWA/Service Worker فقط روی HTTPS کار می‌کند). همهٔ مسیرها نسبی‌اند؛ پس هم در ریشهٔ دامنه و هم در زیرمسیر (مثل `/german-daily/`) کار می‌کند.

## چک‌لیست پیش از انتشار
1. `python3 tools/build_landing.py` (در صورت تغییر قالب صفحهٔ معرفی)
2. `python3 tools/stamp_sw.py` — **حتماً**؛ نسخهٔ SW را با هش فایل‌ها عوض می‌کند تا کاربران قدیمی پیام «نسخهٔ جدید» بگیرند.
3. سرور محلی را اجرا و تست‌ها را بزنید: `python3 tests/test_pwa_offline.py && python3 tests/test_landing_app.py`
4. commit و tag: `git add -A && git commit -m "release" && git tag v5.x.y`

## روش ۱ — GitHub Pages (رایگان)
1. یک مخزن بسازید و محتوای این پوشه را در ریشهٔ شاخهٔ `main` بگذارید.
2. Settings ← Pages ← Source: `Deploy from a branch` ← Branch: `main` / `(root)`.
3. بعد از ۱–۲ دقیقه آدرس: `https://USERNAME.github.io/REPO/`
   (فایل `.nojekyll` از پردازش Jekyll جلوگیری می‌کند. GitHub Pages هدر سفارشی نمی‌پذیرد؛ CSP داخل `<meta>` صفحه‌ها قرار دارد.)

## روش ۲ — Netlify (کشیدن‌ورها)
1. در app.netlify.com ← Add new site ← Deploy manually ← پوشهٔ پروژه را بکشید و رها کنید.
2. فایل `_headers` خودکار اعمال می‌شود (هدرهای امنیتی و `no-cache` برای `sw.js`).

## روش ۳ — Cloudflare Pages
Workers & Pages ← Create ← Pages ← Upload assets ← پوشه را آپلود کنید (`_headers` هم پشتیبانی می‌شود).

## بعد از انتشار
1. آدرس نهایی را باز کنید ← صفحهٔ معرفی ← بخش QR ← آدرس را بررسی و **QR را دانلود** کنید (یا `python3 tools/make_qr.py URL` برای چاپ).
2. روی اندروید (Chrome) و iPhone (Safari) واقعاً نصب کنید و حالت هواپیما را امتحان کنید.
3. اختیاری: `https://web.dev/measure` یا Lighthouse برای امتیاز PWA/Accessibility.

## انتشار نسخهٔ جدید (به‌روزرسانی)
فایل‌ها را تغییر دهید ← `python3 tools/stamp_sw.py` ← آپلود. مرورگر کاربران ظرف چند ساعت (یا با بازکردن برنامه) نسخهٔ جدید را می‌گیرد و پیام «به‌روزرسانی» نشان می‌دهد؛ داده‌های کاربر حفظ می‌شود.

## نکات
- **iOS**: نصب فقط از مسیر Share ← Add to Home Screen است؛ پشتیبانی کامل از iOS 16.4+.
- **اندروید**: برای کارت نصب غنی، اسکرین‌شات‌های manifest (موجود) لازم‌اند.
- **ایران/کشورهای فیلترشده**: اگر Google Translate در دسترس نباشد، برنامه خودکار MyMemory و سپس AI (در صورت وجود کلید) را امتحان می‌کند.
- اگر دامنهٔ دیگری با `Content-Security-Policy` سخت‌گیرانه‌تر دارید، `connect-src https:` لازم است (برای API هوش مصنوعی با آدرس دلخواه).
