from __future__ import annotations

from typing import Dict, Tuple, Optional

import pygame

from .config import WINDOW_SIZE, FPS, BG_COLOR, TEXT_COLOR, FONT_NAME, FONT_SIZE
from .game_object import GameObject
from .input import Input
from .log import log
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
        size: Tuple[int, int] = WINDOW_SIZE,
        fps: int = FPS,
    ) -> None:
        self.size = size
        self.fps = fps

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Asteroids")

        self.clock = pygame.time.Clock()
        self.running = False

        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.bg_color = BG_COLOR
        self.text_color = TEXT_COLOR

        # Менеджер ввода
        self.input = Input()

        # Менеджер игровых объектов
        self.game_objects: list[GameObject] = []
        self.ui_objects: list[GameObject] = []

        # FSM: словарь состояний + текущее состояние
        self._states: Dict[GameStateId, BaseState] = {}
        self._current_state: BaseState | None = None
        self._init_states()

        log("Game initialized with size", self.size, "and FPS", self.fps)

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
        log("Change state to", state_id.name)

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
        log("Game loop started")

        while self.running:
            self.input.begin_frame()

            dt_ms = self.clock.tick(self.fps)
            dt = dt_ms / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

            pygame.display.flip()

        log("Game loop stopped")

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

            self.input.handle_event(event)
            self._current_state.handle_event(event)

    def _update(self, dt: float) -> None:
        if self._current_state is not None:
            self._current_state.update(dt)

    def _draw(self) -> None:
        if self._current_state is not None:
            self._current_state.draw()

        self._draw_debug_overlay()

    # --- отладочный overlay ---

    def _draw_debug_overlay(self) -> None:
        """Отрисовать только FPS в правом верхнем углу."""
        try:
            fps_value = self.clock.get_fps()
            fps_text = f"FPS: {fps_value:5.1f}"
            
            # Используем яркий цвет для лучшей видимости
            if fps_value >= 50:
                fps_color = pygame.Color("lime")
            elif fps_value >= 30:
                fps_color = pygame.Color("yellow")
            else:
                fps_color = pygame.Color("red")
            
            # Рендерим текст (используем тот же шрифт, что и в игре)
            fps_surf = self.font.render(fps_text, True, fps_color)
            
            if fps_surf is None:
                # Если шрифт не работает, используем дефолтный
                default_font = pygame.font.Font(None, 24)
                fps_surf = default_font.render(fps_text, True, fps_color)
            
            if fps_surf is None:
                return
            
            # Размещаем в правом верхнем углу (под уровнем)
            x = self.size[0] - fps_surf.get_width() - 10
            y = 80  # Под UI элементами (Score, Lives находятся на 10 и 40)
            
            # Рисуем полупрозрачный фон для лучшей читаемости
            bg_rect = pygame.Rect(x - 5, y - 2, fps_surf.get_width() + 10, fps_surf.get_height() + 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 200), (0, 0, bg_rect.width, bg_rect.height))
            self.screen.blit(bg_surface, bg_rect)
            
            # Рисуем FPS поверх фона
            self.screen.blit(fps_surf, (x, y))
        except Exception:
            # Если что-то пошло не так, просто игнорируем
            pass
