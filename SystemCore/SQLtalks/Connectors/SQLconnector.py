'''
Тут содержатся два модуля длы непосредственного общения с базой:
- PypyodbcConnector - pypyodbc модуль, поддерживающий и PostgreSQL, и MySQL;

- pyodbc подходит для SQLite, PostgreSQL, MySQL
        https://www.devart.com/odbc/mysql/docs/python.htm
        https://www.devart.com/odbc/postgresql/docs/python.htm
        https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQLite

- PostgreSQLconnector - модуль, для PostgreSQL, соответственно;
- MySQL модуля нет.



В этом документе хранится менеджер обращения к базам данных. Он может работать с:
    PostgreSQL
    MySQL
    SQLite
    ClickHouse

Все воркеры работают с запросами в SQL языка, при этом то, какой воркер будет задействован указывается
    в "авторизационном" элементе, передающемся в воркер.


Они реализуют одинаковый набор методов и свойств:
    allowed: bool - статус разрешения на работу с базой

    connection(act: str, retry_attempts: int or bool = False): bool or None
        Соединение и переподключение

        act - открыть(open)/закрыть(close)/переоткрыть(reopen) конект
        retry_attempts - количество попыток. True - взять дефолтное, False - запрретить
        return - True - Успешно; False - соединение имеет неподходящее состояние; None - ошибка при работе.


    to_base(requests: str, retry_attempts: int or bool = False): bool or None
        Отправка запроса с коррекцией базы

        requests - запрос
        retry_attempts - количество попыток. True - взять дефолтное, False - запрретить
        return - True - Успешно; False - соединение имеет неподходящее состояние; None - ошибка при работе.


    from_base(requests: str, retry_attempts: int or bool = False): tuple or False or None
        Получение данных из базы. tuple имеет вид ((данные строки 1), (данные строки 2), ... ,)
        fetchall()

        requests - запрос
        retry_attempts - количество попыток. True - взять дефолтное, False - запрретить
        return - tuple - ответ базы; False - соединение имеет неподходящее состояние; None - ошибка при работе.

    first_string(requests: str, retry_attempts: int or bool = False): tuple or False or None
        Получение данных из базы. Отдаётся "первая" (нулевая) строка. По сути это from_base()[0] - для удобства,
            когда нас интересует или только первая строка, или мы знаем, что строка всего одна.
            fetchone()

        requests - запрос
        retry_attempts - количество попыток. True - взять дефолтное, False - запрретить
        return - tuple - ответ базы; False - соединение имеет неподходящее состояние; None - ошибка при работе.

    one_value(requests: str, retry_attempts: int or bool = False,
              error_value=None): tuple or False
        Получение данных из базы. Отдаётся нулевое значение нулевой строки. По сути это from_base()[0][0] - для
            удобства, когда, например, мы получаем "максимальное значение" или количество строк.

        requests - запрос
        retry_attempts - количество попыток. True - взять дефолтное, False - запрретить
        error_value - что отдать при ошибке? Важно, ведь параметры True/False/None могут быть "заняты".
        return - tuple - ответ базы; False - соединение имеет неподходящее состояние; error_value - ошибка при работе.









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



