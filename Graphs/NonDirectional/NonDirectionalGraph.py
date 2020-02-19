''' готово, отлажено
Что тут можно дёрнуть:
Протестить:
    1. в create_node или строковый или списковый элементы.
        Но "на живую". Для проверки стоит сохранят в PICKLE
        Не забыть в "заведении контейнера" поправить
    2.
'''

import copy  # Для копирования

from SystemCore.DataContainers.SimpleContainer import SimpleContainer
from Graphs.MainObjects.ElementsAndEdges import GraphConfiguration, EdgeIdentification, narrow_down
from Graphs.MainObjects.ElementsAndEdges import EdgeRelationsList, EdgeRelationsSet, EdgeRelationsString






class NonDirectionalGraph:
    '''
    Объект реализует граф, имеющий единственный тип связи, не являющийся направленным. Все объекты знаюот обо всех
        своих связях.
    '''

    def __init__(self, graph_id: str or int or float or tuple = None,
                 edges_values: bool = False):

        se



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

    def __init__(self, element_id: str or int or float,
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

    @property
    def element_id(self) -> str or int or float or tuple:
        '''
        Получение индекса или сопоставленного элемента объекта графа
        :return: целое число
        '''
        return self.__element_id

class EdgeRelationsStorage:

    '''
    Объект, который будет хранить в себе данные о связях указанного типа вершины с другими вершинами.

    '''


# --------------------------------------------------------
# Функция сужения элемента -------------------------------
# --------------------------------------------------------
def __keep(have_list: list, ids_set: set, keep: bool) -> list:
    '''
    Функция оставляет только "нужные" элементы списка.
    :param have_list: список имеющихся id
    :param ids_set: set поданных id
    :param keep: что сделать: True - оставить только из поданных/ False - удалить поданные из сета имеющихся.
    :return: список - результат
    '''
    have_set = set(have_list)  # Делаем сет из поданного списка

    if keep:  # Если оставить только индексы из ids_set
        result_list = list(have_set.intersection(set(ids_set)))  # Объединение
    else:  # Если удалить индексы из ids_set
        result_list = list(have_set.difference(set(ids_set)))  # Пересечение

    return result_list  # отдадим результат

def narrow_down(element: StringStoringEdgeElement or ListStoringEdgeElement,
                ids_list_or_set: list or set,
                relation: int or str = None,
                keep: bool = True) -> bool:
    '''
    Функция, делающая сужения связей по поданному набору индексов. Задача функции в том, чтобы исключить из связей все
    элементы, которых нет в графе, чтобы избежать ошибок при обработке.
    Если мы удаляем связи элемента А и в работу попадает этот элемент, то у него упадут только связи на самого себя.
    :param element: Элемент, который "сужаем"
    :param ids_list_or_set: список или сет индексов, которые будут оставлены/удалены
    :param relation: тип связи, для которой выполняется действие. Актуально тогда, когда типов связей много и нам нужно
        выбрать один конкретный.
    :param keep: оставить или удалить id из ids_list_or_set? True - оставить, False - удалить
    :return: успешность выполнения. Ошибка возвращяется если не опознан тип элемента или тип связей.
    '''

    if isinstance(ids_list_or_set, list):
        ids_list_or_set = set(ids_list_or_set)

    if isinstance(element, StringStoringEdgeElement):  # Если у элемента несколько типов связей
        # Сформируем список типов связей, с которыми работаем
        if relation is None:  # Если связей нет
            relations = element.relations_types  # Берём список связей
        else:  # Если задан
            if relation in element.relations_types:  # Проверяем, что такая связь есть
                relations = [relation]  # Делаем список
            else:  # Если нет в списке
                return False  # Вернём ошибку

        for relation in relations:  # Погнали по связям
            # Берём список элементов с такйо связью
            related_elements = element.related_elements(relation=relation)  # берём список элементов, связанных с данным
            related_elements = __keep(have_list=related_elements,
                                      ids_set=ids_list_or_set, keep=keep)  # оставляем только нужные

            # оставляем только нужные
            related_elements = __keep(have_list=related_elements, ids_set=ids_list_or_set, keep=keep)
            element._clear_relations(relation=relation)  # Дропаем список элементов с указанной связью
            for el in related_elements:  # Загоним обратно нужные
                element.add_relation(element_id=el, relation=relation)  # добавляем

        return True  # Вернём "успешно"

    else:  # Если тип не опознан
        return False  # Вернём "ошибку"

# ------------------------------------------------------------------------------------------------
# Граф -------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class NodesGraph:
    '''
    Объект, реализующий граф. Объектами графа являются узлы, без рёбер.
    В tuple связи указываются по простому правилу. Связь всегда устанавливается между А и В, внутри А связь к В получит
    нулевой тип из tuple, а В связь от А получит первый тип из tuple. Если граф ненаправленный, tuple[0] = tuple[1].
    Граф не реализует DTO для связей, так как логика работы с такими DTO сльно замедлит операции в случаях, когда DTO
        вообще не используются. При необходимости может быть создан ещё один граф, наследующийся от данного, который
        будет использовать в том числе DTO для рёбер.
    '''

    __default_directed_edges = ('f', 't')
    '''
     Дефолтно:
        "f" (from me) - список элементов (детей), для которых данный является родителем.
        "t" (to me) - список элементов (родителей), для которых данный является дочерним.
        '''
    __default_not_directed_edges = ('r', 'r')  # для "ненаправленных" случаев. Просто тупо детектирует связь.

    def __init__(self,
                 configuration: GraphConfiguration = None,
                 default_edges_types: tuple or bool = True,
                 additional_edges_types: tuple or list = None,
                 process_manager: ProcessesManager = None, launch_module_name: str = None):
        '''
        :param configuration: объект, идентифицирующий граф. Может отсутствовать.
        :param default_edges_types: "дефолтные" типы связей, которыми будут связываться элементы. Значения:
            False - актуально для ненаправленного графа - когда оба элемента получают связь типа "есть связь", без
                указания направления.
            True - актуально для направленного графа A -> B. Берётся tuple __default_directed_edges, в ктором
                указываются названия связей "от" и "к".
            tuple - актуально для направленного графа A -> B. Нулевой элемент которого называет тип связи родителя
                (в А называет тип связи к B), а первый - связь в ребёнке (в B тип связи от А).
                Это если ты прям извращенец - лучше не трогать, чтобы не путаться, т.к. это ничего не изменит в сути.
        :param additional_edges_types: "дополнительные" типы связей. Это отдельные (!) от связей направления рёбра.
            Они будут задаваться отдельными функциями, нежели связи направления. Нужны для удобства, чтобы не маркерить
            связи через их DTO и исключить лишние операции, связанные с извлечением нужного типа связей.
        :param process_manager: менеджер процесса, если он есть. Нужен для логирования.
        :param launch_module_name: имя выхывающего модуля (для логирования)
        '''

        self.__configuration = configuration

        # Добавим менеджер процесса и функцию логирования
        self.__process_manager = process_manager

        self.__nodes_container = MainContainer(objects_type=ListStoringEdgeElement,
                                               identification_object=configuration,
                                               index_type=int)  # Контейнер вершин

        if isinstance(process_manager, ProcessesManager):  # Если менеджер есть
            self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                             launch_module_name=launch_module_name)
            self.__Logger = process_manager.create_logger(module_name=self.__my_name)
            self.__to_log = self.__Logger.to_log  # Установим функцию логирования
        else:  # Если менеджера процесса нет
            self.__to_log = self.__log_stub

        # Установим тип основных связей графа
        if default_edges_types is True:  # Если граф направленный
            self.__default_edges_types = self.__default_directed_edges  # Берём стандартный tuple
        elif default_edges_types is False:  # Если граф ненаправленный
            self.__default_edges_types = self.__default_not_directed_edges  # Просто фиксируем "наличие" связи
        elif isinstance(default_edges_types, tuple):  # Если граф ненаправленный
            if len(default_edges_types) == 2:  # Если tuple верный
                self.__default_edges_types = copy.deepcopy(default_edges_types)  # берём копию, чтобы исключить "неявные" проблемы
            else:
                self.__to_log(message=f'Ошибка настройки графа: len(default_edges_types) != 2 ({len(default_edges_types)})',
                              log_type='ERROR', data={'default_edges_types': default_edges_types})
        else:
            self.__to_log(message='Ошибка настройки графа: default_edges_types не опознан',
                          log_type='ERROR', data={'default_edges_types': default_edges_types})

        # Установим типы "Дополнительных" связей
        if additional_edges_types is None:  # Если дополнительных связей не будет
            self.__additional_edges_types = ()  # Иначе набор пуст
        else:
            self.__additional_edges_types = tuple(additional_edges_types)  # по ходу работы менять их низя


    def __log_stub(self, **kwargs):
        '''
        Заглушка для функции логирования.
        INFO Подтверждение того, что все работает, как ожидалось.
        WARNING Указание на то, что произошло что-то неожиданное или указание на проблему в ближайшем будущем
        (например, «недостаточно места на диске»). Программное обеспечение все еще работает как ожидалось.
        ERROR Из-за более серьезной проблемы программное обеспечение не может выполнять какую-либо функцию.
        CRITICAL Серьезная ошибка, указывающая на то, что сама программа не может продолжить работу.
        :param kwargs: аргументы
        :return: ничего
        '''
        return

    # ------------------------------------------------------------------------------------------------
    # Работа с property ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def configuration(self) -> GraphConfiguration or None:
        '''
        Получение конфигурации графа, если она есть.
        :return: GraphConfiguration or None
        '''
        return self.__configuration

    @property
    def default_edges_types(self) -> tuple:
        '''
        Отдаёт tuple, по которому ставятся связи A->B. A получает нулевой тип связи, B - первый.
        :return:
        '''
        return copy.copy(self.__default_edges_types)

    @property
    def additional_edges_types(self) -> tuple:
        '''
        Получение кортежа "дополнительных" типовсвязи, которые имеются в графе.
        :return: копию tuple-а
        '''
        return copy.copy(self.__additional_edges_types)

    @property
    def nodes_container(self) -> MainContainer:
        '''
        Получение контейнера с вершинами.
        :return:
        '''
        return self.__nodes_container

    @property
    def nodes_ids_list(self) -> list:
        '''
        Получить список индексов элементов в графе. Нужен для иттерирования и замыкания.
        :return: список
        '''
        return self.__nodes_container.dict_keys

    @property
    def nodes_list(self) -> list:
        '''
        Получение списка объектов - вершин.
        :return: список ссылок на элементы графа
        '''
        return self.__nodes_container.objects_list

    # ------------------------------------------------------------------------------------------------
    # Вершины ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def check_node(self, element_id: str or int or float or tuple) -> bool:
        '''
        Функция проверяет существование вершины.
        :param element_id: индекс вершины
        :return: bool статус
        '''
        return self.__nodes_container.check_access(index=element_id)

    def get_node(self, element_id: str or int or float or tuple,
                 create: bool = False) -> StringStoringEdgeElement or None:
        '''
        Функция отдаёт элемент графа. Может создать его под шумок.
        :param element_id: индекс вершины
        :param create: создать ли вершину, если она отсутствует в графе?
        :return: вершина или None, если её нет в графе и создание не разрешено.
        '''
        node = self.__nodes_container.get_object(index=element_id, no_value=None)
        if node is None and create is True:  # Если связи нет, но создание разрешено
            return self.create_node(element_id=element_id)# Создадим.
            # замены быть не может
        else:
            self.__to_log(message='Запрошенной вершины нет в графе',
                          log_type='ERROR', data={'element_id': element_id})
            return node  # Иначе вернём то, что нашли

    def create_node(self, element_id: str or int or float or tuple,
                    replace: bool = True) -> StringStoringEdgeElement or ListStoringEdgeElement or None:
        '''
        Функция создаёт вершину графа.
        :param element_id: индекс вершины
        :param replace: заменить ли элемент при совпадении индекса
        :return: вершину графа или None в случае, если создание элемента провалено или индекс занят и замена запрещена.
        '''

        if self.__nodes_container.check_access(index=element_id) and not replace:  # Если id занят и замена запрещена
            self.__to_log(message='Индекс создаваемого элемента занят, замена запрещена',
                          log_type='ERROR', data={'element_id': element_id})
            return None

        # Агрегируем связи, чтобы передать их в элемент
        relations_types = list(self.default_edges_types).extend(list(self.additional_edges_types))

        # Создаём элемент графа. Не заводя(!) additional_edges_types типы связей, чтобы не забивать память без нужды
        node = ListStoringEdgeElement(element_id=element_id, identification_key=self.configuration,
                                      relations=relations_types)

        # Добавим в контейнер
        self.__nodes_container.add_object(data_object=node, replace=replace, index=element_id)
        return node

    def del_node(self, element_id: str or int or float or tuple,
                 clear_relations: bool = True) -> bool or None:
        '''
        Функция удаляет элемент графа, при этом делая сужение, исключая этот элемент (удаляя все его связи).
        :param element_id: индекс удаляющегося элемента
        :param clear_relations: зачистить ли связи?
        :return: True - объект был и он удалён, False - объекта не было, None - если была ошибка при удалении
        '''

        d_element = self.__nodes_container.get_object(index=element_id, no_value=None)

        if d_element is None:  # Если элемента нет
            return False  # Вернём статус "элемента нет"

        # Зачистка связей внутри элементов
        if clear_relations:
            for process_el_id in self.__nodes_container.dict_keys:  # Пошил по списку индексов
                # Удаляем все типы связей с этим элементом (без перетяжки)
                narrow_down(element=self.__nodes_container.get_object(index=process_el_id),
                            ids_list_or_set=[element_id],
                            keep=False)

        # Удаляем элемент
        self.__nodes_container.del_object(index=element_id)
        return True

    def get_related_elements(self, element_id: str or int or float or tuple,
                             relation: int or str) -> list or None:
        '''
        Функция подготавливает список ссылок на элементы, которые связаны с element_id связью типа relation.
        :param element_id:  индекс элемента
        :param relation: связь, по которой будет подбираться список
        :return: список объектов ListStoringEdgeElement, если элемента нет в графе он "пропустится", но залогируется;
            None в случае, если элемента нет или нет типа связи relation.
        '''

        element = self.__nodes_container.get_object(index=element_id)
        if element is None:
            self.__to_log(message='Элемента с указанным индексом нет в графе',
                          log_type='ERROR', data={'element_id': element_id})
            return None  # Если нет элемента

        ids_list = element.related_elements(relation=relation)  # Получим индексы связанных элементов

        if ids_list is None:  # Если списка связей нет
            self.__to_log(message='Запрашиваемого типа связей нет',
                          log_type='ERROR', data={'element_id': element_id, 'relation': relation})
            return None  # Списка связей нет
        else:  # Если список связей есть
            # Заменим их на ссылки на элемент.
            export_list = []
            for j in range(0, len(ids_list)):
                add_element = self.get_node(element_id=ids_list[j], create=False)
                if not add_element is None:  # Если это элемент
                    export_list.append(add_element)
                else:  # Есди это не элемент
                    self.__to_log(message='Запрашиваемого связанного элемента нет в графе',
                                  log_type='ERROR', data={'element_id': element_id,
                                                          'related_element_id': ids_list[j],
                                                          'relation': relation})
            return export_list  # отдадим список

    # ------------------------------------------------------------------------------------------------
    # Связи ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def is_relation_allowed(self, relation: int or str,
                            main: bool = None) -> bool:
        '''
        Функция проверяет, является ли связь relation разрешённой для графа.
        :param relation: связь, о которой идёт речь
        :param main: параметр регулирует "тип" проверик. True - среди двух основных (default_edges_types), False - в
            дополнительных (additional_edges_types), None - чекает оба.
        :return: статус проверки: True - разрешена, False - запрещена.
        '''
        if main is None or main is True:  # чекаем основной список
            if relation in self.default_edges_types:  # Если есть в основном списке
                return True  # Вернём, что связь разрешена
        elif main is None or main is False:  # чекаем дополнительный
            if relation in self.additional_edges_types:
                return True  # Если есть - вернём разрешённость

        return False  # Если связь ни где не разрешена

    def add_edge(self, from_id: str or int or float or tuple, to_id: str or int or float or tuple,
                 edge_type: str or int or tuple = None,
                 add_to_both: bool = True,
                 create_missing: bool = True) -> bool or None:
        '''
        Функция добавляет связь между двумя элементами. Не дефолтные связи (edge_type != None) работают долго.
        Если связь нужно установить одностороннюю, то указывается только from_id элемент и явный тип связи в edge_type.
        :param from_id: индекс элемента, "от" которого идёт связь.
        :param to_id: элемент "к" которому идёт связь.
        :param edge_type: тип связи. Варианты: None - по умолчанию; str or int - установить обоим (или только from_id,
            если to_id не задан) конкретную связь. Она должна находиться или в additional_edges_types, или в
            Если указан tuple, то его длина должна быть 2, нулевой элемент которого называет тип связи родителя
            (в from_id называет тип связи к to_id), а первый - связь в ребёнке (в to_id тип связи от from_id).
        :param add_to_both: добавить ли связь обоим элементам? True - from_id получит ссылку на to_id соответствующим
            типом edge_type (или edge_type[0]), а to_id получит сслыку на from_id (A: Я->B; B: A->Я);
            False - добавится только ссылка у from_id на to_id (A: Я->B), а обратной ссылки не будет.
        :param create_missing: создать ли "недостающие" вершины.
        :return: статус выполнения операции: True - Всё ок, False - одного или обоих элементов не было в графе,
            None - ошибка (неверный тип edge_type или неразрешённая связь).
        '''
        # Првоерим доступ (именно так, ведь get_node не скажет - был ли элемент в графе или нет)
        if (self.__nodes_container.check_access(index=from_id) + self.__nodes_container.check_access(index=to_id)) == 2:
            result = True  # всё ок
        else:
            result = False  # "кого-то нет"
            if create_missing is False:  # Если создавать нельзя
                self.__to_log(message='Один из элементов отсутствует в графе',
                              log_type='ERROR', data={'from_id': from_id, 'to_id':to_id})
                return result  # вернём статус

        # Получим элементы
        from_element = self.get_node(element_id=from_id, create=create_missing)
        to_element = self.get_node(element_id=to_id, create=create_missing)

        # отформатируем связи в tuple
        if edge_type is None:  # Если свзяь дефолтная
            edge_type = self.default_edges_types  # Берём дефолтный
        else:  # Если это какой-то кастом
            # Сведём к форматному виду
            if isinstance(edge_type, str) or isinstance(edge_type, int):
                edge_type = (edge_type, edge_type)  # Делаем форматный tuple
            elif not isinstance(edge_type, tuple):  # Если тип не правильный (не один из указанных)
                self.__to_log(message='Тип данных добавляемой связи не является разрешённым',
                              log_type='ERROR', data={'edge_type': edge_type,'from_id': from_id, 'to_id': to_id})
                return None  # Это ошибка

            # Проверим разрешённость связей
            if (not self.is_relation_allowed(edge_type[0])) or (not self.is_relation_allowed(edge_type[0])):
                self.__to_log(message='Тип добавляемой связи не является разрешённым',
                              log_type='ERROR',
                              data={'edge_type': edge_type,
                                    'from_id': from_id,
                                    'to_id': to_id})
                return None

            # Првоерим существование типов связей у элементов (создадим, если их нет)
            if not from_element.check_relation_type(relation=edge_type[0]):
                from_element.create_relation_type(relation=edge_type[0])
            if not to_element.check_relation_type(relation=edge_type[1]):
                from_element.create_relation_type(relation=edge_type[1])

        # Добавим элементам связи
        from_element.add_relation(element_id=to_id, relation=edge_type[0])  # Добавили
        if add_to_both:  # Если добавляем обоим
            to_element.add_relation(element_id=from_id, relation=edge_type[1])  # Добавили

        return result

    # проверка связей
    def check_edge(self, from_id: str or int or float or tuple, to_id: str or int or float or tuple = None,
                   edge_type: str or int or tuple = None) -> bool or None:
        '''
        Функция проверяет наличие связи в графе from_id->to_id у обоих элементов. Если указан один элемент,
            проверяется связь только у него.
        :param from_id: индекс элемента, "от" которого идёт связь.
        :param to_id: элемент "к" которому идёт связь. Пустой, если связь "односторонняя".
        :param edge_type: тип связи. Варианты: None - по умолчанию; str or int - установить обоим (или только from_id,
            если to_id не задан) конкретную связь. Она должна находиться или в additional_edges_types, или в
            Если указан tuple, то его длина должна быть 2, нулевой элемент которого называет тип связи родителя
                в from_id называет тип связи к to_id), а первый - связь в ребёнке (в to_id тип связи от from_id).
        :return: статус выполнения операции:
            True - Всё ок, у обоих элементов связь есть (у одного, если указан только from_id);
            False - одного или обоих элементов не было в графе, или у одного или обоих элементов нет связи;
            None - ошибка (неверный тип edge_type или неразрешённая связь).
        '''

        return

    # Удалить связь
    def del_edge(self, from_id: str or int or float or tuple, to_id: str or int or float or tuple = None,
                 edge_type: str or int or tuple = None):
        '''
        Функция добавляет связь между двумя элементами. Не дефолтные связи (edge_type != None) работают долго.
        Если связь нужно установить одностороннюю, то указывается только from_id элемент и явный тип связи в edge_type.
        :param from_id: индекс элемента, "от" которого идёт связь.
        :param to_id: элемент "к" которому идёт связь. Пустой, если связь "односторонняя".
        :param edge_type: тип связи. Варианты: None - по умолчанию; str or int - установить обоим (или только from_id,
            если to_id не задан) конкретную связь. Она должна находиться или в additional_edges_types, или в
            Если указан tuple, то его длина должна быть 2, нулевой элемент которого называет тип связи родителя
                в from_id называет тип связи к to_id), а первый - связь в ребёнке (в to_id тип связи от from_id).
        :return: статус выполнения операции: True - Всё ок, False - одного или обоих элементов не было в графе,
            None - ошибка (неверный тип edge_type или неразрешённая связь).
        '''
        # Проверить, если ti_id None у элемента, на который идёт связь, её отсутсвтие.

        return