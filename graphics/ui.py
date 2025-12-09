"""Пользовательский интерфейс: счёт."""

from __future__ import annotations

from typing import Tuple

import pygame


class UIManager:
    """Менеджер пользовательского интерфейса - только отрисовка очков."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        font_name: str = "consolas",
        font_size: int = 24
    ):
        """
        Создать менеджер UI.
        
        Args:
            screen_size: Размер экрана
            font_name: Имя шрифта
            font_size: Размер шрифта
        """
        self.screen_size = screen_size
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_color = pygame.Color("white")

        # Игровые данные
        self.score = 0

    def set_score(self, score: int) -> None:
        """Установить счёт."""
        self.score = score

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать UI - только счёт."""
        self._draw_score(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        """Отрисовать счёт в правом нижнем углу, где управление."""
        score_text = f"Score: {self.score:,}"
        text_surface = self.font.render(score_text, True, self.text_color)
        # Размещаем в правом нижнем углу, выше подсказок управления
        x = self.screen_size[0] - 300  # Та же позиция X, что и у управления
        y = self.screen_size[1] - 150 - text_surface.get_height() - 10  # Выше подсказок управления
        surface.blit(text_surface, (x, y))
