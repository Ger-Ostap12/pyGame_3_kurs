"""Класс пули врагов."""

from __future__ import annotations

import pygame

from core.game_object import GameObject, Vector2


class EnemyBullet(GameObject):
    """Класс пули врага (для маленьких тарелок)."""

    SPEED = 250.0  # Скорость пули в пикселях/сек
    LIFETIME = 2.0  # Время жизни пули в секундах
    RADIUS = 2.0

    def __init__(self, position: Vector2, direction: Vector2):
        super().__init__(
            position=Vector2(position),
            velocity=direction * self.SPEED,
            radius=self.RADIUS
        )
        self.lifetime = self.LIFETIME

    def update(self, dt: float) -> None:
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        """Рисуем пулю как красный круг."""
        pygame.draw.circle(
            surface,
            pygame.Color("red"),
            (int(self.position.x), int(self.position.y)),
            int(self.RADIUS)
        )


class LargeEnemyBullet(GameObject):
    """Класс большой пули врага (для больших тарелок)."""

    SPEED = 250.0  # Скорость пули в пикселях/сек
    LIFETIME = 2.0  # Время жизни пули в секундах
    RADIUS = 5.0  # Больший радиус для больших пуль

    def __init__(self, position: Vector2, direction: Vector2):
        super().__init__(
            position=Vector2(position),
            velocity=direction * self.SPEED,
            radius=self.RADIUS
        )
        self.lifetime = self.LIFETIME

    def update(self, dt: float) -> None:
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        """Рисуем большую пулю как красный круг."""
        pygame.draw.circle(
            surface,
            pygame.Color("red"),
            (int(self.position.x), int(self.position.y)),
            int(self.RADIUS)
        )

