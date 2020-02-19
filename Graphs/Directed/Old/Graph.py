''' готово, отлажено
# --------------------------------------------------------------------------------------------------------
# Объект DirectedGraphData -------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Объект для хранения направленного графа в виде набора объектов GraphElementData.

Важные оговорки:
    1 в графе не производится никаких манипуляций над/с объектами, не включенными в граф: не образуются
        связи между отсутствующими объектами и объектами графа; "отсутствующие" не участвуют в рассчётах.
    2 в графе индекс обязательно int, а вот ограничения на токены накладывается лишь тем, что они должны
        быть сравнимы: >,<,=.
    3 При создании элемента в графе, последний получает статус "не готов". При добавлении элемента,
        если элемент требует включения в граф, то статус так же будет установлен как "не готов", в противном случае
        изменение статуса при добавлении не произойдёт.

Параметры init
    identification_key - идентификационный ключ графа.


Доступные методы
    @property
        prepared - детектор "построенности графа". Если добавляется какой-либо элемент, он меняется на False

    # Проверка доступа
        access(el_id: int) -> bool - проверяет наличие в словаре элемента el_id

    # Добавление новых объектов
        create(el_id: int, tokens_list: list = None, replace: bool = False) -> bool - Функция создаёт объект
            GraphElement, являющийся элементом графа. Устанавливает self.__prepared = False. Без подгрузки из SQL.
            :param el_id: id нового объекта
            :param tokens_list: список токенов нового объекта
            :param replace: заменить объект, если он существует?
            :return: bool - успешность: true - элемента не было, он создан; False - элемент был. перезаведение
                по repalce.

        add_element(graph_element: GraphElement, replace: bool = False) -> bool - Функция добавляет в словарь готовый
            объект. Если GraphElement.need_to_process = True, то готовность графа сбрасывается: self.__prepared = False.
            Важно, что элементу GraphElement будет передан идентификационный ключ self.identification_key принудительно.
            :param graph_element: элемент графа
            :param replace: заменить ли, если этот элемент уже есть?
            :return: статус выполнения. Если элемент уникален - True, если элемент уже есть - False.

        del_element(el_id: int) -> bool - функция пытается удалить элемент el_id.
            :param el_id: индекс элемента графа
            :return: статус выполнения. Если элемент удалён - True, если элемента и так не было - False.

    # Работа над элементами
        get_elements_ids() -> list - Функция выдаёт список id всех элементов, находящихся в графе.

        get_element(el_id: int) -> GraphElement or None - фукнция передаёт ссылку на элемент графа el_id. Без подгрузки
            из базы данных или иного источника.
            :param el_id: индекс объекта
            :return: GraphElement или None

        parental_edge(parent_id: int, child_id: int) -> bool - Функция добавляет связь от родителя к ребёнку в граф.
            :param parent_id: индекс родителя
            :param child_id: индекс ребёнка
            :return: status (bool). True, если успешно, False, если какого-либо узла нет.

        absorption(eater_id: int, feeder_id: int) -> bool - фукнция "поглощения". Она служит для для "поедания" текущим
            объектом связей другого объекта. Важно, что дублёра поглотить нельзя, как и дублёр не может поглотить
            кого-либо. При этом, если объект из списка связей feeder_id не будет найден, то и связь с не найденным
            объектом скорретирована не будет.
            :param eater_id: индекс объекта, который поглощает. Не дублёр
            :param feeder_id: индекс объекта, который надо поглотить. Не дублёр
            :return: статус выполнения. True - без ошибок, а False - была какая-либо ошибка (кого-то не нашли в наборе).


self параметры
    identification_key - идентификационный ключ графа.
    __Graph_elements_dict - словарь элементов GraphElement
    __prepared - параметр готовности графа. Важно, что при добавлении любого нового элемента, параметр сбрасывается
            на False, т.к. граф получает не встроенные в него элементы.


# --------------------------------------------------------------------------------------------------------
# Объект DirectedGraph -----------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Оболочка над DirectedGraphData, задача которой обеспечить работу процессов пстроения графа, загрузки из базы,
отгрузки в базу, экспорта графа в нужной форме для каких-либо обработок.

Важные оговорки:
    1 в графе не производится никаких манипуляций над/с объектами, не включенными в граф: не образуются
        связи между отсутствующими объектами и объектами графа; "отсутствующие" не участвуют в рассчётах.
    2 в графе индекс обязательно int, а вот ограничения на токены накладывается лишь тем, что они должны
        быть сравнимы: >,<,=.
    3 При создании элемента в графе, последний получает статус "не готов". При добавлении элемента,
        если элемент требует включения в граф, то статус так же будет установлен как "не готов", в противном случае
        изменение статуса при добавлении не произойдёт.

Комментарий:
    self.__Graph_elements_dict_link = self._DirectedGraphData__Graph_elements_dict - для удобства


Параметры init
    launch_module_name: str - параметр для логирования
    process_manager: ProcessesManager - менеджер текущего процесса
    sql_upload_allowed: bool = False - разрешение на подгрузку данных из базы, если запрошенный элемент отсутствует
    identification_key - идентификационный ключ графа.

Доступные методы

    основные @property (БЕЗ setter-а!)
        sql_upload_allowed - получить статус разрешения на работу с базой. Без Setter-a т.к. сейчас SQL модуль
            подгружается в __init__ - e
    @property
        name - имя графа для внешнего пользования. Не связано с MyName
        prepared - детектор "построенности графа". Если добавляется какой-либо элемент, он меняется на False
        narrowed - детектор суженности графа "на себя".

    # Проверка доступа
        access(el_id: int) -> bool - проверяет наличие в словаре элемента el_id

    # Добавление новых объектов
        create(el_id: int, tokens_list: list = None, replace: bool = False) -> bool - Функция создаёт объект
            GraphElement, являющийся элементом графа. Устанавливает self.__prepared = False. Без подгрузки из SQL.
            Важно, что элементу GraphElement будет передан идентификационный ключ self.identification_key принудительно.
            :param el_id: id нового объекта
            :param tokens_list: список токенов нового объекта
            :param replace: заменить объект, если он существует?
            :return: bool - успешность: true - элемента не было, он создан; False - элемент был. перезаведение
                по repalce.

        add_element(graph_element: GraphElement, replace: bool = False) -> bool - Функция добавляет в словарь готовый
            объект. Если GraphElement.need_to_process = True, то готовность графа сбрасывается: self.__prepared = False.
            :param graph_element: элемент графа
            :param replace: заменить ли, если этот элемент уже есть?
            :return: статус выполнения. Если элемент уникален - True, если элемент уже есть - False.

        del_element(el_id: int) -> bool - функция пытается удалить элемент el_id.
            :param el_id: индекс элемента графа
            :return: статус выполнения. Если элемент удалён - True, если элемента и так не было - False.

    # Работа над элементами
        get_elements_ids() -> list - Функция выдаёт список id всех элементов, находящихся в графе.

        get_element(el_id: int, try_to_upload: bool = None) -> GraphElement or None - Функция выдаёт ссылку на объект
            класса GraphElement с индексом el_id. Функция переобозначена, т.к. в неё добавлена возможность подгрузки
            элемента из SQL таблицы
            :param el_id: индекс объекта
            :param try_to_upload: попробовать ли подгрузить элемент из таблицы?
            :return: GraphElement или None

        parental_edge(parent_id: int, child_id: int) -> bool - Функция добавляет связь от родителя к ребёнку в граф.
            :param parent_id: индекс родителя
            :param child_id: индекс ребёнка
            :return: status (bool). True, если успешно, False, если какого-либо узла нет.

        absorption(eater_id: int, feeder_id: int) -> bool - фукнция "поглощения". Она служит для для "поедания" текущим
            объектом связей другого объекта. Важно, что дублёра поглотить нельзя, как и дублёр не может поглотить
            кого-либо. При этом, если объект из списка связей feeder_id не будет найден, то и связь с не найденным
            объектом скорретирована не будет.
            :param eater_id: индекс объекта, который поглощает. Не дублёр
            :param feeder_id: индекс объекта, который надо поглотить. Не дублёр
            :return: статус выполнения. True - без ошибок, а False - была какая-либо ошибка (кого-то не нашли в наборе).

    # Работа с базой
        upload_element(el_id: int, add_to_graph: bool = True) -> GraphElement or None - функция пытается подгрузить
            из SQL таблицы el_id элемент. Если add_to_graph=True, то prepared = False, и элемент добавляется в граф.
            Пока не работает - всегда выдаёт None.
            :param el_id: индекс элемента, который мы попытаемся подгрузить
            :param add_to_graph: добавить объект в граф?
            :return: ссылка на объект или None, если подгрузка не удалась.

    # Сужение графа
        narrow_down() - функция выполняет "сужение графа" на себя. То есть - зачищает связи с элементами, которые
            на момент запуска не находятся в графе.

    # Получение данных о наборе
        get_heads(processed: bool = True) -> list - функция выдаёт список элементов, у которых нет родителей.
            Опционально можно указать, должны ли быть эти элементы уже включены в граф.
            :param processed: собирать только готовые фразы? True - да, False - все.
            :return: список "голов" графа. То есть - элементов, у которых нет родителей.

        get_not_processed() -> dict - функция передаёт словарь с id необработанных элементов. Вид словаря:
            {len: ids_list}, в списках находятся индексы.
            :return: словарь формата {len: ids_list}, где len - количество токенов, а ids_list - список непроработанных
                элементов, имеющих длину списка токенов len.

    # Групповые манипуляции
        mark_as_done(processed_list: list) - Функция отметит все элементы из списка processed_list как
            "не нуждающиеся в обработке" (GraphElement.need_to_process=False)
            :param processed_list: список отработанных индексов
            :return: ничего

        clear_missed_connections() - Задача функции: обойти элементы графа и дропнуть из их списков связей индексы
            элементов, которых нет текущем в наборе. Смысл - не получать ошибки в работе из-за того, что при обработке
            будут запрашиваться отсутствующие графовые элементы. Если хоть где-то было выполнено сужение элемента,
            то narrowed примет значение True.
            :return: - ничего.

    # Функция построения
        upbuild() -> bool - Функция включает в граф элементы, которые уже в словаре графа, но ещё в него ещё не
            включены. То есть - образует связи для элементов с параметром need_to_process=True.
            Комментарий: у фраз параметр "need_to_process" будет меняться только после полного обхода графа.
            Таким образом во время построения случай, когда need_to_process=False приравниевается к необходимости
            разворота рассчёта.
        :return: статус успешности. True - без ошибок, False - с ошибками.


        include_element(new_element: int, heads_ids_list: list = None, mark_as_included: bool = False) -> bool -
            Функция включает в граф объект new_element, при этом с качестве "головных" элементов используюся указанные
            в heads_ids_list. То есть - фукнция встраивает new_element в ветви элементов из heads_ids_list.
            :param new_element: новый элемент, который будет включён в граф. При этом важно, что объект, отвечающий
                этому элементу включается в граф ВНЕ этой функции.
            :param heads_ids_list: список элементов, которые будут считаться(!) головами. То есть, в ветви которых мы
                вошьём new_element, или ветви которых мы пришьём к new_element. Это оптимизационный параметр - чтобы
                не собирать список для каждого элемента графа, так как это очень тяжёлая операция.
            :param mark_as_included: отметить ли новый элемент как обработанный. Имеет смысл, если мы кастомно вставляем один
                элемент, но такой сценарий скорее всего сигнализирует о неверном использовании этой функции.
                Прична в том, что для новых элементов не делается "разворот" на проверку детей, и это экономит время работы.
            :return: успешность выполнения (выполнено без ошибок)

self параметры
    name - имя графа для внешнего пользования. Не связано с MyName
    MyName - своё имя. Для логирования
    identification_key - идентификационный ключ графа.
    __narrowed - детектор того, сужался ли граф.
    __Graph_elements_dict_link - ссылка на словарь элементов GraphElement - _DirectedGraphData__Graph_elements_dict
    __Logger - логер
    __to_log - функция отправки сообщения в лог
    __sql_upload_allowed - детектор разрешения на работу с базой


Комментарий по доработке
После подключения базы в работу нужно сделать функцию подгрузки запрошенного элемента из базы.

Комментарий по работе графа
Как показывает опыт - в графе из N элементов мы имеем порядка 3N связей, и в таком случае количество памяти,
требующееся для кодирования данных в таблице может быть на два порядка выше, чем количество памяти, требующееся для
кодирования строками. При этом были опробованы списки и словари, они тоже требуют больше памяти, чем вариант со
строками в GraphElement.
Скорость текущего варианта наибольшая из всех опробованных.

Комментарий по идентификационному ключу
При создании элемента, граф передаёт ему собственный идентификационный ключ.
При добавлении элемента ему принудительно устанавливается идентификационный ключ текущего графа, игнорируя уже имевшийся
у объекта идентификационный ключ при этом проверка совпадения не делается, т.к. операция создания элемента выполняется
в DirectedGraphData, в котором нет логирования.
Сам же идентификационный ключ на данный момент никак(!) не защищён от изменения ни в графе, ни в его элементах.
'''

from Managers import ProcessesManager

from Graphs.Directed.GraphElement import GraphElement  # Элемент графа
from DataContainers.SetsFunctionality import ContainerIdentificationKey

# --------------------------------------------------------------------------------------------------------
# Объект DirectedGraphData -------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
# класс для хранения данных
class DirectedGraphData:
    '''
    Класс, являющийся самим графом. Класс хранит информацию и предоставляет основной набор методов для её получения.
    '''

    def __init__(self, identification_key: ContainerIdentificationKey = None):
        '''
        Функция настройки объекта
        :param identification_key: идентификационный ключ графа.
        '''
        self.identification_key = identification_key  # Установим идентификационный объект

        # Обновление данных графа
        self.__Graph_elements_dict = {}

        self.__prepared = True  # Детектор построенности графа

    # --------------------------------------------------------------------------------------------------------
    # Работа с пропертями ------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    @property
    def prepared(self):
        return self.__prepared

    @prepared.setter
    def prepared(self, value: bool):
        if isinstance(value, bool):
            self.__prepared = value
        return

    # --------------------------------------------------------------------------------------------------------
    # Проверки -----------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Проверка наличия в графе
    def access(self, el_id: int) -> bool:
        '''
        Функция првоеряет существование элемента el_id в графе (есть ли он в self.__Graph_elements_dict.keys() ?)
        :param el_id: индекс, который надо проверить
        :return: статус проверки
        '''
        try:
            a = self.__Graph_elements_dict[el_id]  # Проверим доступ
            return True  # Если он есть
        except BaseException:  # Если доступа нет
            return False

    # --------------------------------------------------------------------------------------------------------
    # Добавление новых объектов ------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # создать новый объект
    def create(self, el_id: int, tokens_list: list =None,
               replace: bool = False) -> bool:
        '''
        Функция создаёт объект GraphElement, являющийся элементом графа. Устанавливает self.__prepared = False.
            Без подгрузки из SQL.
        :param el_id: id нового объекта
        :param tokens_list: список токенов нового объекта
        :param replace: заменить объект, если он существует?
        :return: bool - успешность: true - элемента не было, он создан; False - элемент был. перезаведение по repalce.
        '''

        asses = self.access(el_id=el_id)  # Проверим, есть и объект с таким id

        if asses:  # Если доступ есть
            if not replace:  # Если элемент есть и замена запрещена
                return False  # Вернём, что элемент был
            else:  # если замена разрешена
                result = False  # результат - элемент был, его заменим
        else:
            result = True  # Всё ок

        self.__Graph_elements_dict[el_id] = GraphElement(element_id=el_id,
                                                         identification_key=self.identification_key)  # Создадим объект
        self.__prepared = False

        if not tokens_list is None:  # Если задан список токенов
            self.__Graph_elements_dict[el_id].tokens_list = tokens_list  # Передадим его объекту

        return result

    # добавить элемент
    def add_element(self, graph_element: GraphElement,
                    replace: bool = False) -> bool:
        '''
        Функция добавляет в словарь готовый объект.
        Если GraphElement.need_to_process = True, то готовность графа сбрасывается: self.__prepared = False.
        :param graph_element: элемент графа
        :param replace: заменить ли, если этот элемент уже есть?
        :return: статус выполнения. Если элемент уникален - True, если элемент уже есть - False.
        '''

        try:
            a = self.__Graph_elements_dict[graph_element.element_id]  # Попробуем запросить индекс элемента графа
            if not replace:  # Если замена запрещена
                return False
            else:  # Если замена разрешена
                result = False  # запомним, что такой элемент не уникален
        except KeyError:  # Если элемента нет
            result = True  # Запомним для return - a

        # Установим свой идентификационный ключ!
        graph_element.identification_key = self.identification_key

        self.__Graph_elements_dict[graph_element.element_id] = graph_element  # Добавим объект в словарь

        if graph_element.need_to_process:  # Если элемент графа требует включения в граф
            self.__prepared = False

        return result

    # удалить элемент
    def del_element(self, el_id: int) -> bool:
        '''
        Фукниция пытается удалить элемент el_id
        :param el_id: индекс элемента графа
        :return: статус выполнения. Если элемент удалён - True, если элемента и так не было - False.
        '''
        try:  # Пробуем удалить
            self.__Graph_elements_dict.pop(el_id)
            return True
        except KeyError:  # Если элемента не было
            return False

    # --------------------------------------------------------------------------------------------------------
    # Работа над элементами ----------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Получить список элементов, находящихся в графе
    def get_elements_ids(self) -> list:
        return list(self.__Graph_elements_dict.keys())

    # Получить ссылку на объект графа
    def get_element(self, el_id: int) -> GraphElement or None:
        '''
        Функция выдаёт ссылку на объект класса GraphElement с индексом el_id.
        :param el_id: индекс объекта
        :return: GraphElement или None
        '''
        try:  # Пробуем сразу отдать элемент
            return self.__Graph_elements_dict[el_id]
        except BaseException:  # Если не удалось получить ссылку
            return None  # Вернём None

    # Добавить связь между элементами
    def add_parental_edge(self, parent_id: int, child_id: int) -> bool:
        '''
        Функция добавляет связь между элементами.
        :param parent_id: индекс родителя
        :param child_id: индекс ребёнка
        :return: status (bool). True, если успешно, False, если какого-либо узла нет.
        '''
        # Получим элементы
        FromElement = self.get_element(el_id=parent_id)  # "Родитель"
        if FromElement is None:
            return False
        ToElement = self.get_element(el_id=child_id)  # Ребёнок
        if ToElement is None:
            return False

        # Добавим связь
        FromElement.add_to(element_id=child_id, relation='child')
        ToElement.add_to(element_id=parent_id, relation='parent')

        return True  # Завершим

    # функция поглощения элементом графа другого элемента
    def absorption(self, eater_id: int, feeder_id: int) -> bool:
        '''
        Функция для поедания текущим объектом связей другого объекта. Важно, что дублёра поглотить нельзя,
        как и дублёр не может поглотить кого-либо. При этом, если объект из списка связей feeder_id не будет найден,
        то и связь перекинута не будет.
        :param eater_id: индекс объекта, который поглощает. Не дублёр
        :param feeder_id: индекс объекта, который надо поглотить. Не дублёр
        :return: статус выполнения. True - без ошибок, а False - была какая-либо ошибка (кого-то не нашли в наборе).
        '''

        # Получим объекты
        eater_object = self.get_element(el_id=eater_id)
        feeder_object = self.get_element(el_id=feeder_id)
        if eater_object is None or feeder_object is None:  # Если хоть один объект не получен
            return False

        if eater_object.duplicate or feeder_object.duplicate:  # Если кто-то является дублёром
            return False  # Выходим, мы не можем его поглотить.

        # Перекинуть связи с feeder_id на eater_id
        is_ok = True
        for el in feeder_object.nearest_parents:
            # Пошли заменим у родителей feeder_id в списке детей feeder_id на eater_id
            Parent = self.get_element(el_id=el)  # Получим элемент
            if Parent is None:  # Если элемента нет
                is_ok = False  # Запомним, что была ошибка
                continue  # Скипаем замену (и для eater_object)
            else:
                Parent.replace(old_value=feeder_id, new_value=eater_id, relation='child')
                # Добавим eater_id родителя
                eater_object.add_to(element_id=el, relation='parent')

        for el in feeder_object.nearest_children:
            # Пошли заменим у детей feeder_id в списке родителей feeder_id на eater_id
            Child = self.get_element(el_id=el)  # Получим элемент
            if Child is None:  # Если элемента нет
                is_ok = False  # Запомним, что была ошибка
                continue  # Скипаем работу
            else:  # Если всё ок
                Child.replace(old_value=feeder_id, new_value=eater_id, relation='parent')
                # добавим eater_id ребёнка
                eater_object.add_to(element_id=el, relation='child')

        for el in feeder_object.doubles:
            # Пошли заменим у дублей feeder_id в списке родителей feeder_id на eater_id
            Double = self.get_element(el_id=el)  # Получим элемент
            if Double is None:  # Если элемента нет
                is_ok = False  # Запомним, что была ошибка
                continue  # Скипаем
            else:
                Double.replace(old_value=feeder_id, new_value=eater_id, relation='double')
                # добавим eater_id дублёра
                eater_object.add_to(element_id=el, relation='double')

        # Установить feeder_id дублёром
        eater_object.add_to(element_id=feeder_id, relation='double')  # Добавим feeder-a в список дублёров eater-a
        feeder_object.set_me_as_double(original_id=eater_id)  # Обновим статус объекта.

        return is_ok

# --------------------------------------------------------------------------------------------------------
# Объект DirectedGraph -----------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
# Класс с массивными методами
class DirectedGraph(DirectedGraphData):
    '''
    Нюанс:
        self.__Graph_elements_dict_link = self._DirectedGraphData__Graph_elements_dict  # для удобства
    '''

    def __init__(self, process_manager: ProcessesManager, launch_module_name: str = None,
                 sql_upload_allowed: bool = False,
                 identification_key: ContainerIdentificationKey = None,
                 ):
        '''
        Функция настройки объекта
        :param sql_upload_allowed: разрешена ли подгрузка недостающих объектов из SQL таблицы?

        :param launch_module_name: имя вызывающего модуля (для логгера)
        :param process_manager: менеджер текущего процесса

        :param identification_key: "идентификационынй ключ" графа
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name,
                                                      log_initialization=True)
        self.__to_log = self.__Logger.to_log

        self.__narrowed = False  # Детектор того, что в графе было сужение

        DirectedGraphData.__init__(self, identification_key=identification_key)  # Выполним init DirectedGraphData
        self.__Graph_elements_dict_link = self._DirectedGraphData__Graph_elements_dict  # Для удобства сделаем ссылку

        # И сделаем дополнительные манипуляции
        self.__sql_upload_allowed = sql_upload_allowed  # Обозначим подгрузку с базы

    # --------------------------------------------------------------------------------------------------------
    # Работа с пропертями ------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    @property  # Было ли сужение в графе
    def narrowed(self):
        return self.__narrowed

    @narrowed.setter
    def narrowed(self, value: bool):
        self.__narrowed = value
        return

    @property
    def sql_upload_allowed(self):
        return self.__sql_upload_allowed

    # --------------------------------------------------------------------------------------------------------
    # Переобозначим функции ----------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Получить ссылку на объект графа
    def get_element(self, el_id: int,
                    try_to_upload: bool = None) -> GraphElement or None:
        '''
        Функция выдаёт ссылку на объект класса GraphElement с индексом el_id.
        :param el_id: индекс объекта
        :param try_to_upload: попробовать ли подгрузить элемент из таблицы?
        :return: GraphElement или None
        '''

        try:  # Пробуем сразу отдать элемент
            return self.__Graph_elements_dict_link[el_id]
        except BaseException:  # Если не удалось получить ссылку
            if try_to_upload is None:  # Если настройка дефолтная
                try_to_upload = self.__sql_upload_allowed  # Берём по дефолту

            if try_to_upload:  # Если подгрузка разрешена
                result = self.upload_element(el_id=el_id)  # Пробуем подгрузить объект
                return result  # Вернём или ссылку на объект, или None

            else:  # Если подгрузка не разрешена
                self.__to_log(message=f'get_element: Запрошен отсутствующий элемент {el_id}',
                              log_type='ERROR')
                return None  # Вернём None

    # --------------------------------------------------------------------------------------------------------
    # Работа с базой -----------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Подгрузить конкретный элемент
    def upload_element(self, el_id: int,
                       add_to_graph: bool = True) -> GraphElement or None:
        '''
        Функция подгружает элемент с указанным id из SQL таблицы. Если add_to_graph == True, то prepared = False.
        :param el_id: индекс элемента, который мы попытаемся подгрузить
        :param add_to_graph: добавить объект в граф?
        :return: ссылка на объект или None, если подгрузка не удалась.
        '''

        # функция создаёт объект
        # и запрашивает метод объекта - подгрузка
        # если подгрузка выполнена, то ставится self.prepared = False  #!!!

        if not self.sql_upload_allowed:  # Если подгрузка запрещена
            return None

        else:  # Если подгрузка разрешена
            return None

    '''
    !!! Вынести в sql_loader объект работу по подгрузке.
        подгружать его в __init__, если дана такая команда (sql_upload_allowed = True).
        и тут юзать его.
    
    
    
    Короче - нам ещё нужна подгрузка какая-нить для "подгрузить всё, чё надо".
    И подгрузка с сужением. Типа - подгрузить на N колен.
    
    
            Добавить две функции
            upload missing (steps: int = 0, relations: str = 'all', doubles: bool = False)
            итераций загрузки
            тип связей
            выгружать ли дубли


            '''

    '''
    1. Подгрузить конкретный элемент
    2. подгрузить граф "вниз" для элемента
    3. подгрузить граф "вверх" для элемента

    !! Подгруженные объекты получают параметр "uploaded_from_sql"=True. У прочих того объекта нет.
    '''

    # --------------------------------------------------------------------------------------------------------
    # Сужение графа ------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    def narrow_down(self):
        '''
        Функция сбрасывает связи графа, ведущие к элементам, которых в графе нет.
        :return: ничего
        '''
        have_ids = set(self.get_elements_ids())  # Получим список id элементов и сделаем set, чтобы в функции не гонять
        for element_id in have_ids:  # Пошли по набору элементов
            # Передадим элементу команду на сужение - оставить только элементы из have_ids
            self.get_element(el_id=element_id, try_to_upload=False).narrow_down(ids_list_or_set=have_ids, keep=True)
            # результат ВСЕГДА будет удачным, т.к. self.get_element никогда не выдаст None тут
        return   # закончим

    # --------------------------------------------------------------------------------------------------------
    # Получение данных о наборе ------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Функция выдаёт "список голов" графа
    def get_heads(self, processed: bool = True) -> list:
        '''
        Функция собирает индексы фраз графа, которые не имеют родителей.
        :param processed: собирать только готовые фразы? True - да, False - все.
        :return: список "голов" графа. То есть - элементов, у которых нет родителей.
        '''
        heads_list = []  # список "голов"

        for el_id in self.get_elements_ids():  # Обойдём элементы
            Graph_element = self.get_element(el_id)  # Берём ссылку для краткости
            if GraphElement is None:  # Если элемента нет
                self.__to_log(message=f'get_heads: Ошибка обработки элемента {el_id}. Элемент отсутсвует в графе',
                              log_type='ERROR')
                continue
            if processed:  # Если собирать только обработанные фразы
                if Graph_element.need_to_process:  # Если фраза требует обработки
                    continue  # Скипаем её
            if Graph_element.nearest_parents == [] and not Graph_element.duplicate:
                # Если список родителей пуст и это НЕ дублёр
                heads_list.append(el_id)  # Добавим индекс в список голов

        return heads_list

    # получить словарь необработанных элементах
    def get_not_processed(self) -> dict:
        '''
        Функция отдаёт словарь вида {len: ids_list}, в списках которого находятся индексы необработанных элементов,
        чей набор токенов имеет длину len.
        :return: словарь формата {len: ids_list}, где len - количество токенов, а ids_list - список непроработанных
            элементов, имеющих длину списка токенов len.
        '''

        process_dict = {}  # Словарь списков элементов, требующих обработки. {len: ids_list}
        for el_id in self.get_elements_ids():  # Обойдём элементы
            Graph_element = self.get_element(el_id=el_id)  # Берём ссылку для краткости
            if GraphElement is None:
                self.__to_log(message=f'get_not_processed:  Ошибка обработки элемента {el_id}. Элемент отсутсвует в графе',
                              log_type='ERROR')
                continue

            # Заполним индексами словарь process_dict
            if Graph_element.need_to_process:  # Если требуется проработка
                # проверим, есть ли в process_dict нужная длина
                try:
                    process_dict[Graph_element.tokens_amount].append(el_id)  # Пробуем пополнить
                except KeyError:  # Если списка с id нужной длины нет
                    process_dict[Graph_element.tokens_amount] = [el_id]  # Создадим список
        return process_dict

    # --------------------------------------------------------------------------------------------------------
    # Групповые манипуляции ----------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # Обозначим отработанным элементам need_to_process=False
    def mark_as_done(self, processed_list: list):
        '''
        Функция отметит все элементы из списков словаря process_dict как "не нуждающиеся в обработке"
        :param processed_list: список отработанных индексов
        :return: ничего
        '''
        # Обозначим отработанным элементам need_to_process=False
        for new_element_id in processed_list:  # Пошли по новым элементам длины elements_len
            NewGraphElement = self.get_element(el_id=new_element_id)  # Пробуем получить элемент
            if NewGraphElement is None:  # Если элемента нет
                self.__to_log(message=f'mark_as_done: Ошибка обработки элемента {new_element_id}. Элемент отсутсвует в графе',
                              log_type='ERROR')
                continue  # Скипаем
            # Если всё ок
            NewGraphElement.need_to_process = False  # Установим, что элемент более не требует обработки

        return

    # Функция "сужения" графа
    def clear_missed_connections(self):
        '''
        Задача функции: обойти элементы графа и дропнуть из их списков индексы элементов, которых нет текущем в наборе.
        Смысл - не получать ошибки в работе из-за того, что в наборе элементов есть ссылки на отсутствующие графовые
        элементы.
        :return:
        '''
        self.__to_log(message='clear_missed_connections: Начато выполнение сужения графа',
                      log_type='INFO')

        in_graph_ids = self.get_elements_ids()  # Получим список id элементов
        ids_string = ' '
        for el_id in in_graph_ids:  # Пошли по списку
            ids_string += str(el_id) + ' '  # Соберём строку с имеющимися id

        graph_narrowed = self.narrowed  # Детектор того, что граф был сужен
        # берём старое значение, т.к. оно может быть true)

        for el_id in in_graph_ids:  # Пошли обойдём граф
            GraphEl = self.get_element(el_id=el_id)  # Возьмём ссылку для удобства

            if GraphEl is None:  # Если не смогли получить
                self.__to_log(message=f'clear_missed_connections: Ошибка обработки элемента {el_id}. Элемент отсутсвует в графе',
                              log_type='ERROR')
                continue
            if GraphEl.duplicate:  # Если элемент дубль
                continue  # тоже скипаем

            narrowed = False  # Детектор сужения набора
            # Обойдём списки элементов графа
            for parent_id in GraphEl.nearest_parents:
                if not (' ' + str(parent_id) + ' ') in ids_string:  # Проверим, есть ли индекс
                    # Если какого-то элемента нет
                    GraphEl.del_from(element_id=parent_id, relation='parent')  # Дропаем
                    narrowed = True  # Отметим, что сужение было
            for child_id in GraphEl.nearest_children:  # Пошли по детям
                if not (' ' + str(child_id) + ' ') in ids_string:  # Проверим, есть ли индекс
                    # Если какого-то элемента нет
                    GraphEl.del_from(element_id=child_id, relation='child')  # Дропаем
                    narrowed = True  # Отметим, что сужение было
            for double_id in GraphEl.doubles:
                if not (' ' + str(double_id) + ' ') in ids_string:  # Проверим, есть ли индекс
                    # Если какого-то элемента нет
                    GraphEl.del_from(element_id=double_id, relation='double')  # Дропаем
                    narrowed = True  # Отметим, что сужение было
            if narrowed:  # Если было сужение
                graph_narrowed = True  # Задатектим, что граф сужен

        self.narrowed = graph_narrowed  # Установим значение в селф
        self.__to_log(message=f'clear_missed_connections: Сужение графа выполнено, детектор сужения {graph_narrowed}',
                      log_type='INFO')
        return

    # --------------------------------------------------------------------------------------------------------
    # Функция построения -------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------
    # обработать все необработанные элементы
    def upbuild(self) -> bool:
        '''
        Функция включает в граф элементы, которые в него ещё не включены. То есть - образует связи для элементов
        с параметром need_to_process=True.
        Комментарий: у фраз параметр "need_to_process" будет меняться только после полного обхода графа. Таким образом
            во время построения случай, когда need_to_process=False приравниевается к необходимости разворота рассчёта.
        :return: статус успешности. True - без ошибок, False - с ошибками.
        '''

        self.__to_log(message=f'upbuild: Начато включение новых элементов в граф.',
                      log_type='INFO')

        if self.prepared:  # Если граф уже готов
            self.__to_log(message='upbuild: Нет элементов, требующих включения',
                          log_type='INFO')
            return True  # Успешно, выйдем

        process_dict = self.get_not_processed()  # Словарь списков элементов, требующих обработки. {len: ids_list}
        sorted_by_len = list(set(process_dict.keys()))  # Сделаем отсортированный список ключей process_dict
        total_count = 0
        for new_elements_len in process_dict.keys():  # Пошли по длинам
            total_count += len(process_dict[new_elements_len])  # Просуммируем общее количество обработанных запросов
        self.__to_log(message=(f'upbuild: Количество элементов, требующих включения в граф {total_count}.' +
                               f' Всего объектов в графе {len(self.get_elements_ids())}'),
                      log_type='INFO')

        failed_elements_ids = []  # Список элементов, для которых обработка упала
        heads_list = self.get_heads(processed=True)  # список "голов". Только включённых в граф

        for new_elements_len in sorted_by_len:  # Пошли по длине от меньшей к большей
            # такова спицифика включения в граф

            elements_list = process_dict[new_elements_len]  # Возьмём ссылку на список элементов
            for new_element_id in elements_list:  # Пошли по новым элементам из списка elements_list

                new_element = self.get_element(el_id=new_element_id)  # Получим элемент, который надо добавить
                if new_element is None:  # Если элемент не получен
                    self.__to_log(message=(f'upbuild: Включение элемента {new_element_id} в граф провалено. ' +
                                           'Элемент не удалось получить в качетсве объекта графа'),
                                  log_type='ERROR')
                    continue  # Скипаем

                try:  # Пробуем выполнить включение
                    process_result = self.include_element(new_element=new_element.element_id,
                                                          heads_ids_list=heads_list,
                                                          mark_as_included=False)
                    if process_result:  # Если выполнение успешно
                        if new_element.nearest_parents == [] and not new_element.duplicate:
                            # Если список родителей пуст после обработки и элемент не стал дублёром
                            heads_list.append(new_element.element_id)  # Добавим элемент в список голов
                    else:
                        self.__to_log(message=(f'upbuild: Включение элемента {new_element_id} в ' +
                                               f'граф провалено. Ошибка внутри include_element'),
                                      log_type='ERROR')
                        failed_elements_ids.append(new_element_id)  # Добавим индекс в список ошибок

                except BaseException as miss:
                    # Логируем
                    self.__to_log(message=(f'upbuild: Включение элемента {new_element_id} в ' +
                                           f'граф провалено. Ошибка запуска процесса: {miss}'),
                                  log_type='ERROR')
                    failed_elements_ids.append(new_element_id)  # Добавим индекс в список ошибок

                # Проверим элементы - головы, которые перестали быть таковыми
                for head_id in heads_list:
                    check_head_link = self.get_element(el_id=head_id)
                    if check_head_link.nearest_parents != [] or check_head_link.duplicate:
                        # если есть хоть один родитель или элемент стал дублёром
                        heads_list.remove(head_id)  # Дропаем родителя из списка

        # Обозначим отработанным элементам need_to_process=False (именно в самом конце)
        for new_elements_len in process_dict.keys():  # Пошли по длинам
            # Вычтем из списка "упавшие" элементы
            if failed_elements_ids != []:  # Если список ошибок не пуст
                update_list = list(set(process_dict[new_elements_len]) - set(failed_elements_ids))
            else:
                update_list = process_dict[new_elements_len]

            self.mark_as_done(
                processed_list=update_list)  # отправим список в коррецию только успешно обработанные

        # Сформируем "дополнительное сообщение"
        if failed_elements_ids == []:  # Если список ошибок не пуст
            add_message = f'выполнено без ошибок. Обработано {total_count} элементов'
            log_type = 'INFO'
            result = True  # Результат - без ошибок
        elif len(failed_elements_ids) < total_count:  # если есть ошибки, но упало не всё
            add_message = (f'выполнено с ошибками. Обработано {total_count} элементов,' +
                           f' получено {len(failed_elements_ids)} ошибок')
            log_type = 'WARNING'
            result = False  # Результат - с ошибками
        else:  # Если всё упало в ошибки
            add_message = f'провалено. Все {total_count} элементов обработаны с ошибкой'
            log_type = 'ERROR'
            result = False  # Результат - с ошибками

        # Закончим
        self.prepared = True  # Обозначим, что граф готов (даже если были ошибки)
        self.__to_log(message=('upbuild: Включение новых элементов в граф ' + add_message),
                      log_type=log_type)
        return result


    # функция включает в граф конкретный элемент
    def include_element(self, new_element: int,
                        heads_ids_list: list = None,
                        mark_as_included: bool = False) -> bool:
        '''
        Функция включает в граф объект new_element, то есть - образует нужные связи.
        :param new_element: новый элемент, который будет включён в граф. При этом важно, что объект, отвечающий
            этому элементу включается в граф ВНЕ этой функции.
        :param heads_ids_list: список элементов, которые будут считаться(!) головами. То есть, в ветви которых мы вошьём
                    new_element, или ветви которых мы пришьём к new_element.
                    Это оптимизационный параметр - чтобы не собирать список для каждого элемента графа,
                    так как это очень тяжёлая операция.
        :param mark_as_included: отметить ли новый элемент как обработанный. Имеет смысл, если мы кастомно вставляем один
            элемент, но такой сценарий скорее всего сигнализирует о неверном использовании этой функции.
            Прична в том, что для новых элементов не делается "разворот" на проверку детей, и это экономит время работы.
        :return: успешность выполнения (выполнено без ошибок)
        '''
        new_element = self.get_element(el_id=new_element)
        if new_element is None:  # Если элемент не получен
            self.__to_log(message=(f'include_element: При запросе встраивания элемента с id "{new_element}" ' +
                                   'получена ошибка - элемента нет в объектах графа. Работа с {new_element} закончена'),
                          log_type='ERROR')
            return False  # Выходим

        # запросим у графа головы
        if not isinstance(heads_ids_list, list):  # Если это не список
            heads_ids_list = self.get_heads(processed=True)  # Берём именно только(!) уже включённые в граф фразы

        # Включим новый элемент в граф
        try:  # Попробуем поработать

            for head_id in heads_ids_list:  # Пошли по "головам"
                # Проверка того, что элемент head_id есть будет тут, т.к. он явно потребуется в __include_to_branch
                parent_object = self.get_element(el_id=head_id)
                if parent_object is None:
                    self.__to_log(message=(f'include_element: При включении в граф элемента {new_element.element_id} ' +
                                           f'был запрошен головной элемент {head_id}, которого нет в объектах графа. ' +
                                           'Включение в ветвь элемента {head_id} пропущено'),
                                  log_type='ERROR')
                    continue  # Скипаем работу с parent_object

                add_result = self.__include_to_branch(parent_id=head_id, child_object=new_element,
                                                      go_deeper=True)
                if not add_result:  # Если new_element не нашёл родителя в ветви paren_object
                    # Проверим, не является ли new_element родителем какого-либо уровня для paren_object
                    self.__include_to_branch(parent_id=new_element.element_id, child_object=parent_object,
                                             go_deeper=False)
                    '''
                    go_deeper=False т.к. связь может быть образована в таком случае только между new_element и
                    paren_object, потому, что у new_element не может быть в детях элементов, которые ещё не находятся
                    в графе, т.к. он включается в граф и сравнивается только с элементами, которые уже в графе.
                    А у paren_object уже установлены ВСЕ возможные связи с элементами графа, т.к. при встраивании
                    paren_object в граф, он сравнивался со всеми уже встроенными элементами, а следующие после
                    paren_object элеенты сравниваются с ним при включении в граф.
                    При этом работать с "родителями" parent_object не надо, т.к. подразумевается, что или parent_object
                    это голова графа, или мы работаем ТОЛЬКО с ним и его ветвью, т.е. - его родители нас не интресуют.
                    
                    Ну и результат этой функции в данном(!) случае нас тоже не интересует.
                    '''

                else:  # Если же привязка в ветвь была
                    if new_element.duplicate:  # Если новый элемент стал чьим-то дублёром по ходу работы
                        return True  # Закончим работу с ним

            if mark_as_included:  # Если нужно отметить элемент как включённый в граф (НЕЖЕЛАТЕЛЬНО ДЕЛАТЬ ТУТ!)
                new_element.need_to_process = True  # Отметим

            return True

        except BaseException as miss:
            self.__to_log(message=(f'include_element: При включении в граф элемента {new_element.element_id} ' +
                                   f'получена ошибка: {miss}'),
                          log_type='ERROR')
            return False



    # Доп функции для построения -----------------------------------------------------------------------------
    '''
    Местами в функции вместо id передаётся ссылка на объект. Это делается для того, чтобы сэкономить время на
        запрашивании объектов из словаря.
    Кроме того, валидация может быть заменена на try - except по той же причине. Т.к. будет очень(!) много операций
    и сокращение времени рассчётов является весьма приоритетным.
    '''

    # Функция детектирует вхождение у двух списков
    @staticmethod
    def _lists_compare(parent_list: list, child_list: list) -> bool:
        '''
        Функция детектирует вхождение родительского списка в дочерний, кроме случая дублирования.
        :param parent_list: родительский список
        :param child_list: дочерний список
        :return: bool - входит ли родительский список целиком в дочерний
        '''

        if len(parent_list) >= len(child_list):  # Если длина родителя больше или равна - вхождения точно нет
            return False

        for parent_token in parent_list:  # Пошли по токенам родителя

            found = False  # Детектор того, найден ли токен родителя в дочерней фразе
            for child_token in child_list:  # Сравнивать будем с "потенциальным" ребёнком
                # Это наиболее быстрый вариант проверки
                if parent_token < child_token:  # Наиболее частый вариант - "пролёт" мимо (отсутствие совпадения)
                    # Если токен фразы родителя должен находиться левее текущего элемента дочерней фразы
                    # И мы дошли до такой ситуации. (мы идём слева на право, и на совпадении прерываем обход)
                    # Значит, что его вообще нет в текущей фразе.
                    break  # Закончим поиск слова

                elif parent_token > child_token:
                    # Если токен фразы родителя должен стоять правее текущего токена дочерней фразы
                    # (мы идём слева на право, и ещё не дошли до совпадения)
                    continue  # Перейдём вправо на один токен В ДОЧЕРНЕЙ ФРАЗЕ

                else:  # Если он не левее и не правее, значит, он равен.
                    # Если текущий токен фразы родителя вошёл в дочернюю фразу
                    # Значит, надо брать следующий токен фразы родителя для сравнения.
                    # Момент оптиимзации - скинем из списка "дочерней фразы" все токены до текущего включительно,
                    # Т.к. мы знаем, что следующий токен из фразы графа должен быть правее текущего
                    # ( если во фразе из графа будут два повторяющихся слова, то и в новой фраз их должно быть два)
                    # Обрежем токены в дочернем наборе слева от текущего
                    child_list = child_list[child_list.index(child_token) + 1:]
                    found = True  # Запомним, что слово совпало
                    break  # Закончили работу с элементом parent_word

            if not found:  # Если слово не найдено
                return False  # То вхождения точно нет

        # Еслит мы обошли все токены родительской фразы и не вышли в return, значит, они все содержатся в дочерней фразе
        return True

    # Функция сравнения двух элементов
    def _entry_detector(self, parent_object: GraphElement, child_object: GraphElement) -> bool or None:
        '''
        Функция для сравнения двух наборов токенов. Цель сравнение - выяснить, нужно ли образовать связь,
        если нужно, то какую.
        :param parent_id: ссылка на родительский элемент графа
        :param child_id: ссылка на "новый" или встраиваемый в граф элемент
        :return: result:
                    True - parent_id является родителем для child_id
                    False - parent_id не является родителем для child_id
                    None - child_id является дублёром для parent_id
        '''
        try:  # Сделаем через try, чтобы не делать валидацию
            if parent_object.element_id == child_object.element_id:  # Если совпал индекс
                return False  # Это дубль индекса

            if parent_object.tokens_list == child_object.tokens_list:  # Если списки токенов совпали
                return None  # Значит, это дубли
            else:  # Если не совпали
                # Задетектируем наличие связи
                compare_result = self._lists_compare(parent_list=parent_object.tokens_list,
                                                     child_list=child_object.tokens_list)
                return compare_result
        except BaseException as miss:  # Если была ошибка
            self.__to_log(message=(f'_entry_detector: Ошибка работы с элементами: parent_object={parent_object} и ' +
                                   f'child_object={child_object}. Результат уфнкции - False. Ошибка: {miss}'),
                          log_type='ERROR')
            return False  # Вернём отсутствие связи

    # Функция для "разворота" на детей элемента, в случае, если родитель был в графе
    def __turn_around(self, parent_object: GraphElement, new_object: GraphElement):
        '''
        Функция,которая врезает элемент new_object в дочерние связи между родителем paren_object и его детьми в случае,
        если кому-то из детей нужно заменить родителя paren_object на new_object.
        :param parent_object: родитель в графе. Точнее - ссылка на него.
        :param new_object: новый элемент графа
        :return: ничего
        '''
        try:  # Чтобы не делать валидацию.
            for pch_index in parent_object.nearest_children:
                pch_object = self.get_element(el_id=pch_index)
                if pch_object is None:
                    self.__to_log(message=(f'turn_around: При развороте на родителе {parent_object.element_id} ' +
                                           f'для нового элемента {new_object.element_id}' +
                                           f' у родителя был запрошен отсутствующий элемент {pch_index}'),
                                  log_type='ERROR')
                    continue  # Скипаем тогда

                else:  # Если объект получен
                    # Проверим, будет ли вхождение нового элемента в pch_object
                    compare_result = self._entry_detector(parent_object=new_object, child_object=pch_object)
                    # Результата None быть не может, так как в таком случае было бы установлено дублирование в include_to_branch
                    if compare_result:  # Если new_object - родитель для pch_object
                        # Удалим у parent_object элемент pch_object из детей
                        parent_object.del_from(element_id=pch_index, relation='child')  # удаляем связь у родителя
                        # Заменим у pch_object родителя parent_object на new_object
                        pch_object.replace(old_value=parent_object.element_id,
                                           new_value=new_object.element_id, relation='parent')
                        new_object.add_to(element_id=pch_index,
                                          relation='child')  # Добавим pch_object в дети new_object
            return  # Закончим

        except BaseException as miss:
            self.__to_log(message=(f'_entry_detector: Ошибка работы с элементами: parent_object={parent_object} и ' +
                                   f'new_object={new_object}. Ошибка: {miss}'),
                          log_type='ERROR')
            return

    # Функция для включения нового элемента в ветвь
    def __include_to_branch(self, parent_id: int, child_object: GraphElement,
                            go_deeper: bool = True) -> bool:
        '''
        Функция встраивает элемент Child в ветвь родителя parent_id.
        :param parent_id: индекс элемента - потенциального родителя в графе.
        :param child_object: GraphElement - объект(!) графа, являющийся "новым" или встраиваемым
        :param go_deeper: пойти ли "вглубь"? . Если да, то проработка провалится в ветку
        :return: bool добавлена ли связь в этой функции или на уровнях ниже. Если родитель "не получен",
                 то результат будет False.
        '''

        status = False  # Для непредвиденных условий образования связи
        parent_object = self.get_element(el_id=parent_id)
        if parent_object is None:  # Если родительский объект не получен
            self.__to_log(message=(f'__include_to_branch: При запросе в графе элемента ' +
                                   f'parent_object по "{parent_id}" получена ошибка - ' +
                                   'элемента нет в объектах графа. Работа с parent_id={parent_id} пропущена'),
                          log_type='ERROR')
            return status  # Результат False

        try:
            # Проверим наличие связи
            compare_result = self._entry_detector(parent_object=parent_object, child_object=child_object)
            if compare_result is None:  # Если child_object есть дубль parent_object
                # скормим через поглощение child_object элементу parent_object
                self.absorption(eater_id=parent_object.element_id, feeder_id=child_object.element_id)
                status = True  # Пометим, что связь была установлена

            elif compare_result is True:  # Если вхождение было
                # Пройдём по детям элемента parent_object
                child_binding = False  # Детектор того, что child_object был привязан к дочернему для parent_object эл-ту
                if go_deeper:  # Если проработка проваливается вглубь
                    for child_el in parent_object.nearest_children:  # Пошли по детям родителя
                        # Проверим, не является ли кто-то из детей parent_object родителем для child_object
                        child_check = self.__include_to_branch(parent_id=child_el,
                                                               child_object=child_object,
                                                               go_deeper=go_deeper)
                        if child_check:  # Если где-то в потомках связь была установлена
                            child_binding = True  # Запомним на детекторе
                # Выполним соответсвующее действие
                if child_binding:  # Если связь была установлена в детях
                    status = True  # Пометим, что связь была установлена у потомков
                    # и ничего не делаем
                else:  # Если связь не была установлена в детях. То есть - она должна быть установлена тут
                    # Установим связь между родителем и ребёнокм
                    self.add_parental_edge(parent_id=parent_object.element_id, child_id=child_object.element_id)
                    if not parent_object.need_to_process:  # Если родитель уже был включён в граф ранее (не в этом запуске)
                        # запустим проверку врезания child_object в дочерние связи parent_object
                        self.__turn_around(parent_object=parent_object, new_object=child_object)

                    status = True  # Пометим, что связь была установлена в текущем элемента
            # Если вхождения не было
            elif compare_result is False:
                status = False  # Пометим, что связь НЕ была установлена

            # если результат не опознан
            else:
                status = False  # Отметим, что связи нет
                self.__to_log(message=(f'include_to_branch: для родителя {parent_object.element_id}' +
                                        f' и ребёнка {child_object.element_id} не установлен тип связи. ' +
                                        'Указано, что связи нет.'),
                              log_type='ERROR')

        except BaseException as miss:
            status = False  # Отметим, что связи нет
            self.__to_log(message=(f'include_to_branch: для родителя {parent_object.element_id}' +
                                    f' и ребёнка {child_object.element_id} получена ошибка при работе: {miss}.' +
                                    ' Указано, что связи нет.'),
                          log_type='ERROR')

        return status

