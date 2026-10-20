"""Optional browser smoke test: no web server or CDN needed.

Run `pip install pytest playwright; playwright install chromium` to enable.
The test injects the exact production HTML/CSS/JS and a mocked local API,
which makes it run in sandboxes that block loopback browser navigation.
"""
from pathlib import Path
import sys
import pytest

playwright = pytest.importorskip("playwright.sync_api")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import default_project


def test_editor_browser_smoke():
    with playwright.sync_playwright() as manager:
        try:
            try:
                browser = manager.chromium.launch(headless=True)
            except Exception:
                # Container runners often have system Chromium but no Playwright download.
                system_chromium = Path("/usr/bin/chromium")
                if not system_chromium.exists(): raise
                browser = manager.chromium.launch(headless=True, executable_path=str(system_chromium), args=["--no-sandbox"])
        except Exception as exc:
            pytest.skip(f"Chromium not available: {exc}")
        try:
            page = browser.new_page(viewport={"width": 1540, "height": 940})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            html = (ROOT / "web/editor.html").read_text(encoding="utf-8")
            html = html.replace('<link rel="stylesheet" href="editor.css">', '')
            html = html.replace('<script src="renderer.js"></script><script src="editor.js"></script>', '')
            page.set_content(html)
            page.add_style_tag(content=(ROOT / "web/editor.css").read_text(encoding="utf-8"))
            page.evaluate('''project => {
                window.fetch = async (path, options) => ({
                    ok: true,
                    json: async () => path === '/api/snapshot' ? {project, live:{}, files:[]} : {ok:true},
                    text: async () => ''
                });
            }''', default_project())
            page.add_script_tag(content=(ROOT / "web/renderer.js").read_text(encoding="utf-8"))
            page.add_script_tag(content=(ROOT / "web/editor.js").read_text(encoding="utf-8"))
            page.evaluate('window.dispatchEvent(new Event("DOMContentLoaded"))')
            page.wait_for_timeout(100)
            assert page.locator('.item-row').count() == 3
            assert page.locator('#previewHost').evaluate('(node) => node.shadowRoot.querySelectorAll(".overlay-card").length') == 3
            css = (ROOT / "web/overlay.css").read_text(encoding="utf-8")
            page.locator('#previewHost').evaluate('''(node, css) => {
                const el = document.createElement('style'); el.textContent = css;
                node.shadowRoot.insertBefore(el, node.shadowRoot.firstChild);
            }''', css)
            page.locator('[data-preset="flame"]').click()
            page.wait_for_timeout(420)
            assert page.locator('[data-field="accent"]').input_value() == '#ff8b19'
            page.locator('#undo').click()
            assert page.locator('[data-field="accent"]').input_value() == '#e600d9'
            page.locator('#redo').click()
            assert page.locator('[data-field="accent"]').input_value() == '#ff8b19'
            page.locator('[data-tab="css"]').click()
            page.locator('#customCSS').fill('.overlay-card { --bg: rgb(3, 4, 5); }')
            background = page.locator('#previewHost').evaluate('''node => getComputedStyle(
                node.shadowRoot.querySelector('.overlay-card')).backgroundColor''')
            assert background == 'rgb(3, 4, 5)', background
            assert not errors, errors
        finally:
            browser.close()
