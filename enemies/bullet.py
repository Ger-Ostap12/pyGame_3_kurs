"""Пули, выпускаемые летающими тарелками."""

from __future__ import annotations

import pygame

from core.game_object import GameObject, Vector2


class EnemyBullet(GameObject):
    """
    Обычная пуля маленькой тарелки.

    Быстрая, точная, красная. Даёт ощущение опасности.
    """

    SPEED: float = 280.0          # пикселей в секунду
    LIFETIME: float = 2.5         # секунды
    RADIUS: float = 3.0           # радиус коллизии

    def __init__(self, position: Vector2, direction: Vector2) -> None:
        """
        Создать пулю врага.

        Args:
            position: Точка вылета пули (обычно центр тарелки).
            direction: Нормализованный вектор направления к игроку.
        """
        super().__init__(
            position=Vector2(position),
            velocity=direction * self.SPEED,
            radius=self.RADIUS,
        )
        self.age = 0.0

    def update(self, dt: float) -> None:
        """
        Обновить положение и время жизни пули.

        Args:
            dt: Дельта времени в секундах.
        """
        super().update(dt)
        self.age += dt
        if self.age >= self.LIFETIME:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать пулю как яркий красный кружок с белой обводкой.

        Args:
            surface: Поверхность для отрисовки.
        """
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, pygame.Color("red"), center, int(self.RADIUS))
        pygame.draw.circle(surface, pygame.Color("white"), center, int(self.RADIUS), 1)


class LargeEnemyBullet(EnemyBullet):
    """
    Большая и медленная пуля большой тарелки.

    Визуально отличается, легче заметить и увернуться.
    """

    SPEED: float = 180.0          # медленнее, чем у маленькой тарелки
    LIFETIME: float = 3.5         # живёт дольше
    RADIUS: float = 6.0           # крупнее

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать большую пулю — оранжевый круг с пульсирующим свечением.

        Args:
            surface: Поверхность для отрисовки.
        """
        center = (int(self.position.x), int(self.position.y))

        # Основное тело
        pygame.draw.circle(surface, pygame.Color("orange"), center, int(self.RADIUS))

        # Внешнее свечение (пульсирует)
        alpha = int(100 + 155 * abs((pygame.time.get_ticks() % 1000) / 1000 - 0.5) * 2)
        glow_surface = pygame.Surface((int(self.RADIUS * 4), int(self.RADIUS * 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            pygame.Color(255, 140, 0, alpha),
            (int(self.RADIUS * 2), int(self.RADIUS * 2)),
            int(self.RADIUS * 2)
        )
        surface.blit(glow_surface, glow_surface.get_rect(center=center))

        # Белая обводка
        pygame.draw.circle(surface, pygame.Color("white"), center, int(self.RADIUS), 2)
