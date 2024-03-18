import os
import sys

from loggers import logger


def restart_program():
    """ Функция перезапускает программу """
    logger.warning("Перезапускаем сервис")
    python = sys.executable
    os.execl(python, python, *sys.argv)
