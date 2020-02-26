import logging
import datetime
import os


class FileConsoleLogger:
    '''
    Объект, использующийся для логирования данных в журналы типа "name.log" и опционально в консоль.

    Уровни логирования: 10 или 'DEBUG'; 20 или 'INFO'; 30 или 'WARNING'; 40 или 'ERROR'; 50 или 'CRITICAL'.


    Свойства и методы:



        module_name - имя модуля

        journals_files - файлы с журналами

        default_logging_level - уровень логирования поумолчанию

        console_logging_level - уровень логирования в консоль

        add_file_handler() - добавляет менеджер логирования в журнал. Важно, если не указан уровень лога,
            будет выбран "WARNING".

        to_log() - непосредственно функция для логирования


        _get_handlers - отдаёт все хэндлеры логера

        _choose_logging_level() - позволяет выбрать/проверить "уровень логирования"



    '''

    __logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    __logging_levels = {'DEBUG': logging.DEBUG,
                        'INFO': logging.INFO,
                        'WARNING': logging.WARNING,
                        'ERROR': logging.ERROR,
                        'CRITICAL': logging.CRITICAL}

    def __init__(self,
                 module_name: str,
                 journals_catalog: str, journal_file: str = None,
                 file_logging_level: str or int = 'DEBUG',
                 console_logging_level: str or int = None,
                 log_initialization: bool = False):
        '''

        :param module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования. Если не задан, создастся автоматически при добавлении
            FileHandler-а.
        :param console_logging_level: уровень логирования в консоль. None - не логировать.
            Не рекомендуется использовать логирование в консоль.
        :param file_logging_level: Уровень логирования в файл .log. Если задан "косячно", поставится "DEBUG"
        :param console_logging_level: Уровень логирования в консоль
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
                                    Логгировать инициализацию ТОЛЬКО для основных модулей.

        '''

        self.__module_name = module_name  # Имя модуля

        # Проверим каталог логирования
        if journals_catalog is None:
            self.__journals_catalog = journals_catalog

        try:
            self.__default_logging_level = self._choose_logging_level(logging_level=file_logging_level)
        except NameError:  # Если тип задан неверно
            self.__default_logging_level = 10  # Ставим дебаг

        if console_logging_level is not None:  # Если не None - логгируем
            self.__console_logging_level = self._choose_logging_level(logging_level=console_logging_level)
        else:  # Если None
            self.__console_logging_level = None

        # Преднастроим логер c хэндлерами
        self.__set_logger(journals_catalog=journals_catalog, journal_file=journal_file,
                          file_logging_level=file_logging_level, console_logging_level=console_logging_level)

        if log_initialization is True:  # Если надо логировать загрузку
            # Модуль логирования всегда подключается в ините объектов.
            self.to_log(message='Инициализация объекта класса', log_type='DEBUG')

    def _choose_logging_level(self, logging_level: str or int) -> int:
        '''
        Установление уровня логирования

        :param logging_level: уровень логирования.
        :return: число, которое позволит установить уровень логгирования: 10 - DEBUG; 20 - INFO; 30 - WARNING;
            40 - ERROR; 50 - CRITICAL. Если уровень логирования не опознан, вернётся "дефолтный" - указанный при
            создании логера.
        '''
        try:
            return self.__logging_levels[logging_level]
        except KeyError:
            if logging_level in [10, 20, 30, 40, 50]:
                return logging_level
            else:
                return self.default_logging_level

    def __set_logger(self, journals_catalog: str, journal_file: str or None,
                     file_logging_level: str = 'DEBUG',
                     console_logging_level: str = None):
        '''
        Функция устанавливает/создаёт логер, который будет использоваться в этом объекте. Если логер уже есть,
            она просто устанавливает его в качестве собственного. Иначе - создаёт и настраивает.

        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования
        :param file_logging_level: Уровень логирования в файл
        :param console_logging_level: Уровень логирования в консоль. None - не логировать вообще.
        :return: ничего
        '''

        self.__Logger = logging.getLogger(self.module_name)  # Запросим логер

        if not self._get_handlers(self.__Logger):  # Если у логера вообще нет хэндлеров (он новый)

            self.__Logger.setLevel('DEBUG')  # Установим уровень логирования самого логера как минимальный

            if console_logging_level is not None:  # Если пишем в консоль
                # Чекнем уровень логирование
                console_logging_level = self._choose_logging_level(logging_level=console_logging_level)

                # Сделаем логирование в консоль
                Stream_handler = logging.StreamHandler()
                Stream_handler.setLevel(console_logging_level)
                stream_formatter = logging.Formatter(self.__logging_format)
                Stream_handler.setFormatter(stream_formatter)
                self.__Logger.addHandler(Stream_handler)  # отдадим в наш экземпляр логера

        # Установим логирование в файл (если хэндлер есть, он он не продублируется)
        self.add_file_handler(journals_catalog=journals_catalog, journal_file=journal_file,
                              file_logging_level=file_logging_level)
        return

    # ---------------------------------------------------------------------------------------------
    # Основные проперти ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def module_name(self) -> str:
        '''
        Имя модуля, который использует данный логер. Причём это имя, созданное менеджером процесса.

        :return: строка с именем модуля
        '''
        return self.__module_name

    @property
    def journals_files(self) -> list:
        '''
        Отдаёт список полных путей к файлам, если у логера есть logging.FileHandler

        :return: список строк с полными путями файлов. Может быть пустым
        '''
        export_list = []
        for handler in self.__Logger.handlers:
            if isinstance(handler, logging.FileHandler):  # Если это хэндлер журнала в файле
                export_list.append(handler.baseFilename.replace('\\', '/'))  # Добавим путь с "правильными" косыми
        return export_list

    @property
    def default_logging_level(self) -> int:
        '''
        Отдаёт "дефолтный" уровень логирования в файл: 10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL

        :return: число
        '''
        return self.__default_logging_level

    @property
    def console_logging_level(self) -> int or None:
        '''
        Отдаёт уровень логирования в консоль. Если это 0 или None - логирование запрощено.
        10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL

        :return: число или None
        '''
        return self.__console_logging_level

    @staticmethod
    def _get_handlers(logger: logging.Logger) -> list:
        '''
        Функция проверяет, есть ли у логера объект handler и возвращяет их список
        Каждый элемент из этого списка будет делать запись в лог. Функция оч важна.
        Ссылка - https://stackoverflow.com/questions/19561058/duplicate-output-in-simple-python-logging-configuration?rq=1

        :param logger: объект - логер
        :return: список handler-ов. Может быть пуст.
        '''
        handlers = logger.handlers
        while True:
            logger = logger.parent
            handlers.extend(logger.handlers)
            if not (logger.parent and logger.propagate):
                break
        return handlers

    # ---------------------------------------------------------------------------------------------
    # Добавление Handler-а ------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def add_file_handler(self, journals_catalog: str, journal_file: str = None,
                         file_logging_level: str or int = 'WARNING') -> bool or None:
        '''
        Функция добавляет логгеру FileHandler для записи в файл.

        :param journals_catalog: каталог файла с журналом
        :param journal_file: имя файла с журналом. Если не задано будет взято имя вида: дата + время + имя модуля вызова
        :param file_logging_level: уровень логирования хэндлера. Дефолтно стоит WARNING, чтобы не засорять
            лог DEBUG сообщениями, т.к. они будут уходить в дефолтный логер файла.
        :return: статус добавления: True - Успешно, False - handler был, None - ошибка (нет каталога или
            неверное имя файла).
        '''
        # Подготовим параметры

        journals_catalog = journals_catalog.replace('\\', '/')  # Сделаем замену на "правильные" косые
        if not journals_catalog.endswith('/'):
            journals_catalog += '/'  # Добавим нужное окончание, если его нет

        if isinstance(journal_file, str):  # Если имя файла задано
            if not journal_file.endswith('.log'):  # Проверим расширение
                journal_file += '.log'  # Установим, если нет

        file_logging_level = self._choose_logging_level(logging_level=file_logging_level)  # Проверим уровень логирования

        if not os.access(journals_catalog, mode=os.F_OK):  # Проверим каталог
            self.to_log(message=(f'Провалена попытка добаления FileHandler логеру "{self.module_name}" ' +
                                 f' с файлом: {journals_catalog + journal_file}. ' +
                                 'Каталог отсутствует'),
                        log_type='ERROR')
            return None


        if journal_file is not None:  # Если имя файла задано явно
            if (journals_catalog + journal_file) in self.journals_files:  # Если хэндлер для этого файла уже есть
                self.to_log(message=(f'Провалена попытка добаления FileHandler логеру "{self.module_name}" ' +
                                     f' с файлом: {journals_catalog + journal_file}. ' +
                                     'FileHandler с этим файлом есть'),
                            log_type='WARNING')
                return False  # Вернём соовтетсвующий статус
        else:  # Если имя не задано
            journal_file = (str(datetime.datetime.now()).replace(':', ';') +
                            f' {self.module_name}' + '.log')

        try:
            File_handler = logging.FileHandler(journals_catalog + journal_file)  # Создадим FileHandler
        except OSError:  # Если имя файла недопустимо
            self.to_log(message=(f'Провалена попытка добаления FileHandler логеру "{self.module_name}" ' +
                                 f' с файлом: {journals_catalog + journal_file}. ' +
                                 'Имя файла недопустимо'),
                        log_type='ERROR')
            return None

        File_handler.setLevel(file_logging_level)  # Установим уровень логирования в файл
        File_handler.set_name(self.module_name)  # Дадим хэндлеру имя, чтобы понимать, чьего он модуля

        file_formatter = logging.Formatter(self.__logging_format)  # Установим форматирование
        File_handler.setFormatter(file_formatter)  # Отдадим formatter в менеджер ведения файла
        self.__Logger.addHandler(File_handler)  # отдадим FileHandler в наш экземпляр логера

        return True  # Вернём успешность

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def to_log(self, message: str,
               log_type: str = 'DEBUG',
               **kwargs):
        '''
        Функция для отправки сообщений лог.

        :param message: сообщение для логирования
        :param log_type: тип сообщения в лог:
                                DEBUG	Подробная информация, как правило, интересна только при диагностике проблем.

                                INFO	Подтверждение того, что все работает, как ожидалось.

                                WARNING	Указание на то, что произошло что-то неожиданное или указание на проблему в
                                        ближайшем будущем (например, «недостаточно места на диске»).
                                        Программное обеспечение все еще работает как ожидалось.

                                ERROR	Из-за более серьезной проблемы программное обеспечение
                                        не может выполнять какую-либо функцию.

                                CRITICAL	Серьезная ошибка, указывающая на то,
                                        что сама программа не может продолжить работу.
        :param kwargs: дополнительные параметры, чтобы не крашилось в случае чего.
        :return: ничего
        '''

        self.__log_message(message=message, log_type=log_type)  # Отправим строку в лог

        return

    def __log_message(self, message: str,
                      log_type: str = 'DEBUG', ):
        '''
        Функция выполняет непосредственную запись в файл

        :param message: сообщение для логирования
        :param log_type: тип сообщения в лог:
                                DEBUG	Подробная информация, как правило, интересна только при диагностике проблем.

                                INFO	Подтверждение того, что все работает, как ожидалось.

                                WARNING	Указание на то, что произошло что-то неожиданное или указание на проблему в
                                        ближайшем будущем (например, «недостаточно места на диске»).
                                        Программное обеспечение все еще работает как ожидалось.

                                ERROR	Из-за более серьезной проблемы программное обеспечение
                                        не может выполнять какую-либо функцию.

                                CRITICAL	Серьезная ошибка, указывающая на то,
                                        что сама программа не может продолжить работу.
        :return: ничего
        '''
        if log_type == 'DEBUG':
            self.__Logger.debug(message)
        elif log_type == 'INFO':
            self.__Logger.info(message)
        elif log_type == 'ERROR':
            self.__Logger.error(message)
        elif log_type == 'WARNING':
            self.__Logger.warning(message)
        elif log_type == 'CRITICAL':
            self.__Logger.critical(message)

        return
