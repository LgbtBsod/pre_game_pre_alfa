class BaseMenu(Entity):
    def __init__(self, game):
        super().__init__(parent=camera.ui, enabled=False)
        self.game = game

    def enable(self):
        super().enable()
        # При показе меню скрываем игровой UI
        if hasattr(self.game, 'ui'):
            self.game.ui.disable()

    def disable(self):
        super().disable()