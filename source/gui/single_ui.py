from .base import PlaybackScreen
from ..game.map_loader import MapLoader
from ..config import SINGLE_MAP, PADDING, HUD_WIDTH, MUTED
from ..solvers import ucs, astar


class SinglePlayerUI(PlaybackScreen):
    title = 'AI Solver'

    def __init__(self, app):
        super().__init__(app)
        self.algorithm = 'UCS'
        self.cost = 0.0
        self.initial = None
        try:
            self.initial = MapLoader.load(SINGLE_MAP)
            self.playback.load([self.initial])
        except ValueError as exc: self.status, self.message = 'ERROR', str(exc)

    def layout(self):
        super().layout()
        width = (HUD_WIDTH - 2 * PADDING - 12) // 2
        self.button('ucs', 'UCS', 138, width=width)
        self.button('astar', 'A*', 138, x=PADDING + width + 12, width=width)
        self.footer(('solve', 'SOLVE'))

    def action(self, key):
        if key in ('back', 'menu'):
            self.app.show('menu')
            return
        if self.pending: return
        if key in ('ucs', 'astar'):
            self.algorithm = 'UCS' if key == 'ucs' else 'A*'
            if self.initial: self.playback.load([self.initial])
            self.cost, self.status, self.message = 0.0, 'READY', ''
            self.clear_overlay()
        elif key == 'solve' and self.initial:
            solver = ucs if self.algorithm == 'UCS' else astar
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
        for key in ('ucs', 'astar', 'solve', 'restart'):
            self.buttons[key].enabled = not self.pending and self.initial is not None
        self.draw_frame()
        if not self.playback.states: return
        state = self.playback.current
        status = self.playback_status('SOLVED' if state.solved else 'NO SOLUTION')
        hud, surface = self.app.hud, self.app.surface
        hud.text(surface, 'ALGORITHM', (PADDING, 110), hud.small, MUTED)
        hud.stat(surface, 'ACTIONS', f'{self.playback.index} / {len(self.playback.states) - 1}',
                 (PADDING, 208, HUD_WIDTH - 2 * PADDING, 78))
        hud.stat(surface, 'TOTAL COST', f'{self.cost:g}', (PADDING, 298, HUD_WIDTH - 2 * PADDING, 78))
        hud.badge(surface, status, (PADDING + 10, 399))
        hud.text(surface, 'Space   Pause / Resume', (PADDING, 439), hud.small)
        hud.text(surface, 'Left / Right   Previous / Next', (PADDING, 464), hud.small)
        self.app.renderer.draw(surface, state, self.board_area, (self.playback.facing('player'),))
        if status == 'SOLVED':
            self.app.hud.text(self.app.surface, 'PUZZLE SOLVED!', (self.board_area.x + 20, self.board_area.y), self.app.hud.title)
