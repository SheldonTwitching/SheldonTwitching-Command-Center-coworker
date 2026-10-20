"""Two-team chat tournament: three hits, best of three rounds, best of five matches."""
import math
import random
import time
import uuid
from collections import deque

PALETTES = [
    {"name": "MAGENTA", "color": "#ff31c8", "accent": "#45d9ff", "hue": 0},
    {"name": "CYAN", "color": "#39dfff", "accent": "#597bff", "hue": 250},
    {"name": "EMBER", "color": "#ff6b46", "accent": "#ffd65c", "hue": 65},
    {"name": "VENOM", "color": "#6fff93", "accent": "#b273ff", "hue": 190},
]
MOVES = ("fireball", "jump", "dragonpunch", "block")
BEATS = {"jump": "fireball", "dragonpunch": "jump", "fireball": "dragonpunch"}
MOVE_NAMES = {"fireball": "fireball", "jump": "jump attack", "dragonpunch": "dragon punch", "block": "block"}
BOT_ID = "__daigotron9000__"


def outcome(left, right):
    if left == right or "block" in (left, right):
        return None
    return 0 if BEATS[left] == right else 1


class Arcade:
    def __init__(self, clock=time.monotonic, rng=None, countdown=600, vote_seconds=None):
        self.clock, self.rng = clock, rng or random.Random()
        self.countdown_seconds = countdown
        self.events, self.seq = deque(maxlen=100), 0
        self.reset()

    def emit(self, kind, **details):
        self.seq += 1
        self.events.append(dict(id=self.seq, kind=kind, **details))

    def reset(self):
        now = self.clock()
        self.session = uuid.uuid4().hex
        self.ends = now + self.countdown_seconds
        self.members, self.pending_teams, self.votes = {}, {}, {}
        self.palette_votes, self.choices = {}, {}
        self.palette, self.locked, self.series_winner = 0, False, None
        self.round_wins, self.match_wins = [0, 0], [0, 0]
        self.round_index, self.match_index, self.series_index = 1, 1, 1
        self.round, self.completed = 0, 0
        self.phase, self.phase_ends = "entry", now + 2
        self.reveal_at, self.winner, self.result = 0, None, ""
        self.impact_applied, self.scored = False, False
        self.next_kind, self.demo = "exchange", False
        self.demo_next = now
        self.audio = {"bass": 0, "level": 0, "treble": 0}
        self.audio_at, self.chat_at = -999, -999
        self.events.clear()
        self.players = [self.fighter(0), self.fighter(1)]
        self.emit("reset")

    def fighter(self, team):
        return dict(user="team-%s" % team, name="TEAM %s" % (team + 1), team=team,
                    hp=100, hits=0, action="idle", bot=False, hit_at=None, defeated=False)

    def team_counts(self):
        return [sum(p["team"] == i for p in self.members.values()) for i in range(2)]

    def join(self, user, name):
        if user == BOT_ID or (user not in self.members and len(self.members) >= 1000):
            return False
        if user not in self.members:
            counts = self.team_counts()
            team = self.rng.choice([i for i in range(2) if counts[i] == min(counts)])
            self.members[user] = {"name": name[:22], "team": team, "seen": self.clock()}
        self.members[user]["seen"] = self.clock()
        counts = self.team_counts()
        for i, p in enumerate(self.players):
            p["bot"] = counts[i] == 0
            p["name"] = "TEAM %s%s" % (i + 1, " / CPU" if not counts[i] else "")
        return True

    def set_team(self, user, team):
        if user not in self.members or team not in (0, 1):
            return False
        if self.phase in ("choose", "bot_choose", "reveal", "result"):
            self.pending_teams[user] = team
        else:
            self.members[user]["team"] = team
        return True

    def start_ballot(self):
        now = self.clock()
        self.members = {u: p for u, p in self.members.items() if now - p["seen"] < 180}
        for user, team in self.pending_teams.items():
            if user in self.members:
                self.members[user]["team"] = team
        self.pending_teams.clear()
        if not self.members:
            self.phase, self.phase_ends = "entry", now + 2
            return
        self.votes, self.choices = {}, {}
        self.round += 1
        self.winner, self.result, self.scored = None, "", False
        counts = self.team_counts()
        for i, p in enumerate(self.players):
            p["action"], p["bot"] = "idle", counts[i] == 0
            p["name"] = "TEAM %s%s" % (i + 1, " / DAIGOTRON9000" if not counts[i] else "")
        self.phase, self.phase_ends = "choose", now + (2.5 if self.demo else 8)
        self.emit("callout", number=self.round, text="Team 1 vs Team 2: vote !fireball, !jump, !dragonpunch or !block. !team 1 / !team 2 to join a side.")

    def action(self, user, move):
        if self.phase != "choose" or self.clock() >= self.phase_ends or move not in MOVES or user not in self.members:
            return False
        # One active vote per viewer. Later commands replace that viewer's vote.
        self.votes[user] = {"team": self.members[user]["team"], "move": move}
        return True

    def tally_moves(self, team):
        return [sum(v["team"] == team and v["move"] == m for v in self.votes.values()) for m in MOVES]

    def leading_move(self, team):
        counts = self.tally_moves(team)
        best = max(counts)
        return self.rng.choice([m for m, n in zip(MOVES, counts) if n == best]) if best else "block"

    def close_ballot(self):
        counts = self.team_counts()
        self.choices = {i: self.leading_move(i) for i in range(2) if counts[i]}
        if len(self.choices) < 2:
            self.phase, self.phase_ends = "bot_choose", self.clock() + 1.25
            self.emit("bot_thinking")
        else:
            self.resolve()

    def resolve(self):
        if self.phase not in ("choose", "bot_choose"):
            return
        for i, p in enumerate(self.players):
            p["action"] = self.choices.get(i, "block")
        self.winner = outcome(*(p["action"] for p in self.players))
        self.phase, self.reveal_at, self.phase_ends = "reveal", self.clock(), self.clock() + 2
        self.impact_applied = False
        for i, p in enumerate(self.players):
            self.emit("action", player=i, action=p["action"])

    def score_exchange(self):
        if self.scored:
            return
        self.scored = True
        a, b = self.players
        self.next_kind = "exchange"
        if self.winner is None:
            blocked = "block" in (a["action"], b["action"])
            self.result = "BLOCKED / DRAW" if blocked else "SAME MOVE / DRAW"
            report = "Team 1 chose %s; Team 2 chose %s. %s" % (MOVE_NAMES[a["action"]], MOVE_NAMES[b["action"]], self.result)
        else:
            w, loser = self.winner, 1 - self.winner
            report = "Team %s's %s beats Team %s's %s." % (w + 1, MOVE_NAMES[self.players[w]["action"]], loser + 1, MOVE_NAMES[self.players[loser]["action"]])
            if self.players[loser]["hits"] >= 3:
                self.round_wins[w] += 1
                self.completed += 1
                self.result = "TEAM %s WINS ROUND" % (w + 1)
                self.next_kind = "round"
                report += " KO! Team %s wins the round (%s-%s)." % (w + 1, *self.round_wins)
                self.emit("ko", result=self.result)
                if self.round_wins[w] >= 2:
                    self.match_wins[w] += 1
                    self.result = "TEAM %s WINS MATCH" % (w + 1)
                    self.next_kind = "match"
                    report += " Match won! Series score %s-%s." % tuple(self.match_wins)
                    if self.match_wins[w] >= 3:
                        self.next_kind = "series"
                        self.result = "TEAM %s WINS SERIES" % (w + 1)
                        if not self.locked:
                            self.palette = self.preferred_palette(w, final=True)
                            self.locked, self.series_winner = True, w
                            report += " Team %s wins the cabinet: %s!" % (w + 1, PALETTES[self.palette]["name"])
                            self.emit("palette", palette=self.palette, team=w)
                        else:
                            report += " Team %s wins the exhibition series!" % (w + 1)
            else:
                self.result = "TEAM %s LANDS A HIT" % (w + 1)
                report += " Team %s: %s/3 hits taken." % (loser + 1, self.players[loser]["hits"])
        self.emit("round_result", number=self.round, text=report)
        self.phase = "result"
        self.phase_ends = self.clock() + (4 if self.next_kind == "series" else 2.5 if self.next_kind != "exchange" else 1)

    def advance_exchange(self):
        if self.next_kind == "series":
            self.series_index += 1
            self.match_index, self.round_index = 1, 1
            self.match_wins, self.round_wins = [0, 0], [0, 0]
        elif self.next_kind == "match":
            self.match_index += 1
            self.round_index, self.round_wins = 1, [0, 0]
        elif self.next_kind == "round":
            self.round_index += 1
        if self.next_kind != "exchange":
            self.players = [self.fighter(0), self.fighter(1)]
        self.start_ballot()

    def palette_counts(self, team):
        return [sum(self.members.get(u, {}).get("team") == team and vote == i for u, vote in self.palette_votes.items()) for i in range(4)]

    def preferred_palette(self, team, final=False):
        counts = self.palette_counts(team)
        if not max(counts):
            return team
        leaders = [i for i, n in enumerate(counts) if n == max(counts)]
        return self.rng.choice(leaders) if final else leaders[0]

    def counts(self):
        return [sum(self.palette_counts(team)[i] for team in range(2)) for i in range(4)]

    def command(self, user, name, text):
        self.tick()
        parts = text.lower().strip().split()
        if not parts or parts[0] not in ("!join", "!team", "!palette", "!fireball", "!jump", "!dragonpunch", "!block"):
            return False
        if parts[0] == "!team" and (len(parts) != 2 or parts[1] not in ("1", "2")):
            return False
        if parts[0] == "!palette" and (self.locked or len(parts) != 2 or parts[1] not in ("1", "2", "3", "4")):
            return False
        self.chat_at = self.clock()
        if not self.join(user, name):
            return False
        if parts[0] == "!team":
            accepted = len(parts) == 2 and parts[1] in ("1", "2") and self.set_team(user, int(parts[1]) - 1)
            if self.phase == "entry":
                self.start_ballot()
            return accepted
        if self.phase == "entry":
            self.start_ballot()
        if parts[0] == "!join":
            return True
        if parts[0] == "!palette":
            if self.locked or len(parts) != 2 or parts[1] not in ("1", "2", "3", "4"):
                return False
            self.palette_votes[user] = int(parts[1]) - 1
            return True
        return self.action(user, parts[0][1:])

    def set_demo(self, enabled):
        self.reset()
        self.demo = bool(enabled)
        if self.demo:
            for i in range(6):
                self.join("demo-%s" % i, "DEMO %s" % i)
            self.start_ballot()

    def tick(self):
        now = self.clock()
        if self.demo:
            for p in self.members.values():
                p["seen"] = now
            if self.phase == "choose" and now >= self.demo_next:
                self.demo_next = now + .6
                for user in self.members:
                    self.action(user, self.rng.choice(MOVES))
        if self.phase == "reveal" and not self.impact_applied and now >= self.reveal_at + .95:
            self.impact_applied = True
            if self.winner is not None:
                loser = 1 - self.winner
                p = self.players[loser]
                p["hits"] += 1
                p["hp"] = max(0, round(100 * (3 - p["hits"]) / 3))
                p["hit_at"], p["defeated"] = self.reveal_at + .95, p["hits"] >= 3
                self.emit("hit", player=loser, lethal=p["defeated"])
        if now < self.phase_ends:
            return
        if self.phase == "entry":
            self.start_ballot()
        elif self.phase == "choose":
            self.close_ballot()
        elif self.phase == "bot_choose":
            for i in range(2):
                if i not in self.choices:
                    self.choices[i] = self.rng.choice(MOVES)
            self.resolve()
        elif self.phase == "reveal":
            self.score_exchange()
        elif self.phase == "result":
            self.advance_exchange()

    def snapshot(self):
        now = self.clock()
        def visible(p):
            elapsed = now - p["hit_at"] if p.get("hit_at") is not None else -1
            if p.get("defeated") and 0 <= elapsed < 3.5:
                animation = ("hitstop" if elapsed < .1 else "hit" if elapsed < .32 else "falling" if elapsed < .7 else
                             "defeated" if elapsed < 2.5 else "rising" if elapsed < 3.05 else "recover")
            else:
                animation = "hit" if 0 <= elapsed < .24 else "recover" if .24 <= elapsed < .75 else "idle"
            return dict(p, ready=p["team"] in self.choices, hitElapsed=elapsed, animationState=animation)
        players = [visible(p) for p in self.players]
        revealing = self.phase in ("reveal", "result")
        counts = self.team_counts()
        return {
            "session": self.session, "remaining": max(0, math.ceil(self.ends - now)), "voteRemaining": 0,
            "locked": self.locked, "palette": self.palette, "palettes": PALETTES, "votes": self.counts(),
            "players": players, "displayPlayers": players, "queue": len(self.members), "round": self.round, "completed": self.completed,
            "phase": self.phase, "phaseRemaining": max(0, math.ceil(self.phase_ends - now)),
            "revealElapsed": max(0, now - self.reveal_at) if revealing else 0,
            "roundRemaining": max(0, math.ceil(self.phase_ends - now)),
            "result": self.result if revealing else "", "winner": self.winner if revealing else None,
            "teams": [{"name": "TEAM %s" % (i + 1), "members": counts[i], "palette": self.palette if self.locked and i == self.series_winner else self.preferred_palette(i),
                       "paletteVotes": self.palette_counts(i), "moveVotes": sum(self.tally_moves(i)),
                       "moveCounts": self.tally_moves(i) if revealing else None} for i in range(2)],
            "roundWins": self.round_wins, "matchWins": self.match_wins, "roundIndex": self.round_index,
            "matchIndex": self.match_index, "seriesIndex": self.series_index, "seriesWinner": self.series_winner,
            "pendingTeamSwitches": len(self.pending_teams),
            "nextKind": self.next_kind,
            "demo": self.demo, "audio": self.audio if now - self.audio_at < 1 else {"bass": 0, "level": 0, "treble": 0},
            "audioConnected": now - self.audio_at < 1, "chatConnected": now - self.chat_at < 30, "events": list(self.events),
        }
