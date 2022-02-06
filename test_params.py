"""Тесты модуля params"""

import configparser
import pytest

from params import Params, WrongParametersFileVersion, CouldNotReadParametersFile

@pytest.fixture
def ini_file_name(tmp_path, log_dir, ini_version1):
    """"Nмя существующего ini-файла"""

    config = configparser.ConfigParser()
    config.add_section('common')
    config.add_section('base')
    config.set('common', 'param1', 'value1')
    config.set('common', 'log_dir', log_dir)
    config.set('common', 'ini_version', ini_version1)
    config.set('base', 'param2', 'value2')

    file = tmp_path / 'test1.ini'
    file_name = str(file)

    with open(file_name, 'w', encoding = 'cp1251') as config_file:
        config.write(config_file)

    yield file_name

    file.unlink(missing_ok=True)

@pytest.fixture
def log_dir():
    """Nмя произвольного каталога."""

    return r'D:\log_dir1'

@pytest.fixture
def ini_version1():
    """Пример версии ini-файла."""

    return 'ver1'

@pytest.fixture
def ini_version2():
    """Пример версии ini-файла."""

    return 'ver2'

@pytest.fixture
def name_nonexistent_file(tmp_path):
    """"Nмя несуществующего файла"""

    return tmp_path / '1'

class TestParams():
    """Проверка конструктора класса Params"""

    def test_succsess(self, ini_file_name, log_dir, ini_version1):
        """Проверка успешного выполнения."""

        # setUp
        script_file_name = 'scriptname'
        script_full_file_name = 'D:\\' + script_file_name

        log_file_name_left = f'{log_dir}\\{script_file_name}.'

        # test
        params = Params(ini_file_name = ini_file_name,
                            script_full_file_name = script_full_file_name,
                            params_required_version = ini_version1)

        assert params.param1 == 'value1'
        assert params.base_param2 == 'value2'
        assert params.ini_version == ini_version1
        assert params.log_file_name[:len(log_file_name_left)]  == log_file_name_left
        assert params.log_file_name[-4:]  == '.log'
        assert params.ib_log_file_name_prefix[:len(log_file_name_left)] == log_file_name_left
        assert params.ib_log_file_name_prefix[-3:] == '.IB'

    def test_wrong_version(self, ini_file_name, ini_version2):
        """Проверка исключения при неверной версии файла."""

        with pytest.raises(WrongParametersFileVersion):
            Params(ini_file_name = ini_file_name,
                script_full_file_name = r'D:\scriptname',
                params_required_version = ini_version2)

    def test_could_not_read_file(self, name_nonexistent_file, ini_version2):
        """Проверка исключения при неуспешном открытии файла."""

        with pytest.raises(CouldNotReadParametersFile):
            Params(ini_file_name = name_nonexistent_file,
                script_full_file_name = r'D:\scriptname',
                params_required_version = ini_version2)
