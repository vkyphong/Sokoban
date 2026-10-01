# Sokoban GUI / game portion

Three Pygame modes share the supplied PNG artwork, map loader, renderer,
buttons, fonts and configuration. The interface uses readable Verdana with
portable font fallbacks, statistic cards and directional player sprites.
No graded search or competitive AI algorithms are implemented.

## Launch

From this project directory:

```sh
python -m pip install -r requirements.txt
python source/main.py
```

Alternatively: `python -m source.main`. Application assets/maps resolve from
the source directory, independently of the working directory. The window is
resizable with a minimum layout of 920 x 740. Esc returns to the menu.

## Modes

- **Manual Play:** WASD/arrows move exactly one cell per key press. Collision,
  bounds, pushing, move/push counts, solved movement lock, victory overlay,
  restart and menu navigation are implemented.
- **AI Solver (Requirement 5):** choose UCS or A*, then Solve. Calls the
  corresponding teammate solver directly; the current placeholders show useful
  unavailable errors. Action count, total cost, statuses, automatic playback
  and restart are implemented. No demo toggle or scripted solution is exposed.
- **Competitive (Requirement 8):** enter a positive maximum step count, then
  Start. Calls the teammate runner directly; its current placeholder reports
  that integration is pending. Neutral/cyan/green boxes, goal variants, scores,
  paired-step playback and match results remain supported through the runner
  contract. There are no human controls for either agent and no demo toggle.

Manual movement switches among the supplied `player1_up/down/left/right`
sprites, including turning toward a blocked cell. Playback derives each
agent's facing from the history of the displayed snapshot, preserving the
last facing when stationary and restoring it correctly when rewinding.
Restart resets facing downward. Missing directional PNGs fall back to the
base player sprite with a warning.

AI playback controls: **Space** pauses/resumes; **Right** advances one
snapshot; **Left** goes back one snapshot. Stepping pauses automatic playback
and clamps to history boundaries. Competitive result overlays also allow
Left to review the match, Play Again, and Back to Menu.

## Created project tree

```text
Sokoban/
├── README.md
├── requirements.txt
├── .gitignore
├── assets/                         original supplied PNGs, unchanged
├── source/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── assets/                     original artwork plus 8 directional PNGs
│   ├── game/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── map_loader.py
│   │   ├── manual_game.py
│   │   └── competitive_validation.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── menu.py
│   │   ├── manual_ui.py
│   │   ├── single_ui.py
│   │   ├── competitive_ui.py
│   │   ├── renderer.py
│   │   ├── asset_manager.py
│   │   ├── button.py
│   │   ├── hud.py
│   │   └── playback.py
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   ├── ucs.py
│   │   ├── astar.py
│   │   └── mock_solver.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent1.py
│   │   ├── agent2.py
│   │   ├── runner.py
│   │   └── mock_competitive.py
│   └── map/
│       ├── single/example_map.txt
│       └── competitive/competitive_map.txt
├── tests/
│   ├── test_game.py
│   ├── test_ui.py
│   └── fixtures/competitive_map.txt fixed map used only by automated tests
└── artifacts/                      rendered screenshots from visual checks
```

Asset names: floor, wall, goal, box, box_on_goal, player1, player2,
box_agent1, box_agent2, box_agent1_on_goal, box_agent2_on_goal (all `.png`).
Directional assets: player1_up, player1_down, player1_left, player1_right,
player2_up, player2_down, player2_left, player2_right (all `.png`).
Missing/corrupt PNGs produce a logged warning and visible fallback, cached
just like real sprites. No new asset images were generated.

## Teammate integration contracts

All logical positions are `(row, column)`. State dataclasses are frozen;
collection inputs are copied to tuples/frozensets. `cells` records actual
map cells, including meaningful spaces, and excludes void in ragged rows.

### UCS and A*

Replace only the respective placeholder implementation:

```python
# source/solvers/ucs.py and source/solvers/astar.py
def solve(initial_state: GameState) -> SolverResult: ...

# source/solvers/interface.py
SolverResult(actions: list[str], states: list[GameState], total_cost: float)
```

Actions must be `UP`, `DOWN`, `LEFT`, `RIGHT`. The GUI validates that
`states[0] == initial_state`, `len(states) == len(actions) + 1`, each action
produces the corresponding snapshot, and cost is finite/nonnegative.
Use `SolverResult([], [], 0)` for no solution. A zero-action solved initial
state is represented by `SolverResult([], [initial_state], 0)`.
Exceptions become GUI error messages. Implementations must avoid Pygame
calls: the GUI executes them in a daemon worker and consumes results on
the main thread. Selecting an algorithm resets its
previous playback so no stale algorithm result is presented.

### Agent 1 and Agent 2

Keep their controllers independently replaceable:

```python
# source/agents/agent1.py
class Agent1:
    def choose_action(self, state: CompetitiveState) -> str: ...

# source/agents/agent2.py
class Agent2:
    def choose_action(self, state: CompetitiveState) -> str: ...
```

Return `UP`, `DOWN`, `LEFT`, `RIGHT`, or `WAIT`. Both controllers must see
the same pre-step state. These contracts contain no decision algorithm.

### Competitive game logic

Implement the dedicated integration seam:

```python
# source/agents/runner.py
def run(initial_state: CompetitiveState, max_steps: int,
        agent1: Agent1, agent2: Agent2) -> list[CompetitiveState]: ...
```

Return the initial snapshot with `step=0` and `max_steps=n`, followed by one
complete snapshot per **paired** step. Collect both agent actions, resolve
them together in the engine, then append the resulting state. Never create
separate playback steps for individual agent movements. The engine owns all
conflict resolution, box ownership and scoring rules. It must prevent agents
from passing through each other, including cell swaps.

Each `CompetitiveState` stores `agent1`, `agent2`, `boxes`, `walls`, `goals`,
`rows`, `columns`, `cells`, `agent1_completed`, `agent2_completed`, `step`,
`max_steps`, and `finished`. Each immutable `BoxState(position, owner)` has
owner `None`, `1`, or `2`. The renderer uses only this supplied ownership
and goal membership to choose sprites. Set `finished=True` for early
termination; reaching `max_steps` also ends the match. Scores determine
Agent 1 win, Agent 2 win, or draw.

Output validation rejects overlap, walls/void, agent swaps, multi-cell
agent movement, invalid owners, changes in board geometry, skipped steps,
and history continuing after termination. It does not decide actions or
resolve competitive conflicts. The runner executes off the GUI thread.

## Map format

Only assignment symbols are accepted: `%` wall, `A` agent, `B` box, `D`
goal, `C` box on goal, and space floor. CRLF is safe and meaningful spaces
are preserved. No `strip()` is applied to map rows. One `A` is required for
single player. The competitive fixture uses two `A` markers, assigned to
Agent 1 then Agent 2 in row-major order; this is a documented local extension
because the supplied format does not define a separate Agent 2 symbol.
Teammates may adapt the loader if their formulation uses separate spawn data.

## Validation and remaining work

```sh
python -m unittest discover -s tests -v
python -m compileall -q source tests
python source/main.py --frames 15
```

The test suite covers movement/push edge cases, counters, immutable snapshots,
map errors and CRLF/spaces/C, solver selection and unavailable placeholders,
no/empty solutions, playback timing/keys/bounds, competitive n validation and
n=1, ownership/score/result states, engine validation, navigation, restart,
resize, and missing/corrupt assets. Screenshots were visually inspected for
the menu, manual mode/victory, solver solved state, competitive colored crates,
and competitive result. A normal Windows desktop startup was also run.

Real UCS, A*, heuristics, experiments, competitive formulation, conflict
resolution and both decision algorithms remain teammate responsibilities.
Mocks remain fixed test fixtures, not general solvers. They are not imported
or selected by the production GUI. The competitive fixture uses the small
map in `tests/fixtures`, independently of the larger user-editable application
map. Tests inject fixtures at the teammate interfaces to verify playback.
macOS compatibility is designed through Pygame/pathlib and portable Python;
macOS 13.7.8 Intel execution has not been tested here.

The installed Pygame 2.6.1 emits a dependency deprecation warning about
`pkg_resources`; this does not prevent launching or passing the tests.
There are no known remaining GUI/game failures from the performed checks.
