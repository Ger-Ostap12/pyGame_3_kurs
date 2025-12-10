"""Менеджер ввода."""

from __future__ import annotations

from typing import Set

import pygame


class Input:
    """
    Менеджер ввода.
    Хранит клавиши, которые сейчас нажаты, и те, которые были нажаты в этом кадре.
    """

    def __init__(self) -> None:
        """Инициализировать менеджер ввода."""
        self._pressed: Set[int] = set()
        self._just_pressed: Set[int] = set()

    def begin_frame(self) -> None:
        """Вызывать в начале каждого кадра."""
        self._just_pressed.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Обработать событие.

        Args:
            event: Событие pygame.
        """
        if event.type == pygame.KEYDOWN:
            key = event.key
            self._pressed.add(key)
            self._just_pressed.add(key)
        elif event.type == pygame.KEYUP:
            key = event.key
            self._pressed.discard(key)

    def is_pressed(self, key: int) -> bool:
        """
        Проверить, нажата ли клавиша.

        Args:
            key: Код клавиши.

        Returns:
            True, если клавиша нажата.
        """
        return key in self._pressed

    def was_pressed(self, key: int) -> bool:
        """
        Проверить, была ли клавиша нажата в этом кадре.

        Args:
            key: Код клавиши.

        Returns:
            True, если клавиша была нажата в этом кадре.
        """
        return key in self._just_pressed