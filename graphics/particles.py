"""Система частиц для эффектов взрывов."""

from __future__ import annotations

import math
import random
from typing import List, Tuple

import pygame
from pygame.math import Vector2


class Particle:
    """Одна частица в системе частиц."""

    def __init__(
        self,
        position: Vector2,
        velocity: Vector2,
        color: pygame.Color,
        lifetime: float,
        size: float = 2.0
    ):
        """
        Создать частицу.
        
        Args:
            position: Начальная позиция
            velocity: Скорость частицы
            color: Цвет частицы
            lifetime: Время жизни в секундах
            size: Размер частицы
        """
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt: float) -> None:
        """
        Обновить частицу.

        Args:
            dt: Дельта времени.
        """
        self.position += self.velocity * dt
        self.lifetime -= dt

        # Уменьшаем размер и яркость со временем
        fade = self.lifetime / self.max_lifetime
        self.size = max(0.5, self.size * fade)

        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать частицу.

        Args:
            surface: Поверхность.
        """
        if not self.alive:
            return

        # Вычисляем альфа-канал на основе оставшегося времени жизни
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = self.color
        if alpha < 255:
            # Создаем цвет с альфа-каналом
            color = pygame.Color(
                min(255, color.r),
                min(255, color.g),
                min(255, color.b),
                alpha
            )

        # Рисуем частицу как круг
        pygame.draw.circle(
            surface,
            color,
            (int(self.position.x), int(self.position.y)),
            int(self.size)
        )

    def is_alive(self) -> bool:
        """Проверить, жива ли частица."""
        return self.alive


class Explosion:
    """Эффект взрыва из частиц."""

    def __init__(
        self,
        position: Vector2,
        color: pygame.Color = pygame.Color("orange"),
        particle_count: int = 30,
        speed: float = 200.0,
        lifetime: float = 0.5
    ):
        """
        Создать взрыв.

        Args:
            position: Позиция взрыва
            color: Основной цвет взрыва
            particle_count: Количество частиц
            speed: Скорость разлёта частиц
            lifetime: Время жизни взрыва в секундах
        """
        self.position = Vector2(position)
        self.particles: List[Particle] = []
        self.alive = True

        # Создаем частицы с разными цветами для эффекта
        colors = [
            color,
            pygame.Color("yellow"),
            pygame.Color("red"),
            pygame.Color("white"),
        ]

        for _ in range(particle_count):
            # Случайное направление
            angle = random.uniform(0, 2 * math.pi)
            velocity_magnitude = random.uniform(speed * 0.5, speed * 1.5)
            velocity = Vector2(
                math.cos(angle) * velocity_magnitude,
                math.sin(angle) * velocity_magnitude
            )

            # Случайный цвет из палитры
            particle_color = random.choice(colors)

            # Случайное время жизни
            particle_lifetime = random.uniform(lifetime * 0.7, lifetime * 1.3)

            # Случайный размер
            particle_size = random.uniform(1.5, 3.5)

            particle = Particle(
                position=self.position,
                velocity=velocity,
                color=particle_color,
                lifetime=particle_lifetime,
                size=particle_size
            )
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """
        Обновить взрыв.

        Args:
            dt: Дельта времени.
        """
        if not self.alive:
            return

        for particle in self.particles:
            particle.update(dt)

        # Проверяем, остались ли живые частицы
        self.alive = any(p.is_alive() for p in self.particles)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать взрыв.

        Args:
            surface: Поверхность.
        """
        if not self.alive:
            return

        for particle in self.particles:
            particle.draw(surface)

    def is_alive(self) -> bool:
        """Проверить активность взрыва."""
        return self.alive


class ParticleSystem:
    """Менеджер системы частиц для управления множеством эффектов."""

    def __init__(self):
        """Создать систему частиц."""
        self.explosions: List[Explosion] = []

    def add_explosion(
        self,
        position: Vector2,
        color: pygame.Color = pygame.Color("orange"),
        particle_count: int = 30,
        speed: float = 200.0,
        lifetime: float = 0.5
    ) -> None:
        """
        Добавить взрыв.

        Args:
            position: Позиция взрыва
            color: Цвет взрыва
            particle_count: Количество частиц
            speed: Скорость разлёта
            lifetime: Время жизни
        """
        explosion = Explosion(
            position=position,
            color=color,
            particle_count=particle_count,
            speed=speed,
            lifetime=lifetime
        )
        self.explosions.append(explosion)

    def update(self, dt: float) -> None:
        """
        Обновить систему.

        Args:
            dt: Дельта времени.
        """
        for explosion in self.explosions:
            explosion.update(dt)

        # Удаляем мёртвые взрывы
        self.explosions = [e for e in self.explosions if e.is_alive()]

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать систему.

        Args:
            surface: Поверхность.
        """
        for explosion in self.explosions:
            explosion.draw(surface)

    def clear(self) -> None:
        """Очистить систему."""
        self.explosions.clear()