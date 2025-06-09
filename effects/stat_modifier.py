from enum import Enum, auto

class ModifierType(Enum):
    FLAT = auto()        # +10 / -10
    PERCENT_ADD = auto() # +50% / -30%
    PERCENT_MULT = auto()# *1.5 / *0.7
    FINAL_ADD = auto()   # !+100 (добавляется после всех расчетов)

class StatModifier:
    """Усовершенствованный класс для работы с бафами и дебафами"""
    
    @staticmethod
    def parse(value):
        """
        Парсит значение модификатора с поддержкой отрицательных значений
        Поддерживаемые форматы:
        - +10 / -10 (флет)
        +50% / -30% (аддитивный процент)
        *1.5 / *0.7 (мультипликатор)
        !+100 (финальное добавление)
        """
        if isinstance(value, (int, float)):
            return float(value), ModifierType.FLAT
            
        if not isinstance(value, str):
            return 0.0, ModifierType.FLAT
            
        value = value.strip()
        
        try:
            if value.startswith('!'):
                return float(value[1:]), ModifierType.FINAL_ADD
            elif value.startswith('*'):
                return float(value[1:]), ModifierType.PERCENT_MULT
            elif '%' in value:
                return float(value.replace('%', '')) / 100, ModifierType.PERCENT_ADD
            elif value.startswith(('+', '-')):
                return float(value), ModifierType.FLAT
            return float(value), ModifierType.FLAT
        except (ValueError, TypeError):
            return 0.0, ModifierType.FLAT
    
    @staticmethod
    def apply(base_value, modifier):
        """
        Применяет модификатор с учетом его типа
        Возвращает новое значение с учетом дебафов
        """
        mod_value, mod_type = StatModifier.parse(modifier)
        
        if mod_type == ModifierType.FLAT:
            return base_value + mod_value
        elif mod_type == ModifierType.PERCENT_ADD:
            return base_value * (1 + mod_value)
        elif mod_type == ModifierType.PERCENT_MULT:
            return base_value * mod_value
        elif mod_type == ModifierType.FINAL_ADD:
            return base_value + mod_value
        return base_value
    
    @staticmethod
    def apply_multiple(base_value, modifiers):
        """
        Последовательно применяет несколько модификаторов
        с правильным порядком расчетов:
        1. Процентные аддитивные
        2. Мультипликативные
        3. Флетовые
        4. Финальные добавления
        """
        groups = {t: [] for t in ModifierType}
        
        # Группируем модификаторы по типам
        for mod in modifiers:
            val, typ = StatModifier.parse(mod)
            groups[typ].append(val)
        
        result = base_value
        
        # 1. Аддитивные проценты (складываются между собой)
        if groups[ModifierType.PERCENT_ADD]:
            total_percent = sum(groups[ModifierType.PERCENT_ADD])
            result *= (1 + total_percent)
        
        # 2. Мультипликаторы (перемножаются)
        if groups[ModifierType.PERCENT_MULT]:
            for mult in groups[ModifierType.PERCENT_MULT]:
                result *= mult
        
        # 3. Флетовые модификаторы
        if groups[ModifierType.FLAT]:
            result += sum(groups[ModifierType.FLAT])
        
        # 4. Финальные добавления
        if groups[ModifierType.FINAL_ADD]:
            result += sum(groups[ModifierType.FINAL_ADD])
        
        return result