import json


def save(pos,item,exp):


    data = {}
    data['save'] = []
    data['save'].append({
        'pos': pos,
        'item': item,
        'exp': exp

    })
    with open('save/1.json', 'w') as outfile:
        json.dump(data, outfile)
        
        
def load():
    data = {}
    with open('save/1.json') as json_file:
        data = json.load(json_file)
    for p in data['save']:
        pos = p['pos']
        item = p['item']
        exp = p['exp']
    return pos, item, exp

