from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame

from core.game_object import GameObject, Vector2
from core.input import Input
from graphics.sprites import ShipSprite


class Bullet(GameObject):
    """Класс пули игрока."""

    SPEED = 500.0  # Скорость пули в пикселях/сек
    LIFETIME = 1.5  # Время жизни пули в секундах
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
        """Рисуем пулю как белый круг."""
        pygame.draw.circle(
            surface,
            pygame.Color("white"),
            (int(self.position.x), int(self.position.y)),
            int(self.RADIUS)
        )


class BulletPool:
    """Пул пуль для оптимизации."""

    def __init__(self, max_bullets: int = 10):
        self.max_bullets = max_bullets
        self.bullets: List[Bullet] = []

    def shoot(self, position: Vector2, direction: Vector2) -> None:
        """Выпустить пулю из заданной позиции в заданном направлении."""
        # Удаляем мертвые пули
        self.bullets = [b for b in self.bullets if b.is_alive()]

        # Если достигли лимита, не стреляем
        if len(self.bullets) >= self.max_bullets:
            return

        bullet = Bullet(position, direction)
        self.bullets.append(bullet)

    def update(self, dt: float, screen_size: Tuple[int, int]) -> None:
        """Обновить все активные пули."""
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.update(dt)
                bullet.wrap_around_screen(screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать все активные пули."""
        for bullet in self.bullets:
            if bullet.is_alive():
                bullet.draw(surface)

    def get_active_bullets(self) -> List[Bullet]:
        """Получить список активных пуль."""
        return [b for b in self.bullets if b.is_alive()]

    def clear(self) -> None:
        """Очистить все пули."""
        self.bullets.clear()


class Player(GameObject):
    """Класс игрока - космический корабль."""

    # Константы управления
    ROTATION_SPEED = 200.0  # градусов в секунду
    ACCELERATION = 300.0  # ускорение при тяге
    MAX_SPEED = 400.0  # максимальная скорость
    DRAG = 0.98  # коэффициент торможения (инерция)
    RADIUS = 15.0  # радиус корабля для коллизий

    # Константы стрельбы
    SHOOT_COOLDOWN = 0.25  # секунд между выстрелами

    # Константы Hyperspace
    HYPERSPACE_COOLDOWN = 2.0  # секунд между использованием

    # Константы жизней
    INITIAL_LIVES = 3
    RESPAWN_INVINCIBILITY = 2.0  # секунд неуязвимости после респауна

    def __init__(self, position: Vector2, screen_size: Tuple[int, int]):
        super().__init__(
            position=Vector2(position),
            velocity=Vector2(0, 0),
            rotation=0.0,
            radius=self.RADIUS
        )

        self.screen_size = screen_size
        self.lives = self.INITIAL_LIVES
        self.shoot_timer = 0.0
        self.hyperspace_timer = 0.0
        self.invincibility_timer = 0.0
        self.bullet_pool = BulletPool()

        # Создаем векторный спрайт корабля
        self.ship_sprite = ShipSprite(size=self.RADIUS * 2.5, color=pygame.Color("white"))

    def handle_input(self, input_manager: Input, dt: float) -> None:
        """Обработать ввод от игрока."""
        # Поворот влево (стрелка влево, A)
        if input_manager.is_pressed(pygame.K_LEFT) or input_manager.is_pressed(pygame.K_a):
            self.rotate(-self.ROTATION_SPEED * dt)

        # Поворот вправо (стрелка вправо, D)
        if input_manager.is_pressed(pygame.K_RIGHT) or input_manager.is_pressed(pygame.K_d):
            self.rotate(self.ROTATION_SPEED * dt)

        # Ускорение (стрелка вверх, W)
        if input_manager.is_pressed(pygame.K_UP) or input_manager.is_pressed(pygame.K_w):
            self.thrust(dt)

        # Стрельба (пробел)
        if input_manager.is_pressed(pygame.K_SPACE):
            self.shoot()

        # Hyperspace (Shift)
        if input_manager.was_pressed(pygame.K_LSHIFT) or input_manager.was_pressed(pygame.K_RSHIFT):
            self.hyperspace()

    def thrust(self, dt: float) -> None:
        """Ускорение корабля в направлении его носа."""
        # Вычисляем направление (rotation в градусах, 0° = вверх)
        angle_rad = math.radians(self.rotation - 90)  # -90 чтобы 0° был вверх
        direction = Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Добавляем ускорение
        self.velocity += direction * self.ACCELERATION * dt

        # Ограничиваем максимальную скорость
        if self.velocity.length() > self.MAX_SPEED:
            self.velocity.scale_to_length(self.MAX_SPEED)

    def shoot(self) -> None:
        """Выстрелить пулей."""
        if self.shoot_timer > 0:
            return

        # Вычисляем направление выстрела
        angle_rad = math.radians(self.rotation - 90)
        direction = Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Стреляем из носа корабля
        offset = direction * self.radius
        bullet_position = self.position + offset

        self.bullet_pool.shoot(bullet_position, direction)
        self.shoot_timer = self.SHOOT_COOLDOWN

    def hyperspace(self) -> None:
        """Телепортировать корабль в случайное место."""
        if self.hyperspace_timer > 0:
            return

        # Случайная позиция на экране
        self.position.x = random.uniform(50, self.screen_size[0] - 50)
        self.position.y = random.uniform(50, self.screen_size[1] - 50)

        # Сбрасываем скорость
        self.velocity = Vector2(0, 0)

        self.hyperspace_timer = self.HYPERSPACE_COOLDOWN

    def update(self, dt: float) -> None:
        """Обновить состояние игрока."""
        # Обновляем таймеры
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        if self.hyperspace_timer > 0:
            self.hyperspace_timer -= dt
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt

        # Применяем инерцию (торможение)
        self.velocity *= self.DRAG

        # Обновляем позицию
        super().update(dt)

        # Оборачиваем вокруг экрана
        self.wrap_around_screen(self.screen_size)

        # Обновляем пули
        self.bullet_pool.update(dt, self.screen_size)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать корабль и пули."""
        # Рисуем пули
        self.bullet_pool.draw(surface)

        # Если неуязвим, мигаем
        if self.is_invincible():
            if int(self.invincibility_timer * 10) % 2 == 0:
                self._draw_ship(surface)
        else:
            self._draw_ship(surface)

    def _draw_ship(self, surface: pygame.Surface) -> None:
        """Отрисовать корабль с учетом поворота используя ShipSprite."""
        self.ship_sprite.draw(surface, self.position, self.rotation)

    def is_invincible(self) -> bool:
        """Проверить, неуязвим ли игрок."""
        return self.invincibility_timer > 0

    def take_damage(self) -> bool:
        """Получить урон. Возвращает True, если игрок все еще жив."""
        if self.is_invincible():
            return True

        self.lives -= 1

        if self.lives > 0:
            self.respawn()
            return True
        else:
            self.kill()
            return False

    def respawn(self) -> None:
        """Возродить игрока в центре экрана."""
        self.position.x = self.screen_size[0] / 2
        self.position.y = self.screen_size[1] / 2
        self.velocity = Vector2(0, 0)
        self.rotation = 0.0
        self.invincibility_timer = self.RESPAWN_INVINCIBILITY
        self.bullet_pool.clear()

    def get_bullets(self) -> List[Bullet]:
        """Получить список активных пуль для проверки коллизий."""
        return self.bullet_pool.get_active_bullets()

    def reset(self) -> None:
        """Сбросить игрока к начальному состоянию."""
        self.lives = self.INITIAL_LIVES
        self.respawn()
