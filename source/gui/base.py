import threading
from queue import Queue, Empty
import pygame
from ..config import BG, HUD_WIDTH, PADDING, INK
from .button import Button
from .playback import PlaybackController


class Screen:
    title = ''

    def __init__(self, app):
        self.app = app
        self.buttons: dict[str, Button] = {}
        self.message = ''

    def layout(self):
        width, height = self.app.surface.get_size()
        self.board_area = pygame.Rect(HUD_WIDTH + PADDING, 95, width - HUD_WIDTH - 2 * PADDING, height - 135)
        self.buttons = {}

    def button(self, key, label, y, x=PADDING, width=HUD_WIDTH - 2 * PADDING):
        self.buttons[key] = Button(label, (x, y, width, 42))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.show('menu')
            return
        for key, button in self.buttons.items():
            if button.clicked(event):
                self.action(key)
                break

    def action(self, key):
        if key == 'back': self.app.show('menu')

    def update(self, dt):
        pass

    def draw_frame(self):
        surface, hud = self.app.surface, self.app.hud
        surface.fill(BG)
        pygame.draw.rect(surface, (242, 223, 191), (0, 0, HUD_WIDTH, surface.get_height()))
        hud.text(surface, self.title, (PADDING, 25), hud.title)
        hud.text(surface, 'SOKOBAN  /  CARTOON PUZZLE LAB', (HUD_WIDTH + PADDING, 38), hud.small)
        for button in self.buttons.values(): button.draw(surface, hud.font)
        hud.wrapped(surface, self.message, pygame.Rect(PADDING, 594, HUD_WIDTH - 2 * PADDING, 120))

    def overlay(self, title, lines):
        surface, hud = self.app.surface, self.app.hud
        shade = pygame.Surface(self.board_area.size, pygame.SRCALPHA)
        shade.fill((49, 36, 25, 170))
        surface.blit(shade, self.board_area)
        card = pygame.Rect(0, 0, min(500, self.board_area.width - 20), 260)
        card.center = self.board_area.center
        pygame.draw.rect(surface, BG, card, border_radius=18)
        hud.text(surface, title, (card.x + 22, card.y + 24), hud.title)
        hud.lines(surface, lines, card.x + 22, card.y + 77)
        for key, label, offset in [('again', 'PLAY AGAIN', -54), ('menu', 'BACK TO MENU', 0)]:
            button = Button(label, (card.x + 22, card.bottom + offset - 60, card.width - 44, 42))
            self.buttons[key] = button
            button.draw(surface, hud.font)

    def clear_overlay(self):
        self.buttons.pop('again', None)
        self.buttons.pop('menu', None)


class PlaybackScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.playback = PlaybackController()
        self.pending = False
        self.results = Queue()
        self.status = 'READY'

    def submit(self, function):
        if self.pending: return
        self.pending = True
        self.status = 'SOLVING'
        self.message = ''

        def work():
            try: self.results.put((True, function()))
            except Exception as exc: self.results.put((False, str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def handle(self, event):
        if event.type == pygame.KEYDOWN and not self.pending:
            if event.key == pygame.K_SPACE: self.playback.toggle_pause()
            elif event.key == pygame.K_RIGHT: self.playback.next()
            elif event.key == pygame.K_LEFT: self.playback.previous()
            self.clear_overlay()
        super().handle(event)

    def update(self, dt):
        if self.pending:
            try:
                success, result = self.results.get_nowait()
            except Empty:
                return
            self.pending = False
            if success:
                try: self.accept_result(result)
                except Exception as exc:
                    self.status, self.message = 'ERROR', str(exc)
            else:
                self.status, self.message = 'ERROR', result
        self.playback.update(dt)

    def playback_status(self, final):
        if self.pending or self.status in ('ERROR', 'NO SOLUTION', 'READY'): return self.status
        if self.playback.finished: return final
        return 'PLAYING' if self.playback.playing else 'PAUSED'
