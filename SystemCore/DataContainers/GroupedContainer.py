'''
Это расширение обычного контейнера на "секционный", который будет использоваться в случаях, где необходим быстрый
доступ к срезу элементов.
'''

import copy

from SystemCore.DataContainers.SimpleContainer import SimpleContainer


class GroupedContainer(SimpleContainer):


    pass




# ------------------------------------------------------------------------------------------------
# Контейнер со срезами ---------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class SectionalContainer(SimpleContainer):
    '''
    Класс - надостройка над MainContainer, в который добавлен "быстрый доступ".
    А именно - внутри класса есть словарь с наборами, в который можно добавлять те или иные объекты. Смысл в том,
    чтобы не обходить все объекты, при необходимости запрсоа какой-либо группы. Важно, что объекты НЕ МОГУТ менять свою
    группу. То есть - классификация статична. Например - классификация по региону парсинга данных или дате парсинга,
    эти свойства не могут измениться по ходу работы. Поэтому, кстати, нет удаления элемента из кластера (кроме как
    при его удалении из набора).
    Наборы хранятся в виде сетов в двухуровневом словаре: {parameter_name: {parameter_value: set()}}
        Property (без setter):
            grouping_parameters - получить список или кортеж параметров, использующихся для группировки. Значения - строки.

        Быстрый доступ:
            get_parameter_values - получить значения параметра, которые используются в кластеризации

            add_to_fast_access_cluster - добавить объект в списки быстрого доступа

            del_fast_access_cluster - удалить список быстрого доступа для значения параметра.

            get_fast_access_cluster - поулчить пересечение указанных списков быстрого доступа

    '''
    def __init__(self, objects_type: object,
                 identification_object: object,
                 grouping_parameters: list or tuple = None,
                 launch_module_name: str = None, process_manager: ProcessesManager = None,
                 holder_name:  str or int or float = None):
        '''
        :param objects_type: тип объектов, которые будут находитсья в контейнере
        :param identification_object: "опознавательный объект". Это может быть id, строка, словарь, контейнер и прочее.
        :param grouping_parameters: Список параметров, которые будут использованы при группировки для быстрого доступа.
            у объекта ОБЯЗАНЫ быть указаны все параметры группировки. В противном случае он отработает неверно.
            Указывать параметры стоит в формате str. Это связано с логикой работы контейнера (**kwargs).
            Список хранит порядок, который будет использоваться в словаре.
            Если параметр не указан - лучше поставить None.
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер процесса, который руководит запуском
        :param holder_name: имя "владельца контейнера" - для логирования. Нужно для того, чтобы не создавать каждому
            контейнеру логер в process_manager-е, а использовать "один на всех".
        '''

        SimpleContainer.__init__(self=self,
                               objects_type=objects_type,
                               identification_object=identification_object)

        self.__set_log_func(launch_module_name=launch_module_name, process_manager=process_manager,
                            holder_name=holder_name)

        # Создадим объекты для быстрого доступа
        if grouping_parameters is None:  # Если параметры не заданы
            self.__grouping_parameters = ()  # tuple с параметрами пуст
        else:
            self.__grouping_parameters = tuple(grouping_parameters)  # tuple с параметрами группировки
        self.__fast_access = {}  # словарь с сетами быстрого доступа
        '''
        При добавлении объекта, он может быть сопровождён набором параметров из шаблона в том порядке, в котором
        они указаны в шаблоне. Параметры должны быть простыми: int, float, str. Не стоит использовать сложные или
        длинные варианты.
        Словарь self.__fast_access имеет вид: {parameter_name: {parameter_value: set()}}
        Не стоит использовать для срезов параметры, которые принимают широкий спектр значений.
        Многопараметрические срезы будут делаться через пересечения сетов.
        '''

    def __set_log_func(self, launch_module_name: str or None, process_manager: ProcessesManager or None,
                       holder_name: str or int or float or None):
        '''
        Функция создаёт функцию логирования и ставит её в self.__to_log. Если process_manager не передан, то будет
        использована "заглушка". Дополнительно будет создано "имя владельнца": self.__holder_name.

        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер процесса, который руководит запуском
        :param holder_name: имя "владельца контейнера" - для логирования.
        :return: ничего
        '''
        if holder_name is None:  # Если не задано имя владельца
            self.__holder_name = '(контейнер {holder_name})'  # добавка от имени пуста
        else:  # если задано
            self.__holder_name = str(holder_name)

        def stub(**kwargs):  # заглушка
            return
        if process_manager is None:  # Если менеджера нет
            self.__to_log = stub  # ставим заглушку
            return  # выходим
        else:  # Если  задан менеджер
            # Делаем логер
            self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                             launch_module_name=launch_module_name)
            self.__Logger = process_manager.create_logger(module_name=self.__my_name,
                                                          log_initialization=True)
            self.__to_log = self.__Logger.to_log
        return

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def grouping_parameters(self) -> tuple:
        '''
        Функция отдаёт копию кортежа параметров. Будет пуст "()", если при создании контейнера grouping_parameters
        был None (или не задан)

        :return: неглубокая копия для защиты от изменения.
        '''
        return copy.copy(self.__grouping_parameters)

    # ------------------------------------------------------------------------------------------------
    # Менеджмент данных ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def del_object(self, index: str or int or float) -> bool:
        '''
        Функция пытается удалить объект из контейнера и из get_fast_access_cluster

        :param index: индекс элемента, который мы удалим
        :return: True - объект был и он удалён, False - объекта не было.
        '''
        try:
            self.__objects_dict.pop(index)
            #  Если всё ок, теперь попробуем удалить объект из сетов get_fast_access_cluster
            for parameter in self.__fast_access.keys():  # Пошли по параметрам
                for value in self.__fast_access[parameter]:  # Пошли по значениям
                    try:
                        self.__fast_access[parameter][value].remove(index)  # пытаемся дропнуть из сета
                    except BaseException:  # если его нет
                        pass  # чилим
            return True  # Если объект был и успешно удалён
        except KeyError:
            return False  # Если объекта с таким индексом не было

    # ------------------------------------------------------------------------------------------------
    # Быстрый доступ ---------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_parameter_values(self, parameter: str) -> list or None:
        '''
        Функция проходит словарь self.__fast_access, проверяя для parameter значения, которые используются при
        кластеризации. Смысл в том, чтобы иметь возможность не только получить список параметров, но и значения
        для каждого из них.

        :param parameter: параметр из __grouping_parameters
        :return: список значений или None, если параметра нет в __grouping_parameters. Сортировка не делается.
                Список может быть пуст.
        '''
        if not parameter in self.__grouping_parameters:  # если нет в параметрах
            self.__to_log(message=f'{self.__holder_name} get_parameter_values: запрошен неразрешённый параметр: {parameter}',
                          log_type='ERROR')
            return None  # Вернём ошибку

        values_list = list(self.__fast_access[parameter].keys())  # Берём список значений параметра
        return values_list

    def add_to_fast_access_cluster(self, object_id: object,
                                   **kwargs) -> bool or None:
        '''
        Функция добавляет объект в словарь быстрого доступа. При условии, что сам объект уже добавлен в контейнер.
        Функция добавит object_id во все сеты пар kwargs вида (key: value).

        :param object_id: индекс объекта из контейнера.
        :param kwargs: значения параметров из кортежа  self.__grouping_parameters. Можно дать любой набор.
        :return: True - если всё ок. False - если была ошибка при добавлении id в один/несколько/все сеты при add.
            None - если была ошибка типа: есть неразрешённые параметры; нет индекса элемента.
        '''

        # Проверим id
        if not self.check_access(index=object_id):  # Если нет id
            self.__to_log(message=f'{self.__holder_name} add_to_fast_access_cluster: в наборе нет элемента с указанным индексом: {object_id}',
                          log_type='ERROR')
            return None  # Вернём ошибку

        for dict_key in kwargs.keys():
            if not dict_key in self.__grouping_parameters:  # Если такого параметра нет
                self.__to_log(message=f'{self.__holder_name} add_to_fast_access_cluster: в grouping_parameters отсутствует dict_key: {dict_key}',
                              log_type='ERROR')
                return None  # Вернём ошибку

        # Если всё ок, то добавим object_id во все спикси пар
        good_deal = True  # детектор "всё путём"
        for dict_key in kwargs.keys():
            try:
                # Пробуем добавить в сет со значением для параметра dict_key равным kwargs[dict_key]
                self.__fast_access[dict_key][kwargs[dict_key]].add(object_id)  # пробуем пополнить сет
            except KeyError:  # Если сета нет
                self.__fast_access[dict_key][kwargs[dict_key]] = set([object_id])  # Сделаем его

            except BaseException as miss:  # Иначе
                self.__to_log(message=(f'{self.__holder_name} add_to_fast_access_cluster: при добавлении элемента "{object_id}"' +
                                       f' произошла ошибка: {miss}'),
                              log_type='ERROR')

                good_deal = False  # всё не путём

        return good_deal  # вернули детектор

    def del_fast_access_cluster(self, **kwargs) -> bool or None:
        '''
        Функция удаляет весь сет для значения "kwargs[dict_key]" параметра "dict_key". Например - удалить
        весь сет для даты 01.01.2020 . Если надо удалить несколько сетов одного параметра (несколько дат),
        потребуется столько запусков, сколько сетов/значений нужно удалить.

        :param kwargs: значения параметров из списка self.__grouping_parameters, кластеры (сеты) которых
            будут удалены.
        :return: True - если всё ок. False - если была ошибка при удалении одиного/нескольких/всех списков-кластеров.
            None - если была ошибка типа: есть неразрешённые параметры.
        '''

        for dict_key in kwargs.keys():
            if not dict_key in self.__grouping_parameters:  # Если такого параметра нет
                self.__to_log(message=f'{self.__holder_name} del_fast_access_cluster: в grouping_parameters отсутствует dict_key: {dict_key}',
                              log_type='ERROR')
                return None  # Вернём ошибку

        # Если всё ок, то пошли удалять списки
        good_deal = True  # детектор "всё путём"
        for dict_key in kwargs.keys():
            try:
                self.__fast_access[dict_key].pop(kwargs[dict_key])  # Пробуем дропнуть сет из словаря параметра dict_key
            except KeyError:  # Если сета нет
                good_deal = False

        return good_deal  # вернули детектор

    def get_fast_access_cluster(self, substitute: bool = True,
                                **kwargs) -> list or None:
        '''
        Функция берёт срез по указанным параметрам. Если полученные во время среза id не будут найдены в наборе,
        что исключается механизмом добавления/удаления элементов в fast_set, то залогируется ERROR, а элемент будет
        пропущен в экспортном списке.

        :param substitute: заменить ли при экспорте id элементов на ссылки на их объекты из контейнера?
        :param kwargs: значения параметров из списка self.__grouping_parameters. Можно дать любой набор.
            если для какого-либо значения сет отсуттсвует, то мы получим в лог WARNING и сразу выйдём в return.
        :return: True - если всё ок. False - если была ошибка при добавлении id в один/несколько/все списки при append.
            None - если была ошибка типа: есть неразрешённые параметры; нет индекса элемента.
        '''
        for dict_key in kwargs.keys():
            if not dict_key in self.__grouping_parameters:  # Если такого параметра нет
                self.__to_log(
                    message=f'{self.__holder_name} get_fast_access_cluster: в grouping_parameters отсутствует dict_key: {dict_key}',
                    log_type='ERROR')
                return None  # Вернём ошибку

        # Если всё ок, то вытащим списки в виде сетов
        for dict_key in kwargs.keys():
            try:
                kwargs[dict_key] = self.__fast_access[dict_key][kwargs[dict_key]]  # получим сет
            except KeyError:  # Если сета нет
                self.__to_log(message=(f'{self.__holder_name} get_fast_access_cluster: для пары ({dict_key}, {kwargs[dict_key]})' +
                                       f' нет списка значений для среза'),
                              log_type='WARNING')
                return []  # срез точно пуст

        # пересечём их
        keys_list = list(kwargs.keys())
        result_set = kwargs[keys_list[0]]  # Берём нулевой сет
        keys_list = keys_list[1:]  # Дропнем нулевой id для удобства
        for dict_key in keys_list:  # Пошли по ключам
            result_set = result_set & kwargs[dict_key]  # поулчим пересечение
            if len(result_set) == 0:  # Если сет пуст
                break  # кончаем

        if substitute:  # Если надо элементы
            result_set = list(result_set)
            for j in range(0, len(result_set)):  # пошил по списку
                element = self.get_object(index=result_set[j])
                if element is None:
                    self.__to_log(message=(f'{self.__holder_name} get_fast_access_cluster: для индекса "{result_set[j]}" ' +
                                           f'в контейнере нет элемента'),
                                  log_type='ERROR')
                else:  # Если элемент есть
                    result_set[j] = element  # чекаем его в список

            return result_set  # Вернём список

        else:  # Если можно id
            return list(result_set)  # вернём список id

    # Добавить "сменить значение параметра"