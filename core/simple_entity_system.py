#!/usr/bin/env python3
"""
Система простых объектов с цветовой индикацией эмоций
Заменяет спрайты на геометрические фигуры с цветовым кодированием
"""

import pygame
import math
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """Типы эмоций"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    CURIOSITY = "curiosity"
    CONFIDENCE = "confidence"


class EntityType(Enum):
    """Типы сущностей"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    ITEM = "item"
    OBSTACLE = "obstacle"
    EFFECT = "effect"


@dataclass
class EmotionState:
    """Состояние эмоции"""
    emotion_type: EmotionType
    intensity: float  # 0.0 - 1.0
    duration: float  # время в секундах
    start_time: float


@dataclass
class EntityVisual:
    """Визуальное представление сущности"""
    entity_type: EntityType
    size: int
    base_color: Tuple[int, int, int]
    shape: str  # "circle", "square", "triangle", "diamond"
    border_width: int = 2
    border_color: Tuple[int, int, int] = (0, 0, 0)
    glow_radius: int = 0
    glow_color: Tuple[int, int, int] = (255, 255, 255)


class EmotionColorMapper:
    """Маппер цветов для эмоций"""
    
    EMOTION_COLORS = {
        EmotionType.NEUTRAL: (128, 128, 128),    # Серый
        EmotionType.HAPPY: (255, 255, 0),        # Желтый
        EmotionType.SAD: (0, 0, 255),            # Синий
        EmotionType.ANGRY: (255, 0, 0),          # Красный
        EmotionType.FEAR: (128, 0, 128),         # Фиолетовый
        EmotionType.SURPRISE: (255, 165, 0),     # Оранжевый
        EmotionType.DISGUST: (0, 128, 0),        # Зеленый
        EmotionType.LOVE: (255, 192, 203),       # Розовый
        EmotionType.CURIOSITY: (0, 255, 255),    # Голубой
        EmotionType.CONFIDENCE: (255, 215, 0)    # Золотой
    }
    
    @classmethod
    def get_emotion_color(cls, emotion_type: EmotionType, intensity: float = 1.0) -> Tuple[int, int, int]:
        """Получение цвета эмоции с учетом интенсивности"""
        base_color = cls.EMOTION_COLORS.get(emotion_type, (128, 128, 128))
        
        # Применяем интенсивность
        return tuple(int(c * intensity) for c in base_color)
    
    @classmethod
    def blend_colors(cls, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    ratio: float) -> Tuple[int, int, int]:
        """Смешивание двух цветов"""
        return tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))


class SimpleEntity:
    """Простая сущность с цветовой индикацией эмоций"""
    
    def __init__(self, entity_id: str, entity_type: EntityType, position: Tuple[float, float, float],
                 visual: EntityVisual, emotion_system=None):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.position = pygame.math.Vector3(position)
        self.visual = visual
        self.emotion_system = emotion_system
        
        # Эмоциональное состояние
        self.current_emotion = EmotionState(EmotionType.NEUTRAL, 0.5, 0.0, time.time())
        self.emotion_history: List[EmotionState] = []
        
        # Анимация
        self.animation_time = 0.0
        self.pulse_phase = 0.0
        self.rotation_angle = 0.0
        
        # Эффекты
        self.effects: List[Dict[str, Any]] = []
        
        logger.info(f"Создана простая сущность: {entity_id} ({entity_type.value})")
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        self.animation_time += delta_time
        self.pulse_phase = (self.pulse_phase + delta_time * 2) % (2 * math.pi)
        self.rotation_angle = (self.rotation_angle + delta_time * 30) % 360
        
        # Обновление эмоций
        self._update_emotions(delta_time)
        
        # Обновление эффектов
        self._update_effects(delta_time)
    
    def _update_emotions(self, delta_time: float):
        """Обновление эмоционального состояния"""
        if self.emotion_system and hasattr(self.emotion_system, 'get_current_emotion'):
            try:
                emotion_data = self.emotion_system.get_current_emotion()
                if emotion_data:
                    emotion_type = EmotionType(emotion_data.get('type', 'neutral'))
                    intensity = emotion_data.get('intensity', 0.5)
                    
                    self.current_emotion = EmotionState(
                        emotion_type=emotion_type,
                        intensity=intensity,
                        duration=0.0,
                        start_time=time.time()
                    )
            except Exception as e:
                logger.warning(f"Ошибка обновления эмоций для {self.entity_id}: {e}")
    
    def _update_effects(self, delta_time: float):
        """Обновление эффектов"""
        for effect in self.effects[:]:
            if 'duration' in effect:
                effect['duration'] -= delta_time
                if effect['duration'] <= 0:
                    self.effects.remove(effect)
    
    def set_emotion(self, emotion_type: EmotionType, intensity: float = 1.0, duration: float = 5.0):
        """Установка эмоции"""
        self.current_emotion = EmotionState(
            emotion_type=emotion_type,
            intensity=intensity,
            duration=duration,
            start_time=time.time()
        )
        
        # Добавляем в историю
        self.emotion_history.append(self.current_emotion)
        if len(self.emotion_history) > 10:  # Ограничиваем историю
            self.emotion_history.pop(0)
        
        logger.debug(f"Установлена эмоция {emotion_type.value} для {self.entity_id}")
    
    def add_effect(self, effect_type: str, duration: float, **params):
        """Добавление эффекта"""
        effect = {
            'type': effect_type,
            'duration': duration,
            'start_time': time.time(),
            **params
        }
        self.effects.append(effect)
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Рендеринг сущности"""
        try:
            # Позиция на экране
            screen_x = int(self.position.x - camera_offset[0])
            screen_y = int(self.position.y - camera_offset[1])
            
            # Размер с учетом пульсации
            pulse_factor = 1.0 + 0.1 * math.sin(self.pulse_phase)
            size = int(self.visual.size * pulse_factor)
            
            # Цвет с учетом эмоций
            emotion_color = EmotionColorMapper.get_emotion_color(
                self.current_emotion.emotion_type,
                self.current_emotion.intensity
            )
            
            # Смешиваем с базовым цветом
            final_color = EmotionColorMapper.blend_colors(
                self.visual.base_color, emotion_color, 0.7
            )
            
            # Рисуем основную фигуру
            self._draw_shape(screen, screen_x, screen_y, size, final_color)
            
            # Рисуем границу
            if self.visual.border_width > 0:
                self._draw_shape(screen, screen_x, screen_y, size, 
                               self.visual.border_color, border=True)
            
            # Рисуем эффекты
            self._draw_effects(screen, screen_x, screen_y, size)
            
            # Рисуем эмоциональную ауру
            self._draw_emotion_aura(screen, screen_x, screen_y, size)
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга сущности {self.entity_id}: {e}")
    
    def _draw_shape(self, screen: pygame.Surface, x: int, y: int, size: int, 
                   color: Tuple[int, int, int], border: bool = False):
        """Рисование формы сущности"""
        width = self.visual.border_width if border else 0
        
        if self.visual.shape == "circle":
            pygame.draw.circle(screen, color, (x, y), size, width)
        
        elif self.visual.shape == "square":
            rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
            pygame.draw.rect(screen, color, rect, width)
        
        elif self.visual.shape == "triangle":
            points = [
                (x, y - size),
                (x - size, y + size),
                (x + size, y + size)
            ]
            pygame.draw.polygon(screen, color, points, width)
        
        elif self.visual.shape == "diamond":
            points = [
                (x, y - size),
                (x + size, y),
                (x, y + size),
                (x - size, y)
            ]
            pygame.draw.polygon(screen, color, points, width)
    
    def _draw_emotion_aura(self, screen: pygame.Surface, x: int, y: int, size: int):
        """Рисование эмоциональной ауры"""
        if self.current_emotion.intensity < 0.3:
            return
        
        emotion_color = EmotionColorMapper.get_emotion_color(
            self.current_emotion.emotion_type,
            self.current_emotion.intensity
        )
        
        # Создаем полупрозрачный цвет
        aura_color = (*emotion_color, 100)  # Альфа-канал
        
        # Размер ауры зависит от интенсивности эмоции
        aura_size = int(size * (1.5 + self.current_emotion.intensity))
        
        # Рисуем несколько кругов для эффекта свечения
        for i in range(3):
            current_size = aura_size - i * 5
            if current_size > size:
                alpha = 50 - i * 15
                current_color = (*emotion_color, max(0, alpha))
                
                # Создаем поверхность для альфа-канала
                aura_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(aura_surface, current_color, (current_size, current_size), current_size)
                screen.blit(aura_surface, (x - current_size, y - current_size))
    
    def _draw_effects(self, screen: pygame.Surface, x: int, y: int, size: int):
        """Рисование эффектов"""
        for effect in self.effects:
            effect_type = effect.get('type', '')
            
            if effect_type == 'heal':
                self._draw_heal_effect(screen, x, y, size, effect)
            elif effect_type == 'damage':
                self._draw_damage_effect(screen, x, y, size, effect)
            elif effect_type == 'buff':
                self._draw_buff_effect(screen, x, y, size, effect)
    
    def _draw_heal_effect(self, screen: pygame.Surface, x: int, y: int, size: int, effect: Dict):
        """Рисование эффекта лечения"""
        progress = 1.0 - (effect.get('duration', 0) / effect.get('total_duration', 1))
        heal_color = (0, 255, 0, 150)
        
        # Рисуем восходящие частицы
        particle_count = int(5 * progress)
        for i in range(particle_count):
            particle_y = y - int(20 * progress) - i * 5
            particle_x = x + (i - particle_count // 2) * 3
            pygame.draw.circle(screen, heal_color, (particle_x, particle_y), 2)
    
    def _draw_damage_effect(self, screen: pygame.Surface, x: int, y: int, size: int, effect: Dict):
        """Рисование эффекта урона"""
        progress = 1.0 - (effect.get('duration', 0) / effect.get('total_duration', 1))
        damage_color = (255, 0, 0, 150)
        
        # Рисуем вспышку
        flash_size = int(size * 2 * progress)
        flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(flash_surface, damage_color, (flash_size, flash_size), flash_size)
        screen.blit(flash_surface, (x - flash_size, y - flash_size))
    
    def _draw_buff_effect(self, screen: pygame.Surface, x: int, y: int, size: int, effect: Dict):
        """Рисование эффекта усиления"""
        progress = 1.0 - (effect.get('duration', 0) / effect.get('total_duration', 1))
        buff_color = (255, 255, 0, 100)
        
        # Рисуем вращающиеся кольца
        ring_count = 3
        for i in range(ring_count):
            ring_size = size + 10 + i * 8
            ring_angle = (self.rotation_angle + i * 120) % 360
            ring_alpha = int(100 * progress * (1 - i / ring_count))
            ring_color = (*buff_color[:3], ring_alpha)
            
            ring_surface = pygame.Surface((ring_size * 2, ring_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, ring_color, (ring_size, ring_size), ring_size, 3)
            screen.blit(ring_surface, (x - ring_size, y - ring_size))


class SimpleEntityManager:
    """Менеджер простых сущностей"""
    
    def __init__(self):
        self.entities: Dict[str, SimpleEntity] = {}
        self.entity_templates: Dict[str, EntityVisual] = {}
        self._create_default_templates()
        
        logger.info("Менеджер простых сущностей инициализирован")
    
    def _create_default_templates(self):
        """Создание шаблонов сущностей по умолчанию"""
        self.entity_templates = {
            'player': EntityVisual(
                entity_type=EntityType.PLAYER,
                size=20,
                base_color=(0, 255, 0),
                shape="circle",
                border_width=3,
                border_color=(255, 255, 255),
                glow_radius=5
            ),
            'enemy': EntityVisual(
                entity_type=EntityType.ENEMY,
                size=15,
                base_color=(255, 0, 0),
                shape="square",
                border_width=2,
                border_color=(100, 0, 0)
            ),
            'npc': EntityVisual(
                entity_type=EntityType.NPC,
                size=18,
                base_color=(0, 0, 255),
                shape="diamond",
                border_width=2,
                border_color=(0, 0, 100)
            ),
            'item': EntityVisual(
                entity_type=EntityType.ITEM,
                size=12,
                base_color=(255, 255, 0),
                shape="triangle",
                border_width=1,
                border_color=(128, 128, 0)
            ),
            'obstacle': EntityVisual(
                entity_type=EntityType.OBSTACLE,
                size=25,
                base_color=(128, 128, 128),
                shape="square",
                border_width=1,
                border_color=(64, 64, 64)
            )
        }
    
    def create_entity(self, entity_id: str, entity_type: str, position: Tuple[float, float, float],
                     emotion_system=None, custom_visual: Optional[EntityVisual] = None) -> SimpleEntity:
        """Создание новой сущности"""
        template = self.entity_templates.get(entity_type)
        if not template and not custom_visual:
            logger.warning(f"Неизвестный тип сущности: {entity_type}, используем шаблон по умолчанию")
            template = self.entity_templates['npc']
        
        visual = custom_visual or template
        entity = SimpleEntity(entity_id, visual.entity_type, position, visual, emotion_system)
        
        self.entities[entity_id] = entity
        logger.info(f"Создана сущность: {entity_id} ({entity_type})")
        
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[SimpleEntity]:
        """Получение сущности по ID"""
        return self.entities.get(entity_id)
    
    def remove_entity(self, entity_id: str):
        """Удаление сущности"""
        if entity_id in self.entities:
            del self.entities[entity_id]
            logger.info(f"Удалена сущность: {entity_id}")
    
    def update_all(self, delta_time: float):
        """Обновление всех сущностей"""
        for entity in self.entities.values():
            entity.update(delta_time)
    
    def render_all(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Рендеринг всех сущностей"""
        # Сортируем по Z-координате для правильного порядка отрисовки
        sorted_entities = sorted(
            self.entities.values(),
            key=lambda e: e.position.z
        )
        
        for entity in sorted_entities:
            entity.render(screen, camera_offset)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[SimpleEntity]:
        """Получение всех сущностей определенного типа"""
        return [e for e in self.entities.values() if e.entity_type == entity_type]
    
    def get_entities_in_radius(self, center: Tuple[float, float, float], 
                              radius: float) -> List[SimpleEntity]:
        """Получение сущностей в радиусе"""
        center_vec = pygame.math.Vector3(center)
        nearby_entities = []
        
        for entity in self.entities.values():
            distance = (entity.position - center_vec).length()
            if distance <= radius:
                nearby_entities.append(entity)
        
        return nearby_entities


# Глобальный экземпляр менеджера
entity_manager = SimpleEntityManager()
