import json
import logging
import datetime
import os
import sys

from SystemCore.Logging.Loggers.СommonFunctions import prepare_exception_and_trace


class JsonLogger:
    '''
    Объект, использующийся для логирования данных в файлы "name.jsonlines".

    Уровни логирования: 10 или 'DEBUG'; 20 или 'INFO'; 30 или 'WARNING'; 40 или 'ERROR'; 50 или 'CRITICAL'.


    Свойства и методы:

        module_name - имя модуля

        default_logging_level - уровень логирования поумолчанию

        journals - список с данными о журналах

        _logger_mistakes - список ошибок, полученных при работе логера


        journals_files - файл с журналом

        to_log() - непосредственно функция для логирования

        _choose_logging_level() - позволяет выбрать/проверить "уровень логирования"
    '''

    __logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    __logging_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def __init__(self,
                 module_name: str,
                 journals_catalog: str, journal_file: str = None,
                 logging_level: str or int = 'DEBUG',
                 log_initialization: bool = False):
        '''

        :param module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования без расширения. Если не задан, создастся автоматически по времени и дате.
        :param logging_level: Уровень логирования в файл .jsonlines. Если задан "косячно", поставится "DEBUG"
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
            Логгировать инициализацию ТОЛЬКО для основных модулей.
        '''

        self.__module_name = module_name  # Имя модуля
        self.__default_logging_level = self._choose_logging_level(logging_level=logging_level)  # Установим уровень лога

        self.__logger_mistakes = []  # Список ошибок логера (как лог логера)

        # Создадим файл журнала если его нет
        self.__prepare_file(journals_catalog=journals_catalog, journal_file=journal_file)

        if log_initialization is True:  # Если надо логировать загрузку
            # Модуль логирования всегда подключается в ините объектов.
            self.to_log(message='Инициализация объекта класса', logging_level='DEBUG')

    def _choose_logging_level(self, logging_level: str or int) -> str:
        '''
        Установление уровня логирования

        :param logging_level: уровень логирования.
        :return: строка с именем уровня логирования
            10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL.
            Если уровень логирования не опознан, вернётся "дефолтный" - указанный при создании логера.
        '''
        if isinstance(logging_level, str):
            if logging_level in self.__logging_levels:  # Првоерим по списку
                return logging_level  # Если из списка - вернём как есть
            return logging.getLevelName(logging_level)  # Иначе прогоним через "получение уровня"

        else:  # Если задано число
            return logging.getLevelName(logging_level)  # вернём строковый уровень

    def __prepare_file(self, journals_catalog: str, journal_file: str = None) -> bool or None:
        '''
        Функция устанавливает файл для логирования

        :param journals_catalog: директория для ведения журнала
        :param journal_file: файл для логирования
        :return: статус добавления: True - Успешно; None - ошибка (нет каталога или неверное имя файла).
        '''

        # Создадим имя файлай
        journals_catalog = os.path.abspath(journals_catalog)  # отформатируем путь

        if isinstance(journal_file, str):  # Если имя файла задано
            if not journal_file.endswith('.jsonlines'):  # Проверим расширение
                journal_file += '.jsonlines'  # Установим, если нет
        else:  # Если имя не задано
            journal_file = (str(datetime.datetime.now()).replace(':', ';') +
                            f' {self.module_name}' + '.jsonlines')
        self.__journal_file = os.path.join(journals_catalog, journal_file)  # Забьём в полный путь

        try:
            if not os.access(self.__journal_file, os.F_OK):  # Если файла нет, создадим
                with open(self.__journal_file, "w", encoding="utf-8") as f:
                    pass
        except FileNotFoundError:  # Если нет каталога
            self.__logger_mistakes.append(sys.exc_info())  # Список ошибок логера (как лог логера)
            return None
        except OSError:  # Если косячное имя файла
            self.__logger_mistakes.append(sys.exc_info())  # Список ошибок логера (как лог логера)
            return None

        return True  # Если всё ок

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def module_name(self) -> str:
        '''
        Общий параметр
        Имя модуля, который использует данный логер. Причём это имя, созданное менеджером процесса.

        :return: строка с именем модуля
        '''
        return self.__module_name

    @property
    def default_logging_level(self) -> str:
        '''
        Общий параметр
        Отдаёт "дефолтный" уровень логирования в файл: 10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL

        :return: число
        '''
        return self.__default_logging_level

    @property
    def _logger_mistakes(self) -> list:
        '''
        Общий параметр
        Функция отдаёт ошибки, полученные при работе логера. Ошибки извлекаются через sys.exc_info().

        :return: копия спискаошибок
        '''
        return self.__logger_mistakes.copy()

    @property
    def journals(self) -> list:
        '''
        Функция отдаёт данные о том, куда логгер отправляет сообщения.
        Обработка списка данных - уже отдельный вопрос.

        :return:
        '''
        return self.journals_files

    # ---------------------------------------------------------------------------------------------
    # Личные property -----------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def journals_files(self) -> list:
        '''
        Общий параметр
        Отдаёт полный путь к файлу лога. В виде списка - для единости интерфейсов

        :return: строка с путём
        '''
        return [self.__journal_file]

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def to_log(self, message: str,
               logging_level: str = 'DEBUG',
               logging_data: object = None,
               exception_mistake: tuple or bool = False,
               trace: list or bool = False,
               **kwargs):
        '''
        Функция для отправки сообщений на сервер логирования.

        :param message: сообщение для логирования
        :param logging_level: тип сообщения в лог:
                                DEBUG	Подробная информация, как правило, интересна только при диагностике проблем.

                                INFO	Подтверждение того, что все работает, как ожидалось.

                                WARNING	Указание на то, что произошло что-то неожиданное или указание на проблему в
                                        ближайшем будущем (например, «недостаточно места на диске»).
                                        Программное обеспечение все еще работает как ожидалось.

                                ERROR	Из-за более серьезной проблемы программное обеспечение
                                        не может выполнять какую-либо функцию.

                                CRITICAL	Серьезная ошибка, указывающая на то,
                                        что сама программа не может продолжить работу.
        :param logging_data: dto объект, который будет залогирован. Обычно содержит информацию о данных,
            обрабатывающихся в скриптах.
        :param exception_mistake: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: ничего
        '''

        # Скорректируем уровень лога, если нужно
        if exception_mistake is not False:  # Если переданы данные об исключении
            if logging_level in ['DEBUG', 'INFO']:  # Если уровень логирования низок
                logging_level = 'WARNING'  # Ставим "WARNING", так как в общем случае exception не всегда ERROR

        # Проверим: является ли уровень логирвоания разрешённым?
        if logging_level != self.default_logging_level:  # Если это не дефолтный уровень
            # Он должен быть правее дефолтного в self.__logging_levels
            if logging_level not in self.__logging_levels[self.__logging_levels.index(logging_level):]:
                return  # Не логируем

        # Выполним развёртку exception_mistake и traceback
        exception_mistake, trace = prepare_exception_and_trace(exception_mistake=exception_mistake, trace=trace)


        # Получим словарь, который будет залогирован
        logging_dto = self.__prepare_logging_json(message=message, logging_level=logging_level,
                                                  logging_data=logging_data,
                                                  exception_mistake=exception_mistake, trace=trace,
                                                  kwargs=kwargs)  # Отправим строку в лог
        # Отправим в файл
        self.__log_to_json(dto_dict=logging_dto)

        return


    def __prepare_logging_json(self, message: str,
                               logging_level: str = 'DEBUG',
                               logging_data: object = None,
                               exception_mistake: str = None,
                               trace: list = None,
                               kwargs: dict = None) -> dict:
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
        :param logging_data: словарь с данными, которые требуется залоггировать
        :param exception_mistake: данные об ошибке. След ошибки передаётся в trace
        :param trace: список строк следа вызова функции логирования или произошедшей ошибки
        :param kwargs: словарь с данными, которые были переданы как "параметры". Он пришивается к data словрю
        :return: DTO в виде словаря
        '''
        logging_dto = {}  # DTO объект
        logging_dto['time'] = str(datetime.datetime.now())
        logging_dto['logging_level'] = self._choose_logging_level(logging_level=logging_level)
        logging_dto['module'] = self.module_name

        logging_dto['message'] = message

        if exception_mistake is not None:
            logging_dto['exception_mistake'] = exception_mistake
        if trace is not None:
            logging_dto['traceback'] = trace

        if logging_data is not None:
            logging_dto['logging_data'] = logging_data

        if kwargs:  # Если словарь не пуст
            logging_dto['additional_data'] = kwargs

        return logging_dto

    def __log_to_json(self, dto_dict: dict):
        '''
        Функция логирует в json файл.

        :param dto_dict: словарь-DTO, который уйдёт в файл в качестве json объекта
        :return: ничего
        '''
        try:
            with open(self.journals_files[0], 'a') as write_file:  # Делаем экспорт
                json.dump(dto_dict, write_file)
                write_file.write('\n')
                write_file.flush()
        except BaseException as miss:  # При ошибке записи
            self.__logger_mistakes.append(sys.exc_info())  # Список ошибок логера

            # Сбросим "неосновные" части сообщения, в которых вероятнее всего ошибка
            logging_dto = {}  # DTO объект
            logging_dto['time'] = dto_dict['time']
            logging_dto['logging_level'] = dto_dict['logging_level']
            logging_dto['module'] = dto_dict['module']
            logging_dto['message'] = dto_dict['message']
            logging_dto['logging_data'] = f'Ошибка отправки данных: {miss}'

            try:  # Попробуем пихнуть основное сообщение
                with open(self.journals_files[0], 'a') as write_file:  # Делаем экспорт
                    json.dump(logging_dto, write_file)
                    write_file.write('\n')
                    write_file.flush()
            except BaseException as miss:  # При ошибке записи
                self.__logger_mistakes.append(sys.exc_info())  # Список ошибок логера

                # Если опять упалоъ
                logging_dto['message'] = f'Ошибка логирования основного сообщения: {miss}'
                logging_dto['logging_level'] = 'ERROR'
                try:  # Попробуем пихнуть основное сообщение
                    with open(self.journals_files[0], 'a') as write_file:  # Делаем экспорт
                        json.dump(logging_dto, write_file)
                        write_file.write('\n')
                        write_file.flush()
                except BaseException:  # При ошибке записи
                    self.__logger_mistakes.append(sys.exc_info())  # Список ошибок логера
                    pass  # Если и это упало, то всё - пиши пропало

        return

