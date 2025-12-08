from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

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
        raise NotImplementedError

    @abstractmethod
    def draw(self) -> None:
        """Отрисовка состояния."""
        raise NotImplementedError


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
    @property
    def id(self) -> GameStateId:
        return GameStateId.PLAYING

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.stop()
            # Временно для теста: по G — Game Over
            if event.key == pygame.K_g:
                self.game.change_state(GameStateId.GAME_OVER)

    def update(self, dt: float) -> None:
        # Здесь позже будут игрок, астероиды и т.п.
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        font = self.game.font
        label = font.render("PLAYING (press G for Game Over)", True, self.game.text_color)

        w, h = self.game.size
        screen.blit(label, (w // 2 - label.get_width() // 2, h // 2))


class GameOverState(BaseState):
    @property
    def id(self) -> GameStateId:
        return GameStateId.GAME_OVER

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.change_state(GameStateId.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.stop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        font = self.game.font
        title = font.render("GAME OVER", True, self.game.text_color)
        hint = font.render("R - restart, Esc - exit", True, self.game.text_color)

        w, h = self.game.size
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 3))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h // 3 + 30))
