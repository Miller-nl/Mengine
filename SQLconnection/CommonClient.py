'''
Стандартный интерфейс:

        # Подключение

        connected - подключена ли база

        connection_data - объект, содержащий авторизационные данные

        connect() -> подключение

        disconnect() -> отключение

        reconnect() ->  переподключение

        # Запросы

        request_commit() - отправка запроса в базу

        request_fetch_all() - получает все строки по запросу

        request_fetch_many() - получает указанное количество строк по запросу

        request_fetch_value() - получает нулевое значение нулевой строки


        _mistakes - список ошибок, полученных при работе с каталогами (.append(sys.exc_info()))

'''

'''
Сделать текущий класс как обёртку для работы с БД
'''
from ..Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger
from ..Logging.CommonFunctions.ForFailedMessages import FailedMessages

from .SQLworkers.RemoteConnectionData import RemoteConnectionData, DefaultDB

from .SQLworkers.PostgreSQL import PostgreSQLconnector
from .SQLworkers.MySQL import MySQLconnector
from .SQLworkers.LiteSQL import SQLiteConnector



class SQLcommunicator:
    '''
    Это обёртка над Postgres или MySQL, которая будет использоваться в работе.
    Цель - исключить проблемы при смене базы даже в случае перехода на иные Worker-ы типа Кликхауса.

    Методы и свойства:


        Логирование
            _Logger - логер

            _my_name - "под имя", использующееся при логировании

            _to_log - сообщение в лог от имени модуля

            _FailedMessages - контейнер упавших запросов. Получить сообщения можно через "failed_requests".

            _remember_only_update - логировались ли только запросы, обновляющие базу?

        Исполнитель:
            engine - драйвер, с которым раотаем (PostgreSQL, MySQL)

            _Worker - объект, соединяющий с базой

        Подключение:
            connected - подключена ли база

            connection_data - объект, содержащий авторизационные данные (RemoteConnectionData)

            connect() -> подключение

            disconnect() -> отключение

            reconnect() ->  переподключение

        Запросы:
            request_commit() - отправка запроса в базу

            request_fetch_all() - получает все строки по запросу

            request_fetch_many() - получает указанное количество строк по запросу

            request_fetch_value() - получает нулевое значение нулевой строки

    '''

    def __init__(self,
                 connection_data: RemoteConnectionData = DefaultDB,
                 logger: CommonLoggingClient = None, parent_name: str = None,
                 failed_requests_logging: bool = True,
                 remember_failed_requests: int = 1000, remember_only_update: bool = True):
        '''

        :param connection_data: данные для соединения с базой. Поумолчанию берётся дефолтная DB.
        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        :param failed_requests_logging: сопровождать ли сообщения об ошибках в исполнителе запросами?
        :param remember_failed_requests: сколько упавших запросов помнить в контейнере? 0 - все (не рекомендуется)
        :param remember_only_update: помнить ли сообщения, только касающиеся обновления базы?
            Рекомендуется - "да".
        '''

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

        # Установим Worker
        self.__ser_worker(connection_data=connection_data, failed_requests_logging=failed_requests_logging)

        self.__FailedMessages = FailedMessages(maximum_list_length=remember_failed_requests)
        self.__remember_only_update = remember_only_update

    # ------------------------------------------------------------------------------------------------
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def _Logger(self) -> CommonLoggingClient:
        '''
        Логер, использующийся в объекте

        :return: логер
        '''
        return self.__Logger

    @property
    def _to_log(self) -> object:
        '''
        Отдаёт функцию логирования, которая используется в работе

        :return: функция
        '''
        return self.__to_log

    @property
    def _my_name(self) -> str:
        '''
        Отдаёт строку с полным структурным навзванием модуля

        :return: строку
        '''
        return self.__my_name

    # ------------------------------------------------------------------------------------------------
    # Упавшие запросы --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def _FailedMessages(self) -> FailedMessages:
        '''
        Контейнер упавших запросов. В качестве имени - имя БД, к которой обращались

        :return:
        '''
        return self.__FailedMessages

    @property
    def _remember_only_update(self) -> bool:
        '''
        Указывает, какой тип запросов сохранялся в контейнер: только на обновление или все.

        :return: bool статус
        '''
        return self.__remember_only_update

    def __log_request(self, request: str):
        '''
        Добавление упавшего запроса в контейнер

        :param request: запрос
        :return: ничего
        '''
        if self._remember_only_update:  # Если запоминаем только запросы на обновление
            is_ok = False
            for operator in update_statements:  # Проверим запрос
                if request.startswith(operator):  # Если запрос начинается с нужного оператора
                    is_ok = True  # детектим
                    break

            if not is_ok:
                return

        self.__FailedMessages.add_message(workers_names=self.connection_data.base_name,
                                          message=request)
        return

    # ------------------------------------------------------------------------------------------------
    # Установка исполнителя --------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def __ser_worker(self, connection_data: RemoteConnectionData, failed_requests_logging: bool):
        '''
        Функция создаёт исполнителя для подключения к базе и подключается к ней.

        :param connection_data: объект с данными для подключения и выбора исполнителя
        :param failed_requests_logging: сопровождать ли сообщения об ошибках в исполнителе запросами?
        :return: ничего
        '''
        self.__Worker = None

        if connection_data.engine == 'PostgreSQL':
            self.__Worker = PostgreSQLconnector(connection_data=connection_data,
                                                logger=self._Logger, parent_name=self.__my_name,
                                                requests_logging=failed_requests_logging)
        elif connection_data.engine == 'MySQL':
            self.__Worker = MySQLconnector(connection_data=connection_data,
                                           logger=self._Logger, parent_name=self.__my_name,
                                           requests_logging=failed_requests_logging)

        elif connection_data.engine == 'SQLite':
            self.__Worker = SQLiteConnector(connection_data=connection_data,
                                            logger=self._Logger, parent_name=self.__my_name,
                                            requests_logging=failed_requests_logging)

        else:  # Если не опознан исполнитель
            self.__to_log(message='Исполнитель не опознан',
                          logging_data={'engine': connection_data.engine},
                          logging_level='ERROR')
            return

        self.__to_log(message='Исполнитель успешно установлен',
                      logging_data={'engine': connection_data.engine}
                      )

        # Выполним подключение к базе
        if self.connect() is None:
            self.__to_log(message='Подключение провалено.',
                          logging_data={'engine': connection_data.engine, 'base_name': connection_data.base_name,
                                       'server': connection_data.server},
                          logging_level='ERROR')

        else:  # Если подключились успешно
            self.__to_log(message='Подключение успешно выполнено',
                          logging_data={'engine': connection_data.engine, 'base_name': connection_data.base_name,
                                       'server': connection_data.server}
                          )
        return

    # ------------------------------------------------------------------------------------------------
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------------
    # Исполнитель и его методы -----------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def engine(self) -> str:
        '''
        Отдаёт название драйвера

        :return:
        '''
        return self._Worker.connection_data.engine

    @property
    def _Worker(self):
        '''
        Получение объекта, выполняющего запросы.

        :return:
        '''
        return self.__Worker

    @property
    def connected(self) -> bool:
        '''
        Статус подключённости к базе.

        :return: True - подключено, False - не подключено
        '''
        return self.__Worker.connected

    @property
    def connection_data(self) -> RemoteConnectionData:
        '''
        Отдаёт объект с данными о соединении с базой

        :return:
        '''
        return self.__Worker.connection_data

    def connect(self) -> bool or None:
        '''
        Функция подключается к базе. Даже в случае ошибки отключения, она отсоединится.

        :return: статус: True - Успешно подключились, False - уже подключены, None - ошибка.
        '''
        return self.__Worker.connect()

    def disconnect(self) -> bool or None:
        '''
        Отключение от базы

        :return: True - Успешно отключились, False - уже отключены, None - ошибка.
        '''
        return self.__Worker.disconnect()

    def reconnect(self) -> bool or None:
        '''
        Функция для переподключения к базе.

        :return: True - Успешно, соединение было, False - Успешно, соединения не было, None - ошибка (при соединении)
        '''
        return self.__Worker.reconnect()

    def request_commit(self, request: str) -> bool or None:
        '''
        Функция для передачи запросов в базу с коммитом.

        :param request: запрос к базе данных
        :return: True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита
        '''
        result = self.__Worker.request_commit(request=request)
        if result is None:
            self.__log_request(request=request)
        return result

    def request_fetch_all(self, request: str) -> list or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ...]

        :param request: запрос
        :return: list - результат, False - нет соединения, None - ошибка.
        '''
        result = self.__Worker.request_fetch_all(request=request)
        if result is None:
            self.__log_request(request=request)
        return result

    def request_fetch_many(self, request: str,
                           size: int = 1) -> list or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ... , (str_n)]

        :param request: запрос
        :param size: количество строк, которые будут извлечены
        :return: list - результат, False - нет соединения, None - ошибка.
        '''
        result = self.__Worker.request_fetch_many(request=request, size=size)
        if result is None:
            self.__log_request(request=request)
        return result

    def request_fetch_value(self, request: str,
                            errors_placeholder: object = None) -> object:
        '''
        Функция получает первое (нулевое) значение первой (нулевой) строки из ответа и возвращат его.
        Нужна для удобства, чтобы можно было легко запросить "количество", "минимум"/"максимум" и прочие подобные
            величины.

        :param request: запрос
        :param errors_placeholder: "заменитель" ошибки. Актуален потому, что значение может быть и None.
            Но "поумолчанию" подразумевается, что единственное запрашиваемое значение не должно быть None.
        :return: "нулевое" значение "нулевой" строки или errors_placeholder в случае ошибки. Отсутствие соединения
            тоже будет считаться ошибкой.
        '''
        result = self.__Worker.request_fetch_value(request=request, errors_placeholder=errors_placeholder)
        if result == errors_placeholder:
            self.__log_request(request=request)
        return result

    # ------------------------------------------------------------------------------------------------
    # "Чистые" запросы к базе ------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    # Запросы к временным таблицам базы --------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    '''
    Сделать как отдельную функцию вообще.
    '''
    # ------------------------------------------------------------------------------------------------
    # Функции миграции -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

