"""Отладочный скрипт для проверки установки Panda3D."""

import sys
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.executable}")

# Проверяем Panda3D
try:
    import panda3d
    logger.info(f"✓ panda3d module found: {panda3d.__file__}")
except ImportError as e:
    logger.error(f"✗ panda3d module not found: {e}")

# Проверяем direct модуль
try:
    import direct
    logger.info(f"✓ direct module found: {direct.__file__}")
except ImportError as e:
    logger.error(f"✗ direct module not found: {e}")

# Проверяем ShowBase
try:
    from direct.showbase.ShowBase import ShowBase
    logger.info("✓ ShowBase successfully imported")
except ImportError as e:
    logger.error(f"✗ ShowBase import failed: {e}")

# Проверяем WindowProperties
try:
    from panda3d.core import WindowProperties
    logger.info("✓ WindowProperties successfully imported")
except ImportError as e:
    logger.error(f"✗ WindowProperties import failed: {e}")

logger.info("\nChecking pip list:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True, check=True)
    if "panda3d" in result.stdout.lower():
        logger.info("✓ Panda3D found in pip list")
    else:
        logger.error("✗ Panda3D not found in pip list")
        logger.info("pip list output:")
        logger.info(result.stdout)
except subprocess.CalledProcessError as e:
    logger.error(f"Error running pip list: {e}")
