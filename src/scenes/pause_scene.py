#!/usr/bin/env python3
"""Pause Scene - Сцена паузы (минимальная рабочая версия)
"""

import logging
from typing import Any, Optional

from .scene_manager import Scene

logger = logging.getLogger(__name__)

# Безопасные импорты Panda3D UI
try:
    from direct.gui.DirectButton import DirectButton  # type: ignore
    from direct.gui.OnscreenText import OnscreenText  # type: ignore
    from panda3d.core import TextNode  # type: ignore
    PANDA_AVAILABLE = True
except Exception:
    PANDA_AVAILABLE = False
    class OnscreenText:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def destroy(self):
            pass
    class DirectButton:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def destroy(self):
            pass
    class TextNode:  # type: ignore
        ACenter = 0


class PauseScene(Scene):
    """Сцена паузы"""

    def __init__(self) -> None:
        super().__init__("pause")
        self.pause_text: Optional[OnscreenText] = None
        self.resume_button: Optional[DirectButton] = None
        self.settings_button: Optional[DirectButton] = None
        self.menu_button: Optional[DirectButton] = None

    def initialize(self) -> bool:
        try:
            logger.info("Инициализация PauseScene...")
            if PANDA_AVAILABLE:
                self.pause_text = OnscreenText(text="Paused",
                                               pos=(0.0, 0.5), scale=0.1,
                                               fg=(1, 1, 0, 1), align=TextNode.ACenter)
                self.resume_button = DirectButton(text="Resume",
                                                  pos=(0, 0, 0.1), scale=0.07,
                                                  command=self._resume)
                self.settings_button = DirectButton(text="Settings",
                                                    pos=(0, 0, -0.1), scale=0.07,
                                                    command=self._open_settings)
                self.menu_button = DirectButton(text="Main Menu",
                                                pos=(0, 0, -0.3), scale=0.07,
                                                command=self._to_menu)
            self.initialized = True
            logger.info("PauseScene инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации PauseScene: {e}")
            return False

    def _resume(self) -> None:
        if self.scene_manager:
            logger.info("Возобновление игры")
            self.scene_manager.load_scene("game_world")

    def _open_settings(self) -> None:
        if self.scene_manager:
            logger.info("Открытие настроек")
            self.scene_manager.load_scene("settings")

    def _to_menu(self) -> None:
        if self.scene_manager:
            logger.info("Возврат в главное меню")
            self.scene_manager.load_scene("main_menu")

    def cleanup(self) -> None:
        try:
            for w in [self.pause_text, self.resume_button, self.settings_button, self.menu_button]:
                if w:
                    w.destroy()
        finally:
            super().cleanup()
