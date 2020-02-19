'''
Тут находятся "основные" объекты графа:
    GraphConfiguration - идентификационный ключ графа

'''
import copy

# ------------------------------------------------------------------------------------------------
# Идентификатор графа ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class GraphConfiguration:
    '''
    Идентификационный объект графа.
    Методы и свойства:
        graph_id - индекс графа

        edges_values - есть ли у графа объекты, находящиеся на рёбрах

        directed_edges - tuple с "направленными" типами вязей

        non_directed_edges - tuple с "ненаправленными" типами вязей

        callback - нужно ли указывать "обратную" связь?

        relations_container_type - тип контейнера для связей 'list', 'set', 'str' - хранятся в контейнерах,
            'dict' - создаёт отдельный тип графа, в котором используется словарь.
    '''

    __default_edge_relations = 'list'
    __default_default_edge = 'r'

    def __init__(self, graph_id: str or int or float or tuple = None,
                 edges_values: bool = False,

                 directed_edges: list or tuple = None,
                 non_directed_edges: list or tuple or str or int = None,
                 default_edge: str or int = None,
                 callback: bool = True, relations_container_type: str = 'list'
                 ):
        '''
        Если не заданы никакие связи, то будет использоваться default_edge в качестве ненаправленной связи.

        :param graph_id: индекс графа, который будет использоваться в работе.
        :param edges_values: статус наличия DTO объектов на связях графа. True - есть, False - нет.
        :param directed_edges: "направленные" связи. Обект знает: входит она в него или выходит.
            Пересечения с non_directed_edges будут удалены в пользу их вхождения в directed_edges.
        :param non_directed_edges: ненаправленные связи - "вход" и "выход" эквивалентны.
            Пересечения с directed_edges будут удалены в пользу их вхождения в directed_edges.
        :param default_edge: связь, считающаяся "по умолчанию". Приоритет: directed_edges[0], non_directed_edges[0],
            self.__default_default_edge - ставится направленная связь 'r'.
            Если заданы default_edge, directed_edges и/или non_directed_edges, default_edge должна входить в них,
            иначе тоже берётся self.__default_default_edge - направленная связь 'r'.
        :param callback: извещать ли элемент, к которому идёт связь, о её наличии? Элемент, из которого
            выходит связь оповещается автоматически.
        :param relations_container_type:  тип контейнера для связей 'list', 'set', 'str' - хранятся в контейнерах,
            'dict' - создаёт отдельный тип графа, в котором используется словарь.
        '''

        self.__graph_id = graph_id
        self.__edges_values = edges_values

        if relations_container_type in ['list', 'set', 'str', 'dict']:
            self.__relations_container_type = relations_container_type
        else:
            self.__relations_container_type = self.__default_edge_relations



        self.__callback = callback





    def __set_edges(self, directed_edges: list or tuple = None,
                    non_directed_edges: list or tuple or str or int = None,
                    default_edge: str or int = None):
        '''

        :param directed_edges: "направленные" связи. Обект знает: входит она в него или выходит.
            Пересечения с non_directed_edges будут удалены в пользу их вхождения в directed_edges.
        :param non_directed_edges: ненаправленные связи - "вход" и "выход" эквивалентны.
            Пересечения с directed_edges будут удалены в пользу их вхождения в directed_edges.
        :param default_edge: связь, считающаяся "по умолчанию". Приоритет: directed_edges[0], non_directed_edges[0],
            self.__default_default_edge - ставится направленная связь 'r'.
            Если заданы default_edge, directed_edges и/или non_directed_edges, default_edge должна входить в них,
            иначе тоже берётся self.__default_default_edge - направленная связь 'r'.
        :return:
        '''

        if directed_edges is None:
            directed_edges = tuple()
        elif not isinstance(directed_edges, tuple):
            directed_edges = tuple(directed_edges)
        self.__directed_edges = directed_edges

        if non_directed_edges is None:
            non_directed_edges = tuple()
        elif not isinstance(non_directed_edges, tuple):
            non_directed_edges = tuple(non_directed_edges)

        # Дропнем пересечение типов если оно есть. Отдав приоритет на направленные (т.к. они информативнее).
        non_directed_edges = tuple(set(non_directed_edges) - set(directed_edges))
        self.__non_directed_edges = non_directed_edges

        # Сделаем словарь для индексирования типов связи:


        self.__default_edge = self.__set_default_edge(default_edge=default_edge)



    def __set_default_edge(self, default_edge: str or int) -> str or int:
        '''
        Функция устанавливает "связь поумолчанию".

        :param default_edge: связь, считающаяся "по умолчанию". Приоритет: directed_edges[0], non_directed_edges[0],
            self.__default_default_edge - ставится направленная связь 'r'.
        :return: статус
        '''
        if default_edge is None:
            if len(self.directed_edges) > 0:  # Если есть элементы
                return self.directed_edges[0]  # чекаем нулевой

            elif len(self.non_directed_edges) > 0:  # Если есть элементы
                return self.non_directed_edges[0]  # чекаем нулевой

            else:  # Если никого нет
                self.__directed_edges = tuple(self.__default_default_edge)  # Добавим в tuple направленных связей
                return self.__default_default_edge  # Берём дефолтный

        else:  # Если задан
            if default_edge in self.directed_edges or default_edge in self.non_directed_edges:  # Если есть в списке
                return default_edge
            else:  # Если нет указанного типа
                self.__directed_edges = tuple(self.__default_default_edge) + self.__directed_edges  # Добавим в tuple направленных связей
                return self.__default_default_edge  # Берём дефолтный

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

    @property
    def directed_edges(self) -> tuple:
        '''
        Функция отдаёт типы "направленных" связей.

        :return: tuple. Пуст, если не заданы.
        '''
        return copy.copy(self.__directed_edges)

    @property
    def non_directed_edges(self) -> tuple:
        '''
        Функция отдаёт "ненаправленные" связи

        :return:  tuple. Пуст, если не заданы.
        '''
        return copy.copy(self.__non_directed_edges)

    @property
    def callback(self) -> bool:
        '''
        Функция указывает: нужно ли для связи A->B, элементу B указывать связь из А.

        :return: статус
        '''
        return self.__callback

    @property
    def relations_container_type(self) -> str:
        '''
        Отдаёт индекс, указывающий тип контейнеров для связи

        :return: строка с типом: 'list', 'set', 'str', 'dict'
        '''
        return self.__relations_container_type

    @property
    def default_edge(self) -> str or int:
        '''
        Отдаёт "связь поумолчанию"

        :return:
        '''
        return self.__default_edge

    # ------------------------------------------------------------------------------------------------
    # Проверка связей --------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def id_edge_directed(self, edge: str or int) -> bool or None:
        '''
        Функция проверяет тип связи и его наличие.

        :param edge: интересующий тип.
        :return: True - связь направленная, False - связь ненаправленная
        '''
        if edge in self.directed_edges:  # Если направлена
            return True
        elif edge in self.non_directed_edges:  # Если ytнаправлена
            return False
        else:
            return None  # Если тип не опознан

