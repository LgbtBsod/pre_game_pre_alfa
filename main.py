# main.py

from ursina import Ursina, window, color, Vec2, Vec3, time, camera
from level import Level

# Запуск игры
app = Ursina()

# Настройки окна
window.title = 'Zelda'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Инициализация уровня
game = Level()

# ФПС лимит
app.set_frame_rate(120)

# Запуск главного цикла
app.run()