import json, re, time
from playwright.sync_api import sync_playwright
import os
BASE=os.environ.get("BASE","http://localhost:8792/")
res=[]
def ok(name, cond, extra=""):
    res.append((name, bool(cond))); print(("PASS " if cond else "FAIL ")+name+(" — "+str(extra) if extra!="" else ""))
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":412,"height":860}, service_workers="allow", locale="fa-IR")
    pg=ctx.new_page()
    errs=[]
    pg.on("pageerror", lambda e: errs.append("pageerror:"+str(e)))
    pg.on("console", lambda m: errs.append("console:"+m.text) if m.type in("error",) else None)
    # ---------- A: manifest + installability ----------
    pg.goto(BASE+"index.html")
    cdp=ctx.new_cdp_session(pg)
    man=cdp.send("Page.getAppManifest")
    ok("manifest has no parse errors", not man.get("errors"), man.get("errors"))
    data=json.loads(man["data"]) if man.get("data") else {}
    ok("manifest start_url/scope", data.get("start_url","").endswith("app.html?source=pwa"), data.get("start_url"))
    ok("manifest icons incl. maskable 512 + any 512", {(i["sizes"],i.get("purpose")) for i in data["icons"]} >= {("512x512","maskable"),("512x512","any")})
    inst=cdp.send("Page.getInstallabilityErrors")
    ok("installability errors empty", inst.get("installabilityErrors")==[] , inst.get("installabilityErrors"))
    # ---------- B: service worker ----------
    pg.wait_for_function("navigator.serviceWorker.ready.then(r=>!!r.active)", timeout=20000)
    keys=pg.evaluate("caches.keys()")
    ok("static cache created", any(k.startswith("gd-static-") for k in keys), keys)
    sk=[k for k in keys if k.startswith("gd-static-")][0]
    cached=pg.evaluate("(k)=>caches.open(k).then(c=>c.keys()).then(r=>r.map(x=>new URL(x.url).pathname))", sk)
    need=["/","/index.html","/app.html","/manifest.webmanifest","/words.min.json","/grammar.json","/icons/icon-192.png","/icons/icon-512.png","/icons/maskable-512.png","/icons/apple-touch-icon.png","/icons/favicon.ico"]
    ok("precache has all required files", all(n in cached for n in need), [n for n in need if n not in cached])
    pg.reload(); pg.wait_for_load_state("load")
    ok("page controlled by SW after reload", pg.evaluate("!!navigator.serviceWorker.controller"))
    ctx.set_offline(True)
    pg.goto(BASE+"app.html"); pg.wait_for_function("window.GD && GD.state.words.length>1000", timeout=15000)
    ok("OFFLINE: app loads 2146 words", pg.evaluate("GD.state.words.length")==2146, pg.evaluate("GD.state.words.length"))
    ok("OFFLINE: grammar has 49 lessons / 16 B2", pg.evaluate("[GD.state.grammar.length, GD.state.grammar.filter(g=>g.level==='B2').length]")==[49,16])
    pg.goto(BASE+"index.html"); pg.wait_for_selector("#qr-canvas")
    ok("OFFLINE: landing page loads", pg.title().startswith("German Daily"))
    pg.goto(BASE+"app.html?tab=leitner&source=shortcut"); pg.wait_for_function("window.GD && GD.state.words.length>1000")
    ok("OFFLINE: ?tab=leitner opens Leitner tab", pg.evaluate("!document.getElementById('tab-leitner').classList.contains('hidden')"))
    ok("OFFLINE: icons served from cache", pg.evaluate("fetch('icons/icon-192.png').then(r=>r.ok)"))
    ctx.set_offline(False)
    ok("no console/page errors (incl. CSP)", not errs, errs[:5])
    b.close()
print("\n%d/%d passed"%(sum(1 for _,c in res if c),len(res)))
