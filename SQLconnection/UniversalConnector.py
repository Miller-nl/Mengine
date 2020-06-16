'''
Модуль для общения с БД

'''

import pymysql
import psycopg2
import sqlite3

from ..Logging.CommonFunctions.ForFailedMessages import FailedMessages
from ..Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger

# ------------------------------------------------------------------------------------------------
# Общие штуки ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

update_statements = ['CREATE', 'DROP', 'ALTER', 'INSERT', 'DELETE', 'UPDATE']

# ------------------------------------------------------------------------------------------------
# Коннектор --------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class RemoteConnectionData:
    '''
    Объект, хранящий данные для удалённого подключения к базе данных: драйвер, адрес, авторизацию.
    Если объект используется для подключения к локальной БД, то у него заданы только движок и каталог.


    Методы и свойства:
        engine - название движка, на котором работает база (PostgreSQL, MySQL, SQLite). Без версии

        base_name - имя базы данных

        catalog - каталог базы

        host - хост

        port - порт

        user - пользователь

        password - пароль

        server - host:port

        authorization - "пользователь:пароль"
    '''

    def __init__(self,
                 engine: str,
                 base_name: str = None,
                 catalog: str = None,
                 host: str = None, port: str or int = None,
                 user: str = None, password: str = None):
        '''

        :param engine: название движка, на котором работает база (PostgreSQL, MySQL, SQLite). Без версии
        :param base_name: имя базы
        :param catalog: каталог с файлом базы для SQLite
        :param host: адрес
        :param port: порт
        :param user: пользователь
        :param password: пароль
        '''

        self.__engine = engine
        self.__base_name = base_name
        self.__catalog = catalog
        self.__host = host
        if port is None:
            self.__port = port
        else:
            self.__port = int(port)
        self.__user = user
        self.__password = password

    # ------------------------------------------------------------------------------------------------
    # Доступы ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def engine(self) -> str:
        '''
        Движок, на котором работает база.

        :return: название движка без версии (PostgreSQL, MySQL)
        '''
        return self.__engine

    @property
    def base_name(self) -> str or None:
        '''
        Имя базы

        :return:
        '''
        return self.__base_name

    @property
    def catalog(self) -> str or None:
        '''
        Для SQLite это каталог базы

        :return: строка с каталогом
        '''
        return self.__catalog

    @property
    def host(self) -> str or None:
        '''
        Хост

        :return:
        '''
        return self.__host

    @property
    def port(self) -> int or None:
        '''
        Порт в виде строки

        :return:
        '''
        return self.__port

    @property
    def user(self) -> str or None:
        '''
        имя пользователя

        :return:
        '''
        return self.__user

    @property
    def password(self) -> str or None:
        '''
        пароль

        :return:
        '''
        return self.__password

    @property
    def server(self) -> str:
        '''
        Отдаёт хост и порт

        :return: "хост:порт"
        '''
        return f'{self.host}:{self.port}'

    @property
    def authorization(self) -> str:
        '''
        Отдаёт пользователя и пароль

        :return: "пользователь:пароль"
        '''
        return f'{self.user}:{self.password}'

# ------------------------------------------------------------------------------------------------
# Коннектор --------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class SQLconnector:
    '''
    Модуль для обращения в SQL базы, используя драйвер.
    Допустимые движки:
        MySQL
        PostgreSQL
        SQLite


    В качестве движка может использоваться любой пакет, у которого есть следующие методы:
        connection = ПАКЕТ.connect(connection_data) - создать подключение
        cursor = connection.cursor()  - создаёт курсор
        connection.close() - закрыть соединение

        cursor.execute() - отправка запроса
        cursor.commit() - коммит запроса
        cursor.rollback() - откат запроса

        fetchall() - получить все запросы
        cursor.fetchmany(size=N) - получить первые N строк
        cursor.close() - закрыть курсор

    Методы и свойства

        Логирование:
            _Logger - логгер

            _my_name - "под имя", использующееся при логировании

            _to_log - функция логирования

        Упавшие запросы:
            _FailedMessages - контейнер упавших запросов или None, если он не требовался.

            _failed_requests_logging - сопровождать ли сообщение логеру упавшим запросом?

            _remember_only_failed_updates - добавлять ли в контейнер только упавшие запросы, относящиеся к обновлению
                информации в базе.



        Подключение:
            engine - название движка

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
                 connection_data: RemoteConnectionData,
                 logger: CommonLoggingClient = None, parent_name: str = None,
                 failed_requests_logging: bool = False,
                 remember_failed_requests: int or None = 1000, remember_only_failed_updates: bool = True):
        '''

        :param connection_data: данные для соединения с базой. Поумолчанию берётся дефолтная DB.
        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        :param failed_requests_logging: сопровождать ли сообщения в логер упавшими запросами?
        :param remember_failed_requests: сколько упавших запросов помнить в контейнере? 0 - все (не рекомендуется)
        :param remember_only_failed_updates: помнить ли сообщения, только касающиеся обновления базы?
            Рекомендуется - "да".
        '''

        self.__connection_data = connection_data  # заберём данные для соединения с базой
        self.__connection = None  # объект - детектор соединения

        self.__failed_requests_logging = failed_requests_logging
        self.__remember_only_failed_updates = remember_only_failed_updates

        if remember_failed_requests is None:  # Если контейнер задавать не нужно
            self.__FailedMessages = None
        else:  # Если нужно
            self.__FailedMessages = FailedMessages(maximum_list_length=remember_failed_requests)

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

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
    def _failed_requests_logging(self) -> bool:
        '''
        Показывает, добавляются ли упавшие запросы в сообщения логера.

        :return: статус
        '''
        return self.__failed_requests_logging

    @property
    def _remember_only_failed_updates(self) -> bool:
        '''
        Функция отдаёт статус необходимости сохранения только запросов, касающихся обновления базы.

        :return: True - запоминать только упавшие добавления/изменения, False - помнить всё.
        '''
        return self.__remember_only_failed_updates

    @property
    def _FailedMessages(self) -> FailedMessages or None:
        '''
        Отдаёт контейнер для упавших запроосв или None, если количество сообщений для контейнера было помечено
            как None.

        :return: контейнер упавших запросов, если он есть.
        '''
        return self.__FailedMessages

    def __log_request(self, request: str) -> None:
        '''
        Добавление упавшего запроса в контейнер

        :param request: запрос
        :return: ничего
        '''

        if self.__FailedMessages is None:  # Если нет контейнера
            return None

        if self._remember_only_failed_updates:  # Если запоминаем только запросы на обновление
            is_ok = False
            for operator in update_statements:  # Проверим запрос
                if request.startswith(operator):  # Если запрос начинается с нужного оператора
                    is_ok = True  # детектим
                    break

            if not is_ok:
                return None

        self.__FailedMessages.add_message(workers_names=self._my_name,
                                          message=request)
        return None

    # ------------------------------------------------------------------------------------------------
    # Движок -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def engine(self) -> str:
        '''
        Возворащает название драйвера, который используется.

        :return: строка - название.
        '''

        return self.connection_data.engine

    def __create_connection(self):
        '''
        Функция создаёт соединение, устанавливая его в self._connection.
        Она нужна для того, чтобы обеспечить разные наборы праметров для разных пакетов.

        :return: объект соединения.
        '''

        engine = self.connection_data.engine

        if engine == 'MySQL':
             return pymysql.connect(host=self.connection_data.host,
                                    port=self.connection_data.port,
                                    user=self.connection_data.user,
                                    password=self.connection_data.password,
                                    database=self.connection_data.base_name
                                    )  # законектились
        elif engine == 'PostgreSQL':
            return psycopg2.connect(host=self.connection_data.host,
                                    port=self.connection_data.port,
                                    user=self.connection_data.user,
                                    password=self.connection_data.password,
                                    dbname=self.connection_data.base_name
                                    )  # законектились
        elif engine == 'SQLite':
            return sqlite3.connect(database=self.connection_data.catalog)  # законектились

        else:
            self.__to_log(message=f'Создание коннектора провалено. Движок не опознан.',
                          logging_data={'engine': self.connection_data.engine},
                          logging_level='ERROR', trace=True)
            return None

    # ------------------------------------------------------------------------------------------------
    # Соединение с базой -----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def connected(self) -> bool:
        '''
        Статус подключённости к базе. Используется для внутренних проверок в том числе.

        :return: True - подключено, False - не подключено
        '''
        if self.__connection is None:  # если объекта подключения нет
            return False
        else:  # Если всё ок
            return True

    @property
    def connection_data(self) -> RemoteConnectionData:
        '''
        Отдаёт объект с данными о соединении с базой

        :return:
        '''
        return self.__connection_data

    def connect(self) -> bool or None:
        '''
        Функция подключается к базе. Даже в случае ошибки отключения, она отсоединится.

        :return: статус: True - Успешно подключились, False - уже подключены, None - ошибка.
        '''

        if self.connected:  # Если конект есть
            return False

        # Пробуем законнектиться
        try:
            self.__connection = self.__create_connection()  # пробуем законектиться

            if self.__connection is None:  # Если не удалось опознать движок (ошибка упадёт ниже)
                return None
            else:  # если всё ок
                return True

        except BaseException:
            self.__to_log(message=f'Подключение к базе провалено',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          logging_level='ERROR', exception_mistake=True)
            self.__connection = None  # ставим переменную на место
            return None

    def disconnect(self) -> bool or None:
        '''
        Отключение от базы

        :return: True - Успешно отключились, False - уже отключены, None - ошибка.
        '''
        if not self.connected:  # Если конекта уже нет
            return False

        try:
            self.__connection.close()  # закрыли соединение с базой
            self.__connection = None  # удалили объект соединения
            return True

        except BaseException :
            # Если отключиться не вышло, принудительно удадалим соединение
            self.__connection = None

            self.__to_log(message='Отключение от базы провалено. Объект соединения удалён.',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          logging_level='ERROR', exception_mistake=True)
            return None

    def reconnect(self) -> bool or None:
        '''
        Функция для переподключения к базе.

        :return: True - Успешно, соединение было, False - Успешно, соединения не было, None - ошибка (при соединении)
        '''
        if self.connected:  # Если подключение есть
            try:
                self.__connection.reset()  # Пробуем переподключиться
                result = True
            except BaseException:
                self.__connection = None # Чекаем отсутствие соединения
                self.__to_log(message='Переподключение к базе провалено',
                              logging_data={'engine': self.connection_data.engine,
                                            'base_name': self.connection_data.base_name,
                                            'server': self.connection_data.server,
                                            'user': self.connection_data.user},
                              logging_level='ERROR', exception_mistake=True)
                result = None  # Чекаем ошибку

        else:  # Если нет
            connect_status = self.connect()  # Создаём
            if connect_status:  # Если успешно
                result = False  # Чекаем статус - соединения не было, создано
            else:
                result = None  # чекаем ошибку

        return result  # Закончим

    # ------------------------------------------------------------------------------------------------
    # Выполнение запросов ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def request_commit(self, request: str) -> bool or None:
        '''
        Функция для передачи запросов в базу с коммитом.

        :param request: запрос к базе данных
        :return: True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита
        '''

        if not self.connected:  # Если соединения нет
            return False

        result = None  # дефолтный результат
        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            self.__connection.commit()  # Внесём изменения в базу
            result = True  # Вернём "успешность"

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass

            if not self._failed_requests_logging:  # Если запрос не логируется
                self.__log_request(request=request)  # положим сообщение в контейнер, если нужно
                request = self._failed_requests_logging  # заменим его
            self.__to_log(message='Отправка данных в базу провалена.',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
        finally:
            try:
                cursor.close()
            except BaseException:
                pass

        return result  # вернём статус

    def request_fetch_all(self, request: str) -> list or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ...]

        :param request: запрос
        :return: list - результат, False - нет соединения, None - ошибка.
        '''
        if not self.connected:  # Если соединения нет
            return False

        result = None  # дефолтный результат
        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchall()  # Получим ответ

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass

            if not self._failed_requests_logging:  # Если запрос не логируется
                self.__log_request(request=request)  # положим сообщение в контейнер, если нужно
                request = self._failed_requests_logging  # заменим его
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)

        finally:
            try:
                cursor.close()
            except BaseException:
                pass

        return result  # Вернём результат

    def request_fetch_many(self, request: str,
                           size: int = 1) -> list or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ... , (str_n)]

        :param request: запрос
        :param size: количество строк, которые будут извлечены
        :return: list - результат, False - нет соединения, None - ошибка.
        '''

        if not self.connected:  # Если соединения нет
            return False

        result = None  # дефолтный результат
        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchmany(size=size)  # Получим ответ

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass

            if not self._failed_requests_logging:  # Если запрос не логируется
                self.__log_request(request=request)  # положим сообщение в контейнер, если нужно
                request = self._failed_requests_logging  # заменим его

            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
        finally:
            try:
                cursor.close()
            except BaseException:
                pass

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
        if not self.connected:  # Если соединения нет
            return errors_placeholder

        result = errors_placeholder  # дефолтный результат
        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchone()[0]  # Получим ответ
            return result  # Вернём "успешность"

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass

            if not self._failed_requests_logging:  # Если запрос не логируется
                self.__log_request(request=request)  # положим сообщение в контейнер, если нужно
                request = self._failed_requests_logging  # заменим его
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'engine': self.connection_data.engine,
                                        'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
        finally:
            try:
                cursor.close()
            except BaseException:
                pass

        return result
