'''


В init передаётся объект "RemoteBaseConnectionData", который содержит в себе всю информацию о базе, с которой
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

    request_commit(request: str) -> bool or None
        True - успешно, False - нет соединения, None - ошибка отправки запроса или коммита

    request_fetch_all(request: str) -> tuple or False or None
        tuple - результат, False - нет соединения, None - ошибка

    request_fetch_many(requests: list, errors_placeholder: object = 'ERROR') -> list or False or None
        list - результаты, False - нет соединения, None - ошибка

    request_fetch_many(request: str, size: int = 1) -> tuple or False or None
        Берёт указанное количество первых строк ответа базы.
        tuple - результат, False - нет соединения, None - ошибка

    request_fetch_value(request: str, errors_placeholder: object = None) -> object
        Бертё только первое значение первой строки. В ответ придёт результат - значение ячейки или
        errors_placeholder в случае любой ошибки, включая отсутствие соединения с базой.

'''