'''
Тут содержатся два модуля длы непосредственного общения с базой:
- PypyodbcConnector - pypyodbc модуль, поддерживающий и PostgreSQL, и MySQL;
- PostgreSQLconnector - модуль, для PostgreSQL, соответственно;
- MySQL модуля нет.

Они реализуют одинаковый набор методов и свойств:
    allowed - статус разрешения на работу с базой

    connection() - открыть/закрыть/переоткрыть конект
    to_base() - отправка запроса с коррекцией базы
    from_base() - получение данных по запросу от базы.

От Тимура: orm, dao, query builder
Полезные ссылки:
    https://python-scripts.com/database
    https://habr.com/ru/post/207110/ - классная ORM. Выглядит удобно для ООП
    https://sqlbuilder.readthedocs.io/en/latest/ - тоже вариант

    https://github.com/jiangwen365/pypyodbc/wiki/A-Hello-World-script-of-pypyodbc - pypyodbc

    Дополнение
    https://khashtamov.com/ru/mysql-python/
    https://www.internet-technologies.ru/articles/posobie-po-mysql-na-python.html
'''


import time
import psycopg2

class ConnectionData:
    '''
    Объект, хранящий данные для подключения
    '''
    def __init__(self, base_name: str,
                 host: str, port: str,
                 user: str, password: str):

        self.base_name = base_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password



# ------------------------------------------------------------------------------------------------
# Выполнение запросов ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class PostgreSQLconnector:
    '''
    Модуль для обращения в PostgerSQL базу.
    Объект получает данные для авторизации в базу и реализует "стандартные методы":
        allowed - статус разрешения на работу с базой

        connection() - открыть/закрыть/переоткрыть конект

        to_base() - отправка запроса с коррекцией базы

        from_base() - получение данных по запросу от базы.


    '''

    def __init__(self,
                 connection_data: ConnectionData,
                 logging_function=None,
                 retry_attempts: int = 3, downtime: float = 0.01):
        '''

        :param connection_data: данные для коннекта к базе
        :param logging_function: функция для логирования. Если она не указана, будет использована "заглушка"
        :param retry_attempts: количество попыток переотправки запроса перед тем, как запрос свалится
        :param downtime: таймаут меджу перезапросами
        '''
        self.__connection_data = connection_data  # заберём данные для соединения с базой

        if logging_function is None:  # Если не передана функция логирования
            logging_function = self.__no_log  # используем заглушку
        self.__to_log = logging_function

        self.__retry_attempts = retry_attempts  # количество попыток подключения/переподключения/выполнения запросов
        self.__downtime = downtime  # Ожидание между запросами при ошибке

        self.__Allowed = False  # Переменная, разрешающая/запрещающая работу с запросами

    def __no_log(self, message: str, log_type: str, *args, **kwargs):
        '''
        Функция - заглушка. На случай, если нет функции логирования.

        :param message: сообщение
        :param log_type: тип логирования
        :param args: для будущих аргументов
        :param kwargs:  для будущих аргументов
        :return:
        '''
        return

    @property
    def allowed(self):
        '''
        Получить статус разрешённости работы с базой.
        Становится True, если соединение есть и оно рабочее. False - если соединения нет или оно получило ошибку.

        :return: bool статус.
        '''
        return self.__Allowed

    # ------------------------------------------------------------------------------------------------
    # Подключение/отключение -------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Функция для работы с подключением к базе
    def connection(self, act: str,
                   retry_attempts: int = None) -> bool:  # подключение, переподключение
        '''
        Функция для подключения, отключения, переподключения к базе.

        :param act: действие, которое надо выполнить:
                        close - закрыть соединение
                        open - открыть соединение
                        reopen - переоткрыть соединение
        :param retry_attempts: количество попыток переподключения.
        :return: статус успешности выполнения операции
        '''

        if retry_attempts is None:  # Если количество не установлено
            retry_attempts = self.__retry_attempts  # Мы берём дефолтное

        current_attempt = 1  # Начнём с первой попытки

        self.__to_log(message=(f'connection: Запрошена операция "{act}". ' +
                               f'Разрешено попыток: {retry_attempts}'),
                      log_type='DEBUG')

        self.__Allowed = False  # Работа с запросами запрещена "заранее"
        # разрешается только в случае удачного открытия соединения

        if act == 'close':
            close_result = self.__connection_close(attempt=current_attempt)  # Пробуем отключиться
            if close_result:
                self.__to_log(message=(f'connection: Попытка {current_attempt} из {retry_attempts} ' +
                                       f'операции "{act}" выполнена. Работа с запросами: {self.__Allowed}'),
                              log_type='DEBUG')
                return True  # Класс!
            else:  # Если не удалось
                self.__to_log(message=(f'connection: Попытка {current_attempt} из {retry_attempts} ' +
                                       f'операции "{act}" провалена. Ожидание {self.__downtime} сек'),
                              log_type='ERROR')
                return False  # Вернём неудачу

        elif act == 'open':
            while current_attempt <= retry_attempts:  # Пробуем, пока не исчерпаем попытки
                open_result = self.__connection_open(attempt=current_attempt)  # Пробуем отключиться
                if open_result:
                    self.__Allowed = True  # Работа с запросами разрешена
                    self.__to_log(message=(f'connection: Попытка {current_attempt} из {retry_attempts} ' +
                                           f'операции "{act}" выполнена. Работа с запросами: {self.__Allowed}'),
                                  log_type='DEBUG')
                    return True  # Класс!
                else:  # Если не удалось
                    self.__to_log(message=(f'connection: Попытка {current_attempt} из {retry_attempts} ' +
                                           f'операции "{act}" провалена. Ожидание {self.__downtime} сек'),
                                  log_type='ERROR')
                    time.sleep(self.__downtime)  # Подождём
                    current_attempt += 1  # Крутанём счётчик попыток

            # Если все попытки провалены
            self.__to_log(message=(f'connection: Операция "{act}" провалена: превышено количество попыток. ' +
                                   f'Работа с запросами {self.__Allowed}'),
                          log_type='ERROR')
            return False  # результат - не выполнено

        elif act == 'reopen':
            close_result = self.connection(act='close')  # Пробуем отключиться
            open_result = self.connection(act='open')  # Пробуем подключиться
            if open_result:
                self.__to_log(message=(f'connection: Операция "{act}" выполнена. Работа с запросами: {self.__Allowed}'),
                              log_type='DEBUG')
            else:
                self.__to_log(message=(f'connection: Операция "{act}" провалена. ' +
                                       f'Работа с запросами {self.__Allowed}'),
                              log_type='ERROR')

            return open_result  # вернём результат

    # Отключиться от базы
    def __connection_close(self, attempt: int) -> bool:
        '''
        Закрыть подключение

        :param attempt: номер попытки отключения.
        :return: bool статус "успешности" отключения.
        '''

        try:
            self.__my_connection.close()  # закрыли соединение с базой
        except BaseException as miss:
            try:
                del self.__my_connection
            except BaseException:
                pass

            self.__to_log(message=(f'__connection_close: Попытка {attempt} отключения от базы провалена: {miss}. ' +
                                   'Выполнено принудительное удаление объекта соединения.'),
                          log_type='ERROR')
            return False

        return True

    # Функция подключения к базе
    def __connection_open(self, attempt: int) -> bool:
        '''
        Функция для подключения к базе.

        :param attempt: номер попытки подключения.
        :return: bool статус успешности.
        '''
        # Пробуем законнектиться
        try:
            self.__my_connection = psycopg2.connect(host=self.__connection_data.host,
                                                    port=self.__connection_data.port,
                                                    user=self.__connection_data.user,
                                                    password=self.__connection_data.password,
                                                    dbname=self.__connection_data.base_name
                                                    )  # законектились
            self.__my_connection_cursor = self.__my_connection.cursor()  # взяли курсор
        except BaseException as miss:
            self.__to_log(message=f'__connection_open: Попытка {attempt} подключения к базе провалена: {miss}',
                          log_type='ERROR')
            return False
        return True

    # ------------------------------------------------------------------------------------------------
    # Выполнение запросов ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
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
                self.__my_connection_cursor.execute(request)  # отправили запрос
                self.__my_connection.commit()  # Внесём изменения в базу
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
                self.__my_connection_cursor.execute(request)  # отправили запрос
                result = self.__my_connection_cursor.fetchall()  # Получим ответ
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

