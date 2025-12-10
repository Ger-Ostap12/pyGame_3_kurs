"""Маленькая летающая тарелка — быстрый и точный враг."""

from __future__ import annotations

import math
import random
from typing import Callable, List, Optional, Tuple

import pygame

from core.game_object import GameObject, Vector2
from .bullet import EnemyBullet


class SmallSaucer(GameObject):
    """
    Маленькая тарелка — быстрый и точный противник.

    Особенности:
    - Движется быстрее большой тарелки
    - Стреляет чаще и точнее
    - Меньше радиус → сложнее попасть
    - Даёт больше очков при уничтожении
    """

    RADIUS: float = 12.0                    # Радиус коллизии
    SPEED: float = 120.0                    # Скорость движения (пикс/сек)
    SHOOT_COOLDOWN: float = 1.8             # Перезарядка между выстрелами
    MAX_BULLETS: int = 8                    # Максимум пуль в воздухе одновременно
    SCORE_VALUE: int = 100                  # Очки за уничтожение

    def __init__(
        self,
        position: Vector2,
        screen_size: Tuple[int, int],
        player_position_getter: Optional[Callable[[], Optional[Vector2]]] = None,
    ) -> None:
        """
        Создать маленькую тарелку.

        Args:
            position: Начальная позиция тарелки.
            screen_size: Размер игрового экрана (для wrap-around).
            player_position_getter: Функция без аргументов, возвращающая текущую позицию игрока
                                   (или None, если игрок мёртв). Нужна для точной стрельбы.
        """
        # Случайное горизонтальное направление при спавне
        direction = Vector2(1, 0) if random.random() < 0.5 else Vector2(-1, 0)

        super().__init__(
            position=Vector2(position),
            velocity=direction * self.SPEED,
            rotation=0.0,
            radius=self.RADIUS,
        )

        self.screen_size = screen_size
        self.player_position_getter = player_position_getter

        # Таймер стрельбы
        self.shoot_timer: float = random.uniform(0.0, self.SHOOT_COOLDOWN)
        self.bullets: List[EnemyBullet] = []

    def shoot(self) -> None:
        """Выпустить пулю точно в сторону текущую позицию игрока."""
        if self.shoot_timer > 0:
            return

        # Очищаем мёртвые пули
        self.bullets = [b for b in self.bullets if b.is_alive()]

        if len(self.bullets) >= self.MAX_BULLETS:
            return

        player_pos = self.player_position_getter() if self.player_position_getter else None
        if player_pos is None:
            return

        direction = (player_pos - self.position)
        if direction.length_squared() < 10:  # слишком близко — не стреляем
            return

        direction.normalize_ip()

        bullet = EnemyBullet(self.position.copy(), direction)
        self.bullets.append(bullet)

        self.shoot_timer = self.SHOOT_COOLDOWN

    def update(self, dt: float) -> None:
        """
        Обновить состояние тарелки каждый кадр.

        Args:
            dt: Дельта времени (секунды).
        """
        # Таймер стрельбы
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        self.shoot()

        # Движение
        super().update(dt)

        # Оборачивание по экрану
        self.wrap_around_screen(self.screen_size)

        # Обновление пуль
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.update(dt)
                bullet.wrap_around_screen(self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать тарелку и её пули.

        Args:
            surface: Поверхность, на которую рисовать.
        """
        # Пули
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.draw(surface)

        # Корпус тарелки — вытянутый овал
        body_rect = pygame.Rect(0, 0, int(self.RADIUS * 2.8), int(self.RADIUS * 1.2))
        body_rect.center = (int(self.position.x), int(self.position.y))

        pygame.draw.ellipse(surface, pygame.Color("white"), body_rect)
        pygame.draw.ellipse(surface, pygame.Color("lime"), body_rect, 2)

        # Купол сверху
        dome_rect = pygame.Rect(0, 0, int(self.RADIUS * 1.8), int(self.RADIUS))
        dome_rect.centerx = int(self.position.x)
        dome_rect.bottom = body_rect.centery

        pygame.draw.ellipse(surface, pygame.Color("cyan"), dome_rect)
        pygame.draw.ellipse(surface, pygame.Color("white"), dome_rect, 1)

        # Мигающий огонёк в центре (имитация жизни)
        flicker = int(pygame.time.get_ticks() / 200) % 2
        light_color = pygame.Color("red") if flicker else pygame.Color("magenta")
        pygame.draw.circle(surface, light_color, (int(self.position.x), int(self.position.y)), 3)

    def get_bullets(self) -> List[EnemyBullet]:
        """
        Вернуть список активных пуль тарелки.

        Используется системой коллизий.

        Returns:
            Список живых пуль.
        """
        return [b for b in self.bullets if b.is_alive()]