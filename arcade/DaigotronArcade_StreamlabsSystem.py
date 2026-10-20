# -*- coding: utf-8 -*-
"""Streamlabs Chatbot adapter (Python 2.7 / IronPython compatible).
Python 2.7.13 script loader adapter; forwards inputs and announces round results.
"""
import os
import json
import time
import codecs
from collections import deque

ScriptName = "Daigotron9000 Arcade"
Website = "https://www.twitch.tv/SheldonTwitching"
Description = "Team move/color voting, team assignment replies and arcade tournament result reports."
Creator = "SheldonTwitching"
Version = "0.4.0"
COMMANDS = set(["!join", "!team", "!fireball", "!jump", "!dragonpunch", "!block", "!palette"])
pending = deque(maxlen=128)
connection_file = ""
last_send = 0
last_error = 0
last_poll = 0
announce_players = False
announce_results = True
last_callout = None
connection_token = None
last_session = None


def Init():
    global connection_file, announce_players, announce_results, last_callout, connection_token, last_session
    folder = os.path.dirname(__file__)
    settings = os.path.join(folder, "Settings.json")
    with codecs.open(settings, "r", "utf-8-sig") as handle:
        settings_data = json.load(handle)
        connection_file = settings_data["ConnectionFile"]
        announce_players = bool(settings_data.get("AnnouncePlayers", False))
        announce_results = bool(settings_data.get("AnnounceResults", True))
    last_callout = None
    connection_token = None
    last_session = None
    pending.clear()


def Execute(data):
    if not data.IsChatMessage():
        return
    pending.append({"user": data.User, "name": data.UserName, "text": data.Message})


def Tick():
    global last_send, last_error, last_poll, last_callout, connection_token, last_session
    now = time.time()
    if now - last_send < 0.1 or (not pending and (not (announce_players or announce_results) or now - last_poll < .75)):
        return
    last_send = now
    try:
        with codecs.open(connection_file, "r", "utf-8-sig") as handle:
            config = json.load(handle)
        if config["token"] != connection_token:
            connection_token, last_callout = config["token"], None
        if pending:
            payload = pending.popleft()
            response = json.loads(Parent.PostRequest(
                config["url"] + "/api/chat",
                {"X-Arcade-Token": config["token"], "Content-Type": "application/json"},
                json.dumps(payload), True))
            if int(response.get("status", 0)) != 200:
                raise ValueError("Overlay unavailable")
            receipt = json.loads(response.get("response", "{}"))
            command = payload["text"].lower().split()[0]
            if receipt.get("accepted") and (receipt.get("newMember") or command in ("!team", "!join")):
                team = receipt.get("pendingTeam") or receipt.get("team")
                if team:
                    message = "@%s: TEAM %s%s" % (payload["name"], team, " from the next ballot." if receipt.get("pendingTeam") else ".")
                    Parent.SendStreamMessage(message)
        if (announce_players or announce_results) and now - last_poll >= .75:
            last_poll = now
            response = json.loads(Parent.GetRequest(config["url"] + "/api/state", {}))
            if int(response.get("status", 0)) != 200:
                raise ValueError("Overlay unavailable")
            state = json.loads(response["response"])
            events = state.get("events", [])
            if state.get("session") != last_session:
                last_callout, last_session = None, state.get("session")
            newest = max([event["id"] for event in events] + [0])
            if last_callout is not None and newest < last_callout:
                last_callout = None
            if last_callout is not None and not state.get("demo", False):
                for event in events:
                    if event["id"] <= last_callout:
                        continue
                    # Consume before sending so a failed call cannot repeat an old result.
                    last_callout = event["id"]
                    current = event.get("number") == state.get("round")
                    callout = announce_players and event["kind"] == "callout" and state.get("phase") == "choose"
                    result = announce_results and event["kind"] == "round_result"
                    if current and (callout or result):
                        Parent.SendStreamMessage(event["text"])
            # Skip historical announcements when the adapter first connects.
            last_callout = max([event["id"] for event in events] + [last_callout or 0])
    except Exception:
        # Do not replay old attacks after reconnecting, or spam chatbot logs.
        if now - last_error > 30:
            Parent.Log(ScriptName, "Arcade host unavailable. Start the local overlay server and check Settings.json.")
            last_error = now


def Unload():
    pending.clear()


def ScriptToggled(state):
    global last_callout, last_session
    last_callout, last_session = None, None
    pending.clear()
