"""Маленькая тарелка - прицельная стрельба в игрока."""

from __future__ import annotations

import math
import random
from typing import Callable, List, Optional, Tuple

import pygame

from core.game_object import GameObject, Vector2
from .bullet import EnemyBullet


class SmallSaucer(GameObject):
    """Маленькая тарелка - прицельная стрельба в игрока (расчёт направления на основе позиций)."""

    RADIUS = 10.0  # Радиус тарелки
    SPEED = 100.0  # Скорость движения (быстрее большой)
    SHOOT_COOLDOWN = 2.0  # секунд между выстрелами (стреляет чаще)
    MAX_BULLETS = 7  # Максимальное количество пуль одновременно

    def __init__(
        self,
        position: Vector2,
        screen_size: Tuple[int, int],
        player_position_getter: Optional[Callable[[], Optional[Vector2]]] = None
    ):
        # Направление движения (горизонтально, но может менять направление)
        direction = Vector2(1, 0) if random.random() < 0.5 else Vector2(-1, 0)
        
        super().__init__(
            position=Vector2(position),
            velocity=direction * self.SPEED,
            rotation=0.0,
            radius=self.RADIUS
        )

        self.screen_size = screen_size
        self.shoot_timer = random.uniform(0.0, self.SHOOT_COOLDOWN)  # Начальная задержка
        self.bullets: List[EnemyBullet] = []
        self.player_position_getter = player_position_getter

    def shoot(self) -> None:
        """Выстрелить пулей в направлении игрока."""
        if self.shoot_timer > 0:
            return

        # Удаляем мертвые пули
        self.bullets = [b for b in self.bullets if b.is_alive()]

        # Если достигли лимита, не стреляем
        if len(self.bullets) >= self.MAX_BULLETS:
            return

        # Получаем позицию игрока через getter
        player_position = None
        if self.player_position_getter is not None:
            player_position = self.player_position_getter()

        # Если позиция игрока недоступна, не стреляем
        if player_position is None:
            return

        # Вычисляем направление к игроку
        direction = player_position - self.position
        
        # Если игрок слишком близко, не стреляем (избегаем деления на ноль)
        if direction.length() < 10:
            return

        direction.normalize_ip()

        # Стреляем из центра тарелки
        bullet = EnemyBullet(self.position, direction)
        self.bullets.append(bullet)

        self.shoot_timer = self.SHOOT_COOLDOWN

    def update(self, dt: float) -> None:
        """Обновить состояние тарелки."""
        # Обновляем таймер стрельбы
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        # Стреляем в игрока
        self.shoot()

        # Обновляем позицию
        super().update(dt)

        # Оборачиваем вокруг экрана
        self.wrap_around_screen(self.screen_size)

        # Обновляем пули
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.update(dt)
                bullet.wrap_around_screen(self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать тарелку и пули."""
        # Рисуем пули
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.draw(surface)

        # Рисуем тарелку (маленький овал) - более заметная
        rect = pygame.Rect(
            int(self.position.x - self.RADIUS),
            int(self.position.y - self.RADIUS / 2),
            int(self.RADIUS * 2),
            int(self.RADIUS)
        )
        # Закрашиваем тарелку
        pygame.draw.ellipse(surface, pygame.Color("white"), rect)
        # Обводим контуром
        pygame.draw.ellipse(surface, pygame.Color("gray"), rect, 2)

        # Рисуем купол сверху (более толстый)
        pygame.draw.arc(
            surface,
            pygame.Color("lightgray"),
            rect,
            0,
            math.pi,
            3
        )
        
        # Рисуем центр для лучшей видимости
        pygame.draw.circle(surface, pygame.Color("white"), (int(self.position.x), int(self.position.y)), 2)

    def get_bullets(self) -> List[EnemyBullet]:
        """Получить список активных пуль для проверки коллизий."""
        return [b for b in self.bullets if b.is_alive()]

