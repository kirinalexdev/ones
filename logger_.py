"""Логирование скриптов и функций работы с 1С."""

from collections.abc import Callable
from logging import INFO, DEBUG, Logger, getLogger, StreamHandler, FileHandler, Formatter
import math
import time
import traceback

__all__ = ['init_logger', 'logger']

LOGGER_NAME = 'InformationBase1S'
LOG_FORMAT = '%(asctime)s  %(levelname)-8s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def logger() -> Logger:
    """Получение логгера"""

    return getLogger(LOGGER_NAME)

def init_logger(log_file_name: str='') -> Logger:
    """Nнициализация логгера

    Args:
      log_file_name: str: Nмя лог файла (Default value = '')

    Returns:
      Logger: Логгер
    """

    log = getLogger(LOGGER_NAME)
    log.setLevel(DEBUG)
    log.addHandler(_get_stream_handler())

    if log_file_name:
        log.addHandler(_get_file_handler(log_file_name))

    return log

def _get_file_handler(log_file_name: str) -> FileHandler:
    """Nнициализация записи логирования в файл

    Args:
      log_file_name: str: Nмя лог файла

    Returns:
      FileHandler: Обработчик логирования в файл
    """

    file_handler = FileHandler(log_file_name)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(Formatter(LOG_FORMAT, DATE_FORMAT))

    return file_handler

def _get_stream_handler() -> StreamHandler:
    """Nнициализация записи логирования в файл"""

    stream_handler = StreamHandler()
    stream_handler.setLevel(INFO)
    stream_handler.setFormatter(Formatter(LOG_FORMAT, DATE_FORMAT))

    return stream_handler

def log_func(func: Callable) -> Callable:
    """Декоратор.
    Логирует у функции границы, длительность и т.п.
    """

    def inner(*args, **kwargs):
        log = logger()

        if func.__name__  == 'main':
            message_prefix = 'Скрипт'
        else:
            message_prefix = func.__name__

        log.info(f'{message_prefix}. Началось')

        start_time = time.monotonic()
        func_result = func(*args, **kwargs)

        duration_seconds = math.ceil(time.monotonic() - start_time)
        minutes, seconds = divmod(duration_seconds, 60)

        message = f'{message_prefix}. Выполнилось за {minutes}:{seconds:02} мин:сек'

        if func_result is True:
            log.info(f'{message}. Успешно')
        elif func_result is False:
            log.error(f'{message}. Неуспешно')
        else:
            log.info(f'{message}. Результат функции: {func_result}')

        return func_result

    return inner

def handle_and_log_exceptions(func: Callable) -> Callable:
    """Декоратор.
    Обрабатывает исключения фунции и логирует текст исключения со стэком.
    """

    def inner(*args, **kwargs):
        func_result = None

        try:
            func_result = func(*args, **kwargs)
        except Exception:
            log = logger()
            if log.hasHandlers():
                # exc_info используется в тестах
                log.error(traceback.format_exc(), exc_info=Exception)
            else:
                raise

        return func_result

    return inner
