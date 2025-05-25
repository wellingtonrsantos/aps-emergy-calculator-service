import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)  # Pode ajustar para DEBUG em desenvolvimento

# Log format
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Log para arquivo com rotação (5 arquivos de até 1MB cada)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
file_handler.setFormatter(formatter)

# Evitar handlers duplicados
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
