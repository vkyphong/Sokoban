# GUI TEST ONLY
# NOT THE REAL COMPETITIVE AI
from dataclasses import replace
from ..game.state import CompetitiveState, BoxState


def run(initial_state: CompetitiveState, max_steps: int) -> list[CompetitiveState]:
    """Fixed paired actions for the bundled map. Ownership is fixture data.

    This fixture is deliberately disjoint: no competitive strategy or general
    conflict resolver is implemented. One snapshot represents both actions.
    """
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError('Maximum steps must be a positive integer.')
    if (initial_state.agent1, initial_state.agent2) != ((2, 2), (4, 10)):
        raise ValueError('Competitive demo requires the bundled competitive map.')
    states = [replace(initial_state, max_steps=max_steps)]
    for step in range(1, min(max_steps, 7) + 1):
        distance = min(step, 6)
        boxes = (BoxState((2, 3 + distance), 1), BoxState((4, 9 - distance), 2),
                 BoxState((6, 6), None))
        state = replace(states[0], agent1=(2, 2 + distance), agent2=(4, 10 - distance),
                        boxes=boxes, agent1_completed=int(distance == 6),
                        agent2_completed=int(distance == 6), step=step,
                        finished=step == 7 or step == max_steps)
        positions = [state.agent1, state.agent2] + [b.position for b in boxes]
        if len(set(positions)) != len(positions) or any(p not in state.cells or p in state.walls for p in positions):
            raise ValueError('Competitive demo does not fit this map.')
        states.append(state)
    return states
