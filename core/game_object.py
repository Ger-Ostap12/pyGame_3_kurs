from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame


Vector2 = pygame.math.Vector2


@dataclass
class GameObject:
    position: Vector2
    velocity: Vector2 = Vector2()
    rotation: float = 0.0  # в градусах

    def update(self, dt: float) -> None:
        """Обновить состояние объекта за dt секунд."""
        self.position += self.velocity * dt

    def draw(self, surface: pygame.Surface) -> None:
        """Нарисовать объект. Базовая реализация — ничего не делает."""
        # Дальше можете использовать для наследников
        pass

    def get_rect(self) -> pygame.Rect:
        """Базовый прямоугольник для коллизий (можно переопределить в наследниках)."""
        # По умолчанию — точечный rect вокруг позиции
        return pygame.Rect(self.position.x, self.position.y, 1, 1)
