"""Local Spotify playback reader for the user's personal OBS widget.

OAuth Authorization Code + PKCE (no client secret), loopback callback, tokens only
under ST_LABELS_HOME. Never send tokens to browser clients or embed in exports.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

AUTHORIZE = "https://accounts.spotify.com/authorize"
TOKEN = "https://accounts.spotify.com/api/token"
CURRENT = "https://api.spotify.com/v1/me/player/currently-playing"
CLIENT_ID_RE = re.compile(r"^[0-9a-zA-Z]{32}$")


class SpotifyBridge:
    def __init__(self, home: Path):
        self.home = Path(home)
        self.lock = threading.RLock()
        self.pending = None
        self.cache = {"connected": False, "playing": False, "title": "", "artist": "", "album": "", "art": "", "url": "", "state": "disconnected"}
        self.next_poll = 0.0

    def _path(self, name):
        return self.home / name

    def _read(self, name):
        try:
            return json.loads(self._path(name).read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}

    def _write(self, name, payload):
        self.home.mkdir(parents=True, exist_ok=True)
        path = self._path(name)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(payload), encoding="utf-8")
        try:
            os.chmod(temp, 0o600)
        except OSError:
            pass
        os.replace(temp, path)

    def client_id(self):
        return str(self._read("spotify_settings.json").get("client_id", ""))

    def configure(self, client_id):
        if not isinstance(client_id, str) or not CLIENT_ID_RE.fullmatch(client_id):
            raise ValueError("Enter a valid 32-character Spotify application Client ID")
        with self.lock:
            if self.client_id() != client_id:
                self.disconnect()
            self._write("spotify_settings.json", {"client_id": client_id})
        return self.status()

    def status(self):
        with self.lock:
            tokens = self._read("spotify_tokens.json")
            return {"configured": bool(self.client_id()), "connected": bool(tokens.get("refresh_token") or tokens.get("access_token")), "client_id": self.client_id(), "redirect_uri": "http://127.0.0.1:47831/spotify/callback"}

    def redirect_uri(self, port):
        return f"http://127.0.0.1:{port}/spotify/callback"

    def start_auth(self, port):
        client_id = self.client_id()
        if not client_id:
            raise ValueError("Save your Spotify app Client ID first")
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")
        state = secrets.token_urlsafe(24)
        with self.lock:
            self.pending = (state, verifier, time.monotonic() + 600, port)
        return AUTHORIZE + "?" + urlencode({"response_type": "code", "client_id": client_id, "redirect_uri": self.redirect_uri(port), "state": state, "code_challenge_method": "S256", "code_challenge": challenge, "scope": "user-read-currently-playing"})

    def _token_post(self, data):
        body = urlencode(data).encode("ascii")
        request = Request(TOKEN, data=body, headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}, method="POST")
        with urlopen(request, timeout=12) as response:
            return json.load(response)

    def finish_auth(self, state, code, port):
        with self.lock:
            pending = self.pending
            self.pending = None  # one-time only
            if not pending or not secrets.compare_digest(str(state), pending[0]) or pending[2] < time.monotonic() or pending[3] != port:
                raise ValueError("Spotify authorization expired or state did not match. Try Connect again.")
            if not code:
                raise ValueError("Spotify did not return an authorization code")
            token = self._token_post({"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri(port), "client_id": self.client_id(), "code_verifier": pending[1]})
            token["expires_at"] = time.time() + float(token.get("expires_in", 3600)) - 90
            self._write("spotify_tokens.json", token)
            self.next_poll = 0
        return True

    def disconnect(self):
        with self.lock:
            self.pending = None
            self._path("spotify_tokens.json").unlink(missing_ok=True)
            self.next_poll = 0
            self.cache = {"connected": False, "playing": False, "title": "", "artist": "", "album": "", "art": "", "url": "", "state": "disconnected"}

    def _get_access_token(self):
        tokens = self._read("spotify_tokens.json")
        if not tokens.get("access_token"):
            return None
        if float(tokens.get("expires_at", 0)) > time.time():
            return tokens["access_token"]
        if not tokens.get("refresh_token"):
            raise ValueError("Spotify login expired; reconnect your account")
        refreshed = self._token_post({"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"], "client_id": self.client_id()})
        if not refreshed.get("refresh_token"):
            refreshed["refresh_token"] = tokens["refresh_token"]
        refreshed["expires_at"] = time.time() + float(refreshed.get("expires_in", 3600)) - 90
        self._write("spotify_tokens.json", refreshed)
        return refreshed["access_token"]

    @staticmethod
    def simplify(payload):
        if not payload or not payload.get("is_playing") or not isinstance(payload.get("item"), dict):
            return {"connected": True, "playing": False, "title": "", "artist": "", "album": "", "art": "", "url": "", "state": "paused"}
        track = payload["item"]
        album = track.get("album") or {}
        images = album.get("images") or []
        art = images[0].get("url", "") if images and isinstance(images[0], dict) else ""
        # Only HTTPS album images returned by Spotify; never arbitrary URLs.
        if not (isinstance(art, str) and art.startswith("https://")):
            art = ""
        artists = track.get("artists") or []
        artist = ", ".join(a.get("name", "") for a in artists if isinstance(a, dict))
        url = (track.get("external_urls") or {}).get("spotify", "")
        if not isinstance(url, str) or not url.startswith("https://open.spotify.com/"):
            url = ""
        return {"connected": True, "playing": True, "title": str(track.get("name") or ""), "artist": artist, "album": str(album.get("name") or ""), "art": art, "url": url, "state": "playing"}

    def now_playing(self):
        with self.lock:
            if time.monotonic() < self.next_poll:
                return dict(self.cache)
            self.next_poll = time.monotonic() + 8
            try:
                token = self._get_access_token()
                if not token:
                    self.cache = {"connected": False, "playing": False, "title": "", "artist": "", "album": "", "art": "", "url": "", "state": "disconnected"}
                    return dict(self.cache)
                request = Request(CURRENT, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
                with urlopen(request, timeout=10) as response:
                    if response.status == 204:
                        self.cache = self.simplify(None)
                    else:
                        self.cache = self.simplify(json.load(response))
            except HTTPError as error:
                if error.code == 429:
                    try:
                        retry = min(300, max(10, int(error.headers.get("Retry-After", 30))))
                    except (TypeError, ValueError):
                        retry = 30
                    self.next_poll = time.monotonic() + retry
                    self.cache = {**self.cache, "state": "rate_limited"}
                elif error.code in (401, 403):
                    self.cache = {"connected": False, "playing": False, "title": "", "artist": "", "album": "", "art": "", "url": "", "state": "authorization_error"}
                else:
                    self.cache = {**self.cache, "state": "network_error"}
            except (URLError, OSError, ValueError, TimeoutError, KeyError):
                self.cache = {**self.cache, "state": "network_error"}
            return dict(self.cache)
