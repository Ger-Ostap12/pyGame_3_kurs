"""Система очков за уничтожение врагов."""

from __future__ import annotations


class ScoringSystem:
    """Система начисления очков за уничтожение врагов."""

    # Очки за уничтожение врагов
    SMALL_SAUCER_POINTS = 10  # Очки за маленькую тарелку
    LARGE_SAUCER_POINTS = 25  # Очки за большую тарелку

    @staticmethod
    def get_points_for_enemy(enemy_type: type) -> int:
        """
        Получить количество очков за уничтожение врага.

        Args:
            enemy_type: Тип врага (класс)

        Returns:
            Количество очков за уничтожение
        """
        from enemies import LargeSaucer, SmallSaucer

        if enemy_type == SmallSaucer:
            return ScoringSystem.SMALL_SAUCER_POINTS
        elif enemy_type == LargeSaucer:
            return ScoringSystem.LARGE_SAUCER_POINTS
        else:
            return 0

    @staticmethod
    def get_points_for_enemy_instance(enemy) -> int:
        """
        Получить количество очков за уничтожение врага по экземпляру.

        Args:
            enemy: Экземпляр врага

        Returns:
            Количество очков за уничтожение
        """
        return ScoringSystem.get_points_for_enemy(type(enemy))

