import os
import pygame

from .game import Game
from .music_manager import MusicManager

__all__ = ["Game"]

# Базовая директория проекта
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_MUSIC_DIR = os.path.join(_BASE_DIR, "assets", "music")

# Пути к музыкальным файлам
MENU_MUSIC = os.path.join(_MUSIC_DIR, "John_Towner_Williams_-_Star_Wars_-_Dujel_sudeb_73511034.mp3")
GAME_MUSIC = os.path.join(_MUSIC_DIR, "John_Williams_-_The_Imperial_March_67946881.mp3")


def _apply_music_patches() -> None:
    """Автоматически добавить музыку в меню и игру."""
    from .states import MenuState, PlayingState
    
    # === Патч для меню (Imperial March) ===
    original_menu_enter = MenuState.enter
    original_menu_exit = MenuState.exit
    
    def menu_enter(self) -> None:
        original_menu_enter(self)
        MusicManager.init()
        if os.path.exists(MENU_MUSIC):
            MusicManager.load_and_play(MENU_MUSIC, loops=-1, volume=0.5)
        else:
            print(f"\n[!] Для музыки в меню положите файл Imperial March в:\n    {_MUSIC_DIR}\n")
    
    def menu_exit(self) -> None:
        MusicManager.fadeout(500)
        original_menu_exit(self)
    
    MenuState.enter = menu_enter
    MenuState.exit = menu_exit
    
    # === Патч для игры (Duel of the Fates) ===
    original_playing_enter = PlayingState.enter
    original_playing_exit = PlayingState.exit
    
    def playing_enter(self) -> None:
        original_playing_enter(self)
        MusicManager.init()
        if os.path.exists(GAME_MUSIC):
            MusicManager.load_and_play(GAME_MUSIC, loops=-1, volume=0.4)
        else:
            print(f"\n[!] Для музыки в игре положите 'duel_of_the_fates.mp3' в:\n    {_MUSIC_DIR}\n")
    
    def playing_exit(self) -> None:
        MusicManager.fadeout(500)
        original_playing_exit(self)
    
    PlayingState.enter = playing_enter
    PlayingState.exit = playing_exit


# Применяем патчи автоматически при импорте
_apply_music_patches()
