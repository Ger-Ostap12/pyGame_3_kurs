from __future__ import annotations

import math
import random
from enum import Enum
from typing import List, Optional, Tuple

import pygame

from .game_object import GameObject, Vector2


class AsteroidSize(Enum):
    """Размеры астероидов."""
    LARGE = "large"
    MEDIUM = "medium"
    SMALL = "small"


class Asteroid(GameObject):
    """Класс астероида с движением, вращением и разбиением."""

    # Параметры по размерам
    SIZE_CONFIG = {
        AsteroidSize.LARGE: {
            "radius": 40.0,
            "min_speed": 30.0,
            "max_speed": 60.0,
            "rotation_speed": 30.0,  # градусов в секунду
            "points": 20,  # очки за уничтожение
        },
        AsteroidSize.MEDIUM: {
            "radius": 20.0,
            "min_speed": 50.0,
            "max_speed": 100.0,
            "rotation_speed": 60.0,
            "points": 50,
        },
        AsteroidSize.SMALL: {
            "radius": 10.0,
            "min_speed": 70.0,
            "max_speed": 150.0,
            "rotation_speed": 90.0,
            "points": 100,
        },
    }

    def __init__(
        self,
        position: Vector2,
        size: AsteroidSize,
        screen_size: Tuple[int, int],
        velocity: Optional[Vector2] = None,
    ):
        config = self.SIZE_CONFIG[size]

        # Если скорость не задана, генерируем случайную
        if velocity is None:
            speed = random.uniform(config["min_speed"], config["max_speed"])
            angle = random.uniform(0, 2 * math.pi)
            velocity = Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )

        super().__init__(
            position=Vector2(position),
            velocity=velocity,
            rotation=random.uniform(0, 360),
            radius=config["radius"]
        )

        self.size = size
        self.screen_size = screen_size
        self.rotation_speed = config["rotation_speed"]
        self.points = config["points"]

        # Случайное направление вращения
        if random.random() < 0.5:
            self.rotation_speed = -self.rotation_speed

        # Создаем спрайт астероида (неправильный многоугольник)
        self._create_sprite()

    def _create_sprite(self) -> None:
        """Создать спрайт астероида в виде неправильного многоугольника."""
        size = int(self.radius * 2)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Генерируем точки для неправильного многоугольника
        num_points = random.randint(8, 12)
        center_x, center_y = size // 2, size // 2

        points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            # Добавляем случайное отклонение радиуса для неровности
            radius_var = random.uniform(0.7, 1.0)
            r = self.radius * radius_var
            x = center_x + math.cos(angle) * r
            y = center_y + math.sin(angle) * r
            points.append((x, y))

        # Рисуем контур астероида
        pygame.draw.polygon(surface, pygame.Color("white"), points, 2)
        self.sprite = surface

    def update(self, dt: float) -> None:
        """Обновить позицию и вращение астероида."""
        # Вращение
        self.rotate(self.rotation_speed * dt)

        # Движение
        super().update(dt)

        # Screen wrap
        self.wrap_around_screen(self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать астероид с учетом вращения."""
        if self.sprite is not None:
            # Поворачиваем спрайт
            rotated_sprite = pygame.transform.rotate(self.sprite, -self.rotation)
            rect = rotated_sprite.get_rect(center=self.position)
            surface.blit(rotated_sprite, rect)
        else:
            # Fallback: простой круг
            pygame.draw.circle(
                surface,
                pygame.Color("white"),
                (int(self.position.x), int(self.position.y)),
                int(self.radius),
                2
            )

    def split(self) -> List[Asteroid]:
        """
        Разбить астероид на меньшие.
        Возвращает список новых астероидов (пустой, если это уже самый маленький).
        """
        if self.size == AsteroidSize.SMALL:
            # Маленькие астероиды не разбиваются
            return []

        # Определяем следующий размер
        if self.size == AsteroidSize.LARGE:
            next_size = AsteroidSize.MEDIUM
        else:  # MEDIUM
            next_size = AsteroidSize.SMALL

        # Создаем 2-3 новых астероида
        num_fragments = random.randint(2, 3)
        new_asteroids = []

        for _ in range(num_fragments):
            # Случайное смещение от центра
            offset_angle = random.uniform(0, 2 * math.pi)
            offset_distance = random.uniform(5, 15)
            new_position = Vector2(
                self.position.x + math.cos(offset_angle) * offset_distance,
                self.position.y + math.sin(offset_angle) * offset_distance
            )

            # Новая скорость с добавлением случайного вектора
            new_velocity = Vector2(self.velocity)
            speed_boost = random.uniform(20, 50)
            angle = random.uniform(0, 2 * math.pi)
            new_velocity += Vector2(
                math.cos(angle) * speed_boost,
                math.sin(angle) * speed_boost
            )

            new_asteroid = Asteroid(
                position=new_position,
                size=next_size,
                screen_size=self.screen_size,
                velocity=new_velocity
            )
            new_asteroids.append(new_asteroid)

        return new_asteroids


class AsteroidWave:
    """Класс для управления волнами астероидов."""

    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.asteroids: List[Asteroid] = []
        self.wave_number = 0

    def spawn_wave(self, num_asteroids: Optional[int] = None) -> None:
        """Создать новую волну астероидов."""
        if num_asteroids is None:
            # Увеличиваем количество с каждой волной
            num_asteroids = 4 + self.wave_number

        self.asteroids.clear()
        self.wave_number += 1

        for _ in range(num_asteroids):
            asteroid = self._spawn_asteroid(AsteroidSize.LARGE)
            self.asteroids.append(asteroid)

    def _spawn_asteroid(self, size: AsteroidSize) -> Asteroid:
        """Создать астероид в случайной позиции на краю экрана."""
        width, height = self.screen_size

        # Случайно выбираем сторону экрана
        side = random.randint(0, 3)

        if side == 0:  # Верх
            x = random.uniform(0, width)
            y = -50
        elif side == 1:  # Право
            x = width + 50
            y = random.uniform(0, height)
        elif side == 2:  # Низ
            x = random.uniform(0, width)
            y = height + 50
        else:  # Лево
            x = -50
            y = random.uniform(0, height)

        return Asteroid(
            position=Vector2(x, y),
            size=size,
            screen_size=self.screen_size
        )

    def add_asteroid(self, asteroid: Asteroid) -> None:
        """Добавить астероид в список."""
        self.asteroids.append(asteroid)

    def remove_asteroid(self, asteroid: Asteroid) -> None:
        """Удалить астероид из списка."""
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)

    def update(self, dt: float) -> None:
        """Обновить все астероиды."""
        for asteroid in self.asteroids:
            if asteroid.is_alive():
                asteroid.update(dt)

        # Удаляем мертвые астероиды
        self.asteroids = [a for a in self.asteroids if a.is_alive()]

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать все астероиды."""
        for asteroid in self.asteroids:
            if asteroid.is_alive():
                asteroid.draw(surface)

    def get_active_asteroids(self) -> List[Asteroid]:
        """Получить список активных астероидов."""
        return [a for a in self.asteroids if a.is_alive()]

    def is_wave_cleared(self) -> bool:
        """Проверить, уничтожены ли все астероиды в текущей волне."""
        return len(self.get_active_asteroids()) == 0

    def clear(self) -> None:
        """Очистить все астероиды."""
        self.asteroids.clear()

