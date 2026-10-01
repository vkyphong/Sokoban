import logging
from pathlib import Path
import pygame
from ..config import ASSET_DIR


class AssetManager:
    """Load PNGs once and cache each requested square size."""
    def __init__(self, directory: Path = ASSET_DIR):
        self.directory = directory
        self.originals: dict[str, pygame.Surface] = {}
        self.scaled: dict[tuple[str, int], pygame.Surface] = {}

    def get(self, name: str, size: int) -> pygame.Surface:
        key = (name, size)
        if key not in self.scaled:
            if name not in self.originals:
                try:
                    self.originals[name] = pygame.image.load(str(self.directory / f'{name}.png')).convert_alpha()
                except (OSError, pygame.error) as exc:
                    logging.warning('Asset %s: %s; using visible debugging fallback.', name, exc)
                    if name.startswith(('player1_', 'player2_')):
                        # Directional artwork is optional: reuse the original
                        # player rather than replace it with a colored square.
                        self.originals[name] = self.get(name.split('_')[0], 64)
                        self.scaled[key] = pygame.transform.smoothscale(self.originals[name], (size, size))
                        return self.scaled[key]
                    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
                    colors = {'floor': (237, 212, 165), 'wall': (158, 109, 59),
                              'player1': (55, 181, 226), 'player2': (76, 170, 84)}
                    color = colors.get(name, (64, 167, 204) if 'agent1' in name else
                                       (75, 164, 85) if 'agent2' in name else (206, 133, 61))
                    surface.fill(color)
                    pygame.draw.rect(surface, (80, 55, 40), surface.get_rect(), 3)
                    if 'goal' in name or name == 'goal':
                        pygame.draw.circle(surface, (215, 75, 68), (32, 32), 15, 4)
                    self.originals[name] = surface
            self.scaled[key] = pygame.transform.smoothscale(self.originals[name], (size, size))
        return self.scaled[key]
