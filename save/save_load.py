
import json
import os


def save(slot=1, data=None):
    file_path = f'saves/slot_{slot}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def load(slot=1):
    file_path = f'saves/slot_{slot}.json'
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r') as f:
        return json.load(f)