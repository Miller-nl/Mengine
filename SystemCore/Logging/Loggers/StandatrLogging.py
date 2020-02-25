import logging
import traceback
import datetime



class StandartLogger:
    '''
        Объект, использующийся для логирования данных.
        Если объекту не указано в init-е, что модуль должен быть создан отдельный логгер, то объект для
        логирования будет использовать уже существующий логер для одинаковых module_name.

        Вывод данных в json файл  НЕ РАБОТАЕТ!! при инициализации ( не логгируется ТОЛЬКО сообщение создания логера)
        '''

    __logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    __logging_levels = {'DEBUG': logging.DEBUG,
                        'INFO': logging.INFO,
                        'WARNING': logging.WARNING,
                        'ERROR': logging.ERROR,
                        'CRITICAL': logging.CRITICAL}

    def __init__(self,
                 module_name: str,
                 journals_catalog: str, journal_file: str,
                 write_to_console: bool = False,
                 file_logging_level: str = 'DEBUG',
                 console_logging_level: str = 'INFO',
                 log_initialization: bool = False,
                 create_new_file_handler: bool = False):
        '''
        :param module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования
        :param write_to_console: выводить сообщения и в журнал, и в консоль тоже? В функции логгирования есть
            отдельная настройка этого параметра. Не обязательно использовать вывод сообщений в консоль для всего логера.
        :param file_logging_level: Уровень логирования в фай (файл .log, в json уходит ВСЁ)
        :param console_logging_level: Уровень логирования в консоль
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
                                    Логгировать инициализацию ТОЛЬКО для основных модулей.
        :param create_new_file_handler: параметр позволяет принудительно создавать отдельный хендлер для логгера с
            именем module_name, который будет логировать в фалйл "journals_catalog + journal_file". Если такой
            хэндлер уже есть, то добаление "не удастся". Добавление хэндлера логируется.
            Можно делать два хэндлера с разными уровнями логирования, например.
        '''

        self.__module_name = module_name  # Имя модуля
        if not journals_catalog.endswith('/'):  # Добавим "косую", если её нет
            journals_catalog += '/'
        self.__journals_catalog = journals_catalog.replace('\\', '/')  # Установим форматированный каталог журнала

        if not journal_file.endswith('.log'):  # Добавим "косую", если её нет
            journal_file += '.log'
        self.__journal_file = journal_file  # файл журнала

        self.__write_to_console = write_to_console  # детектор логирования в консоль

        # Установим уровень логиирования
        self.__logging_level = self.choose_logging_level(logging_level=console_logging_level)

        # Преднастроим логер
        self.__set_logger(module_name=module_name,
                          file_logging_level=file_logging_level, console_logging_level=console_logging_level,
                          create_new_file_handler=create_new_file_handler)

        if log_initialization is True:  # Если надо логировать загрузку
            # Модуль логирования всегда подключается в ините объектов.
            self.to_log(message='Инициализация объекта класса', log_type='DEBUG')

    # ---------------------------------------------------------------------------------------------
    # Основные проперти ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def module_name(self) -> str:
        '''
        Имя модуля, который использует данный логер. Причём это имя, созданное менеджером процесса.

        :return:
        '''
        return self.__module_name

    @property
    def journals_catalog(self) -> str:
        '''
        Каталог с файлом

        :return:
        '''
        return self.__journals_catalog

    @property
    def journal_file(self) -> str:
        '''
        Имя файла с журналом. БЕЗ КАТАЛОГА

        :return:
        '''
        return self.__journal_file

    @property
    def write_to_console(self) -> bool:
        '''
        Получаем детектор вывода данных и в консоль тоже.

        :return:
        '''
        return self.__write_to_console

    # ---------------------------------------------------------------------------------------------
    # Создание и настройка логера -----------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    # Функция создания и преднастройки логера
    def __set_logger(self, module_name: str,
                     file_logging_level: str = 'DEBUG',
                     console_logging_level: str = 'INFO',
                     create_new_file_handler: bool = False):
        '''
        Функция устанавливает/создаёт логер, который будет использоваться в этом объекте.

        :param module_name: имя логера
        :param file_logging_level: Уровень логирования в файл
        :param console_logging_level: Уровень логирования в консоль
        :param create_new_file_handler: параметр позволяет принудительно создавать отдельный хендлер для логгера с
            именем module_name, который будет логировать в фалйл "journals_catalog + journal_file". Если такой
            хэндлер уже есть, то добаление "не удастся". Добавление хэндлера логируется.
        :return: ничего
        '''

        self.__Logger = logging.getLogger(module_name)  # Запросим логер

        if not self.get_file_handlers(self.__Logger):  # Если у логера нет готовых хэндлеров (список пуст)

            self.__Logger.setLevel('DEBUG')  # Установим уровень логирования самого логера как минимальный

            if self.write_to_console:  # Если пишем в консоль
                # Сделаем логирование в консоль
                Stream_handler = logging.StreamHandler()
                Stream_handler.setLevel(console_logging_level)
                stream_formatter = logging.Formatter(self.__logging_format)
                Stream_handler.setFormatter(stream_formatter)
                self.__Logger.addHandler(Stream_handler)  # отдадим в наш экземпляр логера

            # Установим логирование в файл
            File_handler = logging.FileHandler(self.journals_catalog + self.journal_file)  # Обозначим работу с файлом
            File_handler.setLevel(file_logging_level)  # Установим уровень логирования в файл
            File_handler.set_name(module_name)  # Дадим хэндлеру имя, чтобы понимать, чей он

            file_formatter = logging.Formatter(self.__logging_format)  # зададим формат логирования
            File_handler.setFormatter(file_formatter)  # Отдадим форматер сообщения в менеджер ведения файла
            self.__Logger.addHandler(File_handler)  # отдадим в наш экземпляр логера

            return  # Закончили

        elif create_new_file_handler:  # Если список хэндлеров не пуст, но хотим создать новый

            # Залогируем попытку
            self.to_log(message=(f'Предпринята попытка добаления FileHandler логеру "{module_name}" ' +
                                 f' с файлом: {self.journals_catalog + self.journal_file}'),
                        log_type='WARNING')

            create_handler = True  # Детектор необходимости добавления хэндлера

            # Проверим, что нет хэндлера с указанным файлом self.journals_catalog + self.journal_file
            for handler in self.get_file_handlers(self.__Logger):
                if isinstance(handler, logging.FileHandler):  # Если FileHandler
                    if handler.baseFilename.replace('\\', '/') == self.journals_catalog + self.journal_file:
                        # Проверяем путь. Если совпал
                        self.to_log(message=(f'Провалена попытка добаления FileHandler логеру "{module_name}" ' +
                                             f' с файлом: {self.journals_catalog + self.journal_file}. ' +
                                             'FileHandler с этим файлом есть'),
                                    log_type='WARNING')
                        return  # Закончили

                else:  # Если это не FileHandler
                    continue

            # Если дошли до сюда, то FileHandler не был найден и его надо добавить
            File_handler = logging.FileHandler(self.journals_catalog + self.journal_file)  # Обозначим работу с файлом
            File_handler.setLevel(file_logging_level)  # Установим уровень логирования в файл
            File_handler.set_name(module_name)  # Дадим хэндлеру имя, чтобы понимать, чей он

            file_formatter = logging.Formatter(self.__logging_format)  # зададим формат логирования
            File_handler.setFormatter(file_formatter)  # Отдадим форматер сообщения в менеджер ведения файла
            self.__Logger.addHandler(File_handler)  # отдадим в наш экземпляр логера

            self.to_log(message=(f'Предпринята попытка добаления FileHandler логеру "{module_name}" ' +
                                 f' с файлом: {self.journals_catalog + self.journal_file}'),
                        log_type='WARNING')

        # self.__Logger.propagate = False  # Запреты работы с иерархией
        return

    @staticmethod
    def get_file_handlers(logger: logging.Logger) -> list:
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

    def choose_logging_level(self, logging_level: str) -> int:
        '''
        Установление уровня логирования

        :param logging_level: уровень логирования.
        :return: число, которое позволит установить уровень логгирования: 10 - DEBUG; 20 - INFO; 30 - WARNING;
            40 - ERROR; 50 - CRITICAL.
        '''
        if logging_level in self.__logging_levels.keys():  # Если есть в ключах
            logging_level = self.__logging_levels[logging_level]
        else:  # Если не найден вариант логирования
            logging_level = self.__logging_levels['INFO']
        return logging_level

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def to_log(self, message: str,
               log_type: str = 'DEBUG',
               exception_mistake: object = None,
               **kwargs):
        '''
        Функция для отправки сообщений на сервер логирования.

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
        :param exception_mistake: ошибка, полученная при try except
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: ничего
        '''

        log_message = message  # Добавим само сообщение

        if exception_mistake is not None:  # Добавим exception
            log_message = f'{exception_mistake}{exception_mistake.args}: {log_message}'


        self.__log_message(message=log_message, log_type=log_type)  # Отправим строку в лог

        return

    def __log_message(self, message: str,
                      log_type: str = 'DEBUG', ):
        '''
        Функция выполняет непосредственную запись в лог

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


    # ---------------------------------------------------------------------------------------------
    # Общие функции подготовки сообщения ----------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def __expand_exception_mistake(self, exception_mistake: object = None) -> str:
        '''
        Функция разворачивает "ошибку" в строку сообщения.

        :param exception_mistake: ошибка, полученная при try except
        :return: строка форматного сообщения 'ErrorType: error message'
        '''
        if exception_mistake is None:
            return 'Не передан exception_mistake'
        export_string = f'{type(exception_mistake)}'
        export_string = export_string.replace('<class ', '')
        export_string = export_string.replace("'>", '')
        export_string += f': {exception_mistake}'

        return export_string


    def __get_traceback(self) -> list:
        '''
        Фукнция возвращяет "каталог вызова". Нужна для логгирование ошибок.

        :return: список "пути".
        '''
        trace = []
        stack = traceback.extract_stack()[:-3]  # -3, чтобы убрать функцию логирования,  эту и "traceback"
        for s in stack:
            trace.append(s.name + ' -> ' + s.line)
        '''
        !!!! Сделать "стандартной функцией!"
        
        Доп
        type(exception_mistake).with_traceback() - чё за трэйс?
        
        
        
['<module> -> pydevconsole.start_client(host, port)',
 'start_client -> process_exec_queue(interpreter)',
 'process_exec_queue -> more = interpreter.add_exec(code_fragment)',
 'add_exec -> more = self.do_add_exec(code_fragment)',
 'do_add_exec -> res = bool(self.interpreter.add_exec(code_fragment.text))',
 'add_exec -> self.ipython.run_cell(line, store_history=True)',
 'run_cell -> raw_cell, store_history, silent, shell_futures)',
 '_run_cell -> return runner(coro)',
 '_pseudo_sync_runner -> coro.send(None)',
 'run_cell_async -> interactivity=interactivity, compiler=compiler, result=result)',
 'run_ast_nodes -> if (yield from self.run_code(code, result)):']
stack = traceback.extract_stack()[:-3]
stack
Out[5]: 
[<FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\pydevconsole.py, line 386 in <module>>,
 <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\pydevconsole.py, line 327 in start_client>,
 <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\pydevconsole.py, line 174 in process_exec_queue>,
 <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\_pydev_bundle\pydev_code_executor.py, line 106 in add_exec>,
 <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\_pydev_bundle\pydev_ipython_console.py, line 39 in do_add_exec>,
 <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\_pydev_bundle\pydev_ipython_console_011.py, line 441 in add_exec>,
 <FrameSummary file C:\Users\Miller_wpc\AppData\Local\Programs\Python\Python37\lib\site-packages\IPython\core\interactiveshell.py, line 2843 in run_cell>,
 <FrameSummary file C:\Users\Miller_wpc\AppData\Local\Programs\Python\Python37\lib\site-packages\IPython\core\interactiveshell.py, line 2869 in _run_cell>,
 <FrameSummary file C:\Users\Miller_wpc\AppData\Local\Programs\Python\Python37\lib\site-packages\IPython\core\async_helpers.py, line 67 in _pseudo_sync_runner>,
 <FrameSummary file C:\Users\Miller_wpc\AppData\Local\Programs\Python\Python37\lib\site-packages\IPython\core\interactiveshell.py, line 3044 in run_cell_async>]

first = stack[0]
first.name
Out[7]: '<module>'
first.filename
Out[8]: 'C:\\Program Files\\JetBrains\\PyCharm Community Edition 2018.3.5\\helpers\\pydev\\pydevconsole.py'
first.line
Out[9]: 'pydevconsole.start_client(host, port)'
first.lineno
Out[10]: 386
first.locals
kjgahsdgf
        '''
        return trace

    def __log_to_json(self, dto_dict: dict):
        '''
        Функция логирует в json файл.

        :param dto_dict: словарь-DTO, который уйдёт в файл в качестве json объекта
        :return: ничего
        '''
        try:
            with open(self.journals_catalog + self.journal_json_file, 'a') as write_file:  # Делаем экспорт
                json.dump(dto_dict, write_file)
                write_file.write('\n')
                write_file.flush()
        except BaseException as miss:
            self.to_log(message=f'ошибка записи сообщения в файл: {miss}',
                        function_name='__log_to_json',
                        log_type='ERROR',
                        log_to_file=False)
        return

