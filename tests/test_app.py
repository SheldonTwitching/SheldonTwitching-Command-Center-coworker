import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app


def test_default_project():
    p = app.default_project()
    assert p["title"] == "SheldonTwitching Labels"
    assert len(p["items"]) == 3
    assert all(i["file"].endswith(".txt") for i in p["items"])
    assert app.validate_project(p) == p


def test_safe_files(tmp_path):
    (tmp_path / "most_recent_donator.txt").write_text("n3veruary $10.00!", encoding="utf-8")
    (tmp_path / "unicode.txt").write_text("\ufeffΩmegasub", encoding="utf-8")
    (tmp_path / "not_a_label.bin").write_text("bad")
    p = app.default_project()
    p["folder"] = str(tmp_path)
    assert len(app.folder_files(p)) == 2
    assert app.safe_text(str(tmp_path), "most_recent_donator.txt") == "n3veruary $10.00!"
    assert app.safe_text(str(tmp_path), "unicode.txt") == "Ωmegasub"
    assert app.safe_text(str(tmp_path), "../secret.txt") is None
    assert app.safe_text(str(tmp_path), "not_a_label.bin") is None


def test_project_validation():
    p = app.default_project()
    p["width"] = 1
    try: app.validate_project(p)
    except ValueError: pass
    else: assert False, "Invalid width should fail"


def test_export(tmp_path):
    p = app.default_project()
    raw = app.build_export_zip(p, 47831)
    path = tmp_path / "overlay.zip"
    path.write_bytes(raw)
    with zipfile.ZipFile(path) as archive:
        assert set(["overlay.html", "overlay.css", "renderer.js", "project.json", "README.txt"]).issubset(archive.namelist())
        html = archive.read("overlay.html").decode("utf-8")
        assert "SL_EMBEDDED_PROJECT" in html
        assert "http://127.0.0.1:47831" in html


def test_server_http_roundtrip(tmp_path):
    import socket
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    labels = tmp_path / "data"
    labels.mkdir()
    (labels / "most_recent_donator.txt").write_text("P1 $52.00", encoding="utf-8")
    env = os.environ.copy()
    env["ST_LABELS_HOME"] = str(tmp_path / "config")
    server_log = tmp_path / "server-errors.log"
    with server_log.open("wb") as log:
        proc = subprocess.Popen([sys.executable, str(ROOT / "app.py"), "--port", str(port), "--headless"], env=env, stdout=subprocess.DEVNULL, stderr=log)
    base = f"http://127.0.0.1:{port}"
    def get(path):
        with urllib.request.urlopen(base + path, timeout=3) as response:
            return response.read(), response.headers
    def post(path, value):
        request = urllib.request.Request(base + path, data=json.dumps(value).encode(), headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=3) as response:
            return json.loads(response.read())
    try:
        for n in range(40):
            try:
                raw, headers = get("/health")
                break
            except (urllib.error.URLError, ConnectionError):
                time.sleep(.1)
        else: assert False, "Server did not become ready"
        assert json.loads(raw)["ok"]
        assert b"SheldonTwitching Labels" in get("/editor")[0]
        assert b"overlayHost" in get("/overlay")[0]
        startup = json.loads(get("/api/startup")[0])
        assert isinstance(startup["enabled"], bool)
        assert isinstance(startup["supported"], bool)
        project = json.loads(get("/api/project")[0])
        project["items"][0]["label"] = "MY TEST FOLLOWER"
        assert post("/api/project", project)["ok"]
        assert json.loads(get("/api/project")[0])["items"][0]["label"] == "MY TEST FOLLOWER"
        saved_project, project_headers = get("/api/project/download")
        assert json.loads(saved_project)["items"][0]["label"] == "MY TEST FOLLOWER"
        assert "attachment" in project_headers["Content-Disposition"]
        assert (tmp_path / "config" / "project.json.bak").exists()
        bad = json.loads(saved_project)
        bad["items"].append(dict(bad["items"][0]))  # Duplicate IDs rejected.
        try:
            post("/api/project", bad)
        except urllib.error.HTTPError as err:
            assert err.code == 400
        else:
            assert False, "Invalid imported project should be rejected"
        assert json.loads(get("/api/project")[0])["items"][0]["label"] == "MY TEST FOLLOWER"
        assert post("/api/folder", {"folder": str(labels)})["files"] == ["most_recent_donator.txt"]
        try:
            snap = json.loads(get("/api/snapshot")[0])
        except Exception:
            print("Bridge return code:", proc.poll())
            print("Bridge stderr:", server_log.read_text(encoding="utf-8", errors="replace"))
            raise
        assert snap["live"]["most_recent_donator.txt"] == "P1 $52.00"
        zraw, zhead = get("/api/export")
        assert zhead["Content-Type"] == "application/zip"
        assert len(zraw) > 500
    finally:
        proc.terminate()
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()
