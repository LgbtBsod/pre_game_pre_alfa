import pygame
from helper.settings import *
from helper.support import *

class Anim_Tile(pygame.sprite.Sprite):
    def __init__(self, position,groups,sprite_type,surface = pygame.Surface((TILESIZE,TILESIZE))):

        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.animation_speed = 0.05
        self.frame_index = 0

        self.import_player_assets()

        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft = (position[0],position[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft = position)
        self.hitbox = self.rect.inflate(0,-10)


    def import_player_assets(self):
        water_path = 'graphics/water/'

        self.animations = {'lake':[]}

        for animation in self.animations.keys():
            full_path = water_path + animation
            self.animations[animation] = import_folder(full_path)



    def animate(self):

        animation = self.animations['lake']
       
        self.frame_index += self.animation_speed
       
        if self.frame_index >= len(animation):
           self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]

        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.animate()
        