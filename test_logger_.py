"""Тесты модуля logger_"""

from logging import DEBUG, StreamHandler, FileHandler
import pytest

from logger_ import init_logger, Logger
import logger_

from testfixtures import LogCapture

class TestLogger():
    """"Проверка функции logger."""

    def test_success(self):
        """Успешное выполнение."""

        log = logger_.logger()

        assert isinstance(log, Logger)

class TestInitLogger():
    """"Проверка функции logger."""

    def test_success(self):
        """Успешное выполнение."""

        log = init_logger(r'c:\lg')

        assert isinstance(log, Logger)
        assert log.name == logger_.LOGGER_NAME
        assert log.level == DEBUG
        assert len(log.handlers) == 2

class TestGetFileHandler():
    """"Проверка функции _get_file_handler."""

    def test_success(self):
        """Успешное выполнение."""

        log = logger_._get_file_handler(r'c:\lg')

        assert isinstance(log, FileHandler)
        assert log.level == logger_.DEBUG

class TestGetStreamHandler():
    """"Проверка функции _get_stream_handler."""

    def test_success(self):
        """Успешное выполнение."""

        log = logger_._get_stream_handler()

        assert isinstance(log, StreamHandler)
        assert log.level == logger_.INFO

class TestHandleAndLogExceptionsException():
    """"Проверка декоратора handle_and_log_exceptions."""

    def test_success(self):
        """Успешный результат."""

        func_result = 4
        assert self.for_success(func_result) == func_result

    def test_exception(self):
        """Nсключения."""

        with LogCapture() as logs:
            self.for_exception()
            assert not logs.records[0].exc_info is None

    @logger_.handle_and_log_exceptions
    def for_exception(self):
        """Для проверки исключений"""

        raise

    @logger_.handle_and_log_exceptions
    def for_success(self, func_result):
        """Для проверки успешного результата"""

        return func_result

class TestLogFunc():
    """"Проверка декоратора log_func."""

    def test_common(self):
        """Общее логирование для любых результатов."""

        with LogCapture() as logs:
            self.for_test_log_func()

            msg1 = 'for_test_log_func. Выполнилось за'
            msg1_len = len(msg1)

            assert len(logs.records) == 2
            assert logs.records[0].msg == 'for_test_log_func. Началось'
            assert logs.records[1].msg[:msg1_len] == msg1

    @pytest.mark.parametrize('func_result, msg_log_end',
        [(True, 'Успешно'),
        (False, 'Неуспешно'),
        ('Прочее', 'Прочее')])
    def test_boolean(self, func_result, msg_log_end):
        """Логирование всех вариантов результата."""

        with LogCapture() as logs:
            self.for_test_log_func(func_result)
            msg_len = len(msg_log_end)

            assert logs.records[1].msg[-msg_len:] == msg_log_end

    @logger_.log_func
    def for_test_log_func(self, func_result=None):
        """"Вызываемая функция при тестировании"""

        return func_result
