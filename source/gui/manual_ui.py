import pygame
from .base import Screen
from ..game.map_loader import MapLoader
from ..game.manual_game import ManualGame
from ..config import SINGLE_MAP, PADDING


class ManualUI(Screen):
    title = 'MANUAL PLAY'

    def __init__(self, app):
        super().__init__(app)
        self.game = None
        try: self.game = ManualGame(MapLoader.load(SINGLE_MAP))
        except ValueError as exc: self.message = str(exc)

    def layout(self):
        super().layout()
        self.button('restart', 'RESTART', 460)
        self.button('back', 'BACK', 514)

    def action(self, key):
        if key in ('restart', 'again') and self.game:
            self.game.restart()
            self.clear_overlay()
        elif key == 'menu': self.app.show('menu')
        else: super().action(key)

    def handle(self, event):
        directions = {pygame.K_w: 'UP', pygame.K_UP: 'UP', pygame.K_s: 'DOWN', pygame.K_DOWN: 'DOWN',
                      pygame.K_a: 'LEFT', pygame.K_LEFT: 'LEFT', pygame.K_d: 'RIGHT', pygame.K_RIGHT: 'RIGHT'}
        if event.type == pygame.KEYDOWN and event.key in directions and self.game:
            self.game.move(directions[event.key])
        super().handle(event)

    def draw(self):
        self.draw_frame()
        if not self.game: return
        hud, surface = self.app.hud, self.app.surface
        hud.lines(surface, [f'Moves: {self.game.moves}', f'Pushes: {self.game.pushes}', '',
                            'WASD / Arrow Keys', 'Move one cell per press', '', 'Push all crates onto goals.'], PADDING, 112)
        self.app.renderer.draw(surface, self.game.state, self.board_area)
        if self.game.state.solved:
            self.overlay('PUZZLE SOLVED!', [f'Moves: {self.game.moves}   Pushes: {self.game.pushes}'])
