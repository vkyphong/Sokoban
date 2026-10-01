import pygame
from .base import PlaybackScreen
from ..config import COMPETITIVE_MAP, PADDING, HUD_WIDTH, MUTED, ACCENT
from ..game.map_loader import MapLoader
from ..agents import runner
from ..agents.agent1 import Agent1
from ..agents.agent2 import Agent2


class CompetitiveUI(PlaybackScreen):
    title = 'Competitive'

    def __init__(self, app):
        super().__init__(app)
        self.input_text = '50'
        self.focused = False
        self.initial = None
        try:
            self.initial = MapLoader.load(COMPETITIVE_MAP, competitive=True)
            self.playback.load([self.initial])
        except ValueError as exc: self.status, self.message = 'ERROR', str(exc)

    def layout(self):
        super().layout()
        self.input_rect = pygame.Rect(PADDING, 405, HUD_WIDTH - 2 * PADDING, 42)
        self.footer(('start', 'START'))

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
        if key in ('restart', 'again'):
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
            self.submit(lambda: runner.run(self.initial, steps, Agent1(), Agent2()))

    def accept_result(self, states):
        if not states: raise ValueError('Competitive runner returned no state history.')
        from ..game.competitive_validation import validate_history
        validate_history(states, self.initial, int(self.input_text))
        self.playback.load(states)
        self.status = 'PAUSED'
        self.playback.play()

    def draw(self):
        for key in ('start', 'restart'):
            self.buttons[key].enabled = not self.pending and self.initial is not None
        self.draw_frame()
        hud, surface = self.app.hud, self.app.surface
        hud.text(surface, 'MAXIMUM STEPS (n)', (PADDING, 381), hud.small, MUTED)
        pygame.draw.rect(surface, (255, 249, 236), self.input_rect, border_radius=8)
        pygame.draw.rect(surface, (57, 152, 173) if self.focused else (170, 146, 115), self.input_rect, 2, border_radius=8)
        hud.text(surface, self.input_text + ('|' if self.focused else ''), (self.input_rect.x + 10, self.input_rect.y + 8))
        if not self.playback.states: return
        state = self.playback.current
        status = self.playback_status('FINISHED' if state.match_finished else 'PAUSED')
        width = HUD_WIDTH - 2 * PADDING
        hud.stat(surface, 'AGENT 1 / COMPLETED BOXES', state.agent1_completed, (PADDING, 108, width, 76), ACCENT)
        hud.stat(surface, 'AGENT 2 / COMPLETED BOXES', state.agent2_completed, (PADDING, 196, width, 76), (69, 143, 77))
        hud.stat(surface, 'STEP', f'{state.step} / {state.max_steps}', (PADDING, 284, width, 76))
        hud.badge(surface, status, (PADDING + 10, 468))
        hud.text(surface, 'Space   Pause / Resume', (PADDING, 500), hud.small)
        hud.text(surface, 'Left / Right   Previous / Next', (PADDING, 525), hud.small)
        self.app.renderer.draw(surface, state, self.board_area,
                               (self.playback.facing('agent1'), self.playback.facing('agent2')))
        if state.match_finished and self.status not in ('READY', 'ERROR') and not self.pending:
            self.overlay(state.result, [f'Agent 1 Score: {state.agent1_completed}',
                                       f'Agent 2 Score: {state.agent2_completed}',
                                       f'Steps: {state.step} / {state.max_steps}'])
