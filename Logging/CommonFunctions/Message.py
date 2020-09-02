import datetime

from .ExceptionAndTrace import prepare_exception, prepare_trace

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
        Сообщение
            message - само сообщение

            logging_level - уровень сообщения

            logging_data - основные данные, переданые из вызова

            additional_data - дополнительные данне, если требуются

            exception - данные исключения

            trace - данные следа

        Опознавательные данные
            process_name - имя процесса

            session_key - ключ сессии/запуска

            main_module_name - имя основного модуля

            submodule_name - имя "подмодуля"

            function_name - имя вызывающей функции

            time - время вызова

        Экспорт
            get_dict() - получить словарь с данными
    '''

    def __init__(self, message: str,
                 logging_level: int,
                 error_type: type or None = None,
                 main_module_name: str = None,
                 process_name: str = None,
                 session_key: str = None,
                 function_name: str or bool = True,
                 submodule_name: str = None,
                 logging_data: object = None,
                 exception: tuple or bool = True,
                 trace: list or bool = False,
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

        :param error_type: тип ошибки, если требуется.
        :param main_module_name: имя вызывающего модуля в процессе. Это имя, созданное менеджером процесса.
        :param process_name: имя процесса, в котором задействуется модуль (секция) (берётся у логера)
        :param session_key: ключ сессии или порядковый номер запуска, если требуется. (берётся у логера)
        :param submodule_name: имя подмодуля (берётся у отправщика сообщений)
        :param function_name: имя вызывающей функции (берётся у отправщика сообщений)
        :param logging_data: dto объект, который будет залогирован. Обычно содержит информацию о данных,
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :param drop_in_trace: сколько скинуть объектов с конца следа?
        '''

        self.__message = message
        self.__logging_level = logging_level

        self.__error_type = error_type

        # Установим след и исключение
        self.__exception, self.__trace = self.__prepare_exception_and_trace(exception=exception, trace=trace)

        # Подготовим имя функции
        self.__function_name = self.__prepare_function_name(function_name=function_name)

        # Опознавательные данные
        self.__process_name = process_name
        self.__session_key = session_key

        self.__main_module_name = main_module_name
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
                                      trace: list or bool = False):
        '''
        Функция подготавливает данные про след и исключение.

        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :return: exception - данные исключения (строка или None), trace - след (список или None).
        '''
        if exception is False:  # Если не требуется брать исключение
            exception = None  # Укажем его отсутствие

        # Выполним развёртку exception и traceback
        exception = prepare_exception(exception_mistake=exception)
        if exception is not None:  # Если исключение есть
            trace = exception[1]  # отделили след
            exception = exception[0]  # отделили сообщение
        else:  # Если исключения нет
            # Делаем след опционально
            if isinstance(trace, list):  # Если подан уже след
                pass
            elif trace is True:  # Если след набо брать
                # 3 - эта функция, и функции "вызова" сообщения кроме функции логирования
                trace = prepare_trace(trace=trace, drop_last=3 + self.__drop_in_trace)
            else:  # Если False
                trace = None

        return exception, trace

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
    # Сообщение -----------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def error_type(self) -> type or None:
        '''
        Отдаёт тип ошибки или None, если последний не указан.
        :return:
        '''
        return self.__error_type

    @property
    def message(self) -> str:
        '''
        Основное сообщение логера.

        :return:
        '''
        return self.__message

    @property
    def logging_level(self) -> int:
        '''
        Уровень логирования

        :return:
        '''
        return self.__logging_level

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

    @property
    def exception(self) -> str or None:
        '''
        Данные строка с описанием ошибки/исключения, если они есть.

        :return:
        '''
        return self.__exception

    @property
    def trace(self) -> list or None:
        '''
        Список - след вызова сообщения, если он задан

        :return:
        '''
        return self.__trace

    # ---------------------------------------------------------------------------------------------
    # Опознавательные данные ----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def process_name(self) -> str or None:
        '''
        Имя процесса

        :return:
        '''
        return self.__process_name

    @property
    def session_key(self) -> str or None:
        '''
        Ключ запуска сессии

        :return:
        '''
        return self.__session_key

    @property
    def main_module_name(self) -> str or None:
        '''
        Имя основного вызывающего модуля

        :return:
        '''
        return self.__main_module_name

    @property
    def submodule_name(self) -> str or None:
        '''
        Имя вызывающего подмодуля

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

    @property
    def time(self) -> str:
        '''
        Время создания сообщения

        :return:
        '''
        return self.__time

    # ---------------------------------------------------------------------------------------------
    # Экспорт -------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def get_dict(self, trimmed: bool = False) -> dict:
        '''
        Функция подготавливает словарь, если это требуется.
        :param trimmed: сократить ли сообщение? False - нет; True - исключить данные logging_data и additional_data
        :return: словарь
        '''
        export_dict = {}

        export_dict['time'] = self.time

        export_dict['process_name'] = self.process_name
        export_dict['session_key'] = self.session_key
        export_dict['main_module_name'] = self.main_module_name
        export_dict['submodule_name'] = self.submodule_name
        export_dict['function_name'] = self.function_name

        export_dict['message'] = self.message
        export_dict['logging_level'] = self.logging_level
        export_dict['exception'] = self.exception
        export_dict['trace'] = self.trace

        if not trimmed:  # Если отдавать всё
            export_dict['logging_data'] = self.logging_data
            export_dict['additional_data'] = self.additional_data

        export_dict['trimmed'] = trimmed

        return export_dict

