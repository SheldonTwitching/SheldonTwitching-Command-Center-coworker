"""Exercise the actual board routes, persistence, dialogs and Studio navigation."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
import pytest
ROOT=Path(__file__).resolve().parents[1]


def test_board_crud_restart_filters_and_popout(tmp_path):
    pw=pytest.importorskip('playwright.sync_api')
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--headless','--port',str(port)],env={**os.environ,'ST_LABELS_HOME':str(tmp_path)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(60):
            try:
                with urlopen(base+'/health',timeout=1):break
            except OSError:time.sleep(.1)
        with pw.sync_playwright() as p:
            b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/studio');pw.expect(page.locator('#save-status')).to_have_text('Saved locally')
            page.get_by_role('button',name='Board',exact=True).click()
            frame=page.frame_locator('#tool-frame')
            pw.expect(frame.locator('#columns .column')).to_have_count(6)
            frame.get_by_role('button',name='New card',exact=True).click()
            frame.locator('#title').fill('Owner screenshot review')
            frame.locator('#description').fill('Check paint below marquee')
            frame.locator('#acceptance').fill('No unpainted gaps or pink trim bleed')
            frame.locator('#card-area').select_option('cabinet')
            frame.get_by_role('button',name='Save card',exact=True).click()
            pw.expect(frame.locator('#edit')).not_to_be_visible()
            frame.locator('#search').fill('Owner screenshot review')
            try:pw.expect(frame.locator('.card')).to_have_count(1)
            except AssertionError as e:raise AssertionError({'notice':frame.locator('#notice').text_content(),'error':frame.locator('#form-error').text_content(),'pageErrors':errors}) from e
            frame.locator('.card select').select_option('Done')
            pw.expect(frame.locator('#notice')).to_contain_text('Done requires')
            frame.locator('.card select').select_option('Owner testing')
            pw.expect(frame.locator('[aria-label="Owner testing"] .card')).to_have_count(1)
            frame.locator('.card button').click();frame.locator('#blocked').check();frame.locator('#blockedReason').fill('Need OBS rehearsal')
            frame.get_by_role('button',name='Save card',exact=True).click()
            pw.expect(frame.locator('#edit')).not_to_be_visible()
            frame.locator('#blocked-only').check();pw.expect(frame.locator('.card')).to_have_count(1)
            # A second window changes the board; stale dialog retains the owner's draft.
            frame.locator('.card button').click()
            other=b.new_page();other.goto(base+'/studio/board');other.locator('#new').click();other.locator('#title').fill('Concurrent edit');other.get_by_role('button',name='Save card',exact=True).click();pw.expect(other.locator('#edit')).not_to_be_visible()
            frame.locator('#description').fill('Keep this draft after conflict')
            frame.get_by_role('button',name='Save card',exact=True).click()
            pw.expect(frame.locator('#form-error')).to_contain_text('another window')
            pw.expect(frame.locator('#description')).to_have_value('Keep this draft after conflict')
            frame.get_by_role('button',name='Cancel',exact=True).click()
            page.goto(base+'/studio/board');page.locator('#search').fill('Owner screenshot review');pw.expect(page.locator('.card')).to_have_count(1)
            with page.expect_popup() as popup:page.get_by_role('button',name='Pop out board',exact=True).click()
            pop=popup.value;pop.wait_for_load_state();pw.expect(pop.locator('#output')).to_have_attribute('src',base+'/studio/board');pop.close()
            proof=os.environ.get('ST_STUDIO_PROOF_DIR')
            if proof:
                page.locator('#search').fill('');page.locator('#area').select_option('cabinet')
                Path(proof).mkdir(parents=True,exist_ok=True);page.screenshot(path=str(Path(proof)/'command-center-board.png'),full_page=True)
            assert not errors,errors
            assert (tmp_path/'kanban.json').exists()
            b.close()
    finally:
        proc.terminate();proc.wait(timeout=10)
