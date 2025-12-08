from __future__ import annotations

from typing import Tuple

import pygame

from .states import GameState


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
        self.state = GameState.MENU

    def run(self) -> None:
        """Главный игровой цикл."""
        self.running = True

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # секунды

            self._handle_events()
            self._update(dt)
            self._draw()

            pygame.display.flip()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Переключение стейтов для теста
                if event.key == pygame.K_RETURN and self.state == GameState.MENU:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self.state = GameState.PLAYING

    def _update(self, dt: float) -> None:
        if self.state == GameState.MENU:
            self._update_menu(dt)
        elif self.state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state == GameState.GAME_OVER:
            self._update_game_over(dt)

    def _draw(self) -> None:
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_playing()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

    # --- Здесь пока заглушки, их расширим позже  ---

    def _update_menu(self, dt: float) -> None:
        pass

    def _update_playing(self, dt: float) -> None:
        pass

    def _update_game_over(self, dt: float) -> None:
        pass

    def _draw_menu(self) -> None:
        self.screen.fill("black")
        # сюда позже добавим отрисовку меню

    def _draw_playing(self) -> None:
        self.screen.fill("black")
        # сюда подключаем игрока, астероиды и т.д.

    def _draw_game_over(self) -> None:
        self.screen.fill("black")
        # сюда добавим экран game over
