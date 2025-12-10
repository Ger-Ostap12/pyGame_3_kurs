"""
Модуль управления музыкой в игре.
Позволяет загружать и проигрывать фоновую музыку.
"""

import os
import pygame


class MusicManager:
    """Менеджер фоновой музыки и звуковых эффектов."""
    
    _initialized: bool = False
    _current_track: str | None = None
    _volume: float = 0.5
    _sounds: dict[str, pygame.mixer.Sound] = {}
    
    @classmethod
    def init(cls) -> None:
        """Инициализация микшера pygame для музыки."""
        if not cls._initialized:
            pygame.mixer.init()
            cls._initialized = True
    
    @classmethod
    def load_and_play(cls, filepath: str, loops: int = -1, volume: float | None = None) -> bool:
        """
        Загрузить и проиграть музыкальный файл.
        
        Args:
            filepath: Путь к музыкальному файлу
            loops: Количество повторений (-1 для бесконечного)
            volume: Громкость от 0.0 до 1.0
            
        Returns:
            True если музыка загружена и запущена, False в случае ошибки
        """
        cls.init()
        
        if not os.path.exists(filepath):
            print(f"[MusicManager] Файл не найден: {filepath}")
            return False
        
        try:
            pygame.mixer.music.load(filepath)
            if volume is not None:
                cls._volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(cls._volume)
            pygame.mixer.music.play(loops)
            cls._current_track = filepath
            print(f"[MusicManager] Играет: {os.path.basename(filepath)}")
            return True
        except pygame.error as e:
            print(f"[MusicManager] Ошибка загрузки музыки: {e}")
            return False
    
    @classmethod
    def stop(cls) -> None:
        """Остановить воспроизведение музыки."""
        if cls._initialized:
            pygame.mixer.music.stop()
            cls._current_track = None
            print("[MusicManager] Музыка остановлена")
    
    @classmethod
    def pause(cls) -> None:
        """Поставить музыку на паузу."""
        if cls._initialized:
            pygame.mixer.music.pause()
    
    @classmethod
    def unpause(cls) -> None:
        """Продолжить воспроизведение после паузы."""
        if cls._initialized:
            pygame.mixer.music.unpause()
    
    @classmethod
    def set_volume(cls, volume: float) -> None:
        """
        Установить громкость.
        
        Args:
            volume: Громкость от 0.0 до 1.0
        """
        cls._volume = max(0.0, min(1.0, volume))
        if cls._initialized:
            pygame.mixer.music.set_volume(cls._volume)
    
    @classmethod
    def is_playing(cls) -> bool:
        """Проверить, играет ли музыка."""
        if cls._initialized:
            return pygame.mixer.music.get_busy()
        return False
    
    @classmethod
    def fadeout(cls, time_ms: int = 1000) -> None:
        """
        Плавно затухить музыку.
        
        Args:
            time_ms: Время затухания в миллисекундах
        """
        if cls._initialized:
            pygame.mixer.music.fadeout(time_ms)
            cls._current_track = None
    
    @classmethod
    def load_sound(cls, name: str, filepath: str, volume: float = 0.5) -> bool:
        """
        Загрузить звуковой эффект.
        
        Args:
            name: Имя звука для последующего воспроизведения
            filepath: Путь к звуковому файлу
            volume: Громкость от 0.0 до 1.0
            
        Returns:
            True если звук загружен, False в случае ошибки
        """
        cls.init()
        
        if not os.path.exists(filepath):
            print(f"[MusicManager] Звук не найден: {filepath}")
            return False
        
        try:
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(max(0.0, min(1.0, volume)))
            cls._sounds[name] = sound
            return True
        except pygame.error as e:
            print(f"[MusicManager] Ошибка загрузки звука: {e}")
            return False
    
    @classmethod
    def play_sound(cls, name: str) -> None:
        """
        Воспроизвести звуковой эффект.
        
        Args:
            name: Имя звука (предварительно загруженного через load_sound)
        """
        if name in cls._sounds:
            cls._sounds[name].play()

