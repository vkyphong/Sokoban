import pygame
from ..config import TILE_SIZES, PADDING
from ..game.state import GameState, CompetitiveState
from .asset_manager import AssetManager


class SokobanRenderer:
    def __init__(self, assets: AssetManager):
        self.assets = assets
        self.tile_size = 64
        self.origin = (0, 0)

    def grid_to_pixel(self, position: tuple[int, int]) -> tuple[int, int]:
        row, column = position
        return self.origin[0] + column * self.tile_size, self.origin[1] + row * self.tile_size

    def draw(self, surface: pygame.Surface, state: GameState | CompetitiveState,
             area: pygame.Rect, facings: tuple[str, ...] = ('down', 'down')):
        fit = max(1, min((area.width - PADDING) // state.columns, (area.height - PADDING) // state.rows))
        self.tile_size = next((size for size in TILE_SIZES if size <= fit), fit)
        width, height = state.columns * self.tile_size, state.rows * self.tile_size
        self.origin = (area.centerx - width // 2, area.centery - height // 2)
        board = pygame.Rect(*self.origin, width, height)
        pygame.draw.rect(surface, (213, 189, 150), board.inflate(12, 12), border_radius=10)

        def tile(name, position):
            surface.blit(self.assets.get(name, self.tile_size), self.grid_to_pixel(position))

        # Required layer order: floor, goals, walls, boxes, agents.
        for pos in sorted(state.cells): tile('floor', pos)
        for pos in sorted(state.goals): tile('goal', pos)
        for pos in sorted(state.walls): tile('wall', pos)
        if isinstance(state, GameState):
            for pos in sorted(state.boxes): tile('box_on_goal' if pos in state.goals else 'box', pos)
            tile(f'player1_{facings[0]}', state.player)
        else:
            for box in state.boxes:
                name = 'box' if box.owner is None else f'box_agent{box.owner}'
                tile(name + ('_on_goal' if box.position in state.goals else ''), box.position)
            tile(f'player1_{facings[0]}', state.agent1)
            tile(f'player2_{facings[1]}', state.agent2)
