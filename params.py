"""Формирует объект с параметрами считанными из ini-файла."""

import configparser
import datetime
import os

class Params:
    """Создает объект с атрибутами созданными из параметров файла ini"""

    def __init__(self, ini_file_name: str,
                script_full_file_name: str,
                params_required_version: str):
        """
        Args:
            ini_file_name: str: Полное имя считываемого ini-файла
            script_full_file_name: str: Полное имя файла модуля для на основании которго формируемися имя файла лога.
            params_required_version: str: Ожидаемая версия ini-файла. Nспользуется для проверки.
        """

        config = configparser.ConfigParser()
        if not config.read(ini_file_name, encoding = 'cp1251'):
            raise CouldNotReadParametersFile(
                  f'Не удалось прочитать файл параметров {ini_file_name}')

        for section in config.items():
            for key_value in section[1].items():
                param_name = key_value[0]
                if section[0] != 'common':
                    param_name = section[0] +'_'+ param_name

                setattr(self, param_name, key_value[1])

        if self.ini_version != params_required_version:
            raise WrongParametersFileVersion(
                (f'Неверная версия файла параметров. Требуется: {params_required_version}, '
                f'фактическая: {self.ini_version}, файл: {ini_file_name}'))

        script_file_name = os.path.splitext(os.path.basename(script_full_file_name))[0]
        str_data_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        self.log_file_name = f'{self.log_dir}\\{script_file_name}.{str_data_time}.log'
        self.ib_log_file_name_prefix = f'{self.log_dir}\\{script_file_name}.{str_data_time}.IB'


class CouldNotReadParametersFile(Exception):
    """Nсключение 'Не удалось прочитать файл параметров'"""


class WrongParametersFileVersion(Exception):
    """Nсключение 'Неверная версия файла параметров'"""
