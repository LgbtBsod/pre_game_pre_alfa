"""Кнопки пользовательского интерфейса."""

import logging
import tkinter as tk
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class Button:
    def __init__(self, parent, x, y, width, height, text, action=None):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.hovered = False
        self.pressed = False
        
        # Создаем tkinter кнопку
        self.tk_button = tk.Button(
            parent,
            text=text,
            command=self._on_click,
            relief="flat",
            bd=0,
            font=("Arial", 12),
            bg="#4a5a6a",
            fg="white",
            activebackground="#5a6a7a",
            activeforeground="white"
        )
        
        # Размещаем кнопку
        self.tk_button.place(x=x, y=y, width=width, height=height)
        
        # Привязываем события мыши
        self.tk_button.bind("<Enter>", self._on_enter)
        self.tk_button.bind("<Leave>", self._on_leave)
        self.tk_button.bind("<Button-1>", self._on_press)
        self.tk_button.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_enter(self, event):
        """Событие наведения мыши"""
        self.hovered = True
        self.tk_button.configure(bg="#5a6a7a")
    
    def _on_leave(self, event):
        """Событие ухода мыши"""
        self.hovered = False
        self.tk_button.configure(bg="#4a5a6a")
    
    def _on_press(self, event):
        """Событие нажатия"""
        self.pressed = True
        self.tk_button.configure(bg="#3a4a5a")
    
    def _on_release(self, event):
        """Событие отпускания"""
        self.pressed = False
        if self.hovered:
            self.tk_button.configure(bg="#5a6a7a")
        else:
            self.tk_button.configure(bg="#4a5a6a")
    
    def _on_click(self):
        """Обработка клика"""
        if self.action:
            logger.debug(f"Button '{self.text}' pressed")
            return self.action()
        return None
    
    def update(self, mouse_pos, mouse_pressed):
        """Обновляет состояние кнопки (для совместимости)"""
        # В tkinter состояние обновляется автоматически через события
        pass

    def draw(self, surface):
        """Отрисовывает кнопку (для совместимости)"""
        # В tkinter отрисовка происходит автоматически
        pass

    def handle_event(self, event):
        """Обрабатывает событие (для совместимости)"""
        # В tkinter события обрабатываются автоматически
        return None

    def check_hover(self, pos):
        """Проверяет наведение курсора (для совместимости)"""
        # В tkinter наведение обрабатывается автоматически
        pass
    
    def destroy(self):
        """Уничтожает кнопку"""
        if self.tk_button:
            self.tk_button.destroy()
    
    def hide(self):
        """Скрывает кнопку"""
        self.tk_button.place_forget()
    
    def show(self):
        """Показывает кнопку"""
        self.tk_button.place(x=self.x, y=self.y, width=self.width, height=self.height)
    
    def set_text(self, text):
        """Устанавливает текст кнопки"""
        self.text = text
        self.tk_button.configure(text=text)
    
    def set_enabled(self, enabled):
        """Включает/выключает кнопку"""
        if enabled:
            self.tk_button.configure(state="normal")
        else:
            self.tk_button.configure(state="disabled")
