from .ConnectionData import RemoteConnectionData
from Exceptions.ExceptionTypes import ProcessingError

import pymysql
import psycopg2
import sqlite3

class NotConnected(Exception):
    pass

class RequestExecutionError(Exception):
    pass

def prepare_equality(values: dict,
                     sep: str) -> str:
    '''
    Функция собарет данные из словаря в строку вида "key1=value1, key2=value2, ...". Без скобок, чтобы
        можно было использовать в WHERE с другими условиями, если требуется

    :param values: словарь со значениями. Значения уже подготовлены к вставке, если это строка, она ограничена кавычками.
        Это требуется для того, чтобы не экранировать запросы функций.
    :param sep: разделитель: ',' для "SET"; 'AND' для "WHERE"
    :return: строка для вставки
    '''
    export_string = ''
    if isinstance(values, list):  # Если список
        if len(values) > 1:  # Если более одного значения в списке
            for el in values[:-1]:
                export_string += f" {el[0]}={el[1]} {sep} "
        export_string += f" {values[-1][0]}={values[-1][1]}"

    else:  # Если это словарь
        keys = list(values.keys())
        for key in keys[:-1]:
            export_string += f" {key}={values[key]} {sep} "

        key = keys[-1]  # берём последний ключ
        export_string += f" {key}={values[key]} "

    return export_string


class CommonAdapterInterface:
    '''
    Methods
        Access
            engine
            ConnectionData
            Connection
            open - is connection open

        Standard Methods
            cursor()
            commit()
            rollback()
            close()

        Requests
            request_commit()
            request_fetch_all()
            request_fetch_many()
            request_fetch_value()

        Simple Functions
            simple_check()
            simple_insert_string()
            simple_update()


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

        self.__ConnectionData = RemoteConnectionData(engine=engine,
                                                     base_name=base_name,
                                                     catalog=catalog,
                                                     host=host, port=port,
                                                     user=user, password=password)
        self.__Connection = None
        self.connect()


    def connect(self):
        '''
        Функция создаёт соединение, устанавливая его в self._connection.
        Она нужна для того, чтобы обеспечить разные наборы праметров для разных пакетов.

        :return: объект соединения.
        '''

        engine = self.ConnectionData.engine
        try:
            if engine == 'MySQL':
                self.__Connection = pymysql.connect(host=self.ConnectionData.host,
                                                    port=self.ConnectionData.port,
                                                    user=self.ConnectionData.user,
                                                    password=self.ConnectionData.password,
                                                    database=self.ConnectionData.base_name
                                                    )  # законектились
            elif engine == 'PostgreSQL':
                self.__Connection = psycopg2.connect(host=self.ConnectionData.host,
                                                     port=self.ConnectionData.port,
                                                     user=self.ConnectionData.user,
                                                     password=self.ConnectionData.password,
                                                     dbname=self.ConnectionData.base_name
                                                     )  # законектились
            elif engine == 'SQLite':
                self.__Connection = sqlite3.connect(database=self.ConnectionData.catalog)  # законектились

            else:
                raise ProcessingError(f'SQL adapter creation failed. Wrong engine type: {engine}. ' +
                                      'Allowed: MySQL, PostgreSQL, SQLite.')
        except BaseException as miss:
            raise ProcessingError(f'SQL adapter creation failed.') from miss

        self.__connected = True
        return

    # ------------------------------------------------------------------------------------------------
    # Access -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def engine(self) -> str:
        '''
        Возворащает название драйвера, который используется.

        :return: строка - название.
        '''

        return self.ConnectionData.engine

    @property
    def ConnectionData(self) -> RemoteConnectionData:
        '''

        :return:
        '''
        return self.__ConnectionData

    @property
    def Connection(self):
        return self.__Connection

    @property
    def open(self) -> bool:
        return self.__connected

    # ------------------------------------------------------------------------------------------------
    # Standard Methods -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def cursor(self, **kwargs):
        '''
        Returns cursor.

        :param kwargs:
        :return:
        '''
        return self.__Connection.cursor(**kwargs)

    def commit(self):
        self.__Connection.commit()
        return

    def rollback(self):
        self.__Connection.rollback()
        return

    def close(self):
        self.__Connection.close()
        self.__connected = False
        return

    # ------------------------------------------------------------------------------------------------
    # Requests ---------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def request_commit(self, request: str) -> bool or None:
        '''
        Функция для передачи запросов в базу с коммитом.

        :param request: запрос к базе данных
        :return: True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита
        '''

        if not self.open:  # Если соединения нет
            raise NotConnected('Adapter not connected.')

        try:
            cursor = self.Connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            self.Connection.commit()  # Внесём изменения в базу
            return

        except BaseException as miss:  # Если вышла ошибка
            try:
                self.Connection.rollback()  # Откатим операцию
            except BaseException:
                pass
            raise RequestExecutionError(request) from miss

        finally:
            try:
                cursor.close()
            except BaseException:
                pass

    def request_fetch_all(self, request: str) -> list:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ...]

        :param request: запрос
        :return: list - результат, False - нет соединения, None - ошибка.
        '''
        if not self.open:  # Если соединения нет
            raise NotConnected('Adapter not connected.')

        try:
            cursor = self.Connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchall()  # Получим ответ
            return result

        except BaseException as miss:  # Если вышла ошибка
            raise RequestExecutionError(request) from miss

        finally:
            try:
                cursor.close()
            except BaseException:
                pass

    def request_fetch_many(self, request: str,
                           size: int = 1) -> list:
        '''
        Функция получает данные от базы данных. Забираются все строки
        Вид данных [(str1), (str2), ... , (str_n)]

        :param request: запрос
        :param size: количество строк, которые будут извлечены
        :return: list - результат
        '''
        if not self.open:  # Если соединения нет
            raise NotConnected('Adapter not connected.')

        try:
            cursor = self.Connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchmany(size=size)  # Получим ответ
            return result

        except BaseException as miss:  # Если вышла ошибка
            raise RequestExecutionError(request) from miss

        finally:
            try:
                cursor.close()
            except BaseException:
                pass

    def request_fetch_value(self, request: str) -> object:
        '''
        Функция получает первое (нулевое) значение первой (нулевой) строки из ответа и возвращат его.
        Нужна для удобства, чтобы можно было легко запросить "количество", "минимум"/"максимум" и прочие подобные
            величины.

        :param request: запрос
        :param errors_placeholder: "заменитель" ошибки. Актуален потому, что значение может быть и None.
            Но "поумолчанию" подразумевается, что единственное запрашиваемое значение не должно быть None.
        :return: "нулевое" значение "нулевой" строки.
        '''
        if not self.open:  # Если соединения нет
            raise NotConnected('Adapter not connected.')

        try:
            cursor = self.Connection.cursor()  # Взяли курсор
            cursor.execute(request)  # отправили запрос
            result = cursor.fetchone()[0]  # Получим ответ
            return result

        except BaseException as miss:  # Если вышла ошибка
            raise RequestExecutionError(request) from miss

        finally:
            try:
                cursor.close()
            except BaseException:
                pass

    # ------------------------------------------------------------------------------------------------
    # Simple requests --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def simple_check(self,
                     table: str,
                     **kwargs) -> bool:
        '''
        Функция подготавливает запрос для проверки наличия хотя бы одной строки в таблице, удовледворяющей указанным
            условиям.

        :param table: table name
        :param kwargs: parameters for the "WHERE" condition
        :return: status
        '''
        if kwargs == {}:
            where_value = ''  # нет условия
        else:
            where_value = 'WHERE ' + prepare_equality(values=kwargs, sep='AND')

        check_request = ("SELECT " +
                         "CASE " +
                         " WHEN EXISTS " +
                         f"(SELECT * FROM {table} {where_value}) " +
                         "THEN 1 ELSE 0 END")
        result = self.request_fetch_value(check_request)
        return bool(result)

    def simple_insert_string(self,
                             table: str,
                             **kwargs):
        '''
        Фунекция для "простой" вставки строки с параметрами.

        :param table: имя таблицы
        :param kwargs: словарь с элементами ('имя колонки'=значение). Значение уже готово ко вставке. Если это строка,
            она ограничена кавычками.
        :return:
        '''
        if kwargs == {}:
            raise ValueError('No arguments passed.')

        columns = '('
        values = '('

        keys = list(kwargs.keys())
        for key in keys[:-1]:
            columns += f"{key}, "
            if kwargs[key] in (None, 'null'):
                values += "NULL, "
            else:
                values += f"{kwargs[key]}, "
        key = keys[-1]  # берём последний ключ
        columns += f"{key}"
        if kwargs[key] in (None, 'null'):
            values += "NULL"
        else:
            values += f"{kwargs[key]}"

        columns += ')'
        values += ')'
        request = f'INSERT INTO {table} {columns} VALUES {values}'

        self.request_commit(request=request)

        return

    def simple_update(self,
                      table: str,
                      set_values: dict,
                      where: dict = None):
        '''
        Функция для упрощения подготовки запроса на обновление данных в строках.
            Важно, что строковые значения уже должны быть обособлены 'кавычками'.

        :param table: имя таблицы
        :param set_values: словарь или список с элементами ('имя колонки', значение)
        :param where: словарь или список с элементами ('имя колонки', значение). Может быть пуст.
        :return:
        '''
        set_values_string = prepare_equality(values=set_values, sep=',')
        request = f'UPDATE {table} SET {set_values_string}'

        where_string = prepare_equality(values=where, sep='AND')
        if where_string != '':  # если строка с условиями не пустая
            request += f' WHERE {where_string}'

        self.request_commit(request=request)

        return

    def simple_insert(self, table: str,
                      columns_names: list,
                      values_list: list,
                      step: int = 500) -> list:
        '''
        Функция подготавливает набор запросов вида "начало запроса VALUES (), (),..." или WHERE abs IN (value1, value2,...).
        Основная задача состоит в дроблении большого запроса на комлект небольших.
        Функция делает работу "в лоб", без проверок элементов спсика и прочего.

        :param table: table name
        :param columns_names: columns names
        :param values_list: a list of prepared values in Str or tuple format.
              strings: ["(v1, 'v2', v3)", "(vv1, 'vv2', vv3)", ...]
              tuples: [(v1, v2, v3), (vv1, vv2, vv3), ...]
            It is better to pass strings as this will eliminate conversion errors.
            Example: str((1, "asd'dsa", 123)) =  '(1, "asd\'dsa", 123)' - it will raise error.
        :param step: шаг разбиения
        :return: список запросов
        '''

        columns = ''
        for name in columns_names[:-1]:
            columns += f'{name}, '
        columns += f'{columns_names[-1]}'

        def get_add_request(values: list):
            if values == []:
                return None
            request = ''  # чтобы ни в коем случае request не оказался ссылкой на start_request

            if len(values) > 1:  # Добавим набор значений
                for el in values[:-1]:
                    request += str(el) + ', '
            request += str(values[-1])  # добавми последнее или единственное

            return request

        for j in range(0, round(len(values_list) / step) + 1):

            values = get_add_request(values_list[j * step: (j + 1) * step])
            if values is None:
                continue

            request = f'INSERT INTO {table} ({columns}) VALUES ({values})'

            self.request_commit(request=request)

        return

    def simple_expanded_strings(self,
                                table: str,
                                **kwargs) -> list or dict or None:
        '''

        Функция подготавливает словарь для каждой найденной строки в таблице, которая удовлетворяет условиям, заданным
        в функции. Ключами в словаре являются названия столбцов таблицы, а значениями - значения столбцов для
        искомой строки. Из словарей составляется список и передаётся на экспорт.

        :param table: имя таблицы
        :param adapter: SQL коммуникатор с функцией "request_fetch_all" для выполнения запросов.
        :param kwargs: название параметра - имя столбца, значение - то, чему столбец должен быть РАВЕН. В иных
            случаях следует писать запрос целиком.
        :return: список словарей, отвечающих строкам или словарь, если строка была одна.
        '''

        # Подготовим запрос на получение имён столбцов
        columns_response = self.request_fetch_all(f"SHOW COLUMNS FROM {table}")  # Берём колонки

        # Иначе это набор tuple, где первый элемент является названием колонки
        parameters_list = []
        for column in columns_response:
            parameters_list.append(column[0])
        del columns_response

        # Соберём названия столбцов для SELECT
        select_parameters = ''
        if len(parameters_list) > 1:
            for el in parameters_list[:-1]:
                select_parameters += str(el) + ', '
        select_parameters += str(parameters_list[-1]) + ' '  # Добавим последнюю

        # Соберём условие
        if kwargs != {}:
            where_value = prepare_equality(values=kwargs, sep='AND')
            if where_value != '':  # если условие непустое
                where_value = ' WHERE ' + where_value
        else:
            where_value = ''  # иначе условие пустое

        # Соберём запрос
        select_request = f"SELECT {select_parameters} FROM {table} {where_value}"
        select_response = self.request_fetch_all(request=select_request)  # берём данные

        if len(select_response) == 1:  # Если найдена одна строка
            export_dict = {}
            for j in range(0, len(select_response[0])):  # погнали по элементам строки
                export_dict[parameters_list[j]] = select_response[0][j]
            return export_dict

        elif len(select_response) == 0:  # Если не найдено ничего
            return {}

        else:  # если более одной строки
            export_list = []  # список словарей на экспорт
            for result_string in select_response:  # погнали по строкам
                export_dict = {}
                for j in range(0, len(result_string)):  # погнали по элементам строки
                    export_dict[parameters_list[j]] = result_string[j]

                export_list.append(export_dict)  # добавим

            return export_list  # отдаём список