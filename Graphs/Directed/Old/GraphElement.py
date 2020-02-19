''' готово, отлажено
# --------------------------------------------------------------------------------------------------------
# Объект GraphElementData --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Объект для хранения данных элемента направленного графа.

Параметры init:
    element_id - индекс элемента графа
    identification_key - идентификационный ключ графа.

Доступные методы
    основные @property (БЕЗ setter-а!)
        element_id - индекс объекта
        tokens_list - получить список токенов элемента
        tokens_amount - количество токенов

        nearest_parents - список ближайших родителей
        nearest_children - список ближайших детей
        doubles - список дублей текущего элемента. Если элемент - дублёр, то тут будет id оригинала.
        duplicate - является ли элемент дублёром

    @property
        need_to_process - требуется ли обработать (включить в граф) граф?

    # Работа с токенами
        set_tokens(tokens: list or str, replace: bool = False) -> bool - функция устанавливает список токенов в self.
                Корректирует длину списка (__tokens_amount). Если список уже есть, вернёт False и опционально
                переустановит список в зависимости от атрибута replace.


    # Получение/передача информации о связях
        set_me_as_double(original_id: int) - функция устанавливает текущий элемент дублёром для original_id
                внутри собственного набора данных.

        add_to(element_id: int, relation: str) - функция добавляет связь с element_id типа relation.

        del_from(element_id: int, relation: str) -> bool - функция удаляет элемент element_id со связи relation,
                при этом, если связи не было, вернётся False, если связь была, и она удалена, вернётся True.

        replace(old_value: int, new_value: int, relation: str) -> bool - функция заменит old_value на new_value
                в списке relation. Если замена была успешна (значение old_value было), функция вернёт True,
                если заменять было нечего, то вернётся статус False.

    # Проверка/детектирование
        is_parent(el_id: int) -> bool - проверка, является ли el_id родителем

        is_child(el_id: int) -> bool - проверка, является ли el_id ребёнком

        is_duplicate(el_id: int) -> bool - проверка, является ли el_id элементом


self параметры
    mutex - мьютекс элемента, использующийся для разрешения/запрета операций с ним
    identification_key - идентификационный ключ.

    __element_id: int - индекс фразы
    __my_tokens: list - список токенов
    __tokens_amount: int - количество токенов

    __need_to_process: bool - требуется ли включение в граф

    __nearest_parents: str - строка с id родителей вида " id1 id2 id3 "
    __nearest_children: str - строка с id детей
    __doubles - строка с id дублей, если фраза не дублёр. Если фраза дублёр, это строка " original_id "
    __duplicate: bool - является ли текущий элемент дублёром


# --------------------------------------------------------------------------------------------------------
# Объект GraphElement ------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Оболочка вокруг GraphElement, которая должна реализовать работу с базой и некоторые дополнительные функции.

Параметры init:
    element_id - индекс элемента графа
    identification_key - идентификационный ключ графа.

# Доступные методы
    основные @property (БЕЗ setter-а!)
        element_id - индекс объекта
        tokens_list - получить список токенов элемента
        tokens_amount - количество токенов

        nearest_parents - список ближайших родителей
        nearest_children - список ближайших детей
        doubles - список дублей текущего элемента. Если элемент - дублёр, то тут будет id оригинала.
        duplicate - является ли элемент дублёром

    @property
        need_to_process - требуется ли обработать (включить в граф) граф?
        narrowed - детектор сужения элемента внутри графа

    # Работа с токенами
        set_tokens(tokens: list or str, replace: bool = False) -> bool - функция устанавливает список токенов в self.
                Корректирует длину списка (__tokens_amount). Если список уже есть, вернёт False и опционально
                переустановит список в зависимости от атрибута replace.

    # Получение/передача информации о связях
        set_me_as_double(original_id: int) - функция устанавливает текущий элемент дублёром для original_id
                внутри собственного набора данных.

        add_to(element_id: int, relation: str) - функция добавляет связь с element_id типа relation.

        del_from(element_id: int, relation: str) -> bool - функция удаляет элемент element_id со связи relation,
                при этом, если связи не было, вернётся False, если связь была, и она удалена, вернётся True.
        replace(old_value: int, new_value: int, relation: str) -> bool - функция заменит old_value на new_value
                в списке relation. Если замена была успешна (значение old_value было), функция вернёт True,
                если заменять было нечего, то вернётся статус False.

    # Проверка/детектирование
        is_parent(el_id: int) -> bool - проверка, является ли el_id родителем
        is_child(el_id: int) -> bool - проверка, является ли el_id ребёнком
        is_duplicate(el_id: int) -> bool - проверка, является ли el_id элементом

    # Функция сужения
        narrow_down(ids_list_or_set: list or set, keep: bool = True) Функция дропает из связей объекта ссылки
                на индексы, согласно переданному списку и настроёке keep.
                :param ids_list_or_set: список с индексам, которые участвуют в обработке
                :param keep: оставить индексы из списка? True - останутся только индексы из списка;
                        False - останутся только индексы, не нахоядищеся в списке.
                :return: ничего

    # Работа с параметрами
        set_parameter(value, name, replace: bool = True) -> bool - функция устанавливает параметру name заначение
                value и возвращает - был ли встречен объект в наборе.
        get_parameter(name) -> object or None - функция отдаёт параметр name или None, если его нет в словаре.
        get_parameters_keys() -> list - функция передаёт набор параметров.
        del_parameter(name) -> bool - функция пробует удалить параметр Name из словаря параметров и вернуть True.
                Если такого ключа нет в словаре, вернётся False.

self параметры
    mutex - мьютекс элемента, использующийся для разрешения/запрета операций с ним
    identification_key - идентификационный ключ.
    _GraphElementData__element_id: int - индекс фразы
    _GraphElementData__my_tokens: list - список токенов
    _GraphElementData__tokens_amount: int - количество токенов

    _GraphElementData__need_to_process: bool - требуется ли включение в граф

    _GraphElementData__nearest_parents: str - строка с id родителей вида " id1 id2 id3 "
    _GraphElementData__nearest_children: str - строка с id детей
    _GraphElementData__doubles - строка с id дублей, если фраза не дублёр. Если фраза дублёр, это строка " original_id "
    _GraphElementData__duplicate: bool - является ли текущий элемент дублёром

    __narrowed: bool - было ли сужение элемента в рамках набора - графа (сброшены индексы, которых нет в наборе)
    __parameters_dict: dict - словарь доп параметров. "На будущее", чтобы работать со статистикой без подгрузки
            набора запросов.




Комментарий
1. Добавить потом внутренний мютекс, который будет закрывать методы класса, если один из них сейчас вызван.
'''

import copy  # Для копирования

from multiprocessing import Lock
from Graphs.IdentificationKey import IdentificationKey


# --------------------------------------------------------------------------------------------------------
# Объект с базовым набором данных ------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
class GraphElementData:
    '''
        Объект, являющийся элементом графа.
        У элемента есть свой mutex для того, чтобы запретить его обработку во время его коррекции в многопоточном режиме.
        '''

    def __init__(self, element_id: int,
                 identification_key: IdentificationKey = None):
        '''
        :param element_id: собственный номер элемента

        :param identification_key:  идентификационный ключ графа.
        '''


        # Зададим основные параметры
        self.mutex = Lock()  # Мьютекс элемента
        self.identification_key = identification_key  # Идентификационный элемент

        self.__element_id = element_id  # Мой индекс
        self.__my_tokens = []  # Токены, которые будут использоватся для сравнения (дефолтно пуст)
        self.__tokens_amount = 0  # количество токенов в списке (дефолтно ноль)

        # Зададим параметры связей
        self.__nearest_parents = ' '
        self.__nearest_children = ' '
        self.__doubles = ' '  # строка дублёров или строка из element_id элемента, для которого данный является дублёром.
        self.__duplicate = False  # bool статус

        # Зададим дополнительные параметры
        self.__need_to_process = True  # По дефолту всех надо обработать

        # Добавить "Полный список токенов".

    # --------------------------------------------------------------------------------------------------------
    # Работа с пропертями ------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # element_id
    @property
    def element_id(self):
        return self.__element_id

    # Список токенов
    @property
    def tokens_list(self):
        return copy.copy(self.__my_tokens)

    # количество токенов
    @property
    def tokens_amount(self):
        return self.__tokens_amount

    # необходимость обработки
    @property
    def need_to_process(self):
        return self.__need_to_process

    @need_to_process.setter
    def need_to_process(self, value):
        if isinstance(value, bool):
            self.__need_to_process = value
        return

    # СПИСКИ связей элементов -------------

    @property  # Список родителей
    def nearest_parents(self) -> list:
        export = []
        splited = self.__nearest_parents.split(' ')
        splited = splited[1: len(splited) - 1]
        for el in splited:
            export.append(int(el))
        return export

    @property  # Получить список детей
    def nearest_children(self) -> list:
        export = []
        splited = self.__nearest_children.split(' ')
        splited = splited[1: len(splited) - 1]
        for el in splited:
            export.append(int(el))
        return export

    @property  # получить список дублёров
    def doubles(self) -> list:
        export = []
        splitted = self.__doubles.split(' ')
        splitted = splitted[1: len(splitted) - 1]
        for el in splitted:
            export.append(int(el))

        return export

    @property  # Получить статус - является ли объект дублёром
    def duplicate(self) -> bool:
        return copy.copy(self.__duplicate)

    # --------------------------------------------------------------------------------------------------------
    # Работа с токенами --------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Функция для установки набора токенов
    def set_tokens(self, tokens: list or str,
                   replace: bool = False,
                   sort: bool = True) -> bool:
        '''
        Функция устанавливает набор токенов
        :param tokens: набор токенов или токен-строка
        :param replace: заменить ли имеющийся набор, если он есть.
        :param sort: выполнить ли сортировку списка? По дефолту - да, т.к. для графа это критично.
        :return: "статус" установки: True - списка токенов не было, набор установлен; False - токены были, установка
                по атрибуту replace.
        '''

        if self.__my_tokens != []:  # Проверим, есть ли уже список токенов
            if not replace:  # Если токены есть и замена запрещена
                return False
            else:
                result = False  # Если токены есть, но замена разрешена
        else:  # Если токенов нет
            result = True  # Результат - всё ок

        if not isinstance(tokens, list):  # Если подан не список
            tokens = [tokens]  # Сделаем список

        if sort:  # Если нужно выполнить сортировку
            tokens = sorted(tokens)  # Отсортируем его

        self.__my_tokens = tokens  # Токены, которые будут использоватся для сравнения
        self.__tokens_amount = len(tokens)  # количество токенов в списке

        return result  # Вернём данные об установке набора

    # --------------------------------------------------------------------------------------------------------
    # Получение/передача информации о связях -----------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Установить элемент графа как дублёр
    def set_me_as_double(self, original_id: int):
        '''
        Функция делает из текущего элемента дублёра указанного оригинала.
        По сути она просто затирает данные self о связях.
        :param original_id: id  оригинала
        :return: ничего
        '''
        self.__need_to_process = False  # Дублёров не надо обрабатывать

        self.__nearest_parents = ' '
        self.__nearest_children = ' '
        self.__doubles = ' ' + str(original_id) + ' '  # id элемента - оригинала
        self.__duplicate = True  # Фраза получает статус дублёра

        return

    # добавим элемент
    def add_to(self, element_id: int, relation: str):
        '''
        Функция для добавления связи
        :param element_id: значение
        :param relation: тип связи: 'parent', 'child', 'double'.
        :return: ничего
        '''
        if relation == 'parent':
            self.__nearest_parents = self.__add_to(ids_string=self.__nearest_parents, element_id=element_id)
        elif relation == 'child':
            self.__nearest_children = self.__add_to(ids_string=self.__nearest_children, element_id=element_id)
        elif relation == 'double':
            self.__doubles = self.__add_to(ids_string=self.__doubles, element_id=element_id)
        return

    @staticmethod
    def __add_to(ids_string: str, element_id: int) -> str:
        '''
        Функция для включения элемента в набор.
        :param ids_string: набор (строка)
        :param element_id: индекс
        :return: скорректированный список
        '''
        if not (' ' + str(element_id) + ' ') in ids_string:  # Если элемент не в наборе
            ids_string += str(element_id) + ' '  # добавим его туда
        return ids_string

    # удалим элемент
    def del_from(self, element_id: int, relation: str) -> bool:
        '''
        Функция для удаления связи
        :param element_id: значение
        :param relation: тип связи: 'parent', 'child', 'double'.
        :return: статус удаления (был ли запрос в списке)
        '''
        result = False  # Заведомо удаление не выполнено

        if relation == 'parent':
            str_len = len(self.__nearest_parents)
            self.__nearest_parents = self.__del_from(data_str=self.__nearest_parents, element_id=element_id)
            if str_len > len(self.__nearest_parents):  # Если список "похудел"
                result = True  # Результат удаления - успешно

        elif relation == 'child':
            str_len = len(self.__nearest_children)
            self.__nearest_children = self.__del_from(data_str=self.__nearest_children, element_id=element_id)
            if str_len > len(self.__nearest_children):  # Если список "похудел"
                result = True  # Результат удаления - успешно

        elif relation == 'double':
            str_len = len(self.__doubles)
            self.__doubles = self.__del_from(data_str=self.__doubles, element_id=element_id)
            if str_len > len(self.__doubles):  # Если список "похудел"
                result = True  # Результат удаления - успешно

        return result

    @staticmethod
    def __del_from(data_str: str, element_id: int) -> str:
        '''
        Функция для включения элемента в набор.
        :param data_str: набор (строка)
        :param element_id: индекс
        :return: скорректированный список
        '''
        if (' ' + str(element_id) + ' ') in data_str:  # Если значение есть в списке
            splited = data_str.split(' ' + str(element_id) + ' ')
            data_str = splited[0] + ' ' + splited[1]
            # ПРЕЗЮМИРУЕТСЯ! Что значение одно!
        return data_str

    def replace(self, old_value: int, new_value: int, relation: str) -> bool:
        '''
        Функция заменяет значение old_value на new_value в списке relation. Вернётся "результат замены" - True,
        если замена была, False, если не было.
        :param old_value: старое значение индекса
        :param new_value: новое значение индекса
        :param relation: тип связи, где нужна замена
        :return: "результат замены" - True, если замена была, False, если не было.
        '''

        # Првоерим - есть ли указанный id на нужной связи?
        if relation == 'parent':
            if not self.is_parent(el_id=old_value):
                return False  # Вернём статус "неудачно"

        elif relation == 'child':
            if not self.is_child(el_id=old_value):
                return False  # Вернём статус "неудачно"

        elif relation == 'double':
            if not self.is_duplicate(el_id=old_value):
                return False  # Вернём статус "неудачно"

        else:
            return False  # Если тип не опознан

        self.del_from(element_id=old_value, relation=relation)  # Удалим старый
        self.add_to(element_id=new_value, relation=relation)  # Добавим связь

        return True

    # --------------------------------------------------------------------------------------------------------
    # Проверка/детектирование --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    # Родитель ли el_id для этого объекта - bool
    def is_parent(self, el_id: int) -> bool:
        '''
        Проверяет, есть ли el_id в списке родителей данного экземпляра
        :param el_id: индекс элемента, который надо проверить
        :return: bool результат
        '''
        el_id = ' ' + str(el_id) + ' '  # Сделаем строку
        if el_id in self.__nearest_parents:  # Проверим наличие
            return True
        else:
            return False

    # Ребёнок ли el_id для этого объекта - bool
    def is_child(self, el_id: int) -> bool:
        '''
        Проверяет, есть ли el_id в списке детей данного экземпляра
        :param el_id: индекс элемента, который надо проверить
        :return: bool результат
        '''
        el_id = ' ' + str(el_id) + ' '  # Сделаем строку
        if el_id in self.__nearest_children:  # Проверим наличие
            return True
        else:
            return False

    # Дубль ли el_id для этого объекта - bool
    def is_duplicate(self, el_id: int) -> bool:
        '''
        Проверяет, есть ли el_id в указанном списке
        :param el_id: индекс элемента, который надо проверить
        :return: bool результат
        '''
        el_id = ' ' + str(el_id) + ' '  # Сделаем строку
        if el_id in self.__doubles:  # Проверим наличие
            return True
        else:
            return False


# --------------------------------------------------------------------------------------------------------
# Объект с дополнительными функциями ---------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------


class GraphElement(GraphElementData):
    '''
    Объект, являющийся элементом графа.
    У элемента есть свой mutex для того, чтобы запретить его обработку во время его коррекции в многопоточном режиме.
    '''

    def __init__(self, element_id: int,
                 identification_key: IdentificationKey = None):
        '''
        :param element_id: собственный номер элемента
        :param mutex_lock: закрывать ли внутренние операции по изменению свойст отдельным мьютексом?
        :param identification_key:  идентификационный ключ графа.
        '''

        GraphElementData.__init__(self, element_id=element_id,
                                  identification_key=identification_key)  # Выполним init объекта с данными

        # Зададим дополнительные параметры
        self.__narrowed = False  # Был ли объект сужен


        # Uploaded?

        self.__parameters_dict = {}  # Словарь с доп параметрами

    # --------------------------------------------------------------------------------------------------------
    # Работа с пропертями ------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    @property  # Было ли сужение
    def narrowed(self):
        return self.__narrowed

    @narrowed.setter
    def narrowed(self, value: int):
        self.__narrowed = value
        return

    # --------------------------------------------------------------------------------------------------------
    # Функция сужения ----------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Функция обрывания связей с элементами
    def narrow_down(self, ids_list_or_set: list or set,
                    keep: bool = True):
        '''
        Функция дропает из связей объекта ссылки на индексы, согласно переданному списку и настроёке keep.
        При этом параметр self.__narrowed становится True.
        Момент - функция для прямого переустановления списков со связями не предусмотрена. И в доступе извне её
        быть не должно. Так что тут немного "некрасиво" сделано.
        :param ids_list_or_set: список с индексам, которые участвуют в обработке
        :param keep: оставить индексы из списка? True - останутся только индексы из списка; False - останутся только
                    индексы, не нахоядищеся в списке.
        :return: ничего
        '''
        if isinstance(ids_list_or_set, list):  # Если список,
            ids_list_or_set = set(ids_list_or_set)  # Сделаем set

        # Пошли обходить
        self._GraphElementData__nearest_parents = self.__keep(have_set=set(self.nearest_parents),
                                                              ids_set=ids_list_or_set, keep=keep)
        self._GraphElementData__nearest_children = self.__keep(have_set=set(self.nearest_children),
                                                               ids_set=ids_list_or_set, keep=keep)
        self._GraphElementData__doubles = self.__keep(have_set=set(self.doubles),
                                                      ids_set=ids_list_or_set, keep=keep)
        self.narrowed = True  # Установим, что элемент был сужен
        return

    @staticmethod
    def __keep(have_set: set, ids_set: set, keep: bool) -> str:
        '''
        Функция оставляет только "нужные" элементы списка.
        :param have_set: сет имеющихся id
        :param ids_set: сет поданных id
        :param keep: что сделать: True - оставить только из поданных/ False - удалить поданные из сета имеющихся.
        :return: строка результат
        '''
        if keep:  # Если оставить только индексы из ids_set
            result_list = list(have_set.intersection(ids_set))  # Объединение
        else:  # Если удалить индексы из ids_set
            result_list = list(have_set.difference(ids_set))  # Пересечение

        export = ' '  # Соберём строку
        for el in result_list:
            export += str(el) + ' '
        return export

    # --------------------------------------------------------------------------------------------------------
    # Работа с параметрами -----------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Функция устанавливает на индекс name значение value
    def set_parameter(self, value, name,
                      replace: bool = True) -> bool:
        '''
        Функция устанавливает значение параметра name в виде value. Важно, что value и name без указания типа,
        то есть, они произвольные.
        :param value: значение параметра
        :param name: название параметра
        :param replace: заменить ли при встрече индекса?
        :return: если параметра name не было - True, иначе False.
        '''
        try:  # Првоерим существование параметра
            a = self.__parameters_dict[name]
            if not replace:  # Если заменять не нужно
                return False
            else:
                result = False  # Параметр есть и будет заменён
        except KeyError:  # Если параметра нет
            result = True  # Параметра нет

        self.__parameters_dict[name] = value  # Установим значение
        return result  # Закончим

    # Получить список названий/ключей списка параметров
    def get_parameters_keys(self) -> list:
        return list(self.__parameters_dict.keys())

    # функция получает значение параметра name
    def get_parameter(self, name) -> object or None:
        '''
        Функция возвращяет значение параметра name, если оно есть.
        :param name: название параметра
        :return: значение или None, если параметра нет
        '''
        try:  # Пробуем отдать значение
            export = self.__parameters_dict[name]
            return export
        except KeyError:  # если name нет
            return None  # Вернём None

    def del_parameter(self, name) -> bool:
        '''
        Функция пробует удалить из словаря параметров свойство с ключём name
        :param name: ключ для словаря
        :return: успешность мероприятия: True - значение было и удалено, False - значения не было.
        '''

        try:  # Пробуем удалить параметр
            del self.__parameters_dict[name]
            return True
        except KeyError:  # Если не было такого ключа
            return False

    # --------------------------------------------------------------------------------------------------------
    # Работа с SQL таблицами ---------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    # Подгрузка / отгрузка
    # Функция должна будет принимать курсор. И, если он не опознаётся (is None) выдавать результат False.
    # Для того, чтобы объект можно было юзать даже без базы.



