'''
Модуль для общения с PostgreSQL

'''

import psycopg2

from SystemCore.SQLtalks.Connectors.ConnectionDTOs import RemoteBaseConnectionData


# ------------------------------------------------------------------------------------------------
# Выполнение запросов ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class PostgreSQLconnector:
    '''
    Модуль для обращения в PostgerSQL базу.

    Методы и свойства

        # Подключение

        connected - подключена ли база

        connection_data - объект, содержащий авторизационные данные

        connect() -> bool or None
            True - Успешно подключились, False - уже подключены, None - ошибка.

        disconnect() -> bool or None
            True - Успешно отключились, False - уже отключены, None - ошибка.

        reconnect() ->  bool or None
            True - Успешно, соединение было, False - Успешно, соединения не было, None - ошибка

        # Запросы

        request_commit() - отправка запроса в базу

        request_fetch_all() - получает все строки по запросу

        request_fetch_many() - получает указанное количество строк по запросу

        request_fetch_value() - получает нулевое значение нулевой строки

    '''

    def __init__(self,
                 connection_data: RemoteBaseConnectionData,
                 logging_function = None,
                 retry_attempts: int = 0):
        '''

        :param connection_data: данные для коннекта к базе
        :param logging_function: функция для логирования. Если она не указана, будет использована "заглушка"
        :param retry_attempts: количество попыток переотправки запроса перед тем, как запрос свалится. По дефолту это
            ноль - без перезапросов.
        '''

        self.__connection_data = connection_data  # заберём данные для соединения с базой

        if logging_function is None:  # Если не передана функция логирования
            logging_function = self.__no_log  # используем заглушку
        self.__to_log = logging_function

        self.__retry_attempts = retry_attempts  # количество попыток подключения/переподключения/выполнения запросов

        self.__connected = False  # Переменная, разрешающая/запрещающая работу с запросами

    def __no_log(self, message: str,
                 logging_level: str = 'DEBUG',
                 logging_data: object = None,
                 exception_mistake: tuple or bool = False,
                 trace: list or bool = False,
                 **kwargs):
        '''
        Функция - заглушка

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

        return

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
    def connection_data(self) -> RemoteBaseConnectionData:
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
            self.__cursor = self.__connection.cursor()  # взяли курсор
            return True

        except BaseException:
            self.__to_log(message=f'Подключение к базе провалено',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          log_type='ERROR', exception_mistake=True)
            return None

    def disconnect(self) -> bool or None:
        '''
        Отключение от базы

        :return: True - Успешно отключились, False - уже отключены, None - ошибка.
        '''
        if not self.connected:  # Если конекта уже нет
            return False

        try:
            self.__cursor.close()  # закрыли курсор
            self.__connection.close()  # закрыли соединение с базой
            return True

        except BaseException :
            # Если отключиться не вышло, принудительно удадалим соединение
            del self.__connection
            del self.__cursor

            self.__to_log(message='Отключение от базы провалено. Объект соединения удалён.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user},
                          log_type='ERROR', exception_mistake=True)
            return None

    def reconnect(self) -> bool or None:
        '''
        Функция для переподключения к базе.

        :return: True - Успешно, соединение было, False - Успешно, соединения не было, None - ошибка (при соединении)
        '''
        if self.disconnect() is True:  # Если подключение было и оно разорвано
            connect_status = self.connect()  # Подключимся (True или None)
            if connect_status is True:  # если всё ок
                return True  # Вернём, что подключение было, и мы переподключились
            else:  # Если соединение упало
                return None

        else:  # Если соединения не было или была ошибка (но отсоединение произошло)
            connect_status = self.connect()  # Подключимся (True или None)
            if connect_status is True:  # если всё ок
                return False  # Вернём, что подключения не было, но соединение установлено
            else:  # Если соединение упало
                return None

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
            self.__cursor.execute(request)  # отправили запрос
            self.__connection.commit()  # Внесём изменения в базу
            return True  # Вернём "успешность"

        except BaseException:  # Если вышла ошибка
            self.__to_log(message='Отправка данных в базу провалена.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          log_type='ERROR', exception_mistake=True)
            return None

    def request_fetch_all(self, request: str) -> tuple or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных ((str1), (str2),)

        :param request: запрос
        :return: tuple - результат, False - нет соединения, None - ошибка.
        '''

        if not self.connected:  # Если соединения нет
            return False

        try:

            self.__cursor.execute(request)  # отправили запрос
            result = self.__cursor.fetchall()  # Получим ответ

            return result  # Вернём "успешность"

        except BaseException:  # Если вышла ошибка
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          log_type='ERROR', exception_mistake=True)
            return None

    def request_fetch_many(self, request: str,
                           size: int = 1) -> tuple or False or None:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных ((str1), (str2),)

        :param request: запрос
        :param size: количество строк, которые будут извлечены
        :return: tuple - результат, False - нет соединения, None - ошибка.
        '''

        if not self.connected:  # Если соединения нет
            return False

        try:
            self.__cursor.execute(request)  # отправили запрос
            result = self.__cursor.fetchmany(size=size)  # Получим ответ
            return result  # Вернём "результат"

        except BaseException:  # Если вышла ошибка
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          log_type='ERROR', exception_mistake=True)
            return None

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
            self.__cursor.execute(request)  # отправили запрос
            result = self.__cursor.fetchone()[0]  # Получим ответ
            return result  # Вернём "успешность"

        except BaseException:  # Если вышла ошибка
            self.__to_log(message='Получение данных из базы провалено.',
                          logging_data={'base_name': self.connection_data.base_name,
                                        'server': self.connection_data.server,
                                        'user': self.connection_data.user,
                                        'request': request},
                          log_type='ERROR', exception_mistake=True)
            return errors_placeholder

