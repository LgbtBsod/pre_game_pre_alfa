import json


stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}

def save(pos,item,exp):


    data = {}
    data['save'] = []
    data['save'].append({
        'pos': pos,
        'item': item,
        'exp': exp

    })
    with open('helper/default.json', 'w') as outfile:
        json.dump(data, outfile)
        
        
def load():
    data = {}
    with open('helper/default.json') as json_file:
        data = json.load(json_file)
    for p in data['save']:
        pos = p['pos']
        item = p['item']
        exp = p['exp']
    return pos, item, exp

