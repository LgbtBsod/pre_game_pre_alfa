# effect.py

from ursina import time


class Effect:
    def __init__(self, duration, cooldown, effect, get_buff):
        # Время в секундах
        self.duration = duration
        self.cooldown = cooldown
        self.effect = effect
        self.buff = {}
        self.get_buff = get_buff

        self.active = False
        self.unavailable = False
        self.start_time = None

    def pull_my_devil_trigger(self):
        """Активирует эффект"""
        self.active = True
        self.start_time = time.time()
        for key in self.effect:
            self.buff[key] = convert_to_num(self.effect[key])
        print(f"Buff activated: {self.buff}")
        self.get_buff(self.buff)

    def update(self):
        """Обновляет состояние эффекта"""
        if self.active:
            if time.time() - self.start_time >= self.duration:
                self.active = False
                self.unavailable = True
                for key in self.buff:
                    self.buff[key] = 0
                print(f"Buff expired: {self.buff}")
                self.get_buff(self.buff)

        if self.unavailable:
            if time.time() - self.start_time >= self.duration + self.cooldown:
                self.unavailable = False