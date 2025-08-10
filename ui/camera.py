import math
import random
import pygame


class Camera:
    def __init__(self, x=0, y=0):
        # Получаем настройки камеры
        from config.unified_settings import get_camera_settings

        camera_settings = get_camera_settings()

        self.x = x  # Смещение камеры по X
        self.y = y  # Смещение камеры по Y
        self.target_x = x  # Целевая позиция по X
        self.target_y = y  # Целевая позиция по Y
        self.lerp_speed = (
            camera_settings.LERP_SPEED
        )  # Скорость плавного перемещения камеры
        self.zoom = 1.0  # Масштаб (зум)
        self.shake_amount = 0  # Величина тряски экрана
        self.shake_offset = (0, 0)  # Текущее смещение тряски

    def update(self, target_world_x, target_world_y):
        """Обновляет позицию камеры с плавным переходом к цели"""
        # Плавный переход к целевой точке
        self.target_x = target_world_x
        self.target_y = target_world_y
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed

        # Обновление тряски
        if self.shake_amount > 0:
            self.shake_amount -= 1
            angle = random.uniform(0, 2 * math.pi)
            self.shake_offset = (
                math.cos(angle) * self.shake_amount / 2,
                math.sin(angle) * self.shake_amount / 2,
            )
        else:
            self.shake_offset = (0, 0)

    def apply(self, world_x, world_y):
        """Применяет камеру к мировым координатам и возвращает экранные координаты"""
        screen_x = int(
            world_x
            - self.x
            + self.shake_offset[0]
            + pygame.display.get_surface().get_width() // 2
        )
        screen_y = int(
            world_y
            - self.y
            + self.shake_offset[1]
            + pygame.display.get_surface().get_height() // 3
        )
        return screen_x, screen_y

    def shake(self, amount=10):
        """Запускает тряску экрана"""
        self.shake_amount = amount

    def zoom_in(self, factor=0.95):
        """Увеличивает масштаб (приближает)"""
        from config.unified_settings import get_camera_settings

        camera_settings = get_camera_settings()

        self.zoom *= factor
        self.zoom = max(
            camera_settings.MIN_ZOOM, min(camera_settings.MAX_ZOOM, self.zoom)
        )

    def zoom_out(self, factor=1.05):
        """Уменьшает масштаб (удаляет)"""
        from config.unified_settings import get_camera_settings

        camera_settings = get_camera_settings()

        self.zoom *= factor
        self.zoom = max(
            camera_settings.MIN_ZOOM, min(camera_settings.MAX_ZOOM, self.zoom)
        )

    def reset_zoom(self):
        """Сбрасывает масштаб до стандартного"""
        self.zoom = 1.0

    def get_shake_offset(self):
        """Возвращает текущее смещение от тряски"""
        return self.shake_offset

    def set_lerp_speed(self, speed):
        """Устанавливает скорость плавного движения камеры"""
        self.lerp_speed = speed

    def center_on(self, world_x, world_y):
        """Центрирует камеру на определённой точке"""
        self.target_x = world_x
        self.target_y = world_y

    def move(self, dx, dy):
        """Ручное перемещение камеры"""
        self.target_x += dx
        self.target_y += dy

    def reset(self):
        """Сбрасывает камеру в начальное состояние"""
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.zoom = 1.0
        self.shake_amount = 0
        self.shake_offset = (0, 0)
