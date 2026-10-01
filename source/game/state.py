from dataclasses import dataclass

Position = tuple[int, int]


@dataclass(frozen=True)
class GameState:
    player: Position
    boxes: frozenset[Position]
    walls: frozenset[Position]
    goals: frozenset[Position]
    rows: int
    columns: int
    cells: frozenset[Position]

    def __post_init__(self):
        object.__setattr__(self, 'player', tuple(self.player))
        for field in ('boxes', 'walls', 'goals', 'cells'):
            object.__setattr__(self, field, frozenset(tuple(p) for p in getattr(self, field)))

    @property
    def solved(self) -> bool:
        return bool(self.boxes) and self.boxes <= self.goals


@dataclass(frozen=True)
class BoxState:
    position: Position
    owner: int | None = None

    def __post_init__(self):
        object.__setattr__(self, 'position', tuple(self.position))
        if self.owner not in (None, 1, 2):
            raise ValueError('Box owner must be None, 1, or 2.')


@dataclass(frozen=True)
class CompetitiveState:
    agent1: Position
    agent2: Position
    boxes: tuple[BoxState, ...]
    walls: frozenset[Position]
    goals: frozenset[Position]
    rows: int
    columns: int
    cells: frozenset[Position]
    agent1_completed: int = 0
    agent2_completed: int = 0
    step: int = 0
    max_steps: int = 50
    finished: bool = False

    def __post_init__(self):
        for field in ('agent1', 'agent2'):
            object.__setattr__(self, field, tuple(getattr(self, field)))
        object.__setattr__(self, 'boxes', tuple(self.boxes))
        for field in ('walls', 'goals', 'cells'):
            object.__setattr__(self, field, frozenset(tuple(p) for p in getattr(self, field)))
        if isinstance(self.max_steps, bool) or not isinstance(self.max_steps, int) or self.max_steps <= 0:
            raise ValueError('Maximum steps must be a positive integer.')

    @property
    def match_finished(self) -> bool:
        return self.finished or self.step >= self.max_steps

    @property
    def result(self) -> str:
        if self.agent1_completed == self.agent2_completed:
            return 'DRAW!'
        return 'AGENT 1 WINS!' if self.agent1_completed > self.agent2_completed else 'AGENT 2 WINS!'
