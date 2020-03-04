

import psycopg2
import time


class ConnectionData:
    '''
    Объект, хранящий данные для подключения
    '''
    def __init__(self, base_name: str,
                 host: str, port: str,
                 user: str, password: str):

        self.__base_name = base_name
        self.__host = host
        self.__port = str(port)
        self.__user = user
        self.__password = password

    # ------------------------------------------------------------------------------------------------
    # Доступы ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def base_name(self) -> str:
        '''
        Имя базы

        :return:
        '''
        return self.__base_name

    @property
    def host(self) -> str:
        '''
        Хост

        :return:
        '''
        return self.__host

    @property
    def port(self) -> str:
        '''
        Порт в виде строки

        :return:
        '''
        return self.__port

    @property
    def user(self) -> str:
        '''
        имя пользователя

        :return:
        '''
        return self.__user

    @property
    def password(self) -> str:
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

        to_database(request: str) -> bool or None
            True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита

        from_database(request: str) -> tuple or False or None
            tuple - результат, False - нет соединения, None - ошибка

        from_database_set(requests: list, errors_placeholder: object = 'ERROR') -> list or False or None
            list - результаты, False - нет соединения, None - ошибка

        from_database_first_line(request: str) -> tuple or False or None
            Берёт только первую строку
            tuple - результат, False - нет соединения, None - ошибка

        from_database_first_value(request: str) -> object or False or None
            Бертё только первое значение первой строки
            object - результат, False - нет соединения, None - ошибка

    '''

    def __init__(self,
                 connection_data: ConnectionData,
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
    def connection_data(self) -> ConnectionData:
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





    def passss(self):
        '''
        # Запросы

        to_database(request: str) -> bool or None
            True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита

        from_database(request: str) -> tuple or False or None
            tuple - результат, False - нет соединения, None - ошибка

        from_database_set(requests: list, errors_placeholder: object = 'ERROR') -> list or False or None
            list - результаты, False - нет соединения, None - ошибка

        from_database_first_line(request: str) -> tuple or False or None
            Берёт только первую строку
            tuple - результат, False - нет соединения, None - ошибка

        from_database_first_value(request: str) -> object or False or None
            Бертё только первое значение первой строки
            object - результат, False - нет соединения, None - ошибка


        :return:
        '''
        return






















    # отправка данных в базу
    def to_base(self, request: str,
                retry_attempts: int = None,
                try_to_allow: bool = True) -> bool:
        '''
        Функция для отправки запросов в базу.

        :param request: один запрос.
        :param retry_attempts: количество попыток повтора запроса к базе. Если это None, то будет использовано
                дефолтное количество self.__retry_attempts
        :param try_to_allow: попробовать ли подключиться, если работа с запросами запрещена?
        :return: bool статус успешности выполнения.
        '''

        # Проверим курсор
        if not self.__Allowed and try_to_allow:  # Если работа запрешена (курсора нет) но можно подключиться
            self.__to_log(message=f'to_base: Работа с запросами запрещена. Запрашиваю временное подключение к базе',
                          log_type='DEBUG')
            if not self.connection(act='reopen', retry_attempts=1):  # Если переподключение не удалось
                self.__to_log(message=(f'to_base: Ошибка передачи запроса в базу. Работа с запросами запрещена'),
                              log_type='ERROR')
                return False
            else:
                self.__to_log(message=f'to_base: Подключение открыто для выполнения одного запроса',
                              log_type='DEBUG')
                close_after = True  # Если мы законектились внутри функции, то надо будет отконектиться
        else:  # Если соединение есть и всё ок
            close_after = False

        if retry_attempts is None:  # Если не указано количество,
            retry_attempts = self.__retry_attempts  # Установим дефолтное
        current_attempt = 1  # Текущая попытка - 1

        is_ok = False  # По дефолту - запрос не отправлен
        while current_attempt <= retry_attempts:  # Пока есть попытки, будем пытаться
            try:
                self.__cursor.execute(request)  # отправили запрос
                self.__connection.commit()  # Внесём изменения в базу
                is_ok = True  # отметим, что запрос отпарвился
                break  # Закончим попытки
            except BaseException as miss:  # Если вышла ошибка
                self.__to_log(message=(f'to_base: попытка отправки запроса {current_attempt} ' +
                                       f'из {retry_attempts} провалена: {miss}. Соединение будет переоткрыто'),
                              log_type='ERROR')
                # Делаем переподключение, т.к. курсор может зависнуть
                reconnect_result = self.connection(act='reopen', retry_attempts=1)
                if not reconnect_result:  # Если реконект не удался
                    self.__to_log(message=f'to_base: попытка переподключения провалена. Работа закончена',
                                  log_type='ERROR')
                    break
                current_attempt += 1  # Скрутим счётчик попыток

        if close_after:  # Если соединение было на один запрос
            self.connection(act='close')

        if is_ok:  # Если запрос отправился
            return True
        else:  # Если запрос не отправился
            self.__to_log(message=f'to_base: Отправка запроса провалена. Исчерпано количество попыток.',
                          log_type='ERROR')
            return False

    # отправка данных в базу
    def from_base(self, request: str,
                  retry_attempts: int = None,
                  errors_placeholder: object = 'ERROR',
                  try_to_allow: bool = True) -> None or tuple:
        '''
        Функция для получения данных из базы.

        :param request: один запрос.
        :param retry_attempts: количество попыток повтора запроса к базе. Если это None, то будет использовано
                дефолтное количество self.__retry_attempts
        :param errors_placeholder: объект, который будет заполнять упавшие запросы в списке элементов, который будет
            экспортирован. Если значение None - то заполнения не будет.
        :param try_to_allow: попробовать ли подключиться, если работа с запросами запрещена?
        :return: None в случае ошибки или данные или tuple с данными
        '''

        # Проверим курсор
        if not self.__Allowed and try_to_allow:  # Если работа запрешена (курсора нет) но можно подключиться
            self.__to_log(message=f'from_base: Работа с запросами запрещена. Запрашиваю временное подключение к базе',
                          log_type='DEBUG')
            if not self.connection(act='reopen', retry_attempts=1):  # Если переподключение не удалось
                self.__to_log(message=(f'from_base: Ошибка передачи запроса в базу. Работа с запросами запрещена'),
                              log_type='ERROR')
                return None
            else:
                self.__to_log(message=f'from_base: Подключение открыто для выполнения одного запроса',
                              log_type='DEBUG')
                close_after = True  # Если мы законектились внутри функции, то надо будет отконектиться
        else:  # Если соединение есть и всё ок
            close_after = False

        if retry_attempts is None:  # Если не указано количество,
            retry_attempts = self.__retry_attempts  # Установим дефолтное
        current_attempt = 1  # Текущая попытка - 1

        is_ok = False  # По дефолту - запрос не отправлен
        result = errors_placeholder  # и результат по дефолту errors_placeholder
        while current_attempt <= retry_attempts:  # Пока есть попытки, будем пытаться
            try:
                self.__cursor.execute(request)  # отправили запрос
                result = self.__cursor.fetchall()  # Получим ответ
                is_ok = True  # отметим, что запрос отпарвился
                break  # Закончим попытки
            except BaseException as miss:  # Если вышла ошибка
                self.__to_log(message=(f'from_base: попытка отправки запроса {current_attempt} ' +
                                       f'из {retry_attempts} провалена: {miss}. Соединение будет переоткрыто'),
                              log_type='ERROR')
                # Делаем переподключение, т.к. курсор может зависнуть
                reconnect_result = self.connection(act='reopen', retry_attempts=1)
                if not reconnect_result:  # Если реконект не удался
                    self.__to_log(message=f'from_base: попытка переподключения провалена. Работа закончена',
                                  log_type='ERROR')
                    break
                current_attempt += 1  # Скрутим счётчик попыток

        if close_after:  # Если соединение было на один запрос
            self.connection(act='close')

        if is_ok:  # Если запрос отправился
            return result
        else:  # Если запрос не отправился
            self.__to_log(message=f'from_base: Отправка запроса провалена. Исчерпано количество попыток.',
                          log_type='ERROR')
            return result

