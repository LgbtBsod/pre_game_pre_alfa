#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LEGACY shim: экспортируем единую систему достижений из core/achievement_system.py
для устранения дублирования. Оставлено для обратной совместимости импортов.
"""

from core.achievement_system import AchievementSystem  # re-export

__all__ = ["AchievementSystem"]
