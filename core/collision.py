from __future__ import annotations

from typing import Callable, Iterable, List, Tuple

import pygame

from .game_object import GameObject


def rects_collide(rect_a: pygame.Rect, rect_b: pygame.Rect) -> bool:
    """Проверка пересечения двух прямоугольников."""
    return rect_a.colliderect(rect_b)


def masks_collide(
    mask_a: pygame.Mask,
    mask_b: pygame.Mask,
    offset: Tuple[int, int],
) -> bool:
    """Проверка пересечения двух масок с учётом смещения."""
    return mask_a.overlap(mask_b, offset) is not None


def check_collisions(
    group_a: Iterable[GameObject],
    group_b: Iterable[GameObject],
    on_hit: Callable[[GameObject, GameObject], None],
) -> None:
    """
    Перебрать объекты двух групп и вызвать on_hit(a, b), если они столкнулись.

    Сначала используется проверка по Rect, при наличии масок — уточнение по маскам.
    """
    list_a: List[GameObject] = [obj for obj in group_a if obj.is_alive()]
    list_b: List[GameObject] = [obj for obj in group_b if obj.is_alive()]

    for a in list_a:
        rect_a = a.get_rect()
        mask_a = a.get_mask()

        for b in list_b:
            if a is b or not b.is_alive():
                continue

            rect_b = b.get_rect()
            if not rects_collide(rect_a, rect_b):
                continue

            mask_b = b.get_mask()
            if mask_a is not None and mask_b is not None:
                offset = (
                    int(rect_b.x - rect_a.x),
                    int(rect_b.y - rect_a.y),
                )
                if not masks_collide(mask_a, mask_b, offset):
                    continue

            on_hit(a, b)