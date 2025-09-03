#!/usr/bin/env python3
"""Menu Scene - Сцена главного меню (минимальная рабочая версия)
Используется базовый класс Scene из локального scene_manager.
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
    # Заглушки для отсутствия Panda3D
    class OnscreenText:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def setText(self, *args, **kwargs):
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


class MenuScene(Scene):
    """Сцена главного меню"""

    def __init__(self) -> None:
        super().__init__("menu")
        self.title_text: Optional[OnscreenText] = None
        self.start_button: Optional[DirectButton] = None
        self.settings_button: Optional[DirectButton] = None
        self.quit_button: Optional[DirectButton] = None

    def initialize(self) -> bool:
        try:
            logger.info("Инициализация MenuScene...")
            # Создаем минимальные UI элементы, если доступен Panda3D
            if PANDA_AVAILABLE:
                self.title_text = OnscreenText(
                    text="AI-EVOLVE: Enhanced Edition",
                    pos=(0.0, 0.8),
                    scale=0.08,
                    fg=(1.0, 1.0, 1.0, 1.0),
                    align=TextNode.ACenter,
                )
                # Кнопки могут требовать parent=aspect2d, но для минимальной версии опускаем
                self.start_button = DirectButton(text="Start",
                                                pos=(0, 0, 0.3),
                                                scale=0.08,
                                                command=self._start_game)
                self.settings_button = DirectButton(text="Settings",
                                                   pos=(0, 0, 0.1),
                                                   scale=0.08,
                                                   command=self._open_settings)
                self.quit_button = DirectButton(text="Quit",
                                                pos=(0, 0, -0.1),
                                                scale=0.08,
                                                command=self._quit_game)
            self.initialized = True
            logger.info("MenuScene инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации MenuScene: {e}")
            return False

    def _start_game(self) -> None:
        if self.scene_manager:
            logger.info("Переключение на игровую сцену")
            # Идентификатор сцены игрового мира
            self.scene_manager.load_scene("game_world")

    def _open_settings(self) -> None:
        if self.scene_manager:
            logger.info("Переключение на сцену настроек")
            self.scene_manager.load_scene("settings")

    def _quit_game(self) -> None:
        logger.info("Выход из игры запрошен")
        # Фактический выход из приложения должен обрабатываться лаунчером/движком

    def update(self, delta_time: float) -> None:
        # Минимальная логика обновления
        return

    def render(self, render_node: Any) -> None:
        # UI рендерится Panda3D автоматически; оставляем заглушку
        return

    def handle_event(self, event: Any) -> None:
        # Обработка событий для кнопок обрабатывается DirectGUI
        return

    def cleanup(self) -> None:
        try:
            if self.title_text:
                self.title_text.destroy()
            if self.start_button:
                self.start_button.destroy()
            if self.settings_button:
                self.settings_button.destroy()
            if self.quit_button:
                self.quit_button.destroy()
        finally:
            super().cleanup()
