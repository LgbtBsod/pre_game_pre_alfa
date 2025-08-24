#!/usr/bin/env python3
"""
UI System - Система пользовательского интерфейса
Отвечает только за отображение UI элементов и их обновление
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode, Vec4
from ...core.interfaces import ISystem

logger = logging.getLogger(__name__)

class UIElementType(Enum):
    """Типы UI элементов"""
    TEXT = "text"
    IMAGE = "image"
    BUTTON = "button"
    PANEL = "panel"

class UITextAlignment(Enum):
    """Выравнивание текста"""
    LEFT = TextNode.ALeft
    CENTER = TextNode.ACenter
    RIGHT = TextNode.ARight

@dataclass
class UIElement:
    """UI элемент"""
    id: str
    element_type: UIElementType
    widget: Any
    position: tuple
    scale: float
    visible: bool
    update_callback: Optional[Callable] = None

class UISystem(ISystem):
    """
    Система пользовательского интерфейса
    Управляет всеми UI элементами
    """
    
    def __init__(self):
        self.ui_elements: Dict[str, UIElement] = {}
        self.ui_layers: Dict[str, List[str]] = {
            "background": [],
            "game": [],
            "ui": [],
            "overlay": []
        }
        
        # Настройки UI
        self.default_font = "arial.ttf"
        self.default_text_color = (1, 1, 1, 1)
        self.default_text_scale = 0.05
        
        # Состояние
        self.is_initialized = False
        self.fps_counter = None
        self.debug_info = None
        
        logger.info("Система UI инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы UI"""
        try:
            logger.info("Инициализация системы UI...")
            
            # Создание базовых UI элементов
            self._create_base_ui()
            
            self.is_initialized = True
            logger.info("Система UI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы UI: {e}")
            return False
    
    def _create_base_ui(self):
        """Создание базовых UI элементов"""
        try:
            # FPS счетчик
            self.fps_counter = self.create_text(
                "fps_counter",
                "FPS: 0",
                position=(-1.3, 0.8),
                scale=0.04,
                color=(1, 1, 0, 1),
                layer="overlay"
            )
            
            # Отладочная информация
            self.debug_info = self.create_text(
                "debug_info",
                "AI-EVOLVE Panda3D",
                position=(-1.3, 0.9),
                scale=0.05,
                color=(1, 1, 1, 1),
                layer="overlay"
            )
            
            logger.debug("Базовые UI элементы созданы")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых UI элементов: {e}")
    
    def create_text(self, element_id: str, text: str, position: tuple, scale: float = None,
                   color: tuple = None, alignment: UITextAlignment = UITextAlignment.LEFT,
                   layer: str = "ui") -> Optional[str]:
        """Создание текстового элемента"""
        try:
            if element_id in self.ui_elements:
                logger.warning(f"UI элемент {element_id} уже существует")
                return None
            
            # Создаем текстовый виджет
            widget = OnscreenText(
                text=text,
                pos=position,
                scale=scale or self.default_text_scale,
                fg=color or self.default_text_color,
                align=alignment.value,
                mayChange=True
            )
            
            # Создаем UI элемент
            ui_element = UIElement(
                id=element_id,
                element_type=UIElementType.TEXT,
                widget=widget,
                position=position,
                scale=scale or self.default_text_scale,
                visible=True
            )
            
            # Добавляем в систему
            self.ui_elements[element_id] = ui_element
            self.ui_layers[layer].append(element_id)
            
            logger.debug(f"Создан текстовый элемент: {element_id}")
            return element_id
            
        except Exception as e:
            logger.error(f"Ошибка создания текстового элемента {element_id}: {e}")
            return None
    
    def create_image(self, element_id: str, image_path: str, position: tuple, 
                    scale: float = 1.0, layer: str = "ui") -> Optional[str]:
        """Создание графического элемента"""
        try:
            if element_id in self.ui_elements:
                logger.warning(f"UI элемент {element_id} уже существует")
                return None
            
            # Создаем графический виджет
            widget = OnscreenImage(
                image=image_path,
                pos=position,
                scale=scale
            )
            
            # Создаем UI элемент
            ui_element = UIElement(
                id=element_id,
                element_type=UIElementType.IMAGE,
                widget=widget,
                position=position,
                scale=scale,
                visible=True
            )
            
            # Добавляем в систему
            self.ui_elements[element_id] = ui_element
            self.ui_layers[layer].append(element_id)
            
            logger.debug(f"Создан графический элемент: {element_id}")
            return element_id
            
        except Exception as e:
            logger.error(f"Ошибка создания графического элемента {element_id}: {e}")
            return None
    
    def update_text(self, element_id: str, new_text: str):
        """Обновление текста элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return
            
            element = self.ui_elements[element_id]
            if element.element_type != UIElementType.TEXT:
                logger.warning(f"Элемент {element_id} не является текстовым")
                return
            
            element.widget.setText(new_text)
            logger.debug(f"Текст элемента {element_id} обновлен")
            
        except Exception as e:
            logger.error(f"Ошибка обновления текста элемента {element_id}: {e}")
    
    def set_element_visible(self, element_id: str, visible: bool):
        """Установка видимости элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return
            
            element = self.ui_elements[element_id]
            element.visible = visible
            
            if visible:
                element.widget.show()
            else:
                element.widget.hide()
            
            logger.debug(f"Видимость элемента {element_id} изменена: {visible}")
            
        except Exception as e:
            logger.error(f"Ошибка изменения видимости элемента {element_id}: {e}")
    
    def set_element_position(self, element_id: str, position: tuple):
        """Изменение позиции элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return
            
            element = self.ui_elements[element_id]
            element.position = position
            element.widget.setPos(position[0], position[1])
            
            logger.debug(f"Позиция элемента {element_id} изменена: {position}")
            
        except Exception as e:
            logger.error(f"Ошибка изменения позиции элемента {element_id}: {e}")
    
    def set_element_scale(self, element_id: str, scale: float):
        """Изменение масштаба элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return
            
            element = self.ui_elements[element_id]
            element.scale = scale
            element.widget.setScale(scale)
            
            logger.debug(f"Масштаб элемента {element_id} изменен: {scale}")
            
        except Exception as e:
            logger.error(f"Ошибка изменения масштаба элемента {element_id}: {e}")
    
    def remove_element(self, element_id: str):
        """Удаление UI элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return
            
            element = self.ui_elements[element_id]
            
            # Удаляем виджет
            element.widget.destroy()
            
            # Удаляем из слоев
            for layer_elements in self.ui_layers.values():
                if element_id in layer_elements:
                    layer_elements.remove(element_id)
            
            # Удаляем из системы
            del self.ui_elements[element_id]
            
            logger.debug(f"UI элемент {element_id} удален")
            
        except Exception as e:
            logger.error(f"Ошибка удаления UI элемента {element_id}: {e}")
    
    def get_element_info(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об элементе"""
        if element_id not in self.ui_elements:
            return None
        
        element = self.ui_elements[element_id]
        return {
            "id": element.id,
            "type": element.element_type.value,
            "position": element.position,
            "scale": element.scale,
            "visible": element.visible
        }
    
    def get_layer_elements(self, layer: str) -> List[str]:
        """Получение элементов слоя"""
        return self.ui_layers.get(layer, [])
    
    def set_layer_visible(self, layer: str, visible: bool):
        """Установка видимости слоя"""
        try:
            if layer not in self.ui_layers:
                logger.warning(f"Слой {layer} не найден")
                return
            
            for element_id in self.ui_layers[layer]:
                self.set_element_visible(element_id, visible)
            
            logger.debug(f"Видимость слоя {layer} изменена: {visible}")
            
        except Exception as e:
            logger.error(f"Ошибка изменения видимости слоя {layer}: {e}")
    
    def update_fps_counter(self, fps: int):
        """Обновление FPS счетчика"""
        if self.fps_counter:
            self.update_text("fps_counter", f"FPS: {fps}")
    
    def update_debug_info(self, info: str):
        """Обновление отладочной информации"""
        if self.debug_info:
            self.update_text("debug_info", info)
    
    def update(self, delta_time: float) -> None:
        """Обновление системы UI"""
        if not self.is_initialized:
            return
        
        try:
            # Обновляем элементы с callback функциями
            for element in self.ui_elements.values():
                if element.update_callback:
                    try:
                        element.update_callback(delta_time)
                    except Exception as e:
                        logger.error(f"Ошибка в callback элемента {element.id}: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы UI: {e}")
    
    def cleanup(self) -> None:
        """Очистка системы UI"""
        logger.info("Очистка системы UI...")
        
        try:
            # Удаляем все элементы
            for element_id in list(self.ui_elements.keys()):
                self.remove_element(element_id)
            
            # Очищаем слои
            for layer in self.ui_layers:
                self.ui_layers[layer].clear()
            
            # Сбрасываем состояние
            self.fps_counter = None
            self.debug_info = None
            self.is_initialized = False
            
            logger.info("Система UI очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы UI: {e}")
