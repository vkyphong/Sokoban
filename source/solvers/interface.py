from dataclasses import dataclass
from math import isfinite
from ..game.state import GameState
from ..game.manual_game import transition, DIRECTIONS


@dataclass
class SolverResult:
    actions: list[str]
    states: list[GameState]
    total_cost: float

    def validate(self, initial_state: GameState):
        if not self.states:
            if self.actions:
                raise ValueError('Solution actions require state snapshots.')
            return
        if len(self.states) != len(self.actions) + 1 or self.states[0] != initial_state:
            raise ValueError('Solver history must start at initial state with one snapshot per action.')
        if not isfinite(self.total_cost) or self.total_cost < 0:
            raise ValueError('Solver cost must be finite and nonnegative.')
        for index, action in enumerate(self.actions):
            if action not in DIRECTIONS:
                raise ValueError(f'Unknown solver action: {action!r}.')
            expected, _ = transition(self.states[index], action)
            if expected == self.states[index] or expected != self.states[index + 1]:
                raise ValueError(f'Invalid solver state after action {index + 1}.')
