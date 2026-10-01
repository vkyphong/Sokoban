import pygame
from ..config import INK, MUTED


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont('arial', 20)
        self.small = pygame.font.SysFont('arial', 16)
        self.title = pygame.font.SysFont('arial', 32, bold=True)
        self.hero = pygame.font.SysFont('arial', 64, bold=True)

    def text(self, surface, text: str, position, font=None, color=INK):
        surface.blit((font or self.font).render(text, True, color), position)

    def lines(self, surface, lines, x, y, gap=30):
        for line in lines:
            self.text(surface, line, (x, y))
            y += gap

    def wrapped(self, surface, text, rect, color=MUTED):
        x, y = rect.topleft
        line = ''
        for word in text.split():
            trial = f'{line} {word}'.lstrip()
            if self.small.size(trial)[0] > rect.width and line:
                self.text(surface, line, (x, y), self.small, color)
                y += 21
                line = word
            else:
                line = trial
        self.text(surface, line, (x, y), self.small, color)
