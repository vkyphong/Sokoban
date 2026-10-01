from .base import PlaybackScreen
from ..game.map_loader import MapLoader
from ..config import SINGLE_MAP, PADDING
from ..solvers import ucs, astar, mock_solver


class SinglePlayerUI(PlaybackScreen):
    title = 'AI SOLVER'

    def __init__(self, app):
        super().__init__(app)
        self.algorithm = 'UCS'
        self.demo = True
        self.cost = 0.0
        self.initial = None
        try:
            self.initial = MapLoader.load(SINGLE_MAP)
            self.playback.load([self.initial])
        except ValueError as exc: self.status, self.message = 'ERROR', str(exc)

    def layout(self):
        super().layout()
        self.button('ucs', 'UCS', 325, width=112)
        self.button('astar', 'A*', 325, x=149, width=112)
        self.button('demo', 'GUI DEMO: ON' if self.demo else 'TEAM SOLVER', 379)
        self.button('solve', 'SOLVE', 433)
        self.button('restart', 'RESTART', 487)
        self.button('back', 'BACK', 541)

    def action(self, key):
        if key in ('back', 'menu'):
            self.app.show('menu')
            return
        if self.pending: return
        if key in ('ucs', 'astar', 'demo'):
            if key == 'demo': self.demo = not self.demo
            else: self.algorithm = 'UCS' if key == 'ucs' else 'A*'
            if self.initial: self.playback.load([self.initial])
            self.cost, self.status, self.message = 0.0, 'READY', ''
            self.clear_overlay()
        elif key == 'solve' and self.initial:
            solver = mock_solver if self.demo else ucs if self.algorithm == 'UCS' else astar
            self.submit(lambda: solver.solve(self.initial))
        elif key in ('restart', 'again'):
            self.playback.restart()
            self.clear_overlay()
            self.status = 'READY' if len(self.playback.states) == 1 else 'PAUSED'
            self.message = ''

    def accept_result(self, result):
        result.validate(self.initial)
        if not result.states:
            self.playback.load([self.initial])
            self.status, self.message = 'NO SOLUTION', 'Solver returned no solution.'
            self.cost = 0
            return
        self.playback.load(result.states)
        self.cost = result.total_cost
        self.status = 'PAUSED'
        self.playback.play()

    def draw(self):
        self.buttons['ucs'].selected = self.algorithm == 'UCS'
        self.buttons['astar'].selected = self.algorithm == 'A*'
        self.buttons['demo'].label = 'GUI DEMO: ON' if self.demo else 'TEAM SOLVER'
        for key in ('ucs', 'astar', 'demo', 'solve', 'restart'):
            self.buttons[key].enabled = not self.pending and self.initial is not None
        self.draw_frame()
        if not self.playback.states: return
        state = self.playback.current
        status = self.playback_status('SOLVED' if state.solved else 'NO SOLUTION')
        self.app.hud.lines(self.app.surface, [f'Algorithm: {self.algorithm}',
            'GUI TEST ONLY' if self.demo else 'Teammate solver',
            f'Actions: {self.playback.index} / {len(self.playback.states) - 1}',
            f'Total Cost: {self.cost:g}', f'Status: {status}', '',
            'Space: Pause / Resume'], PADDING, 102, 28)
        self.app.hud.text(self.app.surface, 'Left / Right: Previous / Next', (PADDING, 298), self.app.hud.small)
        self.app.renderer.draw(self.app.surface, state, self.board_area)
        if status == 'SOLVED':
            self.app.hud.text(self.app.surface, 'PUZZLE SOLVED!', (self.board_area.x + 20, self.board_area.y), self.app.hud.title)
