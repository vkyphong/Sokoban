"""Run with python -m source.main or python source/main.py from any directory."""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = 'source'

import pygame
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from .gui.asset_manager import AssetManager
from .gui.renderer import SokobanRenderer
from .gui.hud import HUD
from .gui.menu import MainMenu
from .gui.manual_ui import ManualUI
from .gui.single_ui import SinglePlayerUI
from .gui.competitive_ui import CompetitiveUI


class Application:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Sokoban | Manual - AI Solver - Competitive')
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.renderer = SokobanRenderer(self.assets)
        self.hud = HUD()
        self.running = True
        self.show('menu')

    def show(self, name: str):
        screens = {'menu': MainMenu, 'manual': ManualUI, 'single': SinglePlayerUI, 'competitive': CompetitiveUI}
        self.screen = screens[name](self)
        self.screen.layout()

    def process(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.surface = pygame.display.set_mode((max(920, event.w), max(740, event.h)), pygame.RESIZABLE)
            self.screen.layout()
        else:
            self.screen.handle(event)

    def run(self, frames: int | None = None):
        count = 0
        try:
            while self.running and (frames is None or count < frames):
                dt = self.clock.tick(FPS) / 1000.0
                for event in pygame.event.get(): self.process(event)
                self.screen.update(dt)
                self.screen.draw()
                pygame.display.flip()
                count += 1
        finally:
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description='Sokoban GUI with teammate integration interfaces.')
    parser.add_argument('--frames', type=int, help='Exit after N frames (startup smoke test).')
    args = parser.parse_args()
    Application().run(args.frames)


if __name__ == '__main__':
    main()
