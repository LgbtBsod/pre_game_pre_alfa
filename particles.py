# particles.py

from ursina import Entity, destroy, time, Animation, Vec2
from os import walk
import random
from helper.support import import_folder


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            'flame': import_folder('graphics/particles/flame/frames'),
            'aura': import_folder('graphics/particles/aura'),
            'heal': import_folder('graphics/particles/heal/frames'),
            'claw': import_folder('graphics/particles/claw'),
            'slash': import_folder('graphics/particles/slash'),
            'sparkle': import_folder('graphics/particles/sparkle'),
            'leaf_attack': import_folder('graphics/particles/leaf_attack'),
            'thunder': import_folder('graphics/particles/thunder'),
            'warrior': import_folder('graphics/particles/warrior'),
            'squid': import_folder('graphics/particles/smoke_orange'),
            'raccoon': import_folder('graphics/particles/raccoon'),
            'spirit': import_folder('graphics/particles/nova'),
            'bamboo': import_folder('graphics/particles/bamboo'),
            'necromancer': import_folder('graphics/particles/necromancer'),
            'leaf': (
                import_folder('graphics/particles/leaf1'),
                import_folder('graphics/particles/leaf2'),
                import_folder('graphics/particles/leaf3'),
                import_folder('graphics/particles/leaf4'),
                import_folder('graphics/particles/leaf5'),
                import_folder('graphics/particles/leaf6')
            )
        }

    def reflect_images(self, frames):
        new_frames = []
        for frame in frames:
            # Ursina не поддерживает flip напрямую, поэтому можно просто добавить копию
            new_frames.append(frame)
        return new_frames

    def create_grass_particles(self, pos, groups=None):
        animation_frames = random.choice(self.frames['leaf'])
        ParticleEffect(pos, animation_frames, groups)

    def create_particles(self, animation_type, pos, groups=None):
        animation_frames = self.frames[animation_type]
        ParticleEffect(pos, animation_frames, groups)


class ParticleEffect(Entity):
    def __init__(self, position, animation_frames, groups=None):
        super().__init__(
            model='quad',
            texture=animation_frames[0],
            position=Vec2(position[0], position[1]),
            z=-0.2,
            scale=1
        )

        self.sprite_type = 'magic'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames

    def animate(self):
        self.frame_index += self.animation_speed * time.dt * 60
        if self.frame_index >= len(self.frames):
            destroy(self)
        else:
            self.texture = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()