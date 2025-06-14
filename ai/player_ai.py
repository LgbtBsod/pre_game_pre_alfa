import os
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class PlayerAI:
    def __init__(self, input_size=20, output_size=5, model_path="models/player_ai.h5"):
        self.input_size = input_size
        self.output_size = output_size
        self.model_path = model_path

        # Проверяем, существует ли уже обученная модель
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
        else:
            self.model = self._build_model()

        # История для обучения
        self.history = {
            "states": [],
            "actions": []
        }

    def _build_model(self):
        """Создает и компилирует модель ИИ"""
        model = Sequential([
            Dense(128, activation='relu', input_shape=(self.input_size,)),
            Dense(64, activation='relu'),
            Dense(self.output_size, activation='softmax')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def decide_action(self, state):
        """
        Принимает решение на основе текущего состояния
        
        :param state: список из input_size параметров
        :return: индекс действия (int)
        """
        state_array = np.array(state).reshape(1, -1)
        probabilities = self.model.predict(state_array, verbose=0)[0]
        return np.argmax(probabilities)

    def remember(self, state, action):
        """
        Запоминает состояние и действие для последующего обучения
        
        :param state: текущее состояние мира
        :param action: выбранное действие
        """
        self.history["states"].append(state)
        self.history["actions"].append(action)

    def learn_from_experience(self):
        """
        Обучает модель на запомненных действиях
        """
        if not self.history["states"]:
            return

        states = np.array(self.history["states"])
        actions = np.array(self.history["actions"])

        # Преобразуем действия в one-hot формат
        labels = np.zeros((len(actions), self.output_size))
        labels[np.arange(len(actions)), actions] = 1

        # Обучаем модель
        self.model.fit(states, labels, epochs=3, verbose=0)

        # Сохраняем прогресс
        self.save_model()

        # Очищаем историю после обучения
        self.history = {
            "states": [],
            "actions": []
        }

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
        actions = ["exploring", "fighting", "collecting", "resting", "avoiding"]
        if 0 <= action_index < len(actions):
            return actions[action_index]
        return "unknown"

    def train_on_feedback(self, feedback):
        """
        Обучает модель на основе обратной связи от среды
        
        :param feedback: словарь с ключами:
                        - "state" (состояние)
                        - "action" (выбранное действие)
                        - "reward" (-1, 0, +1)
        """
        state = np.array(feedback["state"]).reshape(1, -1)
        action = feedback["action"]
        reward = feedback["reward"]

        # Получаем предикт перед обновлением
        prediction = self.model.predict(state, verbose=0)[0]

        # Обновляем вероятность действия на основе награды
        prediction[action] += reward * 0.1
        prediction /= np.sum(prediction)  # Нормализуем

        # Обучаемся на этом примере
        self.model.fit(state, prediction.reshape(1, -1), epochs=1, verbose=0)

    def reset_history(self):
        """Очищает историю действий"""
        self.history = {
            "states": [],
            "actions": []
        }