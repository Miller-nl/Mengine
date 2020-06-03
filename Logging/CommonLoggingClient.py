'''
Параметры функции логирования:
    to_log(self, message: str,
               function_name: str or bool = True,
               submodule_name: str = None,
               logging_level: int or str = 'DEBUG',
               logging_data: object = None,
               exception: tuple or bool = True,
               trace: list or bool = False,
               **kwargs) -> bool or None:
        Функция для отправки сообщений на сервер логирования.

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param logging_level: тип сообщения в лог. Число или:
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
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: статус отправки сообщения: True - все успешно, False - кто-то упал, None - ушло только
            в контенер с проваленными.

'''

import datetime

from SystemCore.Logging.CommonFunctions.ExceptionAndTrace import prepare_exception, prepare_trace
from SystemCore.Logging.CommonFunctions.LoggingLevels import logging_levels_int, int_logging_level
from SystemCore.Logging.CommonFunctions.ForFailedMessages import FailedMessages

# ------------------------------------------------------------------------------------------------
# Вспомогательные функции ------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
def get_function_name(drop_last: int = 0) -> str:
    '''
    Фукнция отдаёт "короткое" (относительно trace) название функции.

    :param drop_last: сколько вызывающих функций скинуть с конца следа? (кроме этой)
    :return: фортманая строка вида:  obj1.obj2...func
    '''
    trace = prepare_trace(trace=True, drop_last=drop_last + 1)  # Скидываем сколько сказано + себя
    export_str = ''
    for el in trace:
        export_str += str(el.name) + '.'
    export_str = export_str[:-1]  # Дропаем последнюю точку
    return export_str

# ------------------------------------------------------------------------------------------------
# Клиент логирования -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

class CommonLoggingClient:
    '''
    Объект, использующийся как общий клиент для логирования. Если клиенту не передать ни одного логера, он
        будет запоминать внутри себя последние remember_failed_requests сообщений.

    Уровни логирования: 10 или 'DEBUG'; 20 или 'INFO'; 30 или 'WARNING'; 40 или 'ERROR'; 50 или 'CRITICAL'.

    Если не указан ни один воркер, то все сообщения упадут в контейнер _FailedMessages и будут доступны
        из него.

    Свойства и методы:
        Опознавательные данные:
            main_module_name - имя модуля, запустившего логер

            process_name - имя процесса, в котором запущен модуль

            session_name - имя сессии, в которой работает модуль

        О сообщениях логера:
            default_logging_level - уровень логирования поумолчанию

            _MessagesStatuses - словарь, содержащий счётчик сообщений логера. Ключ - статус сообщений

            are_process_cool_yet - детектор полного отсутствия ошибок в сообщениях логера в работе процесса

            are_messages_cool_yet - детектор наличия сообщений, чья отправка была провалена.

            _FailedMessages - получение контейнера с "упавшими" сообщениями. Запросить у контейнера
                сообщения можно через ".failed_requests"

        Создание форматной структуры имён:
            create_subname() - функция создаёт имя модуля

        Писатели лога:
            writers_dict - словарь воркеров. Индекс - имя воркера

            add_writer() - функция добавления писателя лога

            drop_writer() - функция сброса писателя лога.


        Логирование:
            to_log() - непосредственно функция для логирования
    '''

    __int_logging_levels = logging_levels_int
    __default_level = 10

    def __init__(self,
                 main_module_name: str,
                 process_name: str = None, session_name: str = None,
                 logging_level: str or int = 'DEBUG',
                 remember_failed_requests: int = 120,
                 log_initialization: bool = False):
        '''

        :param main_module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param process_name: имя процесса, в котором задействуется модуль (секция)
        :param session_name: имя сессии - запуска (опция)
        :param logging_level: Уровень логирования, использующийся по дефолту в случаях, когда заданный уровень
            сообщения не опознан.
        :param remember_failed_requests: количество сообщений, которые будут заполнены в случае отказа воркера. 0 - все.
        :param log_initialization: логировать инициализацию? По дефолту - нет, чтобы не "срать" в лог.
            Логгировать инициализацию ТОЛЬКО для основных модулей.
        '''

        self.__main_module_name = main_module_name  # Имя модуля
        self.__process_name = process_name  # Имя процесса
        self.__session_name = session_name  # Имя модуля

        self.__default_logging_level = int_logging_level(logging_level=logging_level,
                                                         default_level=10)

        self.__writers_dict = {}  # Список "писателей"

        self._reset_error_counter()  # заводит self.__error_counter

        self.__failed_messages = FailedMessages(maximum_list_length=remember_failed_requests)

        if log_initialization is True:  # Если надо логировать загрузку
            # Модуль логирования всегда подключается в ините объектов.
            self.to_log(message='Инициализация объекта класса', logging_level='DEBUG')

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def main_module_name(self) -> str:
        '''
        Общий параметр
        Имя модуля, который использует данный логер. Причём это имя, созданное менеджером процесса.

        :return: строка с именем модуля
        '''
        return self.__main_module_name

    @property
    def process_name(self) -> str:
        '''
        Общий параметр
        Имя процесса, из которого используется данный логер. Причём это имя, созданное менеджером процесса.
        (Секция)

        :return: строка с именем процесса
        '''
        return self.__process_name

    @property
    def session_name(self) -> str:
        '''
        Общий параметр
        Имя запуска процесса, в котором использует данный логер. Причём это имя, созданное менеджером процесса.
        (Опция)

        :return: строка с именем запуска - сессии
        '''
        return self.__session_name

    @property
    def default_logging_level(self) -> int:
        '''
        Общий параметр
        Отдаёт "дефолтный" уровень логирования в файл: 10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL

        :return: число
        '''
        return self.__default_logging_level

    # ---------------------------------------------------------------------------------------------
    # Счётчик сообщений  --------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def __create_error_counter(self) -> dict:
        '''
        Функция создаёт счётчики ошибок. Счётчик заводится внутри, чтобы

        :return: ничего
        '''

        error_counter = {}  # Список ошибок логера (как лог логера)
        for key in logging_levels_int.keys():
            error_counter[logging_levels_int[key]] = 0  # ставим ноль

        return error_counter

    def _reset_error_counter(self):
        '''
        Функция обновляет счётчик ошибок
        :return:
        '''

        self.__error_counter = self.__create_error_counter()

        return 

    def __add_message_count(self, logging_level: int):
        '''
        Функция крутит счётчик типов сообщений.

        :param logging_level: уровень логирвоания
        :return: ничего
        '''

        try:
            self.__error_counter[logging_level] += 1
        except BaseException:  # Если нет такого счётчика
            if logging_level > max(self.__error_counter.keys()):  # Если уровень привышен
                self.__error_counter[max(self.__error_counter.keys())] += 1
            elif logging_level < min(self.__error_counter.keys()):  # Если уровень ниже минимального
                self.__error_counter[min(self.__error_counter.keys())] += 1

            else:  # иначе
                # Сделаем хит в боижайший "справа" счётчик, так как левый привышен
                logging_level = logging_level // 10 + 1
                self.__add_message_count(logging_level=logging_level)  # считаем
        return

    @property
    def _MessagesStatuses(self) -> dict:
        '''
        Общий параметр
        Отдаёт счётчик сообщений, полученных во время работы. Сообщения делятся также, как функции логирования:
            'DEBUG' - 10, 'INFO' - 20, 'WARNING' - 30, 'ERROR' - 40, 'CRITICAL' - 50

        :return: копия спискаошибок
        '''
        return self.__error_counter.copy()

    @property
    def are_process_cool_yet(self) -> bool:
        '''
        Получения статуса "безошибочности" процесса, который логировался.

        :return: True - не было сообщений уровня Warning или выше; False - были
        '''
        for key in self.__error_counter.keys():
            if key >= 30 and self.__error_counter[key] != 0:  # Если есть ошибка
                return False
        return True

    # ---------------------------------------------------------------------------------------------
    # Проваленные сообщения  ----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def are_messages_cool_yet(self) -> bool:
        '''
        Получения статуса "безошибочности" отправки сообщений, которые логировались

        :return: True - не было сообщений, проваленых воркерами; False - были
        '''
        if not self._FailedMessages.fails_amount:  # Если количество упавших сообщений ноль
            return True
        else:
            return False  # Если более нуля сообщений провалены хоть одним воркером

    @property
    def _FailedMessages(self) -> FailedMessages:
        '''
        Получение контейнра првоаленных сообщений

        :return: объект со списком упавшиъх сообщений
        '''
        return self.__failed_messages

    # ---------------------------------------------------------------------------------------------
    # Писатели лога -------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def writers_dict(self) -> dict:
        '''
        Отдаёт словарь модулей, пишущих лог.

        :return: Словарь tuple-ов {name: (writer, logging_function)}
        '''
        return self.__writers_dict.copy()

    def add_writer(self, writer: object, name: int or str,
                   function_name: str = 'to_log') -> bool or None:
        '''
        Функция добавляет объект, пищущий лог.

        :param writer: писатель
        :param name: имя писателя
        :param function_name: имя функции, выполняющей логирование.
        :return: статус добавления: True - всё ок, Fasle - имя занято,
            None - ошибка типа (нет указанной функции логирования).
        '''
        try:  # Валидация
            logging_function = writer.__getattribute__(name=function_name)
        except AttributeError:  # Если нет функции логирования
            return None

        if name not in self.__writers_dict.keys():  # Првоерим в списке
            self.__writers_dict[name] = (writer, logging_function)
            return True
        else:
            return False

    def drop_writer(self, name: int or str) -> bool:
        '''
        Функция сбрасывает объект, пищущий лог, имеющий указанное имя.

        :param name: имя писателя
        :return: статус: True - был, удалён; False - такого писателя не было.
        '''
        try:  # Дропаем
            self.__writers_dict.pop(name)
            return True
        except KeyError:  # Если имени нет
            return False

    # ---------------------------------------------------------------------------------------------
    # Формирование "под имени"  -------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def create_subname(child_name: str, parent_name: str = None) -> str:
        '''
        Функция создаёт "стандартную" структуру имён модулей, отвечающую их запускам.

        :param child_name: имя "дочернего" модуля.
        :param parent_name: имя "подительского" модуля. Может быть незадано.
        :return: строка полного форматного подъимени.
        '''
        if parent_name is None:
            return child_name
        else:
            if not child_name.startswith(parent_name):  # Если название родителя ещё не включено
                return f'{parent_name}.{child_name}'
            else:  # Если название родителя уже есть в начале
                return child_name  # значит, имя уже форматное

    # ---------------------------------------------------------------------------------------------
    # Функция логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def to_log(self, message: str,
               function_name: str or bool = True,
               submodule_name: str = None,
               logging_level: int or str = 'DEBUG',
               logging_data: object = None,
               exception: tuple or bool = True,
               trace: list or bool = False,
               **kwargs) -> bool or None:
        '''
        Функция для отправки сообщений на сервер логирования.

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param logging_level: тип сообщения в лог. Число или:
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
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: статус отправки сообщения: True - все успешно, False - кто-то упал, None - ушло только
            в контенер с проваленными.
        '''

        DTO = self._prepare_dto(message=message,
                                function_name=function_name,
                                submodule_name=submodule_name,
                                logging_level=logging_level,
                                logging_data=logging_data,
                                exception=exception,
                                trace=trace,
                                **kwargs)

        result = self._send_dto(dto=DTO)

        return result

    # ---------------------------------------------------------------------------------------------
    # Обработка сообщения -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def _prepare_dto(self, message: str,
                     function_name: str or bool = True,
                     submodule_name: str = None,
                     logging_level: int or str = 'DEBUG',
                     logging_data: object = None,
                     exception: tuple or bool = True,
                     trace: list or bool = False,
                     **kwargs) -> dict:
        '''
        Функция для подготовки форматного DTO для сообщения

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param logging_level: тип сообщения в лог. Число или:
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
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: словарь на отправку
        '''

        logging_level = int_logging_level(logging_level=logging_level, default_level=self.default_logging_level)

        self.__add_message_count(logging_level=logging_level)  # крутанём счётчик

        # Скорректируем уровень лога, если нужно
        if exception is not False:  # Если переданы данные об исключении
            if logging_level in ['DEBUG', 'INFO']:  # Если уровень логирования низок
                logging_level = 'WARNING'  # Ставим "WARNING", так как в общем случае exception не всегда ERROR

        # Выполним развёртку exception и traceback
        exception = prepare_exception(exception_mistake=exception)
        if exception is not None:  # Если исключение есть
            trace = exception[1]  # отделили след
            exception = exception[0]  # отделили сообщение
        else:  # Если исключения нет
            # Делаем след опционально
            trace = prepare_trace(trace=trace, drop_last=2)  # Сбросим себя и "to_log" из следа

        if function_name is False:
            function_name = None
        elif function_name is True:  # Если надо определить имя функции
            function_name = get_function_name(drop_last=2)  # Берём имя "без себя" и "без функции логирования"
        elif isinstance(function_name, str):
            pass

        logging_dto = {}  # DTO объект

        logging_dto['time'] = str(datetime.datetime.now())
        logging_dto['logging_level'] = int_logging_level(logging_level=logging_level,
                                                         default_level=self.default_logging_level)
        logging_dto['main_module_name'] = self.main_module_name
        logging_dto['submodule_name'] = submodule_name
        logging_dto['process_name'] = self.process_name
        logging_dto['session_name'] = self.session_name

        logging_dto['message'] = message
        logging_dto['request_trimmed'] = False  # был ли запрос "сокращён"

        logging_dto['function_name'] = function_name

        logging_dto['exception'] = exception
        logging_dto['trace'] = trace

        logging_dto['logging_data'] = logging_data

        logging_dto['additional_data'] = kwargs

        return logging_dto

    def _send_dto(self, dto: dict) -> bool or None:
        '''
        Функция отдаёт DTO в воркеры для логирования.

        :param dto: DTO, уходящий в лог
        :return: статус отправки сообщения: True - все успешно, False - кто-то упал, None - ушло только
            в контенер с проваленными.
        '''

        if not len(self.__writers_dict):  # Если словарь пуст
            self._FailedMessages.add_message(workers_names=self.__class__.__name__, message=dto)
            # Логируем, что сам модуль закосячил (некому логировать)
            return None

        missed_workers = []  # список с именами райтеров, которые не отправили DTO
        for name in self.__writers_dict.keys():
            try:
                send_result = self.__writers_dict[name][1](**dto)  # Отправляем через функцию форкера
                well_done = send_result
            except BaseException:
                well_done = False

            if not well_done:  # Если завалено
                missed_workers.append(name)  # запомним
                # Пробуем отправить "основные данные"
                first_keep = ['time', 'logging_level',
                              'main_module_name', 'process_name', 'session_name',
                              'message']
                for key in list(dto.keys()):  # Проверим первичность ключа
                    if not key in first_keep:
                        dto.pop(key)  # Если не основной - сбрасываем
                dto['request_trimmed'] = True  # Метим, что запрос сокращён

                try:
                    self.__writers_dict[name][1](**dto)  # Отправляем через функцию форкера
                except BaseException:
                    pass

        if len(missed_workers):  # Если длина списка не ноль (но воркеры были)
            self._FailedMessages.add_message(workers_names=missed_workers, message=dto)
            if len(missed_workers) < len(self.writers_dict.keys()):
                return False
            else:
                return None
        else:
            return True

# ------------------------------------------------------------------------------------------------
# Получение логера и имени модуля ----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
def prepare_logger(class_name: str,
                   logger: CommonLoggingClient = None, parent_name: str = None) -> tuple:
    '''
    Функция определяет для класса логгер, "имя класса в текущей структуре" и функцию логирования.
        Это требуется для того, чтобы в поддерживаемом виде инсталировать логгер и сопутсвтующие функции у объектов.
        Объекты, полученные в результате работы, устанавливаются в self как: __Logger, _my_name
        и __to_log соответтсвенно.

    Методы и свойства:
        Логирование
            _Logger - логгер

            _sub_module_name - "под имя", использующееся при логировании

            _to_log - функция логирования

    Параметры в init:
        (logger: CommonLoggingClient = None, parent_name: str = None)

    Описание:
        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.

    Запуск в init
        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)
        # При наследовании
        # logger=self.__Logger, parent_name=self.__my_name,

    property
    # ------------------------------------------------------------------------------------------------
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def _Logger(self) -> CommonLoggingClient:
        ' ''
        Логер, использующийся в объекте

        :return: логер
        ' ''
        return self.__Logger

    @property
    def _to_log(self) -> object:
        ' ''
        Отдаёт функцию логирования, которая используется в работе

        :return: функция
        ' ''
        return self.__to_log

    @property
    def _my_name(self) -> str:
        ' ''
        Отдаёт строку с полным структурным навзванием модуля

        :return: строку
        ' ''
        return self.__my_name


    :param class_name: название класса, для которого выполняется подготовка
    :param logger: логер. Если логер не указан, будет добавлен собственный
    :param parent_name: имя "подмодуля", присвоенное данному коммуникатору. Если не указано - не используется.
    :return: tuple с объектами: (__Logger, _my_name, __to_log)
    '''
    # сформируем имя модуля
    my_name = CommonLoggingClient.create_subname(child_name=class_name,
                                                 parent_name=parent_name)

    if isinstance(logger, CommonLoggingClient):  # если подан логер
        Logger = logger

        # Сделаем обёртку на функцию логирования
        def logging_function(message: str,
                             function_name: str or bool = True,
                             logging_level: int or str = 'DEBUG',
                             logging_data: object = None,
                             exception: tuple or bool = True,
                             trace: list or bool = False,
                             **kwargs) -> bool or None:
            '''
            Функция для отправки сообщений на сервер логирования.

            :param message: сообщение для логирования
            :param function_name: имя вызывающей функции
            :param logging_level: тип сообщения в лог. Число или:
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
                обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
            :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
                всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
                Если этот параметр не False, то trace игнорируется
            :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
                следа внутри функции. Если задан exception_mistake, то trace игнорируется.
            :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
                совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
            :return: статус отправки сообщения: True - все успешно, False - кто-то упал, None - ушло только
                в контенер с проваленными.
            '''
            return Logger.to_log(message=message,
                                 function_name=function_name,
                                 submodule_name=my_name,
                                 logging_level=logging_level,
                                 logging_data=logging_data,
                                 exception=exception,
                                 trace=trace,
                                 **kwargs)

    else:  # Если логер не подан
        Logger = CommonLoggingClient(main_module_name=my_name)  # Создаём логер ЭТОГО ОБЪЕКТА
        # Если бы мы хотели логер родителя - мы бы дали логер родителя

        # возьмём функцию от логера
        logging_function = Logger.to_log


    return Logger, logging_function, my_name


def create_to_log_wrapper(logging_function: object,
                          submodule_name: str) -> object:
    '''
    Функция делает обёртку на функцию логирования, фиксируя "имя подмодуля".

    :param logging_function: функция типа Logger.to_log
    :param submodule_name: имя подмодуля
    :return: функция с фиксированным именем подмодуля
    '''

    # Сделаем обёртку на функцию логирования
    def logging_wrapper(message: str,
                        function_name: str or bool = True,
                        logging_level: int or str = 'DEBUG',
                        logging_data: object = None,
                        exception: tuple or bool = True,
                        trace: list or bool = False,
                        **kwargs) -> bool or None:
        '''
        Функция для отправки сообщений на сервер логирования.

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param logging_level: тип сообщения в лог. Число или:
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
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: статус отправки сообщения: True - все успешно, False - кто-то упал, None - ушло только
            в контенер с проваленными.
        '''
        return logging_function(message=message,
                                function_name=function_name,
                                submodule_name=submodule_name,
                                logging_level=logging_level,
                                logging_data=logging_data,
                                exception=exception,
                                trace=trace,
                                **kwargs)

    return logging_wrapper


