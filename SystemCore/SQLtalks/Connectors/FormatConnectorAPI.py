'''


В init передаётся объект "ConnectionData", который содержит в себе всю информацию о базе, с которой
    мы работаем.


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