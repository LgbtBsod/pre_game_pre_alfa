#!/usr/bin/env python3
"""
Система UI - управление пользовательским интерфейсом
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class UIElementType(Enum):
    """Типы UI элементов"""
    BUTTON = "button"
    LABEL = "label"
    INPUT = "input"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    PANEL = "panel"
    SCROLL_VIEW = "scroll_view"
    GRID = "grid"
    LIST = "list"
    PROGRESS_BAR = "progress_bar"
    TOOLTIP = "tooltip"
    MODAL = "modal"

class UIState(Enum):
    """Состояния UI элементов"""
    NORMAL = "normal"
    HOVERED = "hovered"
    PRESSED = "pressed"
    DISABLED = "disabled"
    FOCUSED = "focused"
    ACTIVE = "active"

@dataclass
class UIElement:
    """UI элемент"""
    element_id: str
    element_type: UIElementType
    position: Tuple[float, float]
    size: Tuple[float, float]
    visible: bool
    enabled: bool
    state: UIState
    text: str = ""
    style: Dict[str, Any] = None
    event_handlers: Dict[str, List[Callable]] = None
    parent_id: Optional[str] = None
    children: List[str] = None
    data: Dict[str, Any] = None

@dataclass
class UIStyle:
    """Стиль UI элемента"""
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    text_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    border_color: Tuple[int, int, int, int] = (128, 128, 128, 255)
    border_width: int = 1
    font_size: int = 14
    font_family: str = "Arial"
    padding: Tuple[int, int, int, int] = (5, 5, 5, 5)
    margin: Tuple[int, int, int, int] = (2, 2, 2, 2)
    corner_radius: int = 0
    shadow_offset: Tuple[int, int] = (0, 0)
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)

@dataclass
class UIEvent:
    """UI событие"""
    event_type: str
    element_id: str
    timestamp: float
    data: Dict[str, Any] = None
    mouse_position: Optional[Tuple[float, float]] = None
    key_code: Optional[int] = None

class UISystem(ISystem):
    """Система пользовательского интерфейса"""
    
    def __init__(self):
        self._system_name = "ui"
        self._system_priority = SystemPriority.LOW
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # UI элементы
        self.ui_elements: Dict[str, UIElement] = {}
        self.element_hierarchy: Dict[str, List[str]] = {}
        
        # Стили
        self.default_styles: Dict[UIElementType, UIStyle] = {}
        self.custom_styles: Dict[str, UIStyle] = {}
        
        # События
        self.event_queue: List[UIEvent] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Фокус и выделение
        self.focused_element: Optional[str] = None
        self.hovered_element: Optional[str] = None
        self.selected_elements: List[str] = []
        
        # Слои UI
        self.ui_layers: Dict[int, List[str]] = {0: []}  # 0 - базовый слой
        
        # Статистика
        self.ui_stats = {
            'elements_count': 0,
            'events_processed': 0,
            'render_calls': 0,
            'update_time': 0.0
        }
        
        logger.info("Система UI инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы UI"""
        try:
            logger.info("Инициализация системы UI...")
            
            # Инициализируем базовые стили
            self._initialize_default_styles()
            
            # Создаем базовые UI элементы
            self._create_base_ui_elements()
            
            # Настраиваем обработчики событий
            self._setup_event_handlers()
            
            self._system_state = SystemState.READY
            logger.info("Система UI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы UI: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы UI"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обрабатываем события
            self._process_event_queue()
            
            # Обновляем анимации
            self._update_animations(delta_time)
            
            # Обновляем состояния элементов
            self._update_element_states(delta_time)
            
            # Обновляем статистику
            self.ui_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы UI: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы UI"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система UI приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы UI: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы UI"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система UI возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы UI: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы UI"""
        try:
            logger.info("Очистка системы UI...")
            
            # Очищаем UI элементы
            self.ui_elements.clear()
            self.element_hierarchy.clear()
            
            # Очищаем стили
            self.default_styles.clear()
            self.custom_styles.clear()
            
            # Очищаем события
            self.event_queue.clear()
            self.event_handlers.clear()
            
            # Сбрасываем фокус
            self.focused_element = None
            self.hovered_element = None
            self.selected_elements.clear()
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система UI очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы UI: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'ui_elements_count': len(self.ui_elements),
            'event_handlers_count': len(self.event_handlers),
            'focused_element': self.focused_element,
            'hovered_element': self.hovered_element,
            'selected_elements_count': len(self.selected_elements),
            'stats': self.ui_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "ui_element_created":
                return self._handle_element_created(event_data)
            elif event_type == "ui_element_updated":
                return self._handle_element_updated(event_data)
            elif event_type == "ui_element_destroyed":
                return self._handle_element_destroyed(event_data)
            elif event_type == "ui_style_changed":
                return self._handle_style_changed(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def create_ui_element(self, element_type: str, element_data: Dict[str, Any]) -> Any:
        """Создание UI элемента"""
        try:
            element_id = element_data.get('element_id', f"ui_element_{len(self.ui_elements)}")
            
            # Создаем UI элемент
            ui_element = UIElement(
                element_id=element_id,
                element_type=UIElementType(element_type),
                position=element_data.get('position', (0.0, 0.0)),
                size=element_data.get('size', (100.0, 50.0)),
                visible=element_data.get('visible', True),
                enabled=element_data.get('enabled', True),
                state=UIState.NORMAL,
                text=element_data.get('text', ""),
                style=element_data.get('style'),
                event_handlers=element_data.get('event_handlers', {}),
                parent_id=element_data.get('parent_id'),
                children=element_data.get('children', []),
                data=element_data.get('data', {})
            )
            
            # Добавляем в систему
            self.ui_elements[element_id] = ui_element
            
            # Добавляем в иерархию
            if ui_element.parent_id:
                if ui_element.parent_id not in self.element_hierarchy:
                    self.element_hierarchy[ui_element.parent_id] = []
                self.element_hierarchy[ui_element.parent_id].append(element_id)
            
            # Добавляем в слой
            layer = element_data.get('layer', 0)
            if layer not in self.ui_layers:
                self.ui_layers[layer] = []
            self.ui_layers[layer].append(element_id)
            
            # Применяем стиль
            if not ui_element.style:
                ui_element.style = self._get_default_style(ui_element.element_type)
            
            self.ui_stats['elements_count'] = len(self.ui_elements)
            logger.debug(f"Создан UI элемент: {element_id}")
            return element_id
            
        except Exception as e:
            logger.error(f"Ошибка создания UI элемента: {e}")
            return None
    
    def update_ui_element(self, element_id: str, element_data: Dict[str, Any]) -> bool:
        """Обновление UI элемента"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            ui_element = self.ui_elements[element_id]
            
            # Обновляем свойства
            if 'position' in element_data:
                ui_element.position = element_data['position']
            if 'size' in element_data:
                ui_element.size = element_data['size']
            if 'visible' in element_data:
                ui_element.visible = element_data['visible']
            if 'enabled' in element_data:
                ui_element.enabled = element_data['enabled']
            if 'text' in element_data:
                ui_element.text = element_data['text']
            if 'style' in element_data:
                ui_element.style = element_data['style']
            if 'data' in element_data:
                ui_element.data.update(element_data['data'])
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления UI элемента {element_id}: {e}")
            return False
    
    def destroy_ui_element(self, element_id: str) -> bool:
        """Уничтожение UI элемента"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            ui_element = self.ui_elements[element_id]
            
            # Удаляем из иерархии
            if ui_element.parent_id and ui_element.parent_id in self.element_hierarchy:
                self.element_hierarchy[ui_element.parent_id].remove(element_id)
            
            # Удаляем из слоя
            for layer_elements in self.ui_layers.values():
                if element_id in layer_elements:
                    layer_elements.remove(element_id)
                    break
            
            # Удаляем элемент
            del self.ui_elements[element_id]
            
            # Сбрасываем фокус если нужно
            if self.focused_element == element_id:
                self.focused_element = None
            if self.hovered_element == element_id:
                self.hovered_element = None
            if element_id in self.selected_elements:
                self.selected_elements.remove(element_id)
            
            self.ui_stats['elements_count'] = len(self.ui_elements)
            logger.debug(f"Уничтожен UI элемент: {element_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения UI элемента {element_id}: {e}")
            return False
    
    def handle_ui_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка UI событий"""
        try:
            # Создаем UI событие
            ui_event = UIEvent(
                event_type=event_type,
                element_id=event_data.get('element_id', ''),
                timestamp=time.time(),
                data=event_data,
                mouse_position=event_data.get('mouse_position'),
                key_code=event_data.get('key_code')
            )
            
            # Добавляем в очередь событий
            self.event_queue.append(ui_event)
            
            # Обрабатываем немедленно если нужно
            if event_type in ['mouse_click', 'key_press', 'focus_change']:
                return self._process_ui_event(ui_event)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки UI события: {e}")
            return False
    
    def set_focus(self, element_id: str) -> bool:
        """Установка фокуса на элемент"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            # Снимаем фокус с предыдущего элемента
            if self.focused_element and self.focused_element in self.ui_elements:
                old_element = self.ui_elements[self.focused_element]
                old_element.state = UIState.NORMAL
                
                # Вызываем обработчик потери фокуса
                self._call_event_handler(self.focused_element, 'on_focus_lost', {})
            
            # Устанавливаем фокус на новый элемент
            self.focused_element = element_id
            new_element = self.ui_elements[element_id]
            new_element.state = UIState.FOCUSED
            
            # Вызываем обработчик получения фокуса
            self._call_event_handler(element_id, 'on_focus_gained', {})
            
            logger.debug(f"Фокус установлен на элемент: {element_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки фокуса на элемент {element_id}: {e}")
            return False
    
    def get_element_at_position(self, position: Tuple[float, float]) -> Optional[str]:
        """Получение элемента в указанной позиции"""
        try:
            # Проверяем элементы в обратном порядке (сверху вниз)
            for layer in sorted(self.ui_layers.keys(), reverse=True):
                for element_id in self.ui_layers[layer]:
                    if element_id in self.ui_elements:
                        element = self.ui_elements[element_id]
                        if element.visible and element.enabled:
                            if self._is_point_in_element(position, element):
                                return element_id
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения элемента в позиции {position}: {e}")
            return None
    
    def _initialize_default_styles(self) -> None:
        """Инициализация базовых стилей"""
        try:
            # Стиль для кнопок
            self.default_styles[UIElementType.BUTTON] = UIStyle(
                background_color=(64, 128, 255, 255),
                text_color=(255, 255, 255, 255),
                border_color=(32, 64, 128, 255),
                border_width=2,
                font_size=14,
                corner_radius=5,
                padding=(10, 5, 10, 5)
            )
            
            # Стиль для меток
            self.default_styles[UIElementType.LABEL] = UIStyle(
                background_color=(0, 0, 0, 0),
                text_color=(0, 0, 0, 255),
                font_size=14,
                padding=(2, 2, 2, 2)
            )
            
            # Стиль для полей ввода
            self.default_styles[UIElementType.INPUT] = UIStyle(
                background_color=(255, 255, 255, 255),
                text_color=(0, 0, 0, 255),
                border_color=(128, 128, 128, 255),
                border_width=1,
                font_size=14,
                padding=(5, 5, 5, 5)
            )
            
            # Стиль для слайдеров
            self.default_styles[UIElementType.SLIDER] = UIStyle(
                background_color=(200, 200, 200, 255),
                border_color=(128, 128, 128, 255),
                border_width=1,
                padding=(2, 2, 2, 2)
            )
            
            logger.debug("Базовые стили UI инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать базовые стили UI: {e}")
    
    def _create_base_ui_elements(self) -> None:
        """Создание базовых UI элементов"""
        try:
            # Создаем корневой контейнер
            root_container = {
                'element_id': 'root_container',
                'element_type': 'panel',
                'position': (0, 0),
                'size': (800, 600),
                'visible': True,
                'enabled': True,
                'layer': 0
            }
            
            self.create_ui_element('panel', root_container)
            logger.debug("Базовые UI элементы созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать базовые UI элементы: {e}")
    
    def _setup_event_handlers(self) -> None:
        """Настройка обработчиков событий"""
        try:
            # Базовые обработчики событий
            self.event_handlers = {
                'on_click': [],
                'on_hover': [],
                'on_focus_gained': [],
                'on_focus_lost': [],
                'on_key_press': [],
                'on_value_changed': []
            }
            
            logger.debug("Обработчики событий UI настроены")
            
        except Exception as e:
            logger.warning(f"Не удалось настроить обработчики событий UI: {e}")
    
    def _process_event_queue(self) -> None:
        """Обработка очереди событий"""
        try:
            while self.event_queue:
                event = self.event_queue.pop(0)
                self._process_ui_event(event)
                self.ui_stats['events_processed'] += 1
                
        except Exception as e:
            logger.warning(f"Ошибка обработки очереди событий UI: {e}")
    
    def _process_ui_event(self, event: UIEvent) -> bool:
        """Обработка UI события"""
        try:
            if event.element_id in self.ui_elements:
                element = self.ui_elements[event.element_id]
                
                # Вызываем обработчик события
                if event.event_type in element.event_handlers:
                    for handler in element.event_handlers[event.event_type]:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error(f"Ошибка в обработчике события {event.event_type}: {e}")
                
                # Вызываем глобальные обработчики
                if event.event_type in self.event_handlers:
                    for handler in self.event_handlers[event.event_type]:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error(f"Ошибка в глобальном обработчике события {event.event_type}: {e}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки UI события: {e}")
            return False
    
    def _update_animations(self, delta_time: float) -> None:
        """Обновление анимаций UI"""
        try:
            # Здесь должна быть логика обновления анимаций UI элементов
            pass
        except Exception as e:
            logger.warning(f"Ошибка обновления анимаций UI: {e}")
    
    def _update_element_states(self, delta_time: float) -> None:
        """Обновление состояний UI элементов"""
        try:
            # Обновляем состояния элементов на основе событий мыши и клавиатуры
            pass
        except Exception as e:
            logger.warning(f"Ошибка обновления состояний UI элементов: {e}")
    
    def _get_default_style(self, element_type: UIElementType) -> UIStyle:
        """Получение стиля по умолчанию для типа элемента"""
        return self.default_styles.get(element_type, UIStyle())
    
    def _is_point_in_element(self, point: Tuple[float, float], element: UIElement) -> bool:
        """Проверка, находится ли точка внутри элемента"""
        try:
            x, y = point
            elem_x, elem_y = element.position
            elem_w, elem_h = element.size
            
            return (elem_x <= x <= elem_x + elem_w and 
                   elem_y <= y <= elem_y + elem_h)
                   
        except Exception as e:
            logger.warning(f"Ошибка проверки позиции точки: {e}")
            return False
    
    def _call_event_handler(self, element_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Вызов обработчика события для элемента"""
        try:
            if element_id in self.ui_elements:
                element = self.ui_elements[element_id]
                if event_type in element.event_handlers:
                    for handler in element.event_handlers[event_type]:
                        try:
                            handler(event_data)
                        except Exception as e:
                            logger.error(f"Ошибка в обработчике события {event_type}: {e}")
                            
        except Exception as e:
            logger.warning(f"Ошибка вызова обработчика события: {e}")
    
    def _handle_element_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания элемента"""
        try:
            return self.create_ui_element(
                event_data.get('element_type', 'label'),
                event_data
            ) is not None
        except Exception as e:
            logger.error(f"Ошибка обработки события создания элемента: {e}")
            return False
    
    def _handle_element_updated(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обновления элемента"""
        try:
            element_id = event_data.get('element_id')
            if element_id:
                return self.update_ui_element(element_id, event_data)
            return False
        except Exception as e:
            logger.error(f"Ошибка обработки события обновления элемента: {e}")
            return False
    
    def _handle_element_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения элемента"""
        try:
            element_id = event_data.get('element_id')
            if element_id:
                return self.destroy_ui_element(element_id)
            return False
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения элемента: {e}")
            return False
    
    def _handle_style_changed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изменения стиля"""
        try:
            element_id = event_data.get('element_id')
            if element_id and element_id in self.ui_elements:
                element = self.ui_elements[element_id]
                if 'style' in event_data:
                    element.style = event_data['style']
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка обработки события изменения стиля: {e}")
            return False
