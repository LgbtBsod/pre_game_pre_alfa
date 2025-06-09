from ursina import *
from helper.settings import GAME_SETTINGS

class GameUI(Entity):
    def __init__(self, level):
        super().__init__(
            parent=camera.ui,
            ignore_paused=True
        )
        self.level = level
        self._init_elements()
        
        self._init_health_bar()
        self._init_exp_bar()
        self._init_stamina_bar()
        self._init_weapon_display()
        self._init_magic_display()
        self._init_debug_info()
        self._init_stamina_effects()

    def _init_elements(self):
        # Полоска здоровья
        self.health_bar = HealthBar(parent=self)
        
        # Полоска маны
        self.mana_bar = ManaBar(parent=self)
        
        # Иконка оружия
        self.weapon_icon = WeaponIcon(parent=self)
        
        # Сначала скрываем все элементы
        self.disable()

    def enable(self):
        """Показывает игровой UI"""
        super().enable()
        for child in self.children:
            child.enable()

    def disable(self):
        """Скрывает игровой UI"""
        super().disable()
        for child in self.children:
            child.disable()

    def _init_health_bar(self):
        """Инициализация полоски здоровья"""
        self.health_bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            position=(-0.7, 0.45),
            scale=(0.4, 0.03),
            texture='white_cube'
        )
        
        self.health_bar = Entity(
            parent=self.health_bg,
            model='quad',
            color=color.red,
            position=(0, 0, -0.1),
            scale=(1, 1, 1),
            texture='white_cube'
        )
        
        self.health_text = Text(
            text='HP: 100/100',
            parent=self.health_bg,
            position=(0, -0.2),
            origin=(0, 0),
            scale=1.5
        )

    def _init_exp_bar(self):
        """Инициализация полоски опыта"""
        self.exp_bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            position=(-0.7, 0.4),
            scale=(0.4, 0.02),
            texture='white_cube'
        )
        
        self.exp_bar = Entity(
            parent=self.exp_bg,
            model='quad',
            color=color.yellow,
            position=(0, 0, -0.1),
            scale=(0, 1, 1),
            texture='white_cube'
        )
        
        self.exp_text = Text(
            text='Lvl: 1 | Exp: 0/1000',
            parent=self.exp_bg,
            position=(0, -0.5),
            origin=(0, 0),
            scale=1.2
        )

    def _init_weapon_display(self):
        """Отображение текущего оружия"""
        self.weapon_bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            position=(0.7, -0.45),
            scale=(0.15, 0.1),
            texture='white_cube'
        )
        
        self.weapon_icon = Entity(
            parent=self.weapon_bg,
            model='quad',
            texture='assets/graphics/weapons/sword/full.png',
            scale=(0.8, 0.8)
        )
        
        self.weapon_text = Text(
            text='Weapon: None',
            parent=self.weapon_bg,
            position=(0, -1.2),
            origin=(0, 0),
            scale=1.5
        )

    def _init_magic_display(self):
        """Отображение текущей магии"""
        self.magic_bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            position=(0.85, -0.45),
            scale=(0.15, 0.1),
            texture='white_cube'
        )
        
        self.magic_icon = Entity(
            parent=self.magic_bg,
            model='quad',
            texture='assets/graphics/flame.png',
            scale=(0.8, 0.8)
        )
        
        self.magic_text = Text(
            text='Magic: None',
            parent=self.magic_bg,
            position=(0, -1.2),
            origin=(0, 0),
            scale=1.5
        )

    def _init_debug_info(self):
        """Отладочная информация"""
        self.debug_text = Text(
            text='',
            position=(-0.85, 0.45),
            scale=1,
            color=color.white
        )
        
    def _init_stamina_bar(self):
        """Инициализация полоски стамины"""
        self.stamina_bg = Entity(
            parent=self,
            model='quad',
            color=color.dark_gray,
            position=(-0.7, 0.35),  # Под полоской здоровья
            scale=(0.4, 0.03),
            texture='white_cube'
        )
        
        self.stamina_bar = Entity(
            parent=self.stamina_bg,
            model='quad',
            color=color.cyan,  # Голубой цвет для стамины
            position=(0, 0, -0.1),
            scale=(1, 1, 1),
            texture='white_cube'
        )
        
        self.stamina_text = Text(
            text='STM: 100/100',
            parent=self.stamina_bg,
            position=(0, -0.2),
            origin=(0, 0),
            scale=1.5
        )

    def _init_stamina_effects(self):
        """Визуальные эффекты при низкой стамине"""
        self.low_stamina_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(100, 100, 255, 50),
            scale=(2, 2),
            alpha=0,
            always_on_top=True
        )

    def update(self):
        """Обновление UI каждый кадр"""
        if not self.level.player:
            return
            
        # Обновление здоровья
        player = self.level.player
        health_percent = player.current_stats['health'] / player.current_stats['max_health']
        self.health_bar.scale_x = health_percent
        self.health_text.text = f"HP: {int(player.current_stats['health'])}/{player.current_stats['max_health']}"
        
        # Обновление стамины (новый код)
        stamina_percent = player.current_stats['stamina'] / player.base_stats['stamina']
        self.stamina_bar.scale_x = stamina_percent
        self.stamina_text.text = f"STM: {int(player.current_stats['stamina'])}/{player.base_stats['stamina']}"
        
        # Эффект при низкой стамине
        if stamina_percent < 0.2:
            self.low_stamina_overlay.alpha = (0.2 - stamina_percent) * 2.5  # Плавное появление
        else:
            self.low_stamina_overlay.alpha = 0
            
        # Изменение цвета при истощении стамины
        if stamina_percent < 0.1:
            self.stamina_bar.color = color.red
        else:
            self.stamina_bar.color = color.cyan
            
        # Обновление опыта
        exp_percent = player.exp / player.exp_to_level
        self.exp_bar.scale_x = exp_percent
        self.exp_text.text = f"Lvl: {player.level} | Exp: {player.exp}/{player.exp_to_level}"
        
        # Обновление оружия
        if hasattr(player, 'weapon'):
            self.weapon_text.text = f"Weapon: {player.weapon}"
            weapon_icon_path = f'assets/graphics/weapons/{player.weapon}/icon.png'
            if os.path.exists(weapon_icon_path):
                self.weapon_icon.texture = weapon_icon_path
        
        # Обновление магии
        if hasattr(player, 'magic'):
            self.magic_text.text = f"Magic: {player.magic}"
            magic_icon_path = f'assets/graphics/magic/{player.magic}/icon.png'
            if os.path.exists(magic_icon_path):
                self.magic_icon.texture = magic_icon_path
        
        # Отладочная информация
        self.debug_text.text = (
            f"Pos: {int(player.position.x)}, {int(player.position.y)}\n"
            f"FPS: {int(1/time.dt)}"
        )

    def toggle_visibility(self, visible):
        """Переключение видимости UI"""
        for child in self.children:
            child.enabled = visible
        self.enabled = visible