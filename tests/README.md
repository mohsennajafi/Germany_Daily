# تست‌ها

همه با Playwright (Chromium) اجرا می‌شوند:

```bash
pip install playwright opencv-python-headless && playwright install chromium
python3 -m http.server 8792          # در ریشهٔ پروژه، در یک ترمینال جدا
python3 tests/test_pwa_offline.py    # manifest، قابلیت نصب، پیش‌کش SW، بارگذاری آفلاین
python3 tests/test_landing_app.py    # صفحهٔ معرفی، QR (رمزگشایی)، گرامر B2، آزمون، تحلیل متن، حذف داده‌ها
python3 tests/test_overflow.py       # نبود اسکرول افقی در عرض‌های 320 تا 1440
```

- `test_a11y_axe.py`: بررسی دسترس‌پذیری با axe-core (`npm i axe-core` و ویرایش مسیر `AX` در بالای فایل).
- `test_update_flow.py`: شبیه‌سازی انتشار نسخهٔ جدید (نیازمند کپی سایت در `/tmp/site2` و سرور روی پورت 8793؛ توضیح در بالای فایل).
- آدرس دیگر: `BASE=https://your-domain/german-daily/ python3 tests/test_pwa_offline.py`
