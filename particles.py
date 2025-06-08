# particles.py

from ursina import Entity, time, destroy
import os 
import random


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            'flame': self.load_animation('graphics/particles/flame/frames'),
            'aura': self.load_animation('graphics/particles/aura'),
            'heal': self.load_animation('graphics/particles/heal/frames'),

            # Атаки
            'claw': self.load_animation('graphics/particles/claw'),
            'slash': self.load_animation('graphics/particles/slash'),
            'sparkle': self.load_animation('graphics/particles/sparkle'),
            'leaf_attack': self.load_animation('graphics/particles/leaf_attack'),
            'thunder': self.load_animation('graphics/particles/thunder'),

            # Смерть монстров
            'warrior': self.load_animation('graphics/particles/warrior'),
            'squid': self.load_animation('graphics/particles/smoke_orange'),
            'raccoon': self.load_animation('graphics/particles/raccoon'),
            'spirit': self.load_animation('graphics/particles/nova'),
            'bamboo': self.load_animation('graphics/particles/bamboo'),
            'necromancer': self.load_animation('graphics/particles/necromancer'),

            # Листья (для генерации частиц)
            'leaf': [
                *self.load_animation('graphics/particles/leaf1'),
                *self.load_animation('graphics/particles/leaf2'),
                *self.load_animation('graphics/particles/leaf3'),
                *self.load_animation('graphics/particles/leaf4'),
                *self.load_animation('graphics/particles/leaf5'),
                *self.load_animation('graphics/particles/leaf6')
            ]
        }

    def load_animation(self, path):
        """Загружает список путей к текстурам из папки"""
        if not os.path.exists(path):
            return []

        frames = []
        for _, __, img_files in os.walk(path):
            for image in img_files:
                full_path = path + '/' + image
                frames.append(full_path)
        return frames

    def create_grass_particles(self, position, groups=None):
        """Создаёт анимированные листья при уничтожении дерева"""
        particle = ParticleEffect(position, self.frames['leaf'], groups)

    def create_particles(self, animation_type, position, groups=None):
        """Создаёт эффекты вроде огня, звезд и т.д."""
        if animation_type in self.frames:
            ParticleEffect(position, self.frames[animation_type], groups)


class ParticleEffect(Entity):
    def __init__(self, position, animation_frames, groups=None):
        super().__init__(
            model='quad',
            texture=animation_frames[0] if animation_frames else None,
            position=(position[0], position[1], -0.3),
            scale=1,
            collider='box'
        )

        self.sprite_type = 'magic'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.groups = groups or []

        # Если нет кадров — уничтожаем объект
        if not self.frames:
            destroy(self)
            return

    def animate(self):
        if self.frame_index < len(self.frames):
            self.texture = self.frames[int(self.frame_index)]
            self.frame_index += self.animation_speed * 60 * time.dt
            if self.frame_index >= len(self.frames):
                destroy(self)  # Удаляем после окончания анимации
        else:
            destroy(self)

    def update(self):
        self.animate()