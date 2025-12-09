"""Фоновые звёзды с эффектом параллакса."""

from __future__ import annotations

import random
from typing import List, Tuple

import pygame
from pygame.math import Vector2


class Star:
    """Одна звезда на фоне."""

    def __init__(
        self,
        position: Vector2,
        speed: float,
        size: float = 1.0,
        color: pygame.Color = pygame.Color("white")
    ):
        """
        Создать звезду.
        
        Args:
            position: Позиция звезды
            speed: Скорость движения (для параллакса)
            size: Размер звезды
            color: Цвет звезды
        """
        self.position = Vector2(position)
        self.speed = speed
        self.size = size
        self.color = color
        self.base_position = Vector2(position)  # Исходная позиция для wrap-around

    def update(self, dt: float, player_velocity: Vector2, screen_size: Tuple[int, int]) -> None:
        """
        Обновить позицию звезды с учётом параллакса.
        
        Args:
            dt: Дельта времени
            player_velocity: Скорость игрока (для параллакса)
            screen_size: Размер экрана
        """
        # Параллакс: звёзды движутся в противоположном направлении от движения игрока
        # с разной скоростью в зависимости от их слоя
        parallax_velocity = -player_velocity * self.speed
        self.position += parallax_velocity * dt

        # Оборачиваем звёзды вокруг экрана
        width, height = screen_size
        if self.position.x < 0:
            self.position.x += width
        elif self.position.x > width:
            self.position.x -= width

        if self.position.y < 0:
            self.position.y += height
        elif self.position.y > height:
            self.position.y -= height

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать звезду."""
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.position.x), int(self.position.y)),
            int(self.size)
        )


class StarField:
    """Поле фоновых звёзд с эффектом параллакса."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        star_count: int = 200,
        num_layers: int = 3
    ):
        """
        Создать поле звёзд.
        
        Args:
            screen_size: Размер экрана
            star_count: Количество звёзд
            num_layers: Количество слоёв звёзд (для параллакса)
        """
        self.screen_size = screen_size
        self.stars: List[Star] = []
        self.num_layers = num_layers

        # Создаём звёзды на разных слоях
        stars_per_layer = star_count // num_layers

        for layer in range(num_layers):
            # Скорость зависит от слоя (дальние звёзды движутся медленнее)
            # Слой 0 - самый дальний (медленный), слой num_layers-1 - ближайший (быстрый)
            speed = (layer + 1) / num_layers

            # Размер и яркость зависят от слоя
            # Ближние звёзды больше и ярче
            base_size = 1.0 + layer * 0.5
            brightness = 150 + layer * 35  # От 150 до 255

            for _ in range(stars_per_layer):
                # Случайная позиция
                x = random.uniform(0, screen_size[0])
                y = random.uniform(0, screen_size[1])

                # Случайный размер с вариацией
                size = random.uniform(base_size * 0.7, base_size * 1.3)

                # Цвет с учётом яркости
                color_value = min(255, int(brightness * random.uniform(0.8, 1.0)))
                color = pygame.Color(color_value, color_value, color_value)

                star = Star(
                    position=Vector2(x, y),
                    speed=speed,
                    size=size,
                    color=color
                )
                self.stars.append(star)

    def update(self, dt: float, player_velocity: Vector2) -> None:
        """
        Обновить все звёзды.
        
        Args:
            dt: Дельта времени
            player_velocity: Скорость игрока для параллакса
        """
        for star in self.stars:
            star.update(dt, player_velocity, self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать все звёзды."""
        for star in self.stars:
            star.draw(surface)

    def reset(self) -> None:
        """Пересоздать поле звёзд (например, при смене уровня)."""
        self.stars.clear()
        stars_per_layer = len(self.stars) // self.num_layers if self.stars else 200 // self.num_layers

        for layer in range(self.num_layers):
            speed = (layer + 1) / self.num_layers
            base_size = 1.0 + layer * 0.5
            brightness = 150 + layer * 35

            for _ in range(stars_per_layer):
                x = random.uniform(0, self.screen_size[0])
                y = random.uniform(0, self.screen_size[1])
                size = random.uniform(base_size * 0.7, base_size * 1.3)
                color_value = min(255, int(brightness * random.uniform(0.8, 1.0)))
                color = pygame.Color(color_value, color_value, color_value)

                star = Star(
                    position=Vector2(x, y),
                    speed=speed,
                    size=size,
                    color=color
                )
                self.stars.append(star)

