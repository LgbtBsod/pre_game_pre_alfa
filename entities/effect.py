import time
from typing import Dict, Any, List

class Effect:
    def __init__(self, effect_id: str, tags: List[str], modifiers: List[Dict[str, Any]]):
        self.id = effect_id
        self.tags = tags
        self.modifiers = modifiers
        self.start_time = time.time()
        self.stacks = 1
        self.active = True
        self.time_since_last_tick = 0.0
        
    def apply(self, entity, is_apply: bool):
        """Применить или отменить эффект"""
        for modifier in self.modifiers:
            attr = modifier['attribute']
            value = modifier['value']
            mode = modifier['mode']
            
            # Рассчет реального значения с учетом стаков
            actual_value = self._calculate_value(entity, attr, value)
            
            # Применение модификатора
            current_value = getattr(entity, attr, 0)
            
            if is_apply:
                if mode == 'add':
                    setattr(entity, attr, current_value + actual_value)
                elif mode == 'multiply':
                    setattr(entity, attr, current_value * actual_value)
                elif mode == 'set':
                    self.original_value = current_value
                    setattr(entity, attr, actual_value)
            else:
                if mode == 'add':
                    setattr(entity, attr, current_value - actual_value)
                elif mode == 'multiply':
                    setattr(entity, attr, current_value / actual_value)
                elif mode == 'set':
                    setattr(entity, attr, self.original_value)
    
    def _calculate_value(self, entity, attr: str, value: Any) -> float:
        """Рассчитать значение эффекта"""
        if isinstance(value, (int, float)):
            return value * self.stacks  # Учет стаков для числовых значений
        
        if isinstance(value, str):
            # Процент от максимального значения
            if value.endswith('%'):
                try:
                    percent = float(value[:-1]) / 100
                except ValueError:
                    return 0.0
                if attr in ['health', 'mana', 'stamina']:
                    base_value = getattr(entity, f"max_{attr}", 0)
                else:
                    base_value = getattr(entity, attr, 0)
                return base_value * percent * self.stacks  # Учет стаков для процентов
            
            # Значение в секунду
            elif '/' in value:
                parts = value.split('/')
                if len(parts) == 2:
                    head = parts[0].strip()
                    # Поддержка вида "1%/1": сначала считаем процент от базового
                    if head.endswith('%'):
                        try:
                            percent = float(head[:-1]) / 100
                        except ValueError:
                            return 0.0
                        if attr in ['health', 'mana', 'stamina']:
                            base_value = getattr(entity, f"max_{attr}", 0)
                        else:
                            base_value = getattr(entity, attr, 0)
                        return base_value * percent * self.stacks
                    # Иначе просто число в секунду
                    try:
                        return float(head) * self.stacks  # Учет стаков для значений в секунду
                    except ValueError:
                        return 0.0
        
        return 0.0
    
    def process_tick(self, entity, delta_time: float):
        """Обработать тик эффекта"""
        self.time_since_last_tick += delta_time
        
        for modifier in self.modifiers:
            if 'interval' in modifier and modifier['interval'] > 0:
                if self.time_since_last_tick >= modifier['interval']:
                    self.time_since_last_tick = 0
                    self.apply_interval_effect(entity, modifier)
    
    def apply_interval_effect(self, entity, modifier):
        """Применить периодический эффект"""
        attr = modifier['attribute']
        value = modifier['value']
        actual_value = self._calculate_value(entity, attr, value)
        
        current_value = getattr(entity, attr, 0)
        
        if isinstance(value, str) and '/' in value:
            # Значение в секунду (уже учтено self.stacks в _calculate_value)
            setattr(entity, attr, current_value + actual_value)
        else:
            setattr(entity, attr, current_value + actual_value)
    
    def is_expired(self) -> bool:
        """Проверить истекло ли время действия эффекта"""
        current_time = time.time()
        for modifier in self.modifiers:
            if 'duration' in modifier:
                elapsed = current_time - self.start_time
                if elapsed >= modifier['duration']:
                    return True
        return False