#!/usr/bin/env python3
"""Load Scene - Сцена загрузки (минимальная рабочая версия)
"""

import logging
from typing import Any, List, Optional

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
        ALeft = 1


class LoadScene(Scene):
    """Сцена загрузки сохранений"""

    def __init__(self) -> None:
        super().__init__("load_game")
        self.title_text: Optional[OnscreenText] = None
        self.load_button: Optional[DirectButton] = None
        self.delete_button: Optional[DirectButton] = None
        self.back_button: Optional[DirectButton] = None
        self.save_labels: List[OnscreenText] = []
        self.selected_index: Optional[int] = None
        self.save_files: List[dict] = []

    def initialize(self) -> bool:
        try:
            logger.info("Инициализация LoadScene...")
            self._load_save_files()
            if PANDA_AVAILABLE:
                self.title_text = OnscreenText(text="Load Game",
                                               pos=(0.0, 0.8), scale=0.08,
                                               fg=(1, 1, 1, 1), align=TextNode.ACenter)
                self._create_save_list()
                self.load_button = DirectButton(text="Load",
                                                pos=(-0.3, 0, -0.8), scale=0.06,
                                                command=self._load_selected)
                self.delete_button = DirectButton(text="Delete",
                                                  pos=(0.0, 0, -0.8), scale=0.06,
                                                  command=self._delete_selected)
                self.back_button = DirectButton(text="Back",
                                                pos=(0.3, 0, -0.8), scale=0.06,
                                                command=self._go_back)
            self.initialized = True
            logger.info("LoadScene инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации LoadScene: {e}")
            return False

    def _load_save_files(self) -> None:
        # Имитация наличия сохранений
        self.save_files = [
            {"name": "Save 1", "date": "2025-09-02 14:30", "level": 5},
            {"name": "Save 2", "date": "2025-09-01 18:45", "level": 3},
            {"name": "Auto Save", "date": "2025-09-02 15:20", "level": 4},
        ]

    def _create_save_list(self) -> None:
        y = 0.4
        self.save_labels = []
        for idx, save in enumerate(self.save_files):
            label = OnscreenText(text=f"{save['name']} - L{save['level']} ({save['date']})",
                                 pos=(-0.8, y), scale=0.05,
                                 fg=(1, 1, 0.7, 1), align=TextNode.ALeft)
            self.save_labels.append(label)
            # Простая зона выбора по индексу: в минимальной версии выбираем первый
            if self.selected_index is None:
                self.selected_index = 0
            y -= 0.1

    def _load_selected(self) -> None:
        if self.selected_index is not None and 0 <= self.selected_index < len(self.save_files):
            save_name = self.save_files[self.selected_index]["name"]
            logger.info(f"Загрузка сохранения: {save_name}")
            if self.scene_manager:
                self.scene_manager.load_scene("game_world")
        else:
            logger.warning("Сохранение не выбрано")

    def _delete_selected(self) -> None:
        if self.selected_index is not None and 0 <= self.selected_index < len(self.save_files):
            save_name = self.save_files[self.selected_index]["name"]
            logger.info(f"Удаление сохранения: {save_name}")
        else:
            logger.warning("Сохранение не выбрано для удаления")

    def _go_back(self) -> None:
        if self.scene_manager:
            logger.info("Возврат в меню")
            self.scene_manager.load_scene("main_menu")

    def cleanup(self) -> None:
        try:
            for w in [self.title_text, self.load_button, self.delete_button, self.back_button]:
                if w:
                    w.destroy()
            for lbl in self.save_labels:
                lbl.destroy()
            self.save_labels = []
        finally:
            super().cleanup()
