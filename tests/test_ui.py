import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import time
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pygame

from source.main import Application
from source.gui.asset_manager import AssetManager
from source.gui.button import Button
from source.config import COMPETITIVE_MAP
from source.game.map_loader import MapLoader
from source.solvers.interface import SolverResult
from source.agents.mock_competitive import run
from source.solvers.mock_solver import solve


class UITests(unittest.TestCase):
    def setUp(self):
        # Keep fixed mock histories independent of user-edited production maps.
        fixture = Path(__file__).parent / 'fixtures' / 'competitive_map.txt'
        patcher = patch('source.gui.competitive_ui.COMPETITIVE_MAP', fixture)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.app = Application()

    def tearDown(self): pygame.quit()

    def key(self, key, unicode=''):
        self.app.process(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode))

    def click(self, key):
        self.app.screen.draw()
        button = self.app.screen.buttons[key]
        self.app.process(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center))

    def finish_job(self):
        deadline = time.monotonic() + 3
        while self.app.screen.pending and time.monotonic() < deadline:
            self.app.screen.update(0)
            time.sleep(0.005)
        self.assertFalse(self.app.screen.pending)
        self.app.screen.draw()

    def test_navigation_manual_win_overlay_restart(self):
        self.click('manual')
        for key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_d, pygame.K_s,
                    pygame.K_a, pygame.K_DOWN, pygame.K_RIGHT): self.key(key)
        self.app.screen.draw()
        self.assertTrue(self.app.screen.game.state.solved)
        self.assertIn('again', self.app.screen.buttons)
        self.click('again')
        self.assertEqual(self.app.screen.game.moves, 0)
        self.assertNotIn('again', self.app.screen.buttons)
        self.click('back')
        self.click('single')
        self.click('back')
        self.click('competitive')
        self.click('back')
        self.click('exit')
        self.assertFalse(self.app.running)

    def test_solver_selection_real_interface_keyboard_and_empty(self):
        self.app.show('single')
        screen = self.app.screen
        self.click('astar')
        self.assertEqual(screen.algorithm, 'A*')
        self.assertNotIn('demo', screen.buttons)
        self.click('solve')
        self.finish_job()
        self.assertEqual(screen.status, 'ERROR')
        self.assertIn('A* solver', screen.message)
        self.click('ucs')
        self.click('solve')
        self.finish_job()
        self.assertIn('UCS solver', screen.message)
        # Inject fixture only in tests; production GUI calls the real interface.
        with patch('source.gui.single_ui.ucs.solve', side_effect=solve):
            self.click('solve')
            self.finish_job()
        self.assertTrue(screen.playback.playing)
        self.key(pygame.K_SPACE)
        self.assertFalse(screen.playback.playing)
        self.key(pygame.K_RIGHT)
        self.assertEqual(screen.playback.index, 1)
        self.key(pygame.K_LEFT)
        self.assertEqual(screen.playback.current, screen.initial)
        self.key(pygame.K_LEFT)
        self.assertEqual(screen.playback.index, 0)
        self.key(pygame.K_SPACE)
        screen.update(10)
        screen.draw()
        self.assertTrue(screen.playback.current.solved)
        self.assertEqual(screen.playback_status('SOLVED'), 'SOLVED')
        self.key(pygame.K_RIGHT)
        self.assertEqual(screen.playback.index, 7)
        self.click('restart')
        self.assertEqual(screen.playback.index, 0)
        screen.accept_result(SolverResult([], [], 0))
        self.assertEqual(screen.status, 'NO SOLUTION')
        screen.accept_result(SolverResult([], [screen.initial], 0))
        self.assertFalse(screen.playback.playing)
        self.assertEqual(screen.playback_status('NO SOLUTION'), 'NO SOLUTION')

    @patch('source.gui.competitive_ui.runner.run', side_effect=lambda s, n, a, b: run(s, n))
    def test_competitive_validation_playback_finish_and_results(self, mocked_runner):
        self.app.show('competitive')
        screen = self.app.screen
        self.assertNotIn('demo', screen.buttons)
        for text in ('', '0', '-1', 'abc', '1.5', ' '):
            screen.input_text = text
            self.click('start')
            self.assertIn('positive integer', screen.message)
            self.assertFalse(screen.pending)
        screen.input_text = '1'
        self.click('start')
        self.finish_job()
        screen.update(1)
        screen.draw()
        self.assertTrue(screen.playback.current.match_finished)
        self.assertIn('again', screen.buttons)
        self.key(pygame.K_LEFT)
        screen.draw()
        self.assertEqual(screen.playback.current.step, 0)
        self.assertNotIn('again', screen.buttons)
        self.key(pygame.K_RIGHT)
        screen.draw()
        self.click('again')
        self.key(pygame.K_SPACE)
        self.assertEqual(screen.playback_status('FINISHED'), 'PLAYING')
        screen.input_text = '50'
        self.click('start')
        self.finish_job()
        self.key(pygame.K_SPACE)
        self.key(pygame.K_RIGHT)
        self.assertEqual(screen.playback.current.step, 1)
        self.key(pygame.K_LEFT)
        self.assertEqual(screen.playback.current.step, 0)
        self.key(pygame.K_SPACE)
        screen.update(10)
        screen.draw()
        self.assertEqual(screen.playback.current.result, 'DRAW!')
        for scores in [(2, 1), (1, 2), (1, 1)]:
            state = replace(screen.playback.current, agent1_completed=scores[0], agent2_completed=scores[1])
            screen.playback.load([state])
            screen.draw()
            self.assertIn('menu', screen.buttons)
        self.click('menu')
        self.assertEqual(type(self.app.screen).__name__, 'MainMenu')

    def test_competitive_engine_unavailable_and_input_events(self):
        self.app.show('competitive')
        screen = self.app.screen
        self.app.process(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=screen.input_rect.center))
        self.key(pygame.K_BACKSPACE)
        self.assertEqual(screen.input_text, '5')
        self.key(pygame.K_1, '1')
        self.assertEqual(screen.input_text, '51')
        screen.focused = False
        self.click('start')
        self.finish_job()
        self.assertEqual(screen.status, 'ERROR')
        self.assertIn('engine has not been integrated', screen.message)

    def test_assets_cache_missing_corrupt_and_render_resize(self):
        with TemporaryDirectory() as directory:
            assets = AssetManager(Path(directory))
            with self.assertLogs(level='WARNING'):
                first = assets.get('player1', 48)
            self.assertIs(first, assets.get('player1', 48))
            (Path(directory) / 'wall.png').write_bytes(b'broken')
            with self.assertLogs(level='WARNING'): assets.get('wall', 64)
        for name in ('manual', 'single', 'competitive'):
            self.app.show(name)
            self.app.screen.draw()
            self.assertEqual(self.app.renderer.tile_size, 64 if name != 'competitive' else 48)
        self.app.process(pygame.event.Event(pygame.VIDEORESIZE, w=920, h=740))
        self.app.screen.draw()
        self.assertEqual(self.app.renderer.tile_size, 40)
        button = Button('disabled', (0, 0, 100, 50), enabled=False)
        self.assertFalse(button.clicked(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))))

    def test_missing_maps(self):
        with patch('source.gui.manual_ui.SINGLE_MAP', Path('missing.txt')):
            self.app.show('manual')
            self.app.screen.draw()
            self.assertIn('Map could not be loaded', self.app.screen.message)
        with patch('source.gui.single_ui.SINGLE_MAP', Path('missing.txt')):
            self.app.show('single')
            self.app.screen.draw()
            self.assertEqual(self.app.screen.status, 'ERROR')
        with patch('source.gui.competitive_ui.COMPETITIVE_MAP', Path('missing.txt')):
            self.app.show('competitive')
            self.app.screen.draw()
            self.assertEqual(self.app.screen.status, 'ERROR')

    def test_directional_sprites_manual_and_historical_playback(self):
        self.app.show('manual')
        screen = self.app.screen
        for key, facing in [(pygame.K_UP, 'up'), (pygame.K_LEFT, 'left'),
                            (pygame.K_DOWN, 'down'), (pygame.K_RIGHT, 'right')]:
            self.key(key)
            screen.draw()
            self.assertEqual(screen.facing, facing)
            self.assertIn((f'player1_{facing}', self.app.renderer.tile_size), self.app.assets.scaled)
        self.click('restart')
        self.assertEqual(screen.facing, 'down')
        self.app.show('single')
        screen = self.app.screen
        screen.accept_result(solve(screen.initial))
        self.assertEqual(screen.playback.facing('player'), 'down')
        self.key(pygame.K_RIGHT)
        self.assertEqual(screen.playback.facing('player'), 'left')
        self.key(pygame.K_RIGHT)
        self.assertEqual(screen.playback.facing('player'), 'right')
        self.key(pygame.K_LEFT)
        self.assertEqual(screen.playback.facing('player'), 'left')
        self.app.show('competitive')
        screen = self.app.screen
        screen.accept_result(run(screen.initial, 50))
        for _ in range(7): self.key(pygame.K_RIGHT)
        screen.draw()
        self.assertEqual(screen.playback.facing('agent1'), 'right')
        self.assertEqual(screen.playback.facing('agent2'), 'left')
        self.assertIn(('player2_left', self.app.renderer.tile_size), self.app.assets.scaled)

    def test_user_competitive_map_fits_display(self):
        state = MapLoader.load(COMPETITIVE_MAP, competitive=True)
        self.app.show('competitive')
        self.app.renderer.draw(self.app.surface, state, self.app.screen.board_area)
        size = self.app.renderer.tile_size
        x, y = self.app.renderer.origin
        area = self.app.screen.board_area
        self.assertGreaterEqual(x, area.left)
        self.assertGreaterEqual(y, area.top)
        self.assertLessEqual(x + state.columns * size, area.right)
        self.assertLessEqual(y + state.rows * size, area.bottom)


if __name__ == '__main__': unittest.main()
