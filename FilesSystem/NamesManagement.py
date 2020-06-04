'''
Эти функции используются для удобного транзата данных о парсящихся запросов через имя файла,
    которое использутеся для парсинга. Дополнительно в имя можгут быть вставлены дата и время,
    что исключит дублирования.
'''

import datetime
import re

# ------------------------------------------------------------------------------------------------
# Подготовка имени файла -------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
def prepare_string(parameter: str, value: str) -> str:
    '''
    Функция подготавливает параметры к зашиванию в имя файла. Нужна для удобства модерации имени.
        Параметр в имени файла будет записан как {key=value}

    :param parameter: "ключ" - date, id и т.п.
    :param value: значение
    :return: строка для добавления в имя файла
    '''
    exprot = ('{' +
              f'{parameter}={value}' +
              '}')
    return exprot


def file_name_expander(parameter: str, file_name: str) -> str or None:
    '''
    Дёргает параметр из имени файла, если там таковой был
        Параметр в имени файла записан как {key=value}. value всегда имеет строковый тип

    :param parameter: имя параметра
    :param file_name: имя файла
    :return: значение параметра в виде строки; None, если его не было или была получена ошибка.
    '''
    try:
        # {value=([^}]*)}  # Всё, что находится в скобках справа от ключа и знака "равно"
        parameter = re.findall('{' + f'{parameter}' + '=([^}]*)}', file_name)[0]  # берём все форматные группы
        return parameter
    except BaseException:  # Если нет такого параметра или в случае ошибки
        return None


def extract_parameters(file_name: str) -> dict or None:
    '''
    Функция извлекает все параметры из имени файла. Отдаёт словарь типа {parameter: value}.
        Ключ и значение строковые. Словарь может быть пуст!
        Параметры в имени файла записаны как {key=value}

    :param file_name: имя файла
    :return: словарь параметров или None, если упала нарезка
    '''
    # Получим список объектов
    parameters = re.findall('{([^}]*)}', file_name)
    export_dict = {}
    for el in parameters:
        try:
            export_dict[el[:el.find('=')]] = el[el.find('=') + 1:]
        except BaseException:  # Плохая обработка падающего исключения
            return None

    return export_dict


def file_name_preparer(add_time: bool = True,
                       start_of_name: str = None,
                       extension: str = 'txt',
                       **kwargs) -> str:
    '''
    Функция создаёт имя файла. Параметры не должны содержать: фигурные скобки, знак равно,
        запрещённые символы.
        Параметры в имени файла будут записаны как {key=value}

    :param add_time: требуется ли добавить время?
    :param start_of_name: дополнительная строка в начале имени файла
    :param extension: расширение файла (без точки в начале)
    :param kwargs: дополнительные параметры, которые будут включены в имя
    :return: строка с названием файла
    '''

    # Начнём имя файла
    if start_of_name is None:
        file_name = ''
    else:
        file_name = start_of_name

    if add_time:  # Если надо добавить время
        time = str(datetime.datetime.now())
        time = time.replace(':', '-')
        time = time.replace('.', '-')
        # '2020-05-14 19-53-46-470780'

        file_name += prepare_string(parameter='time', value=time)  # добавим в имя файла

    for key in kwargs:  # включим доп параметры
        file_name += prepare_string(parameter=key, value=kwargs[key])

    file_name += f'.{extension}'

    return file_name
