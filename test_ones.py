"""Тесты модуля ones"""

from collections import namedtuple
from configparser import ConfigParser
import pytest
from testfixtures import LogCapture
from unittest.mock import patch

import  ones
from ones import CreationInfobase, Designer, Enterprise, GenInfobaseLogFileName
from ones import set_base_parameters_in_list_file, SupportRules, SQLYearOffsets
from ones import FileDBFormats, DBServerTypes, ConfigDumpFormats

@pytest.fixture
def filebase_dir():
    """Nмя произвольного каталога.
    Nспользуется для передачи параметра каталога файловой базы.
    """

    return r'D:\R'

@pytest.fixture
def auth_params():
    """Параметры авторизации."""

    class Result:
        user = 'user1'
        password = 'password1'

    return Result

@pytest.fixture
def serverbase_addr():
    """Параметры серверной информационой базы."""

    class Result:
        server = 'server1'
        infobase = 'infobase1'

    return Result

@pytest.fixture
def other_params():
    """Для параметров функции set_other_params."""

    class Result:
        locale = 'ru_RU'

    return Result

@pytest.fixture
def name_nonexistent_file(tmp_path):
    """Nмя несуществующего файла"""

    return tmp_path / '1'

@pytest.fixture
def name_nonini_file(tmp_path):
    """Nмя существующего файла не ini формата """

    file = tmp_path / "file1.ini"
    file.write_text('-')

    yield str(file)

    file.unlink(missing_ok=True)

@pytest.fixture
def empty_base_list_file_name(tmp_path):
    """Nмя существующего ini-файла с пустыми значениями параметров"""

    config = ConfigParser()
    config.add_section('base1')
    config.set('base1', 'AdditionalParameters', '')
    config.set('base1', 'Version', '')

    file = tmp_path / 'test1.ini'
    file_name = str(file)

    with open(file_name, 'w', encoding = 'utf_8_sig') as config_file:
        config.write(config_file)

    yield file_name

    file.unlink(missing_ok=True)


class TestAnotherFileName():
    """Проверка функции GenInfobaseLogFileName.another_file_name."""

    def test_success(self):
        """Стандартный успешный сценарий."""

        prefix = r'D:\R'

        gen_ib_log_file_name = GenInfobaseLogFileName(prefix)

        file_name1 = gen_ib_log_file_name.another_file_name()
        file_name2 = gen_ib_log_file_name.another_file_name()

        assert file_name1 == f'{prefix}1.log'
        assert file_name2 == f'{prefix}2.log'


class TestIbConnectionStringDesigner():
    """Проверка функции Designer._ib_connection_string"""

    def test_dir_and_other(self, filebase_dir, auth_params, other_params):
        """Задан dir и прочие параметры."""

        designer = Designer(dir_ = filebase_dir)
        designer.set_auth_params(user = auth_params.user, password = auth_params.password)
        designer.set_other_params(locale = other_params.locale)

        actual_value = designer._ib_connection_string()

        expected_value = (f"FILE='{filebase_dir}';"
                         f"Usr='{auth_params.user}';Pwd='{auth_params.password}';"
                         f"Locale={other_params.locale};")

        assert actual_value == expected_value

    def test_dir(self, filebase_dir):
        """Задан dir и НЕ заданы прочие параметры."""

        designer = Designer(dir_ = filebase_dir)

        actual_value = designer._ib_connection_string()

        expected_value = f"FILE='{filebase_dir}';"

        assert actual_value == expected_value

    def test_server_and_other(self, serverbase_addr, auth_params, other_params):
        """Задан server и прочие параметры."""

        designer = Designer(server = serverbase_addr.server,
                            infobase = serverbase_addr.infobase)

        designer.set_auth_params(user = auth_params.user, password = auth_params.password)
        designer.set_other_params(locale = other_params.locale)

        actual_value = designer._ib_connection_string()

        expected_value = (f"Srvr='{serverbase_addr.server}';Ref='{serverbase_addr.infobase}'"
                         f";Usr='{auth_params.user}';Pwd='{auth_params.password}'"
                         f";Locale={other_params.locale};")

        assert actual_value == expected_value

class TestIbConnectionStringCreationInfobase():
    """Проверка функции CreationInfobase._ib_connection_string"""

    @pytest.fixture
    def claster_params(self):
        """Параметры кластера."""

        class Result:
            deny_scheduled_jobs = True
            deny_scheduled_jobs_str = 'Y'
            cluster_administrator_user = 'cluster_administrator_user1'
            cluster_administrator_password = 'cluster_administrator_password1'

        return Result

    @pytest.fixture
    def server_db_params(self):
        """Параметры сервера."""

        class Result:
            db_server_type = DBServerTypes.MS_SQL_SERVER
            db_server_name = 'db_server_name1'
            database = 'database1'
            db_user =  'db_user1'
            db_password = 'db_password1'
            sql_year_offset = SQLYearOffsets.ZERO
            create_db_if_not_exist = True

        return Result

    @pytest.fixture
    def file_db_params(self):
        """Параметры файловой базы."""

        class Result:
            file_db_format = FileDBFormats.F_8_3_8

        return Result

    def test_server(self, claster_params, server_db_params):
        """Серверная база."""

        creation_infobase = CreationInfobase()

        creation_infobase.set_claster_params(claster_params.deny_scheduled_jobs,
                                            claster_params.cluster_administrator_user,
                                            claster_params.cluster_administrator_password)

        creation_infobase.set_server_db_params(db_server_type = server_db_params.db_server_type,
                                        db_server_name = server_db_params.db_server_name,
                                        database = server_db_params.database,
                                        db_user = server_db_params.db_user,
                                        db_password = server_db_params.db_password,
                                        sql_year_offset = server_db_params.sql_year_offset,
                                        create_db_if_not_exist = server_db_params.create_db_if_not_exist)

        expected_value = (f"DBMS={server_db_params.db_server_type.value};"
                         f"DBSrvr='{server_db_params.db_server_name}';"
                         f"DB='{server_db_params.database}';"
                         f"DBUID='{server_db_params.db_user}';"
                         f"SQLYOffs={server_db_params.sql_year_offset.value};"
                         f"DBPwd='{server_db_params.db_password}';"
                         f"CrSQLDB=Y;"
                         f"SchJobDn={claster_params.deny_scheduled_jobs_str};"
                         f"SUsr='{claster_params.cluster_administrator_user}';"
                         f"SPwd='{claster_params.cluster_administrator_password}';")

        actual_value = creation_infobase._ib_connection_string()

        assert actual_value == expected_value

    def test_file(self, filebase_dir, file_db_params):
        """Файловая база"""

        creation_infobase = CreationInfobase(dir_ = filebase_dir)
        creation_infobase.set_file_db_params(file_db_format = file_db_params.file_db_format)

        actual_value = creation_infobase._ib_connection_string()
        expected_value = f"FILE='{filebase_dir}';DBFormat={file_db_params.file_db_format.value};"

        assert actual_value == expected_value

class TestLog1sExecutionError():
    """Проверка функции _log_1s_execution_error"""

    VersionEncodings = namedtuple('VersionEncodings', ['platform_version',
                                                    'encoding'])

    version_encodings = [VersionEncodings('8.3.17', 'cp1251'),
                         VersionEncodings('8.3.18', 'utf_8_sig')]

    @pytest.fixture(params = version_encodings)
    def success_test_params(self, request, tmp_path):
        """Создает тестовые файлы"""

        SuccessTestParams = namedtuple('SuccessTestParams', ['platform_version',
                                                            'gen_ib_log_file_name',
                                                            'file_content'])

        file_content = 'текст1'

        ib_log_file = tmp_path / "file1.log"
        ib_log_file.write_text(file_content, request.param.encoding)
        gen_ib_log_file_name = str(ib_log_file)

        yield SuccessTestParams(request.param.platform_version, gen_ib_log_file_name, file_content)

        ib_log_file.unlink(missing_ok=True)

    def test_success(self, success_test_params):
        """Проверка успешного выполнения"""

        param_result = 1 # произвольное значение

        designer_ = Designer()
        designer_.set_platform_params(exename = '',
                                      platform_version = success_test_params.platform_version)

        with LogCapture() as logs:
            designer_._log_1s_execution_error(param_result, success_test_params.gen_ib_log_file_name)

        msg = f'Код результата: {param_result}: {success_test_params.file_content} '

        assert logs.records[0].msg == msg

    def test_error_no_file(self, name_nonexistent_file):
        """Проверка обработки отсутствия файла лога 1С"""

        return_code = 1 # произвольное значение
        designer_ = Designer()

        with LogCapture() as logs:
            designer_._log_1s_execution_error(return_code = return_code,
                                            gen_ib_log_file_name = name_nonexistent_file)

        msg = (f'Код результата: {return_code}:  '
              f'Для получения текста ошибки не найден файл лога 1С: {name_nonexistent_file}')

        assert logs.records[0].msg == msg


class TestWriteBaseListFile():
    """Проверка функции _write_base_list_file"""

    encoding = 'utf_8_sig'

    def test_success(self, empty_base_list_file_name):
        """Проверка успешного выполнения"""

        # Записали, проверили что факт записи успешен
        config = ConfigParser()
        config.read(empty_base_list_file_name, __class__.encoding)
        base_name =  'base1'
        additional_parameters = '/C 1'
        version_ = '8.1'

        func_result = ones._write_base_list_file(config,
                                                                empty_base_list_file_name,
                                                                base_name,
                                                                additional_parameters,
                                                                version_)

        assert func_result

        # Прочитали записанное, проверили, что записалось то что нужно
        config.read(empty_base_list_file_name, __class__.encoding)

        assert config[base_name]['AdditionalParameters'] == additional_parameters
        assert config[base_name]['Version'] == version_

    def test_error(self, empty_base_list_file_name):
        """Проверка неуспешного выполнения.
        Попытка записи файла без инициализации структуры конфига.
        """

        config = ConfigParser()

        with LogCapture() as logs:
            func_result = ones._write_base_list_file(config,
                                                                    empty_base_list_file_name,
                                                                    base_name_in_the_list = 'a',
                                                                    additional_parameters = 'b',
                                                                    platform_version = 'c')

        msg = f'Не удалось записать файл {empty_base_list_file_name}'
        msg_len = len(msg)

        assert not func_result
        assert logs.records[0].msg[:msg_len] == msg

class TestReadBaseListFile():
    """Проверка функции _read_base_list_file"""

    def test_success(self, empty_base_list_file_name):
        """Проверка успешного выполнения.
        Проверка, что файл прочитался как ini.
        """

        config = ConfigParser()
        func_result = ones._read_base_list_file(config, empty_base_list_file_name)

        assert func_result
        assert config.sections()[0] == 'base1'

    def test_error(self, name_nonini_file):
        """Проверка неуспешного выполнения.
        Попытка чтения файла неверного формата.
        """

        config = ConfigParser()

        with LogCapture() as logs:
            func_result = ones._read_base_list_file(config, name_nonini_file)

        msg = f'Не удалось прочитать файл {name_nonini_file}'
        msg_len = len(msg)

        assert not func_result
        assert logs.records[0].msg[:msg_len] == msg


class TestSetBaseParametersInListFile():
    """Проверка функции set_base_parameters_in_list_file"""

    encoding = 'utf_8_sig'

    def test_success(self, empty_base_list_file_name):
        """Проверка успешного выполнения"""

        # Записали, проверили что факт записи успешен
        base_name =  'base1'
        additional_parameters = '/C 1'
        platform_version = '8.1'

        func_result = set_base_parameters_in_list_file(empty_base_list_file_name,
                                                       base_name,
                                                       additional_parameters,
                                                       platform_version)

        assert func_result

        # Прочитали записанное, проверили, что записалось то что нужно
        config = ConfigParser()
        config.read(empty_base_list_file_name, __class__.encoding)

        assert config[base_name]['AdditionalParameters'] == additional_parameters
        assert config[base_name]['Version'] == platform_version

    def test_error(self, empty_base_list_file_name):
        """Проверка неуспешного выполнения.
        Попытка записи файла c некоректной секцией.
        """
        uncorrect_section = 'base2'

        func_result = set_base_parameters_in_list_file(empty_base_list_file_name,
                                                       base_name_in_the_list = uncorrect_section,
                                                       additional_parameters = 'b',
                                                       platform_version = 'c')

        assert not func_result

class TestCommonRunParametersRunInfobase():
    """Проверка функции RunInfobase._common_run_parameters"""

    def test_epmty(self):
        """Без параметров"""

        # setUp
        run_infobase = ones.RunInfobase()
        run_infobase.set_dialogs_settings(disable_startup_messages = False,
                                          disable_startup_dialogs = False)

        expected_value = []

        # test
        actual_value = run_infobase._common_run_parameters()

        assert actual_value == expected_value

    def test_full(self):
        """Со всеми параметрами"""

        # setUp
        ws_connection_string = 'string1'
        access_code = 'F'
        gen_ib_log_file_name = 'D:\1.log'
        result_file_name = 'D:\res'
        param1 = '/param1'
        param2 = '/param2'

        run_infobase = ones.RunInfobase(ws_connection_string=ws_connection_string)
        run_infobase.set_dialogs_settings(visible=True)
        run_infobase.set_other_params(access_code=access_code, other_params=[param1, param2])
        run_infobase.set_auth_params(user='', password='', use_os_auth=False)

        run_infobase.set_log_ib_params(gen_ib_log_file_name = gen_ib_log_file_name,
                                      truncate_log_ib = False,
                                      result_file_name = result_file_name)

        expected_value = [f'/UC {access_code}',
            '/WA-',
            '/Visible',
            '/DisableStartupMessages',
            '/DisableStartupDialogs',
            f'/Out {gen_ib_log_file_name}',
            '-NoTruncate',
             f'/DumpResult {result_file_name}',
             param1,
             param2]

        # test
        actual_value = run_infobase._common_run_parameters()

        assert actual_value == expected_value

    def test_out_truncate(self):
        """С ветвлением"""

        # setUp
        gen_ib_log_file_name = 'D:\1.log'

        run_infobase = ones.RunInfobase()

        run_infobase.set_dialogs_settings(disable_startup_messages = False,
                                          disable_startup_dialogs = False)

        run_infobase.set_log_ib_params(gen_ib_log_file_name=gen_ib_log_file_name)

        expected_value = [f'/Out {gen_ib_log_file_name}']

        # test
        actual_value = run_infobase._common_run_parameters()

        assert actual_value == expected_value

class TestCommonRunParametersCreationInfobase():
    """Проверка функции CreationInfobase._common_run_parameters"""

    def test_success(self, filebase_dir):
        """Минимум параметров"""

        # setUp
        creation_infobase = CreationInfobase(dir_=filebase_dir)

        expected_value = ["CREATEINFOBASE",
                        f"FILE='{filebase_dir}';",
                        "/DisableStartupMessages",
                        "/DisableStartupDialogs"]
        # test
        actual_value = creation_infobase._common_run_parameters()

        assert actual_value == expected_value

class TestCommonRunParametersEnterprise():
    """Проверка функции Enterprise._common_run_parameters"""

    def test_success(self, filebase_dir):
        """Минимум параметров"""

        # setUp
        enterprise = Enterprise(dir_=filebase_dir)

        expected_value = ["ENTERPRISE",
                        f"/IBConnectionString FILE='{filebase_dir}';",
                        "/DisableStartupMessages",
                        "/DisableStartupDialogs"]

        # test
        actual_value = enterprise._common_run_parameters()

        assert actual_value == expected_value

    def test_launch_param(self, filebase_dir):
        """С переметрами передаваемыми в приложение"""

        # setUp
        launch_param = 'W'

        enterprise = Enterprise(dir_=filebase_dir)

        enterprise.set_dialogs_settings(disable_startup_messages = False,
                                        disable_startup_dialogs = False)

        enterprise.set_other_params(launch_param = launch_param)

        expected_value = ["ENTERPRISE",
                        f"/IBConnectionString FILE='{filebase_dir}';",
                        f"/C {launch_param}"]

        # test
        actual_value = enterprise._common_run_parameters()

        assert actual_value == expected_value

class TestCommonRunParametersDesigner():
    """Проверка функции Designer._common_run_parameters"""

    def test_success(self, filebase_dir):
        """Минимум параметров"""

        # setUp
        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False)

        expected_value = ["DESIGNER",
                         "/DisableStartupMessages",
                         f"/IBConnectionString FILE='{filebase_dir}';"]
        # test
        actual_value = designer._common_run_parameters()

        assert actual_value == expected_value

    def test_repo(self, filebase_dir):
        """Параметры хранилища"""

        # setUp
        repo_dir = r'D:\repo_dir1'
        repo_user = 'repo_user1'
        repo_password = 'repo_password1'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_messages=False, disable_startup_dialogs=False)
        designer.set_repo_params(dir_=repo_dir, user=repo_user, password=repo_password)

        expected_value = ["DESIGNER",
                         f"/IBConnectionString FILE='{filebase_dir}';",
                         f"/ConfigurationRepositoryF {repo_dir}",
                         f"/ConfigurationRepositoryN {repo_user}",
                         f"/ConfigurationRepositoryP {repo_password}"]
        # test
        actual_value = designer._common_run_parameters()

        assert actual_value == expected_value

class TestLoadCfg():
    """Проверка функции Designer.load_cfg."""

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all(self, filebase_dir, expected_result):
        """Проверка корректности формируемых параметров.
        Проверка всех вариантов результата.
        """

        # setUp
        file_name_cf = 'D:\1.cf'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          f"/LoadCfg {file_name_cf}"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.load_cfg(file_name_cf)

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestDumpConfigToFiles():
    """Проверка функции Designer.dump_config_to_files."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров
        при указании всех НЕобязательных параметров.
        """

        # setUp
        dump_dir = r'D:\dir2'
        format_ = ConfigDumpFormats.HIERARCHICAL

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                           f"/IBConnectionString FILE='{filebase_dir}';",
                           f"/DumpConfigToFiles {dump_dir}",
                           f"-Format {format_.value}",
                           f"–update",
                           f"–force"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            designer.dump_config_to_files(dir_=dump_dir, update=True, force=True, format_=format_)

            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка корректности формируемых параметров при НЕуказании необязательных параметров.
        Проверка всех вариантов результата.
        """

        # setUp
        dump_dir = r'D:\dir2'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                           f"/IBConnectionString FILE='{filebase_dir}';",
                           f"/DumpConfigToFiles {dump_dir}"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.dump_config_to_files(dir_ = dump_dir,
                                                          update = False,
                                                          force = False,
                                                          format_ = None)

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestDumpRepoToFile():
    """Проверка функции Designer.dump_repo_to_file."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров
        при указании всех НЕобязательных параметров.
        """

        # setUp
        file_name = 'D:\1.cf'
        version_number = 2

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          f"/ConfigurationRepositoryDumpCfg {file_name}",
                          f"-v {version_number}"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            designer.dump_repo_to_file(file_name=file_name, version_number=version_number)
            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка корректности формируемых параметров при НЕуказании всех НЕобязательных параметров.
        Проверка всех варианты результата.
        """

        # setUp
        file_name = 'D:\1.cf'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          f"/ConfigurationRepositoryDumpCfg {file_name}"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.dump_repo_to_file(file_name=file_name)

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestRunEnterprise():
    """Проверка функции Enterprise.run."""

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка всех вариантов результата."""

        # setUp
        enterprise = Enterprise(dir_=filebase_dir)
        enterprise.set_dialogs_settings(disable_startup_dialogs = False,
                                        disable_startup_messages = False)

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = enterprise.run()

            assert actual_result == expected_result

class TestUpdateFromRepo():
    """Проверка функции Designer.update_from_repo."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров
        при указании всех НЕобязательных параметров.
        """

        # setUp
        version_ = 2
        objects = r'D:\Objects.txt'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)
        designer.set_update_db_cfg_params(update_db_cfg=True, server=True)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositoryUpdateCfg",
                          f'-v {version_}',
                          '-revised',
                          '-force',
                          f'-objects "{objects}"',
                          '/UpdateDBCfg',
                          '-Server']
        # Test
        with patch('ones.RunInfobase._execute_command') as mock:
            designer.update_from_repo(version_=version_, revised=True, force=True, objects=objects)
            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка всех вариантов результата."""

        # setUp
        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositoryUpdateCfg"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.update_from_repo()

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params


class TestCreateRepo():
    """Проверка функции Designer.create_repo."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров,
        при указании всех НЕобязательных параметров.
        """

        # setUp
        changes_allowed_rule = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED
        changes_not_recommended_rule = SupportRules.OBJECT_IS_EDITABLE_SUPPORT_ENABLED

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)


        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositoryCreate",
                          '-AllowConfigurationChanges',
                          f'-ChangesAllowedRule {changes_allowed_rule.value}',
                          f'-ChangesNotRecommendedRule {changes_not_recommended_rule.value}',
                          '-NoBind']

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            designer.create_repo(allow_configuration_changes=True,
                        no_bind=True,
                            changes_allowed_rule = changes_allowed_rule,
                            changes_not_recommended_rule = changes_not_recommended_rule)

            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка всех вариантов результата."""

        # setUp
        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)


        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositoryCreate"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.create_repo(allow_configuration_changes=False)

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestSetRepoLabel():
    """Проверка функции Designer.set_repo_label."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров,
        при указании всех НЕобязательных параметров.
        """

        # setUp
        label = 'label1'
        version_  = 2

        line1 = 'Line1'
        line2 = 'Line2'
        comment = line1 +'\n' + line2

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositorySetLabel",
                          f'-name {label}',
                          f'-v {version_}',
                          f'-comment {line1}',
                          f'-comment {line2}']

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            designer.set_repo_label(label=label, version_=version_, comment=comment)
            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка всех вариантов результата."""

        # setUp

        label = 'label1'

        designer = Designer(dir_=filebase_dir)
        designer.set_dialogs_settings(disable_startup_dialogs=False, disable_startup_messages=False)

        expected_params = ["DESIGNER",
                          f"/IBConnectionString FILE='{filebase_dir}';",
                          "/ConfigurationRepositorySetLabel",
                          f'-name {label}']

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = designer.set_repo_label(label=label)

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestCreateBase():
    """Проверка функции Designer.create_base."""

    def test_all_params(self, filebase_dir):
        """Проверка корректности формируемых параметров,
        при указании всех НЕобязательных параметров.
        """

        # setUp
        base_name_in_the_list = "base_name_in_the_list1"
        template = r'D:\template1.cf'

        creation_infobase = CreationInfobase(dir_=filebase_dir)
        creation_infobase.set_dialogs_settings(disable_startup_dialogs = False,
                                               disable_startup_messages = False)

        expected_params = ["CREATEINFOBASE",
                          f"FILE='{filebase_dir}';",
                          f'/AddInList {base_name_in_the_list}',
                          f'/UseTemplate {template}']

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            creation_infobase.create_base(base_name_in_the_list = base_name_in_the_list,
                                          template = template)

            assert mock.call_args.args[0] == expected_params

    @pytest.mark.parametrize('expected_result', [(True), (False)])
    def test_all_results(self, filebase_dir, expected_result):
        """Проверка всех вариантов результата."""

        # setUp
        creation_infobase = CreationInfobase(dir_=filebase_dir)

        creation_infobase.set_dialogs_settings(disable_startup_dialogs = False,
                                               disable_startup_messages = False)

        expected_params = ["CREATEINFOBASE",
                          f"FILE='{filebase_dir}';"]

        # test
        with patch('ones.RunInfobase._execute_command') as mock:
            mock.return_value = expected_result
            actual_result = creation_infobase.create_base()

            assert actual_result == expected_result
            assert mock.call_args.args[0] == expected_params

class TestExecuteCommand():
    """Проверка функции RunInfobase._execute_command."""

    @pytest.mark.parametrize('returncode, expected_result', [(0, True), (1, False)])
    def test_all_results(self, returncode, expected_result):
        """Проверка всех вариантов результата."""

        # setUp
        run_infobase = ones.RunInfobase()

        # test
        with patch('ones.RunInfobase._subprocess_run') as mock:
            mock.return_value = returncode
            actual_result = run_infobase._execute_command(params=[])

            assert actual_result == expected_result
