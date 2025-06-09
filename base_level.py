#base_level

from typing import Dict, List, Optional, Callable, Any
from ursina import Ursina, camera, time, Entity, destroy
import os

class Level(Entity):
    def __init__(self, game_settings):
        super().__init__()
        self.settings = game_settings
        
        # Инициализация групп спрайтов
        self.visible_sprites: List[Entity] = []
        self.obstacle_sprites: List[Entity] = []
        self.attackable_sprites: List[Entity] = []
        self.enemies: List[Entity] = []
        
        # Инициализация игрока (пока None)
        self.player = None

        # Инициализация UI (будет переопределено в дочернем классе)
        self.ui = None
        self.menus = {}
        
        # Состояние уровня
        self.level_loaded = False
        self.level_name = "unnamed"
        
    def _init_sprite_groups(self):
        """Инициализация групп спрайтов"""
        self.visible_sprites: List[Entity] = []
        self.obstacle_sprites: List[Entity] = []
        self.attackable_sprites: List[Entity] = []
        self.particle_sprites: List[Entity] = []
        
    def _init_entities(self):
        """Инициализация сущностей уровня"""
        self.player: Optional[Entity] = None
        self.enemies: List[Entity] = []
        self.npcs: List[Entity] = []
        self.items: List[Entity] = []
        
    def _init_ui(self):
        """Инициализация интерфейса"""
        self.ui = None  # Должен быть реализован в дочерних классах
        self.menus = {
            'main': None,
            'load': None,
            'inventory': None
        }
        
    def _init_state(self):
        """Инициализация состояния уровня"""
        self.level_loaded = False
        self.level_name = "unnamed"
        self.completed = False
        
    # Основные методы уровня (должны быть переопределены)
    def start_level(self, level_data: Optional[Dict] = None):
        """
        Запуск уровня
        Args:
            level_data: Данные для загрузки уровня (None для нового уровня)
        """
        self.clear_level()
        self._load_map('test')  # Пример, должен быть переопределен
        self.level_loaded = True
        
    def clear_level(self):
        """Безопасная очистка уровня"""
        # Уничтожение игрока
        if hasattr(self, 'player') and self.player:
            self._safe_destroy(self.player)
            self.player = None
        
        # Уничтожение врагов
        for enemy in self.enemies[:]:
            self._safe_destroy(enemy)
            self.enemies.remove(enemy)
        
        # Очистка групп спрайтов
        for group in [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites]:
            for sprite in group[:]:
                self._safe_destroy(sprite)
            group.clear()

    def _safe_destroy(self, entity):
        """Безопасное уничтожение объекта"""
        if not entity:
            return
            
        # Пропускаем строки и другие не-сущности
        if not isinstance(entity, Entity):
            return
            
        # Завершение анимаций (если они есть)
        if hasattr(entity, 'animations'):
            for anim in entity.animations.values():
                if hasattr(anim, 'finish'):
                    anim.finish()
        
        # Уничтожение объекта
        try:
            destroy(entity)
        except Exception as e:
            print(f"[Ошибка] Не удалось уничтожить {entity}: {e}")

    def update(self):
        """Обновление состояния уровня"""
        if not self.level_loaded:
            return
            
        for sprite in self.visible_sprites:
            if hasattr(sprite, 'update'):
                sprite.update()
                
        if self.ui and hasattr(self.ui, 'update'):
            self.ui.update()
            
    # Методы для работы с картой (шаблонные)
    def _load_map(self, map_name: str):
        """
        Загрузка карты (базовый шаблонный метод)
        Args:
            map_name: Имя карты для загрузки
        """
        # Должен быть реализован в дочерних классах
        raise NotImplementedError("Метод _load_map должен быть реализован в дочернем классе")
        
    def _create_entity(self, entity_type: str, pos: tuple, properties: Dict = {}):
        """
        Создание сущности на карте
        Args:
            entity_type: Тип сущности ('player', 'enemy', 'npc', 'item')
            pos: Позиция (x, y)
            properties: Дополнительные свойства сущности
        """
        x, y = pos
        if entity_type == 'player':
            self.player = self._create_player((x, y))
        elif entity_type == 'enemy':
            enemy = self._create_enemy(properties.get('enemy_type', 'default'), (x, y))
            self.enemies.append(enemy)
        elif entity_type == 'npc':
            npc = self._create_npc(properties.get('npc_type', 'default'), (x, y))
            self.npcs.append(npc)
        elif entity_type == 'item':
            item = self._create_item(properties.get('item_type', 'default'), (x, y))
            self.items.append(item)
            
    def _create_player(self, pos: tuple) -> Entity:
        """Создание игрока (должен быть переопределен)"""
        raise NotImplementedError("Метод _create_player должен быть реализован в дочернем классе")
        
    def _create_enemy(self, enemy_type: str, pos: tuple) -> Entity:
        """Создание врага (должен быть переопределен)"""
        raise NotImplementedError("Метод _create_enemy должен быть реализован в дочернем классе")
        
    def _create_npc(self, npc_type: str, pos: tuple) -> Entity:
        """Создание NPC (должен быть переопределен)"""
        raise NotImplementedError("Метод _create_npc должен быть реализован в дочернем классе")
        
    def _create_item(self, item_type: str, pos: tuple) -> Entity:
        """Создание предмета (должен быть переопределен)"""
        raise NotImplementedError("Метод _create_item должен быть реализован в дочернем классе")
        
    # Система событий (может быть расширена)
    def on_player_damaged(self, amount: float, attack_type: str):
        """Обработчик получения урона игроком"""
        if hasattr(self.player, 'take_damage'):
            self.player.take_damage(amount, attack_type)
            
    def on_enemy_death(self, enemy: Entity):
        """Обработчик смерти врага"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            destroy(enemy)
            
    def on_item_pickup(self, item: Entity):
        """Обработчик подбора предмета"""
        if item in self.items:
            self.items.remove(item)
            destroy(item)
            
    # Система сохранения/загрузки
    def save_state(self, slot: int = 1) -> Dict:
        """
        Сохранение состояния уровня
        Returns:
            Словарь с данными для сохранения
        """
        return {
            'player': self.player.to_dict() if hasattr(self.player, 'to_dict') else {},
            'enemies': [e.to_dict() for e in self.enemies if hasattr(e, 'to_dict')],
            'npcs': [n.to_dict() for n in self.npcs if hasattr(n, 'to_dict')],
            'items': [i.to_dict() for i in self.items if hasattr(i, 'to_dict')],
            'level_name': self.level_name,
            'completed': self.completed,
            'timestamp': time.time()
        }
        
    def clear_level(self):
        """Очистка уровня с правильным управлением UI"""
        self._hide_game_ui()
        # ... остальная логика очистки ...
    
    def load_state(self, data: Dict):
        """Загрузка состояния уровня"""
        self.clear_level()
        
        # Здесь должна быть логика загрузки состояния
        # Должна быть реализована в дочерних классах
        raise NotImplementedError("Метод load_state должен быть реализован в дочернем классе")
        
    # UI методы (шаблонные)
    def show_menu(self, menu_name: str):
        """Показать меню"""
        if menu_name in self.menus and self.menus[menu_name]:
            self.menus[menu_name].enable()
            
    def hide_menu(self, menu_name: str):
        """Скрыть меню"""
        if menu_name in self.menus and self.menus[menu_name]:
            self.menus[menu_name].disable()
            
    def toggle_menu(self, menu_name: str):
        """Переключить видимость меню"""
        if menu_name in self.menus and self.menus[menu_name]:
            if self.menus[menu_name].enabled:
                self.hide_menu(menu_name)
            else:
                self.show_menu(menu_name)