"""Базовый класс для игровых объектов."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import pygame

Vector2 = pygame.math.Vector2


@dataclass
class GameObject:
    """Базовый класс для всех игровых объектов (корабль, астероиды, пули и т.д.)."""

    position: Vector2
    velocity: Vector2 = field(default_factory=Vector2)
    rotation: float = 0.0  # градусы
    radius: float = 0.0    # условный «размер» объекта для простых коллизий
    alive: bool = True

    sprite: Optional[pygame.Surface] = None
    mask: Optional[pygame.Mask] = None

    def update(self, dt: float) -> None:
        """
        Обновить положение объекта.

        Args:
            dt: Дельта времени.
        """
        self.position += self.velocity * dt

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать объект.

        Args:
            surface: Поверхность для отрисовки.
        """
        if self.sprite is not None:
            rect = self.sprite.get_rect(center=self.position)
            surface.blit(self.sprite, rect)
        else:
            # Заглушка: простой круг
            if self.radius > 0:
                pygame.draw.circle(surface, pygame.Color("white"), self.position, self.radius, 1)

    def get_rect(self) -> pygame.Rect:
        """Вернуть прямоугольник для коллизий."""
        if self.sprite is not None:
            return self.sprite.get_rect(center=self.position)

        size = int(self.radius * 2) or 1
        return pygame.Rect(
            int(self.position.x - size / 2),
            int(self.position.y - size / 2),
            size,
            size,
        )

    def get_mask(self) -> Optional[pygame.Mask]:
        """Вернуть маску для пиксельных коллизий."""
        if self.mask is not None:
            return self.mask
        if self.sprite is not None:
            self.mask = pygame.mask.from_surface(self.sprite)
            return self.mask
        return None

    def wrap_around_screen(self, size: Tuple[int, int]) -> None:
        """
        Перенести объект на противоположную сторону экрана.

        Args:
            size: Размер экрана.
        """
        width, height = size
        x, y = self.position.x, self.position.y

        if x < 0:
            x += width
        elif x > width:
            x -= width

        if y < 0:
            y += height
        elif y > height:
            y -= height

        self.position.update(x, y)

    def rotate(self, angle_delta: float) -> None:
        """
        Повернуть объект.

        Args:
            angle_delta: Угол поворота в градусах.
        """
        self.rotation = (self.rotation + angle_delta) % 360

    def kill(self) -> None:
        """Пометить объект как мёртвый."""
        self.alive = False

    def is_alive(self) -> bool:
        """Проверить, жив ли объект."""
        return self.alive