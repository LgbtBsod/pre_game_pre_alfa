import os
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class BossAI:
    def __init__(self):
        self.model = self._build_model()
        self.model_path = "models/boss_ai.h5"
        self.learning_rate = 0.001  # Очень медленное обучение для босса

        # Проверяем, существует ли уже обученная модель
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)

        # История действий и состояний для обучения
        self.memory = []

    def _build_model(self):
        """Создает и компилирует модель ИИ босса"""
        model = Sequential([
            Dense(64, activation='relu', input_shape=(8,)),
            Dense(32, activation='relu'),
            Dense(3, activation='softmax')  # 3 действия: атака, защита, спецспособность
        ])
        model.compile(optimizer=Adam(learning_rate=self.learning_rate),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def decide_action(self, health_ratio, player_distance, phase):
        """
        Принимает решение на основе текущего состояния
        
        :param health_ratio: доля оставшегося здоровья [0..1]
        :param player_distance: расстояние до игрока
        :param phase: фаза босса (например, 1, 2, 3)
        :return: индекс действия (0 - атака, 1 - защита, 2 - спецспособность)
        """
        state = self._prepare_state(health_ratio, player_distance, phase)
        probabilities = self.model.predict(state, verbose=0)[0]
        return np.argmax(probabilities)

    def _prepare_state(self, health_ratio, player_distance, phase):
        """
        Подготавливает состояние для модели
        
        :param health_ratio: здоровье босса / max_health
        :param player_distance: расстояние до игрока
        :param phase: фаза босса
        :return: numpy array (batch_size=1, input_size=8)
        """
        # Нормализуем параметры
        norm_health = health_ratio
        norm_distance = min(player_distance / 20.0, 1.0)
        phase_value = phase / 3.0

        # Состояние из 8 параметров
        state = [
            norm_health,
            norm_distance,
            phase_value,
            0,  # резерв
            0,  # резерв
            0,  # резерв
            0,  # резерв
            0   # резерв
        ]
        return np.array([state])

    def remember(self, state, action):
        """
        Запоминает состояние и действие для последующего обучения
        
        :param state: словарь с ключами:
                     - health_ratio
                     - player_distance
                     - phase
        :param action: выбранное действие
        """
        self.memory.append((state, action))

    def learn_from_experience(self, reward=0.1):
        """
        Обучает модель на запомненных действиях
        
        :param reward: награда за успешные действия
        """
        if not self.memory:
            return

        states = []
        actions = []

        for state, action in self.memory:
            prepared_state = self._prepare_state(
                state["health_ratio"],
                state["player_distance"],
                state["phase"]
            )
            label = np.zeros(3)
            label[action] = 1 + reward  # усиление успешного действия
            label = label / label.sum()  # нормализация

            states.append(prepared_state[0])
            actions.append(label)

        states = np.array(states)
        actions = np.array(actions)

        self.model.fit(states, actions, epochs=1, verbose=0)
        self.save_model()
        self.memory.clear()

    def save_model(self):
        """Сохраняет модель на диск"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)

    def load_model(self):
        """Загружает модель с диска"""
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
            return True
        return False

    def get_action_name(self, action_index):
        """Возвращает имя действия по его индексу"""
        actions = ["attack", "defend", "special"]
        if 0 <= action_index < len(actions):
            return actions[action_index]
        return "unknown"

    def train_on_feedback(self, feedback):
        """
        Обучает модель на основе обратной связи от среды
        
        :param feedback: словарь с ключами:
                        - "health_ratio" (здоровье босса)
                        - "player_distance" (расстояние до игрока)
                        - "phase" (фаза)
                        - "action" (выбранное действие)
                        - "reward" (-1, 0, +1)
        """
        state = self._prepare_state(
            feedback["health_ratio"],
            feedback["player_distance"],
            feedback["phase"]
        )

        prediction = self.model.predict(state, verbose=0)[0]
        prediction[feedback["action"]] += feedback["reward"] * 0.1
        prediction /= np.sum(prediction)  # нормализация

        self.model.fit(state, prediction.reshape(1, -1), epochs=1, verbose=0)

    def reset_memory(self):
        """Очищает историю действий"""
        self.memory = []