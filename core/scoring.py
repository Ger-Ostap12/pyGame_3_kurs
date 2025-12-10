"""Система очков за уничтожение врагов."""

from __future__ import annotations


class ScoringSystem:
    """Система начисления очков за уничтожение врагов."""

    # Очки за уничтожение врагов
    SMALL_SAUCER_POINTS = 10   # Очки за маленькую тарелку
    LARGE_SAUCER_POINTS = 25   # Очки за большую тарелку
    LARGE_ASTEROID_POINTS = 20
    MEDIUM_ASTEROID_POINTS = 50
    SMALL_ASTEROID_POINTS = 100

    @staticmethod
    def get_points_for_enemy(enemy_type: type) -> int:
        """
        Получить очки за тип врага.

        Args:
            enemy_type: Класс врага.

        Returns:
            Очки.
        """
        from enemies import LargeSaucer, SmallSaucer
        from asteroids import Asteroid, AsteroidSize

        if enemy_type == SmallSaucer:
            return ScoringSystem.SMALL_SAUCER_POINTS
        elif enemy_type == LargeSaucer:
            return ScoringSystem.LARGE_SAUCER_POINTS
        elif enemy_type == Asteroid:
            # Тип Asteroid без учета размера; уточняется по экземпляру
            return ScoringSystem.LARGE_ASTEROID_POINTS
        else:
            return 0

    @staticmethod
    def get_points_for_enemy_instance(enemy) -> int:
        """
        Получить очки за экземпляр врага.

        Args:
            enemy: Экземпляр врага.

        Returns:
            Очки.
        """
        from asteroids import Asteroid, AsteroidSize

        if isinstance(enemy, Asteroid):
            if enemy.size == AsteroidSize.LARGE:
                return ScoringSystem.LARGE_ASTEROID_POINTS
            if enemy.size == AsteroidSize.MEDIUM:
                return ScoringSystem.MEDIUM_ASTEROID_POINTS
            return ScoringSystem.SMALL_ASTEROID_POINTS

        return ScoringSystem.get_points_for_enemy(type(enemy))