import datetime

from CatalogCommunication.Manager import CatalogsManager
from Logging.Client import LocalLoggerClient

# Менеджер для процесса
class ProcessesManager:
    '''
    Это менеджер процесса. Его задача:
        обеспечение процесса структурой каталогов, для обеспечения нормальной работы.

        логирование данных

    Основные свойства

    Основные методы

    '''

    def __init__(self,
                 process_name: str, session_name: str,
                 main_path: str = 'default',
                 subdirectory: str = None,
                 main_journal_file: str = None):
        '''

        :param process_name: имя процесса.
        :param session_name: имя сессии запуска процесса. Используется для уникализации журналов логирования
        :param main_path: каталог для процесса. Значение 'default' значит, что будет использован указанный в
            Catalogs main_catalog.
        :param subdirectory: подкаталог, в котором будет разворачиватсья стандартная схема папок.
            Например, для тестирования.
        :param main_journal_file: имя главного журнала
        '''

        self.__process_name = process_name  # имя процесса
        self.__session_name = session_name  # имя сессии

        if main_journal_file is None:  # Если основное имя файла не задано
            self.__main_journal_file = self.__get_journal_name()  # Имя файла с основным журналом
        else:
            self.__main_journal_file = main_journal_file

        # Установим менеджер каталога
        self.__CatalogsManager = CatalogsManager(process_name=self.__process_name,
                                                 main_path=main_path,
                                                 subdirectory=subdirectory)

        # Установим дефолтный/основной логер
        self.__Main_Logger = LocalLoggerClient(module_name=self.get_module_name(my_name=self.__class__.__name__),
                                               journals_catalog=self.__CatalogsManager.logging_catalog(),
                                               journal_file=self.__main_journal_file,
                                               write_to_console=True,
                                               file_logging_level='DEBUG',
                                               console_logging_level='INFO',
                                               log_initialization=True)

    def __get_journal_name(self) -> str:
        '''
        Функция создаёт уникальное имя файла для запуска сессии процесса.

        :return:
        '''
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("(%Y-%m-%d) %I-%M%p")
        journal = f'{date_time} {self.session_name} main_journal.log'
        return journal

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def process_name(self):
        '''
        Получение имени процесса, внутри которого мы работаем.

        :return:
        '''
        return self.__process_name

    @property
    def session_name(self):
        '''
        Получение имени сессии, называющей запуск процесса.

        :return:
        '''
        return self.__session_name

    @property
    def CatalogsManager(self) -> CatalogsManager:
        '''
        Отдаём менеджер каталогов, который имеется в менеджере процесса.

        :return:
        '''
        return self.__CatalogsManager

    @property
    def Main_Logger(self) -> LocalLoggerClient:
        '''
        Получение "основного" логра
        :return: "основной" логер процесса
        '''

        return self.__Main_Logger

    # ------------------------------------------------------------------------------------------------
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_module_name(self, my_name: str,
                        launch_module_name: str = None) -> str:
        '''
        Функция для получения имени модуля по имени вызывающего модуля и собственному имени

        :param my_name: имя модуля, указанное в классе самого модуля. Если вызывающий функцию модуль является головным,
            не имеющим "вызывающий модуль", то он отдаёт совё имя, оставив launch_module_name без значения.
        :param launch_module_name: имя вызывающего модуля, оно тоже было получено через эту функцию.
        :return: форматное имя модуля, которое будет использоваться в функция для опознания модуля и структуры
            старших элементов.
        '''
        if launch_module_name is None:
            name = f'[{self.process_name} - {self.session_name}] {my_name}'
            return name
        else:
            name = f'{launch_module_name}.{my_name}'
            return name

    def create_logger(self, module_name: str,
                      journal_file: str = None,
                      journals_catalog: str = None,
                      file_logging_level: str = 'DEBUG',
                      write_to_console: bool = False,
                      console_logging_level: str = 'INFO',
                      log_initialization: bool = False,
                      required_separate_logger: bool = False) -> LocalLoggerClient or None:
        '''
        Функция создаёт логгер для модуля, который его запрашивает.

        :param module_name: имя вызывающего модуля в процессе. У каждого модуля в процессе будет подгружен
            только один логер. Получена через ProcessesManager.get_module_name()
        :param journal_file: файл для логирования
        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param file_logging_level: Уровень логирования в фай
        :param write_to_console: выводить сообщения и в журнал, и в консоль тоже? В функции логгирования есть
            отдельная настройка этого параметра. Не обязательно использовать вывод сообщений в консоль для всего логера.
        :param console_logging_level: Уровень логирования в консоль
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
                                    Логгировать инициализацию ТОЛЬКО для основных модулей.
        :param required_separate_logger: параметр позволяет принудительно создавать отдельный логер объекту.
                Не рекомендуется к использованию без особой нужды!
        :return: объект - логгер или None
        '''

        if journal_file is None:  # Если файл журнала не указан, берём дефолтный
            journal_file = self.__main_journal_file
        if journals_catalog is None:  # Если не задан каталог логирования
            journals_catalog = self.__CatalogsManager.logging_catalog()  # Берём основной каталог логирования

        try:
            Logger = LocalLoggerClient(module_name=module_name,
                                       journals_catalog=journals_catalog, journal_file=journal_file,
                                       file_logging_level=file_logging_level,
                                       console_logging_level=console_logging_level, write_to_console=write_to_console,
                                       log_initialization=log_initialization,
                                       create_personal=required_separate_logger)
            return Logger

        except BaseException as miss:  # В случае ошибки
            self.Main_Logger.to_log(message=(f'Ошибка создания логера: {miss}. Параметры: process_name={self.process_name}, ' +
                                      f'module_name={module_name}, ' +
                                      f'journals_catalog={journals_catalog}, journal_file={journal_file}, ' +
                                      f'log_initialization={log_initialization}, ' +
                                      f'create_personal={required_separate_logger}'),
                             log_type='ERROR')
            return None

    # ------------------------------------------------------------------------------------------------
    # Работа с  ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------