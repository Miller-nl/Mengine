'''
Сделать логгирование в разные файлы - чтобы выносить "ошибки" отдельно.
Сделать логер для сохранения SQL данных.
Добавить в to_log(), при необходимости, функцию trace back

"Основной файл" - 'main_journal' + ".log"


Логгирование в json!
Доп файл, дублирующий журнал в формате jsonl - каждая строка - json объект
https://ru.stackoverflow.com/questions/726673/%D0%BA%D0%B0%D0%BA-%D0%B4%D0%BE%D0%BF%D0%B8%D1%81%D1%8B%D0%B2%D0%B0%D1%82%D1%8C-%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D1%8E-%D0%B2-json-%D1%84%D0%B0%D0%B9%D0%BB-%D0%BD%D0%B0-python
http://jsonlines.org/

import json
frame = {'timestamp':0.015,'movement':'type_2'}
with open('frames.jsonlines', 'a', encoding='utf-8') as file:
    json.dump(frame, file)
    file.write('\n')

Смысл - логирование данных ошибки.
В каком виде делаем:
date дата
time время
type тип
module модуль, в котором была ошибка (module_name)
trace (след вызова - для лучшего понимания картины)

функция ошибки
сообщение
данные - в простом виде каком-то. Без сохранения объектов.
"miss" - онибка из эксепшена


Добавить в "логгион" miss в качестве параметра
и **rwargs, которые будут добавлены в data словарь.

'''

import logging
import traceback
import json
import datetime

# Локальный клиент для логирования
class LocalLoggerClient:
    '''
    Объект, использующийся для логирования данных.
    Если объекту не указано в init-е, что модуль должен быть создан отдельный логгер, то объект для
    логирования будет использовать уже существующий логер для одинаковых module_name.

    Вывод данных в json файл  НЕ РАБОТАЕТ!! при инициализации ( не логгируется ТОЛЬКО сообщение создания логера)
    '''

    def __init__(self,
                 module_name: str,
                 journals_catalog: str, journal_file: str,
                 write_to_console: bool = False,
                 file_logging_level: str = 'DEBUG',
                 console_logging_level: str = 'INFO',
                 log_initialization: bool = False,
                 create_personal: bool = False
                 ):
        '''
        :param module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования
        :param write_to_console: выводить сообщения и в журнал, и в консоль тоже? В функции логгирования есть
            отдельная настройка этого параметра. Не обязательно использовать вывод сообщений в консоль для всего логера.
        :param file_logging_level: Уровень логирования в фай (файл .log, в json уходит ВСЁ)
        :param console_logging_level: Уровень логирования в консоль
        :param parent_structure: Структурная часть, показывающая вызывающие модули: "A.B.C.текущий модуль"
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
                                    Логгировать инициализацию ТОЛЬКО для основных модулей.
        :param create_personal: параметр позволяет принудительно создавать отдельный логер объекту.
                Не рекомендуется к использованию без особой нужды!
        '''

        self.__module_name = module_name  # Имя модуля
        self.__journals_catalog = journals_catalog  # Каталог журнала
        self.__journal_file = journal_file  # файл журнала

        self.__write_to_console = write_to_console  # детектор логирования в консоль

        # Установим уровень логиирования
        self.__logging_level = self.choose_logging_level(logging_level=console_logging_level)

        # Преднастроим логер
        self.__set_logger(module_name=module_name,
                          file_logging_level=file_logging_level, console_logging_level=console_logging_level,
                          required_separate_logger=create_personal)

        if log_initialization is True:  # Если надо логировать загрузку
            # Модуль логирования всегда подключается в ините объектов.
            self.to_log(message='Инициализация объекта класса', log_type='DEBUG')  # НЕ СРАБАТЫВАЕТ ВЫВОД В ФАЙЛ

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
    def journal_json_file(self):
        '''
        Получение json файла с журналом. БЕЗ КАТАЛОГА

        :return:
        '''
        return self.journal_file.replace('.log', '.jsonlines')

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
                     required_separate_logger: bool = False):
        '''
        Функция устанавливает/создаёт логер, который будет использоваться в этом объекте.

        :param module_name: имя логера
        :param file_logging_level: Уровень логирования в файл
        :param console_logging_level: Уровень логирования в консоль
        :param required_separate_logger: нужно ли принудительно создать отдельный логер
        :return: ничего
        '''

        self.__Logger = logging.getLogger(module_name)  # Запросим логер

        if required_separate_logger or self.get_file_handlers(self.__Logger) == []:
            # Если надо принудительно создать логер, или нет готового логера

            self.__Logger.setLevel('DEBUG')  # Установим уровень логирования самого логера как минимальный

            if self.write_to_console:  # Если пишем в консоль
                # Сделаем логирование в консоль
                Stream_handler = logging.StreamHandler()
                Stream_handler.setLevel(console_logging_level)
                stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                Stream_handler.setFormatter(stream_formatter)
                self.__Logger.addHandler(Stream_handler)  # отдадим в наш экземпляр логера

            # Установим логирование в файл
            File_handler = logging.FileHandler(self.journals_catalog + self.journal_file)  # Обозначим работу с файлом
            File_handler.setLevel(file_logging_level)  # Установим уровень логирования в файл
            File_handler.set_name(module_name)  # Дадим хэндлеру имя, чтобы понимать, чей он
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # зададим формат логирования
            File_handler.setFormatter(file_formatter)  # Отдадим форматер сообщения в менеджер ведения файла
            self.__Logger.addHandler(File_handler)  # отдадим в наш экземпляр логера

            # Создадим файл для логирования в jsonlines
            with open(self.journals_catalog + self.journal_json_file, "w", encoding='utf-8') as write_file:
                # Создадим объект для записи
                write_file.flush()
                pass

        # self.__Logger.propagate = False  # Запреты работы с иерархией
        return

    # Функция проверки хэндлеров
    @staticmethod
    def get_file_handlers(logger):
        '''
        Функция проверяет, есть ли у логера объект handler и возвращяет их список
        Каждый элемент из этого списка будет делать запись в лог. Функция оч важна.
        Ссылка - https://stackoverflow.com/questions/19561058/duplicate-output-in-simple-python-logging-configuration?rq=1

        :param logger: объект - логер
        :return: список handler . Может быть пуст.
        '''
        handlers = logger.handlers
        while True:
            logger = logger.parent
            handlers.extend(logger.handlers)
            if not (logger.parent and logger.propagate):
                break

        return handlers

    # Настройка уровня логирования
    @staticmethod
    def choose_logging_level(logging_level: str):
        '''
        Установление уровня логирования

        :param logging_level: уровень логирования.
        :return: объект, который будет передаваться в функцию логирвоания для опознания уровня.
        '''
        logging_levels = {'DEBUG': logging.DEBUG,
                          'INFO': logging.INFO,
                          'WARNING': logging.WARNING,
                          'ERROR': logging.ERROR,
                          'CRITICAL': logging.CRITICAL}

        if logging_level in logging_levels.keys():  # Если есть в ключах
            logging_level = logging_levels[logging_level]

        else:  # Если не найден вариант логирования
            logging_level = logging_levels['INFO']

        return logging_level

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def to_log(self, message: str,
               log_type: str = 'DEBUG',
               child_module: str = None, function_name: str = None,
               data: object = None,
               log_to_file: bool = True,
               miss: object = None,
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
        :param child_module: вызывающий подмодуль
        :param function_name: имя вызывающей функции (func.__name__)
        :param data: dto объект, который будет залогирован
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :param log_to_file: логирование в файл. Нужен для логирования ошибки записи в json (запрещать запись в json)
        :param miss: ошибка, полученная при эксепшине
        :return: ничего
        '''

        # Сделаем сообщение в логер
        log_message = ''
        if not child_module is None:  # Если есть "подмодуль"
            log_message += child_module
            if not function_name is None:  # Если есть ещё и имя функции
                log_message += f'.{function_name}: '
        elif not function_name is None:  # Если есть только имя функции
            log_message += f'{function_name}: '
        log_message += message  # Добавим само сообщение
        self.__log_message(message=log_message, log_type=log_type)  # Отправим строку в лог

        if log_to_file:  # Если пишем и в json
            dto_dict = self.__prepare_logging_json(message=message, log_type=log_type,
                                                   child_module=child_module, function_name=function_name,
                                                   data=data,
                                                   kwargs=kwargs)  # подготовим DTO

            # Экспортим в файл
            self.__log_to_json(dto_dict=dto_dict)

        return

    def __log_message(self, message: str,
                      log_type: str = 'DEBUG',):
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

    def __prepare_logging_json(self, message: str,
                               log_type: str = 'DEBUG',
                               child_module: str = None,
                               function_name: str = None,
                               data: object = None,
                               kwargs: dict = None,
                               miss: object = None) -> dict:
        '''
        Функция подготавливает DTO с данными для логирования

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
        :param module: имя вызывающего модуля. Для логирования через основной, а не персональные логеры.
        :param function_name: функция, которая делает обращение
        :param data: словарь с данными, которые требуется залоггировать
        :param kwargs: словарь с данными, которые были переданы как "параметры". Он пришивается к data словрю
        :param miss: ошибка, полученная в эксепшине
        :return: DTO в виде словаря
        '''
        logging_dto = {}  # DTO объект
        logging_dto['time'] = str(datetime.datetime.now())
        logging_dto['log_type'] = log_type
        logging_dto['module'] = self.__Logger.name
        logging_dto['message'] = message
        logging_dto['function_name'] = function_name
        logging_dto['child_module'] = child_module

        log_data = {}
        if isinstance(data, dict):  # Если подан словарь с данными
            log_data.update(data)
        if isinstance(kwargs, dict):
            log_data.update(kwargs)
        logging_dto['data'] = log_data

        logging_dto['miss'] = str(miss)  # Чтобы потом конвертнулось в json

        trace = []
        stack = traceback.extract_stack()[:-3] # -3, чтобы убрать функцию логирования, эту и "traceback"
        for s in stack:
            trace.append(s.name + ' -> ' + s.line)
        logging_dto['trace'] = trace

        return logging_dto

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

