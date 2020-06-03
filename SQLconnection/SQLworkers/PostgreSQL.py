'''
Модуль для общения с PostgreSQL

'''

import psycopg2

from ..SQLworkers.RemoteConnectionData import RemoteConnectionData
from ...Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger

# ------------------------------------------------------------------------------------------------
# Выполнение запросов ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class PostgreSQLconnector:
    '''
    Модуль для обращения в PostgerSQL базу.

    Методы и свойства
        Логирование:
            _Logger - логгер

            _my_name - "под имя", использующееся при логировании

            _to_log - функция логирования

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
                 connection_data: RemoteConnectionData,
                 logger: CommonLoggingClient = None, parent_name: str = None,
                 requests_logging: bool = False):
        '''

        :param connection_data: данные для коннекта к базе
        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        :param requests_logging: логировать ли упавшие запросы в журнал? По дефолту - нет.
        '''

        self.__connection_data = connection_data  # заберём данные для соединения с базой

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

        self.__requests_logging = requests_logging

        self.__connected = False  # Переменная, разрешающая/запрещающая работу с запросами


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
    # Соединение с базой -----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def connected(self) -> bool:
        '''
        Статус подключённости к базе.

        :return: True - подключено, False - не подключено
        '''
        return self.__connected

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
            self.__connection = psycopg2.connect(host=self.connection_data.host,
                                                 port=self.connection_data.port,
                                                 user=self.connection_data.user,
                                                 password=self.connection_data.password,
                                                 dbname=self.connection_data.base_name
                                                 )  # законектились
            self.__connected = True
            return True

        except BaseException:
            self.__to_log(message=f'Подключение к базе провалено',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          logging_level='ERROR', exception=True)
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
            self.__connected = False
            return True

        except BaseException :
            # Если отключиться не вышло, принудительно удадалим соединение
            self.__connected = False

            self.__to_log(message='Отключение от базы провалено. Объект соединения удалён.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          logging_level='ERROR', exception=True)
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
                self.__connected = False  # Чекаем отсутствие соединения
                self.__to_log(message='Переподключение к базе провалено',
                              logging_data={'base_name': self.connection_data.base_name,
                                            'server': self.connection_data.server,
                                            'user': self.connection_data.user},
                              logging_level='ERROR', exception=True)
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
            if not self.__requests_logging:  # Если запрос не логируется
                request = self.__requests_logging  # заменим его

            self.__to_log(message='Отправка данных в базу провалена.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
            result = None
        finally:
            cursor.close()

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

        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchall()  # Получим ответ

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass
            if not self.__requests_logging:  # Если запрос не логируется
                request = self.__requests_logging  # заменим его
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
            result = None  # Установим ошибку на экспорт

        finally:
            cursor.close()

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

        try:
            cursor = self.__connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchmany(size=size)  # Получим ответ

        except BaseException:  # Если вышла ошибка
            try:
                self.__connection.rollback()  # Откатим операцию
            except BaseException:
                pass
            if not self.__requests_logging:  # Если запрос не логируется
                request = self.__requests_logging  # заменим его
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
            result = None
        finally:
            cursor.close()

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
            if not self.__requests_logging:  # Если запрос не логируется
                request = self.__requests_logging  # заменим его
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          logging_level='ERROR', exception=True)
            result = errors_placeholder
        finally:
            cursor.close()

        return result

