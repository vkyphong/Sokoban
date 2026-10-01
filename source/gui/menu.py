import pygame
from .base import Screen
from .button import Button
from ..config import BG, MUTED


class MainMenu(Screen):
    def layout(self):
        width, height = self.app.surface.get_size()
        self.buttons = {key: Button(label, (width // 2 - 155, height // 2 - 20 + i * 64, 310, 48))
                        for i, (key, label) in enumerate([
                            ('manual', 'MANUAL PLAY'), ('single', 'AI SOLVER'),
                            ('competitive', 'COMPETITIVE'), ('exit', 'EXIT')])}

    def action(self, key):
        if key == 'exit': self.app.running = False
        else: self.app.show(key)

    def draw(self):
        surface, hud = self.app.surface, self.app.hud
        surface.fill(BG)
        width, height = surface.get_size()
        pygame.draw.circle(surface, (240, 219, 178), (width // 2, height // 2 - 85), 230)
        for name, x in [('player1', width // 2 - 185), ('player2', width // 2 + 60)]:
            surface.blit(self.app.assets.get(name, 125), (x, height // 2 - 230))
        title = hud.hero.render('SOKOBAN', True, (65, 49, 40))
        surface.blit(title, title.get_rect(center=(width // 2, height // 2 - 72)))
        for button in self.buttons.values(): button.draw(surface, hud.font)
        label = hud.small.render('Push. Plan. Compete.  |  AI modes include labeled GUI demos.', True, MUTED)
        surface.blit(label, label.get_rect(center=(width // 2, height - 40)))
