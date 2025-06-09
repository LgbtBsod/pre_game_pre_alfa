# entity.py

from ursina import Entity, Vec2
import math

class EntityBase(Entity):
    def wave_value(self):
        value = math.sin(time.time() * 10)
        return 255 if value >= 0 else 0