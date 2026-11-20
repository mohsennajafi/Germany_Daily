#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ساخت اسکرین‌شات‌های manifest و صفحهٔ معرفی (screenshots/*.png).
اجرا:  python3 tools/make_screenshots.py     (نیازمند playwright + chromium)"""
import json, subprocess, sys, time, re
from pathlib import Path
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"; OUT.mkdir(exist_ok=True)
PORT = 8791
TEXT = "Ich habe gestern meine Kollegen besucht, weil ich Zeit hatte. Wir stehen jeden Morgen um sechs Uhr auf."
FA = {"Ich habe gestern meine Kollegen besucht, weil ich Zeit hatte.": "دیروز همکارانم را ملاقات کردم، چون وقت داشتم.",
      "Wir stehen jeden Morgen um sechs Uhr auf.": "ما هر صبح ساعت شش بیدار می‌شویم."}

def mock(route):
    from urllib.parse import unquote
    q = unquote(re.search(r"[?&]q=([^&]*)", route.request.url).group(1))
    route.fulfill(status=200, headers={"access-control-allow-origin": "*", "content-type": "application/json"},
                  body=json.dumps([[[FA.get(q, q), q]]], ensure_ascii=False))

def main():
    from playwright.sync_api import sync_playwright
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--directory", str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            ctx = b.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=3, locale="fa-IR", service_workers="block", bypass_csp=True)
            ctx.route("**/translate.googleapis.com/**", mock)
            pg = ctx.new_page()
            pg.goto(f"http://localhost:{PORT}/app.html")
            pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
            pg.evaluate("""()=>{const w=GD.state.words.find(x=>x.g==='die Herausforderung'); GD.state.dailyList=[w]; GD.state.dailyIndex=0; GD.showDailyCard();}""")
            pg.screenshot(path=str(OUT / "home-narrow.png"))
            pg.evaluate("""()=>{const L=GD.state.settings.leitner; for(const g of ['die Herausforderung','sich entscheiden','die Nachhaltigkeit']){L[g]={b:1,d:GD.dateStr()};}}""")
            pg.click('[data-tab="leitner"]'); pg.click('[data-rev="start"]'); pg.click('[data-rev="show"]')
            pg.screenshot(path=str(OUT / "leitner-narrow.png"))
            pg.click('[data-tab="text"]'); pg.fill("#tr-input", TEXT); pg.click("#btn-tr-go")
            pg.wait_for_function("() => document.querySelector('#tr-status').textContent.includes('✅')")
            pg.click('#tr-text [data-tok="2"]')
            pg.evaluate("window.scrollTo(0,0)")
            pg.screenshot(path=str(OUT / "text-narrow.png"))
            pg.click('[data-tab="grammar"]'); pg.click('[data-gram="B2-01"]')
            pg.screenshot(path=str(OUT / "grammar-narrow.png"))
            ctx.close()
            ctx2 = b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1, locale="fa-IR", service_workers="block", bypass_csp=True)
            ctx2.route("**/translate.googleapis.com/**", mock)
            pg = ctx2.new_page(); pg.goto(f"http://localhost:{PORT}/app.html")
            pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
            pg.click('[data-tab="text"]'); pg.fill("#tr-input", TEXT); pg.click("#btn-tr-go")
            pg.wait_for_function("() => document.querySelector('#tr-status').textContent.includes('✅')")
            pg.screenshot(path=str(OUT / "wide.png"))
            b.close()
    finally:
        srv.terminate()
    print(sorted(x.name for x in OUT.iterdir()))

if __name__ == "__main__":
    main()
