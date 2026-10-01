from dataclasses import replace
from .state import GameState

DIRECTIONS = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}


def transition(state: GameState, action: str) -> tuple[GameState, bool]:
    """Apply one legal movement; return unchanged state if blocked, and push flag."""
    dr, dc = DIRECTIONS[action]
    target = (state.player[0] + dr, state.player[1] + dc)
    if target not in state.cells or target in state.walls:
        return state, False
    boxes = state.boxes
    pushed = target in boxes
    if pushed:
        beyond = (target[0] + dr, target[1] + dc)
        if beyond not in state.cells or beyond in state.walls or beyond in boxes:
            return state, False
        boxes = frozenset((boxes - {target}) | {beyond})
    return replace(state, player=target, boxes=boxes), pushed


class ManualGame:
    def __init__(self, initial_state: GameState):
        self.initial_state = initial_state
        self.restart()

    def restart(self):
        self.state = self.initial_state
        self.moves = self.pushes = 0

    def move(self, action: str) -> bool:
        if self.state.solved:
            return False
        state, pushed = transition(self.state, action)
        if state == self.state:
            return False
        self.state = state
        self.moves += 1
        self.pushes += int(pushed)
        return True
