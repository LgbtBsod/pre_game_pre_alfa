from equip.chance import *
from player import *
from equip.item_base import *
from helper.support import *


equip = []

equip.append(list(artifacts.keys())[0])
equip.append(list(artifacts.keys())[1])
equip.append(list(artifacts.keys())[2])
equip.append(list(artifacts.keys())[3])


def get_base(player): 
    base_stat = {}
    for i in player.keys():
        base_stat[i] = player[i]
    return base_stat
    

def return_stats(stat_dict,stats):
    must_be_plused = {}
    
    for first in stat_dict.keys():
        one = stats[first]
        two = stat_dict[first]
        three = one*two
        must_be_plused[first] = three
    
    return must_be_plused
    
def get_equip_stat():
    stat_dict = {}
    for item in equip:
        one_step = list(artifacts[item].values())[0]
        for x in list(one_step.keys()):
            if x in stat_dict:
                any = stat_dict[x]
                stat_dict[x] = convert_to_num(one_step[x])+ any
            else:
                stat_dict[x] = convert_to_num(one_step[x])
    return stat_dict       


def current_stats(must_be_plused,stats):
    current_stats = {}
    current_stats = stats
    for item in must_be_plused.keys():
        one = stats[item]
        two = must_be_plused[item]
        three = one + two
        current_stats[item] = three 
    #print(current_stats)
    return current_stats
    