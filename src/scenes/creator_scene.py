#!/usr/bin/env python3
"""
Creator Scene - Сцена режима "Творец мира" на Panda3D
Пользователь создает препятствия, ловушки, сундуки и врагов
"""

import logging
import math
import random
from typing import List, Optional, Dict, Any, Tuple
from panda3d.core import NodePath, PandaNode, Vec3, Point3, LVector3
from panda3d.core import OrthographicLens, PerspectiveLens
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from panda3d.core import TextNode, PandaNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel

from core.scene_manager import Scene
from systems.world.world_manager import WorldManager, WorldObjectType, ObjectState
from systems.ui.ui_system import UISystem, WorldObjectTemplate, ObjectCategory

logger = logging.getLogger(__name__)

class CreatorCamera:
    """Камера для режима создания"""
    
    def __init__(self, camera_node: NodePath):
        self.camera_node = camera_node
        
        # Позиция камеры
        self.world_x = 0.0
        self.world_y = -15.0
        self.world_z = 10.0
        
        # Масштаб
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        
        # Настройка ортографической проекции
        self._setup_orthographic_projection()
    
    def _setup_orthographic_projection(self):
        """Настройка ортографической проекции"""
        lens = OrthographicLens()
        lens.setFilmSize(40, 30)
        lens.setNearFar(-100, 100)
        self.camera_node.node().setLens(lens)
        
        # Устанавливаем позицию камеры
        self.camera_node.setPos(self.world_x, self.world_y, self.world_z)
        self.camera_node.lookAt(0, 0, 0)
    
    def move(self, dx: float, dy: float, dz: float = 0):
        """Перемещение камеры"""
        self.world_x += dx
        self.world_y += dy
        self.world_z += dz
        
        # Обновляем позицию камеры
        self.camera_node.setPos(self.world_x, self.world_y, self.world_z)
    
    def set_zoom(self, zoom: float):
        """Установка масштаба"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
        # Обновляем проекцию
        lens = self.camera_node.node().getLens()
        if isinstance(lens, OrthographicLens):
            lens.setFilmSize(40 / self.zoom, 30 / self.zoom)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Преобразование экранных координат в мировые"""
        # Простое преобразование для ортографической проекции
        world_x = screen_x * 20 / self.zoom + self.world_x
        world_y = screen_y * 15 / self.zoom + self.world_y
        return world_x, world_y

class CreatorScene(Scene):
    """Сцена режима "Творец мира" на Panda3D"""
    
    def __init__(self):
        super().__init__("creator")
        
        # Системы
        self.world_manager: Optional[WorldManager] = None
        self.ui_system: Optional[UISystem] = None
        
        # Panda3D узлы
        self.scene_root = None
        self.world_root = None
        self.ui_root = None
        
        # Камера создания
        self.camera: Optional[CreatorCamera] = None
        
        # Состояние создания
        self.creation_mode = False
        self.selected_template: Optional[WorldObjectTemplate] = None
        self.preview_object = None
        
        # UI элементы Panda3D
        self.toolbar_frame = None
        self.templates_frame = None
        self.properties_frame = None
        self.stats_frame = None
        
        # Информационные тексты
        self.info_text = None
        self.stats_text = None
        self.help_text = None
        
        # Кнопки инструментов
        self.tool_buttons = {}
        
        logger.info("Сцена творца мира Panda3D создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены творца мира"""
        try:
            logger.info("Начало инициализации сцены творца мира Panda3D...")
            
            # Создание корневых узлов
            self._create_scene_nodes()
            
            # Создаем камеру создания
            if hasattr(self, 'scene_manager') and self.scene_manager:
                from panda3d.core import Camera
                camera_node = self.scene_manager.render_node.find("**/+Camera")
                if camera_node.isEmpty():
                    camera = Camera('creator_camera')
                    camera_node = self.scene_manager.render_node.attachNewNode(camera)
                self.camera = CreatorCamera(camera_node)
            
            # Инициализируем системы
            self._initialize_systems()
            
            # Создание UI элементов
            self._create_ui_elements()
            
            # Настройка освещения
            self._setup_lighting()
            
            # Создание сетки для размещения
            self._create_placement_grid()
            
            logger.info("Сцена творца мира Panda3D успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены творца мира: {e}")
            return False
    
    def _create_scene_nodes(self):
        """Создание корневых узлов сцены"""
        # Используем корневые узлы, созданные менеджером сцен
        if self.scene_root:
            self.world_root = self.scene_root.attachNewNode("world")
            self.ui_root = self.scene_root.attachNewNode("ui")
        else:
            # Fallback если корневые узлы не созданы
            if hasattr(self, 'scene_manager') and self.scene_manager:
                self.scene_root = self.scene_manager.render_node.attachNewNode("creator_scene")
                self.world_root = self.scene_root.attachNewNode("world")
                self.ui_root = self.scene_root.attachNewNode("ui")
    
    def _initialize_systems(self):
        """Инициализация систем"""
        try:
            # Создаем менеджер мира
            self.world_manager = WorldManager()
            if hasattr(self.world_manager, 'initialize'):
                self.world_manager.initialize()
            
            # Создаем UI систему
            self.ui_system = UISystem()
            if hasattr(self.ui_system, 'initialize'):
                self.ui_system.initialize()
            
            logger.debug("Системы сцены творца мира инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать некоторые системы: {e}")
    
    def _create_ui_elements(self):
        """Создание UI элементов для режима творца мира"""
        try:
            # Основная панель инструментов
            self.toolbar_frame = DirectFrame(
                frameColor=(0, 0, 0, 0.8),
                frameSize=(-1, 1, 0.9, 1),
                parent=self.ui_root
            )
            
            # Заголовок
            title_label = DirectLabel(
                text="🎨 РЕЖИМ ТВОРЦА МИРА",
                scale=0.05,
                pos=(0, 0, 0.95),
                frameColor=(0, 0, 0, 0),
                text_fg=(0, 255, 255, 1),
                parent=self.toolbar_frame
            )
            
            # Кнопки инструментов
            tool_configs = [
                ("placement", "🎯 Размещение", (-0.8, 0, 0.92), (0, 255, 100, 0.8)),
                ("edit", "✏️ Редактирование", (-0.6, 0, 0.92), (255, 100, 255, 0.8)),
                ("preview", "👁️ Просмотр", (-0.4, 0, 0.92), (255, 193, 7, 0.8)),
                ("clear", "🗑️ Очистить", (-0.2, 0, 0.92), (255, 100, 100, 0.8))
            ]
            
            for tool_id, text, pos, color in tool_configs:
                button = DirectButton(
                    text=text,
                    scale=0.04,
                    pos=pos,
                    frameColor=color,
                    text_fg=(1, 1, 1, 1),
                    relief=1,
                    command=self._handle_tool_button,
                    extraArgs=[tool_id],
                    parent=self.toolbar_frame
                )
                self.tool_buttons[tool_id] = button
            
            # Панель шаблонов объектов
            self.templates_frame = DirectFrame(
                frameColor=(0, 0, 0, 0.7),
                frameSize=(-1, -0.7, -0.8, 0.8),
                parent=self.ui_root
            )
            
            templates_label = DirectLabel(
                text="📦 ШАБЛОНЫ ОБЪЕКТОВ",
                scale=0.04,
                pos=(-0.85, 0, 0.75),
                frameColor=(0, 0, 0, 0),
                text_fg=(255, 255, 255, 1),
                parent=self.templates_frame
            )
            
            # Кнопки категорий
            category_configs = [
                ("combat", "⚔️ Бой", (-0.85, 0, 0.6), (217, 83, 79, 0.8)),
                ("exploration", "🔍 Исследование", (-0.85, 0, 0.5), (91, 192, 222, 0.8)),
                ("environment", "🌍 Окружение", (-0.85, 0, 0.4), (92, 184, 92, 0.8)),
                ("rewards", "💰 Награды", (-0.85, 0, 0.3), (255, 193, 7, 0.8))
            ]
            
            for category_id, text, pos, color in category_configs:
                button = DirectButton(
                    text=text,
                    scale=0.035,
                    pos=pos,
                    frameColor=color,
                    text_fg=(1, 1, 1, 1),
                    relief=1,
                    command=self._handle_category_button,
                    extraArgs=[category_id],
                    parent=self.templates_frame
                )
                self.tool_buttons[f"category_{category_id}"] = button
            
            # Панель свойств
            self.properties_frame = DirectFrame(
                frameColor=(0, 0, 0, 0.7),
                frameSize=(0.7, 1, -0.8, 0.8),
                parent=self.ui_root
            )
            
            properties_label = DirectLabel(
                text="⚙️ СВОЙСТВА",
                scale=0.04,
                pos=(0.85, 0, 0.75),
                frameColor=(0, 0, 0, 0),
                text_fg=(255, 255, 255, 1),
                parent=self.properties_frame
            )
            
            # Панель статистики
            self.stats_frame = DirectFrame(
                frameColor=(0, 0, 0, 0.8),
                frameSize=(-1, 1, -1, -0.8),
                parent=self.ui_root
            )
            
            self.stats_text = DirectLabel(
                text="📊 Статистика: Объектов создано: 0",
                scale=0.035,
                pos=(-0.9, 0, -0.95),
                frameColor=(0, 0, 0, 0),
                text_fg=(255, 255, 255, 1),
                parent=self.stats_frame
            )
            
            # Информационный текст
            self.info_text = DirectLabel(
                text="🎯 Выберите инструмент и объект для размещения",
                scale=0.04,
                pos=(0, 0, 0.8),
                frameColor=(0, 0, 0, 0.7),
                text_fg=(0, 255, 255, 1),
                parent=self.ui_root
            )
            
            # Текст помощи
            self.help_text = DirectLabel(
                text="💡 Подсказка: ЛКМ - разместить объект, ПКМ - отменить, Колесо мыши - масштаб",
                scale=0.03,
                pos=(0, 0, -0.9),
                frameColor=(0, 0, 0, 0.7),
                text_fg=(255, 255, 100, 1),
                parent=self.ui_root
            )
            
            logger.debug("UI элементы сцены творца мира созданы")
            
        except Exception as e:
            logger.error(f"Ошибка создания UI элементов: {e}")
    
    def _setup_lighting(self):
        """Настройка освещения для сцены"""
        if not self.scene_root:
            return
        
        # Основное направленное освещение
        dlight = DirectionalLight('creator_dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.scene_root.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.scene_root.setLight(dlnp)
        
        # Фоновое освещение
        alight = AmbientLight('creator_alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        alnp = self.scene_root.attachNewNode(alight)
        self.scene_root.setLight(alnp)
        
        logger.debug("Освещение сцены творца мира настроено")
    
    def _create_placement_grid(self):
        """Создание сетки для размещения объектов"""
        try:
            from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
            from panda3d.core import GeomVertexWriter, GeomLines
            
            # Создаем геометрию сетки
            format = GeomVertexFormat.getV3c4()
            vdata = GeomVertexData('grid', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            color = GeomVertexWriter(vdata, 'color')
            
            # Создаем линии сетки
            grid_size = 20
            grid_spacing = 1.0
            
            # Горизонтальные линии
            for i in range(-grid_size, grid_size + 1):
                y = i * grid_spacing
                vertex.addData3(-grid_size * grid_spacing, y, 0)
                vertex.addData3(grid_size * grid_spacing, y, 0)
                color.addData4(0.3, 0.3, 0.3, 0.5)
                color.addData4(0.3, 0.3, 0.3, 0.5)
            
            # Вертикальные линии
            for i in range(-grid_size, grid_size + 1):
                x = i * grid_spacing
                vertex.addData3(x, -grid_size * grid_spacing, 0)
                vertex.addData3(x, grid_size * grid_spacing, 0)
                color.addData4(0.3, 0.3, 0.3, 0.5)
                color.addData4(0.3, 0.3, 0.3, 0.5)
            
            # Создаем линии
            lines = GeomLines(Geom.UHStatic)
            for i in range((grid_size * 2 + 1) * 2):
                lines.addVertices(i * 2, i * 2 + 1)
            
            # Создаем геометрию
            geom = Geom(vdata)
            geom.addPrimitive(lines)
            
            # Создаем узел
            node = GeomNode('grid')
            node.addGeom(geom)
            
            # Создаем NodePath
            grid_np = self.world_root.attachNewNode(node)
            grid_np.setTransparency(True)
            
            logger.debug("Сетка размещения создана")
            
        except Exception as e:
            logger.warning(f"Не удалось создать сетку размещения: {e}")
    
    def _handle_tool_button(self, tool_id: str):
        """Обработка нажатия кнопки инструмента"""
        try:
            if tool_id == "placement":
                self.creation_mode = True
                self.info_text.setText("🎯 Режим размещения: Выберите объект для размещения")
            elif tool_id == "edit":
                self.creation_mode = False
                self.info_text.setText("✏️ Режим редактирования: Выберите объект для редактирования")
            elif tool_id == "preview":
                self.creation_mode = False
                self.info_text.setText("👁️ Режим просмотра: Наблюдайте за созданным миром")
            elif tool_id == "clear":
                self._clear_world()
                self.info_text.setText("🗑️ Мир очищен")
            
            logger.info(f"Активирован инструмент: {tool_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки инструмента {tool_id}: {e}")
    
    def _handle_category_button(self, category_id: str):
        """Обработка нажатия кнопки категории"""
        try:
            if not self.ui_system:
                return
            
            # Получаем доступные шаблоны для категории
            category = ObjectCategory(category_id)
            templates = self.ui_system.get_available_templates(category)
            
            if templates:
                # Показываем шаблоны в панели свойств
                self._show_templates_in_properties(templates)
                self.info_text.setText(f"📦 Выберите объект из категории: {category.value}")
            else:
                self.info_text.setText(f"❌ Нет доступных объектов в категории: {category.value}")
            
            logger.info(f"Выбрана категория: {category_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки категории {category_id}: {e}")
    
    def _show_templates_in_properties(self, templates: List[WorldObjectTemplate]):
        """Показ шаблонов в панели свойств"""
        try:
            # Очищаем панель свойств
            for child in self.properties_frame.getChildren():
                child.destroy()
            
            # Заголовок
            DirectLabel(
                text="📦 ДОСТУПНЫЕ ОБЪЕКТЫ",
                scale=0.035,
                pos=(0.85, 0, 0.75),
                frameColor=(0, 0, 0, 0),
                text_fg=(255, 255, 255, 1),
                parent=self.properties_frame
            )
            
            # Создаем кнопки для каждого шаблона
            for i, template in enumerate(templates[:8]):  # Максимум 8 шаблонов
                button = DirectButton(
                    text=f"{template.icon} {template.name}",
                    scale=0.03,
                    pos=(0.85, 0, 0.6 - i * 0.08),
                    frameColor=(0, 100, 200, 0.8),
                    text_fg=(1, 1, 1, 1),
                    relief=1,
                    command=self._select_template,
                    extraArgs=[template.template_id],
                    parent=self.properties_frame
                )
            
        except Exception as e:
            logger.error(f"Ошибка показа шаблонов: {e}")
    
    def _select_template(self, template_id: str):
        """Выбор шаблона для размещения"""
        try:
            if not self.ui_system:
                return
            
            # Выбираем шаблон
            if self.ui_system.select_template(template_id):
                self.selected_template = self.ui_system.selected_template
                self.info_text.setText(f"🎯 Выбран: {self.selected_template.name}. Кликните для размещения")
                logger.info(f"Выбран шаблон: {self.selected_template.name}")
            else:
                self.info_text.setText("❌ Не удалось выбрать шаблон")
            
        except Exception as e:
            logger.error(f"Ошибка выбора шаблона {template_id}: {e}")
    
    def _clear_world(self):
        """Очистка мира"""
        try:
            if self.world_manager:
                # Очищаем все объекты
                for object_id in list(self.world_manager.world_objects.keys()):
                    self.world_manager.remove_world_object(object_id)
                
                logger.info("Мир очищен")
            
        except Exception as e:
            logger.error(f"Ошибка очистки мира: {e}")
    
    def handle_mouse_click(self, x: float, y: float, button: str):
        """Обработка клика мыши"""
        try:
            if not self.camera:
                return
            
            # Преобразуем экранные координаты в мировые
            world_x, world_y = self.camera.screen_to_world(x, y)
            
            if button == "left" and self.creation_mode and self.selected_template:
                # Размещаем объект
                self._place_object(world_x, world_y)
            elif button == "right":
                # Отменяем выбор
                self.selected_template = None
                self.info_text.setText("🎯 Выберите объект для размещения")
            
        except Exception as e:
            logger.error(f"Ошибка обработки клика мыши: {e}")
    
    def _place_object(self, world_x: float, world_y: float):
        """Размещение объекта в мире"""
        try:
            if not self.world_manager or not self.selected_template:
                return
            
            # Создаем данные объекта
            object_data = {
                'id': f"{self.selected_template.template_id}_{self.world_manager.world_stats['total_objects']}",
                'template_id': self.selected_template.template_id,
                'type': self.selected_template.object_type.value,
                'name': self.selected_template.name,
                'x': world_x,
                'y': world_y,
                'z': 0,
                'properties': self.selected_template.properties.copy(),
                'created_by': 'user',
                'creation_time': time.time()
            }
            
            # Добавляем объект в мир
            object_id = self.world_manager.add_world_object(object_data)
            
            if object_id:
                # Создаем визуальное представление
                self._create_visual_object(object_data)
                
                # Обновляем статистику
                self._update_stats()
                
                self.info_text.setText(f"✅ Размещен: {self.selected_template.name}")
                logger.info(f"Размещен объект: {self.selected_template.name} в ({world_x}, {world_y})")
            else:
                self.info_text.setText("❌ Не удалось разместить объект")
            
        except Exception as e:
            logger.error(f"Ошибка размещения объекта: {e}")
    
    def _create_visual_object(self, object_data: Dict[str, Any]):
        """Создание визуального представления объекта"""
        try:
            from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
            from panda3d.core import GeomVertexWriter, GeomTriangles
            
            # Создаем геометрию объекта
            format = GeomVertexFormat.getV3c4()
            vdata = GeomVertexData('object', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            color = GeomVertexWriter(vdata, 'color')
            
            # Получаем свойства объекта
            width = object_data['properties'].get('width', 1.0)
            height = object_data['properties'].get('height', 1.0)
            depth = object_data['properties'].get('depth', 1.0)
            obj_color = object_data['properties'].get('color', (1.0, 1.0, 1.0, 1.0))
            
            # Создаем куб
            half_w = width / 2
            half_h = height / 2
            half_d = depth / 2
            
            # Вершины куба
            vertices = [
                (-half_w, -half_d, -half_h), (half_w, -half_d, -half_h),
                (half_w, half_d, -half_h), (-half_w, half_d, -half_h),
                (-half_w, -half_d, half_h), (half_w, -half_d, half_h),
                (half_w, half_d, half_h), (-half_w, half_d, half_h)
            ]
            
            # Добавляем вершины
            for v in vertices:
                vertex.addData3(*v)
                color.addData4(*obj_color)
            
            # Создаем треугольники
            prim = GeomTriangles(Geom.UHStatic)
            
            # Грани куба
            faces = [
                (0, 1, 2), (2, 3, 0),  # Передняя грань
                (1, 5, 6), (6, 2, 1),  # Правая грань
                (5, 4, 7), (7, 6, 5),  # Задняя грань
                (4, 0, 3), (3, 7, 4),  # Левая грань
                (3, 2, 6), (6, 7, 3),  # Верхняя грань
                (4, 5, 1), (1, 0, 4)   # Нижняя грань
            ]
            
            for face in faces:
                prim.addVertices(*face)
                prim.closePrimitive()
            
            # Создаем геометрию
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            # Создаем узел
            node = GeomNode('world_object')
            node.addGeom(geom)
            
            # Создаем NodePath и позиционируем
            np = self.world_root.attachNewNode(node)
            np.setPos(object_data['x'], object_data['y'], object_data['z'])
            np.setTransparency(True)
            
            # Сохраняем ссылку на узел в объекте мира
            if self.world_manager and object_data['id'] in self.world_manager.world_objects:
                self.world_manager.world_objects[object_data['id']].node = np
            
        except Exception as e:
            logger.warning(f"Не удалось создать визуальное представление объекта: {e}")
    
    def _update_stats(self):
        """Обновление статистики"""
        try:
            if self.world_manager:
                stats = self.world_manager.get_world_stats()
                self.stats_text.setText(
                    f"📊 Статистика: Объектов создано: {stats['total_objects']} | "
                    f"Препятствий: {stats['obstacles_count']} | "
                    f"Ловушек: {stats['traps_count']} | "
                    f"Сундуков: {stats['chests_count']} | "
                    f"Врагов: {stats['enemies_count']}"
                )
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def update(self, delta_time: float):
        """Обновление сцены творца мира"""
        # Обновляем системы
        if self.world_manager:
            self.world_manager.update(delta_time)
        
        if self.ui_system:
            self.ui_system.update(delta_time)
        
        # Обновляем статистику
        self._update_stats()
    
    def render(self, render_node):
        """Отрисовка сцены творца мира"""
        # Panda3D автоматически отрисовывает сцену
        pass
    
    def handle_event(self, event):
        """Обработка событий"""
        # Обработка событий Panda3D
        pass
    
    def cleanup(self):
        """Очистка сцены творца мира"""
        logger.info("Очистка сцены творца мира Panda3D...")
        
        # Очищаем системы
        if self.world_manager:
            self.world_manager.cleanup()
        
        if self.ui_system:
            self.ui_system.cleanup()
        
        # Очищаем Panda3D узлы
        if self.scene_root:
            self.scene_root.removeNode()
        
        # Очищаем UI элементы
        if self.toolbar_frame:
            self.toolbar_frame.destroy()
        if self.templates_frame:
            self.templates_frame.destroy()
        if self.properties_frame:
            self.properties_frame.destroy()
        if self.stats_frame:
            self.stats_frame.destroy()
        
        logger.info("Сцена творца мира Panda3D очищена")
