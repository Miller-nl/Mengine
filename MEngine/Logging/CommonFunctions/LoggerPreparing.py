from ..CommonLoggingClient import CommonLoggingClient, raise_exception

# ------------------------------------------------------------------------------------------------
# Получение логера и имени модуля ----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
def prepare_logger(class_name: str,
                   logger: CommonLoggingClient or bool = False, parent_name: str = None) -> tuple:
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
        :param logger: логер. True - создать новый, False и None - использовать raise.
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
                             error_type: type or None = None,
                             raise_error: bool = False,
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
            :param error_type: тип ошибки, если требуется.
            :param raise_error: поднять ли ошибку?
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
                                 error_type=error_type,
                                 raise_error=raise_error,
                                 logging_data=logging_data,
                                 exception=exception,
                                 trace=trace,
                                 **kwargs)

    elif logger is True:  # Если логер не подан, но надо создать
        Logger = CommonLoggingClient(main_module_name=my_name)  # Создаём логер ЭТОГО ОБЪЕКТА
        # Если бы мы хотели логер родителя - мы бы дали логер родителя

        # возьмём функцию от логера
        logging_function = Logger.to_log

    elif (logger is False) or (logger is None):
        Logger = None
        logging_function = raise_exception

    else:
        raise ValueError(f'logger value is incorrect: {logger}. Expected bool or None or CommonLoggingClient.')

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
                        error_type: type or None = None,
                        raise_error: bool = False,
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
        :param error_type: тип ошибки, если требуется.
        :param raise_error: поднять ли ошибку?
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
                                error_type=error_type,
                                raise_error=raise_error,
                                logging_data=logging_data,
                                exception=exception,
                                trace=trace,
                                **kwargs)

    return logging_wrapper


