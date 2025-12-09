from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

import pygame
from pygame.math import Vector2

from .config import FONT_NAME, FONT_SIZE
from .player import Player
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

        # Инициализируем UI
        self.score = 0
        self.level = 1
        self.ui_manager.set_score(0)
        self.ui_manager.set_lives(self.player.lives)
        self.ui_manager.set_level(1)
        self.ui_manager.set_next_level_score(1000)

    def exit(self) -> None:
        """При выходе очищаем игрока и графические системы."""
        self.player = None
        self.star_field = None
        self.particle_system = None
        self.ui_manager = None
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

        # Применяем wrap-around ко всем объектам
        for obj in self.game.game_objects:
            obj.wrap_around_screen(self.game.size)

        # Обновляем графические системы
        if self.star_field is not None and self.player is not None:
            player_velocity = self.player.velocity if self.player.is_alive() else Vector2(0, 0)
            self.star_field.update(dt, player_velocity)

        if self.particle_system is not None:
            self.particle_system.update(dt)

        # Обновляем UI
        if self.ui_manager is not None and self.player is not None:
            self.ui_manager.set_lives(self.player.lives)
            self.ui_manager.set_score(self.score)
            self.ui_manager.set_level(self.level)

            # Проверяем переход на следующий уровень
            if self.ui_manager.check_level_up():
                self.level += 1
                self.ui_manager.set_level(self.level)
                self.ui_manager.set_next_level_score(self.level * 1000)

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
