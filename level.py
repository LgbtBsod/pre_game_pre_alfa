from player.player import LikePlayer
from enemy.enemy import Enemy
from tile import Tile
from anim_tile import AnimTile
from helper.support import import_csv_layout
import os
from base_level import Level
from UI.main_menu import MainMenu
from UI.load_menu import LoadMenu
from UI.save_menu import SaveMenu
from UI.GameUI import GameUI
from UI.InventoryUI import InventoryUI
from equip.items_data import ItemsData
from save.save_load import save


class GameLevel(Level):
    def __init__(self, game_settings):
        super().__init__(game_settings)
        # Инициализация систем
        self.items_data = ItemsData()
        self._init_callbacks()
        self.visible_sprites = []
        self.obstacle_sprites = []
        self.attackable_sprites = []

        # Группы сущностей
        self.enemies = []  # ← добавлено
        self.npcs = []
        self.items = []

        # Инициализация игрока
        self.player = None
        self.particle_sprites = []
        self._init_ui_elements()
        self._hide_game_ui()  # Скрываем UI при инициализации
        
    def _init_ui_elements(self):
        """Инициализация UI элементов (но не показываем их)"""
        self.ui = GameUI(self)
        self.ui.disable()  # Сначала скрываем
        
        self.main_menu = MainMenu(self)
        self.load_menu = LoadMenu(self)
        self.save_menu = SaveMenu(self)
        
        self.menus = {
            'main': self.main_menu,
            'load': self.load_menu,
            'inventory': None  # Будет инициализирован при создании игрока
        }

    def _hide_game_ui(self):
        """Скрывает все игровые UI элементы"""
        if hasattr(self, 'ui'):
            self.ui.disable()
        for menu in self.menus.values():
            if menu:
                menu.disable()
        
    def _init_callbacks(self):
        """Инициализация callback-функций"""
        self.drops = self._handle_item_pickup
        self.on_player_damaged = self._handle_player_damage
        self.on_enemy_death = self._handle_enemy_death

    def _init_ui(self): 
        """Инициализация интерфейса (вызывается после создания игрока)"""
        if not hasattr(self, 'player') or self.player is None:
            return
            
        self.ui = GameUI(self)
        self.load_menu = LoadMenu(self)
        self.main_menu = MainMenu(self)
        
        # Инициализация инвентаря только если игрок существует
        self.menus = {
            'main': self.main_menu,
            'load': self.load_menu,
            'inventory': InventoryUI(self.player, self.player.equipment)
        }
        
    def start_level(self, map_name='test'):
        """Запуск уровня с показом игрового UI"""
        self.clear_level()
        self._load_map(map_name)
        
        # Инициализация инвентаря только после создания игрока
        if hasattr(self, 'player'):
            self.menus['inventory'] = InventoryUI(self.player, self.player.equipment)
            self.menus['inventory'].disable()
        
        # Показываем игровой UI
        if hasattr(self, 'ui'):
            self.ui.enable()
        
        self.level_loaded = True


    def _load_map(self, map_name='test'):
        """Загрузка карты из CSV"""
        from helper.support import import_csv_layout
        
        map_dir = f'assets/map/{map_name}'
        layouts = {
            'boundary': import_csv_layout(f'{map_dir}_block.csv'),
            'tree': import_csv_layout(f'{map_dir}_tree.csv'),
            'entities': import_csv_layout(f'{map_dir}_entities.csv')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    self._process_map_cell(style, col, row_index, col_index)

    def _process_map_cell(self, style, col, row, col_index):
        """Обрабатывает одну ячейку карты"""
        if col == '-1':
            return

        x = col_index * self.settings['TILESIZE']
        y = -row * self.settings['TILESIZE']

        if style == 'boundary':
            Tile((x, y), [self.obstacle_sprites], 'invisible')
        elif style == 'tree':
            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'tree')
        elif style == 'entities':
            self._spawn_entity(col, (x, y))

    def _spawn_entity(self, entity_id, pos):
        """Создает сущность на карте"""
        entity_map = {
            '164': ('player', {}),
            '160': ('enemy', {'enemy_type': 'warrior'}),
            '131': ('enemy', {'enemy_type': 'necromancer'})
        }
        
        if entity_id in entity_map:
            entity_type, properties = entity_map[entity_id]
            self._create_entity(entity_type, pos, properties)

    def _create_player(self, pos):
        """Создание игрока с инициализацией инвентаря"""
        player = LikePlayer(
            position=pos,
            groups=[self.visible_sprites],
            obstacle_sprites=self.obstacle_sprites
        )
        
        # Стартовые предметы
        player.inventory.extend(['Health Potion', 'Mana Potion'])
        return player

    def _create_enemy(self, enemy_type, pos):
            return Enemy(
                name=enemy_type,  # Исправленный параметр
                position=pos,
                groups=[self.visible_sprites, self.attackable_sprites],
                obstacle_sprites=self.obstacle_sprites,
                damage_player=self.on_player_damaged,
                death_callback=self.on_enemy_death,
                add_exp=self.add_exp,
                drops=self.drops
            )
            
    def _handle_item_pickup(self, item_name):
        """Обработчик получения предмета"""
        print(f"[Game] Получен предмет: {item_name}")
        if self.items_data.item_exists(item_name):
            self.player.add_item(item_name)
            self.menus['inventory'].update_inventory()

    def _handle_player_damage(self, amount, attack_type):
        """Обработчик урона игроку"""
        if self.player and hasattr(self.player, 'take_damage'):
            self.player.take_damage(amount, attack_type)

    def _handle_enemy_death(self, enemy):
        """Обработчик смерти врага"""
        if enemy in self.attackable_sprites:
            self.attackable_sprites.remove(enemy)
            destroy(enemy)

    def add_exp(self, amount):
        """Добавление опыта игроку"""
        if self.player:
            self.player.gain_exp(amount)
            self.ui.update()

    def save_state(self):
        """Подготовка данных для сохранения"""
        return {
            'player': self.player.to_dict(),
            'enemies': [e.to_dict() for e in self.attackable_sprites if hasattr(e, 'to_dict')],
            'level_name': self.level_name,
            'inventory': self.player.inventory,
            'equipment': self.player.equipment.equipped_items
        }

    def load_state(self, data):
        """Загрузка состояния игры"""
        self.clear_level()
        
        # Загрузка игрока
        if 'player' in data:
            self.player = LikePlayer.from_dict(data['player'])
            self.player.obstacle_sprites = self.obstacle_sprites
            self.visible_sprites.append(self.player)
            
            # Восстановление инвентаря
            self.player.inventory = data.get('inventory', [])
            for item in data.get('equipment', []):
                self.player.equipment.equip_item(item)

        # Загрузка врагов
        for enemy_data in data.get('enemies', []):
            enemy = Enemy.from_dict(enemy_data)
            enemy.setup_callbacks(
                damage_player=self.on_player_damaged,
                death_callback=self.on_enemy_death,
                add_exp=self.add_exp,
                drops=self.drops
            )
            self.enemies.append(enemy)
            self.visible_sprites.append(enemy)
            self.attackable_sprites.append(enemy)

        self.level_loaded = True

    def save_game(self, slot=1):
        """Сохранение игры в указанный слот"""
        data = self.save_state()
        save(slot=slot, data=data)
        print(f'[Game] Игра сохранена в слот {slot}')

    def show_load_menu(self):
        """Отображение меню загрузки"""
        self.show_menu('load')
        
    def load_player_data(self, player_data):
        """Создает игрока из данных"""
        from player.player import LikePlayer
        self.player = LikePlayer.from_dict(player_data)
        self.visible_sprites.append(self.player)

    def load_enemies_data(self, enemies_data):
        """Создает врагов из данных"""
        from enemy.enemy import Enemy
        for enemy_data in enemies_data:
            enemy = Enemy.from_dict(enemy_data)
            self.visible_sprites.append(enemy)
            self.attackable_sprites.append(enemy)
    
    def show_menu(self, menu_name):
        """Показывает указанное меню и скрывает остальные"""
        # Скрываем все меню
        for name, menu in self.menus.items():
            if menu:
                menu.disable()
        
        # Скрываем игровой UI при открытии меню
        if hasattr(self, 'ui'):
            self.ui.disable()
        
        # Показываем нужное меню
        if menu_name in self.menus and self.menus[menu_name]:
            self.menus[menu_name].enable()