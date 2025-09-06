#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode, Vec4, Vec3
from panda3d.core import CardMaker, TransparencyAttrib

class SettingsScreen:
    """Экран настроек"""
    
    def __init__(self, game):
        self.game = game
        self.elements = []
        self.settings = {
            'fullscreen': False,
            'volume': 0.7,
            'vsync': True
        }
        
    def enter(self):
        """Вход в состояние настроек"""
        self.create_background()
        self.create_title()
        self.create_settings()
        self.create_buttons()
        
    def exit(self):
        """Выход из состояния настроек"""
        for element in self.elements:
            if hasattr(element, 'destroy'):
                element.destroy()
            else:
                element.removeNode()
        self.elements.clear()
        
    def create_background(self):
        """Создание фона"""
        cm = CardMaker("settings_background")
        cm.setFrame(-2, 2, -1.5, 1.5)
        background = self.game.aspect2d.attachNewNode(cm.generate())
        background.setColor(0.1, 0.1, 0.2, 1.0)
        background.setTransparency(TransparencyAttrib.MAlpha)
        self.elements.append(background)
        
    def create_title(self):
        """Создание заголовка"""
        title = OnscreenText(
            text="Settings",
            pos=(0, 0.4),
            scale=0.12,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            shadowOffset=(0.05, 0.05),
            align=TextNode.ACenter,
            parent=self.game.aspect2d
        )
        self.elements.append(title)
        
    def create_settings(self):
        """Создание элементов настроек"""
        # Полноэкранный режим
        fullscreen_label = OnscreenText(
            text="Fullscreen:",
            pos=(-0.3, 0.2),
            scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.game.aspect2d
        )
        self.elements.append(fullscreen_label)
        
        self.fullscreen_btn = DirectButton(
            text="OFF" if not self.settings['fullscreen'] else "ON",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.8, 0.2, 1) if self.settings['fullscreen'] else (0.8, 0.2, 0.2, 1),
            frameSize=(-0.1, 0.1, -0.03, 0.03),
            pos=(0.2, 0, 0.2),
            command=self.toggle_fullscreen,
            parent=self.game.aspect2d
        )
        self.elements.append(self.fullscreen_btn)
        
        # Громкость
        volume_label = OnscreenText(
            text="Volume:",
            pos=(-0.3, 0.1),
            scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.game.aspect2d
        )
        self.elements.append(volume_label)
        
        # Кнопки громкости
        volume_down_btn = DirectButton(
            text="-",
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.05, 0.05, -0.03, 0.03),
            pos=(0.1, 0, 0.1),
            command=self.volume_down,
            parent=self.game.aspect2d
        )
        self.elements.append(volume_down_btn)
        
        volume_up_btn = DirectButton(
            text="+",
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-0.05, 0.05, -0.03, 0.03),
            pos=(0.2, 0, 0.1),
            command=self.volume_up,
            parent=self.game.aspect2d
        )
        self.elements.append(volume_up_btn)
        
        # Отображение текущей громкости
        self.volume_text = OnscreenText(
            text=f"{int(self.settings['volume'] * 100)}%",
            pos=(0.3, 0.1),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.game.aspect2d
        )
        self.elements.append(self.volume_text)
        
        # VSync
        vsync_label = OnscreenText(
            text="VSync:",
            pos=(-0.3, 0.0),
            scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.game.aspect2d
        )
        self.elements.append(vsync_label)
        
        self.vsync_btn = DirectButton(
            text="OFF" if not self.settings['vsync'] else "ON",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.8, 0.2, 1) if self.settings['vsync'] else (0.8, 0.2, 0.2, 1),
            frameSize=(-0.1, 0.1, -0.03, 0.03),
            pos=(0.2, 0, 0.0),
            command=self.toggle_vsync,
            parent=self.game.aspect2d
        )
        self.elements.append(self.vsync_btn)
        
    def create_buttons(self):
        """Создание кнопок"""
        # Кнопка "Apply"
        apply_btn = DirectButton(
            text="Apply",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.8, 0.2, 1),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            pos=(-0.2, 0, -0.2),
            command=self.apply_settings,
            parent=self.game.aspect2d
        )
        self.elements.append(apply_btn)
        
        # Кнопка "Back"
        back_btn = DirectButton(
            text="Back",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.8, 0.2, 0.2, 1),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            pos=(0.2, 0, -0.2),
            command=self.go_back,
            parent=self.game.aspect2d
        )
        self.elements.append(back_btn)
        
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.fullscreen_btn.setText("OFF" if not self.settings['fullscreen'] else "ON")
        self.fullscreen_btn['frameColor'] = (0.2, 0.8, 0.2, 1) if self.settings['fullscreen'] else (0.8, 0.2, 0.2, 1)
        
    def volume_up(self):
        """Увеличить громкость"""
        self.settings['volume'] = min(1.0, self.settings['volume'] + 0.1)
        self.volume_text.setText(f"{int(self.settings['volume'] * 100)}%")
        
    def volume_down(self):
        """Уменьшить громкость"""
        self.settings['volume'] = max(0.0, self.settings['volume'] - 0.1)
        self.volume_text.setText(f"{int(self.settings['volume'] * 100)}%")
        
    def toggle_vsync(self):
        """Переключение VSync"""
        self.settings['vsync'] = not self.settings['vsync']
        self.vsync_btn.setText("OFF" if not self.settings['vsync'] else "ON")
        self.vsync_btn['frameColor'] = (0.2, 0.8, 0.2, 1) if self.settings['vsync'] else (0.8, 0.2, 0.2, 1)
        
    def apply_settings(self):
        """Применить настройки"""
        # Здесь можно применить настройки к игре
        print(f"Настройки применены: {self.settings}")
        self.go_back()
        
    def go_back(self):
        """Вернуться назад"""
        if self.game.state_manager.get_previous_state():
            self.game.state_manager.change_state(self.game.state_manager.get_previous_state())
        else:
            self.game.state_manager.change_state("start")
