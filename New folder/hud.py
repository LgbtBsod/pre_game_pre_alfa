#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shim-модуль HUD: экспортирует улучшенную реализацию из `enhanced_hud`.
Устранено случайное внедрение постороннего кода. Единственная ответственность — ре-экспорт.
"""

from enhanced_hud import EnhancedHUD as HUD

__all__ = ["HUD"]
