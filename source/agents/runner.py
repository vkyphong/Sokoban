from ..game.state import CompetitiveState
from .agent1 import Agent1
from .agent2 import Agent2


def run(initial_state: CompetitiveState, max_steps: int,
        agent1: Agent1, agent2: Agent2) -> list[CompetitiveState]:
    """Integration seam: resolve BOTH actions together into ONE snapshot per step.

    The teammate engine owns collisions (including swaps/crossing), ownership,
    scores and termination. Both choose_action calls receive the same state.
    """
    raise NotImplementedError('Competitive game engine has not been integrated yet.')
