import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app
from spotify_bridge import SpotifyBridge


def test_tip_money_and_fallback(tmp_path):
    assert app.parse_money("This month's total: $1,234.56", 9) == 1234.56
    assert app.parse_money("none", 9) == 9
    assert app.parse_money("-$5.00", 9) == 0
    project = app.default_project()
    project["tipBar"].update({"amountFile": "raised.txt", "goalFile": "goal.txt"})
    folder = tmp_path / "labels"
    folder.mkdir()
    (folder / "raised.txt").write_text("$12.50")
    (folder / "goal.txt").write_text("$50")
    project["folder"] = str(folder)
    with patch.object(app, "load_project", return_value=project):
        data = app.tip_snapshot()
    assert data["amount"] == 12.5
    assert data["goal"] == 50
    assert data["percent"] == 25
    project["tipBar"]["goalFallback"] = 0
    (folder / "goal.txt").unlink()
    with patch.object(app, "load_project", return_value=project):
        assert app.tip_snapshot()["percent"] == 0


def test_tip_validation_and_upgrade():
    project = app.default_project()
    project["tipBar"]["amountFile"] = "../outside.txt"
    try:
        app.validate_project(project)
    except ValueError:
        pass
    else:
        assert False, "Traversal should be rejected"
    project = app.default_project()
    project.pop("tipBar")
    assert app.validate_project(project)["tipBar"]["title"] == "STREAM COSTS"


def test_spotify_pkce_secret_local_only(tmp_path):
    b = SpotifyBridge(tmp_path)
    client = "a" * 32
    b.configure(client)
    login = b.start_auth(47831)
    parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(login).query)
    assert parsed["code_challenge_method"] == ["S256"]
    assert parsed["redirect_uri"] == ["http://127.0.0.1:47831/spotify/callback"]
    assert "client_secret" not in login
    state = parsed["state"][0]
    with patch.object(b, "_token_post", return_value={"access_token": "private-access", "refresh_token": "private-refresh", "expires_in": 3600}):
        try:
            b.finish_auth("wrong-state", "auth-code", 47831)
        except ValueError:
            pass
        else:
            assert False, "CSRF state must be verified"
        login = b.start_auth(47831)
        state = urllib.parse.parse_qs(urllib.parse.urlsplit(login).query)["state"][0]
        b.finish_auth(state, "auth-code", 47831)
    assert b.status()["connected"]
    assert "private-access" not in json.dumps(b.status())
    b.disconnect()
    assert not b.status()["connected"]
    assert not (tmp_path / "spotify_tokens.json").exists()


def test_spotify_payload():
    result = SpotifyBridge.simplify({"is_playing": True, "item": {"name": "Track", "artists": [{"name": "Artist"}], "album": {"name": "Album", "images": [{"url": "https://i.scdn.co/image/abc"}]}, "external_urls": {"spotify": "https://open.spotify.com/track/abc"}}})
    assert result["title"] == "Track"
    assert result["artist"] == "Artist"
    assert result["state"] == "playing"
    assert SpotifyBridge.simplify({"is_playing": False})["state"] == "paused"
    assert SpotifyBridge.simplify({"is_playing": True, "item": {"name": "T", "album": {"images": [{"url": "javascript:alert(1)"}]}}})["art"] == ""


def test_widget_export_and_routes(tmp_path):
    import socket
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env["ST_LABELS_HOME"] = str(tmp_path / "cfg")
    proc = subprocess.Popen([sys.executable, str(ROOT / "app.py"), "--port", str(port), "--headless"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for i in range(50):
            try:
                urllib.request.urlopen(base + "/health", timeout=1).close()
                break
            except urllib.error.URLError:
                time.sleep(.1)
        else:
            assert False, "Bridge did not start"
        for url in ("/now-playing", "/tip-bar", "/now-playing.css", "/tip-bar.js", "/roster.json", "/assets/sf6/ryu.png"):
            with urllib.request.urlopen(base + url, timeout=3) as res:
                assert res.status == 200
                assert res.read()
        with urllib.request.urlopen(base + "/api/tip-bar") as response:
            assert json.load(response)["goal"] == 50
        with urllib.request.urlopen(base + "/api/spotify/status") as response:
            state = json.load(response)
            assert not state["connected"]
        with urllib.request.urlopen(base + "/api/spotify/now-playing") as response:
            assert json.load(response)["state"] == "disconnected"
        with urllib.request.urlopen(base + "/api/export") as response:
            import io, zipfile
            with zipfile.ZipFile(io.BytesIO(response.read())) as archive:
                for name in ("now-playing.html", "now-playing.js", "tip-bar.html", "tip-bar.css"):
                    assert name in archive.namelist()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
