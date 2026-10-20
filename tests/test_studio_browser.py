"""Actual app preview/navigation and measured transparent source integration."""
import json, os, socket, subprocess, sys, time
from pathlib import Path
from urllib.request import urlopen
import pytest
pw=pytest.importorskip('playwright.sync_api')
ROOT=Path(__file__).resolve().parents[1]

def test_command_center_preview_and_parts(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    env={**os.environ,'ST_LABELS_HOME':str(tmp_path)}
    process=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--headless','--port',str(port)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(50):
            try:
                with urlopen(base+'/health',timeout=1):break
            except OSError:time.sleep(.1)
        with pw.sync_playwright() as manager:
            try:browser=manager.chromium.launch()
            except Exception as exc:pytest.skip(f'Chromium unavailable: {exc}')
            errors=[];network=[];console=[];page=browser.new_page(viewport={'width':1600,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
            page.on('requestfailed',lambda r:network.append((r.url,r.failure)) if 'ERR_ABORTED' not in (r.failure or '') else None)
            page.goto(base+'/studio')
            pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            page.get_by_role('button',name='Preview',exact=True).click()
            page.locator('#preview-scene').select_option('gameplay')
            pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            pw.expect(page.locator('#scene-preview')).to_have_attribute('src','/studio/scene?scene=gameplay&format=landscape')
            try:page.locator('#preview-output').select_option('/studio/parts/buttons',timeout=15000)
            except Exception as exc:raise AssertionError({'pageErrors':errors,'requests':network[-30:],'console':console[-30:],'toast':page.locator('#toast').text_content(),'sources':page.locator('#source-links').text_content()}) from exc
            pw.expect(page.locator('#scene-preview')).to_have_attribute('src','/studio/parts/buttons')
            page.get_by_role('button',name='Audio & Lighting',exact=True).click()
            pw.expect(page.locator('#audio-panel')).to_be_visible()
            assert page.locator('#studio-obs-source').count()==1
            page.get_by_role('button',name='Widgets & Chat',exact=True).click()
            pw.expect(page.locator('[data-reader="mode"]')).to_be_visible()
            page.get_by_role('button',name='Widget Roadmaps',exact=True).click()
            pw.expect(page.get_by_role('heading',name='Cabinet Structure & Marquee',exact=True)).to_be_visible()
            proof=os.environ.get('ST_STUDIO_PROOF_DIR')
            if proof:
                Path(proof).mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(Path(proof)/'roadmaps-updated.png'))
            with urlopen(base+'/api/project',timeout=2) as response:label_id=json.load(response)['items'][0]['id']
            page.goto(base+'/overlay?label='+label_id)
            pw.expect(page.locator('#overlayHost .overlay-card')).to_have_count(1)
            pw.expect(page.locator('#overlayHost .overlay-card')).to_have_attribute('data-id',label_id)
            page.goto(base+'/arcade/overlay')
            try:pw.expect(page.locator('html')).to_have_attribute('data-marquee-style','graffiti',timeout=15000)
            except AssertionError as exc:raise AssertionError({'pageErrors':errors,'requests':network,'console':console}) from exc
            if proof:
                page.wait_for_timeout(300);page.screenshot(path=str(Path(proof)/'native-graffiti-marquee.png'),omit_background=True)
            page.goto(base+'/studio/parts/all')
            page.wait_for_function('document.querySelector("canvas").width===1920')
            page.wait_for_timeout(700)
            import io
            from PIL import Image
            # Native controls/reflections are visible near the deck; middle of glass is alpha.
            page.set_viewport_size({'width':1920,'height':1080})
            shot=page.screenshot(omit_background=True)
            image=Image.open(io.BytesIO(shot))
            assert image.getpixel((1000,500))[3]==0
            assert image.getpixel((190,500))[3]>0
            if proof:Path(proof,'gameplay-parts.png').write_bytes(shot)
            page.goto(base+'/studio')
            page.get_by_role('button',name='Preview',exact=True).click()
            page.locator('#preview-scene').select_option('gameplay')
            pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            if proof:
                page.wait_for_timeout(700);page.screenshot(path=str(Path(proof)/'command-center-preview.png'))
            assert not errors,errors
            browser.close()
    finally:
        process.terminate();process.wait(timeout=10)
