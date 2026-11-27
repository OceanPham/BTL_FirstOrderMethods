"""Offline content and browser checks. Requires Playwright only for maintenance."""
from pathlib import Path
import argparse, json, hashlib, re, math
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright

GUIDE=Path(__file__).resolve().parents[1]
def check_content():
    raw=(GUIDE/"sources.js").read_text(encoding="utf-8")
    data=json.loads(raw.split("window.GUIDE_SOURCES = ",1)[1].rstrip().removesuffix(";"))
    assert len(data["files"])==5
    html=(GUIDE/"index.html").read_text(encoding="utf-8")
    for key in re.findall(r'data-snippet="([^"]+)"',html):
        sn=data["snippets"][key];f=data["files"][sn["file"]]
        assert sn["code"]=="\n".join(f["text"].splitlines()[sn["start"]-1:sn["end"]])
        path=GUIDE.parent/"code"/f["name"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==f["sha256"],f["name"]
    ids=re.findall(r'\bid="([^"]+)"',html)
    assert len(ids)==len(set(ids)),"Duplicate HTML IDs"
    for target in re.findall(r'(?:src|href)="([^"]+)"',html):
        if target.startswith("#"): assert target[1:] in ids,target
        elif not urlsplit(target).scheme: assert (GUIDE/target).exists(),target
    print("PASS: local assets, anchor IDs, 5 source hashes, all 23 exact excerpts")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--browser",default="msedge",choices=["msedge","chromium"]);ap.add_argument("--screenshots",type=Path)
    a=ap.parse_args();check_content()
    if a.screenshots:a.screenshots.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,**({"channel":"msedge"} if a.browser=="msedge" else {}))
        ctx=browser.new_context(viewport={"width":1440,"height":1000},reduced_motion="reduce")
        page=ctx.new_page();errors=[];remote=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("request",lambda r:remote.append(r.url) if r.url.startswith(("http:","https:")) else None)
        page.goto((GUIDE/"index.html").as_uri());page.wait_for_load_state("networkidle")
        assert page.locator(".snippet").count()==23
        assert page.locator("main>section").count()==14
        assert page.locator(".mark-read").count()==13
        assert page.locator("main>section").nth(1).get_attribute("id")=="problem"
        assert "Input" in page.locator("#problem").inner_text()
        assert "Output" in page.locator("#problem").inner_text()
        assert page.locator('a[href="#run"]').count()>=3
        assert page.locator("#run .command-tools button").count()==10
        assert page.locator("h1").evaluate("el=>getComputedStyle(el).fontFamily").startswith("Arial")
        assert page.locator(".formula").first.evaluate("el=>getComputedStyle(el).fontFamily").startswith("Arial")
        cdp=ctx.new_cdp_session(page)
        root=cdp.send("DOM.getDocument")["root"]["nodeId"]
        title_node=cdp.send("DOM.querySelector",{"nodeId":root,"selector":"h1"})["nodeId"]
        cdp.send("CSS.enable")
        fonts=cdp.send("CSS.getPlatformFontsForNode",{"nodeId":title_node})["fonts"]
        assert any("Arial" in f["familyName"] for f in fonts),fonts
        print("PASS: first input/output section, 10 command blocks, actual Arial title font")
        # Images load lazily; visit each figure before checking decoded pixels.
        for img in page.locator("img").all():
            img.scroll_into_view_if_needed()
            page.wait_for_function("el=>el.complete&&el.naturalWidth>0",arg=img.element_handle())
        page.evaluate("window.scrollTo(0,0)")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"),"desktop horizontal overflow"
        if a.screenshots:
            page.screenshot(path=str(a.screenshots/"desktop.png"))
            page.locator("#problem").screenshot(path=str(a.screenshots/"problem.png"))
            page.locator("#run").screenshot(path=str(a.screenshots/"run.png"))
        expected={"gd":0.7877037037037037,"sgd":0.666,"mb":0.78375}
        for method,w in expected.items():
            page.select_option("#method",method)
            for _ in range(3):page.click("#step")
            got=float(page.locator("#sim-status").get_attribute("data-w"))
            assert math.isclose(got,w,abs_tol=1e-12),(method,got)
            assert page.locator("#step").is_disabled()
            assert page.locator("#history tr").count()==3
        assert math.isclose(page.evaluate("GuideMath.loss(GuideMath.wStar)"),9/28,abs_tol=1e-12)
        page.select_option("#rate","0.02");assert float(page.locator("#sim-status").get_attribute("data-w"))==0
        page.select_option("#method","gd");page.click("#step")
        assert math.isclose(float(page.locator("#sim-status").get_attribute("data-w")),13/150,abs_tol=1e-12)
        page.select_option("#rate","0.1");page.select_option("#method","mb");page.click("#step")
        if a.screenshots:page.locator("#lab").screenshot(path=str(a.screenshots/"lab.png"))
        print("PASS: 3 methods, all 3-step results, reset on rate change, optimal loss")
        page.select_option("#quad-rate","0.5");page.click("#quad-step")
        assert "z = 0" in page.locator("#quad-status").inner_text()
        page.select_option("#quad-rate","1");page.click("#quad-step")
        assert "z = -2" in page.locator("#quad-status").inner_text()
        page.select_option("#quad-rate","1.1");page.click("#quad-step")
        assert "z = -2.4" in page.locator("#quad-status").inner_text()
        page.click("#quad-reset")
        assert "Bước 0" in page.locator("#quad-status").inner_text()
        print("PASS: convergence, oscillation and divergence controls")
        page.locator('[data-mark="6"]').click()
        assert page.locator("#read-count").inner_text()=="1 / 13 mục"
        page.locator('[data-mark="0"]').click()
        assert page.locator("#read-count").inner_text()=="2 / 13 mục"
        page.reload();page.wait_for_load_state("networkidle")
        assert page.locator('[data-mark="6"]').get_attribute("aria-pressed")=="true"
        assert page.locator('[data-mark="0"]').get_attribute("aria-pressed")=="true"
        page.locator("#run .command-tools button").first.click()
        assert page.locator("#run .command-block .copy-status").first.inner_text()
        page.fill("#nav-search","numpy");assert page.locator("nav a:visible").count()==1
        page.fill("#nav-search","no-such-lesson");assert page.locator("#nav-empty").is_visible()
        page.fill("#nav-search","")
        page.locator(".open-source").first.click()
        assert page.locator("#full-source").get_attribute("open") is not None
        assert page.locator("#source-select").input_value()=="01"
        page.select_option("#source-select","05")
        assert "optimizer.step()" in page.locator("#source-code").inner_text()
        with page.expect_download() as info:page.click("#download-source")
        assert info.value.suggested_filename=="05_pytorch_mang_no_ron.py"
        page.locator(".copy-code").first.click()
        assert page.locator(".copy-status").first.inner_text()
        correct=[1,2,1,2,1,1,2,0]
        for i,answer in enumerate(correct):page.check(f'input[name="q{i}"][value="{answer}"]')
        page.locator('#quiz-form button[type="submit"]').click()
        assert "8 / 8" in page.locator("#quiz-score").inner_text()
        assert page.locator(".feedback.correct").count()==8
        page.locator('#quiz-form button[type="reset"]').click()
        assert page.locator('input[type="radio"]:checked').count()==0
        assert page.locator("#quiz-score").inner_text()==""
        print("PASS: persisted reading, search, full-source switch, download, copy status, quiz")
        page.locator("#numpy").scroll_into_view_if_needed()
        if a.screenshots:
            page.locator('[data-snippet="03:loop"]').screenshot(path=str(a.screenshots/"code.png"))
        page.emulate_media(media="print")
        assert page.locator("#sidebar").is_hidden()
        page.emulate_media(media="screen")
        mobile=ctx.new_page();mobile.set_viewport_size({"width":390,"height":844})
        mobile.goto((GUIDE/"index.html").as_uri());mobile.wait_for_load_state("networkidle")
        assert mobile.evaluate("document.documentElement.scrollWidth<=innerWidth"),"mobile horizontal overflow"
        assert mobile.locator("#sidebar").is_hidden()
        mobile.click("#menu-toggle");assert mobile.locator("#sidebar").is_visible()
        mobile.locator('nav a[href="#lab"]').click();assert mobile.locator("#sidebar").is_hidden()
        mobile.select_option("#method","sgd");mobile.click("#step")
        assert math.isclose(float(mobile.locator("#sim-status").get_attribute("data-w")),0.1,abs_tol=1e-12)
        if a.screenshots:mobile.screenshot(path=str(a.screenshots/"mobile.png"))
        assert mobile.evaluate("document.documentElement.scrollWidth<=innerWidth"),"lab mobile overflow"
        assert not errors,errors
        assert not remote,remote
        print("PASS: 390px mobile menu/lab, print layout, no JS errors, zero remote requests")
        browser.close()
    print("ALL GUIDE CHECKS PASSED")
if __name__=="__main__":main()

