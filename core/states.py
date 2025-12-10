from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

import pygame
from pygame.math import Vector2

from .config import FONT_NAME, FONT_SIZE
from .player import Player
from .scoring import ScoringSystem
from .collision import check_collisions
from asteroids import Asteroid, AsteroidField
from enemies import LargeSaucer, SmallSaucer
from graphics.particles import ParticleSystem
from graphics.stars import StarField
from graphics.ui import UIManager

if TYPE_CHECKING:
    from .game import Game


class GameStateId(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class BaseState(ABC):
    """Базовый класс для состояний игры (меню/игра/game over и т.п.)."""

    def __init__(self, game: Game) -> None:
        self.game = game

    @property
    @abstractmethod
    def id(self) -> GameStateId:
        """Идентификатор состояния (для переключения)."""
        raise NotImplementedError

    def enter(self) -> None:
        """Вызывается при входе в состояние."""
        pass

    def exit(self) -> None:
        """Вызывается при выходе из состояния."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Обработка одного события pygame."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Обновление логики состояния."""
        pass

    @abstractmethod
    def draw(self) -> None:
        """Отрисовка состояния."""
        pass


class MenuState(BaseState):
    @property
    def id(self) -> GameStateId:
        return GameStateId.MENU

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state(GameStateId.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.stop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        font = self.game.font
        title = font.render("ASTEROIDS (MENU)", True, self.game.text_color)
        hint = font.render("Enter - start, Esc - exit", True, self.game.text_color)

        w, h = self.game.size
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 3))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h // 3 + 30))


class PlayingState(BaseState):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.player: Optional[Player] = None
        self.star_field: Optional[StarField] = None
        self.particle_system: Optional[ParticleSystem] = None
        self.ui_manager: Optional[UIManager] = None
        self.asteroid_field: Optional[AsteroidField] = None
        self.score = 0
        self.level = 1

    @property
    def id(self) -> GameStateId:
        return GameStateId.PLAYING

    def enter(self) -> None:
        """При входе в состояние создаем игрока и графические системы."""
        # Очищаем все старые объекты
        self.game.clear_objects()

        # Создаем графические системы
        self.star_field = StarField(self.game.size, star_count=200, num_layers=3)
        self.particle_system = ParticleSystem()
        self.ui_manager = UIManager(self.game.size, FONT_NAME, FONT_SIZE)

        # Создаем игрока в центре экрана
        center = Vector2(self.game.size[0] / 2, self.game.size[1] / 2)
        self.player = Player(position=center, screen_size=self.game.size)

        # Добавляем игрока в менеджер объектов
        self.game.add_object(self.player)

        # Создаем поле астероидов
        self.asteroid_field = AsteroidField(self.game.size, self.game.add_object)
        self.asteroid_field.reset()
        self.asteroid_field.spawn_wave(center)

        # Создаем врагов
        screen_width, screen_height = self.game.size
        player_x, player_y = center.x, center.y

        # Минимальное расстояние от игрока для спавна
        min_distance = 200
        max_distance = 400

        # Функция для получения позиции игрока (общая для всех тарелок)
        def get_player_pos():
            if self.player is not None and self.player.is_alive():
                return self.player.position
            return None

        # Создаем 2 большие тарелки - спавним их ближе к игроку для видимости
        for i in range(2):
            # Спавним врагов в видимой области рядом с игроком
            angle = (i * 180) + random.uniform(-30, 30)  # Разные углы от игрока
            distance = random.uniform(250, 350)  # Расстояние от игрока
            angle_rad = math.radians(angle)
            pos = center + Vector2(
                math.cos(angle_rad) * distance,
                math.sin(angle_rad) * distance
            )
            # Ограничиваем позицию экраном
            pos.x = max(50, min(screen_width - 50, pos.x))
            pos.y = max(50, min(screen_height - 50, pos.y))

            large_saucer = LargeSaucer(pos, self.game.size, get_player_pos)
            self.game.add_object(large_saucer)

        # Создаем 2 маленькие тарелки с прицельной стрельбой - спавним их ближе к игроку
        for i in range(2):
            # Спавним врагов в видимой области рядом с игроком
            angle = (i * 180) + 90 + random.uniform(-30, 30)  # Разные углы от игрока
            distance = random.uniform(250, 350)  # Расстояние от игрока
            angle_rad = math.radians(angle)
            pos = center + Vector2(
                math.cos(angle_rad) * distance,
                math.sin(angle_rad) * distance
            )
            # Ограничиваем позицию экраном
            pos.x = max(50, min(screen_width - 50, pos.x))
            pos.y = max(50, min(screen_height - 50, pos.y))

            small_saucer = SmallSaucer(pos, self.game.size, get_player_pos)
            self.game.add_object(small_saucer)

        # Инициализируем UI
        self.score = 0
        self.level = 1
        self.ui_manager.set_score(0)

    def exit(self) -> None:
        """При выходе очищаем игрока и графические системы."""
        self.player = None
        self.star_field = None
        self.particle_system = None
        self.ui_manager = None
        self.asteroid_field = None
        self.game.clear_objects()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Пауза или выход в меню
                self.game.change_state(GameStateId.MENU)
            elif event.key == pygame.K_t:
                # Тестовая клавиша для демонстрации взрыва
                if self.player is not None and self.particle_system is not None:
                    self.particle_system.add_explosion(
                        self.player.position,
                        color=pygame.Color("orange"),
                        particle_count=40,
                        speed=250.0,
                        lifetime=0.6
                    )

    def update(self, dt: float) -> None:
        # Обновляем игрока (обработка ввода)
        if self.player is not None and self.player.is_alive():
            self.player.handle_input(self.game.input, dt)

        # Обновляем все объекты через менеджер
        self.game.update_objects(dt)

        # Проверяем коллизии между пулями игрока и врагами
        if self.player is not None and self.player.is_alive():
            player_bullets = self.player.get_bullets()
            asteroids = [
                obj for obj in self.game.game_objects
                if isinstance(obj, Asteroid) and obj.is_alive()
            ]
            enemies = [
                obj for obj in self.game.game_objects
                if isinstance(obj, (LargeSaucer, SmallSaucer)) and obj.is_alive()
            ]

            # Простая проверка коллизий на основе расстояния (радиусная проверка)
            for bullet in player_bullets:
                if not bullet.is_alive():
                    continue

                for enemy in enemies:
                    if not enemy.is_alive():
                        continue

                    # Вычисляем расстояние между центрами
                    distance = (bullet.position - enemy.position).length()
                    # Проверяем коллизию (сумма радиусов)
                    collision_distance = bullet.radius + enemy.radius

                    if distance <= collision_distance:
                        # Попадание! Уничтожаем врага
                        enemy.kill()
                        # Уничтожаем пулю
                        bullet.kill()
                        # Начисляем очки
                        points = ScoringSystem.get_points_for_enemy_instance(enemy)
                        self.score += points
                        # Создаём взрыв
                        if self.particle_system is not None:
                            self.particle_system.add_explosion(
                                enemy.position,
                                color=pygame.Color("orange"),
                                particle_count=30,
                                speed=200.0,
                                lifetime=0.5
                            )
                        # Одна пуля может попасть только в одного врага
                        break

                if not bullet.is_alive():
                    # Пуля уже использована на враге
                    continue

                # Коллизии пуль и астероидов
                for asteroid in asteroids:
                    if not asteroid.is_alive():
                        continue

                    distance = (bullet.position - asteroid.position).length()
                    collision_distance = bullet.radius + asteroid.radius
                    if distance <= collision_distance:
                        self._destroy_asteroid(asteroid)
                        bullet.kill()
                        points = ScoringSystem.get_points_for_enemy_instance(asteroid)
                        self.score += points
                        if self.particle_system is not None:
                            self.particle_system.add_explosion(
                                asteroid.position,
                                color=pygame.Color("gray"),
                                particle_count=25,
                                speed=180.0,
                                lifetime=0.4
                            )
                        break

        # Применяем wrap-around ко всем объектам
        for obj in self.game.game_objects:
            obj.wrap_around_screen(self.game.size)

        # Проверяем столкновения игрока и астероидов
        if self.player is not None and self.player.is_alive():
            asteroids = [
                obj for obj in self.game.game_objects
                if isinstance(obj, Asteroid) and obj.is_alive()
            ]
            for asteroid in asteroids:
                distance = (self.player.position - asteroid.position).length()
                if distance <= self.player.radius + asteroid.radius:
                    self._destroy_asteroid(asteroid)
                    points = ScoringSystem.get_points_for_enemy_instance(asteroid)
                    self.score += points
                    if self.particle_system is not None:
                        self.particle_system.add_explosion(
                            asteroid.position,
                            color=pygame.Color("gray"),
                            particle_count=25,
                            speed=200.0,
                            lifetime=0.45
                        )
                    # Наносим урон игроку
                    still_alive = self.player.take_damage()
                    if not still_alive:
                        break

        # Обновляем графические системы
        if self.star_field is not None and self.player is not None:
            player_velocity = self.player.velocity if self.player.is_alive() else Vector2(0, 0)
            self.star_field.update(dt, player_velocity)

        if self.particle_system is not None:
            self.particle_system.update(dt)

        # Обновляем UI
        if self.ui_manager is not None:
            self.ui_manager.set_score(self.score)

        # Генерация новых волн астероидов
        if self.asteroid_field is not None:
            active_asteroids = [
                obj for obj in self.game.game_objects
                if isinstance(obj, Asteroid) and obj.is_alive()
            ]
            if len(active_asteroids) == 0:
                self.level += 1
                player_pos = self.player.position if (self.player is not None and self.player.is_alive()) else None
                self.asteroid_field.next_wave(player_pos)

        # Проверяем, жив ли игрок
        if self.player is not None and not self.player.is_alive():
            # Создаём взрыв при смерти игрока
            if self.particle_system is not None:
                self.particle_system.add_explosion(
                    self.player.position,
                    color=pygame.Color("red"),
                    particle_count=50,
                    speed=300.0,
                    lifetime=0.8
                )
            # Переходим в Game Over
            self.game.change_state(GameStateId.GAME_OVER)

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        # Рисуем фоновые звёзды (параллакс)
        if self.star_field is not None:
            self.star_field.draw(screen)

        # Рисуем игровые объекты (включая игрока)
        self.game.draw_objects()

        # Рисуем эффекты частиц (взрывы)
        if self.particle_system is not None:
            self.particle_system.draw(screen)

        # Рисуем UI (счёт, жизни, уровень)
        if self.ui_manager is not None:
            self.ui_manager.draw(screen)

        # Отображаем подсказки управления
        self._draw_controls_hint()

    def _destroy_asteroid(self, asteroid: Asteroid) -> None:
        """Удалить астероид и добавить его осколки в игру."""
        if not asteroid.is_alive():
            return
        asteroid.kill()
        fragments = asteroid.split()
        for child in fragments:
            self.game.add_object(child)

    def _draw_controls_hint(self) -> None:
        """Отрисовка подсказок по управлению."""
        font = pygame.font.Font(None, 24)
        hints = [
            "Controls:",
            "Arrow Keys / WASD - Move & Rotate",
            "Space - Shoot",
            "Shift - Hyperspace",
            "ESC - Menu"
        ]

        x, y = self.game.size[0] - 300, self.game.size[1] - 150
        for hint in hints:
            text_surf = font.render(hint, True, pygame.Color("gray"))
            self.game.screen.blit(text_surf, (x, y))
            y += 25


class GameOverState(BaseState):
    @property
    def id(self) -> GameStateId:
        return GameStateId.GAME_OVER

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.change_state(GameStateId.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state(GameStateId.MENU)

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        font = self.game.font
        title_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2)

        title = title_font.render("GAME OVER", True, pygame.Color("red"))
        hint1 = font.render("R - restart", True, self.game.text_color)
        hint2 = font.render("Esc - menu", True, self.game.text_color)

        w, h = self.game.size
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 3))
        screen.blit(hint1, (w // 2 - hint1.get_width() // 2, h // 3 + 80))
        screen.blit(hint2, (w // 2 - hint2.get_width() // 2, h // 3 + 110))
