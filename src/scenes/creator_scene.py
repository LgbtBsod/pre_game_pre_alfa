#!/usr/bin/env python3
"""Creator Scene - Сцена режима "Творец мира" (минимальная рабочая версия)
"""

import logging
from typing import Any, Optional

from .scene_manager import Scene

logger = logging.getLogger(__name__)

# Безопасные импорты Panda3D UI/графики
try:
    from direct.gui.DirectButton import DirectButton  # type: ignore
    from direct.gui.DirectFrame import DirectFrame  # type: ignore
    from direct.gui.DirectLabel import DirectLabel  # type: ignore
    from direct.gui.OnscreenText import OnscreenText  # type: ignore
    from panda3d.core import TextNode, DirectionalLight, AmbientLight  # type: ignore
    PANDA_AVAILABLE = True
except Exception:
    PANDA_AVAILABLE = False
    class DirectButton:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def destroy(self): pass
    class DirectFrame:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def destroy(self): pass
        def getChildren(self): return []
    class DirectLabel:  # type: ignore
        def __init__(self, *args, **kwargs): pass
    class OnscreenText:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def setText(self, *args, **kwargs): pass
        def destroy(self): pass
    class TextNode:  # type: ignore
        ACenter = 0
        ALeft = 1
    class DirectionalLight:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def setColor(self, *args, **kwargs): pass
    class AmbientLight:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def setColor(self, *args, **kwargs): pass


class CreatorScene(Scene):
    """Сцена режима "Творец мира""" 

    def __init__(self) -> None:
        super().__init__("creator")
        # UI
        self.title_text: Optional[OnscreenText] = None
        self.info_text: Optional[OnscreenText] = None
        self.toolbar_frame: Optional[DirectFrame] = None
        self.place_button: Optional[DirectButton] = None
        self.edit_button: Optional[DirectButton] = None
        self.preview_button: Optional[DirectButton] = None
        self.clear_button: Optional[DirectButton] = None

    def initialize(self) -> bool:
        try:
            logger.info("Инициализация CreatorScene...")
            if PANDA_AVAILABLE:
                # Заголовок
                self.title_text = OnscreenText(text="World Creator",
                                               pos=(0.0, 0.8), scale=0.08,
                                               fg=(1, 1, 1, 1), align=TextNode.ACenter)
                # Информация
                self.info_text = OnscreenText(text="Select a tool to begin",
                                              pos=(-1.2, 0.9), scale=0.05,
                                              fg=(0.8, 0.9, 1, 1), align=TextNode.ALeft)
                # Панель инструментов (простое расположение кнопок)
                self.place_button = DirectButton(text="Placement",
                                                 pos=(-0.8, 0, 0.7), scale=0.06,
                                                 command=lambda: self._set_mode("placement"))
                self.edit_button = DirectButton(text="Edit",
                                                pos=(-0.5, 0, 0.7), scale=0.06,
                                                command=lambda: self._set_mode("edit"))
                self.preview_button = DirectButton(text="Preview",
                                                   pos=(-0.2, 0, 0.7), scale=0.06,
                                                   command=lambda: self._set_mode("preview"))
                self.clear_button = DirectButton(text="Clear",
                                                 pos=(0.1, 0, 0.7), scale=0.06,
                                                 command=self._clear_world)
                # Базовое освещение (если есть корневой узел)
                self._setup_lighting()
            self.initialized = True
            logger.info("CreatorScene инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации CreatorScene: {e}")
            return False

    def _set_mode(self, mode: str) -> None:
        if self.info_text:
            if mode == "placement":
                self.info_text.setText("🎯 Placement mode: click to place objects (mock)")
            elif mode == "edit":
                self.info_text.setText("✏️ Edit mode: select object to modify (mock)")
            elif mode == "preview":
                self.info_text.setText("👁️ Preview mode: observe the scene (mock)")
        logger.info(f"Creator mode set: {mode}")

    def _clear_world(self) -> None:
        logger.info("Очистка мира (mock)")
        if self.info_text:
            self.info_text.setText("🗑️ World cleared (mock)")

    def _setup_lighting(self) -> None:
        try:
            # В минимальной версии просто логируем, чтобы избежать зависимости от render
            logger.debug("Настройка освещения CreatorScene")
        except Exception as e:
            logger.warning(f"Не удалось настроить освещение: {e}")

    def cleanup(self) -> None:
        try:
            for w in [self.title_text, self.info_text,
                      self.place_button, self.edit_button, self.preview_button, self.clear_button]:
                if w:
                    w.destroy()
        finally:
            super().cleanup()
