/**
 * German Daily – Service Worker (کار آفلاین)
 * ------------------------------------------------------------
 * تماس با توسعه‌دهنده / Contact
 *   ایمیل : mohsen.najafi.najafi@gmail.com
 *   تلفن  : 00989177662400
 * ------------------------------------------------------------
 * استراتژی: «کش اول، همزمان به‌روزرسانی از شبکه» (stale-while-revalidate)
 * برای فایل‌های برنامه؛ و «شبکه اول، کش پشتیبان» برای بقیه درخواست‌ها.
 */

// با هر تغییر در فایل‌ها، شماره نسخه را زیاد کنید تا کش قدیمی پاک شود
const CACHE = "gd-v8";

// کش جداگانهٔ ترجمه‌ها (کش مرورگر): پاسخ سرویس‌های ترجمه اینجا ذخیره می‌شود تا بدون اینترنت هم در دسترس باشد
const TR_CACHE = "gd-translate-v1";
const TR_HOSTS = ["translate.googleapis.com", "api.mymemory.translated.net"];
const TR_MAX = 500;

// فایل‌هایی که هنگام نصب کش می‌شوند
const ASSETS = ["./", "./index.html", "./words.min.json", "./grammar.json", "./manifest.json", "./icon.svg"];

// نصب: کش‌کردن فایل‌ها
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

// فعال‌سازی: حذف کش‌های قدیمی
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== TR_CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// آیا این درخواست جزو فایل‌های خود برنامه است؟
function isAppAsset(url) {
  return /\/(index\.html|words\.min\.json|grammar\.json|manifest\.json|icon\.svg)$/.test(url) || url.endsWith("/");
}

// نگه‌داشتن حداکثر TR_MAX پاسخ ترجمه (قدیمی‌ترین‌ها حذف می‌شوند)
async function trimTranslateCache() {
  const c = await caches.open(TR_CACHE), keys = await c.keys();
  for (let i = 0; i < keys.length - TR_MAX; i++) await c.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const url = e.request.url;

  // درخواست‌های ترجمه: اول شبکه؛ موفق بود در کش ذخیره کن، نشد (آفلاین) از کش بخوان
  if (e.request.method === "GET" && TR_HOSTS.some(h => url.includes(h))) {
    e.respondWith(
      fetch(e.request).then(res => {
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(TR_CACHE).then(c => c.put(e.request, clone)).then(trimTranslateCache).catch(() => {});
        }
        return res;
      }).catch(() => caches.match(e.request, { cacheName: TR_CACHE })
        .then(r => r || new Response("{}", { status: 503, statusText: "offline" })))
    );
    return;
  }

  // فایل‌های برنامه: اگر در کش بود همان را بده و همزمان نسخه جدید را بگیر
  if (isAppAsset(url)) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetched = fetch(e.request).then(res => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
          return res;
        }).catch(() => cached);
        return cached || fetched;
      })
    );
    return;
  }

  // بقیه (مثلاً درخواست‌های API): اول شبکه، در صورت خطا کش
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
