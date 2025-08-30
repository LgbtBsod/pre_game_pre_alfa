#!/usr / bin / env python3
"""
    Класс NPC - неигровые персонажи
"""

imp or t logg in g
imp or t time
from typ in g imp or t Dict, L is t, Optional, Any, Union
from dataclasses imp or t dataclass, field:
    pass  # Добавлен pass в пустой блок
from ..c or e.constants imp or t constants_manager, StatType, DamageType, AIState
    EntityType
from .base_entity imp or t BaseEntity, EntityType as BaseEntityType

logger== logg in g.getLogger(__name__)

@dataclass:
    pass  # Добавлен pass в пустой блок
class NPCStats:
    """Дополнительные характеристики NPC"""
        # Социальные характеристики
        reputation: int== 0
        influence: int== 0

        # Профессиональные характеристики
        profession: str== "civilian"
        skill_level: int== 1

        # Экономические характеристики
        wealth: int== 0
        trade_skill: float== 0.5

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class NPCPersonality:
    """Личность NPC"""
    # Основные черты характера
    friendl in ess: float== 0.5  # -1.0 до 1.0
    aggression: float== 0.3    # 0.0 до 1.0
    curiosity: float== 0.4     # 0.0 до 1.0
    loyalty: float== 0.6       # 0.0 до 1.0

    # Поведенческие паттерны
    talkativeness: float== 0.5  # 0.0 до 1.0
    generosity: float== 0.4     # 0.0 до 1.0
    honesty: float== 0.7        # 0.0 до 1.0

    # Предпочтения
    preferred_topics: L is t[str]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
    d is liked_topics: L is t[str]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
@dataclass:
    pass  # Добавлен pass в пустой блок
class NPCMem or y:
    """Дополнительная память NPC"""
        # Социальные связи
        known_players: L is t[str]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
        known_npcs: L is t[str]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
        relationships: Dict[str
        float]== field(default_factor == dict)  # entity_id -> relationship_value:
        pass  # Добавлен pass в пустой блок
        # История взаимодействий
        conversations: L is t[Dict[str, Any]]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
        trades: L is t[Dict[str, Any]]== field(default_factor == list):
        pass  # Добавлен pass в пустой блок
        # Временные метки
        last_conversation: float== 0.0
        last_trade: float== 0.0
        last_mood_change: float== 0.0

        class NPC(BaseEntity):
    """Класс неигрового персонажа - наследуется от BaseEntity"""

    def __ in it__(self, npc_id: str, name: str, npc_type: str== "civilian"):
        # Инициализируем базовую сущность
        super().__ in it__(npc_id, BaseEntityType.NPC, name)

        # Дополнительные характеристики NPC
        self.npc_stats== NPCStats(professio == npc_type)
        self.personality== NPCPersonality()
        self.npc_mem or y== NPCMem or y()

        # Специфичные для NPC настройки
        self. in vent or y.max_slots== 15  # Меньше слотов инвентаря
        self. in vent or y.max_weight== 80.0  # Меньше веса
        self.mem or y.max_mem or ies== 150  # Средняя память
        self.mem or y.learn in g_rate== 0.5  # Средняя скорость обучения

        # Поведение и состояние
        self.behavior== "passive"  # passive, aggressive, friendly, neutral
        self.current_mood== "neutral"  # happy, sad, angry, scared, neutral
        self. is _busy== False
        self. is _interact in g== False

        # Диалоги и квесты
        self.dialogue_options: L is t[str]== []
        self.available_quests: L is t[str]== []
        self.completed_quests: L is t[str]== []
        self.quest_giver== False

        # Торговля
        self. is _merchant== False
        self.shop_ in vent or y: L is t[str]== []
        self.prices: Dict[str, int]== {}

        # Расписание
        self.schedule: Dict[str, str]== {}  # time -> activity
        self.current_activity== "idle"

        logger. in fo(f"Создан NPC: {name} ({npc_type})")

    def update(self, delta_time: float):
        """Обновление состояния NPC"""
            try:
            # Обновляем базовую сущность
            super().update(delta_time)

            # Обновляем расписание
            self._update_schedule(delta_time)

            # Обновляем настроение
            self._update_mood(delta_time)

            # Обновляем поведение
            self._update_behavi or(delta_time)

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления NPC {self.entity_id}: {e}")

            def _update_schedule(self, delta_time: float):
        """Обновление расписания NPC"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления расписания NPC {self.entity_id}: {e}")

    def _update_mood(self, delta_time: float):
        """Обновление настроения NPC"""
            try:
            current_time== time.time()

            # Базовое изменение настроения в зависимости от активности
            mood_change== 0.0

            if self.current_activity == "w or k":
            mood_change== -0.01 * delta_time  # Работа немного утомляет
            elif self.current_activity == "le is ure":
            mood_change== 0.02 * delta_time   # Досуг поднимает настроение
            elif self.current_activity == "social":
            mood_change== 0.015 * delta_time  # Общение улучшает настроение
            elif self.current_activity == "sleep":
            mood_change== 0.01 * delta_time   # Сон восстанавливает

            # Применяем изменение настроения
            self.emotions.mood== max( - 1.0, m in(1.0
            self.emotions.mood + mood_change))

            # Обновляем текущее настроение
            if self.emotions.mood > 0.3:
            self.current_mood== "happy"
            elif self.emotions.mood < -0.3:
            self.current_mood== "sad"
            else:
            self.current_mood== "neutral"

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления настроения NPC {self.entity_id}: {e}")

            def _update_behavi or(self, delta_time: float):
        """Обновление поведения NPC"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления поведения NPC {self.entity_id}: {e}")

    def interact_with_player(self, player_id: str, interaction_type: str,
                        context: Dict[str, Any]== None) -> Dict[str, Any]:
                            pass  # Добавлен pass в пустой блок
        """Взаимодействие с игроком"""
            try:
            if not context:
            context== {}

            # Обновляем время последнего взаимодействия
            self.npc_mem or y.last_conversation== time.time()

            # Добавляем игрока в известных, если его там нет
            if player_id not in self.npc_mem or y.known_players:
            self.npc_mem or y.known_players.append(player_id)
            self.npc_mem or y.relationships[player_id]== 0.0

            # Рассчитываем изменение отношений
            relationship_change== self._calculate_relationship_change( in teraction_type
            context)
            self.npc_mem or y.relationships[player_id] == relationship_change

            # Обновляем настроение от взаимодействия
            self._update_mood_from_ in teraction( in teraction_type
            relationship_change)

            # Записываем взаимодействие
            interaction_rec or d== {
            'player_id': player_id,
            ' in teraction_type': interaction_type,
            'context': context,
            'relationship_change': relationship_change,
            'timestamp': time.time()
            }
            self.npc_mem or y.conversations.append( in teraction_rec or d)

            # Добавляем память о взаимодействии
            self.add_mem or y('social', {
            'action': 'player_ in teraction',
            'player_id': player_id,
            ' in teraction_type': interaction_type
            }, 'player_ in teraction', {
            'player_id': player_id,
            'relationship_change': relationship_change,
            'new_relationship': self.npc_mem or y.relationships[player_id]
            }, True)

            # Формируем ответ
            response== self._generate_response( in teraction_type, context
            relationship_change)

            logger.debug(f"NPC {self.entity_id} взаимодействовал с игроком {player_id}: { in teraction_type}")
            return response

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка взаимодействия NPC {self.entity_id} с игроком: {e}")
            return {'success': False, 'message': 'Ошибка взаимодействия'}

            def _calculate_relationship_change(self, interaction_type: str
            context: Dict[str, Any]) -> float:
            pass  # Добавлен pass в пустой блок
        """Расчет изменения отношений"""
        base_change== 0.0

        if interaction_type == "greet in g":
            base_change== 0.1
        elif interaction_type == "gift":
            gift_value== context.get('gift_value', 0):
                pass  # Добавлен pass в пустой блок
            base_change== m in(0.5, gift_value / 100.0):
                pass  # Добавлен pass в пустой блок
        elif interaction_type == "trade":
            trade_fairness== context.get('trade_fairness', 0.5)
            base_change== (trade_fairness - 0.5) * 0.3
        elif interaction_type == "quest_completion":
            base_change== 0.2
        elif interaction_type == " in sult":
            base_change== -0.3
        elif interaction_type == "attack":
            base_change== -0.8

        # Модифицируем базовое изменение личностью
        if self.personality.friendl in ess > 0.7:
            base_change == 1.2  # Дружелюбные NPC более отзывчивы
        elif self.personality.friendl in ess < 0.3:
            base_change == 0.8  # Неприветливые NPC менее отзывчивы

        return base_change

    def _update_mood_from_ in teraction(self, interaction_type: str
        relationship_change: float):
            pass  # Добавлен pass в пустой блок
        """Обновление настроения от взаимодействия"""
            mood_change== relationship_change * 0.5  # Настроение меняется медленнее отношений

            if interaction_type == "gift":
            mood_change == 0.1  # Подарки всегда поднимают настроение
            elif interaction_type == " in sult":
            mood_change == 0.2  # Оскорбления портят настроение

            self.emotions.mood== max( - 1.0, m in(1.0
            self.emotions.mood + mood_change))

            def _generate_response(self, interaction_type: str, context: Dict[str, Any]

            relationship_change: float) -> Dict[str, Any]:
            pass  # Добавлен pass в пустой блок
        """Генерация ответа на взаимодействие"""
        response== {
            'success': True,
            'npc_id': self.entity_id,
            'npc_name': self.name,
            ' in teraction_type': interaction_type,
            'relationship_change': relationship_change,
            'current_relationship': self.npc_mem or y.relationships.get(context.get('player_id', ''), 0.0),
            'mood': self.current_mood,
            'behavi or ': self.behavior
        }

        # Генерируем сообщение в зависимости от типа взаимодействия
        if interaction_type == "greet in g":
            if self.current_mood == "happy":
                response['message']== f"Привет! Рад тебя видеть, {context.get('player_name', 'путник')}!"
            elif self.current_mood == "sad":
                response['message']== f"Привет... {context.get('player_name', 'путник')}..."
            else:
                response['message']== f"Здравствуй, {context.get('player_name', 'путник')}."

        elif interaction_type == "gift":
            response['message']== "Спасибо за подарок! Это очень мило с твоей стороны."

        elif interaction_type == "trade":
            if relationship_change > 0:
                response['message']== "Приятно иметь дело с честным торговцем!"
            else:
                response['message']== "Хм, думаю мы могли бы договориться о лучшей цене..."

        elif interaction_type == "quest_completion":
            response['message']== "Отлично! Ты справился с заданием. Спасибо!"

        else:
            response['message']== "Интересно..."

        return response

    def get_dialogue_options(self, player_id: str) -> L is t[Dict[str, Any]]:
        """Получение доступных диалоговых опций"""
            try:
            options== []
            relationship== self.npc_mem or y.relationships.get(player_id, 0.0)

            # Базовые опции
            options.append({
            'id': 'greet in g',
            'text': 'Поздороваться',
            'available': True,
            'relationship_required': -1.0
            })

            # Опции в зависимости от отношений
            if relationship > 0.3:
            options.append({
            'id': 'personal_question',
            'text': 'Спросить о личном',
            'available': True,
            'relationship_required': 0.3
            })

            if relationship > 0.5:
            options.append({
            'id': 'fav or _request',
            'text': 'Попросить услугу',
            'available': True,
            'relationship_required': 0.5
            })

            # Торговые опции для торговцев
            if self. is _merchant:
            options.append({
            'id': 'trade',
            'text': 'Торговать',
            'available': True,
            'relationship_required': 0.0
            })

            # Квестовые опции
            if self.quest_giver and self.available_quests:
            options.append({
            'id': 'quest_offer',
            'text': 'Спросить о заданиях',
            'available': True,
            'relationship_required': 0.0
            })

            return options

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения диалоговых опций NPC {self.entity_id}: {e}")
            return []

            def respond_to_dialogue(self, dialogue_id: str, player_id: str,
            context: Dict[str, Any]== None) -> Dict[str, Any]:
            pass  # Добавлен pass в пустой блок
        """Ответ на диалог"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка ответа на диалог NPC {self.entity_id}: {e}")
            return {'success': False, 'message': 'Ошибка диалога'}

    def add_quest(self, quest_id: str) -> bool:
        """Добавление квеста NPC"""
            try:
            if quest_id not in self.available_quests:
            self.available_quests.append(quest_id)
            self.quest_giver== True

            logger.debug(f"Квест {quest_id} добавлен NPC {self.entity_id}")
            return True

            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка добавления квеста NPC {self.entity_id}: {e}")
            return False

            def complete_quest(self, quest_id: str) -> bool:
        """Завершение квеста NPC"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка завершения квеста NPC {self.entity_id}: {e}")
            return False

    def set_merchant(self, is_merchant: bool, shop_items: L is t[str]== None,
                    prices: Dict[str, int]== None) -> bool:
                        pass  # Добавлен pass в пустой блок
        """Установка NPC как торговца"""
            try:
            self. is _merchant== is_merchant

            if is_merchant:
            self.shop_ in vent or y== shop_items or []
            self.prices== prices or {}
            self.npc_stats.profession== "merchant"

            logger.debug(f"NPC {self.entity_id} стал торговцем")

            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка установки торговца NPC {self.entity_id}: {e}")
            return False

            def get_npc_data(self) -> Dict[str, Any]:
        """Получение данных NPC"""
        base_data== super().get_entity_data()

        # Добавляем специфичные для NPC данные
        npc_data== {
            * * base_data,
            'npc_stats': {
                'reputation': self.npc_stats.reputation,
                ' in fluence': self.npc_stats. in fluence,
                'profession': self.npc_stats.profession,
                'skill_level': self.npc_stats.skill_level,
                'wealth': self.npc_stats.wealth,
                'trade_skill': self.npc_stats.trade_skill
            },
            'personality': {
                'friendl in ess': self.personality.friendl in ess,
                'aggression': self.personality.aggression,
                'curiosity': self.personality.curiosity,
                'loyalty': self.personality.loyalty,
                'talkativeness': self.personality.talkativeness,
                'generosity': self.personality.generosity,
                'honesty': self.personality.honesty,
                'preferred_topics': self.personality.preferred_topics,
                'd is liked_topics': self.personality.d is liked_topics
            },
            'npc_mem or y': {
                'known_players': self.npc_mem or y.known_players,
                'known_npcs': self.npc_mem or y.known_npcs,
                'relationships': self.npc_mem or y.relationships,
                'conversations_count': len(self.npc_mem or y.conversations),
                'trades_count': len(self.npc_mem or y.trades),
                'last_conversation': self.npc_mem or y.last_conversation,
                'last_trade': self.npc_mem or y.last_trade
            },
            'behavi or ': {
                'current_behavi or ': self.behavi or ,
                'current_mood': self.current_mood,
                'current_activity': self.current_activity,
                ' is _busy': self. is _busy,
                ' is _interact in g': self. is _interact in g
            },
            'quests': {
                'available_quests': self.available_quests,
                'completed_quests': self.completed_quests,
                'quest_giver': self.quest_giver
            },
            'trade': {
                ' is _merchant': self. is _merchant,
                'shop_ in vent or y': self.shop_ in vent or y,
                'prices': self.prices
            },
            'schedule': {
                'current_schedule': self.schedule,
                'current_activity': self.current_activity
            }
        }

        return npc_data

    def get_ in fo(self) -> str:
        """Получение информации о NPC"""
            base_ in fo== super().get_ in fo()

            npc_ in fo== (f"\n - -- NPC - - -\n"
            f"Профессия: {self.npc_stats.profession} | Репутация: {self.npc_stats.reputation}\n"
            f"Поведение: {self.behavi or } | Настроение: {self.current_mood}\n"
            f"Активность: {self.current_activity} | Дружелюбие: {self.personality.friendl in ess:.2f}\n"
            f"Известные игроки: {len(self.npc_mem or y.known_players)} | "
            f"Известные NPC: {len(self.npc_mem or y.known_npcs)}\n"
            f"Доступные квесты: {len(self.available_quests)} | "
            f"Торговец: {'Да' if self. is _merchant else 'Нет'}"):
            pass  # Добавлен pass в пустой блок
            return base_ in fo + npc_ in fo