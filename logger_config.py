
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'ENDC': '\033[0m'       # Reset
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
        return super().format(record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler with rotation (max 5MB per file, keep 3 backup files)
    file_handler = RotatingFileHandler(
        'debug.log',
        maxBytes=5*1024*1024,
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
