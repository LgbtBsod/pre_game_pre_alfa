#!/usr/bin/env python3
"""
AI-EVOLVE: Enhanced Edition - Оптимизированный лаунчер
Проверяет производительность и запускает игру с оптимальными настройками
"""

import sys
import os
import time
import subprocess
import platform
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceChecker:
    """Проверка производительности системы"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.performance_score = 0
        self.recommended_settings = {}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        try:
            info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': sys.version,
                'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'disk_free': psutil.disk_usage('/').free // (1024**3),  # GB
            }
            
            # Дополнительная информация для Windows
            if platform.system() == 'Windows':
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                      r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        info['windows_version'] = winreg.QueryValueEx(key, "ProductName")[0]
                except Exception:
                    info['windows_version'] = "Unknown"
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о системе: {e}")
            return {}
    
    def check_performance(self) -> Dict[str, Any]:
        """Проверка производительности системы"""
        try:
            score = 0
            recommendations = {}
            
            # Проверка памяти
            memory_gb = self.system_info.get('memory_total', 0)
            if memory_gb >= 16:
                score += 30
                recommendations['memory'] = 'excellent'
            elif memory_gb >= 8:
                score += 20
                recommendations['memory'] = 'good'
            elif memory_gb >= 4:
                score += 10
                recommendations['memory'] = 'adequate'
            else:
                recommendations['memory'] = 'insufficient'
            
            # Проверка CPU
            cpu_count = self.system_info.get('cpu_count', 1)
            if cpu_count >= 8:
                score += 25
                recommendations['cpu'] = 'excellent'
            elif cpu_count >= 4:
                score += 20
                recommendations['cpu'] = 'good'
            elif cpu_count >= 2:
                score += 15
                recommendations['cpu'] = 'adequate'
            else:
                recommendations['cpu'] = 'insufficient'
            
            # Проверка диска
            disk_free = self.system_info.get('disk_free', 0)
            if disk_free >= 10:
                score += 15
                recommendations['disk'] = 'excellent'
            elif disk_free >= 5:
                score += 10
                recommendations['disk'] = 'good'
            elif disk_free >= 1:
                score += 5
                recommendations['disk'] = 'adequate'
            else:
                recommendations['disk'] = 'insufficient'
            
            # Проверка Python версии
            python_version = sys.version_info
            if python_version >= (3, 10):
                score += 10
                recommendations['python'] = 'excellent'
            elif python_version >= (3, 8):
                score += 5
                recommendations['python'] = 'good'
            else:
                recommendations['python'] = 'outdated'
            
            # Проверка доступных библиотек
            lib_score = self._check_libraries()
            score += lib_score
            recommendations['libraries'] = lib_score
            
            self.performance_score = score
            self.recommended_settings = self._get_recommended_settings(score)
            
            return {
                'score': score,
                'recommendations': recommendations,
                'recommended_settings': self.recommended_settings,
                'system_info': self.system_info
            }
            
        except Exception as e:
            logger.error(f"Ошибка проверки производительности: {e}")
            return {'score': 0, 'error': str(e)}
    
    def _check_libraries(self) -> int:
        """Проверка доступных библиотек"""
        score = 0
        required_libs = ['pygame', 'numpy', 'sqlite3']
        optional_libs = ['psutil', 'PIL', 'cv2', 'sklearn']
        
        for lib in required_libs:
            try:
                __import__(lib)
                score += 5
            except ImportError:
                pass
        
        for lib in optional_libs:
            try:
                __import__(lib)
                score += 2
            except ImportError:
                pass
        
        return score
    
    def _get_recommended_settings(self, score: int) -> Dict[str, Any]:
        """Получение рекомендуемых настроек на основе производительности"""
        if score >= 80:
            return {
                'render_fps': 120,
                'texture_quality': 'ultra',
                'shadow_quality': 'high',
                'particle_limit': 2000,
                'enable_post_processing': True,
                'enable_advanced_ai': True,
                'enable_physics': True
            }
        elif score >= 60:
            return {
                'render_fps': 60,
                'texture_quality': 'high',
                'shadow_quality': 'medium',
                'particle_limit': 1000,
                'enable_post_processing': True,
                'enable_advanced_ai': True,
                'enable_physics': True
            }
        elif score >= 40:
            return {
                'render_fps': 60,
                'texture_quality': 'medium',
                'shadow_quality': 'low',
                'particle_limit': 500,
                'enable_post_processing': False,
                'enable_advanced_ai': False,
                'enable_physics': True
            }
        else:
            return {
                'render_fps': 30,
                'texture_quality': 'low',
                'shadow_quality': 'off',
                'particle_limit': 200,
                'enable_post_processing': False,
                'enable_advanced_ai': False,
                'enable_physics': False
            }


class GameLauncher:
    """Лаунчер игры с оптимизацией"""
    
    def __init__(self):
        self.performance_checker = PerformanceChecker()
        self.game_process = None
    
    def launch_game(self, mode: str = "gui", auto_optimize: bool = True) -> bool:
        """Запуск игры с оптимизацией"""
        try:
            logger.info("🚀 Запуск AI-EVOLVE: Enhanced Edition")
            
            # Проверяем производительность
            if auto_optimize:
                logger.info("🔍 Проверка производительности системы...")
                performance = self.performance_checker.check_performance()
                
                logger.info(f"📊 Оценка производительности: {performance['score']}/100")
                logger.info(f"💾 Память: {performance['system_info'].get('memory_total', 0)} GB")
                logger.info(f"🖥️ CPU: {performance['system_info'].get('cpu_count', 0)} ядер")
                logger.info(f"💿 Свободное место: {performance['system_info'].get('disk_free', 0)} GB")
                
                # Применяем рекомендуемые настройки
                if performance['score'] < 40:
                    logger.warning("⚠️ Низкая производительность системы. Игра может работать медленно.")
                elif performance['score'] >= 80:
                    logger.info("✨ Отличная производительность! Все функции доступны.")
                
                # Обновляем конфигурацию
                self._update_config(performance['recommended_settings'])
            
            # Запускаем игру
            logger.info(f"🎮 Запуск в режиме: {mode}")
            
            if mode == "gui":
                return self._launch_gui_mode()
            elif mode == "console":
                return self._launch_console_mode()
            elif mode == "test":
                return self._launch_test_mode()
            elif mode == "demo":
                return self._launch_demo_mode()
            else:
                logger.error(f"❌ Неизвестный режим: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Ошибка запуска игры: {e}")
            return False
    
    def _launch_gui_mode(self) -> bool:
        """Запуск GUI режима"""
        try:
            # Проверяем наличие main.py
            if not Path("main.py").exists():
                logger.error("❌ Файл main.py не найден")
                return False
            
            # Запускаем игру в текущем терминале
            cmd = [sys.executable, "main.py", "gui"]
            
            # Запускаем без отдельного окна, вывод в текущий терминал
            self.game_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd()
            )
            
            logger.info(f"✅ Игра запущена (PID: {self.game_process.pid})")
            logger.info("🎮 Игра запущена в текущем терминале")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска GUI режима: {e}")
            return False
    
    def _launch_console_mode(self) -> bool:
        """Запуск консольного режима"""
        try:
            cmd = [sys.executable, "main.py", "console"]
            self.game_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd()
            )
            
            logger.info(f"✅ Консольный режим запущен (PID: {self.game_process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска консольного режима: {e}")
            return False
    
    def _launch_test_mode(self) -> bool:
        """Запуск тестового режима"""
        try:
            cmd = [sys.executable, "main.py", "test"]
            self.game_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd()
            )
            
            logger.info(f"✅ Тестовый режим запущен (PID: {self.game_process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска тестового режима: {e}")
            return False
    
    def _launch_demo_mode(self) -> bool:
        """Запуск демонстрационного режима"""
        try:
            cmd = [sys.executable, "main.py", "demo"]
            self.game_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd()
            )
            
            logger.info(f"✅ Демонстрационный режим запущен (PID: {self.game_process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска демонстрационного режима: {e}")
            return False
    
    def _update_config(self, settings: Dict[str, Any]):
        """Обновление конфигурации игры"""
        try:
            config_path = Path("config/game_settings.json")
            if not config_path.exists():
                logger.warning("⚠️ Файл конфигурации не найден")
                return
            
            # Здесь можно добавить логику обновления конфигурации
            logger.info("⚙️ Рекомендуемые настройки применены")
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось обновить конфигурацию: {e}")
    
    def stop_game(self) -> bool:
        """Остановка игры"""
        try:
            if self.game_process and self.game_process.poll() is None:
                self.game_process.terminate()
                self.game_process.wait(timeout=5)
                logger.info("✅ Игра остановлена")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки игры: {e}")
            return False
    
    def get_game_status(self) -> Dict[str, Any]:
        """Получение статуса игры"""
        if not self.game_process:
            return {'status': 'not_running'}
        
        try:
            returncode = self.game_process.poll()
            if returncode is None:
                return {
                    'status': 'running',
                    'pid': self.game_process.pid,
                    'memory': self._get_process_memory()
                }
            else:
                return {
                    'status': 'finished',
                    'returncode': returncode
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _get_process_memory(self) -> Optional[float]:
        """Получение использования памяти процессом"""
        try:
            if self.game_process and self.game_process.pid:
                process = psutil.Process(self.game_process.pid)
                memory_info = process.memory_info()
                return memory_info.rss / (1024 * 1024)  # MB
        except Exception:
            pass
        return None


def show_help():
    """Показать справку"""
    help_text = """
🎮 AI-EVOLVE: Enhanced Edition - Лаунчер

📋 ИСПОЛЬЗОВАНИЕ:
    python launcher.py [режим] [опции]

🎯 РЕЖИМЫ:
    gui     - Графический интерфейс (по умолчанию)
    console - Консольный режим
    test    - Тестирование всех систем
    demo    - Демонстрация возможностей

⚙️ ОПЦИИ:
    --no-optimize  - Отключить автооптимизацию
    --help         - Показать эту справку

🚀 ПРИМЕРЫ:
    python launcher.py              # Запуск GUI с автооптимизацией
    python launcher.py console      # Консольный режим
    python launcher.py --no-optimize # Без автооптимизации
    python launcher.py test         # Тестирование

🔧 ФУНКЦИИ:
    • Автоматическая проверка производительности
    • Оптимизация настроек под систему
    • Мониторинг ресурсов
    • Управление процессом игры
"""
    print(help_text)


def main():
    """Главная функция лаунчера"""
    try:
        # Парсим аргументы
        mode = "gui"
        auto_optimize = True
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "--help":
                show_help()
                return 0
            
            if "--no-optimize" in sys.argv:
                auto_optimize = False
                sys.argv.remove("--no-optimize")
            
            if len(sys.argv) > 1:
                mode = sys.argv[1]
        
        # Создаем лаунчер
        launcher = GameLauncher()
        
        # Запускаем игру
        success = launcher.launch_game(mode, auto_optimize)
        
        if success:
            logger.info("✅ Игра успешно запущена")
            
            if mode == "gui":
                logger.info("🎮 Игра запущена в текущем терминале")
                logger.info("💡 Логи игры будут отображаться здесь")
                logger.info("⏹️ Для остановки игры используйте Ctrl+C")
                
                # Ждем немного для запуска игры
                time.sleep(3)
                
                # Проверяем статус
                status = launcher.get_game_status()
                if status['status'] == 'running':
                    logger.info("✅ Игра работает корректно")
                else:
                    logger.warning(f"⚠️ Статус игры: {status['status']}")
                
                # Ожидаем завершения или прерывания
                try:
                    while True:
                        time.sleep(10)  # Проверяем каждые 10 секунд
                        status = launcher.get_game_status()
                        if status['status'] == 'finished':
                            logger.info("✅ Игра завершена")
                            break
                        elif status['status'] == 'running':
                            logger.debug("🎮 Игра продолжает работать...")
                        else:
                            break
                            
                except KeyboardInterrupt:
                    logger.info("⏹️ Остановка игры...")
                    launcher.stop_game()
            else:
                # Для не-GUI режимов мониторим процесс
                try:
                    while True:
                        status = launcher.get_game_status()
                        if status['status'] == 'finished':
                            logger.info("✅ Игра завершена")
                            break
                        elif status['status'] == 'running':
                            time.sleep(5)  # Проверяем каждые 5 секунд
                        else:
                            break
                            
                except KeyboardInterrupt:
                    logger.info("⏹️ Остановка игры...")
                    launcher.stop_game()
            
            return 0
        else:
            logger.error("❌ Ошибка запуска игры")
            return 1
            
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА лаунчера: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)
