# save/save_load.py

import os
import json


def save(slot=1, data=None):
    """Сохраняет данные в указанный слот"""
    if not os.path.exists('saves'):
        os.makedirs('saves')

    file_path = f'saves/slot_{slot}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f'[Save] Сохранено в {file_path}')


def load(slot=1):
    """Загружает данные из указанного слота"""
    file_path = f'saves/slot_{slot}.json'
    if not os.path.exists(file_path):
        print(f'[Save] Слот {slot} не найден')
        return None

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f'[Save] Загружено из {file_path}')
        return data
    except Exception as e:
        print(f'[Save] Ошибка загрузки: {e}')
        return None