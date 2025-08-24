#!/usr/bin/env python3
"""
Game Scene - Основная игровая сцена
Отвечает только за игровой процесс и управление игровыми системами
"""

import logging
import pygame
import math
from typing import List, Optional, Dict, Any, Tuple
from ..core.scene_manager import Scene
from ..systems import (
    EvolutionSystem, AISystem, CombatSystem, 
    CraftingSystem, InventorySystem
)

logger = logging.getLogger(__name__)

class IsometricCamera:
    """Изометрическая камера"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Позиция камеры в мировых координатах
        self.world_x = 0.0
        self.world_y = 0.0
        
        # Масштаб
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        
        # Изометрические углы (стандартные 30 градусов)
        self.iso_angle = math.radians(30)
        self.cos_angle = math.cos(self.iso_angle)
        self.sin_angle = math.sin(self.iso_angle)
        
        # Размер тайла в пикселях
        self.tile_width = 64
        self.tile_height = 32
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Преобразование мировых координат в экранные (изометрическая проекция)"""
        # Смещение относительно камеры
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
        
        # Изометрическая проекция
        iso_x = (rel_x - rel_y) * self.cos_angle
        iso_y = (rel_x + rel_y) * self.sin_angle
        
        # Применяем масштаб
        iso_x *= self.zoom
        iso_y *= self.zoom
        
        # Центрируем на экране
        screen_x = int(iso_x + self.screen_width // 2)
        screen_y = int(iso_y + self.screen_height // 2)
        
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Преобразование экранных координат в мировые"""
        # Убираем центрирование
        rel_x = (screen_x - self.screen_width // 2) / self.zoom
        rel_y = (screen_y - self.screen_height // 2) / self.zoom
        
        # Обратная изометрическая проекция
        world_x = (rel_x / self.cos_angle + rel_y / self.sin_angle) / 2 + self.world_x
        world_y = (rel_y / self.sin_angle - rel_x / self.cos_angle) / 2 + self.world_y
        
        return world_x, world_y
    
    def move(self, dx: float, dy: float):
        """Перемещение камеры"""
        self.world_x += dx
        self.world_y += dy
    
    def set_zoom(self, zoom: float):
        """Установка масштаба"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
    
    def follow_entity(self, entity: Dict[str, Any], smooth: float = 0.1):
        """Следование за сущностью"""
        target_x = entity['x']
        target_y = entity['y']
        
        # Плавное следование
        self.world_x += (target_x - self.world_x) * smooth
        self.world_y += (target_y - self.world_y) * smooth

class GameScene(Scene):
    """Основная игровая сцена"""
    
    def __init__(self):
        super().__init__("game")
        
        # Игровые системы
        self.systems: Dict[str, Any] = {}
        
        # Игровые объекты
        self.entities: List[Any] = []
        self.particles: List[Any] = []
        self.ui_elements: List[Any] = []
        
        # Изометрическая камера
        self.camera = None  # Инициализируется в initialize()
        
        # Игровое время
        self.game_time = 0.0
        self.day_night_cycle = 0.0
        
        # Состояние игры
        self.game_paused = False
        self.show_debug = False
        
        # Графика
        self.background: Optional[pygame.Surface] = None
        self.font: Optional[pygame.font.Font] = None
        
        # Цвета
        self.colors = {
            'background': (50, 100, 50),
            'text': (255, 255, 255),
            'debug': (255, 255, 0),
            'ui': (100, 100, 100)
        }
        
        logger.info("Игровая сцена создана")
    
    def initialize(self) -> bool:
        """Инициализация игровой сцены"""
        try:
            logger.info("Инициализация игровой сцены...")
            
            # Инициализация изометрической камеры
            self.camera = IsometricCamera(1600, 900)
            
            # Создание шрифтов
            self._create_fonts()
            
            # Создание фона
            self._create_background()
            
            # Инициализация игровых систем
            self._initialize_game_systems()
            
            # Создание начальных объектов
            self._create_initial_objects()
            
            self.initialized = True
            logger.info("Игровая сцена успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игровой сцены: {e}")
            return False
    
    def _create_fonts(self):
        """Создание шрифтов"""
        try:
            self.font = pygame.font.Font(None, 24)
            logger.debug("Шрифты созданы")
        except Exception as e:
            logger.warning(f"Не удалось создать шрифты: {e}")
            self.font = pygame.font.SysFont(None, 24)
    
    def _create_background(self):
        """Создание фона игры"""
        try:
            # Создаем простой фон с травой
            self.background = pygame.Surface((1600, 900))
            
            # Рисуем траву
            grass_color = (34, 139, 34)
            self.background.fill(grass_color)
            
            # Добавляем текстуру
            for x in range(0, 1600, 20):
                for y in range(0, 900, 20):
                    if (x + y) % 40 == 0:
                        pygame.draw.circle(self.background, (28, 120, 28), (x, y), 2)
            
            logger.debug("Фон игры создан")
            
        except Exception as e:
            logger.warning(f"Не удалось создать фон: {e}")
            self.background = None
    
    def _initialize_game_systems(self):
        """Инициализация игровых систем"""
        try:
            # Здесь будут инициализироваться все игровые системы
            # AI, бой, крафтинг, эволюция и т.д.
            
            # Инициализация систем
            self.systems['evolution'] = EvolutionSystem()
            self.systems['ai'] = AISystem()
            self.systems['combat'] = CombatSystem()
            self.systems['crafting'] = CraftingSystem()
            self.systems['inventory'] = InventorySystem()
            
            # Инициализируем каждую систему
            for system_name, system in self.systems.items():
                if hasattr(system, 'initialize'):
                    system.initialize()
            
            logger.debug("Игровые системы инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать некоторые системы: {e}")
    
    def _create_initial_objects(self):
        """Создание начальных игровых объектов"""
        try:
            # Создаем тестового игрока
            self._create_test_player()
            
            # Создаем тестовых NPC
            self._create_test_npcs()
            
            # Создаем UI элементы
            self._create_ui_elements()
            
            logger.debug("Начальные объекты созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать некоторые объекты: {e}")
    
    def _create_test_player(self):
        """Создание тестового игрока"""
        player = {
            'type': 'player',
            'x': 800,
            'y': 450,
            'width': 32,
            'height': 32,
            'color': (255, 255, 0),
            'health': 100,
            'max_health': 100,
            'speed': 5.0
        }
        self.entities.append(player)
        logger.debug("Тестовый игрок создан")
    
    def _create_test_npcs(self):
        """Создание тестовых NPC"""
        npc_positions = [
            (400, 300, (255, 0, 0)),    # Красный NPC
            (1200, 600, (0, 0, 255)),   # Синий NPC
            (600, 700, (0, 255, 0))     # Зеленый NPC
        ]
        
        for i, (x, y, color) in enumerate(npc_positions):
            npc = {
                'type': 'npc',
                'x': x,
                'y': y,
                'width': 24,
                'height': 24,
                'color': color,
                'health': 50,
                'max_health': 50,
                'speed': 2.0,
                'ai_state': 'idle',
                'level': 1,
                'experience': 0
            }
            self.entities.append(npc)
            
            # Регистрируем NPC в AI системе
            if 'ai' in self.systems:
                entity_id = f"npc_{i}"
                if hasattr(self.systems['ai'], 'register_entity'):
                    self.systems['ai'].register_entity(entity_id, npc)
        
        logger.debug(f"Создано {len(npc_positions)} тестовых NPC")
    
    def _create_ui_elements(self):
        """Создание UI элементов"""
        # HUD элементы
        hud_elements = [
            {'type': 'health_bar', 'x': 20, 'y': 20, 'width': 200, 'height': 20},
            {'type': 'minimap', 'x': 1400, 'y': 20, 'width': 180, 'height': 120},
            {'type': 'inventory', 'x': 20, 'y': 800, 'width': 400, 'height': 80},
            {'type': 'menu_button', 'x': 1400, 'y': 800, 'width': 180, 'height': 40}
        ]
        
        for element in hud_elements:
            self.ui_elements.append(element)
        
        logger.debug(f"Создано {len(hud_elements)} UI элементов")
    
    def update(self, delta_time: float):
        """Обновление игровой сцены"""
        if self.game_paused:
            return
        
        # Обновление игрового времени
        self.game_time += delta_time
        self.day_night_cycle = (self.game_time / 300.0) % 1.0  # 5 минут на цикл
        
        # Обновление игровых систем
        self._update_game_systems(delta_time)
        
        # Обновление сущностей
        self._update_entities(delta_time)
        
        # Обновление частиц
        self._update_particles(delta_time)
        
        # Обновление UI
        self._update_ui(delta_time)
        
        # Обновление камеры
        self._update_camera(delta_time)
    
    def _update_game_systems(self, delta_time: float):
        """Обновление игровых систем"""
        # Здесь будет обновление всех игровых систем
        # AI, бой, крафтинг, эволюция и т.д.
        try:
            # Обновляем системы, которые имеют метод update
            if 'ai' in self.systems:
                # AI система обновляет все зарегистрированные сущности
                for entity in self.entities:
                    if entity['type'] == 'npc':
                        entity_id = f"{entity['type']}_{id(entity)}"
                        if hasattr(self.systems['ai'], 'update_entity'):
                            self.systems['ai'].update_entity(entity_id, entity, delta_time)
            
            # Обновляем систему боя
            if 'combat' in self.systems and hasattr(self.systems['combat'], 'update_combat'):
                self.systems['combat'].update_combat(delta_time)
            
            # Обновляем систему крафтинга
            if 'crafting' in self.systems and hasattr(self.systems['crafting'], 'update_crafting'):
                self.systems['crafting'].update_crafting(delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления игровых систем: {e}")
    
    def _update_entities(self, delta_time: float):
        """Обновление игровых сущностей"""
        for entity in self.entities:
            if entity['type'] == 'player':
                self._update_player(entity, delta_time)
            elif entity['type'] == 'npc':
                self._update_npc(entity, delta_time)
    
    def _update_player(self, player: dict, delta_time: float):
        """Обновление игрока"""
        # Обработка ввода
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            player['y'] -= player['speed']
        if keys[pygame.K_s]:
            player['y'] += player['speed']
        if keys[pygame.K_a]:
            player['x'] -= player['speed']
        if keys[pygame.K_d]:
            player['x'] += player['speed']
        
        # Ограничение позиции игрока
        player['x'] = max(0, min(1600 - player['width'], player['x']))
        player['y'] = max(0, min(900 - player['height'], player['y']))
    
    def _update_npc(self, npc: dict, delta_time: float):
        """Обновление NPC"""
        # Простой AI для тестовых NPC
        if npc['ai_state'] == 'idle':
            # Случайное движение
            if pygame.time.get_ticks() % 120 == 0:  # Каждые 2 секунды
                import random
                npc['x'] += random.randint(-20, 20)
                npc['y'] += random.randint(-20, 20)
                
                # Ограничение позиции
                npc['x'] = max(0, min(1600 - npc['width'], npc['x']))
                npc['y'] = max(0, min(900 - npc['height'], npc['y']))
    
    def _update_particles(self, delta_time: float):
        """Обновление частиц"""
        # Удаляем устаревшие частицы
        self.particles = [p for p in self.particles if p.get('life', 0) > 0]
        
        # Обновляем оставшиеся частицы
        for particle in self.particles:
            particle['life'] -= delta_time
            particle['x'] += particle.get('vx', 0) * delta_time
            particle['y'] += particle.get('vy', 0) * delta_time
    
    def _update_ui(self, delta_time: float):
        """Обновление UI"""
        # Обновление HUD элементов
        pass
    
    def _update_camera(self, delta_time: float):
        """Обновление изометрической камеры"""
        if not self.camera:
            return
            
        # Находим игрока для следования
        player = next((e for e in self.entities if e['type'] == 'player'), None)
        if player:
            # Плавно следуем за игроком
            self.camera.follow_entity(player, smooth=0.05)
        
        # Обработка управления камерой
        keys = pygame.key.get_pressed()
        camera_speed = 200.0 * delta_time
        
        # Управление камерой стрелками (если не следуем за игроком)
        if keys[pygame.K_LEFT]:
            self.camera.move(-camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            self.camera.move(camera_speed, 0)
        if keys[pygame.K_UP]:
            self.camera.move(0, -camera_speed)
        if keys[pygame.K_DOWN]:
            self.camera.move(0, camera_speed)
        
        # Масштабирование
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:  # Приближение
            self.camera.set_zoom(self.camera.zoom + 1.0 * delta_time)
        if keys[pygame.K_MINUS]:  # Отдаление
            self.camera.set_zoom(self.camera.zoom - 1.0 * delta_time)
    
    def render(self, screen: pygame.Surface):
        """Отрисовка игровой сцены"""
        # Отрисовка фона
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(self.colors['background'])
        
        # Отрисовка игровых объектов
        self._render_entities(screen)
        
        # Отрисовка частиц
        self._render_particles(screen)
        
        # Отрисовка UI
        self._render_ui(screen)
        
        # Отрисовка отладочной информации
        if self.show_debug:
            self._render_debug_info(screen)
    
    def _render_entities(self, screen: pygame.Surface):
        """Отрисовка игровых сущностей с изометрической проекцией"""
        if not self.camera:
            return
            
        for entity in self.entities:
            # Проверяем корректность цвета
            if 'color' not in entity or not isinstance(entity['color'], (tuple, list)) or len(entity['color']) != 3:
                logger.warning(f"Некорректный цвет для сущности {entity.get('type', 'unknown')}: {entity.get('color', 'missing')}")
                entity['color'] = (255, 255, 255)  # Белый цвет по умолчанию
            
            # Проверяем, что все компоненты цвета - числа от 0 до 255
            color = entity['color']
            if not all(isinstance(c, (int, float)) and 0 <= c <= 255 for c in color):
                logger.warning(f"Некорректные значения цвета для сущности {entity.get('type', 'unknown')}: {color}")
                entity['color'] = (255, 255, 255)  # Белый цвет по умолчанию
                color = entity['color']
            
            # Преобразуем мировые координаты в экранные (изометрическая проекция)
            screen_x, screen_y = self.camera.world_to_screen(entity['x'], entity['y'])
            
            # Размеры в изометрической проекции
            iso_width = int(entity['width'] * self.camera.zoom)
            iso_height = int(entity['height'] * self.camera.zoom * 0.5)  # Сжимаем по вертикали для изометрии
            
            if entity['type'] == 'player':
                # Игрок - желтый ромб (изометрическая проекция прямоугольника)
                self._draw_isometric_rect(screen, screen_x, screen_y, iso_width, iso_height, (255, 255, 0))
                
                # Полоска здоровья над игроком
                health_ratio = entity['health'] / entity['max_health']
                health_width = int(iso_width * health_ratio)
                health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.25 else (255, 0, 0)
                
                # Фон полоски здоровья
                pygame.draw.rect(screen, (100, 0, 0), (screen_x - iso_width//2, screen_y - iso_height - 15, iso_width, 5))
                # Полоска здоровья
                pygame.draw.rect(screen, health_color, (screen_x - iso_width//2, screen_y - iso_height - 15, health_width, 5))
                
            elif entity['type'] == 'npc':
                # NPC - цветной ромб
                self._draw_isometric_rect(screen, screen_x, screen_y, iso_width, iso_height, color)
                
                # Полоска здоровья над NPC
                health_ratio = entity['health'] / entity['max_health']
                health_width = int(iso_width * health_ratio)
                health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.25 else (255, 0, 0)
                
                # Фон полоски здоровья
                pygame.draw.rect(screen, (100, 0, 0), (screen_x - iso_width//2, screen_y - iso_height - 15, iso_width, 5))
                # Полоска здоровья
                pygame.draw.rect(screen, health_color, (screen_x - iso_width//2, screen_y - iso_height - 15, health_width, 5))
    
    def _draw_isometric_rect(self, screen: pygame.Surface, center_x: int, center_y: int, width: int, height: int, color: tuple):
        """Отрисовка изометрического прямоугольника (ромба)"""
        # Точки ромба
        points = [
            (center_x, center_y - height),  # Верх
            (center_x + width//2, center_y),  # Право
            (center_x, center_y + height),  # Низ
            (center_x - width//2, center_y)   # Лево
        ]
        
        # Рисуем заполненный ромб
        pygame.draw.polygon(screen, color, points)
        
        # Рисуем контур
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    def _render_particles(self, screen: pygame.Surface):
        """Отрисовка частиц"""
        for particle in self.particles:
            # Проверяем корректность цвета частицы
            if 'color' not in particle or not isinstance(particle['color'], (tuple, list)) or len(particle['color']) != 3:
                logger.warning(f"Некорректный цвет для частицы: {particle.get('color', 'missing')}")
                particle['color'] = (255, 255, 255)  # Белый цвет по умолчанию
            
            # Проверяем, что все компоненты цвета - числа от 0 до 255
            color = particle['color']
            if not all(isinstance(c, (int, float)) and 0 <= c <= 255 for c in color):
                logger.warning(f"Некорректные значения цвета для частицы: {color}")
                particle['color'] = (255, 255, 255)  # Белый цвет по умолчанию
                color = particle['color']
            
            # Отрисовка частицы
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), 3)
            
            # Полоска жизни частицы
            life_ratio = particle['life'] / particle['max_life']
            life_width = int(10 * life_ratio)
            life_color = (0, 255, 0) if life_ratio > 0.5 else (255, 255, 0) if life_ratio > 0.25 else (255, 0, 0)
            
            pygame.draw.rect(screen, (255, 0, 0), (int(particle['x'] - 5), int(particle['y'] - 8), 10, 2))
            pygame.draw.rect(screen, life_color, (int(particle['x'] - 5), int(particle['y'] - 8), life_width, 2))
    
    def _render_ui(self, screen: pygame.Surface):
        """Отрисовка UI"""
        if not self.font:
            return
        
        # Отрисовка HUD элементов
        for element in self.ui_elements:
            if element['type'] == 'health_bar':
                self._render_health_bar(screen, element)
            elif element['type'] == 'minimap':
                self._render_minimap(screen, element)
            elif element['type'] == 'inventory':
                self._render_inventory(screen, element)
            elif element['type'] == 'menu_button':
                self._render_menu_button(screen, element)
    
    def _render_health_bar(self, screen: pygame.Surface, element: dict):
        """Отрисовка полоски здоровья"""
        player = next((e for e in self.entities if e['type'] == 'player'), None)
        if not player:
            return
        
        x, y, width, height = element['x'], element['y'], element['width'], element['height']
        
        # Фон полоски здоровья
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Полоска здоровья
        health_ratio = player['health'] / player['max_health']
        health_width = int(width * health_ratio)
        health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.25 else (255, 0, 0)
        
        pygame.draw.rect(screen, health_color, (x, y, health_width, height))
        
        # Текст здоровья
        health_text = f"HP: {player['health']}/{player['max_health']}"
        text_surface = self.font.render(health_text, True, self.colors['text'])
        screen.blit(text_surface, (x + 5, y + 2))
    
    def _render_minimap(self, screen: pygame.Surface, element: dict):
        """Отрисовка мини-карты"""
        x, y, width, height = element['x'], element['y'], element['width'], element['height']
        
        # Фон мини-карты
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        
        # Отрисовка сущностей на мини-карте
        scale = min(width, height) / 1600  # Масштаб карты
        
        for entity in self.entities:
            map_x = x + entity['x'] * scale
            map_y = y + entity['y'] * scale
            
            if entity['type'] == 'player':
                color = (255, 255, 0)  # Желтый для игрока
            else:
                color = entity['color']
            
            pygame.draw.circle(screen, color, (int(map_x), int(map_y)), 2)
    
    def _render_inventory(self, screen: pygame.Surface, element: dict):
        """Отрисовка инвентаря"""
        x, y, width, height = element['x'], element['y'], element['width'], element['height']
        
        # Фон инвентаря
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        
        # Заголовок инвентаря
        if self.font:
            title_text = "Инвентарь"
            title_surface = self.font.render(title_text, True, self.colors['text'])
            screen.blit(title_surface, (x + 5, y + 5))
    
    def _render_menu_button(self, screen: pygame.Surface, element: dict):
        """Отрисовка кнопки "Назад в меню" """
        x, y, width, height = element['x'], element['y'], element['width'], element['height']
        
        # Фон кнопки
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        
        # Текст кнопки
        if self.font:
            text_surface = self.font.render("Назад в меню", True, self.colors['text'])
            text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
            screen.blit(text_surface, text_rect)
    
    def _render_debug_info(self, screen: pygame.Surface):
        """Отрисовка отладочной информации"""
        if not self.font:
            return
        
        debug_info = [
            f"FPS: {pygame.time.get_ticks() // 1000}",
            f"Entities: {len(self.entities)}",
            f"Particles: {len(self.particles)}",
            f"Camera: ({self.camera_x:.1f}, {self.camera_y:.1f})",
            f"Game Time: {self.game_time:.1f}s",
            f"Day/Night: {self.day_night_cycle:.2f}"
        ]
        
        for i, info in enumerate(debug_info):
            text_surface = self.font.render(info, True, self.colors['debug'])
            screen.blit(text_surface, (10, 10 + i * 25))
    
    def handle_event(self, event: pygame.event.Event):
        """Обработка событий"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
    
    def _handle_keydown(self, event: pygame.event.Event):
        """Обработка нажатий клавиш"""
        if event.key == pygame.K_F1:
            self.show_debug = not self.show_debug
        elif event.key == pygame.K_p:
            # Переход к сцене паузы
            if self.scene_manager:
                logger.info("Переход к сцене паузы")
                self.scene_manager.switch_to_scene("pause", "instant")
            else:
                logger.warning("SceneManager недоступен для перехода к паузе")
        elif event.key == pygame.K_SPACE:
            self._create_test_particle()
        elif event.key == pygame.K_ESCAPE:
            # Возврат в главное меню
            if self.scene_manager:
                logger.info("Возврат в главное меню")
                self.scene_manager.switch_to_scene("menu", "instant")
            else:
                logger.warning("SceneManager недоступен для возврата в меню")
    
    def _handle_mouse_click(self, event: pygame.event.Event):
        """Обработка кликов мыши"""
        if event.button == 1:  # Левый клик
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клик по кнопке "Назад в меню"
            for element in self.ui_elements:
                if element['type'] == 'menu_button':
                    if (element['x'] <= mouse_pos[0] <= element['x'] + element['width'] and 
                        element['y'] <= mouse_pos[1] <= element['y'] + element['height']):
                        if self.scene_manager:
                            logger.info("Клик по кнопке 'Назад в меню'")
                            self.scene_manager.switch_to_scene("menu", "instant")
                        return
            
            # Создание частицы в месте клика
            self._create_particle_at(mouse_pos[0], mouse_pos[1])
    
    def _create_test_particle(self):
        """Создание тестовой частицы"""
        import random
        
        particle = {
            'x': random.randint(0, 1600),
            'y': random.randint(0, 900),
            'vx': random.uniform(-50, 50),
            'vy': random.uniform(-50, 50),
            'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
            'life': 2.0,
            'max_life': 2.0
        }
        
        self.particles.append(particle)
    
    def _create_particle_at(self, x: int, y: int):
        """Создание частицы в указанной позиции"""
        import random
        
        particle = {
            'x': x,
            'y': y,
            'vx': random.uniform(-30, 30),
            'vy': random.uniform(-30, 30),
            'color': (255, 255, 0),
            'life': 1.0,
            'max_life': 1.0
        }
        
        self.particles.append(particle)
    
    def cleanup(self):
        """Очистка ресурсов игровой сцены"""
        logger.info("Очистка игровой сцены...")
        
        # Очистка графических ресурсов
        self.background = None
        self.font = None
        
        # Очистка игровых объектов
        self.entities.clear()
        self.particles.clear()
        self.ui_elements.clear()
        
        # Очистка систем
        self.systems.clear()
        
        super().cleanup()
        logger.info("Игровая сцена очищена")
