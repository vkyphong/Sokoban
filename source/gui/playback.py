from typing import Generic, TypeVar, Sequence
from ..config import PLAYBACK_DELAY

T = TypeVar('T')


class PlaybackController(Generic[T]):
    """Snapshot navigation and delta-time playback with clamped boundaries."""
    def __init__(self, delay: float = PLAYBACK_DELAY):
        if delay <= 0:
            raise ValueError('Playback delay must be positive.')
        self.delay = delay
        self.states: tuple[T, ...] = ()
        self.index = 0
        self.playing = False
        self.elapsed = 0.0

    def load(self, states: Sequence[T]):
        if not states:
            raise ValueError('Playback needs at least one state.')
        self.states = tuple(states)
        self.restart()

    @property
    def current(self) -> T:
        return self.states[self.index]

    @property
    def finished(self) -> bool:
        return bool(self.states) and self.index == len(self.states) - 1

    def restart(self):
        self.index = 0
        self.pause()

    def play(self):
        self.playing = bool(self.states) and not self.finished

    def pause(self):
        self.playing = False
        self.elapsed = 0.0

    def toggle_pause(self):
        self.pause() if self.playing else self.play()

    def next(self):
        self.pause()
        self.index = min(self.index + 1, max(0, len(self.states) - 1))

    def previous(self):
        self.pause()
        self.index = max(0, self.index - 1)

    def update(self, dt: float):
        if not self.playing:
            return
        self.elapsed += max(0, dt)
        while self.elapsed >= self.delay and not self.finished:
            self.elapsed -= self.delay
            self.index += 1
        if self.finished:
            self.pause()

    def facing(self, attribute: str) -> str:
        """Facing of the displayed snapshot, independent of navigation order.

        Preserve the last movement direction across WAIT/stationary steps.
        Rewinding restores that historical facing rather than reversing it.
        """
        directions = {(-1, 0): 'up', (1, 0): 'down', (0, -1): 'left', (0, 1): 'right'}
        for index in range(self.index, 0, -1):
            before = getattr(self.states[index - 1], attribute)
            after = getattr(self.states[index], attribute)
            delta = (after[0] - before[0], after[1] - before[1])
            if delta in directions:
                return directions[delta]
        return 'down'
