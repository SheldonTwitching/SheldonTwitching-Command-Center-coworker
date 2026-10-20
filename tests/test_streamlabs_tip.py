"""Streamlabs Tip Goal integration must not be mistaken for a Streamlabels text bar."""
from pathlib import Path
from unittest.mock import patch
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def test_streamlabs_tip_assets_and_export():
    import app
    assert (ROOT / 'streamlabs-tip-goal' / 'HTML.txt').is_file()
    project = app.default_project()
    project['tipBar'].update(accent='#ff00bb', secondary='#ff3355', animation='pulse', fontSize=23, customCSS='#st-tip-goal { letter-spacing: 1px; }')
    css = app.render_streamlabs_tip_css(project)
    assert '#ff00bb' in css and '#ff3355' in css and '23px' in css
    assert 'letter-spacing: 1px' in css
    js = app.render_streamlabs_tip_js(project)
    assert "root.dataset.animation = 'pulse'" in js
    package = app.build_streamlabs_tip_zip(project)
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        assert set(archive.namelist()) == {'HTML.txt', 'CSS.txt', 'JS.txt', 'INSTALL.txt'}
        assert 'goalLoad' in archive.read('JS.txt').decode('utf-8')
        assert 'goalEvent' in archive.read('JS.txt').decode('utf-8')
        assert 'streamlabs.com' in archive.read('INSTALL.txt').decode('utf-8')


def test_legacy_data_bridge_not_used_as_live_stream_costs_source():
    source = (ROOT / 'scenes/gameplay.html').read_text(encoding='utf-8')
    assert 'src="http://127.0.0.1:47831/tip-bar"' not in source
    assert 'STREAMLABS TIP GOAL' in source
    import app
    assert app.default_project()['tipBar']['accent']