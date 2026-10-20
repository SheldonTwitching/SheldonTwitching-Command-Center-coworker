"""Pop-outs preserve native output sizes and leave the editor available."""
import os,socket,subprocess,sys,time
from pathlib import Path
from urllib.request import urlopen
import pytest
ROOT=Path(__file__).resolve().parents[1]

def test_popout_sources_zoom_and_editors(tmp_path):
    pw=pytest.importorskip('playwright.sync_api')
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--headless','--port',str(port)],env={**os.environ,'ST_LABELS_HOME':str(tmp_path)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(60):
            try:
                with urlopen(base+'/health',timeout=1):break
            except OSError:time.sleep(.1)
        with pw.sync_playwright() as p:
            b=p.chromium.launch();context=b.new_context();page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/studio');pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            with page.expect_popup() as popped:page.get_by_role('button',name='Pop out Live stream scene preview',exact=True).click()
            popup=popped.value;popup.wait_for_load_state();pw.expect(popup.locator('#output')).to_have_attribute('src',__import__('re').compile('/studio/scene'))
            popup.get_by_role('button',name='100% native',exact=True).click();pw.expect(popup.locator('#percent')).to_have_text('100%')
            assert popup.locator('#output').evaluate('f=>f.style.width')=='1920px'
            popup.locator('#zoom').fill('200');pw.expect(popup.locator('#percent')).to_have_text('200%')
            assert popup.locator('#output').evaluate('f=>f.style.width')=='1920px'
            assert popup.locator('#extent').evaluate('f=>f.style.width')=='3840px'
            popup.close();pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            for path,label in [('/studio/cabinet','Pop out Live cabinet parts preview'),('/arcade/editor','Pop out Live arcade overlay'),('/editor','Pop out label preview')]:
                page.goto(base+path)
                with page.expect_popup() as popped:page.get_by_role('button',name=label,exact=True).click()
                pop=popped.value;pop.wait_for_load_state();pw.expect(pop.locator('#output')).to_have_attribute('src',__import__('re').compile('/studio/parts/all|/arcade/overlay|/overlay'))
                if path=='/studio/cabinet':
                    pop.get_by_role('button',name='100% native',exact=True).click();pw.expect(pop.locator('#output')).to_have_css('width','2060px')
                pop.close()
            page.goto(base+'/studio');pw.expect(page.locator('#save-status')).to_have_text('Saved locally');page.get_by_role('button',name='Setup & Sources',exact=True).click();pw.expect(page.locator('#source-links .preview-popout').first).to_be_visible()
            with page.expect_popup() as popped:page.locator('#source-links .preview-popout').first.click()
            popped.value.close()
            assert not errors,errors
            b.close()
    finally:proc.terminate();proc.wait(timeout=10)
