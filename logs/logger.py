from logging.handlers import RotatingFileHandler
import logging

formatter = logging.Formatter(
"%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app_logger = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10_000_000,
    backupCount=5,
)

error_logger = RotatingFileHandler(
    "logs/error.log",
    maxBytes=10_000_000,
    backupCount=5,
)

console_logger = logging.StreamHandler()

app_logger.setLevel(logging.INFO)
error_logger.setLevel(logging.ERROR)
console_logger.setLevel(logging.DEBUG)

app_logger.setFormatter(formatter)
error_logger.setFormatter(formatter)
console_logger.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

#что бы случайно не повторить хендлер
if not root_logger.handlers:
    root_logger.addHandler(app_logger)
    root_logger.addHandler(error_logger)
    root_logger.addHandler(console_logger)
