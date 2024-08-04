from equip.chance import*
import random
import pygame
from interactive import Use_spite

class Chest(Use_spite):
    def __init__(self,pos,group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/player/down_idle/down.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-10)
        
    def loot_in_chest(amount):
        loot=[]
        while len(loot) < amount:
            for x in range(random.randint(0,5)):
                loot.append('exp')
            for y in range(random.randint(0,10)):
                loot.append('gold')
            if chance('50%'):
                loot.append('common')
            elif chance('20%'):
                loot.append('rare')
            elif chance('10%'):
                loot.append('legendary')
            elif chance('1%'):
                loot.append('eternal')
            
        print(loot)   
    
    def update(self,player):
        self.get_distance(player,self.direction)
        