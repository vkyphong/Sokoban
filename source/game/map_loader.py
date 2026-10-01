from pathlib import Path
from .state import GameState, CompetitiveState, BoxState, Position


class MapError(ValueError):
    """Readable map loading/validation error."""


class MapLoader:
    """Assignment symbols only. Repeated A marks the two competitive agents.

    Ragged rows are supported: absent cells are void, never traversable.
    Spaces, including trailing spaces, are meaningful floor cells.
    """

    @staticmethod
    def load(path: Path, competitive: bool = False, max_steps: int = 50):
        try:
            text = Path(path).read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as exc:
            raise MapError(f'Map could not be loaded: {path.name}: {exc}') from exc
        return MapLoader.parse(text, competitive, max_steps)

    @staticmethod
    def parse(text: str, competitive: bool = False, max_steps: int = 50):
        lines = text.splitlines()
        if not lines or not any(lines):
            raise MapError('Map is empty.')
        players: list[Position] = []
        walls, boxes, goals, cells = set(), set(), set(), set()
        for row, line in enumerate(lines):
            for column, symbol in enumerate(line):
                pos = (row, column)
                if symbol not in '%ABDC ':
                    raise MapError(f'Unknown symbol {symbol!r} at row {row + 1}, column {column + 1}.')
                cells.add(pos)
                if symbol == '%': walls.add(pos)
                if symbol == 'A': players.append(pos)
                if symbol in 'BC': boxes.add(pos)
                if symbol in 'DC': goals.add(pos)
        expected = 2 if competitive else 1
        if len(players) != expected:
            raise MapError(f'Expected {expected} A agent marker(s); found {len(players)}.')
        if not boxes or len(goals) < len(boxes):
            raise MapError('Map needs boxes and at least as many goals as boxes.')
        common = dict(walls=frozenset(walls), goals=frozenset(goals), rows=len(lines),
                      columns=max(map(len, lines)), cells=frozenset(cells))
        if competitive:
            if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
                raise MapError('Maximum steps must be a positive integer.')
            return CompetitiveState(agent1=players[0], agent2=players[1],
                                    boxes=tuple(BoxState(p) for p in sorted(boxes)),
                                    max_steps=max_steps, **common)
        return GameState(player=players[0], boxes=frozenset(boxes), **common)
