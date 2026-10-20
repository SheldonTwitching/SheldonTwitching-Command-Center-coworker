"""SheldonTwitching Labels: local-only Windows overlay editor + OBS data bridge.

Start with `python app.py`. For Windows desktop window, install pywebview.
All state lives in %APPDATA%/SheldonTwitchingLabels unless ST_LABELS_HOME is set.
"""
from __future__ import annotations

import argparse
import mimetypes
import hmac
import io
import json
import os
import re
import shutil
import socket
import sys
import threading
import time
import webbrowser
import zipfile
from copy import deepcopy
from http import HTTPStatus
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from studio_runtime import StudioRuntime, SCENES as STUDIO_SCENES
from spotify_bridge import SpotifyBridge
from storage_paths import data_home
from arcade_studio import ArcadeStudio, PALETTES, STYLE_PRESETS, INPUT_FLAGS, validated as validate_arcade

APP_PORT = 47831
MAX_POST = 2_500_000
MAX_FILE = 65536
FILE_LIMIT = 250
LOCK = threading.RLock()


def bundle_root():
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


WEB = bundle_root() / "web"
ASSETS = bundle_root() / "assets"
SCENES = bundle_root() / "scenes"
TIP_THEME = bundle_root() / "streamlabs-tip-goal"
ARCADE_WEB = bundle_root() / "arcade"
HOME = data_home()
PROJECT_FILE = HOME / "project.json"
BACKUP_FILE = HOME / "project.json.bak"
SPOTIFY = SpotifyBridge(HOME)
ARCADE_STUDIO = ArcadeStudio(HOME)
ARCADE_EVENT_POLL = 0.0
STUDIO = StudioRuntime(HOME)


def default_project():
    def item(item_id, label, file_name, icon, x, fallback, accent):
        return dict(id=item_id, name=label.title(), label=label, file=file_name, icon=icon,
                    x=x, y=29, w=430, h=114, enabled=True, fontSize=30, labelSize=15,
                    iconSize=39, gap=15, pad=18, radius=13, border=2,
                    bg="#230934e8", accent=accent, textColor="#ffffff", labelColor="#e5b7ff",
                    font="'Arial Narrow', Impact, sans-serif", align="left", fontWeight=800,
                    shadow=13, parseMode="raw", delimiter=":", part=0, pattern="",
                    prefix="", suffix="", fallback=fallback,
                    enter="slide-up", exit="fade", transitionMs=550, dwell=5)

    return dict(version=1, title="SheldonTwitching Labels", width=900, height=180,
                folder="", rotation=True, customCSS="", tipBar=dict(
                    title="STREAM COSTS", amountFile="", goalFile="", amountFallback=10,
                    goalFallback=50, currency="$", accent="#e600d9", secondary="#ff1648",
                    animation="shine", fontSize=21, customCSS=""), items=[
                    item("follower", "MOST RECENT FOLLOWER", "most_recent_follower.txt", "⭐", 235, "ArcadeChallenger", "#e600d9"),
                    item("donor", "MOST RECENT DONOR", "most_recent_donator.txt", "🔥", 235, "n3veruary $10.00!", "#ff8b19"),
                    item("subscriber", "MOST RECENT SUBSCRIBER", "most_recent_subscriber.txt", "💜", 235, "ComboKing", "#b961ff")
                ])


def save_project(project):
    HOME.mkdir(parents=True, exist_ok=True)
    temp = PROJECT_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    if PROJECT_FILE.exists():
        try:
            shutil.copy2(PROJECT_FILE, BACKUP_FILE)
        except OSError:
            pass
    os.replace(temp, PROJECT_FILE)


def load_project():
    with LOCK:
        for candidate in (PROJECT_FILE, BACKUP_FILE):
            if candidate.exists():
                try:
                    project = json.loads(candidate.read_text(encoding="utf-8"))
                    return validate_project(project)
                except (OSError, ValueError, TypeError, json.JSONDecodeError):
                    pass
        project = default_project()
        save_project(project)
        return project


def validate_project(value):
    if not isinstance(value, dict):
        raise ValueError("Project must be an object")
    items = value.get("items")
    if not isinstance(items, list) or len(items) > 100:
        raise ValueError("Project must have 0–100 items")
    if not (160 <= int(value.get("width", 0)) <= 3840 and 80 <= int(value.get("height", 0)) <= 2160):
        raise ValueError("Invalid canvas size")
    if not isinstance(value.get("customCSS", ""), str) or len(value.get("customCSS", "")) > 150000:
        raise ValueError("CSS must be text under 150 KB")
    ids = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not re.fullmatch(r"[\w-]{1,60}", item["id"]):
            raise ValueError("Invalid item ID")
        if item["id"] in ids:
            raise ValueError("Duplicate item ID")
        ids.add(item["id"])
        for numeric_key in ("x", "y", "w", "h", "dwell", "transitionMs"):
            if numeric_key in item:
                try:
                    num = float(item[numeric_key])
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid {numeric_key} for {item['id']}")
                if not -10000 <= num <= 10000:
                    raise ValueError(f"Invalid {numeric_key} for {item['id']}")
        for text_key in ("name", "label", "file", "icon", "pattern", "fallback", "prefix", "suffix"):
            if text_key in item and (not isinstance(item[text_key], str) or len(item[text_key]) > (700000 if text_key == "icon" else 1500)):
                raise ValueError(f"Invalid {text_key} for {item['id']}")
    value.setdefault("tipBar", deepcopy(default_project()["tipBar"]))
    tip = value.get("tipBar", {})
    if not isinstance(tip, dict):
        raise ValueError("Invalid tip bar settings")
    for key in ("amountFile", "goalFile"):
        name = tip.get(key, "")
        if not isinstance(name, str) or (name and (Path(name).name != name or not name.lower().endswith(".txt"))):
            raise ValueError("Tip file must be a .txt filename from your Streamlabels folder")
    for key in ("amountFallback", "goalFallback"):
        try: v = float(tip.get(key, 0))
        except (ValueError, TypeError): raise ValueError("Invalid tip amount")
        if not 0 <= v <= 100000000: raise ValueError("Invalid tip amount")
    try:
        font_size = int(float(tip.get("fontSize", 21)))
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Invalid Streamlabs Tip Goal title font size")
    if not 12 <= font_size <= 36:
        raise ValueError("Streamlabs Tip Goal title font size must be between 12 and 36 pixels")
    tip["fontSize"] = font_size
    if not isinstance(tip.get("customCSS", ""), str) or len(tip.get("customCSS", "")) > 150000:
        raise ValueError("Tip CSS must be under 150 KB")
    if len(str(tip.get("title", ""))) > 100:
        raise ValueError("Tip title is too long")
    if not isinstance(value.get("folder", ""), str):
        raise ValueError("Invalid folder")
    if len(value.get("folder", "")) > 4096:
        raise ValueError("Folder path too long")
    return value


def folder_files(project):
    folder = Path(project.get("folder") or "")
    if not project.get("folder") or not folder.is_dir():
        return []
    try:
        return sorted((p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".txt"), key=str.lower)[:FILE_LIMIT]
    except OSError:
        return []


def safe_text(folder, name):
    if not name or not isinstance(name, str) or Path(name).name != name or not name.lower().endswith(".txt"):
        return None
    base = Path(folder)
    if not base.is_dir():
        return None
    try:
        path = (base / name).resolve(strict=True)
        if path.parent != base.resolve(strict=True) or not path.is_file():
            return None
        if path.stat().st_size > MAX_FILE:
            return "[Label file exceeds 64 KB]"
        raw = path.read_bytes()
        try:
            return raw.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            return raw.decode("cp1252", errors="replace").strip()
    except (OSError, ValueError):
        return None


def snapshot():
    project = load_project()
    folder = project.get("folder", "")
    names = set(folder_files(project))
    live = {}
    for item in project.get("items", []):
        name = item.get("file", "")
        if name not in live:
            live[name] = safe_text(folder, name) if name in names else None
    return dict(project=project, live=live, files=sorted(names), folderReady=bool(folder and Path(folder).is_dir()))


def parse_money(raw, fallback):
    """Extract money from an amount label; never assume a Streamlabels filename."""
    if not isinstance(raw, str):
        return float(fallback)
    match = re.search(r"(?<![\w])(?P<neg1>-)?\s*[$€£]?\s*(?P<neg2>-)?\s*(?P<amount>\d[\d,]*(?:\.\d{1,2})?)", raw)
    if not match:
        return float(fallback)
    try:
        amount = float(match.group("amount").replace(",", ""))
        return 0.0 if match.group("neg1") or match.group("neg2") else amount
    except ValueError:
        return float(fallback)


def tip_snapshot():
    p = load_project()
    tip = p.get("tipBar", {})
    files = set(folder_files(p))
    folder = p.get("folder", "")
    def read_num(key, fallback):
        filename = tip.get(key, "")
        text = safe_text(folder, filename) if filename and filename in files else None
        return parse_money(text, tip.get(fallback, 0))
    amount = read_num("amountFile", "amountFallback")
    goal = read_num("goalFile", "goalFallback")
    return {"tipBar": tip, "amount": amount, "goal": goal, "percent": min(100, amount / goal * 100) if goal > 0 else 0}



def render_streamlabs_tip_css(project):
    """Build arcade CSS for Streamlabs' own Tip Goal, not the local demo bar."""
    tip = project.get("tipBar", {})
    def hex_color(key, fallback):
        candidate = tip.get(key, fallback)
        return candidate if isinstance(candidate, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", candidate) else fallback
    try:
        font_size = max(12, min(36, int(float(tip.get("fontSize", 21)))))
    except (TypeError, ValueError, OverflowError):
        font_size = 21
    css = (TIP_THEME / "CSS.txt").read_text(encoding="utf-8")
    css = css.replace("%%ACCENT%%", hex_color("accent", "#e600d9"))
    css = css.replace("%%SECONDARY%%", hex_color("secondary", "#ff1648"))
    css = css.replace("%%FONT_SIZE%%", str(font_size))
    custom = tip.get("customCSS", "")
    return css + ("\n/* SheldonTwitching custom CSS */\n" + custom if isinstance(custom, str) and custom else "")


def render_streamlabs_tip_js(project):
    animation = project.get("tipBar", {}).get("animation", "shine")
    if animation not in ("shine", "pulse", "none"):
        animation = "shine"
    return (TIP_THEME / "JS.txt").read_text(encoding="utf-8").replace("%%ANIMATION%%", animation)


def build_streamlabs_tip_zip(project):
    """The owner's Streamlabs dashboard owns the goal and updates."""
    buffer = io.BytesIO()
    instructions = (
        "SheldonTwitching Labels — Streamlabs Tip Goal Arcade Theme\n\n"
        "Your existing Streamlabs.com Tip Goal remains the source of truth.\n"
        "Do NOT create another goal or paste private widget URLs into GitHub.\n\n"
        "1. Open streamlabs.com/dashboard > All Widgets > Tip Goal > Settings.\n"
        "2. Back up the existing custom HTML/CSS/JS in that widget first.\n"
        "3. Enable Custom HTML/CSS, then paste the contents of HTML.txt, CSS.txt,\n"
        "   and JS.txt into the respective tabs. Save Settings.\n"
        "4. Keep the SAME existing Streamlabs Tip Goal URL in OBS, as its OWN\n"
        "   Browser Source positioned over the gameplay scene's empty tip slot.\n"
        "5. Do not use the old local /tip-bar browser source for Stream Costs.\n"
        "6. Custom JavaScript uses Streamlabs goalLoad/goalEvent event data;\n"
        "   live event behavior requires a test in the Streamlabs widget preview.\n"
        "   Amounts and goal targets are managed at Streamlabs.com, not here.\n"
        "7. Adjust colors/font/motion inside SheldonTwitching Labels, download\n"
        "   this ZIP again and re-paste the generated CSS and JS to apply edits.\n"
        "Theme preview in local editor uses SAMPLE values, not live donations.\n"
    )
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("HTML.txt", (TIP_THEME / "HTML.txt").read_bytes())
        archive.writestr("CSS.txt", render_streamlabs_tip_css(project))
        archive.writestr("JS.txt", render_streamlabs_tip_js(project))
        archive.writestr("INSTALL.txt", instructions)
    return buffer.getvalue()


def build_export_zip(project, port):
    buffer = io.BytesIO()
    data = json.dumps(project, ensure_ascii=False).replace("<", "\\u003c")
    html = (WEB / "overlay.html").read_text(encoding="utf-8")
    embedded = '<script>window.SL_EMBEDDED_PROJECT=' + data + ';window.SL_API_BASE="http://127.0.0.1:' + str(port) + '";</script>'
    html = html.replace('<!-- EMBEDDED_CONFIG -->', embedded)
    readme = f"""SheldonTwitching Labels — exported overlay\n\nRecommended OBS URL: http://127.0.0.1:{port}/overlay\nBrowser Source dimensions: {project['width']} × {project['height']}\n\nYou can also load this folder's overlay.html as a local file in OBS.\nThe lightweight SheldonTwitching Labels bridge must be running to\nread live Streamlabels .txt files (browsers cannot read arbitrary Windows files).\nThe designer window may be closed as long as the bridge is running.\n\nThis ZIP contains a snapshot of your visual design and embedded icons.\nStyles are in overlay.css plus the project's custom CSS.\nUse the local URL above to see live visual edits without re-exporting.\n"""
    readme += "\nAdditional OBS URLs (bridge running):\n" + f"- Spotify Now Playing: http://127.0.0.1:{port}/now-playing\n- Streamlabs Tip Goal: Export HTML/CSS/JS from the editor (data lives at Streamlabs.com)\nLegacy demo tip bar: http://127.0.0.1:{port}/tip-bar\n"
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in ("now-playing.html", "now-playing.css", "now-playing.js", "tip-bar.html", "tip-bar.css", "tip-bar.js"):
            content = (WEB / file).read_text(encoding="utf-8")
            if file.endswith(".html"):
                content = content.replace("<!-- EMBEDDED_CONFIG -->", f'<script>window.SL_API_BASE="http://127.0.0.1:{port}";</script>')
            archive.writestr(file, content.encode("utf-8"))
        archive.writestr("overlay.html", html)
        archive.writestr("overlay.css", (WEB / "overlay.css").read_bytes())
        archive.writestr("renderer.js", (WEB / "renderer.js").read_bytes())
        archive.writestr("README.txt", readme)
        archive.writestr("project.json", json.dumps(project, indent=2, ensure_ascii=False))
    return buffer.getvalue()


def startup_script():
    """Per-user Windows Startup folder; no administrator rights needed."""
    roaming = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    return roaming / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "SheldonTwitching Labels Bridge.cmd"


def get_startup_status():
    return {"supported": sys.platform == "win32", "enabled": sys.platform == "win32" and startup_script().exists()}


def set_startup(enabled):
    if sys.platform != "win32":
        raise ValueError("Automatic startup is available on Windows only")
    path = startup_script()
    if enabled:
        path.parent.mkdir(parents=True, exist_ok=True)
        if getattr(sys, "frozen", False):
            executable, extra = sys.executable, ""
        else:
            executable, extra = sys.executable, f' "{Path(__file__).resolve()}"'
        # This launcher starts the bridge headless; desktop editor is available from tray.
        command = f'@echo off\nstart "" "{executable}"{extra} --headless\n'
        path.write_text(command, encoding="utf-8")
    else:
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise ValueError(f"Cannot disable auto-start: {exc}") from exc
    return get_startup_status()


class CommandCenterServer(ThreadingHTTPServer):
    # OBS opens many source connections together; the default backlog is only five.
    request_queue_size = 128
    # Windows SO_REUSEADDR permits a second listener to steal an existing bridge port.
    allow_reuse_address = sys.platform != "win32"

    def server_bind(self):
        if sys.platform == "win32":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def bridge_status(port):
    """Identify our bridge and verify an HTML Studio before reusing a listener."""
    import urllib.request
    owned = False
    try:
        base = f"http://127.0.0.1:{port}"
        with urllib.request.urlopen(base + "/health", timeout=1) as response:
            if json.loads(response.read()).get("app") != "SheldonTwitching Labels":
                return "foreign"
        owned = True
        version_file = ARCADE_WEB / "build-info.json"
        local_version = json.loads(version_file.read_text(encoding="utf-8")) if version_file.exists() else {"version": "2.0.0-dev"}
        with urllib.request.urlopen(base + "/api/version", timeout=1) as response:
            remote_version = json.loads(response.read())
        if remote_version.get("name") != "SheldonTwitching - Command Center":
            return "previous"
        if any(remote_version.get(key) != local_version.get(key) for key in ("version", "commit")):
            return "previous"
        with urllib.request.urlopen(base + "/studio", timeout=1) as response:
            if "text/html" not in response.headers.get("Content-Type", "") or b'id="save-status"' not in response.read():
                return "previous"
        with urllib.request.urlopen(base + "/api/studio/project", timeout=1) as response:
            json.loads(response.read())
        return "compatible"
    except HTTPError:
        return "previous" if owned else "foreign"
    except (OSError, ValueError, HTTPException):
        return "foreign"


def launch_bridge(preferred_port):
    """Keep previous OBS bridges alive; select one stable fallback for this build."""
    notice = ""
    for port in range(preferred_port, min(preferred_port + 21, 65536)):
        try:
            server = CommandCenterServer(("127.0.0.1", port), Handler)
            server.startup_notice = notice + (f" Current address: http://127.0.0.1:{port}/studio" if notice else "")
            return server, port
        except OSError:
            status = bridge_status(port)
            if status == "compatible":
                return None, port
            if port == preferred_port:
                if status != "previous":
                    raise
                notice = (f"An earlier SheldonTwitching bridge is using port {preferred_port}. "
                          "It is still running. Command Center opened on a different local port. "
                          "Use Setup & Sources to copy OBS URLs for this instance. "
                          "To return to the normal port, exit both bridges from their tray menus and reopen Command Center.")
    raise OSError("No free Command Center port was found near the configured port.")


class Handler(BaseHTTPRequestHandler):
    server_version = "SheldonTwitchingLabels/0.8"

    def log_message(self, fmt, *args):
        if os.environ.get("ST_LABELS_DEBUG"):
            super().log_message(fmt, *args)

    def cors_origin(self):
        origin = self.headers.get("Origin", "")
        if origin == "null" or re.fullmatch(r"http://(127\.0\.0\.1|localhost):[0-9]{1,5}", origin):
            return origin
        return None

    def send_bytes(self, status, data, media="application/json; charset=utf-8", download=None):
        self.send_response(status)
        self.send_header("Content-Type", media)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if self.cors_origin():
            self.send_header("Access-Control-Allow-Origin", self.cors_origin())
            self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data, status=200):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        if self.cors_origin():
            self.send_header("Access-Control-Allow-Origin", self.cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def local_host(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")

    def do_GET(self):
        if not self.local_host():
            return self.send_json({"error": "Invalid host"}, 403)
        path = urlsplit(self.path).path
        if path in ('/studio','/studio/scene','/studio/chat','/studio/text','/studio/cabinet'):
            name={'/studio':'studio.html','/studio/scene':'studio-scene.html','/studio/chat':'studio-chat.html','/studio/text':'studio-text.html','/studio/cabinet':'cabinet-workbench.html'}[path]
            return self.send_bytes(200,(ARCADE_WEB/name).read_bytes(),'text/html; charset=utf-8')
        if path.startswith('/studio/parts/'):
            if path.rsplit('/',1)[-1] not in ('all','cabinet','buttons','joystick','arrows','lighting','reflection','marquee'):return self.send_json({'error':'Unknown cabinet part'},404)
            return self.send_bytes(200,(ARCADE_WEB/'cabinet-parts.html').read_bytes(),'text/html; charset=utf-8')
        if path.startswith('/arcade/world/') or path in ('/arcade/feature-registry.json','/arcade/studio.js','/arcade/studio.css','/arcade/studio-scene.js','/arcade/stages.js','/arcade/layouts.js','/arcade/studio-chat.js','/arcade/audio-input.js','/arcade/project-spec.json','/arcade/stage-registry.json','/arcade/cabinet-rig.js','/arcade/graffiti-marquee.js','/arcade/marquee-layer.js','/arcade/frame-clock.js','/arcade/cabinet-structure.json','/arcade/cabinet-workbench.js','/arcade/cabinet-materials.js'):
            candidate=(ARCADE_WEB/path[len('/arcade/'):]).resolve()
            if not candidate.is_relative_to(ARCADE_WEB.resolve()) or candidate.suffix.lower() not in ('.html','.js','.css','.png','.webp','.json','.webm') or not candidate.is_file():return self.send_json({'error':'Not found'},404)
            return self.send_bytes(200,candidate.read_bytes(),mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream')
        if path == '/api/version':
            version_file=ARCADE_WEB/'build-info.json'
            return self.send_json(json.loads(version_file.read_text()) if version_file.exists() else {'name':'SheldonTwitching - Command Center','version':'2.0.0-dev','updates':'https://github.com/SheldonTwitching/SheldonTwitching-Command-Center/actions'})
        if path == '/api/studio/text':
            from text_reader import read_text
            return self.send_json(read_text(STUDIO.get()['textReader']))
        if path == '/api/studio/feeds':return self.send_json(snapshot())
        if path == '/api/studio/project':return self.send_json(STUDIO.get())
        if path == '/api/studio/bundle':return self.send_json({'schema':1,'studio':STUDIO.get(),'arcade':ARCADE_STUDIO.get(),'labels':load_project()})
        if path == '/api/studio/audio':return self.send_json(STUDIO.audio_snapshot())
        if path == '/api/studio/environment':return self.send_json(STUDIO.environment())
        if path == '/api/studio/chat':return self.send_json(STUDIO.messages_snapshot())
        if path == '/api/studio/scene-list':return self.send_json({'scenes':STUDIO_SCENES})
        if path == '/api/state':return self.send_json(STUDIO.game_state())
        if path == '/api/bootstrap':return self.send_json({**STUDIO.connection(self.server.server_port),'startupNotice':getattr(self.server,'startup_notice','')})
        if path == '/api/studio/chatbot-export':
            connection=STUDIO.connection(self.server.server_port);buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
                z.write(ARCADE_WEB/'DaigotronArcade_StreamlabsSystem.py','DaigotronStudio/DaigotronArcade_StreamlabsSystem.py')
                z.writestr('DaigotronStudio/Settings.json',json.dumps({'ConnectionFile':connection['connectionFile'],'AnnouncePlayers':False,'AnnounceResults':True},indent=2))
                z.writestr('DaigotronStudio/INSTALL.txt','Import this folder in Streamlabs Chatbot Python 2.7 Scripts. Keep SheldonTwitching Labels running. All chat messages feed the local editable chat widget; commands feed the team game. The connection file is local to this PC. Do not share that file. No credentials are included in this ZIP.')
            return self.send_bytes(200,buf.getvalue(),'application/zip','DaigotronStudio.zip')
        if path == '/assets/ST-Command-Center.png':return self.send_bytes(200,(ASSETS/'ST-Command-Center.png').read_bytes(),'image/png')
        arcade_static = {
            "/arcade/editor": ("editor.html", "text/html; charset=utf-8"),
            "/arcade/overlay": ("overlay.html", "text/html; charset=utf-8"),
            "/arcade/editor.css": ("editor.css", "text/css; charset=utf-8"),
            "/arcade/overlay.css": ("overlay.css", "text/css; charset=utf-8"),
            "/arcade/editor.js": ("editor.js", "text/javascript; charset=utf-8"),
            "/arcade/sprites.js": ("sprites.js", "text/javascript; charset=utf-8"),
            "/arcade/overlay.js": ("overlay.js", "text/javascript; charset=utf-8"),
        }
        if re.fullmatch(r"/arcade/assets/[A-Za-z0-9_-]+\.(?:png|json)", path):
            asset = ARCADE_WEB / "assets" / path.rsplit("/", 1)[1]
            if not asset.is_file():
                return self.send_json({"error": "Asset not found"}, 404)
            return self.send_bytes(200, asset.read_bytes(), "image/png" if asset.suffix == ".png" else "application/json")
        if path in arcade_static:
            filename, mimetype = arcade_static[path]
            return self.send_bytes(200, (ARCADE_WEB / filename).read_bytes(), mimetype)
        if path == "/api/arcade/config":
            return self.send_json(ARCADE_STUDIO.get())
        if path == "/api/arcade/presets":
            return self.send_json({"palettes": {**PALETTES,**ARCADE_STUDIO.get()["savedPalettes"]}, "styles": STYLE_PRESETS, "inputs": list(INPUT_FLAGS)})
        if path == "/api/arcade/live":
            global ARCADE_EVENT_POLL
            now = time.monotonic()
            with LOCK:
                if now >= ARCADE_EVENT_POLL:
                    ARCADE_EVENT_POLL = now + 0.8
                    c = ARCADE_STUDIO.get()
                    sources = c["eventFiles"]
                    project = load_project()
                    folder = project.get("folder", "")
                    # Streamlabels text updates never replace the Streamlabs.com Tip Goal.
                    event_snapshot = ({kind: (filename, safe_text(folder, filename))
                                 for kind, filename in sources.items() if filename} if folder else {})
                    # Authorized Spotify track changes can trigger the song lights.
                    if not sources.get("song") and c["eventSettings"]["song"]["enabled"]:
                        track = SPOTIFY.now_playing()
                        if track.get("playing") and track.get("title"):
                            label = (track["title"] + " — " + track.get("artist", ""))[:80]
                            event_snapshot["song"] = ("spotify:currently-playing", label)
                    ARCADE_STUDIO.observe_events(event_snapshot)
            return self.send_json(ARCADE_STUDIO.live())
        static = {
            "/preview-window": ("preview-window.html", "text/html; charset=utf-8"),
            "/preview-window.js": ("preview-window.js", "text/javascript; charset=utf-8"),
            "/preview-popout.js": ("preview-popout.js", "text/javascript; charset=utf-8"),
            "/now-playing": ("now-playing.html", "text/html; charset=utf-8"),
            "/tip-bar": ("tip-bar.html", "text/html; charset=utf-8"),
            "/streamlabs-tip-preview": ("streamlabs-tip-preview.html", "text/html; charset=utf-8"),
            "/now-playing.css": ("now-playing.css", "text/css; charset=utf-8"),
            "/now-playing.js": ("now-playing.js", "text/javascript; charset=utf-8"),
            "/tip-bar.css": ("tip-bar.css", "text/css; charset=utf-8"),
            "/tip-bar.js": ("tip-bar.js", "text/javascript; charset=utf-8"),
            "/": ("../arcade/studio.html", "text/html; charset=utf-8"),
            "/editor": ("editor.html", "text/html; charset=utf-8"),
            "/overlay": ("overlay.html", "text/html; charset=utf-8"),
            "/editor.css": ("editor.css", "text/css; charset=utf-8"),
            "/editor.js": ("editor.js", "text/javascript; charset=utf-8"),
            "/renderer.js": ("renderer.js", "text/javascript; charset=utf-8"),
            "/overlay.css": ("overlay.css", "text/css; charset=utf-8"),
        }
        if re.fullmatch(r"/assets/sf6/[a-z0-9-]+\.(?:png|webp)", path):
            asset = ASSETS / "sf6" / Path(path).name
            if asset.is_file() and asset.stat().st_size < 500000:
                media = "image/webp" if asset.suffix == ".webp" else "image/png"
                return self.send_bytes(200, asset.read_bytes(), media)
            return self.send_json({"error": "Missing icon"}, 404)
        if re.fullmatch(r"/scenes/(?:gameplay|starting|brb|ending)\.html|/scenes/scene\.(?:css|js)|/scenes/arcade-frame\.webp", path):
            scene = SCENES / Path(path).name
            media = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".webp": "image/webp"}[scene.suffix]
            if scene.is_file() and scene.stat().st_size < 2_000_000:
                return self.send_bytes(200, scene.read_bytes(), media)
            return self.send_json({"error": "Missing scene asset"}, 404)
        if path == "/roster.json":
            return self.send_bytes(200, (WEB / "roster.json").read_bytes(), "application/json; charset=utf-8")
        if path in static:
            filename, media = static[path]
            self.send_bytes(200, (WEB / filename).read_bytes(), media)
        elif path == "/streamlabs-tip-theme.css":
            self.send_bytes(200, render_streamlabs_tip_css(load_project()).encode("utf-8"), "text/css; charset=utf-8")
        elif path == "/streamlabs-tip-theme.js":
            self.send_bytes(200, render_streamlabs_tip_js(load_project()).encode("utf-8"), "text/javascript; charset=utf-8")
        elif path == "/api/export-streamlabs-tip-theme":
            self.send_bytes(200, build_streamlabs_tip_zip(load_project()), "application/zip", "SheldonTwitching-Streamlabs-Tip-Goal-Theme.zip")
        elif path == "/api/tip-bar":
            self.send_json(tip_snapshot())
        elif path == "/api/spotify/status":
            self.send_json(SPOTIFY.status())
        elif path == "/api/spotify/now-playing":
            self.send_json(SPOTIFY.now_playing())
        elif path == "/spotify/connect":
            try:
                auth_url = SPOTIFY.start_auth(self.server.server_port)
                self.send_response(302)
                self.send_header("Location", auth_url)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 400)
        elif path == "/spotify/callback":
            params = parse_qs(urlsplit(self.path).query)
            try:
                if "error" in params:
                    raise ValueError("Spotify login cancelled or rejected")
                SPOTIFY.finish_auth(params.get("state", [""])[0], params.get("code", [""])[0], self.server.server_port)
                message = "Spotify connected. Return to SheldonTwitching Labels."
            except (ValueError, OSError, HTTPError, URLError) as exc:
                message = "Spotify connection failed. Return to the editor and try again."
            self.send_bytes(200, ("<!doctype html><meta charset=utf-8><title>Spotify Connection</title><body style='background:#160824;color:white;font:24px sans-serif;padding:50px'>"+message+"</body>").encode(), "text/html; charset=utf-8")
        elif path == "/api/snapshot":
            self.send_json(snapshot())
        elif path == "/api/project":
            self.send_json(load_project())
        elif path == "/api/project/download":
            data = json.dumps(load_project(), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_bytes(200, data, "application/json; charset=utf-8", "SheldonTwitching-Labels-Project.json")
        elif path == "/api/startup":
            self.send_json(get_startup_status())
        elif path == "/api/sources":
            p = load_project()
            self.send_json({"files": folder_files(p), "folder": p.get("folder", "")})
        elif path == "/api/export":
            self.send_bytes(200, build_export_zip(load_project(), self.server.server_port), "application/zip", "SheldonTwitching-Labels-Overlay.zip")
        elif path == "/health":
            self.send_json({"ok": True, "app": "SheldonTwitching Labels"})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if not self.local_host():
            return self.send_json({"error": "Invalid host"}, 403)
        path = urlsplit(self.path).path
        origin = self.headers.get("Origin", "")
        if origin and origin not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"):
            return self.send_json({"error": "Cross-origin writes are not allowed"}, 403)
        if self.headers.get("Content-Type", "").split(";")[0].lower().strip() != "application/json":
            return self.send_json({"error": "Content type must be application/json"}, 415)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_POST:
                return self.send_json({"error": "Invalid request size"}, 413)
            data = json.loads(self.rfile.read(length))
            if path == '/api/studio/project':return self.send_json(STUDIO.save(data))
            if path == '/api/studio/bundle':
                from studio_runtime import validate as validate_studio
                if not isinstance(data,dict) or set(data)!={'schema','studio','arcade','labels'} or data['schema']!=1:raise ValueError('Unsupported Command Center project')
                studio=validate_studio(data['studio']);arcade=validate_arcade(data['arcade']);labels=validate_project(data['labels'])
                with LOCK:
                    old=(STUDIO.get(),ARCADE_STUDIO.get(),load_project())
                    try:STUDIO.save(studio);ARCADE_STUDIO.save(arcade);save_project(labels)
                    except OSError:
                        STUDIO.save(old[0]);ARCADE_STUDIO.save(old[1]);save_project(old[2]);raise
                return self.send_json({'ok':True,'studio':STUDIO.get()})
            if path == '/api/studio/action':return self.send_json(STUDIO.command(data))
            if path == '/api/studio/chat/test':
                return self.send_json(STUDIO.chat({'user':'studio-preview','name':'STUDIO TEST','text':str(data.get('text','Preview message'))[:500],'test':True}))
            if path in ('/api/chat','/api/audio','/api/admin'):
                token=STUDIO.connection(self.server.server_port)['token']
                if not hmac.compare_digest(self.headers.get('X-Arcade-Token',''),token):return self.send_json({'error':'Unauthorized local adapter'},403)
                return self.send_json(STUDIO.chat(data) if path=='/api/chat' else STUDIO.audio(data) if path=='/api/audio' else STUDIO.command(data))
            if path == "/api/arcade/config":
                self.send_json(ARCADE_STUDIO.save(data))
            elif path == "/api/arcade/action":
                if not isinstance(data, dict) or isinstance(data.get("button"), bool):
                    raise ValueError("Button index must be a number from 0 to 8")
                self.send_json(ARCADE_STUDIO.click(data.get("button")))
            elif path == "/api/arcade/learn":
                if not isinstance(data, dict):
                    raise ValueError("Visual button required")
                self.send_json(ARCADE_STUDIO.start_learn(data.get("button")))
            elif path == "/api/arcade/learn/cancel":
                self.send_json(ARCADE_STUDIO.cancel_learn())
            elif path == "/api/arcade/event":
                if not isinstance(data, dict):
                    raise ValueError("Choose an arcade event")
                self.send_json(ARCADE_STUDIO.trigger_event(data.get("kind"), data.get("text", "")))
            elif path == "/api/project":
                validate_project(data)
                with LOCK:
                    save_project(data)
                self.send_json({"ok": True})
            elif path == "/api/spotify/config":
                if not isinstance(data, dict):
                    raise ValueError("Client ID is required")
                self.send_json(SPOTIFY.configure(data.get("client_id")))
            elif path == "/api/spotify/disconnect":
                SPOTIFY.disconnect()
                self.send_json({"ok": True})
            elif path == "/api/startup":
                if not isinstance(data, dict) or not isinstance(data.get("enabled"), bool):
                    raise ValueError("Enabled must be true or false")
                self.send_json(set_startup(data["enabled"]))
            elif path == "/api/folder":
                if not isinstance(data, dict) or not isinstance(data.get("folder"), str):
                    raise ValueError("Folder path required")
                folder = Path(data["folder"]).expanduser()
                if not folder.is_dir():
                    raise ValueError("Folder does not exist")
                with LOCK:
                    project = load_project()
                    project["folder"] = str(folder.resolve())
                    save_project(project)
                self.send_json({"ok": True, "files": folder_files(project)})
            else:
                self.send_json({"error": "Not found"}, 404)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)


def make_tray(on_open, on_quit, port=APP_PORT):
    """Windows-only tray; returns an icon or None if dependencies are unavailable."""
    if sys.platform != "win32":
        return None
    try:
        import pystray
        from PIL import Image
        path = ASSETS / "ST-Command-Center.png"
        artwork = Image.open(path).convert("RGBA")
        return pystray.Icon(
            "SheldonTwitchingLabels", artwork, "SheldonTwitching - Command Center — OBS bridge running",
            menu=pystray.Menu(
                pystray.MenuItem("Open Command Center", lambda icon, item: on_open(), default=True),
                pystray.MenuItem("Open OBS preview", lambda icon, item: webbrowser.open(f"http://127.0.0.1:{port}/studio/scene")),
                pystray.MenuItem("Start with Windows", lambda icon, item: (set_startup(not get_startup_status()["enabled"]), icon.update_menu()), checked=lambda item: get_startup_status()["enabled"]),
                pystray.MenuItem("Exit — stop OBS bridge", lambda icon, item: on_quit()),
            ),
        )
    except (ImportError, OSError) as exc:
        print(f"System tray unavailable: {exc}")
        return None


def open_desktop(port):
    """Closing the design window hides it to the tray, keeping OBS alive."""
    try:
        import webview
    except ImportError:
        webbrowser.open(f"http://127.0.0.1:{port}/studio")
        print("The editor opened in your browser. Ctrl+C stops the bridge.")
        try:
            while True:
                time.sleep(30)
        except KeyboardInterrupt:
            return

    quitting = threading.Event()
    tray = None

    class NativeAPI:
        def open_preview(self, path):
            parsed = urlsplit(path) if isinstance(path, str) else None
            if not parsed or parsed.scheme or parsed.netloc or parsed.path != '/preview-window':
                return {'ok': False, 'error': 'Choose a local preview window.'}
            webview.create_window("Preview - Command Center", f"http://127.0.0.1:{port}" + path,
                                  js_api=NativeAPI(), width=1200, height=850, min_size=(480, 320),
                                  background_color="#100d20")
            return {'ok': True}

        def choose_folder(self):
            try:
                paths = window.create_file_dialog(webview.FOLDER_DIALOG)
                return paths[0] if paths else ""
            except Exception:
                return ""

    window = webview.create_window("SheldonTwitching - Command Center", f"http://127.0.0.1:{port}/studio", js_api=NativeAPI(), width=1440, height=900, min_size=(1100, 680), background_color="#13081f")

    def quit_app():
        quitting.set()
        if tray:
            try:
                tray.stop()
            except Exception:
                pass
        try:
            for preview_window in list(webview.windows):
                preview_window.destroy()
        except Exception:
            pass

    def hide_on_close():
        if quitting.is_set() or tray is None:
            return False
        window.hide()
        return True

    window.events.closing += hide_on_close
    def init_tray():
        nonlocal tray
        tray = make_tray(lambda: window.show(), quit_app, port)
        if tray:
            threading.Thread(target=tray.run, name="SheldonTwitching-Tray", daemon=True).start()

    try:
        webview.start(init_tray, debug=bool(os.environ.get("ST_LABELS_DEBUG")))
    finally:
        quitting.set()
        if tray:
            try:
                tray.stop()
            except Exception:
                pass


def headless_bridge(port):
    """Tray-only launcher for streaming without the designer window."""
    stop_event = threading.Event()
    def quit_app():
        stop_event.set()
        if tray:
            tray.stop()

    tray = make_tray(lambda: webbrowser.open(f"http://127.0.0.1:{port}/studio"), quit_app, port)
    if tray:
        tray.run()   # Stop via tray Exit; safe for Windows notification area.
    else:
        try:
            while not stop_event.wait(30):
                pass
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description="SheldonTwitching Labels local OBS overlay editor")
    parser.add_argument("--port", type=int, default=APP_PORT)
    parser.add_argument("--headless", action="store_true", help="Keep data bridge running without opening the editor")
    args = parser.parse_args()
    load_project()
    try:
        server, port = launch_bridge(args.port)
    except OSError as exc:
        message = f"Command Center could not start: {exc}. Another application may be using port {args.port}."
        print(message)
        if not args.headless and sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, "SheldonTwitching - Command Center", 0)
        return 1
    if server is None:
        if not args.headless:
            webbrowser.open(f"http://127.0.0.1:{port}/studio")
        print(f"Reusing Command Center on port {port}.")
        return 0
    args.port = port
    print(f"SheldonTwitching Labels: http://127.0.0.1:{args.port}/studio")
    print(f"OBS browser source:     http://127.0.0.1:{args.port}/overlay")
    print(f"Arcade Overlay v2 editor: http://127.0.0.1:{args.port}/arcade/editor")
    print(f"Arcade Overlay v2 OBS:    http://127.0.0.1:{args.port}/arcade/overlay")
    print(f"Spotify Now Playing:    http://127.0.0.1:{args.port}/now-playing")
    print(f"Arcade Tip Bar:         http://127.0.0.1:{args.port}/tip-bar")
    print(f"Configuration folder:  {HOME}")
    try:
        server_thread = threading.Thread(target=server.serve_forever, name="SheldonTwitching-Bridge", daemon=True)
        server_thread.start()
        if args.headless:
            headless_bridge(args.port)
        else:
            open_desktop(args.port)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
