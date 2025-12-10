"""Модуль для работы с базой данных игроков и рекордов."""

import os
import sqlite3
from typing import List, Tuple, Optional


class Database:
    """Менеджер базы данных для хранения никнеймов и рекордов."""
    
    _instance: Optional['Database'] = None
    _db_path: str = ""
    
    def __new__(cls) -> 'Database':
        """Singleton pattern - один экземпляр базы данных."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        # Путь к базе данных в папке проекта
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self._db_path = os.path.join(base_dir, "game_data.db")
        
        self._create_tables()
        self._initialized = True
        
        # Текущий игрок
        self.current_player: Optional[str] = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных."""
        return sqlite3.connect(self._db_path)
    
    def _create_tables(self) -> None:
        """Создать таблицы если их нет."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT UNIQUE NOT NULL,
                best_score INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def set_current_player(self, nickname: str) -> None:
        """Установить текущего игрока (создать если не существует)."""
        self.current_player = nickname
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Проверяем существует ли игрок
        cursor.execute('SELECT id FROM players WHERE nickname = ?', (nickname,))
        result = cursor.fetchone()
        
        if result is None:
            # Создаём нового игрока
            cursor.execute(
                'INSERT INTO players (nickname) VALUES (?)',
                (nickname,)
            )
            conn.commit()
        
        conn.close()
    
    def get_current_player(self) -> Optional[str]:
        """Получить никнейм текущего игрока."""
        return self.current_player
    
    def save_score(self, score: int) -> bool:
        """
        Сохранить результат игры. Обновляет best_score если новый результат лучше.
        
        Returns:
            True если это новый рекорд, False иначе
        """
        if self.current_player is None:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Получаем текущий лучший результат
        cursor.execute(
            'SELECT best_score FROM players WHERE nickname = ?',
            (self.current_player,)
        )
        result = cursor.fetchone()
        
        if result is None:
            conn.close()
            return False
        
        current_best = result[0]
        is_new_record = score > current_best
        
        # Обновляем статистику
        if is_new_record:
            cursor.execute(
                'UPDATE players SET best_score = ?, games_played = games_played + 1 WHERE nickname = ?',
                (score, self.current_player)
            )
        else:
            cursor.execute(
                'UPDATE players SET games_played = games_played + 1 WHERE nickname = ?',
                (self.current_player,)
            )
        
        conn.commit()
        conn.close()
        
        return is_new_record
    
    def get_best_score(self, nickname: Optional[str] = None) -> int:
        """Получить лучший результат игрока."""
        if nickname is None:
            nickname = self.current_player
        
        if nickname is None:
            return 0
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT best_score FROM players WHERE nickname = ?',
            (nickname,)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 0
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Получить таблицу лидеров (только игроки с результатом > 0)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT nickname, best_score FROM players WHERE best_score > 0 ORDER BY best_score DESC LIMIT ?',
            (limit,)
        )
        results = cursor.fetchall()
        
        conn.close()
        
        return results
    
    def player_exists(self, nickname: str) -> bool:
        """Проверить существует ли игрок."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM players WHERE nickname = ?', (nickname,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result is not None


# Глобальный экземпляр базы данных
db = Database()

