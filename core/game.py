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

        # Шрифт для вывода FPS и текста (пока один общий)
        self.font = pygame.font.SysFont("consolas", 18)

        # Цвета
        self.bg_color = pygame.Color("black")
        self.text_color = pygame.Color("white")

    def run(self) -> None:
        """Главный игровой цикл."""
        self.running = True

        while self.running:
            dt_ms = self.clock.tick(self.fps)
            dt = dt_ms / 1000.0  # секунды

            self._handle_events()
            self._update(dt)
            self._draw(dt)

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

                # Пример входа в экран Game Over, пока просто по клавише G
                if event.key == pygame.K_g and self.state == GameState.PLAYING:
                    self.state = GameState.GAME_OVER

    def _update(self, dt: float) -> None:
        if self.state == GameState.MENU:
            self._update_menu(dt)
        elif self.state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state == GameState.GAME_OVER:
            self._update_game_over(dt)

    def _draw(self, dt: float) -> None:
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_playing()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        # Поверх всего рисуем FPS в углу
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
