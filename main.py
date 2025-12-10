"""Точка входа в игру Asteroids (3-й курс).

Запускает основной цикл игры, инициализирует pygame и управляет
переключением состояний через Game.
"""

import pygame

from core.game import Game


def main() -> None:
    """Основная функция запуска игры."""
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()