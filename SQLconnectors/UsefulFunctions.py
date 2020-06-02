'''
Функции для быстрой и удобной сборки простых запросов на вставку и обновление данных.
'''

from .CommonClient import SQLcommunicator

def simple_check(table: str,
                 where: list = None) -> str:
    '''
    Функция для проверки наличия хотябы одной строки с указанными условиями.

    :param table: имя таблицы
    :param where: список с элементами ('имя колонки', значение). Может быть пуст.
    :return: запрос на проверку
    '''

    if where is not None:  # если условие есть
        where_value = ' WHERE '
        if len(where) > 1:  # Если более одного значения в списке
            for el in where[:-1]:
                where_value += f" {el[0][0]}={el[0][1]} AND "
        where_value += f" {where[-1][0]}={where[-1][1]}"
    else:
        where_value = ''  # иначе условие пустое

    check_request = ("SELECT " +
                     "CASE " +
                     " WHEN EXISTS " +
                     f"(SELECT TOP (1) 1 FROM {table} {where_value}) " +
                     "THEN True ELSE False END")
    return check_request


def simple_update(table: str,
                  set_values: list,
                  where: list = None) -> str:
    '''
    Функция для упрощения подготовки запроса на обновление данных в строках.
        Важно, что строковые значения уже должны быть обособлены 'кавычками'.

    :param table: имя таблицы
    :param set_values: список с элементами ('имя колонки', значение)
    :param where: список с элементами ('имя колонки', значение). Может быть пуст.
    :return: строка запроса на обновление
    '''

    request = f'UPDATE {table} SET '

    if len(set_values) > 1:  # Если более одного значения в списке
        for el in set_values[:-1]:
            request += f" {el[0][0]}={el[0][1]}, "
    request += f" {set_values[-1][0]}={set_values[-1][1]}"

    if where is not None:  # Если условие задано
        request += ' WHERE '
        if len(where) > 1:  # Если более одного значения в списке
            for el in where[:-1]:
                request += f" {el[0][0]}={el[0][1]} AND "
        request += f" {where[-1][0]}={where[-1][1]}"

    return request


def add_values_set_separation(values_list: list,
                              start_request: str,
                              end_request: str = None,
                              step: int = 500) -> list:
    '''
    Функция подготавливает набор запросов вида "начало запроса VALUES (), (),..." или WHERE abs IN (value1, value2,...).
        Основная задача состоит в дроблении большого запроса на комлект небольших.
    Функция делает работу "в лоб", без проверок элементов спсика и прочего.

    :param values_list: список подготовленных значений в формате Str или tuple
    :param start_request: начало запроса, после которого будут вставлены значения
    :param end_request: добавка в конце запроса, если нужна
    :param step: шаг разбиения
    :return: список запросов
    '''

    def get_add_request(values: list):
        if values == []:
            return None
        request = start_request + ' '  # чтобы ни в коем случае request не оказался ссылкой на start_request

        if len(values) > 1:  # Добавим набор значений
            for el in values[:-1]:
                request += str(el) + ', '
        request += str(values[-1])  # добавми последнее или единственное

        return request

    add_requests = []  # список запросов на добавление
    for j in range(0, round(len(values_list) / step) + 1):
        request = get_add_request(values_list[j * step: (j + 1) * step])
        if request is not None:
            add_requests.append(request)

    if end_request is not None:  # если всем запросам нужна добавка в конце
        for i in range(0, len(add_requests)):
            add_requests[i] += end_request

    return add_requests


def get_string_parameters(table: str,
                          communicator: SQLcommunicator,
                          where: list = None) -> list or dict or None:
    '''
    Функция подготавливает словарь или список словарей, отвечающих найденным строкам. Индексами в словарях
        выступают навзвания столбцов, значения которых являются значениями словарей.

    :param table: имя таблицы
    :param communicator: SQL коммуникатор с функцией "request_fetch_all" для выполнения запросов.
    :param where: список с элементами ('имя колонки', значение). Может быть пуст.
    :return: словарь, если найдена одна строка, попадающая под указанное условие;
             список словарей если строк более одной;
             пустой словарь, если не найдено ни одной строки;
             None - в случае ошибки.
    '''

    # Подготовим запрос на получение имён столбцов
    columns_request = f"SHOW COLUMNS FROM {table}"
    columns_response = communicator.request_fetch_all(columns_request)  # Берём колонки
    if columns_response is None or columns_response is False:  # если запрос упал
        return None

    # Иначе это набор tuple, где первый элемент является названием колонки
    parameters_list = []
    for column in columns_response:
        parameters_list.append(column[0])
    del columns_response

    # Соберём названия столбцов для SELECT
    select_parameters = ''
    if len(parameters_list) > 1:
        for el in parameters_list:
            select_parameters += str(el) + ', '
    select_parameters += str(parameters_list[-1]) + ' '  # Добавим последнюю

    # Соберём условие
    if where is not None:  # если условие есть
        where_value = ' WHERE '
        if len(where) > 1:  # Если более одного значения в списке
            for el in where[:-1]:
                where_value += f" {el[0][0]}={el[0][1]} AND "
        where_value += f" {where[-1][0]}={where[-1][1]}"
    else:
        where_value = ''  # иначе условие пустое

    # Соберём запрос
    select_request = f"SELECT {select_parameters} FROM {table} {where_value}"
    select_response = communicator.request_fetch_all(request=select_request)  # берём данные
    if select_response is None or select_response is False:  # если запрос упал
        return None

    if len(select_response) == 1:  # Если найдена одна строка
        export_dict = {}
        for j in range(0, len(select_response[0])):  # погнали по элементам строки
            export_dict[parameters_list[j]] = select_response[0][j]
        return export_dict

    elif len(select_response) == 0:  # Если не найдено ничего
        return {}

    else:  # еслиболее одной строки
        export_list = []  # список словарей на экспорт
        for result_string in select_response:  # погнали по строкам
            export_dict = {}
            for j in range(0, len(result_string)):  # погнали по элементам строки
                export_dict[parameters_list[j]] = result_string[j]

            export_list.append(export_dict)  # добавим

        return export_list  # отдаём список



