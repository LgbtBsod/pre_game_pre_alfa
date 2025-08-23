#!/usr/bin/env python3
"""
Быстрый тест запуска и остановки игры
"""

import subprocess
import time
import sys
import psutil
import signal
import os

def test_game_launch():
    """Тестирует запуск игры и корректную работу"""
    print("🎮 Тестирование запуска игры...")
    
    try:
        # Запускаем игру
        process = subprocess.Popen(
            [sys.executable, "main.py", "gui"],
            cwd=os.getcwd()
        )
        
        print(f"✅ Игра запущена (PID: {process.pid})")
        
        # Ждем немного
        time.sleep(5)
        
        # Проверяем, что процесс работает
        if process.poll() is None:
            print("✅ Игра работает корректно")
            
            # Проверяем память
            try:
                ps_process = psutil.Process(process.pid)
                memory_info = ps_process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                print(f"📊 Использование памяти: {memory_mb:.1f} MB")
                
                cpu_percent = ps_process.cpu_percent(interval=1)
                print(f"🖥️ Использование CPU: {cpu_percent:.1f}%")
                
            except Exception as e:
                print(f"⚠️ Не удалось получить статистику: {e}")
        else:
            print(f"❌ Игра завершилась с кодом: {process.returncode}")
            return False
        
        # Останавливаем процесс
        print("⏹️ Остановка игры...")
        process.terminate()
        
        # Ждем завершения
        try:
            process.wait(timeout=5)
            print("✅ Игра корректно остановлена")
        except subprocess.TimeoutExpired:
            print("⚠️ Принудительное завершение...")
            process.kill()
            process.wait()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_launcher():
    """Тестирует лаунчер"""
    print("\n🚀 Тестирование лаунчера...")
    
    try:
        # Запускаем лаунчер без запуска игры (с модификацией)
        # Можно добавить специальный флаг для тестирования
        process = subprocess.Popen(
            [sys.executable, "launcher.py", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=10)
        
        if process.returncode == 0:
            print("✅ Лаунчер работает корректно")
            if "AI-EVOLVE" in stdout:
                print("✅ Справка отображается корректно")
            return True
        else:
            print(f"❌ Лаунчер завершился с ошибкой: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования лаунчера: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Быстрое тестирование запуска AI-EVOLVE")
    print("=" * 50)
    
    # Тест лаунчера
    launcher_ok = test_launcher()
    
    # Тест игры
    game_ok = test_game_launch()
    
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТЫ:")
    print(f"   Лаунчер: {'✅' if launcher_ok else '❌'}")
    print(f"   Игра: {'✅' if game_ok else '❌'}")
    
    if launcher_ok and game_ok:
        print("\n🎉 Все тесты пройдены! Игра готова к использованию.")
        print("\n🚀 Рекомендуемые команды:")
        print("   python launcher.py    # Запуск через лаунчер")
        print("   python main.py gui    # Прямой запуск")
    else:
        print("\n⚠️ Найдены проблемы. Проверьте логи.")
    
    return 0 if (launcher_ok and game_ok) else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
