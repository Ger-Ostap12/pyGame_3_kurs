"""Пользовательский интерфейс: счёт, жизни, следующий уровень."""

from __future__ import annotations

from typing import Tuple

import pygame
from pygame.math import Vector2


class UIManager:
    """Менеджер пользовательского интерфейса."""

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
        self.large_font = pygame.font.SysFont(font_name, font_size * 2)
        self.text_color = pygame.Color("white")
        self.accent_color = pygame.Color("yellow")

        # Игровые данные
        self.score = 0
        self.lives = 3
        self.level = 1
        self.next_level_score = 1000  # Очки для перехода на следующий уровень

    def set_score(self, score: int) -> None:
        """Установить счёт."""
        self.score = score

    def add_score(self, points: int) -> None:
        """Добавить очки к счёту."""
        self.score += points

    def set_lives(self, lives: int) -> None:
        """Установить количество жизней."""
        self.lives = lives

    def set_level(self, level: int) -> None:
        """Установить уровень."""
        self.level = level

    def set_next_level_score(self, score: int) -> None:
        """Установить количество очков для следующего уровня."""
        self.next_level_score = score

    def check_level_up(self) -> bool:
        """
        Проверить, достигнут ли следующий уровень.
        
        Returns:
            True, если нужно перейти на следующий уровень
        """
        return self.score >= self.next_level_score

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать весь UI."""
        self._draw_score(surface)
        self._draw_lives(surface)
        # self._draw_level(surface)  # Убрано по запросу
        self._draw_next_level_progress(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        """Отрисовать счёт."""
        score_text = f"Score: {self.score:,}"
        text_surface = self.font.render(score_text, True, self.text_color)
        surface.blit(text_surface, (10, 10))

    def _draw_lives(self, surface: pygame.Surface) -> None:
        """Отрисовать количество жизней."""
        lives_text = f"Lives: {self.lives}"
        text_surface = self.font.render(lives_text, True, self.text_color)
        # Отступ от счёта
        score_height = self.font.get_height()
        y_offset = 10 + score_height + 10
        surface.blit(text_surface, (10, y_offset))

        # Также рисуем иконки жизней (маленькие кораблики)
        icon_size = 20
        icon_spacing = 25
        start_x = 10
        # Отступ от текста жизней
        start_y = y_offset + text_surface.get_height() + 10

        for i in range(self.lives):
            x = start_x + i * icon_spacing
            y = start_y
            self._draw_life_icon(surface, x, y, icon_size)

    def _draw_life_icon(self, surface: pygame.Surface, x: int, y: int, size: int) -> None:
        """Отрисовать иконку жизни (маленький кораблик)."""
        # Создаём маленький спрайт корабля
        points = [
            (x + size // 2, y),  # Нос
            (x, y + size),  # Левый угол
            (x + size // 2, y + size * 0.75),  # Центр сзади
            (x + size, y + size)  # Правый угол
        ]
        pygame.draw.polygon(surface, self.text_color, points, 1)

    def _draw_level(self, surface: pygame.Surface) -> None:
        """Отрисовать текущий уровень."""
        level_text = f"Level: {self.level}"
        text_surface = self.font.render(level_text, True, self.accent_color)
        
        # Размещаем в правом верхнем углу
        x = self.screen_size[0] - text_surface.get_width() - 10
        surface.blit(text_surface, (x, 10))

    def _draw_next_level_progress(self, surface: pygame.Surface) -> None:
        """Отрисовать прогресс до следующего уровня."""
        if self.score >= self.next_level_score:
            # Уже достигли следующего уровня
            progress_text = "Ready!"
            text_surface = self.font.render(progress_text, True, self.accent_color)
        else:
            # Показываем прогресс (убираем "Next Level:" чтобы не дублировать)
            remaining = self.next_level_score - self.score
            progress_text = f"{remaining:,} pts"
            text_surface = self.font.render(progress_text, True, self.text_color)

        # Размещаем в правом верхнем углу (так как Level убран)
        x = self.screen_size[0] - text_surface.get_width() - 10
        y = 10  # Верхний угол, так как Level больше нет
        surface.blit(text_surface, (x, y))

        # Рисуем прогресс-бар с отступом от текста
        bar_width = 200
        bar_height = 8
        bar_x = self.screen_size[0] - bar_width - 10
        bar_y = y + text_surface.get_height() + 10  # Отступ от текста прогресса

        # Фон прогресс-бара
        pygame.draw.rect(
            surface,
            pygame.Color(50, 50, 50),
            (bar_x, bar_y, bar_width, bar_height)
        )

        # Заполнение прогресс-бара
        if self.next_level_score > 0:
            progress = min(1.0, self.score / self.next_level_score)
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(
                    surface,
                    self.accent_color,
                    (bar_x, bar_y, fill_width, bar_height)
                )

    def reset(self) -> None:
        """Сбросить UI к начальному состоянию."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.next_level_score = 1000

