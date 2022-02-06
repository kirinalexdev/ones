"""
Создание информационной базы.

Настройки заданы хардкодом.
Логи пишет только платформа 1С.

Ожидаемый результат:
- Созданна база в каталоге base1.
- Лог файл ib_log1.log создан платформой 1С с результатами создания информационной базы.
"""

from ones import CreationInfobase

def main():
    # Настройки
    base_dir = r'.\base1'
    exename = r'D:\Program Files\1cv8\8.3.10.2753\bin\1cv8.exe'
    platform_version = '8.3.10.2753'
    ib_log_file_name = r'.\ib_log1.log' # В этот лог пишет платформа 1С

    # Выполнение
    ib = CreationInfobase(base_dir)
    ib.set_platform_params(exename, platform_version)
    ib.set_log_ib_params(ib_log_file_name)
    return ib.create_base()

if __name__ == '__main__':
    main()
            

