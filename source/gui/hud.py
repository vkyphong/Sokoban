import pygame
from ..config import INK, MUTED, PANEL, ACCENT


class HUD:
    def __init__(self):
        # Prefer regular readable faces; avoid platform font-name aliases that
        # can accidentally select a condensed or light variant.
        family = 'verdana,dejavusans,liberationsans'
        self.font = pygame.font.SysFont(family, 18)
        self.small = pygame.font.SysFont(family, 13)
        self.title = pygame.font.SysFont(family, 25, bold=True)
        self.hero = pygame.font.SysFont(family, 60, bold=True)
        self.number = pygame.font.SysFont(family, 30, bold=True)

    def stat(self, surface, label, value, rect, color=INK):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surface, PANEL, rect, border_radius=14)
        self.text(surface, label, (rect.x + 16, rect.y + 12), self.small, MUTED)
        self.text(surface, str(value), (rect.x + 16, rect.y + 32), self.number, color)

    def badge(self, surface, label, position):
        color = (180, 75, 63) if label in ('ERROR', 'NO SOLUTION') else ACCENT
        rendered = self.small.render(label, True, color)
        rect = rendered.get_rect(topleft=position).inflate(20, 12)
        pygame.draw.rect(surface, PANEL, rect, border_radius=9)
        surface.blit(rendered, rendered.get_rect(center=rect.center))

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
