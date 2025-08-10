"""
Менеджер рендеринга - управляет отрисовкой всех игровых элементов
Версия для Panda3D с улучшенной производительностью
"""

import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from panda3d.core import (
    WindowFramework, PandaFramework, NodePath, 
    Point3, Vec3, Vec4, TransparencyAttrib,
    TextNode, AntialiasAttrib, DirectionalLight,
    AmbientLight, PerspectiveLens, OrthographicLens,
    CardMaker, LineSegs, PandaNode
)
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task

from core.game_state_manager import game_state_manager
from config.game_constants import PLAYER_COLOR, TEXT_COLOR


@dataclass
class RenderStats:
    """Статистика рендеринга"""

    frames_rendered: int = 0
    entities_rendered: int = 0
    render_time: float = 0.0
    last_fps_time: float = 0.0
    fps: int = 0


class RenderManager:
    """Управляет рендерингом всех игровых элементов с Panda3D"""

    def __init__(self, base: ShowBase, game_state: game_state_manager):
        self.base = base
        self.game_state = game_state
        
        # Получаем размеры окна
        self.width = self.base.win.get_x_size()
        self.height = self.base.win.get_y_size()

        # Позиция камеры
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0

        # Статистика рендеринга
        self.stats = RenderStats()
        self.stats.last_fps_time = time.time()

        # Кэш для оптимизации
        self._cached_entities: Dict[int, NodePath] = {}
        self._last_render_time = 0

        # Получаем настройки рендеринга
        from config.unified_settings import UnifiedSettings
        self._render_interval = 1.0 / UnifiedSettings.RENDER_FPS

        # Настройки рендеринга
        self.show_fps = True
        self.show_debug_info = False
        self.show_health_bars = True
        self.show_names = True

        # Цвета и стили
        self.colors = {
            "background": Vec4(0.1, 0.1, 0.1, 1.0),
            "border": Vec4(0.2, 0.2, 0.2, 1.0),
            "text": Vec4(1.0, 1.0, 1.0, 1.0),
            "player": Vec4(0.0, 0.8, 1.0, 1.0),
            "enemy_warrior": Vec4(1.0, 0.2, 0.2, 1.0),
            "enemy_archer": Vec4(1.0, 0.4, 0.8, 1.0),
            "enemy_mage": Vec4(0.2, 0.6, 1.0, 1.0),
            "health_good": Vec4(0.0, 1.0, 0.0, 1.0),
            "health_warning": Vec4(1.0, 1.0, 0.0, 1.0),
            "health_critical": Vec4(1.0, 0.0, 0.0, 1.0),
            "health_bg": Vec4(0.2, 0.2, 0.2, 1.0),
            "health_border": Vec4(0.4, 0.4, 0.4, 1.0),
        }

        # Создаем сцены
        self._setup_scenes()
        self._setup_lighting()
        self._setup_camera()

    def _setup_scenes(self):
        """Настройка сцен"""
        # Основная сцена для игровых объектов
        self.game_scene = self.base.render.attach_new_node("game_scene")
        
        # Сцена для UI элементов
        self.ui_scene = self.base.render2d.attach_new_node("ui_scene")
        
        # Сцена для отладочной информации
        self.debug_scene = self.base.render2d.attach_new_node("debug_scene")

    def _setup_lighting(self):
        """Настройка освещения"""
        # Основное освещение
        main_light = DirectionalLight("main_light")
        main_light.set_color(Vec4(0.8, 0.8, 0.8, 1.0))
        main_light_np = self.game_scene.attach_new_node(main_light)
        main_light_np.set_hpr(45, -45, 0)
        self.game_scene.set_light(main_light_np)

        # Фоновое освещение
        ambient_light = AmbientLight("ambient_light")
        ambient_light.set_color(Vec4(0.3, 0.3, 0.3, 1.0))
        ambient_light_np = self.game_scene.attach_new_node(ambient_light)
        self.game_scene.set_light(ambient_light_np)

    def _setup_camera(self):
        """Настройка камеры"""
        # Устанавливаем камеру в ортографический режим для 2D игры
        lens = OrthographicLens()
        lens.set_film_size(20, 15)  # Размер видимой области
        self.base.cam.node().set_lens(lens)
        
        # Позиционируем камеру
        self.base.cam.set_pos(0, -10, 0)
        self.base.cam.look_at(Point3(0, 0, 0))

    def clear(self):
        """Очистка сцен"""
        # Очищаем игровые объекты
        for child in self.game_scene.get_children():
            if child.get_name().startswith("entity_"):
                child.remove_node()
        
        # Очищаем UI элементы
        for child in self.ui_scene.get_children():
            if child.get_name().startswith("ui_"):
                child.remove_node()

    def update(self):
        """Обновление экрана"""
        # Panda3D обновляет экран автоматически
        pass

    def set_camera(self, x: float, y: float, zoom: float = 1.0):
        """Установка позиции камеры"""
        self.camera_x = x
        self.camera_y = y
        self.camera_zoom = max(0.1, min(3.0, zoom))
        
        # Обновляем позицию камеры
        self.base.cam.set_pos(x, -10, y)
        
        # Обновляем зум через размер линзы
        lens = self.base.cam.node().get_lens()
        if isinstance(lens, OrthographicLens):
            lens.set_film_size(20 / self.camera_zoom, 15 / self.camera_zoom)

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Преобразование мировых координат в экранные"""
        # В Panda3D координаты уже в мировых единицах
        return world_x, world_y

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Преобразование экранных координат в мировые"""
        # В Panda3D координаты уже в мировых единицах
        return screen_x, screen_y

    def render_area(self, area_name: str):
        """Рендеринг игровой области"""
        try:
            # Создаем фон
            self._create_background()
            
            # Создаем сетку
            self._create_grid()
            
            # Создаем название области
            self._create_area_name(area_name)
            
        except Exception as e:
            print(f"Ошибка рендеринга области: {e}")

    def _create_background(self):
        """Создание фона"""
        # Создаем плоскость для фона
        cm = CardMaker("background")
        cm.set_frame(-10, 10, -7.5, 7.5)
        background = self.game_scene.attach_new_node(cm.generate())
        background.set_color(self.colors["background"])
        background.set_depth_write(False)
        background.set_depth_test(False)

    def _create_grid(self, grid_size: float = 1.0):
        """Создание сетки"""
        try:
            # Создаем линии сетки
            ls = LineSegs("grid")
            ls.set_color(self.colors["border"])
            ls.set_thickness(1.0)
            
            # Вертикальные линии
            for x in range(-10, 11, int(grid_size)):
                ls.move_to(x, -7.5, 0)
                ls.draw_to(x, 7.5, 0)
            
            # Горизонтальные линии
            for y in range(-7, 8, int(grid_size)):
                ls.move_to(-10, y, 0)
                ls.draw_to(10, y, 0)
            
            grid_node = ls.create()
            grid_np = self.game_scene.attach_new_node(grid_node)
            grid_np.set_depth_write(False)
            
        except Exception as e:
            print(f"Ошибка создания сетки: {e}")

    def _create_area_name(self, area_name: str):
        """Создание названия области"""
        try:
            text = OnscreenText(
                text=f"Область: {area_name}",
                pos=(0, 0.8),
                scale=0.05,
                fg=self.colors["text"],
                shadow=(0, 0, 0, 1),
                parent=self.ui_scene
            )
            text.set_name("area_name")
            
        except Exception as e:
            print(f"Ошибка создания названия области: {e}")

    def render_entity(self, entity):
        """Рендеринг сущности"""
        try:
            if not entity or not hasattr(entity, 'position'):
                return

            # Получаем стиль сущности
            style = self._get_entity_style(entity)
            
            # Проверяем, нужно ли рендерить
            if not self._should_render_entity(entity):
                return

            # Создаем или обновляем визуальное представление
            entity_node = self._get_or_create_entity_node(entity, style)
            
            # Обновляем позицию
            entity_node.set_pos(entity.position[0], 0, entity.position[1])
            
            # Рисуем имя
            if self.show_names:
                self._render_entity_name(entity, style)
            
            # Рисуем полоску здоровья
            if self.show_health_bars:
                self._render_health_bar(entity, style)

            self.stats.entities_rendered += 1

        except Exception as e:
            print(f"Ошибка рендеринга сущности: {e}")

    def _should_render_entity(self, entity) -> bool:
        """Проверяет, нужно ли рендерить сущность"""
        if not entity or not hasattr(entity, 'position'):
            return False
        
        # Проверяем, находится ли сущность в поле зрения камеры
        x, y = entity.position[0], entity.position[1]
        
        # Добавляем запас для рендеринга
        margin = 5
        return (-10 - margin <= x <= 10 + margin and 
                -7.5 - margin <= y <= 7.5 + margin)

    def _get_entity_style(self, entity) -> Dict:
        """Получает стиль для сущности"""
        style = {
            "color": self.colors["enemy_warrior"],
            "size": 0.5,
            "shape": "circle",
            "name": "Unknown"
        }
        
        try:
            if hasattr(entity, 'entity_type'):
                if entity.entity_type == "player":
                    style.update({
                        "color": self.colors["player"],
                        "size": 0.6,
                        "name": "Игрок"
                    })
                elif entity.entity_type == "enemy":
                    if hasattr(entity, 'enemy_type'):
                        if entity.enemy_type == "warrior":
                            style["color"] = self.colors["enemy_warrior"]
                        elif entity.enemy_type == "archer":
                            style["color"] = self.colors["enemy_archer"]
                        elif entity.enemy_type == "mage":
                            style["color"] = self.colors["enemy_mage"]
                    
                    if hasattr(entity, 'name'):
                        style["name"] = entity.name
                    else:
                        style["name"] = "Враг"
            
            if hasattr(entity, 'level'):
                style["name"] += f" (Ур.{entity.level})"
                
        except Exception as e:
            print(f"Ошибка получения стиля сущности: {e}")
        
        return style

    def _get_or_create_entity_node(self, entity, style: Dict) -> NodePath:
        """Получает или создает узел для сущности"""
        entity_id = id(entity)
        
        if entity_id in self._cached_entities:
            # Обновляем цвет существующего узла
            node = self._cached_entities[entity_id]
            node.set_color(style["color"])
            return node
        
        # Создаем новый узел
        size = style.get("size", 0.5)
        shape = style.get("shape", "circle")
        
        if shape == "circle":
            # Создаем сферу
            from panda3d.core import GeomNode
            node = self.base.loader.load_model("models/sphere")
            if not node.is_empty():
                node.set_scale(size)
            else:
                # Fallback - создаем простую сферу
                node = self._create_sphere(size)
        else:
            # Создаем куб
            node = self._create_cube(size)
        
        node.set_color(style["color"])
        node.set_name(f"entity_{entity_id}")
        node.reparent_to(self.game_scene)
        
        self._cached_entities[entity_id] = node
        return node

    def _create_sphere(self, radius: float) -> NodePath:
        """Создает простую сферу"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles
        
        # Создаем вершины сферы
        format = GeomVertexFormat.get_v3n3c4()
        vdata = GeomVertexData('sphere', format, Geom.UH_static)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Простая сфера из 8 вершин куба
        for x in [-radius, radius]:
            for y in [-radius, radius]:
                for z in [-radius, radius]:
                    vertex.add_data3(x, y, z)
                    color.add_data4(1, 1, 1, 1)
        
        # Создаем треугольники
        tris = GeomTriangles(Geom.UH_static)
        # Добавляем грани куба...
        
        geom = Geom(vdata)
        geom.add_primitive(tris)
        
        node = GeomNode('sphere')
        node.add_geom(geom)
        
        return NodePath(node)

    def _create_cube(self, size: float) -> NodePath:
        """Создает куб"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles
        
        format = GeomVertexFormat.get_v3n3c4()
        vdata = GeomVertexData('cube', format, Geom.UH_static)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Вершины куба
        for x in [-size, size]:
            for y in [-size, size]:
                for z in [-size, size]:
                    vertex.add_data3(x, y, z)
                    color.add_data4(1, 1, 1, 1)
        
        # Создаем треугольники для граней куба
        tris = GeomTriangles(Geom.UH_static)
        # Добавляем грани...
        
        geom = Geom(vdata)
        geom.add_primitive(tris)
        
        node = GeomNode('cube')
        node.add_geom(geom)
        
        return NodePath(node)

    def _render_entity_name(self, entity, style: Dict):
        """Рендеринг имени сущности"""
        try:
            name = style.get("name", "Unknown")
            x, y = entity.position[0], entity.position[1]
            
            # Создаем текст над сущностью
            text = OnscreenText(
                text=name,
                pos=(x, y + 1),
                scale=0.03,
                fg=self.colors["text"],
                shadow=(0, 0, 0, 1),
                parent=self.game_scene
            )
            text.set_name(f"name_{id(entity)}")
            
        except Exception as e:
            print(f"Ошибка рендеринга имени: {e}")

    def _render_health_bar(self, entity, style: Dict):
        """Рендеринг полоски здоровья"""
        try:
            if not hasattr(entity, 'health') or not hasattr(entity, 'max_health'):
                return
                
            x, y = entity.position[0], entity.position[1]
            health_ratio = entity.health / max(1, entity.max_health)
            
            # Определяем цвет здоровья
            if health_ratio > 0.6:
                fill_color = self.colors["health_good"]
            elif health_ratio > 0.3:
                fill_color = self.colors["health_warning"]
            else:
                fill_color = self.colors["health_critical"]
            
            # Создаем полоску здоровья
            bar_width = 1.0
            bar_height = 0.1
            
            # Фон полоски
            cm = CardMaker(f"health_bg_{id(entity)}")
            cm.set_frame(-bar_width/2, bar_width/2, -bar_height/2, bar_height/2)
            bg = self.game_scene.attach_new_node(cm.generate())
            bg.set_color(self.colors["health_bg"])
            bg.set_pos(x, 0, y + 0.8)
            bg.set_depth_write(False)
            
            # Заполнение полоски
            if health_ratio > 0:
                fill_width = bar_width * health_ratio
                cm = CardMaker(f"health_fill_{id(entity)}")
                cm.set_frame(-fill_width/2, fill_width/2, -bar_height/2, bar_height/2)
                fill = self.game_scene.attach_new_node(cm.generate())
                fill.set_color(fill_color)
                fill.set_pos(x, 0, y + 0.8)
                fill.set_depth_write(False)
                
        except Exception as e:
            print(f"Ошибка рендеринга полоски здоровья: {e}")

    def render_ui(self):
        """Рендеринг UI элементов"""
        try:
            # Рендерим FPS
            if self.show_fps:
                self._update_fps()
                self._render_fps()
            
            # Рендерим отладочную информацию
            if self.show_debug_info:
                self._render_debug_info()
                
        except Exception as e:
            print(f"Ошибка рендеринга UI: {e}")

    def _update_fps(self):
        """Обновление FPS"""
        current_time = time.time()
        self.stats.frames_rendered += 1
        
        if current_time - self.stats.last_fps_time >= 1.0:
            self.stats.fps = self.stats.frames_rendered
            self.stats.frames_rendered = 0
            self.stats.last_fps_time = current_time

    def _render_fps(self):
        """Рендеринг FPS"""
        try:
            # Удаляем старый FPS текст
            old_fps = self.debug_scene.find("fps_text")
            if not old_fps.is_empty():
                old_fps.remove_node()
            
            # Создаем новый FPS текст
            text = OnscreenText(
                text=f"FPS: {self.stats.fps}",
                pos=(-1.3, 0.9),
                scale=0.04,
                fg=self.colors["text"],
                shadow=(0, 0, 0, 1),
                parent=self.debug_scene
            )
            text.set_name("fps_text")
            
        except Exception as e:
            print(f"Ошибка рендеринга FPS: {e}")

    def _render_debug_info(self):
        """Рендеринг отладочной информации"""
        try:
            # Удаляем старую отладочную информацию
            old_debug = self.debug_scene.find("debug_info")
            if not old_debug.is_empty():
                old_debug.remove_node()
            
            debug_text = [
                f"Камера: ({self.camera_x:.1f}, {self.camera_y:.1f})",
                f"Зум: {self.camera_zoom:.2f}",
                f"Сущности: {self.stats.entities_rendered}",
                f"Время рендера: {self.stats.render_time:.3f}ms"
            ]
            
            # Создаем контейнер для отладочной информации
            debug_container = self.debug_scene.attach_new_node("debug_info")
            
            for i, text in enumerate(debug_text):
                text_node = OnscreenText(
                    text=text,
                    pos=(-1.3, 0.8 - i * 0.05),
                    scale=0.03,
                    fg=self.colors["text"],
                    shadow=(0, 0, 0, 1),
                    parent=debug_container
                )
                
        except Exception as e:
            print(f"Ошибка рендеринга отладочной информации: {e}")

    def render_frame(self):
        """Рендеринг одного кадра"""
        try:
            start_time = time.time()
            
            # Очищаем старые элементы
            self.clear()
            
            # Рендерим UI
            self.render_ui()
            
            # Обновляем статистику
            self.stats.render_time = (time.time() - start_time) * 1000
            
        except Exception as e:
            print(f"Ошибка рендеринга кадра: {e}")

    def center_camera_on_player(self, player):
        """Центрирует камеру на игроке"""
        try:
            if player and hasattr(player, 'position'):
                self.camera_x = player.position[0]
                self.camera_y = player.position[1]
                self.set_camera(self.camera_x, self.camera_y, self.camera_zoom)
        except Exception as e:
            print(f"Ошибка центрирования камеры: {e}")

    def get_world_position(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Получает мировую позицию по экранным координатам"""
        return self.screen_to_world(screen_x, screen_y)

    def draw_banner(self, text: str, color: Vec4 = None):
        """Рисует баннер с текстом"""
        try:
            if color is None:
                color = self.colors["text"]
            
            # Создаем баннер
            text_node = OnscreenText(
                text=text,
                pos=(0, 0),
                scale=0.08,
                fg=color,
                shadow=(0, 0, 0, 1),
                parent=self.ui_scene
            )
            text_node.set_name("banner")
            
        except Exception as e:
            print(f"Ошибка рисования баннера: {e}")

    def draw_minimap(self, entities: List, player, size: float = 0.3):
        """Рисует миникарту"""
        try:
            if not entities and not player:
                return
                
            # Позиция миникарты (правый верхний угол)
            map_x = 1.2
            map_y = 0.8
            
            # Фон миникарты
            cm = CardMaker("minimap_bg")
            cm.set_frame(map_x - size, map_x + size, map_y - size, map_y + size)
            bg = self.ui_scene.attach_new_node(cm.generate())
            bg.set_color(self.colors["background"])
            bg.set_depth_write(False)
            
            # Масштаб миникарты
            scale = size / 10  # 20 - размер игрового мира
            
            # Рисуем игрока
            if player and hasattr(player, 'position'):
                px = map_x + player.position[0] * scale
                py = map_y + player.position[1] * scale
                
                cm = CardMaker("player_minimap")
                cm.set_frame(-0.01, 0.01, -0.01, 0.01)
                player_dot = self.ui_scene.attach_new_node(cm.generate())
                player_dot.set_color(self.colors["player"])
                player_dot.set_pos(px, 0, py)
                player_dot.set_depth_write(False)
            
            # Рисуем врагов
            for entity in entities:
                if hasattr(entity, 'position'):
                    ex = map_x + entity.position[0] * scale
                    ey = map_y + entity.position[1] * scale
                    
                    cm = CardMaker(f"enemy_minimap_{id(entity)}")
                    cm.set_frame(-0.008, 0.008, -0.008, 0.008)
                    enemy_dot = self.ui_scene.attach_new_node(cm.generate())
                    enemy_dot.set_color(self.colors["enemy_warrior"])
                    enemy_dot.set_pos(ex, 0, ey)
                    enemy_dot.set_depth_write(False)
                    
        except Exception as e:
            print(f"Ошибка рисования миникарты: {e}")

    def toggle_debug_info(self):
        """Переключает отображение отладочной информации"""
        self.show_debug_info = not self.show_debug_info

    def toggle_fps_display(self):
        """Переключает отображение FPS"""
        self.show_fps = not self.show_fps

    def toggle_health_bars(self):
        """Переключает отображение полосок здоровья"""
        self.show_health_bars = not self.show_health_bars

    def toggle_names(self):
        """Переключает отображение имен"""
        self.show_names = not self.show_names

    def get_render_stats(self) -> RenderStats:
        """Получает статистику рендеринга"""
        return self.stats
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Очищаем кэш сущностей
            for node in self._cached_entities.values():
                if not node.is_empty():
                    node.remove_node()
            self._cached_entities.clear()
            
            # Очищаем сцены
            self.game_scene.remove_node()
            self.ui_scene.remove_node()
            self.debug_scene.remove_node()
            
        except Exception as e:
            print(f"Ошибка очистки render manager: {e}")
