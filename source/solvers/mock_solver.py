# GUI TEST ONLY
# THIS IS NOT UCS OR A*
from ..game.manual_game import transition
from ..game.state import GameState
from .interface import SolverResult


def solve(initial_state: GameState) -> SolverResult:
    """Replay a fixed script for the bundled example; perform no search."""
    actions = ['LEFT', 'RIGHT', 'RIGHT', 'DOWN', 'LEFT', 'DOWN', 'RIGHT']
    states = [initial_state]
    for action in actions:
        state, _ = transition(states[-1], action)
        if state == states[-1]:
            raise ValueError('Demo script does not fit this map. Integrate a real solver for custom maps.')
        states.append(state)
    if not states[-1].solved:
        raise ValueError('Demo script only supports the bundled example map.')
    return SolverResult(actions, states, float(len(actions)))
