from helper.support import *
from equip.item_base import *


class Equipment:
    def __init__(self,current_stats):
        super().__init__()
        self.equip = []
        self.name_item = 0
        self.current_stats = current_stats
        self.equip_stat = {}
        self.item = list(artifacts.keys())[self.name_item]
        self.equip_stat = {'health':0,'attack':0,'magic':0,
        'agility':0,'hp_regen':0,'speed':0,'stamina':0,'energy':0,'strength':0}
        
    def add_to_bag(self,item):
        if item in self.equip:
            pass
        else:   
            self.equip.append(item)
            self.get_equip_stat()
            print(self.equip)
            
    def get_equip_stat(self):   
        for item in self.equip:
            one_step = list(artifacts[item].values())[0]
            for x in list(one_step.keys()):
                if x == 'crit_rate' or x == 'crit_chance':
                    if x in self.equip_stat:
                        any = self.equip_stat[x]
                        self.equip_stat[x] = (one_step[x])
                    else:
                        self.equip_stat[x] = (one_step[x])
                else:    
                    if x in self.equip_stat:
                        any = self.equip_stat[x]
                        self.equip_stat[x] = (one_step[x])+ any
                    else:
                        self.equip_stat[x] = (one_step[x])
            
            print(self.equip_stat)
        self.current_stats(self.equip_stat)
        self.equip_stat.clear()
 
    def update(self):
        self.get_equip_stat()