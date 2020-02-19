'''
Фабрика по сбору элементов графа

'''

from Graphs.MainObjects.ElementsAndEdges import GraphConfiguration, EdgeIdentification
from Graphs.MainObjects.ElementsAndEdges import EdgeRelationsList, EdgeRelationsSet, EdgeRelationsString



class GraphElement(EdgeIdentification):

    def __init__(self,
                 element_id: str or int or float or tuple,
                 label: object = None,
                 graph_configuration: GraphConfiguration = None,
                 edge_relations: str = 'list'):
        '''

        :param element_id: индекс элемента или ссылка на сопоставленный объект.
        :param label: метка элемента. Например его тип.
        :param graph_configuration: конфигурационный объект графа
        :param edge_relations:  тип хранения связей: 'list', 'set', 'str' - указывает контейнер для связей.
        '''

        EdgeIdentification.__init__(self,
                                    element_id=element_id,
                                    label=label,
                                    graph_configuration=graph_configuration)

        if edge_relations == 'list':
            self.__relations = EdgeRelationsList
        elif edge_relations == 'str':
            self.__relations = EdgeRelationsSet
        elif edge_relations == 'set':
            self.__relations = EdgeRelationsString



class EdgesFactory:
    '''
    Фабрика производит элементы графа, но не добавляет их в контейнер!

    '''
    def __init__(self, graph_configuration: GraphConfiguration = None,
                 directed_nodes: bool = True,
                 additional_nodes: list or tuple = None,
                 edge_relations: str = 'list'):
        '''

        :param graph_configuration: конфигурационный объект графа
        :param directed_nodes: являются ли связи направленными?
            True - да. Элемент получит типы связей  ('p', 'c'): parents - связи, приходящие от радителей, children -
                связи, исходящие к дочерним элементам.
            False - у элемента будет единственный тим связи 'all'
        :param additional_nodes: дополнительные типы связей, которые будут исплльзованы в элементе.
        :param edge_relations: тип хранения связей: 'list', 'set', 'str' - указывает контейнер для связей.
        '''