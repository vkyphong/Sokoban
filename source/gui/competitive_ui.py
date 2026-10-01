import pygame
from .base import PlaybackScreen
from ..config import COMPETITIVE_MAP, PADDING, INK
from ..game.map_loader import MapLoader
from ..agents import mock_competitive, runner
from ..agents.agent1 import Agent1
from ..agents.agent2 import Agent2


class CompetitiveUI(PlaybackScreen):
    title = 'COMPETITIVE'

    def __init__(self, app):
        super().__init__(app)
        self.input_text = '50'
        self.focused = False
        self.demo = True
        self.initial = None
        try:
            self.initial = MapLoader.load(COMPETITIVE_MAP, competitive=True)
            self.playback.load([self.initial])
        except ValueError as exc: self.status, self.message = 'ERROR', str(exc)

    def layout(self):
        super().layout()
        self.input_rect = pygame.Rect(PADDING, 330, 237, 42)
        self.button('demo', 'GUI DEMO: ON', 387)
        self.button('start', 'START', 441)
        self.button('restart', 'RESTART', 495)
        self.button('back', 'BACK', 549)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.input_rect.collidepoint(event.pos) and not self.pending
        if event.type == pygame.KEYDOWN and self.focused and not self.pending:
            if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.action('start')
                self.focused = False
            elif event.key == pygame.K_ESCAPE: self.focused = False
            elif event.unicode and event.unicode.isprintable() and len(self.input_text) < 9:
                self.input_text += event.unicode
            return
        super().handle(event)

    def action(self, key):
        if key in ('back', 'menu'):
            self.app.show('menu')
            return
        if self.pending: return
        if key == 'demo':
            self.demo = not self.demo
            self.playback.load([self.initial]) if self.initial else None
            self.status, self.message = 'READY', ''
            self.clear_overlay()
        elif key in ('restart', 'again'):
            self.playback.restart()
            self.clear_overlay()
            self.status = 'PAUSED' if len(self.playback.states) > 1 else 'READY'
            self.message = ''
        elif key == 'start' and self.initial:
            try:
                if not self.input_text.isascii() or not self.input_text.isdecimal(): raise ValueError
                steps = int(self.input_text)
                if steps < 1: raise ValueError
            except ValueError:
                self.message = 'Maximum steps must be a positive integer.'
                return
            self.focused = False
            self.clear_overlay()
            if self.demo:
                self.submit(lambda: mock_competitive.run(self.initial, steps))
            else:
                self.submit(lambda: runner.run(self.initial, steps, Agent1(), Agent2()))

    def accept_result(self, states):
        if not states: raise ValueError('Competitive runner returned no state history.')
        from ..game.competitive_validation import validate_history
        validate_history(states, self.initial, int(self.input_text))
        self.playback.load(states)
        self.status = 'PAUSED'
        self.playback.play()

    def draw(self):
        self.buttons['demo'].label = 'GUI DEMO: ON' if self.demo else 'TEAM AGENTS'
        for key in ('demo', 'start', 'restart'):
            self.buttons[key].enabled = not self.pending and self.initial is not None
        self.draw_frame()
        hud, surface = self.app.hud, self.app.surface
        hud.text(surface, 'Maximum Steps (n)', (PADDING, 306), hud.small)
        pygame.draw.rect(surface, (255, 249, 236), self.input_rect, border_radius=8)
        pygame.draw.rect(surface, (57, 152, 173) if self.focused else (170, 146, 115), self.input_rect, 2, border_radius=8)
        hud.text(surface, self.input_text + ('|' if self.focused else ''), (self.input_rect.x + 10, self.input_rect.y + 8))
        if not self.playback.states: return
        state = self.playback.current
        status = self.playback_status('FINISHED' if state.match_finished else 'PAUSED')
        hud.lines(surface, ['GUI TEST ONLY' if self.demo else 'Teammate competitive engine',
            f'Agent 1 Completed Boxes: {state.agent1_completed}',
            f'Agent 2 Completed Boxes: {state.agent2_completed}',
            f'Step: {state.step} / {state.max_steps}', f'Status: {status}',
            'Space: Pause / Resume'], PADDING, 104, 30)
        hud.text(surface, 'Left / Right: Previous / Next', (PADDING, 284), hud.small)
        self.app.renderer.draw(surface, state, self.board_area)
        if state.match_finished and self.status not in ('READY', 'ERROR') and not self.pending:
            self.overlay(state.result, [f'Agent 1 Score: {state.agent1_completed}   Agent 2 Score: {state.agent2_completed}',
                                       f'Steps: {state.step} / {state.max_steps}'])
