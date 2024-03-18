import logging
import os
from datetime import datetime

from config import PATH_PROJECT


def get_my_logger() -> logging.Logger:
    log_name = f"log_{datetime.now().strftime('%d_%m_%Y')}.log"
    log_path = os.path.join(PATH_PROJECT, "logs", log_name)
    result_logger = logging.getLogger("logging_er")
    result_logger.setLevel("DEBUG")
    file_handler = logging.FileHandler(filename=log_path, encoding="UTF-8")
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(filename)s-%(funcName)s: %(message)s", datefmt="%d.%m.%Y-%H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    result_logger.addHandler(file_handler)
    return result_logger


logger = get_my_logger()
