#!/usr / bin / env python3
"""
    Система крафтинга - создание предметов из материалов
"""

imp or t logg in g
imp or t time
imp or t r and om
from typ in g imp or t Dict, L is t, Optional, Any, Union
from dataclasses imp or t dataclass, field:
    pass  # Добавлен pass в пустой блок
from ...c or e. in terfaces imp or t ISystem, SystemPri or ity, SystemState
from ...c or e.state_manager imp or t StateManager
from ...c or e.reposit or y imp or t Reposit or yManager, DataType, St or ageType
from ...c or e.constants imp or t constants_manager, ItemType, ItemRarity
    ItemCateg or y, StatType, BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS
    SYSTEM_LIMITS

logger== logg in g.getLogger(__name__)

@dataclass:
    pass  # Добавлен pass в пустой блок
class Recipe:
    """Рецепт крафтинга"""
        recipe_id: str
        name: str
        description: str
        categ or y: str
        difficulty: int== 1  # 1 - 10
        required_level: int== 1
        craft in g_time: float== 1.0  # секунды
        experience_ga in : int== 10
        success_chance: float== 1.0
        materials: Dict[str, int]== field(default_factor == dict)  # item_id: count
        tools: L is t[str]== field(default_factor == list)  # required tools:
        pass  # Добавлен pass в пустой блок
        result_item: str== ""
        result_count: int== 1
        result_quality: float== 1.0
        unlock_conditions: Dict[str, Any]== field(default_factor == dict):
        pass  # Добавлен pass в пустой блок
        is_d is covered: bool== False
        d is covery_chance: float== 0.1

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class Craft in gSession:
    """Сессия крафтинга"""
    session_id: str
    entity_id: str
    recipe_id: str
    start_time: float== field(default_factor == time.time):
        pass  # Добавлен pass в пустой блок
    progress: float== 0.0  # 0.0 - 1.0
    is_completed: bool== False
    is_failed: bool== False
    result_items: L is t[str]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
    experience_ga in ed: int== 0
    materials_used: Dict[str, int]== field(default_factor == dict):
        pass  # Добавлен pass в пустой блок
@dataclass:
    pass  # Добавлен pass в пустой блок
class Craft in gResult:
    """Результат крафтинга"""
        success: bool
        item_id: str== ""
        item_count: int== 0
        quality: float== 1.0
        experience_ga in ed: int== 0
        materials_consumed: Dict[str, int]== field(default_factor == dict):
        pass  # Добавлен pass в пустой блок
        err or _message: str== ""
        craft in g_time: float== 0.0

        class Craft in gSystem(ISystem):
    """Система крафтинга"""

    def __ in it__(self):
        self._system_name== "craft in g"
        self._system_pri or ity== SystemPri or ity.NORMAL
        self._system_state== SystemState.UNINITIALIZED
        self._dependencies== []
        # Интеграция с архитектурой(опционально)
        self.state_manager: Optional[StateManager]== None
        self.reposit or y_manager: Optional[Reposit or yManager]== None
        self.event_bus== None

        # Рецепты
        self.recipes: Dict[str, Recipe]== {}

        # Активные сессии крафтинга
        self.craft in g_sessions: Dict[str, Craft in gSession]== {}

        # История крафтинга
        self.craft in g_h is tory: L is t[Dict[str, Any]]== []

        # Настройки системы
        self.system_sett in gs== {
            'max_craft in g_sessions': SYSTEM_LIMITS["max_craft in g_sessions"],
            'base_success_chance': PROBABILITY_CONSTANTS["base_craft in g_success"],
            'quality_variance': 0.2,
            'experience_multiplier': 1.0,
            'auto_d is covery_enabled': True
        }

        # Статистика системы
        self.system_stats== {
            'total_recipes': 0,
            'active_sessions': 0,
            'completed_crafts': 0,
            'failed_crafts': 0,
            'total_experience_ga in ed': 0,
            'update_time': 0.0
        }

        logger. in fo("Система крафтинга инициализирована")

    @property
    def system_name(self) -> str:
        return self._system_name

    @property
    def system_pri or ity(self) -> SystemPri or ity:
        return self._system_pri or ity

    @property
    def system_state(self) -> SystemState:
        return self._system_state

    @property
    def dependencies(self) -> L is t[str]:
        return self._dependencies

    def initialize(self) -> bool:
        """Инициализация системы крафтинга"""
            try:
            logger. in fo("Инициализация системы крафтинга...")

            # Настраиваем систему
            self._setup_craft in g_system()

            # Создаем базовые рецепты
            self._create_base_recipes()

            # Регистрация состояний / репозиториев при наличии менеджеров
            self._reg is ter_system_states()
            self._reg is ter_system_reposit or ies()

            self._system_state== SystemState.READY
            logger. in fo("Система крафтинга успешно инициализирована")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации системы крафтинга: {e}")
            self._system_state== SystemState.ERROR
            return False

            def update(self, delta_time: float) -> bool:
        """Обновление системы крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления системы крафтинга: {e}")
            return False

    def pause(self) -> bool:
        """Приостановка системы крафтинга"""
            try:
            if self._system_state == SystemState.READY:
            self._system_state== SystemState.PAUSED
            logger. in fo("Система крафтинга приостановлена")
            return True
            return False
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка приостановки системы крафтинга: {e}")
            return False

            def resume(self) -> bool:
        """Возобновление системы крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка возобновления системы крафтинга: {e}")
            return False

    def cleanup(self) -> bool:
        """Очистка системы крафтинга"""
            try:
            logger. in fo("Очистка системы крафтинга...")

            # Очищаем все данные
            self.recipes.clear()
            self.craft in g_sessions.clear()
            self.craft in g_h is tory.clear()

            # Сбрасываем статистику
            self.system_stats== {
            'total_recipes': 0,
            'active_sessions': 0,
            'completed_crafts': 0,
            'failed_crafts': 0,
            'total_experience_ga in ed': 0,
            'update_time': 0.0
            }

            self._system_state== SystemState.DESTROYED
            logger. in fo("Система крафтинга очищена")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки системы крафтинга: {e}")
            return False

            def get_system_ in fo(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        info== {
            'name': self.system_name,
            'state': self.system_state.value,
            'pri or ity': self.system_pri or ity.value,
            'dependencies': self.dependencies,
            'total_recipes': len(self.recipes),
            'active_sessions': len(self.craft in g_sessions),
            'stats': self.system_stats
        }
        # Вывод некоторых агрегатов наверх для удобства UI / тестов
        info['completed_crafts']== self.system_stats.get('completed_crafts', 0)
        info['failed_crafts']== self.system_stats.get('failed_crafts', 0)
        return info

    def _reg is ter_system_states(self) -> None:
        """Регистрация состояний системы(mock - friendly)."""
            if not self.state_manager:
            return
            try:
            # Предпочитаем update_state(для mock в тестах)
            self.state_manager.update_state("craft in g_system_sett in gs", self.system_sett in gs)
            self.state_manager.update_state("craft in g_system_stats", self.system_stats)
            self.state_manager.update_state("craft in g_active_sessions", l is t(self.craft in g_sessions.keys()))
            except Exception:
            pass
            pass
            pass
            # Fallback на реальную реализацию
            try:
            from ...c or e.state_manager imp or t StateType, StateScope
            self.state_manager.reg is ter_state("craft in g_system_sett in gs", self.system_sett in gs, StateType.CONFIGURATION, StateScope.SYSTEM)
            self.state_manager.reg is ter_state("craft in g_system_stats", self.system_stats, StateType.STATISTICS, StateScope.SYSTEM)
            self.state_manager.reg is ter_state("craft in g_active_sessions", l is t(self.craft in g_sessions.keys()), StateType.DYNAMIC_DATA, StateScope.SYSTEM)
            except Exception:
            pass
            pass  # Добавлен pass в пустой блок
            def _reg is ter_system_reposit or ies(self) -> None:
        """Регистрация репозиториев системы(mock - friendly)."""
        if not self.reposit or y_manager:
            return
        try:
        except Exception:
            pass
            pass  # Добавлен pass в пустой блок
    def h and le_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
            try:
            if event_type == "entity_created":
            return self._h and le_entity_created(event_data)
            elif event_type == "entity_destroyed":
            return self._h and le_entity_destroyed(event_data)
            elif event_type == "item_acquired":
            return self._h and le_item_acquired(event_data)
            elif event_type == "skill_learned":
            return self._h and le_skill_learned(event_data)
            else:
            return False
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события {event_type}: {e}")
            return False

            def _setup_craft in g_system(self) -> None:
        """Настройка системы крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Не удалось настроить систему крафтинга: {e}")

    def _create_base_recipes(self) -> None:
        """Создание базовых рецептов"""
            try:
            # Простые рецепты
            simple_recipes== [
            Recipe(
            recipe_i == "wooden_stick",
            nam == "Деревянная палка",
            descriptio == "Простая деревянная палка",
            categor == "woodw or king",
            difficult == 1,:
            pass  # Добавлен pass в пустой блок
            required_leve == 1,
            craft in g_tim == 2.0,
            experience_gai == 5,
            material == {"wood": 1},
            result_ite == "wooden_stick",
            result_coun == 1,
            is_d is covere == True
            ),
            Recipe(
            recipe_i == "stone_tool",
            nam == "Каменный инструмент",
            descriptio == "Примитивный каменный инструмент",
            categor == "stonew or king",
            difficult == 2,:
            pass  # Добавлен pass в пустой блок
            required_leve == 2,
            craft in g_tim == 5.0,
            experience_gai == 15,
            material == {"stone": 2, "wooden_stick": 1},
            tool == ["hammer"],
            result_ite == "stone_tool",
            result_coun == 1,
            is_d is covere == True
            ),
            Recipe(
            recipe_i == "leather_arm or ",
            nam == "Кожаная броня",
            descriptio == "Легкая кожаная броня",
            categor == "leatherw or king",
            difficult == 3,:
            pass  # Добавлен pass в пустой блок
            required_leve == 3,
            craft in g_tim == 10.0,
            experience_gai == 25,
            material == {"leather": 3, "thread": 2},
            tool == ["needle"],
            result_ite == "leather_arm or ",
            result_coun == 1,
            is_d is covere == True
            )
            ]

            # Средние рецепты
            medium_recipes== [
            Recipe(
            recipe_i == "iron_sw or d",
            nam == "Железный меч",
            descriptio == "Надежный железный меч",
            categor == "blacksmith in g",
            difficult == 5,:
            pass  # Добавлен pass в пустой блок
            required_leve == 5,
            craft in g_tim == 20.0,
            experience_gai == 50,
            material == {"iron_ in got": 2, "wooden_stick": 1},
            tool == ["anvil", "hammer"],
            result_ite == "iron_sw or d",
            result_coun == 1,
            is_d is covere == False,
            d is covery_chanc == 0.3
            ),
            Recipe(
            recipe_i == "heal in g_potion",
            nam == "Зелье лечения",
            descriptio == "Восстанавливает здоровье",
            categor == "alchemy",
            difficult == 4,:
            pass  # Добавлен pass в пустой блок
            required_leve == 4,
            craft in g_tim == 15.0,
            experience_gai == 40,
            material == {"herb": 2, "water": 1, "bottle": 1},
            tool == ["cauldron"],
            result_ite == "heal in g_potion",
            result_coun == 1,
            is_d is covere == False,
            d is covery_chanc == 0.4
            )
            ]

            # Сложные рецепты
            complex_recipes== [
            Recipe(
            recipe_i == "magic_staff",
            nam == "Магический посох",
            descriptio == "Мощный магический посох",
            categor == "enchant in g",
            difficult == 8,:
            pass  # Добавлен pass в пустой блок
            required_leve == 8,
            craft in g_tim == 60.0,
            experience_gai == 100,
            material == {"rare_wood": 1, "magic_crystal": 2, "gold_ in got": 1},
            tool == ["enchant in g_table"],
            result_ite == "magic_staff",
            result_coun == 1,
            is_d is covere == False,
            d is covery_chanc == 0.1
            ),
            Recipe(
            recipe_i == "dragon_arm or ",
            nam == "Драконья броня",
            descriptio == "Легендарная броня из чешуи дракона",
            categor == "arm or smith in g",
            difficult == 10,:
            pass  # Добавлен pass в пустой блок
            required_leve == 10,
            craft in g_tim == 120.0,
            experience_gai == 200,
            material == {"dragon_scale": 5, "mythril_ in got": 3, "enchanted_thread": 2},
            tool == ["master_anvil", "magic_hammer"],
            result_ite == "dragon_arm or ",
            result_coun == 1,
            is_d is covere == False,
            d is covery_chanc == 0.05
            )
            ]

            # Добавляем все рецепты
            all_recipes== simple_recipes + medium_recipes + complex_recipes
            for recipe in all_recipes:
            self.recipes[recipe.recipe_id]== recipe

            logger. in fo(f"Создано {len(all_recipes)} базовых рецептов")

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка создания базовых рецептов: {e}")

            def _update_craft in g_sessions(self, delta_time: float) -> None:
        """Обновление активных сессий крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка обновления сессий крафтинга: {e}")

    def _check_completed_sessions(self) -> None:
        """Проверка завершенных сессий"""
            try:
            # Удаляем завершенные сессии
            completed_sessions== [
            session_id for session_id
            session in self.craft in g_sessions.items():
            pass  # Добавлен pass в пустой блок
            if session. is _completed or session. is _failed:
            pass  # Добавлен pass в пустой блок
            ]

            for session_id in completed_sessions:
            del self.craft in g_sessions[session_id]

            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки завершенных сессий: {e}")

            def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка обновления статистики системы: {e}")

    def _h and le_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
            try:
            entity_id== event_data.get('entity_id')
            craft in g_skills== event_data.get('craft in g_skills', [])

            if entity_id:
            # Здесь можно добавить логику для новых сущностей
            logger.debug(f"Обработано событие создания сущности {entity_id}")
            return True
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события создания сущности: {e}")
            return False

            def _h and le_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события уничтожения сущности: {e}")
            return False

    def _h and le_item_acquired(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения предмета"""
            try:
            entity_id== event_data.get('entity_id')
            item_id== event_data.get('item_id')
            item_type== event_data.get('item_type')

            if entity_id and item_id and item_type:
            # Проверяем, не разблокирует ли предмет новые рецепты
            self._check_recipe_unlocks(entity_id, item_id, item_type)
            return True
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события получения предмета: {e}")
            return False

            def _h and le_skill_learned(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изучения навыка"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события изучения навыка: {e}")
            return False

    def start_craft in g(self, entity_id: str, recipe_id: str
        materials: Dict[str, int]== None) -> Optional[str]:
            pass  # Добавлен pass в пустой блок
        """Начало крафтинга"""
            try:
            if entity_id not in self.recipes:
            logger.warn in g(f"Рецепт {recipe_id} не найден")
            return None

            recipe== self.recipes[recipe_id]

            # Проверяем требования
            if not self._check_recipe_requirements(entity_id, recipe):
            logger.warn in g(f"Не выполнены требования рецепта {recipe_id}")
            return None

            # Проверяем лимит сессий
            if len(self.craft in g_sessions) >= self.system_sett in gs['max_craft in g_sessions']:
            logger.warn in g("Достигнут лимит активных сессий крафтинга")
            return None

            # Создаем сессию крафтинга
            session_id== f"craft_{entity_id}_{ in t(time.time() * 1000)}"
            session== Craft in gSession(
            session_i == session_id,
            entity_i == entity_id,
            recipe_i == recipe_id
            )

            # Добавляем в систему
            self.craft in g_sessions[session_id]== session

            # Записываем в историю
            current_time== time.time()
            self.craft in g_h is tory.append({
            'timestamp': current_time,
            'action': 'craft in g_started',
            'session_id': session_id,
            'entity_id': entity_id,
            'recipe_id': recipe_id
            })

            logger. in fo(f"Начата сессия крафтинга {session_id} для {entity_id}")
            return session_id

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка начала крафтинга {recipe_id} для {entity_id}: {e}")
            return None

            def _check_recipe_requirements(self, entity_id: str
            recipe: Recipe) -> bool:
            pass  # Добавлен pass в пустой блок
        """Проверка требований рецепта"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки требований рецепта: {e}")
            return False

    def _check_craft in g_success(self, recipe: Recipe
        session: Craft in gSession) -> bool:
            pass  # Добавлен pass в пустой блок
        """Проверка успеха крафтинга"""
            try:
            # Базовая вероятность успеха
            base_chance== recipe.success_chance

            # Применяем случайность
            if r and om.r and om() <= base_chance:
            return True
            else:
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки успеха крафтинга: {e}")
            return False

            def _complete_craft in g_session(self, session: Craft in gSession
            success: bool) -> None:
            pass  # Добавлен pass в пустой блок
        """Завершение сессии крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка завершения сессии крафтинга: {e}")

    def _cancel_entity_craft in g_sessions(self, entity_id: str) -> None:
        """Отмена всех сессий крафтинга сущности"""
            try:
            sessions_to_cancel== [
            session_id for session_id
            session in self.craft in g_sessions.items():
            pass  # Добавлен pass в пустой блок
            if session.entity_id == entity_id:
            pass  # Добавлен pass в пустой блок
            ]

            for session_id in sessions_to_cancel:
            session== self.craft in g_sessions[session_id]
            session. is _failed== True

            # Записываем в историю
            current_time== time.time()
            self.craft in g_h is tory.append({
            'timestamp': current_time,
            'action': 'craft in g_cancelled',
            'session_id': session_id,
            'entity_id': entity_id,
            'recipe_id': session.recipe_id
            })

            logger.debug(f"Отменена сессия крафтинга {session_id}")

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка отмены сессий крафтинга для {entity_id}: {e}")

            def _check_recipe_unlocks(self, entity_id: str, item_id: str
            item_type: str) -> None:
            pass  # Добавлен pass в пустой блок
        """Проверка разблокировки рецептов при получении предмета"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки разблокировки рецептов: {e}")

    def _check_item_recipe_unlock(self, recipe: Recipe, item_id: str
        item_type: str) -> bool:
            pass  # Добавлен pass в пустой блок
        """Проверка разблокировки рецепта предметом"""
            try:
            # Здесь должна быть логика проверки разблокировки
            # Пока просто возвращаем False для демонстрации
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки разблокировки рецепта предметом: {e}")
            return False

            def _check_skill_recipe_unlocks(self, entity_id: str
            skill_name: str) -> None:
            pass  # Добавлен pass в пустой блок
        """Проверка разблокировки рецептов при изучении навыка"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки разблокировки рецептов навыком: {e}")

    def _check_skill_recipe_unlock(self, recipe: Recipe
        skill_name: str) -> bool:
            pass  # Добавлен pass в пустой блок
        """Проверка разблокировки рецепта навыком"""
            try:
            # Здесь должна быть логика проверки разблокировки
            # Пока просто возвращаем False для демонстрации
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка проверки разблокировки рецепта навыком: {e}")
            return False

            def get_recipe_ in fo(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о рецепте"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения информации о рецепте {recipe_id}: {e}")
            return None

    def get_available_recipes(self, entity_id: str
        categ or y: str== None) -> L is t[Dict[str, Any]]:
            pass  # Добавлен pass в пустой блок
        """Получение доступных рецептов"""
            try:
            available_recipes== []

            for recipe in self.recipes.values():
            if not recipe. is _d is covered:
            cont in ue

            if categ or y and recipe.categ or y != categ or y:
            cont in ue

            # Проверяем доступность
            if self._check_recipe_requirements(entity_id, recipe):
            recipe_ in fo== self.get_recipe_ in fo(recipe.recipe_id)
            if recipe_ in fo:
            available_recipes.append(recipe_ in fo)

            return available_recipes

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения доступных рецептов для {entity_id}: {e}")
            return []

            def get_craft in g_session_ in fo(self, session_id: str) -> Optional[Dict[str
            Any]]:
            pass  # Добавлен pass в пустой блок
        """Получение информации о сессии крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения информации о сессии крафтинга {session_id}: {e}")
            return None

    def cancel_craft in g(self, session_id: str) -> bool:
        """Отмена крафтинга"""
            try:
            if session_id not in self.craft in g_sessions:
            return False

            session== self.craft in g_sessions[session_id]
            session. is _failed== True

            # Записываем в историю
            current_time== time.time()
            self.craft in g_h is tory.append({
            'timestamp': current_time,
            'action': 'craft in g_cancelled',
            'session_id': session_id,
            'entity_id': session.entity_id,
            'recipe_id': session.recipe_id
            })

            logger. in fo(f"Отменен крафтинг {session_id}")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка отмены крафтинга {session_id}: {e}")
            return False

            def get_craft in g_h is tory(self, entity_id: str== None
            limit: int== 50) -> L is t[Dict[str, Any]]:
            pass  # Добавлен pass в пустой блок
        """Получение истории крафтинга"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения истории крафтинга: {e}")
            return []

    def add_custom_recipe(self, recipe_data: Dict[str, Any]) -> bool:
        """Добавление пользовательского рецепта"""
            try:
            recipe_id== recipe_data.get('recipe_id')
            if not recipe_id or recipe_id in self.recipes:
            return False

            # Создаем новый рецепт
            recipe== Recipe(
            recipe_i == recipe_id,
            nam == recipe_data.get('name', ''),
            descriptio == recipe_data.get('description', ''),
            categor == recipe_data.get('categ or y', 'custom'),
            difficult == recipe_data.get('difficulty', 1),:
            pass  # Добавлен pass в пустой блок
            required_leve == recipe_data.get('required_level', 1),
            craft in g_tim == recipe_data.get('craft in g_time', 1.0),
            experience_gai == recipe_data.get('experience_ga in ', 10),
            success_chanc == recipe_data.get('success_chance', 1.0),
            material == recipe_data.get('materials', {}),
            tool == recipe_data.get('tools', []),
            result_ite == recipe_data.get('result_item', ''),
            result_coun == recipe_data.get('result_count', 1),
            result_qualit == recipe_data.get('result_quality', 1.0),
            unlock_condition == recipe_data.get('unlock_conditions', {}),
            is_d is covere == recipe_data.get(' is _d is covered', True),
            d is covery_chanc == recipe_data.get('d is covery_chance', 0.0)
            )

            # Добавляем в систему
            self.recipes[recipe_id]== recipe

            logger. in fo(f"Добавлен пользовательский рецепт {recipe_id}")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка добавления пользовательского рецепта: {e}")
            return False

            def remove_recipe(self, recipe_id: str) -> bool:
        """Удаление рецепта"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка удаления рецепта {recipe_id}: {e}")
            return False