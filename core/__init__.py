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
GAME_OVER_MUSIC = os.path.join(_MUSIC_DIR, "DOORS_Roblox_OST_-_Guiding_Light_75159771.mp3")
SHOOT_SOUND = os.path.join(_MUSIC_DIR, "the-sound-of-a-laser-shot.mp3")
DAMAGE_SOUND = os.path.join(_MUSIC_DIR, "Приглушенный удар, но решительный.mp3")
DEATH_SOUND = os.path.join(_MUSIC_DIR, "Castlevania – Death_ Музыка из игры Dendy.mp3")


def _apply_music_patches() -> None:
    """Автоматически добавить музыку в меню, игру, экран поражения и звук выстрела."""
    from .states import PlayingState
    from .ui_states import MenuState, GameOverState
    from .player import Player
    
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
    
    # === Патч для экрана поражения (Guiding Light) ===
    original_gameover_enter = GameOverState.enter
    original_gameover_exit = GameOverState.exit
    
    def gameover_enter(self) -> None:
        original_gameover_enter(self)
        MusicManager.init()
        if os.path.exists(GAME_OVER_MUSIC):
            MusicManager.load_and_play(GAME_OVER_MUSIC, loops=-1, volume=0.5)
        else:
            print(f"\n[!] Для музыки на экране поражения положите файл в:\n    {_MUSIC_DIR}\n")
    
    def gameover_exit(self) -> None:
        MusicManager.fadeout(500)
        original_gameover_exit(self)
    
    GameOverState.enter = gameover_enter
    GameOverState.exit = gameover_exit
    
    # === Загрузка звуковых эффектов ===
    MusicManager.init()
    if os.path.exists(SHOOT_SOUND):
        MusicManager.load_sound("shoot", SHOOT_SOUND, volume=0.3)
    if os.path.exists(DAMAGE_SOUND):
        MusicManager.load_sound("damage", DAMAGE_SOUND, volume=0.5)
    if os.path.exists(DEATH_SOUND):
        MusicManager.load_sound("death", DEATH_SOUND, volume=0.6)
    
    # === Патч для звука выстрела игрока ===
    original_player_shoot = Player.shoot
    
    def player_shoot(self) -> None:
        # Проверяем cooldown до вызова оригинального метода
        if self.shoot_timer > 0:
            return
        original_player_shoot(self)
        MusicManager.play_sound("shoot")
    
    Player.shoot = player_shoot
    
    # === Патч для звуков урона и смерти игрока ===
    original_player_take_damage = Player.take_damage
    
    def player_take_damage(self) -> bool:
        # Если неуязвим, просто вызываем оригинал
        if self.is_invincible():
            return original_player_take_damage(self)
        
        # Вызываем оригинальный метод
        still_alive = original_player_take_damage(self)
        
        if still_alive:
            # Игрок получил урон, но выжил
            MusicManager.play_sound("damage")
        else:
            # Игрок умер
            MusicManager.play_sound("death")
        
        return still_alive
    
    Player.take_damage = player_take_damage


# Применяем патчи автоматически при импорте
_apply_music_patches()
