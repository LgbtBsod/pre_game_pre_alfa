#!/usr / bin / env python3
"""
    Система управления состоянием - централизованное управление игровым состоянием
    Улучшенная версия с поддержкой групп, валидации и производительности
"""

imp or t logg in g
imp or t time
from typ in g imp or t Dict, L is t, Optional, Any, Type, TypeVar, Generic, Callable
    Union
from dataclasses imp or t dataclass, field:
    pass  # Добавлен pass в пустой блок
from enum imp or t Enum
imp or t thread in g
imp or t copy
from abc imp or t abstractmethod
imp or t weakref

from .architecture imp or t BaseComponent, ComponentType, Pri or ity, Event
    create_event

logger== logg in g.getLogger(__name__)

# ============================================================================
# ТИПЫ СОСТОЯНИЙ
# ============================================================================

class StateType(Enum):
    """Типы состояний"""
        GLOBAL== "global"
        ENTITY== "entity"
        SYSTEM== "system"
        UI== "ui"
        TEMPORARY== "temp or ary"
        CONFIGURATION== "configuration"
        STATISTICS== "stat is tics"
        DATA== "data"

        class StateScope(Enum):
    """Области видимости состояний"""
    PRIVATE== "private"
    PROTECTED== "protected"
    PUBLIC== "public"

class StateValidation(Enum):
    """Типы валидации состояний"""
        NONE== "none"
        TYPE== "type"
        RANGE== "range"
        ENUM== "enum"
        CUSTOM== "custom"

        # ============================================================================
        # БАЗОВЫЕ КЛАССЫ СОСТОЯНИЙ
        # ============================================================================

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class StateChange:
    """Изменение состояния с улучшенной структурой"""
    state_id: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str
    metadata: Dict[str, Any]== field(default_factor == dict):
        pass  # Добавлен pass в пустой блок
    change_type: str== "update"  # update, reset, rest or e, clear

@dataclass:
    pass  # Добавлен pass в пустой блок
class StateSnapshot:
    """Снимок состояния с версионированием"""
        state_id: str
        value: Any
        timestamp: float
        version: int
        metadata: Dict[str, Any]== field(default_factor == dict):
        pass  # Добавлен pass в пустой блок
        checksum: Optional[str]== None

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class StateValidationRule:
    """Правило валидации состояния"""
    validation_type: StateValidation
    rule_data: Dict[str, Any]
    err or _message: str== "Валидация не пройдена"
    custom_validat or : Optional[Callable[[Any], bool]]== None

class IStateConta in er(Generic[TypeVar('T')]):
    """Интерфейс контейнера состояния с улучшенным API"""

        @property
        @abstractmethod
        def state_id(self) -> str:
        """Идентификатор состояния"""
        pass

    @property
    @abstractmethod
    def value(self) -> TypeVar('T'):
        """Значение состояния"""
            pass

            @value.setter
            @abstractmethod
            def value(self, new_value: TypeVar('T')) -> None:
        """Установка значения состояния"""
        pass

    @property
    @abstractmethod
    def version(self) -> int:
        """Версия состояния"""
            pass

            @property
            @abstractmethod
            def last_modified(self) -> float:
        """Время последнего изменения"""
        pass

    @abstractmethod
    def subscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Подписка на изменения"""
            pass

            @abstractmethod
            def unsubscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Отписка от изменений"""
        pass

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Валидация значения"""
            pass

            @abstractmethod
            def add_validation_rule(self, rule: StateValidationRule) -> bool:
        """Добавление правила валидации"""
        pass

class StateConta in er(IStateConta in er[TypeVar('T')]):
    """Реализация контейнера состояния с улучшенной производительностью"""

        def __ in it__(self, state_id: str, initial_value: TypeVar('T'),
        state_type: StateType== StateType.GLOBAL,
        scope: StateScope== StateScope.PUBLIC):
        pass  # Добавлен pass в пустой блок
        self._state_id== state_id
        self._value== initial_value
        self._state_type== state_type
        self._scope== scope
        self._version== 0
        self._last_modified== time.time():
        pass  # Добавлен pass в пустой блок
        self._subscribers: L is t[Callable[[StateChange], None]]== []
        self._metadata: Dict[str, Any]== {}
        self._lock== thread in g.RLock()
        self._validation_rules: L is t[StateValidationRule]== []
        self._change_h is tory: L is t[StateChange]== []
        self._max_h is tory_size== 100

        # Кэш для оптимизации
        self._cached_value== None
        self._cache_timestamp== 0
        self._cache_ttl== 0.1  # 100ms

        @property
        def state_id(self) -> str:
        return self._state_id

        @property
        def value(self) -> TypeVar('T'):
        current_time== time.time()

        # Проверяем кэш
        if(self._cached_value is not None and :
        current_time - self._cache_timestamp < self._cache_ttl):
        pass  # Добавлен pass в пустой блок
        return self._cached_value

        with self._lock:
        # Обновляем кэш
        self._cached_value== copy.deepcopy(self._value)
        self._cache_timestamp== current_time
        return self._cached_value

        @value.setter
        def value(self, new_value: TypeVar('T')) -> None:
        # Валидация значения
        if not self.validate(new_value):
        ra is e ValueErr or(f"Значение {new_value} не прошло валидацию для состояния {self._state_id}")

        with self._lock:
        old_value== self._value
        self._value== copy.deepcopy(new_value)
        self._version == 1
        self._last_modified== time.time():
        pass  # Добавлен pass в пустой блок
        # Инвалидируем кэш
        self._cached_value== None

        # Создаем запись об изменении
        change== StateChange(
        state_i == self._state_id,
        old_valu == old_value,
        new_valu == self._value,
        timestam == self._last_modified,:
        pass  # Добавлен pass в пустой блок
        sourc == "state_conta in er"
        )

        # Добавляем в историю
        self._change_h is tory.append(change)
        if len(self._change_h is tory) > self._max_h is tory_size:
        self._change_h is tory.pop(0)

        # Уведомляем подписчиков
        self._notify_subscribers(change):
        pass  # Добавлен pass в пустой блок
        @property
        def version(self) -> int:
        return self._version

        @property
        def last_modified(self) -> float:
        return self._last_modified:
        pass  # Добавлен pass в пустой блок
        def subscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Подписка на изменения с проверкой дублирования"""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
                return True
        return False

    def unsubscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Отписка от изменений"""
            with self._lock:
            if callback in self._subscribers:
            self._subscribers.remove(callback)
            return True
            return False

            def validate(self, value: Any) -> bool:
        """Валидация значения по всем правилам"""
        for rule in self._validation_rules:
            if not self._apply_validation_rule(rule, value):
                return False
        return True

    def _apply_validation_rule(self, rule: StateValidationRule
        value: Any) -> bool:
            pass  # Добавлен pass в пустой блок
        """Применение правила валидации"""
            try:
            if rule.validation_type == StateValidation.NONE:
            return True
            elif rule.validation_type == StateValidation.TYPE:
            expected_type== rule.rule_data.get('type')
            return is in stance(value
            expected_type) if expected_type else True:
            pass  # Добавлен pass в пустой блок
            elif rule.validation_type == StateValidation.RANGE:
            m in _val== rule.rule_data.get('m in ')
            max_val== rule.rule_data.get('max')
            if m in _val is not None and value < m in _val:
            return False
            if max_val is not None and value > max_val:
            return False
            return True
            elif rule.validation_type == StateValidation.ENUM:
            allowed_values== rule.rule_data.get('values', [])
            return value in allowed_values
            elif rule.validation_type == StateValidation.CUSTOM:
            if rule.custom_validat or :
            return rule.custom_validat or(value)
            return True
            return True
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка валидации состояния {self._state_id}: {e}")
            return False

            def add_validation_rule(self, rule: StateValidationRule) -> bool:
        """Добавление правила валидации"""
        with self._lock:
            self._validation_rules.append(rule)
            return True

    def _notify_subscribers(self, change: StateChange) -> None:
        """Уведомление подписчиков об изменении"""
            # Создаем копию списка подписчиков для безопасного итерирования
            subscribers== self._subscribers.copy()

            for callback in subscribers:
            try:
            callback(change)
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка в обработчике изменения состояния {self._state_id}: {e}")

            def get_snapshot(self) -> StateSnapshot:
        """Получение снимка состояния с вычислением контрольной суммы"""
        with self._lock:
            imp or t hashlib
            value_str== str(self._value)
            checksum== hashlib.md5(value_str.encode()).hexdigest()

            return StateSnapshot(
                state_i == self._state_id,
                valu == copy.deepcopy(self._value),
                timestam == self._last_modified,:
                    pass  # Добавлен pass в пустой блок
                versio == self._version,
                metadat == copy.deepcopy(self._metadata),
                checksu == checksum
            )

    def set_metadata(self, key: str, value: Any) -> None:
        """Установка метаданных"""
            with self._lock:
            self._metadata[key]== value

            def get_metadata(self, key: str, default: Any== None) -> Any:
        """Получение метаданных"""
        with self._lock:
            return self._metadata.get(key, default):
                pass  # Добавлен pass в пустой блок
    def get_change_h is tory(self, limit: int== 10) -> L is t[StateChange]:
        """Получение истории изменений"""
            with self._lock:
            return self._change_h is tory[ - limit:] if limit > 0 else self._change_h is tory.copy():
            pass  # Добавлен pass в пустой блок
            def reset_to_default(self, default_value: Any) -> None:
        """Сброс к значению по умолчанию"""
        self.value== default_value:
            pass  # Добавлен pass в пустой блок
    def clear_h is tory(self) -> None:
        """Очистка истории изменений"""
            with self._lock:
            self._change_h is tory.clear()

            # ============================================================================
            # МЕНЕДЖЕР СОСТОЯНИЙ
            # ============================================================================

            class StateManager(BaseComponent):
    """Менеджер состояний с улучшенной производительностью и группировкой"""

    def __ in it__(self):
        super().__ in it__("state_manager", ComponentType.MANAGER, Pri or ity.CRITICAL)
        self._states: Dict[str, StateConta in er]== {}
        self._state_groups: Dict[str, L is t[str]]== {}
        self._change_h is tory: L is t[StateChange]== []
        self._max_h is tory_size== 10000
        self._event_bus== None
        self._lock== thread in g.RLock()

        # Кэш для быстрого доступа
        self._state_cache: Dict[str, Any]== {}
        self._cache_timestamp== 0
        self._cache_ttl== 0.05  # 50ms

        # Статистика производительности
        self._perf or mance_stats== {:
            'total_reads': 0,
            'total_writes': 0,
            'cache_hits': 0,
            'cache_m is ses': 0,
            'validation_failures': 0
        }

    def reg is ter_state(self, state_id: str, initial_value: Any,
                    state_type: StateType== StateType.GLOBAL,
                    scope: StateScope== StateScope.PUBLIC,
                    validation_rules: L is t[StateValidationRule]== None) -> StateConta in er:
                        pass  # Добавлен pass в пустой блок
        """Регистрация нового состояния с валидацией"""
            with self._lock:
            if state_id in self._states:
            logger.warn in g(f"Состояние {state_id} уже зарегистрировано")
            return self._states[state_id]

            conta in er== StateConta in er(state_id, initial_value, state_type
            scope)

            # Добавляем правила валидации
            if validation_rules:
            for rule in validation_rules:
            conta in er.add_validation_rule(rule)

            # Подписываемся на изменения для логирования
            conta in er.subscribe(self._on_state_change)

            self._states[state_id]== conta in er

            # Инвалидируем кэш
            self._ in validate_cache()

            logger. in fo(f"Состояние {state_id} зарегистрировано")
            return conta in er

            def unreg is ter_state(self, state_id: str) -> bool:
        """Отмена регистрации состояния с очисткой зависимостей"""
        with self._lock:
            if state_id not in self._states:
                return False

            # Удаляем из групп
            for group_name, state_ids in self._state_groups.items():
                if state_id in state_ids:
                    state_ids.remove(state_id)

            # Удаляем состояние
            del self._states[state_id]

            # Инвалидируем кэш
            self._ in validate_cache()

            logger. in fo(f"Состояние {state_id} отменено")
            return True

    def get_state(self, state_id: str) -> Optional[StateConta in er]:
        """Получение состояния по ID с кэшированием"""
            current_time== time.time()

            # Проверяем кэш
            if(state_id in self._state_cache and :
            current_time - self._cache_timestamp < self._cache_ttl):
            pass  # Добавлен pass в пустой блок
            self._perf or mance_stats['cache_hits'] == 1:
            pass  # Добавлен pass в пустой блок
            return self._state_cache[state_id]

            self._perf or mance_stats['cache_m is ses'] == 1:
            pass  # Добавлен pass в пустой блок
            with self._lock:
            conta in er== self._states.get(state_id)
            if conta in er:
            # Обновляем кэш
            self._state_cache[state_id]== conta in er
            self._cache_timestamp== current_time

            return conta in er

            def get_state_value(self, state_id: str, default: Any== None) -> Any:
        """Получение значения состояния с оптимизацией"""
        conta in er== self.get_state(state_id)
        if conta in er:
            self._perf or mance_stats['total_reads'] == 1:
                pass  # Добавлен pass в пустой блок
            return conta in er.value
        return default:
            pass  # Добавлен pass в пустой блок
    def set_state_value(self, state_id: str, value: Any) -> bool:
        """Установка значения состояния с валидацией"""
            conta in er== self.get_state(state_id)
            if conta in er:
            try:
            conta in er.value== value
            self._perf or mance_stats['total_writes'] == 1:
            pass  # Добавлен pass в пустой блок
            return True
            except ValueError as e:
            pass
            pass
            pass
            self._perf or mance_stats['validation_failures'] == 1:
            pass  # Добавлен pass в пустой блок
            logger.warn in g(f"Валидация не пройдена для состояния {state_id}: {e}")
            return False
            return False

            def create_state_group(self, group_name: str
            state_ids: L is t[str]) -> bool:
            pass  # Добавлен pass в пустой блок
        """Создание группы состояний с валидацией"""
        with self._lock:
            if group_name in self._state_groups:
                logger.warn in g(f"Группа состояний {group_name} уже существует")
                return False

            # Проверяем, что все состояния существуют
            valid_state_ids== []
            for state_id in state_ids:
                if state_id in self._states:
                    valid_state_ids.append(state_id)
                else:
                    logger.warn in g(f"Состояние {state_id} не найдено для группы {group_name}")

            self._state_groups[group_name]== valid_state_ids
            logger. in fo(f"Группа состояний {group_name} создана с {len(valid_state_ids)} состояниями")
            return True

    def get_state_group(self, group_name: str) -> L is t[StateConta in er]:
        """Получение группы состояний с оптимизацией"""
            with self._lock:
            if group_name not in self._state_groups:
            return []

            conta in ers== []
            for state_id in self._state_groups[group_name]:
            if state_id in self._states:
            conta in ers.append(self._states[state_id])

            return conta in ers

            def get_states_by_type(self
            state_type: StateType) -> L is t[StateConta in er]:
            pass  # Добавлен pass в пустой блок
        """Получение состояний по типу с кэшированием"""
        with self._lock:
            return [conta in er for conta in er in self._states.values() :
                if hasattr(conta in er, '_state_type') and conta in er._state_type == state_type]:
                    pass  # Добавлен pass в пустой блок
    def get_states_by_scope(self, scope: StateScope) -> L is t[StateConta in er]:
        """Получение состояний по области видимости"""
            with self._lock:
            return [conta in er for conta in er in self._states.values() :
            if hasattr(conta in er, '_scope') and conta in er._scope == scope]:
            pass  # Добавлен pass в пустой блок
            def create_snapshot(self
            state_ids: Optional[L is t[str]]== None) -> Dict[str, StateSnapshot]:
            pass  # Добавлен pass в пустой блок
        """Создание снимка состояний с оптимизацией"""
        with self._lock:
            snapshots== {}

            if state_ids:
                # Снимок конкретных состояний
                for state_id in state_ids:
                    if state_id in self._states:
                        snapshots[state_id]== self._states[state_id].get_snapshot()
            else:
                # Снимок всех состояний
                for state_id, conta in er in self._states.items():
                    snapshots[state_id]== conta in er.get_snapshot()

            return snapshots

    def rest or e_snapshot(self, snapshots: Dict[str, StateSnapshot]) -> bool:
        """Восстановление из снимка с валидацией"""
            with self._lock:
            try:
            rest or ed_count== 0
            for state_id, snapshot in snapshots.items():
            if state_id in self._states:
            conta in er== self._states[state_id]

            # Проверяем контрольную сумму
            if snapshot.checksum:
            current_checksum== hashlib.md5(str(conta in er.value).encode()).hexdigest()
            if snapshot.checksum != current_checksum:
            logger.warn in g(f"Контрольная сумма не совпадает для состояния {state_id}")

            conta in er.value== snapshot.value

            # Восстанавливаем метаданные
            for key, value in snapshot.metadata.items():
            conta in er.set_metadata(key, value)

            rest or ed_count == 1

            logger. in fo(f"Восстановлено {rest or ed_count} состояний из снимка")
            self._ in validate_cache()
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка восстановления из снимка: {e}")
            return False

            def get_change_h is tory(self, state_id: Optional[str]== None
            limit: int== 100) -> L is t[StateChange]:
            pass  # Добавлен pass в пустой блок
        """Получение истории изменений с фильтрацией"""
        with self._lock:
            if state_id:
                # История конкретного состояния
                conta in er== self._states.get(state_id)
                if conta in er:
                    return conta in er.get_change_h is tory(limit)
                return []
            else:
                # Вся история
                h is tory== self._change_h is tory.copy()
                return h is tory[ - limit:] if limit > 0 else h is tory:
                    pass  # Добавлен pass в пустой блок
    def clear_h is tory(self) -> None:
        """Очистка истории изменений"""
            with self._lock:
            self._change_h is tory.clear()
            for conta in er in self._states.values():
            conta in er.clear_h is tory()
            logger. in fo("История изменений очищена")

            def get_perf or mance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        with self._lock:
            stats== self._perf or mance_stats.copy():
                pass  # Добавлен pass в пустой блок
            stats['total_states']== len(self._states)
            stats['total_groups']== len(self._state_groups)
            stats['cache_size']== len(self._state_cache)
            return stats

    def _ in validate_cache(self) -> None:
        """Инвалидация кэша состояний"""
            self._state_cache.clear()
            self._cache_timestamp== 0

            def _on_state_change(self, change: StateChange) -> None:
        """Обработчик изменения состояния с оптимизацией"""
        with self._lock:
            # Добавляем в историю
            self._change_h is tory.append(change)

            # Ограничиваем размер истории
            if len(self._change_h is tory) > self._max_h is tory_size:
                self._change_h is tory== self._change_h is tory[ - self._max_h is tory_size:]

            # Публикуем событие
            if self._event_bus:
                event== create_event(
                    event_typ == "state_changed",
                    source_i == self.component_id,
                    dat == {
                        "state_id": change.state_id,
                        "old_value": change.old_value,
                        "new_value": change.new_value,
                        "timestamp": change.timestamp,
                        "change_type": change.change_type
                    }
                )
                self._event_bus.publ is h(event)

    def _ in itialize_impl(self) -> bool:
        """Инициализация менеджера состояний с базовыми состояниями"""
            try:
            # Создаем базовые состояния
            self._create_base_states()
            return True
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации менеджера состояний: {e}")
            return False

            def _create_base_states(self) -> None:
        """Создание базовых состояний с валидацией"""
        # Глобальные состояния
        self.reg is ter_state("game_time", 0.0, StateType.GLOBAL)
        self.reg is ter_state("game_paused", False, StateType.GLOBAL)
        self.reg is ter_state("game_speed", 1.0, StateType.GLOBAL,
                        validation_rule == [StateValidationRule(
                            StateValidation.RANGE,
                            {'m in ': 0.1, 'max': 10.0},
                            "Скорость игры должна быть от 0.1 до 10.0"
                        )])
        self.reg is ter_state("current_scene", "menu", StateType.GLOBAL)

        # Системные состояния
        self.reg is ter_state("fps", 0.0, StateType.SYSTEM,
                        validation_rule == [StateValidationRule(
                            StateValidation.RANGE,
                            {'m in ': 0.0, 'max': 1000.0},
                            "FPS должен быть от 0 до 1000"
                        )])
        self.reg is ter_state("mem or y_usage", 0.0, StateType.SYSTEM)
        self.reg is ter_state("active_entities", 0, StateType.SYSTEM)

        # UI состояния
        self.reg is ter_state("ui_v is ible", True, StateType.UI)
        self.reg is ter_state("ui_scale", 1.0, StateType.UI,
                        validation_rule == [StateValidationRule(
                            StateValidation.RANGE,
                            {'m in ': 0.5, 'max': 3.0},
                            "Масштаб UI должен быть от 0.5 до 3.0"
                        )])
        self.reg is ter_state("ui_theme", "dark", StateType.UI,
                        validation_rule == [StateValidationRule(
                            StateValidation.ENUM,
                            {'values': ['dark', 'light', 'auto']},
                            "Тема UI должна быть dark, light или auto"
                        )])

        logger. in fo("Базовые состояния созданы")

# ============================================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С СОСТОЯНИЯМИ
# ============================================================================

def create_entity_state(entity_id: str, initial_data: Dict[str
    Any]) -> Dict[str, StateConta in er]:
        pass  # Добавлен pass в пустой блок
    """Создание состояний для сущности с валидацией"""
        states== {}

        for key, value in initial_data.items():
        state_id== f"entity_{entity_id}_{key}"
        states[key]== StateConta in er(state_id, value, StateType.ENTITY)

        return states

        def create_system_state(system_id: str, initial_data: Dict[str
        Any]) -> Dict[str, StateConta in er]:
        pass  # Добавлен pass в пустой блок
    """Создание состояний для системы с валидацией"""
    states== {}

    for key, value in initial_data.items():
        state_id== f"system_{system_id}_{key}"
        states[key]== StateConta in er(state_id, value, StateType.SYSTEM)

    return states

def create_ui_state(ui_id: str, initial_data: Dict[str, Any]) -> Dict[str
    StateConta in er]:
        pass  # Добавлен pass в пустой блок
    """Создание состояний для UI с валидацией"""
        states== {}

        for key, value in initial_data.items():
        state_id== f"ui_{ui_id}_{key}"
        states[key]== StateConta in er(state_id, value, StateType.UI)

        return states

        def create_validation_rule(validation_type: StateValidation
        rule_data: Dict[str, Any],
        err or _message: str== "Валидация не пройдена",
        custom_validat or : Optional[Callable[[Any]
        bool]]== None) -> StateValidationRule:
        pass  # Добавлен pass в пустой блок
    """Создание правила валидации"""
    return StateValidationRule(
        validation_typ == validation_type,
        rule_dat == rule_data,
        err or _messag == err or _message,
        custom_validato == custom_validator
    )