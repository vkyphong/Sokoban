import pygame
from .base import Screen
from ..game.map_loader import MapLoader
from ..game.manual_game import ManualGame
from ..config import SINGLE_MAP, PADDING, HUD_WIDTH, MUTED


class ManualUI(Screen):
    title = 'Manual Play'

    def __init__(self, app):
        super().__init__(app)
        self.game = None
        self.facing = 'down'
        try: self.game = ManualGame(MapLoader.load(SINGLE_MAP))
        except ValueError as exc: self.message = str(exc)

    def layout(self):
        super().layout()
        self.footer()

    def action(self, key):
        if key in ('restart', 'again') and self.game:
            self.game.restart()
            self.facing = 'down'
            self.clear_overlay()
        elif key == 'menu': self.app.show('menu')
        else: super().action(key)

    def handle(self, event):
        directions = {pygame.K_w: 'UP', pygame.K_UP: 'UP', pygame.K_s: 'DOWN', pygame.K_DOWN: 'DOWN',
                      pygame.K_a: 'LEFT', pygame.K_LEFT: 'LEFT', pygame.K_d: 'RIGHT', pygame.K_RIGHT: 'RIGHT'}
        if event.type == pygame.KEYDOWN and event.key in directions and self.game and not self.game.state.solved:
            action = directions[event.key]
            self.facing = action.lower()
            self.game.move(action)
        super().handle(event)

    def draw(self):
        self.draw_frame()
        if not self.game: return
        hud, surface = self.app.hud, self.app.surface
        width = (HUD_WIDTH - 2 * PADDING - 12) // 2
        hud.stat(surface, 'MOVES', self.game.moves, (PADDING, 112, width, 90))
        hud.stat(surface, 'PUSHES', self.game.pushes, (PADDING + width + 12, 112, width, 90))
        hud.text(surface, 'HOW TO PLAY', (PADDING, 247), hud.small, MUTED)
        hud.text(surface, 'WASD / Arrow Keys', (PADDING, 279))
        hud.wrapped(surface, 'Move one tile at a time. Push every crate onto a coral goal to solve the puzzle.',
                    pygame.Rect(PADDING, 318, HUD_WIDTH - 2 * PADDING, 120))
        self.app.renderer.draw(surface, self.game.state, self.board_area, (self.facing,))
        if self.game.state.solved:
            self.overlay('PUZZLE SOLVED!', [f'Moves: {self.game.moves}   Pushes: {self.game.pushes}'])
