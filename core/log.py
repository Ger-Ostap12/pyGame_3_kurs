"""Простое логирование."""

from __future__ import annotations

import datetime
import sys
from typing import Any


def log(*args: Any) -> None:
    """
    Простое логирование с таймстампом в stdout.

    Args:
        *args: Аргументы для логирования.
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    message = " ".join(str(a) for a in args)
    sys.stdout.write(f"[{timestamp}] {message}\n")
    sys.stdout.flush()