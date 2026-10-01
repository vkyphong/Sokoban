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
FONT_SIZE, HUD_WIDTH, PADDING = 22, 285, 24
BG = (247, 236, 213)
INK = (65, 49, 40)
MUTED = (127, 105, 85)
ACCENT = (57, 152, 173)
