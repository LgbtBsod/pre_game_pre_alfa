from ursina import Ursina, camera, window, Vec2
from ursina.prefabs.hot_reloader import HotReloader
from level import Level
from UI.save_menu import SaveMenu

app = Ursina()

# Настройки окна
HotReloader().enabled = False
camera.orthographic = True
camera.fov = 10
window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = 'Zelda Like RPG'
window.borderless = False
window.fullscreen = False

game = Level()
save_menu = SaveMenu(game)


# Инициализация геймпада
gamepad = None

if hasattr(app, 'gamepads') and len(app.gamepads) > 0:
    gamepad = app.gamepads[0]
    print(f"Connected gamepad: {gamepad}")


def input(key):
    print(key)
    # Обработка клавиатуры
    if key == 'escape':
        save_menu.toggle()
    if key == 'f5':
        game.save_game(slot=1)
    if key == 'f9':
        game.load_game(slot=1)
    
    if gamepad:
        if key == 'gamepad start':
            save_menu.toggle()
        if key == 'gamepad back':
            game.save_game(slot=1)
        if key == 'gamepad a':
            print("Button A pressed")
        if key == 'gamepad b':
            print("Button B pressed")




def update():
    if gamepad:
        # Обработка аналоговых стиков
        left_x = gamepad.left_x
        left_y = gamepad.left_y
        
        # Мертвая зона
        deadzone = 0.2
        if abs(left_x) > deadzone or abs(left_y) > deadzone:
            movement = Vec2(left_x, -left_y)
            # game.player.move(movement)  # Раскомментируйте для использования
            
        # Обработка триггеров
        right_trigger = gamepad.right_trigger
        if right_trigger > 0.5:
            print("Right trigger pressed")

app.run()
