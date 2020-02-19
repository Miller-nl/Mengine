'''
В "Контейнер" данных на ряду с set, list, str, dict добавить nx - networkx.


Граф сделать как контейнер "опознавательных" частей элементов. а вот уже хранение связей делегировать в
    один из вариантов контейнеров, указанных выще.

    Особенность в том, что при хранении в словаре и nx мы будем генерить связи в списки "на лету"? Или как?

Сначала сделать граф для одного типа связей - направленный, ненаправленынй. После сделать граф для нескольких типов.

Короче там разница получается в следующем?

Стандартные методы и свойства

    Вершины
        nodes_ids - список индексов элементов

        get_node(element_id) -> object or Nine - отдаёт вершину графа, если она была.

        create_node(element_id, label) -> bool or None - создаёт вершину с меткой label

        check_node(element_id) -> bool - проверяет наличие вершины

        nodes(parameter, value) -> list - срез вершин по параметру. Типа выделить "магазины" или "клиентов"

        labeled_nodes(value) -> list - отдаёт список вершин с меткой value

    Связи
        add_edge(from_id, to_id, type, callback: bool or None,
                 create: bool = False) -> bool or None - Добавляет связь от from_id
            к to_id типа type, если связь ненаправлена, то callback укажет - стоит ли оповестить элемент
            to_id о связи типа type с from_id? create - создать отсутствующие?
            Ответ: True - Успешно, False - нет/небыло одного или обоих элемнтов, None - запрещённый тип связи.

        check_edge(from_id, to_id, type, direct: bool or None) -> bool or None - проверяет наличие связи между from_id и
            to_id типа type. direct указывает, какую связь проверять True - от from_id к to_id, False - обратаня: от
            to_id к from_id, None - любая.
            Ответ: True - есть, False - нет, None - запрещённый тип связи.

        del_edge(from_id, to_id, type, direct: bool or None) -> bool or None - удаляет связь между from_id и
            to_id типа type. direct указывает, какую связь удалить True - от from_id к to_id, False - обратную: от
            to_id к from_id, None - обе.
            Ответ: True - удалено, False - нет одного или обоих элемнтов, None - запрещённый тип связи.

        ВОПРОС - отдавать в каком виде?

        edges(parameter, value) -> list - срез вершин по параметру. Типа выделить "магазины" или "клиентов"

        typied_edges(type, direct: bool or None) -> list - отдаёт набор связей указанного типа.

        labeled_nodes(value) -> list - отдаёт список связей с меткой value

    Конвертация
        в networkx
        в Gephi

'''
from SystemCore.DataContainers.SimpleContainer import SimpleContainer
from Graphs.MainObjects.EdgesNodes import GraphConfiguration, EdgeIdentification
from Graphs.MainObjects.EdgesNodes import NodeRelationsList, NodeRelationsSet, NodeRelationsString


# ------------------------------------------------------------------------------------------------
# Создание элементов -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class ElementsFactory:

    def __init__(self, graph_configuration: GraphConfiguration):
        '''

        :param graph_configuration:  идентификационный ключ графа.
        '''

        self.__graph_configuration = graph_configuration

    @property
    def graph_configuration(self) -> GraphConfiguration or None:
        '''
        Получение идентификатора графа.

        :return: объект - идентификатор или None, если его нет.
        '''
        return self.__graph_configuration

    # ------------------------------------------------------------------------------------------------
    # Создание элементов -----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def create_node(self, node_id: str or int or float or tuple,
                    label: object = None) -> :
        '''

        :param element_id: индекс элемента или ссылка на сопоставленный объект.
        :param label: метка элемента. Например его тип.
        :return:
        '''

'''
            :param directed_edges: "направленные" связи. Обект знает: входит она в него или выходит.
            :param non_directed_edges: ненаправленные связи - "вход" и "выход" эквивалентны
            :param callback: извещать ли элемент, к которому идёт связь, о её наличии? Элемент, из которого
                выходит связь оповещается автоматически.
            :param edge_relations:  тип хранения связей: 'list', 'set', 'str' - указывает контейнер для связей.
            '''


# ------------------------------------------------------------------------------------------------
# Граф -------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

class Graph:
    '''
    Сейчас выглядит так. Интерфейс останется, начинку можно будет изменить позже.

    '''


    def __init__(self, graph_id: str or int or float or tuple = None,
                 edges_values: bool = False,

                 directed_edges: list or tuple or str or int = None,
                 non_directed_edges: list or tuple or str or int = None,
                 callback: bool = True, relations_container_type: str = 'list'
                 ):
        '''
        :param graph_id: индекс графа, который будет использоваться в работе.
        :param edges_values: статус наличия DTO объектов на связях графа. True - есть, False - нет.
        :param directed_edges: "направленные" связи. Обект знает: входит она в него или выходит.
        :param non_directed_edges: ненаправленные связи - "вход" и "выход" эквивалентны
        :param callback: извещать ли элемент, к которому идёт связь, о её наличии? Элемент, из которого
            выходит связь оповещается автоматически.
        :param relations_container_type: тип контейнера для связей 'list', 'set', 'str' - хранятся в контейнерах,
            'dict' - создаёт отдельный тип графа, в котором используется словарь.
        '''

        # Конвертнём насройки в объект
        self.__graph_configuration = GraphConfiguration(graph_id=graph_id, edges_values=edges_values,
                                                        directed_edges=directed_edges,
                                                        non_directed_edges=non_directed_edges,
                                                        callback=callback, relations_container_type=relations_container_type)
