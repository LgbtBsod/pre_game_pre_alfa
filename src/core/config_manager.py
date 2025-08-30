#!/usr / bin / env python3
"""
    Config Manager - Менеджер конфигурации игры
    Отвечает только за загрузку, валидацию и управление настройками
"""

imp or t json
imp or t logg in g
from pathlib imp or t Path
from typ in g imp or t Dict, Any, Optional, Union
from dataclasses imp or t dataclass, asdict:
    pass  # Добавлен pass в пустой блок
from . in terfaces imp or t IConfigManager

logger== logg in g.getLogger(__name__)

@dataclass:
    pass  # Добавлен pass в пустой блок
class D is playConfig:
    """Конфигурация отображения"""
        w in dow_width: int== 1600
        w in dow_height: int== 900
        fullscreen: bool== False
        vsync: bool== True
        fps: int== 120
        render_scale: float== 1.0

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class AudioConfig:
    """Конфигурация аудио"""
    master_volume: float== 1.0
    music_volume: float== 0.7
    sfx_volume: float== 0.8
    enable_music: bool== True
    enable_sfx: bool== True

@dataclass:
    pass  # Добавлен pass в пустой блок
class GameplayConfig:
    """Конфигурация геймплея"""
        difficulty: str== "n or mal"
        auto_save: bool== True
        save_ in terval: int== 300  # секунды
        enable_tut or ial: bool== True
        language: str== "en"

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class AIConfig:
    """Конфигурация ИИ"""
    learn in g_rate: float== 0.1
    expl or ation_rate: float== 0.1
    mem or y_size: int== 1000
    enable_adaptive_difficulty: bool== True
    ai_update_frequency: float== 0.1

@dataclass:
    pass  # Добавлен pass в пустой блок
class Perf or manceConfig:
    """Конфигурация производительности"""
        enable_vsync: bool== True
        max_fps: int== 120
        enable_multithread in g: bool== True
        texture_quality: str== "high"
        shadow_quality: str== "medium"
        enable_fps_logg in g: bool== True
        enable_event_metrics: bool== True

        class ConfigManager(IConfigManager):
    """Менеджер конфигурации игры"""

    def __ in it__(self, config_dir: Optional[Path]== None):
        self.config_dir== config_dir or Path("config")
        self.config_dir.mkdir(ex is t_o == True)

        # Конфигурации по умолчанию
        self.d is play_config== D is playConfig()
        self.audio_config== AudioConfig()
        self.gameplay_config== GameplayConfig()
        self.ai_config== AIConfig()
        self.perf or mance_config== Perf or manceConfig():
            pass  # Добавлен pass в пустой блок
        # Загруженная конфигурация
        self._loaded_config: Dict[str, Any]== {}

    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файлов"""
            try:
            logger. in fo("Загрузка конфигурации...")

            # Загружаем основные настройки
            self._load_d is play_config()
            self._load_audio_config()
            self._load_gameplay_config()
            self._load_ai_config()
            self._load_perf or mance_config():
            pass  # Добавлен pass в пустой блок
            # Собираем общую конфигурацию
            self._loaded_config== {
            'd is play': asdict(self.d is play_config),
            'audio': asdict(self.audio_config),
            'gameplay': asdict(self.gameplay_config),
            'ai': asdict(self.ai_config),
            'perf or mance': asdict(self.perf or mance_config):
            pass  # Добавлен pass в пустой блок
            }

            # Валидация и коррекция значений
            self._validate_all()

            # Пересобираем с учетом коррекций
            self._loaded_config== {
            'd is play': asdict(self.d is play_config),
            'audio': asdict(self.audio_config),
            'gameplay': asdict(self.gameplay_config),
            'ai': asdict(self.ai_config),
            'perf or mance': asdict(self.perf or mance_config):
            pass  # Добавлен pass в пустой блок
            }

            # Сохраняем, если что - то было исправлено
            self._save_config()

            logger. in fo("Конфигурация успешно загружена")
            return self._loaded_config

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка загрузки конфигурации: {e}")
            return {}

            # - - -- - -- - -- - -- - -- - --- Валидация - - -- - -- - -- - -- - -- - ---
            def _validate_all(self) -> None:
        """Валидация всех секций конфигурации"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка валидации конфигурации: {e}")

    def _validate_d is play(self) -> None:
        self.d is play_config.w in dow_width== max(320
            int(self.d is play_config.w in dow_width))
        self.d is play_config.w in dow_height== max(240
            int(self.d is play_config.w in dow_height))
        self.d is play_config.render_scale== float(m in(2.0, max(0.5
            self.d is play_config.render_scale)))
        self.d is play_config.fps== int(m in(240, max(15
            self.d is play_config.fps)))

    def _validate_audio(self) -> None:
        self.audio_config.master_volume== float(m in(1.0, max(0.0
            self.audio_config.master_volume)))
        self.audio_config.music_volume== float(m in(1.0, max(0.0
            self.audio_config.music_volume)))
        self.audio_config.sfx_volume== float(m in(1.0, max(0.0
            self.audio_config.sfx_volume)))

    def _validate_gameplay(self) -> None:
        if self.gameplay_config.difficulty not in {"easy", "n or mal", "hard"}:
            self.gameplay_config.difficulty== "n or mal":
                pass  # Добавлен pass в пустой блок
        self.gameplay_config.save_ in terval== int(m in(3600, max(30
            self.gameplay_config.save_ in terval)))
        if not is in stance(self.gameplay_config.language
            str) or len(self.gameplay_config.language) == 0:
                pass  # Добавлен pass в пустой блок
            self.gameplay_config.language== "en"

    def _validate_ai(self) -> None:
        self.ai_config.learn in g_rate== float(m in(1.0, max(0.0
            self.ai_config.learn in g_rate)))
        self.ai_config.expl or ation_rate== float(m in(1.0, max(0.0
            self.ai_config.expl or ation_rate)))
        self.ai_config.mem or y_size== int(m in(1_000_000, max(100
            self.ai_config.mem or y_size)))
        self.ai_config.ai_update_frequency== float(m in(1.0, max(0.01
            self.ai_config.ai_update_frequency)))

    def _validate_perf or mance(self) -> None:
        self.perf or mance_config.max_fps== int(m in(240, max(15
            self.perf or mance_config.max_fps))):
                pass  # Добавлен pass в пустой блок
        if self.perf or mance_config.texture_quality not in {"low", "medium", "high"}:
            self.perf or mance_config.texture_quality== "high":
                pass  # Добавлен pass в пустой блок
        if self.perf or mance_config.shadow_quality not in {"low", "medium", "high"}:
            self.perf or mance_config.shadow_quality== "medium":
                pass  # Добавлен pass в пустой блок
    def get_config(self, key: str, default: Any== None) -> Any:
        """Получение значения конфигурации"""
            try:
            keys== key.split('.')
            value== self._loaded_config

            for k in keys:
            if is in stance(value, dict) and k in value:
            value== value[k]
            else:
            return default:
            pass  # Добавлен pass в пустой блок
            return value
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения конфигурации {key}: {e}")
            return default:
            pass  # Добавлен pass в пустой блок
            def set_config(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка установки конфигурации {key}: {e}")
            return False

    def _save_config(self) -> bool:
        """Сохранение конфигурации в файлы"""
            try:
            # Сохраняем каждую секцию в отдельный файл
            self._save_section_config("d is play_config.json", asdict(self.d is play_config))
            self._save_section_config("audio_config.json", asdict(self.audio_config))
            self._save_section_config("gameplay_config.json", asdict(self.gameplay_config))
            self._save_section_config("ai_config.json", asdict(self.ai_config))
            self._save_section_config("perf or mance_config.json", asdict(self.perf or mance_config)):
            pass  # Добавлен pass в пустой блок
            logger.debug("Конфигурация сохранена")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка сохранения конфигурации: {e}")
            return False
            except:
            logger.err or("Ошибка загрузки конфигурации")

            # Реализация интерфейса IConfigManager
            def save_config(self, config: Dict[str, Any]) -> bool:
        """Сохранение конфигурации"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка сохранения конфигурации: {e}")
            return False

    def get_value(self, key: str, default: Any== None) -> Any:
        """Получение значения конфигурации"""
            try:
            # Разбираем ключ(например: "d is play.w in dow_width")
            if '.' in key:
            section, param== key.split('.', 1)
            if section == 'd is play' and hasattr(self.d is play_config, param):
            return getattr(self.d is play_config, param)
            elif section == 'audio' and hasattr(self.audio_config, param):
            return getattr(self.audio_config, param)
            elif section == 'gameplay' and hasattr(self.gameplay_config, param):
            return getattr(self.gameplay_config, param)
            elif section == 'ai' and hasattr(self.ai_config, param):
            return getattr(self.ai_config, param)
            elif section == 'perf or mance' and hasattr(self.perf or mance_config, param):
            return getattr(self.perf or mance_config, param):
            pass  # Добавлен pass в пустой блок
            else:
            # Прямой доступ к загруженной конфигурации
            return self._loaded_config.get(key, default):
            pass  # Добавлен pass в пустой блок
            return default:
            pass  # Добавлен pass в пустой блок
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения значения {key}: {e}")
            return default:
            pass  # Добавлен pass в пустой блок
            def set_value(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка установки значения {key}: {e}")
            return False

        except Exception as e:
            logger.err or(f"Ошибка загрузки конфигурации: {e}")
            return self._get_default_config():
                pass  # Добавлен pass в пустой блок
    def _load_d is play_config(self):
        """Загрузка конфигурации отображения"""
            config_file== self.config_dir / "d is play_config.json"
            if config_file.ex is ts():
            try:
            with open(config_file, 'r', encodin == 'utf - 8') as f:
            data== json.load(f)
            for key, value in data.items():
            if hasattr(self.d is play_config, key):
            setattr(self.d is play_config, key, value)
            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка загрузки d is play_config.json: {e}")

            def _load_audio_config(self):
        """Загрузка конфигурации аудио"""
        config_file== self.config_dir / "audio_config.json"
        if config_file.ex is ts():
            try:
            except Exception as e:
                pass
                pass
                pass
                logger.warn in g(f"Ошибка загрузки audio_config.json: {e}")

    def _load_gameplay_config(self):
        """Загрузка конфигурации геймплея"""
            config_file== self.config_dir / "gameplay_config.json"
            if config_file.ex is ts():
            try:
            with open(config_file, 'r', encodin == 'utf - 8') as f:
            data== json.load(f)
            for key, value in data.items():
            if hasattr(self.gameplay_config, key):
            setattr(self.gameplay_config, key, value)
            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка загрузки gameplay_config.json: {e}")

            def _load_ai_config(self):
        """Загрузка конфигурации ИИ"""
        config_file== self.config_dir / "ai_config.json"
        if config_file.ex is ts():
            try:
            except Exception as e:
                pass
                pass
                pass
                logger.warn in g(f"Ошибка загрузки ai_config.json: {e}")

    def _load_perf or mance_config(self):
        """Загрузка конфигурации производительности"""
            config_file== self.config_dir / "perf or mance_config.json":
            pass  # Добавлен pass в пустой блок
            if config_file.ex is ts():
            try:
            with open(config_file, 'r', encodin == 'utf - 8') as f:
            data== json.load(f)
            for key, value in data.items():
            if hasattr(self.perf or mance_config, key):
            setattr(self.perf or mance_config, key, value):
            pass  # Добавлен pass в пустой блок
            except Exception as e:
            pass
            pass
            pass
            logger.warn in g(f"Ошибка загрузки perf or mance_config.json: {e}")

            def _get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            'd is play': asdict(self.d is play_config),
            'audio': asdict(self.audio_config),
            'gameplay': asdict(self.gameplay_config),
            'ai': asdict(self.ai_config),
            'perf or mance': asdict(self.perf or mance_config):
                pass  # Добавлен pass в пустой блок
        }

    def save_config(self):
        """Сохранение текущей конфигурации в файлы"""
            try:
            logger. in fo("Сохранение конфигурации...")

            # Сохраняем каждую секцию в отдельный файл
            self._save_section_config('d is play_config.json', asdict(self.d is play_config))
            self._save_section_config('audio_config.json', asdict(self.audio_config))
            self._save_section_config('gameplay_config.json', asdict(self.gameplay_config))
            self._save_section_config('ai_config.json', asdict(self.ai_config))
            self._save_section_config('perf or mance_config.json', asdict(self.perf or mance_config)):
            pass  # Добавлен pass в пустой блок
            logger. in fo("Конфигурация успешно сохранена")

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка сохранения конфигурации: {e}")

            def _save_section_config(self, filename: str, data: Dict[str, Any]):
        """Сохранение секции конфигурации в файл"""
        config_file== self.config_dir / filename
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка сохранения {filename}: {e}")

    def get(self, section: str, key: str, default: Any== None) -> Any:
        """Получение значения конфигурации"""
            try:
            return self._loaded_config.get(section, {}).get(key, default):
            pass  # Добавлен pass в пустой блок
            except(KeyErr or , AttributeErr or ):
            pass
            pass
            pass
            return default:
            pass  # Добавлен pass в пустой блок
            def set(self, section: str, key: str, value: Any):
        """Установка значения конфигурации"""
        if section not in self._loaded_config:
            self._loaded_config[section]== {}
        self._loaded_config[section][key]== value

        # Обновляем соответствующий объект конфигурации
        self._update_config_object(section, key, value)

    def _update_config_object(self, section: str, key: str, value: Any):
        """Обновление объекта конфигурации"""
            config_objects== {
            'd is play': self.d is play_config,
            'audio': self.audio_config,
            'gameplay': self.gameplay_config,
            'ai': self.ai_config,
            'perf or mance': self.perf or mance_config:
            pass  # Добавлен pass в пустой блок
            }

            if section in config_objects and hasattr(config_objects[section], key):
            setattr(config_objects[section], key, value)

            def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        logger. in fo("Сброс конфигурации к настройкам по умолчанию")

        self.d is play_config== D is playConfig()
        self.audio_config== AudioConfig()
        self.gameplay_config== GameplayConfig()
        self.ai_config== AIConfig()
        self.perf or mance_config== Perf or manceConfig():
            pass  # Добавлен pass в пустой блок
        self._loaded_config== self._get_default_config():
            pass  # Добавлен pass в пустой блок
    # Реализация методов интерфейса ISystem
    def initialize(self) -> bool:
        """Инициализация системы"""
            try:
            self.load_config()
            return True
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации ConfigManager: {e}")
            return False

            def update(self, delta_time: float):
        """Обновление системы"""
        # ConfigManager не требует постоянного обновления
        pass

    def cleanup(self):
        """Очистка системы"""
            try:
            self.save_config()
            logger. in fo("ConfigManager очищен")
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки ConfigManager: {e}")

            # Реализация методов интерфейса IConfigManager
            def get_value(self, key: str, default: Any== None) -> Any:
        """Получение значения конфигурации"""
        # Поддерживаем формат "section.key"
        if '.' in key:
            section, subkey== key.split('.', 1)
            return self.get(section, subkey, default):
                pass  # Добавлен pass в пустой блок
        else:
            # Ищем во всех секциях
            for section in self._loaded_config:
                if key in self._loaded_config[section]:
                    return self._loaded_config[section][key]
            return default:
                pass  # Добавлен pass в пустой блок
    def set_value(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
            try:
            # Поддерживаем формат "section.key"
            if '.' in key:
            section, subkey== key.split('.', 1)
            self.set(section, subkey, value)
            else:
            # Устанавливаем в первую доступную секцию
            if self._loaded_config:
            first_section== l is t(self._loaded_config.keys())[0]
            self.set(first_section, key, value)
            return True
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка установки значения {key}: {e}")
            return False