import random
import unittest
from game_engine import Arcade, MOVES, outcome


class Clock:
    now = 100
    def __call__(self):
        return self.now


class TeamTournamentTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.game = Arcade(clock=self.clock, rng=random.Random(3))

    def advance(self, seconds):
        self.clock.now += seconds
        self.game.tick()

    def phase_end(self):
        self.advance(max(0, self.game.phase_ends - self.clock()) + .01)

    def roster(self):
        self.game.join("a", "Alpha")
        self.game.join("b", "Beta")
        self.game.set_team("a", 0)
        self.game.set_team("b", 1)
        self.game.start_ballot()

    def hit(self, winner=0, next_ballot=True):
        self.assertEqual(self.game.phase, "choose")
        self.game.action("a", "jump" if winner == 0 else "fireball")
        self.game.action("b", "fireball" if winner == 0 else "jump")
        self.phase_end()
        self.assertEqual(self.game.phase, "reveal")
        self.advance(1)
        self.phase_end()
        self.assertEqual(self.game.phase, "result")
        if next_ballot:
            self.phase_end()

    def test_attack_cycle_and_block_draws(self):
        for a, b in [("jump", "fireball"), ("dragonpunch", "jump"), ("fireball", "dragonpunch")]:
            self.assertEqual(outcome(a,b),0)
            self.assertEqual(outcome(b,a),1)
        for move in MOVES:
            self.assertIsNone(outcome(move,move))
            self.assertIsNone(outcome(move,"block"))

    def test_auto_balance_new_viewers(self):
        for i in range(31):
            self.game.join(str(i),str(i))
            a,b=self.game.team_counts()
            self.assertLessEqual(abs(a-b),1)

    def test_one_vote_per_viewer_replace_not_spam(self):
        self.roster()
        for _ in range(10):
            self.game.action("a","fireball")
        self.game.action("a","jump")
        self.assertEqual(self.game.tally_moves(0),[0,1,0,0])

    def test_switch_is_deferred_and_cannot_vote_both_sides(self):
        self.roster()
        self.game.action("a","fireball")
        self.game.set_team("a",1)
        self.game.action("a","jump")
        self.assertEqual(self.game.members["a"]["team"],0)
        self.assertEqual(self.game.tally_moves(0),[0,1,0,0])
        self.assertEqual(self.game.tally_moves(1),[0,0,0,0])
        self.game.start_ballot()
        self.assertEqual(self.game.members["a"]["team"],1)
        self.assertEqual(len(self.game.votes),0)

    def test_team_majority_selects_move_and_hides_counts_until_reveal(self):
        self.roster()
        self.game.join("c","Gamma")
        self.game.join("d","Delta")
        self.game.members["c"]["team"]=0
        self.game.members["d"]["team"]=0
        self.game.action("a","fireball")
        self.game.action("c","jump")
        self.game.action("d","jump")
        self.assertIsNone(self.game.snapshot()["teams"][0]["moveCounts"])
        self.phase_end()
        self.assertEqual(self.game.choices[0],"jump")
        self.assertIsNotNone(self.game.snapshot()["teams"][0]["moveCounts"])

    def test_tied_ballot_selects_only_tied_leaders(self):
        self.roster()
        self.game.join("c","Gamma")
        self.game.members["c"]["team"]=0
        self.game.action("a","fireball")
        self.game.action("c","jump")
        self.assertIn(self.game.leading_move(0),("fireball","jump"))

    def test_three_hits_needed_for_knockout(self):
        self.roster()
        self.hit(next_ballot=False)
        self.assertEqual(self.game.players[1]["hits"],1)
        self.assertEqual(self.game.players[1]["hp"],67)
        self.assertFalse(self.game.players[1]["defeated"])
        self.assertEqual(self.game.round_wins,[0,0])
        self.phase_end()
        self.hit()
        self.assertEqual(self.game.players[1]["hits"],2)
        self.assertFalse(self.game.players[1]["defeated"])
        self.hit(next_ballot=False)
        self.assertEqual(self.game.players[1]["hp"],0)
        self.assertTrue(self.game.players[1]["defeated"])
        self.assertEqual(self.game.round_wins,[1,0])
        self.phase_end()
        self.assertEqual(self.game.round_index,2)
        self.assertTrue(all(p["hits"]==0 for p in self.game.players))

    def test_two_rounds_win_a_match(self):
        self.roster()
        for _ in range(6):
            self.hit()
        self.assertEqual(self.game.match_wins,[1,0])
        self.assertEqual(self.game.round_wins,[0,0])
        self.assertEqual(self.game.match_index,2)

    def test_split_rounds_require_deciding_third_round(self):
        self.roster()
        for winner in [0]*3+[1]*3:
            self.hit(winner)
        self.assertEqual(self.game.round_wins,[1,1])
        self.assertEqual(self.game.round_index,3)
        self.assertEqual(self.game.match_wins,[0,0])
        for _ in range(3):
            self.hit(1)
        self.assertEqual(self.game.match_wins,[0,1])

    def test_best_of_five_can_reach_deciding_fifth_match(self):
        self.roster()
        # Keep members eligible during a long deterministic simulated tournament.
        for winner in [0,1,0,1]:
            for _ in range(6):
                self.game.members["a"]["seen"]=self.clock()
                self.game.members["b"]["seen"]=self.clock()
                self.hit(winner)
        self.assertEqual(self.game.match_wins,[2,2])
        self.assertEqual(self.game.match_index,5)
        self.assertFalse(self.game.locked)

    def test_three_matches_lock_only_winning_teams_palette(self):
        self.roster()
        self.game.palette_votes={"a":2,"b":3}
        for index in range(18):
            self.game.members["a"]["seen"]=self.clock()
            self.game.members["b"]["seen"]=self.clock()
            self.hit(next_ballot=index!=17)
        self.assertEqual(self.game.match_wins,[3,0])
        self.assertTrue(self.game.locked)
        self.assertEqual(self.game.series_winner,0)
        self.assertEqual(self.game.palette,2)
        self.assertFalse(self.game.command("b","Beta","!palette 4"))
        self.phase_end()
        self.assertEqual(self.game.match_wins,[0,0])
        self.assertEqual(self.game.series_index,2)
        self.assertEqual(self.game.phase,"choose")
        self.assertEqual(self.game.palette,2)

    def test_draw_does_not_damage_or_score(self):
        self.roster()
        self.game.action("a","block")
        self.game.action("b","fireball")
        self.phase_end()
        self.phase_end()
        self.assertTrue(all(p["hits"]==0 for p in self.game.players))
        self.assertEqual(self.game.round_wins,[0,0])
        self.assertIn("DRAW",self.game.result)

    def test_no_votes_defaults_to_block_on_populated_team(self):
        self.roster()
        self.phase_end()
        self.assertEqual(self.game.choices,{0:"block",1:"block"})

    def test_empty_team_cpu_waits_for_ballot_then_picks_randomly(self):
        self.game.command("a","Alpha","!join")
        team=self.game.members["a"]["team"]
        self.game.action("a","jump")
        self.phase_end()
        self.assertEqual(self.game.phase,"bot_choose")
        self.assertNotIn(1-team,self.game.choices)
        self.phase_end()
        self.assertEqual(self.game.phase,"reveal")
        self.assertIn(self.game.choices[1-team],MOVES)

    def test_no_audience_waits_instead_of_running_two_bots(self):
        self.phase_end()
        self.assertEqual(self.game.phase,"entry")
        self.assertEqual(self.game.round,0)

    def test_result_event_once_per_exchange(self):
        self.roster()
        self.hit(next_ballot=False)
        reports=[e for e in self.game.events if e["kind"]=="round_result"]
        self.assertEqual(len(reports),1)
        self.assertIn("1/3 hits",reports[0]["text"])
        self.advance(.1)
        self.assertEqual(len([e for e in self.game.events if e["kind"]=="round_result"]),1)

    def test_palette_vote_and_countdown_do_not_interrupt_ballot(self):
        self.roster()
        self.game.command("a","Alpha","!palette 3")
        self.assertEqual(self.game.palette_counts(0),[0,0,1,0])
        self.assertEqual(self.game.phase,"choose")
        self.clock.now=self.game.ends+1
        self.assertEqual(self.game.snapshot()["remaining"],0)
        self.assertFalse(self.game.locked)

    def test_stale_audio_goes_dark(self):
        self.game.audio={"level":.9,"bass":.8,"treble":.5}
        self.game.audio_at=self.clock()
        self.advance(2)
        self.assertFalse(self.game.snapshot()["audioConnected"])


if __name__=="__main__":
    unittest.main()
