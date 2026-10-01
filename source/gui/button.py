import pygame
from ..config import INK, ACCENT


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
        color = (209, 204, 192) if not self.enabled else ACCENT if self.selected else (
            (235, 188, 111) if hover else (231, 204, 160))
        pygame.draw.rect(surface, (196, 168, 128), self.rect.move(0, 3), border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        label = font.render(self.label, True, (255, 255, 255) if self.selected else INK)
        surface.blit(label, label.get_rect(center=self.rect.center))
