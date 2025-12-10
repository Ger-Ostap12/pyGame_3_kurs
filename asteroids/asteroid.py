"""Астероиды."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

import pygame

from core.game_object import GameObject, Vector2


class AsteroidSize(Enum):
    LARGE = auto()
    MEDIUM = auto()
    SMALL = auto()


@dataclass(frozen=True)
class AsteroidStats:
    radius: float
    speed_min: float
    speed_max: float
    fragments: int
    score: int


ASTEROID_CONFIG: dict[AsteroidSize, AsteroidStats] = {
    AsteroidSize.LARGE: AsteroidStats(radius=48.0, speed_min=50.0, speed_max=90.0, fragments=3, score=20),
    AsteroidSize.MEDIUM: AsteroidStats(radius=28.0, speed_min=80.0, speed_max=130.0, fragments=2, score=50),
    AsteroidSize.SMALL: AsteroidStats(radius=16.0, speed_min=120.0, speed_max=190.0, fragments=0, score=100),
}


def _random_velocity(size: AsteroidSize) -> Vector2:
    """
    Сгенерировать скорость.

    Args:
        size: Размер.

    Returns:
        Скорость.
    """
    stats = ASTEROID_CONFIG[size]
    speed = random.uniform(stats.speed_min, stats.speed_max)
    angle = random.uniform(0, math.tau)
    return Vector2(math.cos(angle), math.sin(angle)) * speed


class Asteroid(GameObject):
    """Астероид."""

    def __init__(
        self,
        position: Vector2,
        velocity: Optional[Vector2],
        size: AsteroidSize,
        screen_size: Tuple[int, int],
        seed: Optional[int] = None,
    ) -> None:
        """
        Инициализировать астероид.

        Args:
            position: Позиция.
            velocity: Скорость.
            size: Размер.
            screen_size: Размер экрана.
            seed: Семя.
        """
        self.size = size
        self.screen_size = screen_size
        self.random = random.Random(seed)

        stats = ASTEROID_CONFIG[size]

        # Если скорость не задана, выбираем случайную
        initial_velocity = Vector2(velocity) if velocity is not None else _random_velocity(size)

        super().__init__(
            position=Vector2(position),
            velocity=initial_velocity,
            rotation=self.random.uniform(0, 360),
            radius=stats.radius,
        )

        self.rotation_speed = self.random.uniform(-60.0, 60.0)
        self.shape_points = self._generate_shape()

    def _generate_shape(self) -> List[Vector2]:
        """Сгенерировать форму."""
        stats = ASTEROID_CONFIG[self.size]
        points: List[Vector2] = []
        point_count = 12 if self.size == AsteroidSize.LARGE else 10 if self.size == AsteroidSize.MEDIUM else 8

        for i in range(point_count):
            angle = (math.tau / point_count) * i
            # Добавляем шум к радиусу
            noise = self.random.uniform(0.75, 1.15)
            radius = stats.radius * noise
            points.append(Vector2(math.cos(angle) * radius, math.sin(angle) * radius))
        return points

    def split(self) -> List["Asteroid"]:
        """Разделить на осколки."""
        if self.size == AsteroidSize.SMALL:
            return []

        next_size = AsteroidSize.MEDIUM if self.size == AsteroidSize.LARGE else AsteroidSize.SMALL
        fragments: List[Asteroid] = []
        stats = ASTEROID_CONFIG[self.size]

        for _ in range(stats.fragments):
            velocity = _random_velocity(next_size)
            # Лёгкий сдвиг, чтобы осколки не стартовали в точности из центра
            offset = Vector2(self.random.uniform(-5, 5), self.random.uniform(-5, 5))
            child = Asteroid(
                position=self.position + offset,
                velocity=velocity,
                size=next_size,
                screen_size=self.screen_size,
            )
            fragments.append(child)

        return fragments

    def update(self, dt: float) -> None:
        """
        Обновить астероид.

        Args:
            dt: Дельта времени.
        """
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        super().update(dt)
        self.wrap_around_screen(self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать астероид.

        Args:
            surface: Поверхность.
        """
        # Поворачиваем предгенерированные точки
        angle_rad = math.radians(self.rotation)
        sin_a, cos_a = math.sin(angle_rad), math.cos(angle_rad)
        transformed: List[Tuple[float, float]] = []
        for point in self.shape_points:
            x = point.x * cos_a - point.y * sin_a
            y = point.x * sin_a + point.y * cos_a
            transformed.append((self.position.x + x, self.position.y + y))

        pygame.draw.polygon(surface, pygame.Color("white"), transformed, width=2)


class AsteroidField:
    """Менеджер волн астероидов."""

    def __init__(self, screen_size: Tuple[int, int], add_object: Callable[[GameObject], None]) -> None:
        """
        Инициализировать поле.

        Args:
            screen_size: Размер экрана.
            add_object: Функция добавления объекта.
        """
        self.screen_size = screen_size
        self.add_object = add_object
        self.level = 1

    def reset(self) -> None:
        """Сбросить поле."""
        self.level = 1

    def spawn_wave(self, player_position: Optional[Vector2]) -> None:
        """
        Создать волну.

        Args:
            player_position: Позиция игрока.
        """
        base_count = 4 + (self.level - 1)  # Каждая волна становится плотнее
        spawn_count = min(base_count, 10)

        for _ in range(spawn_count):
            pos = self._random_edge_position(player_position)
            asteroid = Asteroid(
                position=pos,
                velocity=None,
                size=AsteroidSize.LARGE,
                screen_size=self.screen_size,
            )
            self.add_object(asteroid)

    def next_wave(self, player_position: Optional[Vector2]) -> None:
        """
        Следующая волна.

        Args:
            player_position: Позиция игрока.
        """
        self.level += 1
        self.spawn_wave(player_position)

    def _random_edge_position(self, player_position: Optional[Vector2]) -> Vector2:
        """
        Случайная позиция на краю.

        Args:
            player_position: Позиция игрока.

        Returns:
            Позиция.
        """
        width, height = self.screen_size
        margin = 60
        min_distance = 220
        for _ in range(20):
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                pos = Vector2(random.uniform(margin, width - margin), margin)
            elif side == "bottom":
                pos = Vector2(random.uniform(margin, width - margin), height - margin)
            elif side == "left":
                pos = Vector2(margin, random.uniform(margin, height - margin))
            else:
                pos = Vector2(width - margin, random.uniform(margin, height - margin))

            if player_position is None:
                return pos

            if (pos - player_position).length() >= min_distance:
                return pos

        return Vector2(width / 2, margin)