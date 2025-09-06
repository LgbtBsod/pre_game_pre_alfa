#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEGACY shim: экспортируем StartScreen из screens/start_screen_new.py
для устранения дублирования и единообразного использования.
"""

from .start_screen_new import StartScreen  # re-export

__all__ = ["StartScreen"]
