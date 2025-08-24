#!/usr/bin/env python3
"""
Оптимизированная игровая сцена с простыми объектами
Заменяет функциональность старого GameInterface с улучшенной архитектурой
"""

import pygame
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import random

from core.game_engine import GameState
from core.simple_entity_system import entity_manager, SimpleEntity, EmotionType
from core.isometric_system import IsometricProjection, BeaconNavigationSystem
from core.movement_system import MovementSystem
from core.level_progression import LevelProgressionSystem
from ui.modern_hud import create_modern_hud, get_modern_hud, ModernHUD
from ui.camera import Camera

logger = logging.getLogger(__name__)


@dataclass
class GameSceneConfig:
    """Конфигурация игровой сцены"""
    enable_debug_hud: bool = False
    enable_ai_learning: bool = True
    enable_autonomous_movement: bool = True
    camera_speed: int = 20
    zoom_speed: float = 1.2
    entity_spawn_rate: float = 2.0  # секунды между спавном


class GameScene:
    """
    Оптимизированная игровая сцена с простыми объектами
    Управляет игровым процессом и взаимодействием с системами
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.config = GameSceneConfig()
        
        # Игровые объекты
        self.player: Optional[SimpleEntity] = None
        self.entities: List[SimpleEntity] = []
        self.obstacles: List[Any] = []
        self.chests: List[Any] = []
        self.items: List[Any] = []
        
        # Системы
        self.movement_system = MovementSystem()
        self.level_progression = LevelProgressionSystem()
        self.beacon_navigation = BeaconNavigationSystem()
        
        # Современный HUD
        self.modern_hud: Optional[ModernHUD] = None
        self._create_modern_hud()
        
        # Состояние
        self.autonomous_movement = self.config.enable_autonomous_movement
        self.current_cycle = 1
        self.game_time = 0.0
        self.last_spawn_time = 0.0
        
        # Статистика
        self.stats = {
            'enemies_defeated': 0,
            'items_collected': 0,
            'levels_completed': 0,
            'play_time': 0.0,
            'entities_count': 0,
            'fps': 0.0
        }
        
        logger.info("Игровая сцена инициализирована")
    
    def _create_modern_hud(self):
        """Создание современного HUD"""
        try:
            if self.engine.screen and self.engine.renderer:
                fonts = self.engine.renderer.fonts if hasattr(self.engine.renderer, 'fonts') else {}
                self.modern_hud = create_modern_hud(self.engine.screen, fonts)
                logger.info("Современный HUD создан")
        except Exception as e:
            logger.error(f"Ошибка создания современного HUD: {e}")
    
    def initialize(self) -> bool:
        """Инициализация сцены"""
        try:
            logger.info("Инициализация игровой сцены...")
            
            # Создание игрока
            self._create_player()
            
            # Создание начального мира
            self._create_initial_world()
            
            # Инициализация систем
            self._initialize_systems()
            
            logger.info("Игровая сцена успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игровой сцены: {e}")
            return False
    
    def _create_player(self):
        """Создание игрока"""
        try:
            # Получаем системы
            emotion_system = self.engine.get_system('emotion_system')
            
            # Создаем игрока как простую сущность
            self.player = entity_manager.create_entity(
                entity_id="PLAYER_001",
                entity_type="player",
                position=(400, 300, 0),
                emotion_system=emotion_system
            )
            
            # Устанавливаем начальную эмоцию
            if self.player:
                self.player.set_emotion(EmotionType.CONFIDENCE, 0.7)
            
            logger.info("Игрок создан")
            
        except Exception as e:
            logger.error(f"Ошибка создания игрока: {e}")
    
    def _create_initial_world(self):
        """Создание начального мира"""
        try:
            # Создаем несколько NPC
            for i in range(3):
                npc = entity_manager.create_entity(
                    entity_id=f"NPC_{i:03d}",
                    entity_type="npc",
                    position=(
                        random.randint(100, 700),
                        random.randint(100, 500),
                        0
                    )
                )
                if npc:
                    # Случайная эмоция для NPC
                    emotions = list(EmotionType)
                    emotion = random.choice(emotions)
                    intensity = random.uniform(0.3, 0.8)
                    npc.set_emotion(emotion, intensity)
                    self.entities.append(npc)
            
            # Создаем несколько врагов
            for i in range(2):
                enemy = entity_manager.create_entity(
                    entity_id=f"ENEMY_{i:03d}",
                    entity_type="enemy",
                    position=(
                        random.randint(200, 600),
                        random.randint(200, 400),
                        0
                    )
                )
                if enemy:
                    enemy.set_emotion(EmotionType.ANGRY, 0.6)
                    self.entities.append(enemy)
            
            # Создаем предметы
            for i in range(5):
                item = entity_manager.create_entity(
                    entity_id=f"ITEM_{i:03d}",
                    entity_type="item",
                    position=(
                        random.randint(50, 750),
                        random.randint(50, 550),
                        0
                    )
                )
                if item:
                    self.entities.append(item)
            
            logger.info(f"Начальный мир создан: {len(self.entities)} сущностей")
            
        except Exception as e:
            logger.error(f"Ошибка создания начального мира: {e}")
    
    def _initialize_systems(self):
        """Инициализация систем"""
        try:
            # Инициализация системы прогрессии
            self.level_progression.initialize()
            
            # Инициализация навигации
            self.beacon_navigation.initialize()
            
            logger.info("Системы инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации систем: {e}")
    
    def handle_event(self, event: pygame.event.Event):
        """Обработка событий"""
        try:
            # Обработка HUD событий
            if self.modern_hud and self.modern_hud.handle_event(event):
                return
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
                
        except Exception as e:
            logger.error(f"Ошибка обработки события: {e}")
    
    def _handle_keydown(self, key: int):
        """Обработка нажатий клавиш"""
        try:
            if key == pygame.K_ESCAPE:
                self.engine.set_state(GameState.PAUSED)
                return
            
            # Управление камерой
            if key == pygame.K_c and self.player:
                self._center_camera_on_player()
            
            # Свободная камера
            camera_speed = self.config.camera_speed
            if key in (pygame.K_LEFT, pygame.K_a):
                self._move_camera(-camera_speed, 0)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self._move_camera(camera_speed, 0)
            elif key in (pygame.K_UP, pygame.K_w):
                self._move_camera(0, -camera_speed)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self._move_camera(0, camera_speed)
            
            # Переключение состояний
            elif key == pygame.K_i:
                self.engine.set_state(GameState.INVENTORY)
            elif key == pygame.K_g:
                self.engine.set_state(GameState.GENETICS)
            elif key == pygame.K_e:
                self.engine.set_state(GameState.EMOTIONS)
            elif key == pygame.K_v:
                self.engine.set_state(GameState.EVOLUTION)
            
            # Игровое взаимодействие
            elif self.player:
                self._handle_gameplay_input(key)
            
        except Exception as e:
            logger.error(f"Ошибка обработки нажатия клавиши: {e}")
    
    def _handle_gameplay_input(self, key: int):
        """Обработка игрового ввода"""
        try:
            # Создание объектов
            if key == pygame.K_1:
                self._create_trap()
            elif key == pygame.K_2:
                self._create_geo_barrier()
            elif key == pygame.K_3:
                self._create_chest()
            elif key == pygame.K_4:
                self._add_enemy()
            
            # Активация эмоций
            elif key == pygame.K_5:
                self._activate_emotion("angry")
            elif key == pygame.K_6:
                self._activate_emotion("curiosity")
            elif key == pygame.K_7:
                self._activate_emotion("fear")
            elif key == pygame.K_8:
                self._activate_emotion("love")
            
            # Навигация
            elif key == pygame.K_m:
                self._navigate_to_beacon()
            elif key == pygame.K_x:
                self._cancel_navigation()
            
            # Управление камерой
            elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
                self._zoom_camera(1.2)
            elif key == pygame.K_MINUS:
                self._zoom_camera(1/1.2)
            
            # Автономность
            elif key == pygame.K_SPACE:
                self._toggle_autonomous_movement()
            
        except Exception as e:
            logger.error(f"Ошибка обработки игрового ввода: {e}")
    
    def _center_camera_on_player(self):
        """Центрирование камеры на игроке"""
        try:
            if not self.player or not self.engine.renderer:
                return
            
            iso_projection = self.engine.renderer.isometric_projection
            if not iso_projection:
                return
            
            iso_x, iso_y = iso_projection.world_to_iso(
                self.player.position.x, self.player.position.y, self.player.position.z
            )
            
            iso_projection.camera_x = iso_x - self.engine.config.window_width // 2
            iso_projection.camera_y = iso_y - self.engine.config.window_height // 2
            
        except Exception as e:
            logger.error(f"Ошибка центрирования камеры: {e}")
    
    def _move_camera(self, dx: int, dy: int):
        """Перемещение камеры"""
        try:
            if not self.engine.renderer or not self.engine.renderer.isometric_projection:
                return
            
            iso_projection = self.engine.renderer.isometric_projection
            iso_projection.camera_x += dx
            iso_projection.camera_y += dy
            
        except Exception as e:
            logger.error(f"Ошибка перемещения камеры: {e}")
    
    def _zoom_camera(self, factor: float):
        """Масштабирование камеры"""
        try:
            if not self.engine.renderer or not self.engine.renderer.isometric_projection:
                return
            
            iso_projection = self.engine.renderer.isometric_projection
            iso_projection.set_zoom(iso_projection.zoom * factor)
            
        except Exception as e:
            logger.error(f"Ошибка масштабирования камеры: {e}")
    
    def _create_trap(self):
        """Создание ловушки"""
        try:
            if not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            trap_pos = (
                player_pos[0] + random.randint(-50, 50),
                player_pos[1] + random.randint(-50, 50),
                player_pos[2]
            )
            
            # Создаем ловушку как препятствие
            trap = entity_manager.create_entity(
                entity_id=f"TRAP_{int(time.time())}",
                entity_type="obstacle",
                position=trap_pos
            )
            
            if trap:
                self.obstacles.append(trap)
                logger.info(f"Создана ловушка: {trap.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания ловушки: {e}")
    
    def _create_geo_barrier(self):
        """Создание геобарьера"""
        try:
            if not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            barrier_pos = (
                player_pos[0] + random.randint(-30, 30),
                player_pos[1] + random.randint(-30, 30),
                player_pos[2]
            )
            
            # Создаем геобарьер
            barrier = entity_manager.create_entity(
                entity_id=f"BARRIER_{int(time.time())}",
                entity_type="obstacle",
                position=barrier_pos
            )
            
            if barrier:
                self.obstacles.append(barrier)
                logger.info(f"Создан геобарьер: {barrier.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания геобарьера: {e}")
    
    def _create_chest(self):
        """Создание сундука"""
        try:
            if not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            chest_pos = (
                player_pos[0] + random.randint(-40, 40),
                player_pos[1] + random.randint(-40, 40),
                player_pos[2]
            )
            
            # Создаем сундук как предмет
            chest = entity_manager.create_entity(
                entity_id=f"CHEST_{int(time.time())}",
                entity_type="item",
                position=chest_pos
            )
            
            if chest:
                self.chests.append(chest)
                logger.info(f"Создан сундук: {chest.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания сундука: {e}")
    
    def _add_enemy(self):
        """Добавление врага"""
        try:
            if not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            enemy_pos = (
                player_pos[0] + random.randint(-100, 100),
                player_pos[1] + random.randint(-100, 100),
                player_pos[2]
            )
            
            # Создаем врага
            enemy = entity_manager.create_entity(
                entity_id=f"ENEMY_{int(time.time())}",
                entity_type="enemy",
                position=enemy_pos
            )
            
            if enemy:
                enemy.set_emotion(EmotionType.ANGRY, 0.8)
                self.entities.append(enemy)
                logger.info(f"Добавлен враг: {enemy.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления врага: {e}")
    
    def _activate_emotion(self, emotion_type: str):
        """Активация эмоции"""
        try:
            if not self.player:
                return
            
            # Преобразуем строку в EmotionType
            emotion_map = {
                'angry': EmotionType.ANGRY,
                'curiosity': EmotionType.CURIOSITY,
                'fear': EmotionType.FEAR,
                'love': EmotionType.LOVE,
                'happy': EmotionType.HAPPY,
                'sad': EmotionType.SAD,
                'surprise': EmotionType.SURPRISE,
                'confidence': EmotionType.CONFIDENCE
            }
            
            emotion = emotion_map.get(emotion_type, EmotionType.NEUTRAL)
            self.player.set_emotion(emotion, 0.8)
            logger.info(f"Активирована эмоция: {emotion_type}")
            
        except Exception as e:
            logger.error(f"Ошибка активации эмоции: {e}")
    
    def _navigate_to_beacon(self):
        """Навигация к маяку"""
        try:
            if not self.player:
                return
            
            # Находим ближайший маяк
            nearest_beacon = self.beacon_navigation.find_nearest_beacon(self.player.position)
            if nearest_beacon:
                self.beacon_navigation.set_navigation_target(nearest_beacon)
                logger.info(f"Навигация к маяку: {nearest_beacon}")
            else:
                logger.info("Маяки не найдены")
            
        except Exception as e:
            logger.error(f"Ошибка навигации к маяку: {e}")
    
    def _cancel_navigation(self):
        """Отмена навигации"""
        try:
            self.beacon_navigation.clear_navigation_target()
            logger.info("Навигация отменена")
            
        except Exception as e:
            logger.error(f"Ошибка отмены навигации: {e}")
    
    def _toggle_autonomous_movement(self):
        """Переключение автономного движения"""
        try:
            self.autonomous_movement = not self.autonomous_movement
            status = "включено" if self.autonomous_movement else "отключено"
            logger.info(f"Автономное движение {status}")
            
        except Exception as e:
            logger.error(f"Ошибка переключения автономного движения: {e}")
    
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """Обработка клика мыши"""
        try:
            # Здесь можно добавить обработку кликов по UI элементам
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обработки клика мыши: {e}")
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """Обработка движения мыши"""
        try:
            # Здесь можно добавить обработку движения мыши
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обработки движения мыши: {e}")
    
    def update(self, delta_time: float):
        """Обновление сцены"""
        try:
            self.game_time += delta_time
            
            # Обновление игрока
            if self.player:
                self._update_player(delta_time)
            
            # Обновление сущностей
            self._update_entities(delta_time)
            
            # Обновление систем
            self._update_systems(delta_time)
            
            # Обновление HUD
            self._update_hud(delta_time)
            
            # Спавн новых сущностей
            self._spawn_entities(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления сцены: {e}")
    
    def _update_player(self, delta_time: float):
        """Обновление игрока"""
        try:
            if not self.player:
                return
            
            # Обновление движения
            if self.autonomous_movement:
                self.movement_system.update_autonomous_movement(self.player, delta_time)
            
            # Обновление AI
            if hasattr(self.player, 'ai_system') and self.player.ai_system:
                self.player.ai_system.update(delta_time)
            
            # Обновление эмоций
            if hasattr(self.player, 'emotion_system') and self.player.emotion_system:
                self.player.emotion_system.update(delta_time)
            
            # Обновление генетики
            if hasattr(self.player, 'genetic_system') and self.player.genetic_system:
                self.player.genetic_system.update(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления игрока: {e}")
    
    def _update_entities(self, delta_time: float):
        """Обновление сущностей"""
        try:
            for entity in self.entities[:]:  # Копия списка для безопасного удаления
                if entity:
                    # Обновление AI
                    if hasattr(entity, 'ai_system') and entity.ai_system:
                        entity.ai_system.update(delta_time)
                    
                    # Проверка здоровья
                    if hasattr(entity, 'health') and entity.health <= 0:
                        self.entities.remove(entity)
                        entity_manager.remove_entity(entity.entity_id)
                        self.stats['enemies_defeated'] += 1
                        logger.info(f"Сущность {entity.entity_id} уничтожена")
                
        except Exception as e:
            logger.error(f"Ошибка обновления сущностей: {e}")
    
    def _update_systems(self, delta_time: float):
        """Обновление систем"""
        try:
            # Обновление прогрессии
            self.level_progression.update(delta_time)
            
            # Обновление навигации
            self.beacon_navigation.update(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    def _update_hud(self, delta_time: float):
        """Обновление HUD"""
        try:
            if self.modern_hud:
                # Обновление HUD
                self.modern_hud.update(delta_time)
                
                # Обновление данных игрока
                if self.player:
                    player_data = {
                        'health': 100.0,  # Здесь должны быть реальные данные
                        'energy': 85.0,
                        'experience': 45.0,
                        'level': 5.0
                    }
                    self.modern_hud.update_player_data(player_data)
                
                # Обновление эмоций
                if self.player:
                    emotions = {
                        'confidence': 0.7,
                        'curiosity': 0.3,
                        'happiness': 0.5
                    }
                    self.modern_hud.update_emotions(emotions)
                
                # Обновление статистики
                self.stats['entities_count'] = len(self.entities)
                self.stats['fps'] = self.engine.stats.get('avg_fps', 0.0)
                self.modern_hud.update_game_stats(self.stats)
            
        except Exception as e:
            logger.error(f"Ошибка обновления HUD: {e}")
    
    def _spawn_entities(self, delta_time: float):
        """Спавн новых сущностей"""
        try:
            current_time = time.time()
            if current_time - self.last_spawn_time > self.config.entity_spawn_rate:
                self.last_spawn_time = current_time
                
                # Случайный тип сущности
                entity_types = ['npc', 'enemy', 'item']
                entity_type = random.choice(entity_types)
                
                # Случайная позиция
                pos = (
                    random.randint(50, 750),
                    random.randint(50, 550),
                    0
                )
                
                # Создаем сущность
                entity = entity_manager.create_entity(
                    entity_id=f"{entity_type.upper()}_{int(current_time)}",
                    entity_type=entity_type,
                    position=pos
                )
                
                if entity:
                    # Устанавливаем случайную эмоцию для NPC и врагов
                    if entity_type in ['npc', 'enemy']:
                        emotions = list(EmotionType)
                        emotion = random.choice(emotions)
                        intensity = random.uniform(0.3, 0.8)
                        entity.set_emotion(emotion, intensity)
                    
                    self.entities.append(entity)
                    logger.debug(f"Создана новая сущность: {entity.entity_id}")
                
        except Exception as e:
            logger.error(f"Ошибка спавна сущностей: {e}")
    
    def render(self, screen: pygame.Surface):
        """Рендеринг сцены"""
        try:
            if not self.engine.renderer:
                return
            
            # Рендеринг мира
            self._render_world(screen)
            
            # Рендеринг сущностей
            self._render_entities(screen)
            
            # Рендеринг игрока
            self._render_player(screen)
            
            # Рендеринг HUD
            self._render_hud(screen)
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга сцены: {e}")
    
    def _render_world(self, screen: pygame.Surface):
        """Рендеринг мира"""
        try:
            if not self.engine.renderer:
                return
            
            # Рендеринг фона
            self.engine.renderer.render_background(screen)
            
            # Рендеринг объектов
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'render'):
                    obstacle.render(screen)
            
            for chest in self.chests:
                if hasattr(chest, 'render'):
                    chest.render(screen)
            
            for item in self.items:
                if hasattr(item, 'render'):
                    item.render(screen)
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга мира: {e}")
    
    def _render_entities(self, screen: pygame.Surface):
        """Рендеринг сущностей"""
        try:
            if not self.engine.renderer:
                return
            
            # Получаем смещение камеры
            camera_offset = (0, 0)
            if hasattr(self.engine.renderer, 'isometric_projection'):
                iso_projection = self.engine.renderer.isometric_projection
                if iso_projection:
                    camera_offset = (iso_projection.camera_x, iso_projection.camera_y)
            
            # Рендеринг всех сущностей через менеджер
            entity_manager.render_all(screen, camera_offset)
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга сущностей: {e}")
    
    def _render_player(self, screen: pygame.Surface):
        """Рендеринг игрока"""
        try:
            if not self.engine.renderer or not self.player:
                return
            
            # Игрок уже отрендерен в _render_entities
            pass
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга игрока: {e}")
    
    def _render_hud(self, screen: pygame.Surface):
        """Рендеринг HUD"""
        try:
            if self.modern_hud:
                self.modern_hud.render()
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга HUD: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            logger.info("Очистка игровой сцены")
            
            # Очистка сущностей
            for entity in self.entities:
                if hasattr(entity, 'cleanup'):
                    entity.cleanup()
            
            # Очистка HUD
            if self.modern_hud and hasattr(self.modern_hud, 'cleanup'):
                self.modern_hud.cleanup()
            
            logger.info("Игровая сцена очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки игровой сцены: {e}")
