import pygame
from ..config import INK, ACCENT, PANEL


class Button:
    def __init__(self, label: str, rect, enabled: bool = True):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.enabled = enabled
        self.selected = False

    def clicked(self, event: pygame.event.Event) -> bool:
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

    def draw(self, surface, font):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        primary = self.selected or self.label in ('SOLVE', 'START', 'PLAY AGAIN', 'MANUAL PLAY')
        color = (219, 214, 202) if not self.enabled else (
            (35, 121, 144) if hover else ACCENT) if primary else (
            (249, 228, 189) if hover else PANEL)
        pygame.draw.rect(surface, (207, 188, 162), self.rect.move(0, 3), border_radius=12)
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        label = font.render(self.label, True, (255, 255, 255) if primary and self.enabled else INK)
        surface.blit(label, label.get_rect(center=self.rect.center))
