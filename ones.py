""""Библиотека работы с платформой 1С путем запуска через командную строку."""

from enum import Enum
from configparser import ConfigParser
import subprocess
from packaging import version

from logger_ import logger
import logger_

__all__ = ['CreationInfobase', 'Designer', 'Enterprise',
           'GenInfobaseLogFileName', 'set_base_parameters_in_list_file',
           'SupportRules', 'SQLYearOffsets', 'FileDBFormats', 'DBServerTypes', 'ConfigDumpFormats']


class SupportRules(Enum):
    """Правила поддержки для объектов при создании хранилища.

    Attributes:
      OBJECT_NOT_EDITABLE: str: Объект поставщика не редактируется
      OBJECT_IS_EDITABLE_SUPPORT_ENABLED: str: Объект поставщика редактируется с сохранением поддержки
      OBJECT_NOT_SUPPORTED: str: Объект поставщика снят с поддержки
    """

    OBJECT_NOT_EDITABLE = 'ObjectNotEditable'
    OBJECT_IS_EDITABLE_SUPPORT_ENABLED = 'ObjectIsEditableSupportEnabled'
    OBJECT_NOT_SUPPORTED = 'ObjectNotSupported'


class SQLYearOffsets(Enum):
    """Смещения дат, используемые для хранения дат в Microsoft SQL Server.

    Attributes:
      ZERO: str: 0
      TWO_THOUSAND: str: 2000
    """

    ZERO = '0'
    TWO_THOUSAND = '2000'


class FileDBFormats(Enum):
    """Форматы, в которых будет создаваться база данных в файловом варианте.

    Attributes:
      F_8_2_14: str: 8.2.14
      F_8_3_8: str: 8.3.8
    """

    F_8_2_14 = '8.2.14'
    F_8_3_8  = '8.3.8'


class DBServerTypes(Enum):
    """Типы сервера баз данных.

    Attributes:
      MS_SQL_SERVER: str: MSSQLServer
      POSTGRE_SQL: str: PostgreSQL
      IBM_DB2: str: IBMDB2
      ORACLE_DATABASE: str: OracleDatabase
    """

    MS_SQL_SERVER = 'MSSQLServer'
    POSTGRE_SQL = 'PostgreSQL'
    IBM_DB2 = 'IBMDB2'
    ORACLE_DATABASE = 'OracleDatabase'


class ConfigDumpFormats(Enum):
    """Форматы выгрузки конфигурации в файлы.

    Attributes:
      PLAIN: str: Плоский формат. https://its.1c.ru/db/v8310doc/bookmark/dev/TI000001620
      HIERARCHICAL: str: Nерархический формат. https://its.1c.ru/db/v8310doc/bookmark/dev/TI000001619
    """

    PLAIN = 'Plain'
    HIERARCHICAL = 'Hierarchical'


class RunInfobase:
    """Абстрактный класс по запуску 1С."""

    def __init__(self, 
                dir_: str ='',
                server: str='', infobase: str='',
                ws_connection_string: str=''):
        """
        Args:
          dir_: str: Каталог файловой базы (Default value = '')
          server: str: Nмя сервера 1С (Default value = '')
          infobase: str: Nмя базы на сервере 1С (Default value = '')
          ws_connection_string: Адрес базы на веб-сервере (Default value = '')
        """

        self._dir = dir_
        self._server = server
        self._infobase = infobase
        self._ws_connection_string = ws_connection_string
        self.set_platform_params('')
        self.set_auth_params(user='')
        self.set_log_ib_params()
        self.set_dialogs_settings()
        self.set_other_params()

    def set_auth_params(self, user: str, password: str='', use_os_auth: bool=True):
        """Установка параметров авторизации.

        Args:
          user: str: Nмя пользователя базы 1С
          password: str: Пароль пользователя базы 1С (Default value = '')
          use_os_auth: bool: Установка обязательного применения аутентификации ОС при старте 1С (Default value = True)
        """

        self._user = user
        self._password = password
        self._use_os_auth = use_os_auth

    def set_dialogs_settings(self, visible: bool=False,
                            disable_startup_messages: bool=True,
                            disable_startup_dialogs: bool=True):
        """Установка параметров диалоговых окон.

        Args:
          visible: bool: На время работы конфигуратора открывается окно заставки (Default value = False)
          disable_startup_messages: bool: Подавляет стартовое сообщение 
                                          Конфигурация базы данных не соответствует сохраненной конфигурации.
                                          Продолжить? (Default value = True)
          disable_startup_dialogs: bool: Отключает вызов стартового диалога и диалогов аутентификации (Default value = True)
        """

        self._visible = visible
        self._disable_startup_messages = disable_startup_messages
        self._disable_startup_dialogs = disable_startup_dialogs

    def set_log_ib_params(self, gen_ib_log_file_name : str='',
                                truncate_log_ib: bool=True,
                                result_file_name: str=''):
        """Установка параметров логирования платформой.

        Args:
          gen_ib_log_file_name : str: Полное имя файла для вывода служебных сообщений 1С (Default value = '')
          truncate_log_ib: bool: Очищать файл перед записью в него (Default value = True)
          result_file_name: str: Полное имя файла для записи результата работы конфигуратора в файл. 
                                Результат ‑ число (0 ‑ в случае успеха) (Default value = '')
        """

        self._ib_log_file_name = gen_ib_log_file_name
        self._truncate_log_ib = truncate_log_ib
        self._result_file_name = result_file_name

    def set_platform_params(self, exename: str, platform_version: str=''):
        """Установка разных параметров запуска платформы.

        Args:
          exename: str: Полное имя исполняемого файла платформы 1С
          platform_version: str: Nспользуемая версия платформы. Может использоваться для разных целей. (Default value = '')
        """

        self._exename = exename
        self._platform_version = platform_version

    def set_other_params(self, access_code: str='', locale: str='', other_params: list=None):
        """Установка прочих параметров.

        Args:
          access_code: str:  (Default value = '')
          locale: str:  (Default value = '')
          other_params: list: Произвольные параметры, которые будут использованы в коммандной строке запуска 1С (Default value = None)
        """

        self._access_code = access_code
        self._locale = locale
        self._other_params = other_params if other_params else []

    def _subprocess_run(self, params: list):
        """Обертка для удобства мокирования.

        Args:
          params: list: Параметры запуска согласно требования функции subprocess.run

        Returns:
          completed_process.returncode: Код возвращаемый фукцией subprocess.run
        """

        completed_process = subprocess.run(params)
        return completed_process.returncode

    def _execute_command(self, params: list) -> int:
        """Непосредственно запуск 1С.

        Args:
          params: list: Параметры запуска согласно требования функции subprocess.run

        Returns:
          bool: Успешно/неуспешно выполнение
        """

        params.insert(0, self._exename)

        logger().debug('Параметры запуска: ' + ' '.join(params))

        return_code = self._subprocess_run(params)
        result = (return_code == 0)

        if not result:
            self._log_1s_execution_error(return_code, self._ib_log_file_name)

        return result

    def _log_1s_execution_error(self, return_code: int, gen_ib_log_file_name: str=''):
        """Логирование ошибки выполнения 1С в том числе из лога создавамого платформой 1С.

        Args:
          return_code: int: Результат возвращаемый платформой 1С после выполнения
          gen_ib_log_file_name: str: Полное имя файла для вывода служебных сообщений 1С (Default value = '')
        """

        content_file_log = ''
        error_prefix = 'Для получения текста ошибки'
        error_text = ''

        if gen_ib_log_file_name:
            # До 8.3.18 файл вывода служебных сообщений, который указывается в параметре /Out
            # у командной строки запуска клиентских приложений и конфигуратора, формировался
            # в системной кодировке операционной системы.
            #
            # №сточник:
            # https://dl04.1c.ru/content/Platform/8_3_18_1363/1cv8upd_8_3_18_1363.htm#a92fdc30-5e0a-11ea-8371-0050569f678a
            if (not self._platform_version or
             version.parse(self._platform_version) >= version.parse('8.3.18')):
                version_encoding = 'utf_8_sig'
            else:
                version_encoding = 'cp1251'

            try:
                with open(gen_ib_log_file_name, 'r', encoding=version_encoding) as file:
                    content_file_log = file.read().strip()

            except FileNotFoundError:
                error_text = f'{error_prefix} не найден файл лога 1С: {gen_ib_log_file_name}'

            except PermissionError:
                error_text = (f'{error_prefix} не хватило прав '
                             f'для открытия файла лога 1С: {gen_ib_log_file_name}')

            except Exception as ex:
                error_text = (f'{error_prefix} не удалось прочитать файла лога 1С: '
                             f'{gen_ib_log_file_name}. Ошибка: {ex}')

        logger().error(f'Код результата: {return_code}: {content_file_log} {error_text}')

    def _ib_connection_string(self) -> str:
        """Возвращает строку соединения для параметра /IBConnectionString,
        который задает строку соединения с информационной базой."""

        # TODO возможно есть смысл уйти от параметра /IBConnectionString 
        # и переделать на параметры /F /S и т.п, т.к. в текущем варианте есть ограничения -
        # - не вижу возможност экранирования апострофа, кавычек.
        # Например параметре FILE= сейчас нельзя использовать апострофы.

        ib_connection_string = ''

        if self._dir:
            ib_connection_string += f"FILE='{self._dir}';"

        elif self._server:
            ib_connection_string += f"Srvr='{self._server}';"
            ib_connection_string += f"Ref='{self._infobase}';"

        elif self._ws_connection_string:
            ib_connection_string += f"ws='{self._ws_connection_string}';"
        

        if self._user:
            ib_connection_string += f"Usr='{self._user}';"

        if self._password:
            ib_connection_string += f"Pwd='{self._password}';"

        if self._locale:
            ib_connection_string += f"Locale={self._locale};"

        return ib_connection_string

    def _common_run_parameters(self) -> list:
        """Возвращает список общих параметров запуска 1С."""

        params  = list()

        if self._access_code:
            # это работает и для DESIGNER и для ENTERPRISE
            params.append(f"/UC {self._access_code}")

        if not self._use_os_auth:
            params.append('/WA-')

        if self._visible:
            params.append('/Visible')

        if self._disable_startup_messages:
            params.append('/DisableStartupMessages')

        if self._disable_startup_dialogs:
            params.append('/DisableStartupDialogs')

        if self._ib_log_file_name:
            params.append(f"/Out {self._ib_log_file_name}")

            if not self._truncate_log_ib:
                params.append('-NoTruncate')

        if self._result_file_name:
            params.append(f"/DumpResult {self._result_file_name}")

        for param in self._other_params:
            params.append(param)

        return params


class CreationInfobase(RunInfobase):
    """Создание информационной базы."""

    def __init__(self, dir_: str ='', server: str='', infobase: str=''):
        super().__init__(dir_, server, infobase)
        """
        Args:
          dir_: str: Каталог файловой базы (Default value = '')
          server: str: Nмя сервера 1С (Default value = '')
          infobase: str: Nмя базы на сервере 1С (Default value = '')
        """

        self.set_file_db_params()
        self.set_server_db_params(db_server_type=None, db_server_name='', database='')
        self.set_claster_params()

    @logger_.log_func
    def create_base(self, base_name_in_the_list: str='', template: str='') -> bool:
        """Создание базы.

        Args:
          base_name_in_the_list: str: Полное имя файла списка баз 1С.
                                      Речь про файл ibases.v8i (Default value = '')
          template: str: Полное имя файла шаблона на основании которого создается база 1С.
                         В качестве шаблонов могут быть файлы конфигурации (.cf)
                         или файлы выгрузки информационной базы (.dt). (Default value = '')

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()

        if base_name_in_the_list:
            params.append(f'/AddInList {base_name_in_the_list}')

        if template:
            params.append(f'/UseTemplate {template}')

        result = self._execute_command(params)

        return result

    def set_file_db_params(self, file_db_format: FileDBFormats=None):
        """Установка параметров файловой базы.

        Args:
          file_db_format: FileDBFormats: Формат, в котором будет создаваться база данных 
                                         в файловом варианте (Default value = None)
        """

        self._file_db_format = file_db_format

    def set_server_db_params(self, db_server_type: DBServerTypes,
                      db_server_name: str,
                      database: str,
                      db_user: str = '',
                      db_password: str = '',
                      sql_year_offset: SQLYearOffsets = None,
                      create_db_if_not_exist: bool = False):
        """Установка параметров серверной базы.

        Args:
          db_server_type: DBServerTypes: Тип используемого сервера баз данных
          db_server_name: str: Nмя сервера баз данных
          database: str: Nмя базы данных в сервере баз данных.
          db_user: str: Nмя пользователя сервера баз данных (Default value = '')
          db_password: str: Пароль пользователя сервера баз данных (Default value = '')
          sql_year_offset: SQLYearOffsets: Смещение дат, используемое для хранения дат в Microsoft SQL Server (Default value = None)
          create_db_if_not_exist: bool: Создать базу данных в случае ее отсутствия (Default value = False)
        """

        self._db_server_type = db_server_type
        self._db_server_name = db_server_name
        self._database = database
        self._db_user = db_user
        self._db_password = db_password
        self._sql_year_offset = sql_year_offset
        self._create_db_if_not_exist = create_db_if_not_exist

    def set_claster_params(self,
                           deny_scheduled_jobs: bool = False,
                           cluster_administrator_user: str = '',
                           cluster_administrator_password: str = ''):
        """Установка параметров кластера.

        Args:
          deny_scheduled_jobs: bool: В созданной базе запретить выполнение регламентных созданий (Default value = False)
          cluster_administrator_user: str: Nмя администратора кластера, в котором должен быть создан начальный образ (Default value = '')
          cluster_administrator_password: str: Пароль администратора кластера (Default value = '')
        """

        self._deny_scheduled_jobs = deny_scheduled_jobs
        self._cluster_administrator_user = cluster_administrator_user
        self._cluster_administrator_password = cluster_administrator_password

    def _ib_connection_string(self) -> str:
        """Возвращает строку соединения для параметра /IBConnectionString, для создания базы."""

        ib_connection_string = super()._ib_connection_string()

        if self._db_server_type:
            ib_connection_string += f"DBMS={self._db_server_type.value};"

        if self._db_server_name:
            ib_connection_string += f"DBSrvr='{self._db_server_name}';"

        if self._database:
            ib_connection_string += f"DB='{self._database}';"

        if self._db_user:
            ib_connection_string += f"DBUID='{self._db_user}';"

        if not self._sql_year_offset is None:
            ib_connection_string += f"SQLYOffs={self._sql_year_offset.value};"

        if self._db_password:
            ib_connection_string += f"DBPwd='{self._db_password}';"

        if self._create_db_if_not_exist:
            ib_connection_string += "CrSQLDB=Y;"

        if self._deny_scheduled_jobs:
            ib_connection_string += "SchJobDn=Y;"

        if self._cluster_administrator_user:
            ib_connection_string += f"SUsr='{self._cluster_administrator_user}';"

        if self._cluster_administrator_password:
            ib_connection_string += f"SPwd='{self._cluster_administrator_password}';"

        if not self._file_db_format is None:
            ib_connection_string += f"DBFormat={self._file_db_format.value};"

        return ib_connection_string

    def _common_run_parameters(self) -> list:
        """Возвращает список общих параметров создания базы."""

        params = super()._common_run_parameters()

        # CREATEINFOBASE Должен быть в начале, иначе будет ошибка 'Неопределен режим запуска'
        # ib_connection_string Должен быть следующим параметром за CREATEINFOBASE
        params.insert(0, 'CREATEINFOBASE')
        params.insert(1, self._ib_connection_string())

        return params

class Designer(RunInfobase):
    """Работа с информационной базой из конфигуратора."""

    def __init__(self, dir_: str ='', server: str='', infobase: str=''):
        """
        Args:
          dir_: str: Каталог файловой базы (Default value = '')
          server: str: Nмя сервера 1С (Default value = '')
          infobase: str: Nмя базы на сервере 1С (Default value = '')
        """

        super().__init__(dir_, server, infobase)
        self.set_repo_params(dir_='', user='')
        self.set_update_db_cfg_params()

    @logger_.log_func
    def load_cfg(self, file_name_cf: str) -> bool:
        """Загрузка конфигурации из файла.

        Args:
          file_name_cf: str: имя cf или cfe файла

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        params.append(f'/LoadCfg {file_name_cf}')

        result = self._execute_command(params)

        return result

    @logger_.log_func
    def dump_config_to_files(self,
                             dir_: str,
                             update: bool = True,
                             force: bool = True,
                             format_: ConfigDumpFormats = None) -> bool:
        """Выгрузка конфигурации в файлы.

        Args:
          dir_: str: Каталог выгрузки
          update: bool: Выполнить обновление ранее совершенной выгрузки (Default value = True)
          force: bool: Если текущая версия формата выгрузки не совпадает с версией формата
                       в файле версий, будет выполнена полная выгрузка. Возможно совместное
                       использование с параметром update (Default value = True)
          format_: ConfigDumpFormats: Формат выгрузки конфигурации в файлы (Default value = None)

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        params.append(f'/DumpConfigToFiles {dir_}')

        if format_:
            params.append(f'-Format {format_.value}')

        if update:
            params.append('–update')

        if force:
            params.append('–force')

        result = self._execute_command(params)

        return result

    @logger_.log_func
    def dump_repo_to_file(self, file_name: str, version_number: str='') -> bool:
        """Сохранение конфигурации из хранилища в файл.

        Args:
          file_name: str: Nмя cf файла
          version_number: str: Номер версии хранилиша, если номер версии не указан, или равен -1, 
                               будет сохранена последняя версия (Default value = '')

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        params.append(f"/ConfigurationRepositoryDumpCfg {file_name}")

        if version_number:
            params.append(f'-v {version_number}')

        result = self._execute_command(params)

        return result

    @logger_.log_func
    def update_from_repo(self,
                         version_: int = 0,
                         revised: bool = False,
                         force: bool = False,
                         objects: str = '') -> bool:
        """Обновление конфигурации из хранилища.

        Args:
          version_: int: Номер версии в хранилище конфигурации. В том случае, если конфигурация подключена к хранилищу,
                         то номер версии (если он указан) игнорируется и будет получена актуальная версия конфигурации хранилища.
                         Если конфигурация не подключена к хранилищу, то выполняется получение указанной версии,
                         а если версия не указана (или значение равно -1) будет получена актуальная версия конфигурации 
                         (Default value = 0)
          revised: bool: Получать захваченные объекты, если потребуется.
                         Если конфигурация не подключена к хранилищу, то параметр игнорируется (Default value = False)
          force: bool: Если при пакетном обновлении конфигурации из хранилища должны быть получены новые 
                       объекты конфигурации или удалиться существующие, указание этого параметра 
                       свидетельствует о подтверждении пользователем описанных выше операций. 
                       Если параметр не указан ‑ действия выполнены не будут (Default value = False)
          objects: str: Путь к файлу со списком объектов, которые будут участвовать в операции. 
                        Если файл указан – в операции участвуют только указанные в файле объекты,
                        в противном случае участвует вся конфигурация. 
                        Описание формата файла см. здесь https://its.1c.ru/db/v8310doc#bookmark:adm:TI000000698
                        (Default value = '')

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()

        params.append('/ConfigurationRepositoryUpdateCfg')

        if version_ != 0:
            params.append(f'-v {version_}')

        if revised:
            params.append('-revised')

        if force:
            params.append('-force')

        if objects:
            params.append(f'-objects "{objects}"')

        if self._update_db_cfg_params['update_db_cfg']:
            params.append('/UpdateDBCfg')

            if self._update_db_cfg_params['server']:
                params.append('-Server')

        result = self._execute_command(params)

        return result

    @logger_.log_func
    def create_repo(self,
     allow_configuration_changes: bool = True,
     changes_allowed_rule: SupportRules = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED,
     changes_not_recommended_rule: SupportRules = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED,
     no_bind: bool = False) -> bool:
        """Создание хранилища.

        Args:
          allow_configuration_changes: bool: Если конфигурация находится на поддержке без возможности изменения,
                                             будет включена возможность изменения. (Default value = True)
          changes_allowed_rule: SupportRules: Устанавливает правило поддержки для объектов, для которых 
                                              изменения разрешены поставщиком. 
                                              (Default value = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED)
          changes_not_recommended_rule: SupportRules: Устанавливает правило поддержки для объектов, для которых
                                                      изменения не рекомендуются поставщиком
                                                      (Default value = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED)
          no_bind: bool: К созданному хранилищу подключение выполнено не будет (Default value = False)

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        params.append('/ConfigurationRepositoryCreate')

        if allow_configuration_changes:
            params.append('-AllowConfigurationChanges')
            params.append(f'-ChangesAllowedRule {changes_allowed_rule.value}')
            params.append(f'-ChangesNotRecommendedRule {changes_not_recommended_rule.value}')

        if no_bind:
            params.append('-NoBind')

        result = self._execute_command(params)

        return result

    @logger_.log_func
    def set_repo_label(self, label: str, version_: int=0, comment: str='') -> bool:
        """Установка метки на версию хранилища.

        Args:
          label: str: Текст метки 
          version_: int: Номер версии хранилища (Default value = 0)
          comment: str: Текст комментария к устанавливаемой метке (Default value = '')

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        params.append('/ConfigurationRepositorySetLabel')
        params.append(f'-name {label}') # TODO В документации указано помещать значение в двойных кавычках. 
                                        # Не понял как это сделать не сломав значение.
        

        if version_ != 0:
            params.append(f'-v {version_}')

        for line in comment.splitlines():
            params.append(f'-comment {line}') # TODO В документации указано помещать значение в двойных кавычках.
                                              # Не понял как это сделать не сломав значение.

        result = self._execute_command(params)

        return result

    def set_repo_params(self, dir_: str, user: str, password: str=''):
        """Установка параметров хранилища.

        Args:
          dir_: str: Каталог хранилища
          user: str: Nмя пользователя хранилища
          password: str: Пароль пользователя хранилища (Default value = '')
        """

        self._repo_dir = dir_
        self._repo_user = user
        self._repo_password = password

    def set_update_db_cfg_params(self, update_db_cfg: bool=False, server: bool=True):
        """Установка параметров обновления базы.
        Параметры сделаны словарем, а не отдельными атрибутами т.е. у параметра /UpdateDBCfg
        платформа допускает много доп. параметров и удобнее их хранить вместе.

        Args:
          update_db_cfg: bool: Выполнить обновление конфигурации базы данных (Default value = False)
          server: bool: Обновление будет выполняться на сервере (Default value = True)
        """

        self._update_db_cfg_params = {'update_db_cfg': update_db_cfg, 'server': server}

    def _common_run_parameters(self) -> list:
        """Возвращает список общих параметров работы с базой из конфгуратора."""

        # DESIGNER Должен быть в начале, иначе будет ошибка 'Неопределен режим запуска'
        params = super()._common_run_parameters()
        params.insert(0, 'DESIGNER')
        params.append(f'/IBConnectionString {self._ib_connection_string()}')

        if self._repo_dir:
            params.append(f"/ConfigurationRepositoryF {self._repo_dir}")
            params.append(f'/ConfigurationRepositoryN {self._repo_user}')

        if self._repo_password:
            params.append(f'/ConfigurationRepositoryP {self._repo_password}')

        return params

class Enterprise(RunInfobase):
    """Работа с информационной базой в режиме предприятия."""

    def __init__(self,
                dir_: str ='',
                server: str='',
                infobase: str='',
                ws_connection_string: str=''):
        """
        Args:
          dir_: str: Каталог файловой базы (Default value = '')
          server: str: Nмя сервера 1С (Default value = '')
          inыfobase: str: Nмя базы на сервере 1С (Default value = '')
          ws_connection_string: Адрес базы на веб-сервере (Default value = '')
        """
                
        super().__init__(dir_, server, infobase, ws_connection_string)
        self.set_other_params()

    @logger_.log_func
    def run(self) -> bool:
        """Запуск 1С

        Returns:
          bool: Успешно/неуспешно
        """

        params = self._common_run_parameters()
        result = self._execute_command(params)

        return result

    def set_other_params(self, 
                        access_code: str = '', 
                        locale: str = '', 
                        other_params: list = None, 
                        launch_param: str = ''):
        """Установка прочих параметров.

        Args:
          access_code: str: Код доступа для установкм соединения с базой, 
                            на которую установлена блокировка установки соединений. (Default value = '')
          locale: str: Язык (страна), который будет использован при открытии или создании информационной базы (Default value = '')
          other_params: list: Произвольные параметры, которые будут использованы в коммандной строке запуска 1С (Default value = None)
          launch_param: str: Параметр передаваемый в прикладное решение (Default value = '')
        """

        super().set_other_params(access_code, locale, other_params)
        self._launch_param = launch_param

    def _common_run_parameters(self) -> list:
        """Возвращает список общих параметров работы с базой в режиме предприятия."""

        # ENTERPRISE Должен быть в начале, иначе будет ошибка 'Неопределен режим запуска'
        # /IBConnectionString должен быть после ENTERPRISE
        # иначе ошибка 'Неопределена информационная база'
        params = super()._common_run_parameters()
        params.insert(0, 'ENTERPRISE')
        params.insert(1, f'/IBConnectionString {self._ib_connection_string()}')

        if self._launch_param:
            params.append(f'/C {self._launch_param}')

        return params

class GenInfobaseLogFileName:
    """Формирование полного имени файла лога в который будет писать платформа 1С.
    Генерирует числовой постфикс для каждого последующего имени.
    """

    def __init__(self, full_log_ib_name_prefix: str):
        """
        Args:
          full_log_ib_name_prefix: str: Префикс полного имени файла лога. Например c:\temp\filename
        """

        self._configurator_run_number = 0
        self._full_log_ib_name_prefix = full_log_ib_name_prefix

    def another_file_name(self) -> str:
        """Возвращает очередное имя файла лога."""

        self._configurator_run_number += 1
        return f'{self._full_log_ib_name_prefix}{self._configurator_run_number}.log'


@logger_.log_func
def set_base_parameters_in_list_file(file_name_list_base: str,
                                    base_name_in_the_list: str,
                                    additional_parameters: str = '',
                                    platform_version: str = '') -> bool:
    """Устанавливает параметры запуска информационной базы в файле ibases.v8i

    Args:
      file_name_list_base: str: Полное имя файла списка баз 1С - ibases.v8i
      base_name_in_the_list: str: Nмя базы устанавливаемое в списке баз
      additional_parameters: str: Строка для установки в поле "Дополнительные параметры запуска" у базы в списке баз (Default value = '')
      platform_version: str: Строка для установки в поле "Версия 1С:Предприятие" у базы в списке баз (Default value = '')

    Returns:
      bool: Успешно/неуспешно выполнение
    """

    config = ConfigParser()

    result = _read_base_list_file(config, file_name_list_base)

    result = (result and _write_base_list_file(config,
                                               file_name_list_base,
                                               base_name_in_the_list,
                                               additional_parameters,
                                               platform_version))

    return result

def _read_base_list_file(config: ConfigParser, file_name: str) -> bool:
    """Читает файл списка информационных баз.

    Args:
      config: ConfigParser: Парсер ini-файла
      file_name: str: Полное имя файла списка баз 1С - ibases.v8i

    Returns:
      bool: Успешно/неуспешно выполнение
    """

    result = True

    error_message = f'Не удалось прочитать файл {file_name}'

    try:
        config.read(file_name, encoding='utf_8_sig')

    except Exception as ex:
        result = False
        error_message = f'{error_message}. Ошибка: {ex}'

    if not result:
        logger().error(error_message)

    return result

def _write_base_list_file(config: ConfigParser,
                          file_name: str,
                          base_name_in_the_list: str,
                          additional_parameters: str= '',
                          platform_version: str= '') -> bool:
    """Записывает параметры в файл списка информационных баз.

    Args:
      config: ConfigParser: Парсер ini-файла
      file_name: str: Полное имя файла списка баз 1С - ibases.v8i
      base_name_in_the_list: str: Nмя базы устанавливаемое в списке баз
      additional_parameters: str: Строка для установки в поле "Дополнительные параметры запуска" у базы в списке баз (Default value = '')
      platform_version: str: Строка для установки в поле "Версия 1С:Предприятие" у базы в списке баз (Default value = '')

    Returns:
      bool: Успешно/неуспешно выполнение
    """

    result = True

    try:
        if additional_parameters:
            config[base_name_in_the_list]['AdditionalParameters'] = additional_parameters

        if platform_version:
            config[base_name_in_the_list]['Version'] = platform_version

        with open(file_name, 'w', encoding='utf_8_sig') as configfile:
            config.write(configfile, space_around_delimiters = False)

    except Exception as ex:
        result = False
        logger().error(f'Не удалось записать файл {file_name}. Ошибка: {ex}')

    return result
