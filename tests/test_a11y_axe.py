import json
from playwright.sync_api import sync_playwright
AX=open('/tmp/jt/node_modules/axe-core/axe.min.js',encoding='utf-8').read()
def run(pg,label):
    pg.evaluate(AX)
    r=pg.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','best-practice']}}).then(r=>r.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,help:v.help,ex:v.nodes[0].target.join(' ')})))")
    print("==",label, "violations:",len(r))
    for v in r: print("  ",v['impact'],v['id'],v['n'],v['help'],'|',v['ex'])
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":412,"height":860}, service_workers="block", bypass_csp=True); pg=ctx.new_page()
    pg.goto("http://localhost:8792/index.html"); pg.wait_for_load_state("networkidle"); run(pg,"landing")
    pg.goto("http://localhost:8792/app.html"); pg.wait_for_function("() => window.GD && GD.state.words.length>1000"); run(pg,"app/daily")
    for tab in ("leitner","text","search","verbs","grammar","ai","settings"):
        pg.click(f'[data-tab="{tab}"]'); run(pg,"app/"+tab)
    pg.click('[data-tab="grammar"]'); pg.click('[data-gram="B2-01"]'); run(pg,"app/grammar-modal")
    b.close()
