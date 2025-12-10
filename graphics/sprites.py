"""Векторные спрайты для корабля и астероидов."""

from __future__ import annotations

import math
import random
from typing import List, Tuple

import pygame
from pygame.math import Vector2


class ShipSprite:
    """Векторный спрайт корабля в стиле полилиний."""

    def __init__(
        self, 
        size: float = 30.0, 
        color: pygame.Color = pygame.Color("white"),
        glow: bool = True
    ):
        """
        Создать спрайт корабля.
        
        Args:
            size: Размер корабля (диаметр)
            color: Цвет корабля
            glow: Добавить эффект свечения
        """
        self.size = size
        self.color = color
        self.glow = glow
        self.base_surface = self._create_base_sprite()

    def _create_base_sprite(self) -> pygame.Surface:
        """Создать базовый спрайт корабля с детализированным дизайном."""
        # Создаем поверхность с альфа-каналом
        surface_size = int(self.size * 2.5)
        surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)

        center_x, center_y = surface_size // 2, surface_size // 2
        size = self.size

        # Определяем точки для корабля (более детализированная форма)
        # Нос корабля (острый, вверх)
        nose = (center_x, center_y - size * 0.5)

        # Верхние точки корпуса (крылья)
        left_wing_top = (center_x - size * 0.4, center_y - size * 0.1)
        right_wing_top = (center_x + size * 0.4, center_y - size * 0.1)

        # Боковые точки кормы
        left_wing_bottom = (center_x - size * 0.45, center_y + size * 0.2)
        right_wing_bottom = (center_x + size * 0.45, center_y + size * 0.2)

        # Центр кормы (двигатель)
        center_back = (center_x, center_y + size * 0.5)

        # Основной контур корабля
        main_points = [nose, left_wing_top, left_wing_bottom, center_back, 
                      right_wing_bottom, right_wing_top, nose]
        pygame.draw.lines(surface, self.color, closed=True, points=main_points, width=2)

        # Внутренние линии для детализации
        # Линия от носа к корме
        pygame.draw.line(surface, self.color, nose, center_back, 1)
        
        # Горизонтальные линии на корпусе
        mid_y = center_y - size * 0.05
        pygame.draw.line(surface, self.color, 
                        (center_x - size * 0.3, mid_y),
                        (center_x + size * 0.3, mid_y), 1)

        # Окно кабины (ромбовидное)
        window_points = [
            (center_x, center_y - size * 0.25),  # Верх
            (center_x - size * 0.15, center_y - size * 0.1),  # Лево
            (center_x, center_y - size * 0.05),  # Низ
            (center_x + size * 0.15, center_y - size * 0.1),  # Право
        ]
        pygame.draw.polygon(surface, self.color, window_points, 1)
        
        # Внутренняя заливка окна (полупрозрачная)
        window_color = pygame.Color(self.color.r, self.color.g, self.color.b, 80)
        pygame.draw.polygon(surface, window_color, window_points)

        # Двигатели на корме (два сопла)
        engine_left = (center_x - size * 0.15, center_y + size * 0.35)
        engine_right = (center_x + size * 0.15, center_y + size * 0.35)
        
        # Сопла двигателей
        pygame.draw.line(surface, self.color, engine_left, center_back, 2)
        pygame.draw.line(surface, self.color, engine_right, center_back, 2)
        
        # Внутренние линии сопел
        pygame.draw.line(surface, self.color,
                        (center_x - size * 0.1, center_y + size * 0.3),
                        (center_x - size * 0.2, center_y + size * 0.4), 1)
        pygame.draw.line(surface, self.color,
                        (center_x + size * 0.1, center_y + size * 0.3),
                        (center_x + size * 0.2, center_y + size * 0.4), 1)

        # Панели на крыльях
        pygame.draw.line(surface, self.color,
                        (center_x - size * 0.35, center_y),
                        (center_x - size * 0.4, center_y + size * 0.1), 1)
        pygame.draw.line(surface, self.color,
                        (center_x + size * 0.35, center_y),
                        (center_x + size * 0.4, center_y + size * 0.1), 1)

        # Декоративные точки на корпусе
        pygame.draw.circle(surface, self.color, 
                          (center_x - size * 0.25, center_y + size * 0.05), 2, 0)
        pygame.draw.circle(surface, self.color, 
                          (center_x + size * 0.25, center_y + size * 0.05), 2, 0)

        # Эффект свечения (если включен)
        if self.glow:
            self._add_glow_effect(surface, center_x, center_y, size)

        return surface

    def _add_glow_effect(
        self, 
        surface: pygame.Surface, 
        center_x: int, 
        center_y: int, 
        size: float
    ) -> None:
        """Добавить эффект свечения к кораблю."""
        # Создаем полупрозрачные слои для свечения
        glow_color = pygame.Color(self.color.r, self.color.g, self.color.b, 40)
        
        # Свечение вокруг носа
        nose_glow = (center_x, center_y - size * 0.5)
        pygame.draw.circle(surface, glow_color, nose_glow, int(size * 0.15), 0)
        
        # Свечение вокруг двигателей
        engine_glow_y = center_y + size * 0.5
        pygame.draw.circle(surface, glow_color, 
                          (center_x - size * 0.15, engine_glow_y), 
                          int(size * 0.1), 0)
        pygame.draw.circle(surface, glow_color, 
                          (center_x + size * 0.15, engine_glow_y), 
                          int(size * 0.1), 0)

    def get_rotated_sprite(self, angle: float) -> pygame.Surface:
        """
        Получить повёрнутый спрайт корабля.
        
        Args:
            angle: Угол поворота в градусах (0 = вверх)
            
        Returns:
            Повёрнутая поверхность
        """
        # pygame.transform.rotate поворачивает против часовой стрелки
        # Нам нужно повернуть на -angle, так как в игре 0° = вверх
        return pygame.transform.rotate(self.base_surface, -angle)

    def draw(
        self,
        surface: pygame.Surface,
        position: Vector2,
        angle: float = 0.0
    ) -> None:
        """
        Отрисовать корабль на поверхности.
        
        Args:
            surface: Поверхность для отрисовки
            position: Позиция корабля
            angle: Угол поворота в градусах
        """
        rotated = self.get_rotated_sprite(angle)
        rect = rotated.get_rect(center=(int(position.x), int(position.y)))
        surface.blit(rotated, rect)


class AsteroidSprite:
    """Векторный спрайт астероида в стиле полилиний."""

    def __init__(
        self,
        size: float,
        color: pygame.Color = pygame.Color("white"),
        irregularity: float = 0.3,
        seed: int | None = None
    ):
        """
        Создать спрайт астероида.
        
        Args:
            size: Размер астероида (радиус)
            color: Цвет астероида
            irregularity: Коэффициент неправильности формы (0.0-1.0)
            seed: Семя для генерации формы (для воспроизводимости)
        """
        self.size = size
        self.color = color
        self.irregularity = irregularity
        self.seed = seed if seed is not None else random.randint(0, 10000)
        
        # Генерируем форму астероида
        self.points = self._generate_points()
        self.base_surface = self._create_base_sprite()

    def _generate_points(self) -> List[Tuple[float, float]]:
        """Сгенерировать точки для неправильной формы астероида."""
        random.seed(self.seed)
        num_points = random.randint(8, 12)  # Количество вершин
        points = []

        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            
            # Базовый радиус с вариацией
            base_radius = self.size
            variation = base_radius * self.irregularity * random.uniform(-1, 1)
            radius = base_radius + variation

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))

        random.seed()  # Сбрасываем seed
        return points

    def _create_base_sprite(self) -> pygame.Surface:
        """Создать базовый спрайт астероида."""
        # Создаем поверхность с альфа-каналом
        surface_size = int(self.size * 2.5)
        surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)

        center_x, center_y = surface_size // 2, surface_size // 2

        # Смещаем точки относительно центра
        screen_points = [
            (int(center_x + x), int(center_y + y))
            for x, y in self.points
        ]

        # Рисуем контур астероида (полилиния)
        pygame.draw.lines(
            surface,
            self.color,
            closed=True,
            points=screen_points,
            width=2
        )

        # Добавляем несколько внутренних линий для детализации
        if len(screen_points) > 3:
            # Рисуем несколько случайных линий внутри
            for _ in range(2):
                p1 = random.choice(screen_points)
                p2 = random.choice(screen_points)
                if p1 != p2:
                    pygame.draw.line(surface, self.color, p1, p2, 1)

        return surface

    def get_rotated_sprite(self, angle: float) -> pygame.Surface:
        """
        Получить повёрнутый спрайт астероида.
        
        Args:
            angle: Угол поворота в градусах
            
        Returns:
            Повёрнутая поверхность
        """
        return pygame.transform.rotate(self.base_surface, -angle)

    def draw(
        self,
        surface: pygame.Surface,
        position: Vector2,
        angle: float = 0.0
    ) -> None:
        """
        Отрисовать астероид на поверхности.
        
        Args:
            surface: Поверхность для отрисовки
            position: Позиция астероида
            angle: Угол поворота в градусах
        """
        rotated = self.get_rotated_sprite(angle)
        rect = rotated.get_rect(center=(int(position.x), int(position.y)))
        surface.blit(rotated, rect)

