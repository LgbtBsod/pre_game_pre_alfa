#!/usr/bin/env python3
"""
Простой тест Panda3D для проверки базовой функциональности
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties, Vec3, TextNode
from direct.gui.DirectGui import DirectButton, DirectLabel

class SimpleTest(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        props = WindowProperties()
        props.setTitle("Простой тест Panda3D")
        props.setSize(800, 600)
        self.win.requestProperties(props)
        
        # Простой текст
        self.text = DirectLabel(
            text="Тест Panda3D работает!",
            pos=(0, 0, 0),
            scale=0.07,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter
        )
        
        # Простая кнопка
        self.button = DirectButton(
            text="Тест кнопки",
            pos=(0, 0, -0.3),
            scale=0.05,
            command=self.test_button,
            frameColor=(0.2, 0.6, 0.2, 1)
        )
        
        # Запуск простого цикла
        self.taskMgr.add(self.update, "update")
    
    def test_button(self):
        print("Кнопка работает!")
        self.text['text'] = "Кнопка нажата!"
    
    def update(self, task):
        return Task.cont

def main():
    app = SimpleTest()
    app.run()

if __name__ == "__main__":
    main()
