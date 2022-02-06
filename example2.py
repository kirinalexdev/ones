"""
Создание информационной базы.

Настройки заданы хардкодом.
Логи пишет платформа 1С и скрипт.

Ожидаемый результат:
- Созданна база в каталоге base1.
- Лог файл ib_log1.log создан платформой 1С с результатами создания информационной базы.
- Лог файл log1.log с записями о ходе выполнения скрипта и с параметрами запуска 1С
- Записи на экране о ходе выполнения скрипта 
"""

import logger_
from ones import CreationInfobase, GenInfobaseLogFileName

@logger_.handle_and_log_exceptions
@logger_.log_func
def main():
    # Настройки
    base_dir = r'base1'
    exename = r'D:\Program Files\1cv8\8.3.10.2753\bin\1cv8.exe'
    platform_version = '8.3.10.2753'

    logger_.init_logger('log1.log') # В этот лог пишет скрипт
    
    gen_ib_log_file_name = GenInfobaseLogFileName(full_log_ib_name_prefix = 'ib_log')
    ib_log_file_name = gen_ib_log_file_name.another_file_name() # В этот лог пишет платформа 1С

    # Выполнение
    ib = CreationInfobase(base_dir)
    ib.set_platform_params(exename, platform_version)
    ib.set_log_ib_params(ib_log_file_name)
    
    return ib.create_base()

if __name__ == '__main__':
    main()
            

