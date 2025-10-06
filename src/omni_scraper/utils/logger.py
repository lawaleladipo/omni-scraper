import logging
import logging.handlers
from pathlib import Path
from ..config.settings import config

def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level_name = config.get('logging.level') or 'INFO'
    log_level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(log_level)

    log_dir = Path(config.base_dir) / 'logs'
    log_dir.mkdir(exist_ok=True, parents=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / config.get('logging.file', 'omni_scraper.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(config.get('logging.format') or "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger(__name__)
