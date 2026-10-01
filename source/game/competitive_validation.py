from .state import CompetitiveState


def validate_history(states: list[CompetitiveState], initial: CompetitiveState, max_steps: int):
    """Reject invalid engine histories, including overlap and agents swapping.

    This validates engine output; it does not choose or resolve actions.
    """
    if not states or states[0].step != 0:
        raise ValueError('Competitive history must begin at step zero.')
    first = states[0]
    if (first.agent1, first.agent2, first.boxes) != (initial.agent1, initial.agent2, initial.boxes):
        raise ValueError('Competitive history must begin at the supplied initial state.')
    for index, state in enumerate(states):
        if state.step != index or state.step > max_steps or state.max_steps != max_steps:
            raise ValueError('Competitive history must contain one snapshot per paired step within n.')
        if (state.cells, state.walls, state.goals, state.rows, state.columns) != (
                initial.cells, initial.walls, initial.goals, initial.rows, initial.columns):
            raise ValueError('Competitive board geometry cannot change during playback.')
        positions = [state.agent1, state.agent2] + [b.position for b in state.boxes]
        if len(set(positions)) != len(positions) or any(p not in state.cells or p in state.walls for p in positions):
            raise ValueError('Competitive snapshot contains overlapping or blocked entities.')
        if any(b.owner not in (None, 1, 2) for b in state.boxes):
            raise ValueError('Box owner must be None, 1, or 2.')
        if min(state.agent1_completed, state.agent2_completed) < 0:
            raise ValueError('Completed-box counts cannot be negative.')
        if index:
            previous = states[index - 1]
            if previous.match_finished:
                raise ValueError('Competitive history continues after match completion.')
            if (state.agent1, state.agent2) == (previous.agent2, previous.agent1):
                raise ValueError('Agents cannot pass through each other by swapping cells.')
            for old, new in [(previous.agent1, state.agent1), (previous.agent2, state.agent2)]:
                if abs(old[0] - new[0]) + abs(old[1] - new[1]) > 1:
                    raise ValueError('Each agent can move at most one grid cell per paired step.')
    if not states[-1].match_finished:
        raise ValueError('Competitive history must end with finished=True or at the step limit.')
