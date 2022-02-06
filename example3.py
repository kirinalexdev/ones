"""
Создание информационной базы.

Настройки заданы в ini-файле.
Логи пишет платформа 1С и скрипт.

Ожидаемый результат:
- Создана база в каталоге base1 и прописана в списке баз как "Example create base".
- Лог файл example3.[датавремя].IB1.log создан платформой 1С с результатами создания информационной базы.
- Лог файл example3.[датавремя].log с записями о ходе выполнения скрипта и с параметрами запуска 1С.
- Записи на экране о ходе выполнения скрипта.
"""

import logger_
from ones import CreationInfobase, GenInfobaseLogFileName
from params import Params

@logger_.handle_and_log_exceptions
@logger_.log_func
def main():
    # Настройки
    params = Params(ini_file_name = r'example3.ini',
                    script_full_file_name = __file__,
                    params_required_version = 'example_create_base_1')

    logger_.init_logger(params.log_file_name) # В этот лог пишет скрипт
    
    gen_ib_log_file_name = GenInfobaseLogFileName(params.ib_log_file_name_prefix)
    ib_log_file_name = gen_ib_log_file_name.another_file_name() # В этот лог пишет платформа 1С

    # Выполнение
    ib = CreationInfobase(params.test_base_dir)
    ib.set_platform_params(params.exename, params.platform_version)
    ib.set_log_ib_params(ib_log_file_name)
    
    return ib.create_base(params.test_base_name)

if __name__ == '__main__':
    main()
            

