# شبیه‌سازی به‌روزرسانی Service Worker:
#   rm -rf /tmp/site2 && cp -r <project> /tmp/site2
#   (cd /tmp/site2 && python3 -m http.server 8793 &)   سپس این فایل را اجرا کنید.
import re, time
from playwright.sync_api import sync_playwright
BASE="http://localhost:8793/"
def ok(n,c,e=""): print(("PASS " if c else "FAIL ")+n+(" — "+str(e) if e!="" else ""))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(service_workers="allow", viewport={"width":412,"height":860}); pg=ctx.new_page()
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE+"app.html"); pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
    pg.wait_for_function("() => navigator.serviceWorker.ready.then(r=>!!r.active)")
    v1=pg.evaluate("caches.keys()"); ok("v1 cache present", any(k.startswith("gd-static-5.") for k in v1), v1)
    pg.reload(); pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
    pg.evaluate("GD.leitnerAdd('die Umfrage')"); 
    # ---- publish "new version": change VERSION in sw.js on the server ----
    sw=open("/tmp/site2/sw.js",encoding="utf-8").read()
    sw2=re.sub(r'const VERSION = "[^"]*";','const VERSION = "5.TESTNEW";',sw,count=1); open("/tmp/site2/sw.js","w",encoding="utf-8").write(sw2)
    pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())")
    pg.wait_for_selector("#toast", timeout=15000)
    ok("update toast appears", "نسخهٔ جدید" in pg.inner_text("#toast"), pg.inner_text("#toast"))
    ok("old SW still controlling (no forced reload)", pg.evaluate("!!navigator.serviceWorker.controller"))
    with pg.expect_navigation(timeout=15000):
        pg.click("#toast .btn")
    pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
    pg.wait_for_function("() => caches.keys().then(k=>k.some(x=>x==='gd-static-5.TESTNEW'))")
    keys=pg.evaluate("caches.keys()")
    ok("new cache active, old static cache deleted", "gd-static-5.TESTNEW" in keys and sum(k.startswith("gd-static-") for k in keys)==1, keys)
    ok("user data preserved after update", pg.evaluate("!!(JSON.parse(localStorage.getItem('gd_v3')).leitner||{})['die Umfrage']"))
    ok("no page errors", not errs, errs)
    b.close()
