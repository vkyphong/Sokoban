from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / 'assets'
SINGLE_MAP = ROOT / 'map' / 'single' / 'example_map.txt'
COMPETITIVE_MAP = ROOT / 'map' / 'competitive' / 'competitive_map.txt'
WINDOW_WIDTH, WINDOW_HEIGHT = 1120, 780
FPS = 60
DEFAULT_TILE_SIZE, MIN_TILE_SIZE = 64, 32
TILE_SIZES = (64, 48, 40, 32)
PLAYBACK_DELAY = 0.45
FONT_SIZE, HUD_WIDTH, PADDING = 18, 320, 24
BG = (248, 241, 228)
INK = (61, 49, 42)
MUTED = (133, 117, 100)
ACCENT = (44, 140, 164)
PANEL = (255, 251, 242)
SIDEBAR = (237, 222, 198)
