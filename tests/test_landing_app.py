import json, re, time, cv2, numpy as np
from playwright.sync_api import sync_playwright
import os
BASE=os.environ.get("BASE","http://localhost:8792/")
res=[]
def ok(name, cond, extra=""):
    res.append((name, bool(cond))); print(("PASS " if cond else "FAIL ")+name+(" — "+str(extra) if extra!="" else ""))
def decode(path):
    img=cv2.imread(path); d=cv2.QRCodeDetector(); val,_,_=d.detectAndDecode(img); return val
FAKE="https://example.com/german-daily/"
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- landing: QR / UA tabs ----------
    ctx=b.new_context(viewport={"width":1100,"height":900}, service_workers="block", accept_downloads=True)
    pg=ctx.new_page(); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(BASE+"index.html"); pg.wait_for_selector("#qr-canvas")
    ok("landing: desktop tab selected by default", pg.get_attribute("#t-desktop","aria-selected")=="true")
    pg.screenshot(path="/tmp/land_top.png")
    # default QR encodes the page URL
    pg.locator("#qr-canvas").screenshot(path="/tmp/qr_default.png")
    ok("QR (current URL) decodes", decode("/tmp/qr_default.png")==BASE+"index.html", decode("/tmp/qr_default.png"))
    pg.fill("#qr-url", FAKE)
    with pg.expect_download() as dl: pg.click("#qr-download")
    dl.value.save_as("/tmp/qr_dl.png")
    ok("downloaded QR PNG decodes to custom URL", decode("/tmp/qr_dl.png")==FAKE, decode("/tmp/qr_dl.png"))
    pg.fill("#qr-url","not a url"); ok("invalid URL disables download", pg.is_disabled("#qr-download"))
    pg.fill("#qr-url", "http://localhost:8792/"); ok("localhost shows warning", "فقط روی شبکهٔ خودتان" in pg.inner_text("#qr-note"))
    ok("landing: no console/page errors (CSP)", not errs, errs[:4])
    ctx.close()
    # iOS UA
    ctx=b.new_context(viewport={"width":390,"height":844}, service_workers="block", user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", has_touch=True, is_mobile=True)
    pg=ctx.new_page(); pg.goto(BASE+"index.html"); pg.wait_for_selector("#t-ios")
    ok("landing: iOS UA → iOS tab", pg.get_attribute("#t-ios","aria-selected")=="true" and not pg.is_visible("#p-android") and pg.is_visible("#p-ios"))
    ok("landing: iOS pill text", "Add to Home Screen" in pg.inner_text("#install-status"))
    pg.screenshot(path="/tmp/land_ios.png", full_page=True)
    ctx.close()
    ctx=b.new_context(viewport={"width":412,"height":860}, service_workers="block", user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36", has_touch=True, is_mobile=True)
    pg=ctx.new_page(); pg.goto(BASE+"index.html"); pg.wait_for_selector("#t-android")
    ok("landing: Android UA → Android tab", pg.get_attribute("#t-android","aria-selected")=="true")
    # simulate beforeinstallprompt → one-click button appears
    pg.evaluate("""()=>{const e=new Event('beforeinstallprompt'); e.prompt=()=>{window.__prompted=true}; e.userChoice=Promise.resolve({outcome:'accepted'}); window.dispatchEvent(e);}""")
    ok("landing: install button appears on beforeinstallprompt", pg.is_visible("#btn-install"))
    pg.click("#btn-install"); pg.wait_for_timeout(100)
    ok("landing: install button calls prompt()", pg.evaluate("window.__prompted===true"))
    ctx.close()
    # standalone redirect
    ctx=b.new_context(viewport={"width":412,"height":860}, service_workers="block")
    ctx.add_init_script("Object.defineProperty(window.navigator,'standalone',{get:()=>true})")
    pg=ctx.new_page(); pg.goto(BASE+"index.html"); pg.wait_for_url("**/app.html**", timeout=8000)
    ok("landing: standalone launch redirects to app.html", "/app.html" in pg.url, pg.url)
    ctx.close()
    # ---------- app regression ----------
    ctx=b.new_context(viewport={"width":412,"height":860}, service_workers="block", locale="fa-IR")
    def mock(route):
        from urllib.parse import unquote
        q=unquote(re.search(r"[?&]q=([^&]*)",route.request.url).group(1))
        route.fulfill(status=200, headers={"access-control-allow-origin":"*","content-type":"application/json"}, body=json.dumps([[["ترجمه: "+q,q]]],ensure_ascii=False))
    ctx.route("**/translate.googleapis.com/**", mock)
    pg=ctx.new_page(); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("dialog", lambda d: d.accept())
    pg.goto(BASE+"app.html"); pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
    ok("app: 2146 words, 227 verbs", pg.evaluate("[GD.state.words.length, GD.state.verbs.length]")==[2146,227], pg.evaluate("[GD.state.words.length, GD.state.verbs.length]"))
    chs=pg.evaluate("[...document.querySelectorAll('#filter-chapter option')].map(o=>o.value).filter(Boolean)")
    ok("app: new chapters present (Umwelt, Wirtschaft, Politik, Medien, Wissenschaft)", all(c in chs for c in ["Umwelt","Wirtschaft","Politik","Medien","Wissenschaft"]), chs)
    # B2 words with plural + example appear in a card
    html=pg.evaluate("GD.renderCard(GD.state.words.find(w=>w.g==='die Herausforderung'),true)")
    ok("card: plural + plural example", 'class="plural"' in html and "pl-ex" in html)
    # grammar B2 list + quiz
    pg.click('[data-tab="grammar"]')
    ok("grammar: B2 header + 16 items", pg.evaluate("[...document.querySelectorAll('#grammar-list h3')].map(h=>h.textContent).includes('B2') && document.querySelectorAll('#grammar-list [data-gram^=\"B2-\"]').length")==16)
    pg.click('[data-gram="B2-02"]')
    ok("grammar modal opens with quiz (3 questions)", pg.evaluate("document.querySelectorAll('#modal-body .quiz-q').length")==3)
    # click wrong then right
    q0=pg.locator("#modal-body .quiz-q").first
    opts=q0.locator(".quiz-opt"); ans=pg.evaluate("GD.state.grammar.find(g=>g.id==='B2-02').quiz[0].answer")
    wrong=(ans+1)%3
    opts.nth(wrong).click()
    ok("quiz: wrong marked bad, right marked ok, explanation shown", opts.nth(wrong).evaluate("e=>e.classList.contains('bad')") and opts.nth(ans).evaluate("e=>e.classList.contains('ok')") and "نادرست" in q0.locator(".quiz-exp").inner_text())
    pg.keyboard.press("Escape")
    ok("modal closes on Escape", pg.evaluate("document.getElementById('modal').classList.contains('hidden')"))
    # analyzer B2 detection
    TXT="Wenn ich mehr Zeit gehabt hätte, wäre ich gekommen. Er sagte, er sei krank gewesen. Entweder bleiben wir hier oder wir fahren weiter. Die Aufgabe muss bald gelöst werden. Er tut, als ob er nichts wüsste. Das Problem lässt sich leicht lösen. Ich freue mich darauf, dich zu sehen. Er wird den Termin vergessen haben. Das ist die Frau, mit der ich arbeite. Wir müssen eine Entscheidung treffen."
    ids=pg.evaluate("(t)=>GD.getAnalyzer().analyze(t,GD.state.grammar).grammar.map(g=>g.id).filter(i=>i.startsWith('B2'))", TXT)
    want={"B2-01","B2-02","B2-03","B2-08","B2-09","B2-10","B2-11","B2-12","B2-14","B2-15"}
    ok("analyzer detects B2 patterns", want<=set(ids), {"found":sorted(ids),"missing":sorted(want-set(ids))})
    # text tab end-to-end, translation mocked, tok click, link to grammar page
    pg.click('[data-tab="text"]'); pg.fill("#tr-input","Wenn ich Zeit gehabt hätte, wäre ich gekommen."); pg.click("#btn-tr-go")
    pg.wait_for_function("() => document.querySelector('#tr-status').textContent.includes('✅')")
    pg.click('#tr-out .grammar-item[data-gram="B2-02"]')
    ok("text tab: B2 grammar chip opens lesson page", "Konjunktiv II" in pg.inner_text("#modal-body") or pg.evaluate("document.getElementById('modal-title').textContent.length>0"))
    pg.keyboard.press("Escape")
    # leitner + wipe
    pg.evaluate("GD.leitnerAdd('die Umfrage')"); 
    ok("leitner stored", pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('gd_v3')).leitner||{}).length")>=1)
    pg.click('[data-tab="settings"]')
    ok("settings: install card present", pg.is_visible("#install-card") and len(pg.inner_text("#install-hint"))>10)
    ok("settings: version label", "۲۱۴۶" in pg.inner_text("#app-version"))
    pg.click("#btn-wipe"); pg.wait_for_load_state("load"); pg.wait_for_timeout(600); pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
    ok("wipe: localStorage gd_* cleared", pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('gd_')).length")<=1, pg.evaluate("Object.keys(localStorage)"))
    ok("app: no console/page errors (CSP etc.)", not errs, errs[:5])
    b.close()
print("\n%d/%d passed"%(sum(1 for _,c in res if c),len(res)))
