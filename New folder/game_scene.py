#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEGACY shim: экспортируем улучшенную сцену из game_scene_new.py
для единообразного использования и устранения дублирования.
"""

from game_scene_new import GameScene  # re-export

__all__ = ["GameScene"]


