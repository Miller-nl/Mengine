'''
Тут находятся "основные" объекты графа:
    GraphConfiguration - идентификационный ключ графа

    EdgeIdentification - идентификационный объект элемента графа

    EdgeRelationsList, EdgeRelationsSet, EdgeRelationsString - набор объектов для хранения данных
        (отличаются скоростью работы и занимаемой памятью)

    narrow_down - функция сужения связей вершины графа (EdgeRelations)

    NodeIdentification - идентификационный элемент ребра

'''

import copy  # Для копирования


# ------------------------------------------------------------------------------------------------
# Идентификатор графа ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class GraphConfiguration:
    '''
    Идентификационный объект графа.
    Методы и свойства:
        graph_id - индекс графа
        edges_values - есть ли у графа объекты, находящиеся на рёбрах
    '''

    def __init__(self, graph_id: str or int or float or tuple = None,
                 edges_values: bool = False):
        '''
        :param graph_id: индекс графа, который будет использоваться в работе.
        :param edges_values: тип графа: статус наличия каких-либо объектов на связях графа. True - есть, False - нет.
        '''

        self.__graph_id = graph_id
        self.__edges_values = edges_values

    # ------------------------------------------------------------------------------------------------
    # Доступ к данным --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def graph_id(self) -> str or int or float or tuple or None:
        '''
        Получение индекса графа

        :return: целое число
        '''
        return self.__graph_id

    @property
    def edges_values(self) -> bool:
        '''
        Получение статуса связей - есть ли объекты с данными для связей?

        :return: статус существования объектов на рёбрах графа.
        '''
        return self.__edges_values


# ------------------------------------------------------------------------------------------------
# Вершины ----------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class EdgeIdentification:
    '''
    Объект, реализующий опознание элемента графа.
    Методы и свойства:
        identification_key - опознавательный ключ графа

        label - метка

        element_id - индекс элемента или ссылка на сопоставленный объект.
    '''

    def __init__(self, element_id: str or int or float or tuple,
                 label: object = None,
                 identification_key: GraphConfiguration = None):
        '''
        :param element_id: индекс элемента или ссылка на сопоставленный объект.
        :param label: метка элемента. Например его тип.
        :param identification_key:  идентификационный ключ графа.
        '''
        self.__identification_key = identification_key
        self.__label = label
        self.__element_id = element_id  # Мой индекс

    # ------------------------------------------------------------------------------------------------
    # Основные данные --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def element_id(self) -> str or int or float or tuple:
        '''
        Получение индекса или сопоставленного элемента объекта графа

        :return: целое число
        '''
        return self.__element_id

    @property
    def identification_key(self) -> GraphConfiguration or None:
        '''
        Получение идентификатора графа.

        :return: объект - идентификатор или None, если его нет.
        '''
        return self.__identification_key

    @property
    def label(self) -> object:
        '''
        Получение метки элемента графа

        :return: метка
        '''
        return self.__label


class EdgeRelationsList:
    '''
    Объект, который будет хранить в себе данные о связях указанного типа вершины с другими вершинами.
    Вид хранения - "в списке". Подходит когда объём памяти важнее скорости.

    Основные методы и свойства:
        element_id - индекс элемента графа

        related_ids - список индексов связанных элементов

        _reset() - очистить связи

        add_relation() - добавить связь

        check_relation() - проверить свзяь

        del_relation() - удалить связь
    '''

    def __init__(self, element_id: str or int or float or tuple):
        '''

        :param element_id: индекс элемента
        '''
        self.__element_id = element_id  # Мой индекс
        self.__relations = []  # Создадим объект хранения связей

    def _reset(self):
        '''
        Сбрасывает содержимое набора связей

        :return:
        '''
        self.__relations.clear()
        return

    @property
    def element_id(self) -> str or int or float or tuple:
        '''
        Получение индекса или сопоставленного элемента объекта графа

        :return: целое число
        '''
        return self.__element_id

    @property
    def related_ids(self) -> list:
        '''
        Функция отдаёт все связанные индексы

        :return:
        '''
        return self.__relations.copy()

    # ------------------------------------------------------------------------------------------------
    # Работа со связями ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_relation(self, element_id: str or int or float or tuple):
        '''
        Функция добавляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        if not element_id in self.__relations:
            self.__relations.append(element_id)
        return

    def check_relation(self, element_id: str or int or float or tuple) -> bool:
        '''
        Функция проверяет связь с элементом

        :param element_id: индекс элемента
        :return: статус: True - связь есть, False - связи нет.
        '''
        if element_id in self.__relations:
            return True
        else:
            return False

    def del_relation(self, element_id: str or int or float or tuple):
        '''
        Функция удаляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        try:
            self.__relations.pop(self.__relations.index(element_id))
        except ValueError or IndexError:
            pass

        return


class EdgeRelationsSet:
    '''
    Объект, который будет хранить в себе данные о связях указанного типа вершины с другими вершинами.
    Вид хранения - "в упорядоченном наборе". Подходит, когда требуется скорость, но не критична память.

    Основные методы и свойства:
        element_id - индекс элемента графа

        related_ids - список индексов связанных элементов

        _reset() - очистить связи

        add_relation() - добавить связь

        check_relation() - проверить свзяь

        del_relation() - удалить связь
    '''

    def __init__(self, element_id: str or int or float or tuple):
        '''

        :param element_id: индекс элемента
        '''
        self.__element_id = element_id  # Мой индекс
        self.__relations = set()  # Создадим объект хранения связей

    def _reset(self):
        '''
        Сбрасывает содержимое набора связей

        :return:
        '''
        self.__relations.clear()  # сделали чистый набор
        return

    @property
    def element_id(self) -> str or int or float or tuple:
        '''
        Получение индекса или сопоставленного элемента объекта графа

        :return: целое число
        '''
        return self.__element_id

    @property
    def related_ids(self) -> list:
        '''
        Функция отдаёт все связанные индексы

        :return:
        '''
        return list(self.__relations)

    # ------------------------------------------------------------------------------------------------
    # Работа со связями ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_relation(self, element_id: str or int or float or tuple):
        '''
        Функция добавляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        self.__relations.add(element_id)
        return

    def check_relation(self, element_id: str or int or float or tuple) -> bool:
        '''
        Функция проверяет связь с элементом

        :param element_id: индекс элемента
        :return: статус: True - связь есть, False - связи нет.
        '''
        if element_id in self.__relations:
            return True
        else:
            return False

    def del_relation(self, element_id: str or int or float or tuple):
        '''
        Функция удаляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        self.__relations.discard(element_id)
        return


class EdgeRelationsString:
    '''
    Объект, который будет хранить в себе данные о связях указанного типа вершины с другими вершинами.
    Вид хранения - "в строке". Подходит когда требуется экономия памяти и индекс связей int, float, str.
        Не конфликтующий с хранением в строке.

    Основные методы и свойства:
        element_id - индекс элемента графа

        related_ids - список индексов связанных элементов

        _reset() - очистить связи

        add_relation() - добавить связь

        check_relation() - проверить свзяь

        del_relation() - удалить связь
    '''

    __sep = '%;'

    def __init__(self, element_id: str or int or float):
        '''

        :param element_id: индекс элемента
        '''
        self.__element_id = element_id  # Мой индекс
        self.__relations = copy.copy(self.__sep)  # Создадим объект хранения связей

    def _reset(self):
        '''
        Сбрасывает содержимое набора связей

        :return:
        '''
        self.__relations = copy.copy(self.__sep)  # сделали чистый набор
        return

    @property
    def element_id(self) -> str or int or float:
        '''
        Получение индекса или сопоставленного элемента объекта графа
        :return: целое число
        '''
        return self.__element_id

    @property
    def related_ids(self) -> list:
        '''
        Функция отдаёт все связанные индексы

        :return:
        '''
        ids_list = self.__relations.split(self.__sep)
        ids_list = ids_list[1:len(ids_list) - 1]  # Сбросим пограничные пустые

        export = []
        if type(self.element_id) is int:
            for j in range(0, len(ids_list)):
                try:
                    export.append(int(ids_list[j]))
                except BaseException:
                    pass

        elif type(self.element_id) is float:
            for j in range(0, len(ids_list)):
                for j in range(0, len(ids_list)):
                    try:
                        export.append(float(ids_list[j]))
                    except BaseException:
                        pass

        elif type(self.element_id) is str:
            export = ids_list

        return ids_list

    # ------------------------------------------------------------------------------------------------
    # Работа со связями ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_relation(self, element_id: str or int or float):
        '''
        Функция добавляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        if not f'{self.__sep}{element_id}{self.__sep}' in self.__relations:
            self.__relations += f'{element_id}{self.__sep}'
        return

    def check_relation(self, element_id: str or int or float) -> bool:
        '''
        Функция проверяет связь с элементом

        :param element_id: индекс элемента
        :return: статус: True - связь есть, False - связи нет.
        '''
        if f'{self.__sep}{element_id}{self.__sep}' in self.__relations:
            return True
        else:
            return False

    def del_relation(self, element_id: str or int or float):
        '''
        Функция удаляет связь с элементом

        :param element_id: индекс элемента
        :return: ничего
        '''
        self.__relations = self.__relations.replace(f'{self.__sep}{element_id}{self.__sep}', f'{self.__sep}')
        return


def narrow_down(edge_relations: EdgeRelationsList or EdgeRelationsSet or EdgeRelationsString,
                ids_list_or_set: list or set,
                keep: bool = True):
    '''
    Функция, делающая сужения связей по заданному набору индексов. Задача функции в том, чтобы исключить из связей все
    элементы, которых нет в графе, чтобы избежать ошибок при обработке.
    Функция работает непосредственно с контейнером, изменяя его.

    :param edge_relations: контейнер со связями
    :param ids_list_or_set: список или сет индексов, которые будут оставлены/удалены
    :param keep: оставить или удалить id из ids_list_or_set? True - оставить, False - удалить
    :return: ничего
    '''
    # Делаем сет для скорости обращений
    if isinstance(ids_list_or_set, list):
        ids_list_or_set = set(ids_list_or_set)

    if keep:  # Если оставляем только указанные
        for related_id in edge_relations.related_ids:  # Пошли по индексам
            if not related_id in ids_list_or_set:  # Если индекс не разрешён
                edge_relations.del_relation(related_id)  # Сбрасываем связь
    else:  # Если скинуть указанные
        for related_id in edge_relations.related_ids:  # Пошли по индексам
            if related_id in ids_list_or_set:  # Если индекс не разрешён
                edge_relations.del_relation(related_id)  # Сбрасываем связь
    return


# ------------------------------------------------------------------------------------------------
# Рёбра ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class NodeIdentification:
    '''
    Объект, реализующий опознание элемента графа.
    Методы и свойства:
        identification_key - опознавательный ключ графа

        label - метка

        from_id - индекс элемента от которого идёт связь

        to_id - индекс элемента к которому идёт связь
    '''

    def __init__(self, from_id: str or int or float or tuple,
                 to_id: str or int or float or tuple,
                 label: object = None,
                 identification_key: GraphConfiguration = None):
        '''
        :param from_id: индекс элемента от которого идёт связь
        :param to_id: индекс элемента к которому идёт связь
        :param label: метка элемента. Например - тип.
        :param identification_key:  идентификационный ключ графа.
        '''
        self.__identification_key = identification_key
        self.__label = label
        self.__from_id = from_id
        self.__to_id = to_id

    # ------------------------------------------------------------------------------------------------
    # Основные данные --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def from_id(self) -> str or int or float or tuple:
        '''
        Получение индекса элемента от которого идёт связь

        :return: целое число
        '''
        return self.__from_id

    @property
    def to_id(self) -> str or int or float or tuple:
        '''
        Получение индекса элемента к которому идёт связь

        :return: целое число
        '''
        return self.__to_id

    @property
    def identification_key(self) -> GraphConfiguration or None:
        '''
        Получение идентификатора графа.

        :return: объект - идентификатор или None, если его нет.
        '''
        return self.__identification_key

    @property
    def label(self) -> object:
        '''
        Получение метки элемента графа

        :return: метка
        '''
        return self.__label

