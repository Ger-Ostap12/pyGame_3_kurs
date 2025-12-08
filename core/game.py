from __future__ import annotations

from typing import Dict, Tuple

import pygame

from .states import (
    BaseState,
    GameStateId,
    MenuState,
    PlayingState,
    GameOverState,
)


class Game:
    def __init__(
        self,
        size: Tuple[int, int] = (800, 600),
        fps: int = 60,
    ) -> None:
        self.size = size
        self.fps = fps

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Asteroids")

        self.clock = pygame.time.Clock()
        self.running = False

        self.font = pygame.font.SysFont("consolas", 18)
        self.bg_color = pygame.Color("black")
        self.text_color = pygame.Color("white")

        # FSM: словарь состояний + текущее состояние
        self._states: Dict[GameStateId, BaseState] = {}
        self._current_state: BaseState | None = None
        self._init_states()

    # --- управление состояниями ---

    def _init_states(self) -> None:
        self._states = {
            GameStateId.MENU: MenuState(self),
            GameStateId.PLAYING: PlayingState(self),
            GameStateId.GAME_OVER: GameOverState(self),
        }
        self.change_state(GameStateId.MENU)

    def change_state(self, state_id: GameStateId) -> None:
        """Переключиться на другое состояние игры."""
        if self._current_state is not None:
            self._current_state.exit()

        self._current_state = self._states[state_id]
        self._current_state.enter()

    # --- основной цикл ---

    def run(self) -> None:
        self.running = True

        while self.running:
            dt_ms = self.clock.tick(self.fps)
            dt = dt_ms / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

            pygame.display.flip()

    def stop(self) -> None:
        """Корректно остановить игру."""
        self.running = False

    # --- внутренние шаги цикла ---

    def _handle_events(self) -> None:
        if self._current_state is None:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return

            self._current_state.handle_event(event)

    def _update(self, dt: float) -> None:
        if self._current_state is not None:
            self._current_state.update(dt)

    def _draw(self) -> None:
        if self._current_state is not None:
            self._current_state.draw()

        # Поверх всего показываем FPS
        fps = self.clock.get_fps()
        fps_surf = self.font.render(f"FPS: {fps:5.1f}", True, self.text_color)
        self.screen.blit(fps_surf, (10, 10))

    # --- Заглушки стейтов ---

    def _update_menu(self, dt: float) -> None:
        pass

    def _update_playing(self, dt: float) -> None:
        pass

    def _update_game_over(self, dt: float) -> None:
        pass

    def _draw_menu(self) -> None:
        self.screen.fill(self.bg_color)

        title = self.font.render("ASTEROIDS (MENU)", True, self.text_color)
        hint = self.font.render("Enter - start, Esc - exit", True, self.text_color)

        self.screen.blit(title, (self.size[0] // 2 - title.get_width() // 2, self.size[1] // 3))
        self.screen.blit(hint, (self.size[0] // 2 - hint.get_width() // 2, self.size[1] // 3 + 30))

    def _draw_playing(self) -> None:
        self.screen.fill(self.bg_color)

        label = self.font.render("PLAYING (press G to Game Over)", True, self.text_color)
        self.screen.blit(label, (self.size[0] // 2 - label.get_width() // 2, self.size[1] // 2))

    def _draw_game_over(self) -> None:
        self.screen.fill(self.bg_color)

        title = self.font.render("GAME OVER", True, self.text_color)
        hint = self.font.render("R - restart, Esc - exit", True, self.text_color)

        self.screen.blit(title, (self.size[0] // 2 - title.get_width() // 2, self.size[1] // 3))
        self.screen.blit(hint, (self.size[0] // 2 - hint.get_width() // 2, self.size[1] // 3 + 30))
