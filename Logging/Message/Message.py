import datetime

from Logging.Message.ExceptionAndTrace import prepare_exception, prepare_trace

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
# Сообщение логирования --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class Message:
    '''
    Объект, реализующий DTO для сообщений.
    Методы и свойства:
        Identification
            app_name
            launch_key
            processing_key
            submodule_name
            function_name
            identification() - Get all identification parameters

        Message
            time
            logging_level
            message
            main_message() - Get all message parameters

        Data
            logging_data
            additional_data
            all_log_data() - Get all data parameters

        Exception
            error_type
            exception_message
            trace
            exception_data() - Get all exception_message parameters


        Сообщение
            message - само сообщение

            logging_level - уровень сообщения

            logging_data - основные данные, переданые из вызова

            additional_data - дополнительные данне, если требуются

            exception_message - данные исключения

            trace - данные следа

        Опознавательные данные
            app_name - имя основного модуля

            launch_key - ключ сессии/запуска логгера

            processing_key - имя процесса обработки в приложении



            submodule_name - имя "подмодуля"

            function_name - имя вызывающей функции

            time - время вызова

        Экспорт
            get_dict() - получить словарь с данными
    '''

    def __init__(self, message: str,
                 logging_level: int,

                 app_name: str = None,
                 launch_key: str = None,
                 processing_key: str = None,

                 function_name: str or bool = True,
                 submodule_name: str = None,

                 logging_data: object = None,

                 exception: tuple or bool = True,
                 trace: list or bool = False,
                 error_type: type or None = None,

                 drop_in_trace: int = 2,
                 **kwargs):
        '''

        :param message: сообщение для логирования
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

        :param app_name: имя приложения
        :param launch_key: ключ запуска приложения
        :param processing_key: ключ конкретного процесса обработки в приложении
        :param submodule_name: имя подмодуля (берётся у отправщика сообщений)
        :param function_name: имя вызывающей функции (берётся у отправщика сообщений)
        :param logging_data: dto объект, который будет залогирован. Обычно содержит информацию о данных,
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param error_type: тип ошибки, если требуется. Игнорируется, если используется exception.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :param drop_in_trace: сколько скинуть объектов с конца следа?
        '''

        self.__message = message
        self.__logging_level = logging_level

        # Установим след и исключение
        error_type, exception_message, trace = self.__prepare_exception_and_trace(exception=exception,
                                                                                  error_type=error_type,
                                                                                  trace=trace)
        self.__error_type = error_type
        self.__trace = trace
        self.__exception_message = exception_message

        # Подготовим имя функции
        self.__function_name = self.__prepare_function_name(function_name=function_name)

        # Опознавательные данные
        self.__app_name = app_name
        self.__launch_key = launch_key

        self.__processing_key = processing_key
        self.__submodule_name = submodule_name

        self.__time = str(datetime.datetime.now())

        # Данные
        self.__logging_data = logging_data
        self.__additional_data = kwargs

        self.__drop_in_trace = drop_in_trace


    # ---------------------------------------------------------------------------------------------
    # Подготовка параметров -----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def __prepare_exception_and_trace(self,
                                      exception: tuple or bool = True,
                                      error_type: type or None = None,
                                      trace: list or bool = False):
        '''
        Функция подготавливает данные про след и исключение.

        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: error_type явно переданный тип ошибки. Игнорируется, если используется exception
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :return: error_type, exception_message - данные исключения (строка или None), trace - след (список или None).
        '''
        if exception is False:  # Если не требуется брать исключение
            exception = None  # Укажем его отсутствие

        # Выполним развёртку exception_message и traceback
        exception = prepare_exception(exception_mistake=exception)

        if exception is not None:  # Если исключение есть
            error_type = exception[0]
            exception_message = exception[1].args[0]
            trace = exception[2]  # отделили след

        else:  # Если исключения нет
            exception_message = None

            # Делаем след опционально
            if isinstance(trace, list):  # Если подан уже след
                pass
            elif trace is True:  # Если след набо брать
                # 3 - эта функция, и функции "вызова" сообщения кроме функции логирования
                trace = prepare_trace(trace=trace, drop_last=3 + self.__drop_in_trace)
            else:  # Если False
                trace = None

        return error_type, exception_message, trace

    def __prepare_function_name(self, function_name: str or bool = True) -> str or None:
        '''
        Функция подготавливает имя функции, вызывающей сообщение.

        :param function_name: имя вызывающей функции или запрос/отказ от её логирования.
        :return: имя функции
        '''
        if function_name is True:  # Если надо определить имя функции
            return get_function_name(drop_last=2)  # Берём имя "без себя" и "без функции логирования"
        elif isinstance(function_name, str):
            return function_name
        else:
            return None

    # ---------------------------------------------------------------------------------------------
    # identification ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def app_name(self) -> str or None:
        '''
        Имя приложения

        :return:
        '''
        return self.__app_name

    @property
    def launch_key(self) -> str or None:
        '''
        Ключ запуска приложения

        :return:
        '''
        return self.__launch_key

    @property
    def processing_key(self) -> str or None:
        '''
         ключ конкретного процесса обработки в приложении

        :return:
        '''
        return self.__processing_key

    @property
    def submodule_name(self) -> str or None:
        '''
        Имя вызывающего подмодуля приложения

        :return:
        '''
        return self.__submodule_name

    @property
    def function_name(self) -> str or None:
        '''
        Имя вызывающей функции

        :return:
        '''
        return self.__function_name

    def identification(self) -> dict:
        '''
        returns identification data
        :return:
        '''
        identification = {'app_name': self.app_name,
                          'launch_key': self.launch_key,
                          'processing_key': self.processing_key,
                          'submodule_name': self.submodule_name,
                          'function_name': self.function_name}
        return identification

    # ---------------------------------------------------------------------------------------------
    # Message -------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def time(self) -> str:
        '''
        Время создания сообщения

        :return:
        '''
        return self.__time

    @property
    def logging_level(self) -> int:
        '''
        Уровень логирования

        :return:
        '''
        return self.__logging_level

    @property
    def message(self) -> str:
        '''
        Основное сообщение логера.

        :return:
        '''
        return self.__message

    def main_message(self) -> dict:
        '''

        :return:
        '''
        message = {'time': self.time,
                   'logging_level': self.logging_level,
                   'error_type': self.error_type,
                   'message': self.message}
        return message

    # ---------------------------------------------------------------------------------------------
    # Log Data ------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def logging_data(self) -> dict or str or list:
        '''
        Отдаёт переданную в качестве основных данных логирования информацию

        :return:
        '''
        return self.__logging_data

    @property
    def additional_data(self) -> dict:
        '''
        Переданные "дополнительные" данные.

        :return:
        '''
        return self.__additional_data

    def all_log_data(self) -> dict:
        log_data = {'logging_data': self.logging_data, 'additional_data': self.additional_data}
        return log_data

    # ---------------------------------------------------------------------------------------------
    # Exception Data ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def error_type(self) -> type or None:
        '''
        Отдаёт тип ошибки или None, если последний не указан.
        :return:
        '''
        return self.__error_type

    @property
    def exception_message(self) -> str or None:
        '''
        Данные строка с описанием ошибки/исключения, если они есть.

        :return:
        '''
        return self.__exception_message

    @property
    def trace(self) -> list or None:
        '''
        Список - след вызова сообщения, если он задан

        :return:
        '''
        return self.__trace

    def exception_data(self) -> dict:
        exception_data = {'error_type': self.error_type,
                          'exception_message': self.exception_message,
                          'trace': self.trace}
        return exception_data

    # ---------------------------------------------------------------------------------------------
    # Экспорт -------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def get_dict(self,
                 main_message: bool = True,
                 identification: bool = True,
                 all_log_data: bool = True,
                 exception_data: bool = True) -> dict:
        '''
        Prepares a dictionary with message parameters

        :param main_message:
        :param identification:
        :param all_log_data:
        :param exception_data:
        :return:
        '''
        export_dict = {}

        if main_message:
            export_dict = {**export_dict, **self.main_message()}

        if identification:
            export_dict = {**export_dict, **self.identification()}

        if all_log_data:
            export_dict = {**export_dict, **self.all_log_data()}

        if exception_data:
            export_dict = {**export_dict, **self.exception_data()}

        return export_dict

