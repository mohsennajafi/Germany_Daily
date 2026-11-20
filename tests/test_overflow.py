import os
BASE=os.environ.get("BASE","http://localhost:8792/")
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch()
    for W in (320,360,390,412,768,1100,1440):
        ctx=b.new_context(viewport={"width":W,"height":800}, service_workers="block", is_mobile=W<600, has_touch=W<600); pg=ctx.new_page()
        for url in ("index.html","app.html"):
            pg.goto(BASE+url); pg.wait_for_load_state("networkidle")
            if url=="app.html": pg.wait_for_function("() => window.GD && GD.state.words.length>1000")
            sw=pg.evaluate("document.documentElement.scrollWidth"); iw=pg.evaluate("window.innerWidth")
            print(("OK  " if sw<=iw+1 else "OVER"), url, "viewport",W,"scrollWidth",sw)
        ctx.close()
    b.close()
