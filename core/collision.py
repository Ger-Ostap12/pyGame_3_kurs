from typing import Optional

import pygame


def rects_collide(rect_a: pygame.Rect, rect_b: pygame.Rect) -> bool:
    """Проверка пересечения двух прямоугольников."""
    return rect_a.colliderect(rect_b)


def masks_collide(
    mask_a: pygame.Mask,
    mask_b: pygame.Mask,
    offset: tuple[int, int],
) -> bool:
    """
    Проверка пересечения двух масок.

    offset: смещение mask_b относительно mask_a (dx, dy).
    """
    return mask_a.overlap(mask_b, offset) is not None
