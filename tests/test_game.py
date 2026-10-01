import unittest
from dataclasses import replace, FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

from source.config import SINGLE_MAP, COMPETITIVE_MAP
from source.game.map_loader import MapLoader, MapError
from source.game.manual_game import ManualGame, transition
from source.game.state import BoxState
from source.game.competitive_validation import validate_history
from source.gui.playback import PlaybackController
from source.solvers import ucs, astar, mock_solver
from source.solvers.interface import SolverResult
from source.agents import mock_competitive, runner
from source.agents.agent1 import Agent1
from source.agents.agent2 import Agent2


class MapTests(unittest.TestCase):
    def test_symbols_crlf_spaces_and_c(self):
        state = MapLoader.parse('%%%%%\r\n%A C%  \r\n%%%%%\r\n')
        self.assertEqual(state.columns, 7)
        self.assertIn((1, 6), state.cells)
        self.assertIn((1, 3), state.boxes & state.goals)
        self.assertNotIn((0, 6), state.cells)

    def test_errors(self):
        for text in ['', '%@BD%', '%B D%', '%AA BD%', '%AB %']:
            with self.subTest(text=text), self.assertRaises(MapError): MapLoader.parse(text)
        with self.assertRaises(MapError): MapLoader.load(Path('missing-map.txt'))
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.txt'
            path.write_bytes(b'\xff')
            with self.assertRaises(MapError): MapLoader.load(path)


class ManualTests(unittest.TestCase):
    def test_collection_inputs_are_copy_safe(self):
        original = MapLoader.load(SINGLE_MAP)
        mutable_boxes = set(original.boxes)
        state = replace(original, player=list(original.player), boxes=mutable_boxes)
        mutable_boxes.clear()
        self.assertEqual(state.boxes, original.boxes)
        self.assertIsInstance(state.player, tuple)
        competitive = MapLoader.load(COMPETITIVE_MAP, competitive=True)
        mutable_boxes = list(competitive.boxes)
        copied = replace(competitive, boxes=mutable_boxes)
        mutable_boxes.clear()
        self.assertEqual(copied.boxes, competitive.boxes)

    def test_demo_movements_counters_win_restart(self):
        initial = MapLoader.load(SINGLE_MAP)
        game = ManualGame(initial)
        self.assertTrue(game.move('LEFT'))
        self.assertFalse(game.move('LEFT'))
        self.assertEqual((game.moves, game.pushes), (1, 0))
        game.restart()
        result = mock_solver.solve(initial)
        result.validate(initial)
        for action in result.actions: self.assertTrue(game.move(action))
        self.assertTrue(game.state.solved)
        self.assertEqual((game.moves, game.pushes), (7, 2))
        self.assertFalse(game.move('UP'))
        self.assertEqual(initial.player, (2, 2))
        self.assertEqual(initial.boxes, frozenset({(2, 3), (4, 3)}))
        game.restart()
        self.assertEqual((game.moves, game.pushes), (0, 0))
        self.assertEqual(game.state, initial)
        self.assertFalse(game.state.solved)
        with self.assertRaises(FrozenInstanceError): game.state.player = (0, 0)

    def test_push_blocked_wall_and_box_and_void(self):
        for text in ['%%%%%%\n%AB% D\n%%%%%%', '%%%%%%%\n%ABBDD%\n%%%%%%%']:
            game = ManualGame(MapLoader.parse(text))
            self.assertFalse(game.move('RIGHT'))
            self.assertEqual((game.moves, game.pushes), (0, 0))
        game = ManualGame(MapLoader.parse('A BD'))
        self.assertFalse(game.move('LEFT'))
        self.assertFalse(game.move('UP'))
        self.assertFalse(game.move('DOWN'))


class PlaybackTests(unittest.TestCase):
    def test_timing_navigation_and_boundaries(self):
        p = PlaybackController(delay=0.5)
        with self.assertRaises(ValueError): p.load([])
        p.load([0, 1, 2])
        p.previous()
        self.assertEqual(p.index, 0)
        p.play()
        p.update(0.49)
        self.assertEqual(p.index, 0)
        p.update(0.01)
        self.assertEqual(p.index, 1)
        p.toggle_pause()
        p.update(20)
        self.assertEqual(p.index, 1)
        p.toggle_pause()
        p.update(0.5)
        self.assertTrue(p.finished)
        self.assertFalse(p.playing)
        p.next()
        self.assertEqual(p.index, 2)
        p.previous()
        self.assertEqual(p.current, 1)
        p.restart()
        self.assertEqual(p.index, 0)
        self.assertFalse(p.playing)

    def test_empty_and_invalid_solution(self):
        state = MapLoader.load(SINGLE_MAP)
        SolverResult([], [], 0).validate(state)
        SolverResult([], [state], 0).validate(state)
        for result in [SolverResult(['RIGHT'], [state], 1),
                       SolverResult(['RIGHT'], [state, state], 1),
                       SolverResult([], [state], float('nan'))]:
            with self.assertRaises(ValueError): result.validate(state)
        for solver in (ucs, astar):
            with self.assertRaisesRegex(NotImplementedError, 'not been integrated'): solver.solve(state)


class CompetitiveTests(unittest.TestCase):
    def setUp(self):
        self.initial = MapLoader.load(Path(__file__).parent / 'fixtures' / 'competitive_map.txt', competitive=True)

    def test_fixture_steps_ownership_scores(self):
        for limit in (1, 2, 6, 7, 50, 999999999):
            states = mock_competitive.run(self.initial, limit)
            validate_history(states, self.initial, limit)
            self.assertTrue(states[-1].match_finished)
            self.assertEqual(states[-1].step, min(limit, 7))
            self.assertEqual({b.owner for b in states[0].boxes}, {None})
            self.assertEqual({b.owner for b in states[1].boxes}, {None, 1, 2})
            if limit >= 6:
                self.assertEqual((states[6].agent1_completed, states[6].agent2_completed), (1, 1))
                self.assertTrue(all(b.position in states[6].goals for b in states[6].boxes if b.owner))
        for n in (0, -1, True, 'a'):
            with self.assertRaises(ValueError): mock_competitive.run(self.initial, n)

    def test_winners_and_placeholders(self):
        self.assertEqual(replace(self.initial, agent1_completed=2).result, 'AGENT 1 WINS!')
        self.assertEqual(replace(self.initial, agent2_completed=2).result, 'AGENT 2 WINS!')
        self.assertEqual(self.initial.result, 'DRAW!')
        for agent in (Agent1(), Agent2()):
            with self.assertRaises(NotImplementedError): agent.choose_action(self.initial)
        with self.assertRaises(NotImplementedError): runner.run(self.initial, 50, Agent1(), Agent2())

    def test_engine_invalid_overlap_swap_and_teleport(self):
        states = mock_competitive.run(self.initial, 1)
        for bad in [replace(states[1], agent1=states[1].agent2),
                    replace(states[1], agent1=states[0].agent2, agent2=states[0].agent1),
                    replace(states[1], agent1=(7, 1)), replace(states[1], step=2)]:
            with self.assertRaises(ValueError): validate_history([states[0], bad], self.initial, 1)


if __name__ == '__main__': unittest.main()
