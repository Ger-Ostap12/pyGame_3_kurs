from __future__ import annotations

from typing import Dict, Tuple

import pygame

from .game_object import GameObject
from .input import Input
from .states import (
    BaseState,
    GameStateId,
    MenuState,
    PlayingState,
    GameOverState,
)


class Game:
    def __init__(
        self,
        size: Tuple[int, int] = (800, 600),
        fps: int = 60,
    ) -> None:
        self.size = size
        self.fps = fps

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Asteroids")

        self.clock = pygame.time.Clock()
        self.running = False

        self.font = pygame.font.SysFont("consolas", 18)
        self.bg_color = pygame.Color("black")
        self.text_color = pygame.Color("white")

        # Менеджер ввода
        self.input = Input()

        # Менеджер игровых объектов
        self.game_objects: list[GameObject] = []
        self.ui_objects: list[GameObject] = []

        # FSM: словарь состояний + текущее состояние
        self._states: Dict[GameStateId, BaseState] = {}
        self._current_state: BaseState | None = None
        self._init_states()

    # --- управление состояниями ---

    def _init_states(self) -> None:
        self._states = {
            GameStateId.MENU: MenuState(self),
            GameStateId.PLAYING: PlayingState(self),
            GameStateId.GAME_OVER: GameOverState(self),
        }
        self.change_state(GameStateId.MENU)

    def change_state(self, state_id: GameStateId) -> None:
        if self._current_state is not None:
            self._current_state.exit()

        self._current_state = self._states[state_id]
        self._current_state.enter()

    # --- менеджер объектов ---

    def add_object(self, obj: GameObject, ui: bool = False) -> None:
        if ui:
            self.ui_objects.append(obj)
        else:
            self.game_objects.append(obj)

    def clear_objects(self) -> None:
        self.game_objects.clear()
        self.ui_objects.clear()

    def update_objects(self, dt: float) -> None:
        for obj in self.game_objects:
            if obj.is_alive():
                obj.update(dt)
        self.game_objects = [obj for obj in self.game_objects if obj.is_alive()]

        for obj in self.ui_objects:
            if obj.is_alive():
                obj.update(dt)
        self.ui_objects = [obj for obj in self.ui_objects if obj.is_alive()]

    def draw_objects(self) -> None:
        for obj in self.game_objects:
            obj.draw(self.screen)
        for obj in self.ui_objects:
            obj.draw(self.screen)

    # --- основной цикл ---

    def run(self) -> None:
        self.running = True

        while self.running:
            self.input.begin_frame()

            dt_ms = self.clock.tick(self.fps)
            dt = dt_ms / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

            pygame.display.flip()

    def stop(self) -> None:
        self.running = False

    # --- внутренние шаги цикла ---

    def _handle_events(self) -> None:
        if self._current_state is None:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return

            # сначала обновляем состояние ввода
            self.input.handle_event(event)
            # потом отдаём событие текущему состоянию
            self._current_state.handle_event(event)

    def _update(self, dt: float) -> None:
        if self._current_state is not None:
            self._current_state.update(dt)

    def _draw(self) -> None:
        if self._current_state is not None:
            self._current_state.draw()

        # FPS поверх всего
        fps = self.clock.get_fps()
        fps_surf = self.font.render(f"FPS: {fps:5.1f}", True, self.text_color)
        self.screen.blit(fps_surf, (10, 10))