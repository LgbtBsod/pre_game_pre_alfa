#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

class GameStatistics:
    """Система статистики игры"""
    
    def __init__(self, save_file="statistics.json"):
        self.save_file = save_file
        self.stats = self.load_default_stats()
        self.load_statistics()
        
    def load_default_stats(self):
        """Загрузка статистики по умолчанию"""
        return {
            "game_sessions": 0,
            "total_play_time": 0,
            "enemies_killed": 0,
            "deaths": 0,
            "distance_traveled": 0,
            "attacks_made": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "best_survival_time": 0,
            "best_kill_streak": 0,
            "current_session": {
                "start_time": None,
                "enemies_killed": 0,
                "distance_traveled": 0,
                "attacks_made": 0,
                "damage_dealt": 0,
                "damage_taken": 0,
                "survival_time": 0
            }
        }
        
    def start_session(self):
        """Начало игровой сессии"""
        self.stats["game_sessions"] += 1
        self.stats["current_session"]["start_time"] = datetime.now().isoformat()
        self.reset_current_session()
        
    def end_session(self):
        """Завершение игровой сессии"""
        if self.stats["current_session"]["start_time"]:
            # Обновляем общую статистику
            self.stats["total_play_time"] += self.stats["current_session"]["survival_time"]
            
            # Проверяем рекорды
            if self.stats["current_session"]["survival_time"] > self.stats["best_survival_time"]:
                self.stats["best_survival_time"] = self.stats["current_session"]["survival_time"]
                
            self.save_statistics()
            
    def reset_current_session(self):
        """Сброс текущей сессии"""
        self.stats["current_session"].update({
            "enemies_killed": 0,
            "distance_traveled": 0,
            "attacks_made": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "survival_time": 0
        })
        
    def add_enemy_kill(self):
        """Добавление убийства врага"""
        self.stats["enemies_killed"] += 1
        self.stats["current_session"]["enemies_killed"] += 1
        
    def add_death(self):
        """Добавление смерти"""
        self.stats["deaths"] += 1
        
    def add_distance(self, distance):
        """Добавление пройденного расстояния"""
        self.stats["distance_traveled"] += distance
        self.stats["current_session"]["distance_traveled"] += distance
        
    def add_attack(self):
        """Добавление атаки"""
        self.stats["attacks_made"] += 1
        self.stats["current_session"]["attacks_made"] += 1
        
    def add_damage_dealt(self, damage):
        """Добавление нанесенного урона"""
        self.stats["damage_dealt"] += damage
        self.stats["current_session"]["damage_dealt"] += damage
        
    def add_damage_taken(self, damage):
        """Добавление полученного урона"""
        self.stats["damage_taken"] += damage
        self.stats["current_session"]["damage_taken"] += damage
        
    def update_survival_time(self, time):
        """Обновление времени выживания"""
        self.stats["current_session"]["survival_time"] = time
        
    def get_stat(self, stat_name):
        """Получение статистики"""
        return self.stats.get(stat_name, 0)
        
    def get_current_session_stat(self, stat_name):
        """Получение статистики текущей сессии"""
        return self.stats["current_session"].get(stat_name, 0)
        
    def get_all_stats(self):
        """Получение всей статистики"""
        return self.stats.copy()
        
    def save_statistics(self):
        """Сохранение статистики"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
            
    def load_statistics(self):
        """Загрузка статистики"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)
                    self.merge_stats(loaded_stats)
            except Exception as e:
                print(f"Ошибка загрузки статистики: {e}")
                
    def merge_stats(self, loaded_stats):
        """Слияние загруженной статистики с текущей"""
        for key, value in loaded_stats.items():
            if key in self.stats:
                if isinstance(value, dict) and isinstance(self.stats[key], dict):
                    self.stats[key].update(value)
                else:
                    self.stats[key] = value
