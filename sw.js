/* German Daily – Service Worker
 * Mohsen Najafi · mohsen.najafi.najafi@gmail.com
 *
 * - پیش‌کش (precache) همهٔ فایل‌های برنامه → کار کامل آفلاین
 * - نسخهٔ جدید فقط بعد از تأیید کاربر (پیام SKIP_WAITING) فعال می‌شود
 * - پاسخ سرویس‌های ترجمه (GET) در کش جداگانه ذخیره می‌شود تا بدون اینترنت هم در دسترس باشد
 * - VERSION را با `python3 tools/stamp_sw.py` به‌طور خودکار (هش فایل‌ها) به‌روز کنید
 */
const VERSION = "5.374b763b4b";          // ← توسط tools/stamp_sw.py جایگزین می‌شود
const CACHE = "gd-static-" + VERSION;
const TR_CACHE = "gd-translate-v1";
const TR_HOSTS = ["translate.googleapis.com", "api.mymemory.translated.net"];
const TR_MAX = 500;

const PRECACHE = [
  "./", "./index.html", "./app.html", "./manifest.webmanifest",
  "./words.min.json", "./grammar.json",
  "./icons/icon.svg", "./icons/icon-192.png", "./icons/icon-512.png",
  "./icons/maskable-192.png", "./icons/maskable-512.png",
  "./icons/apple-touch-icon.png", "./icons/favicon-32.png", "./icons/favicon.ico",
  "./screenshots/home-narrow.png", "./screenshots/leitner-narrow.png",
  "./screenshots/text-narrow.png", "./screenshots/grammar-narrow.png"
];

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // cache:"reload" → همیشه از شبکه (نه از کش HTTP مرورگر) تا نسخهٔ قدیمی ذخیره نشود
    await Promise.all(PRECACHE.map(async url => {
      const res = await fetch(new Request(url, { cache: "reload" }));
      if (!res.ok) throw new Error("precache failed: " + url + " " + res.status);
      await cache.put(url, res);
    }));
    // نکته: skipWaiting() صدا زده نمی‌شود؛ نسخهٔ جدید منتظر تأیید کاربر می‌ماند
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.startsWith("gd-") && k !== CACHE && k !== TR_CACHE).map(k => caches.delete(k)));
    // کش‌های قدیمی نسخه‌های قبل (gd-v7 و …)
    await Promise.all(keys.filter(k => /^gd-v\d+$/.test(k)).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("message", event => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

async function trimTranslateCache() {
  const c = await caches.open(TR_CACHE), keys = await c.keys();
  for (let i = 0; i < keys.length - TR_MAX; i++) await c.delete(keys[i]);
}

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // ---- سرویس‌های ترجمه: اول شبکه (و ذخیره)، بعد کش ----
  if (TR_HOSTS.includes(url.hostname)) {
    event.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(TR_CACHE).then(c => c.put(req, clone)).then(trimTranslateCache).catch(() => {});
        }
        return res;
      } catch (_) {
        const hit = await caches.match(req, { cacheName: TR_CACHE });
        return hit || new Response("{}", { status: 503, statusText: "offline" });
      }
    })());
    return;
  }

  // ---- سایر درخواست‌های بین‌دامنه‌ای (API هوش مصنوعی و …): دست نزن ----
  if (url.origin !== self.location.origin) return;

  // ---- صفحه‌ها (navigate): اول کش (هم‌نسخه با داده‌ها)؛ اگر نبود شبکه ----
  // نسخهٔ جدید از مسیر به‌روزرسانی SW (با تأیید کاربر) می‌رسد تا HTML و داده همیشه هم‌نسخه بمانند.
  if (req.mode === "navigate") {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const hit = await cache.match(req, { ignoreSearch: true });
      if (hit) return hit;
      try { return await fetch(req); }
      catch (_) {
        const isApp = url.pathname.endsWith("/app.html");
        return (await cache.match(isApp ? "./app.html" : "./index.html")) || Response.error();
      }
    })());
    return;
  }

  // ---- فایل‌های ایستا: اول کش (نسخه‌بندی‌شده)، بعد شبکه + ذخیره ----
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req, { ignoreSearch: true });
    if (hit) return hit;
    try {
      const res = await fetch(req);
      if (res && res.ok && res.type === "basic") cache.put(req, res.clone()).catch(() => {});
      return res;
    } catch (_) {
      return Response.error();
    }
  })());
});
