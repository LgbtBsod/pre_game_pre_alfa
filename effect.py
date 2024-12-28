import pygame
from time import time
from helper.support import*
from helper.settings import *

class Effect:
    def __init__(self,duration, cooldown,effect,get_buff):
        super().__init__()
        self.duration = duration * FPS
        self.cooldown = cooldown * FPS
        self.active = False
        self.unavailable = False
        self.effect = effect
        self.buff = {}
        self.dur = None
        self.cd = None
        self.get_buff = get_buff
        
    def pull_my_devil_trigger(self):
        self.active = True
        self.dur = pygame.time.get_ticks()
        for effect in self.effect.keys():
            self.buff[effect] = convert_to_num(self.effect[effect])   
        print(self.buff)
            
    
    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.dur == self.duration:
            self.active = False
            self.unavailable = True
        if current_time - self.cooldown == self.cd:
            self.unavailable = False
                 
    def duration(self):
        while self.active:
            #self.get_buff(self.buff)
            print(self.buff)
        if self.unavailable:
            for x in self.buff:
                self.buff[x] = 0
            #self.get_buff(self.buff)
            print(self.buff)
        
    def update(self):
        self.cooldown()
        self.duration()




def brave(now=0,max=0):
    if now < (max/3):
        return True
    else:
        return False
        
