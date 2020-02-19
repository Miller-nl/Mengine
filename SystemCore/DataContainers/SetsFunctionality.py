'''
Тут располагаются контейнеры для работы с наборами данных. Контейнеры имеют форматный вид и должны сократить количество
кода в описании семантических ядер, фраз, страниц, доменов и прочих объектов, которые имеют в себе наборы данных.
Используются два основных объекта:
ContainerIdentificationKey - идентификационный ключ набора, который содержит данные для опознания сета.
    Ключ может быть дополнен какими либо свойствами, но не методами.

# --------------------------------------------------------------------------------------------------------
# Контейнер ContainerIdentificationKey -------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Идентификационный ключ набора. Нужен для удобства логирования и хранения идентификационных данных набора.

Параметры init:
     name - имя контейнера
     data_description - словесное описание данных. Будет использоваться в логировании.
     date - явно переданная дата в виде datetime.date . Можно создать объект через
        datetime.date(year, month, day), передав нужные данные. Если указать True, то в self будет установллне
        datetime.date.today(). Подразумевается использование для занесения данных о частотах и SERP в базу SQL

Доступные свойства без setter-а:
    name - имя контейнера
    description - описание контейнера
    date - дата в виде datetime.date
    parameters - копия словаря с параметрами.

Доступные методы:
     def add_parameter(name: str, value: object, replace: bool = True) -> bool - Функция добавляет параметр в self.
        :param name: имя параметра
        :param value:  значение параметра
        :param replace: заменить ли параметр, если он уже был
        :return: True, если индекс name был свободным, False, если был занят

    def get_parameter(name: str, no_value: object = None) -> object - Функция пытается выдать параметр из словаря с параметрами.
        :param name: имя параметра
        :param no_value: значение, которое будет выдано в случае отсутствия параметра.
        :return: значение параметра


self параметры:
    __name - имя набора
    __description - описание набора
    __date - дата, связанная с набором
    __parameters_dict - словарь с параметрами

# --------------------------------------------------------------------------------------------------------
# Контейнер SetContainer ---------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Контейнер для хранения внутри себя набора однотипных данных. Основная задача - упразнение стандартных функций типа
get/set/delete в объектах, производящях операции с данными.
Контейнер может устанавливать конкретные id объектам  при их добавлении, а может нумеровать их самостоятельно.

Параметры init:
    launch_module_name - имя вызывающего модуля (объекта, содержащего контейнер)
    process_manager - менеджер процесса, который руководит запуском.
    objects_type - тип данных объектов. Именно по нему будут создаваться объекты в create.
    identification_key - идентификационный ключ контейнера с данными.

Доступные свойства без setter-а:
    identification_key - идентификационный ключ набора
    objects_dict - неглубокая копия словаря с объектами (для защиты словаря от изменения)
    dict_keys - ключи словаря
    max_key - максимальный "целый" ключ, присутствующий в словаре. Он используется для генерации индекса новых
        элементов. Но тогда все индексы должны быть целыми, это важно.


Доступные методы:
    check_access(index: object) -> bool - Првоерка наличия объекта на индексе
        :param index: индекс/имя в наборе
        :return: статус

    get_object(index: object, no_value: object = None) -> object or None - Функция возвращает объект или None
        :param index: индекс/имя в наборе
        :param no_value: что вернуть если объекта нет?
        :return: объект или None, если объекта нет

    add_object(data_object: object, replace: bool = True,
               index_name: str or int or float = 'default') -> bool or int or None -  Функция принимает объект типа,
        указанного в __init__ (objects_type)
        :param data_object: объект, который надо поместить в контейнер. Тип объекта self.__objects_type
        :param replace: заменить если индекс занят?
        :param index_name: индекс словаря, на который будет добавлен объект. По умолчанию это __max_key + 1
        :return: Если индекс указан явно: был ли свободен индекс? True - свободен, False - был занят.
                 Если индекс поставлен 'default' - вернёт индекс
                 В случае ошибки - None

    create_object - функции нет из за ошибки передачи аргументов. Так что передавать можно только готовые объекты.

    del_object( index_name: str or int or float) -> bool - Функция пытается удалить объект
        :param index_name: индекс элемента, который мы удалим
        :return: True - объект был и он удалён, False - объекта не было


self параметры:
    __Logger - логер
    __to_log - фукнция логирования
    __identification_key - идентификационный ключ
    __objects_type - тип объектов, хранящихся в контейнере
    __objects_dict - словарь с объектами
    __max_key - "максимальный целый ключ"
'''


import copy
import datetime

from Managers.ProcessesManager import ProcessesManager

# ------------------------------------------------------------------------------------------------
# Идентификационный ключ контейнера --------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class ContainerIdentificationKey:
    '''
    "Опознавательный ключ" контейнера. Чтобы стандартизировать работу с наборами.
    Для удобства есть словарь с "параметрами", в который можно добавлять любые кастомные данные.
    '''

    def __init__(self, name: str or int,
                 data_description: str = None,
                 date: datetime.date = None):
        '''
        :param name: имя контейнера
        :param data_description: словесное описание данных.
        :param date: явно переданная дата в виде datetime.date . Можно создать объект через
            datetime.date(year, month, day), передав нужные данные. Если указать True, то в self будет установллне
             datetime.date.today().
        '''

        self.__name = name  # Установим имя
        self.__description = data_description  # установим тип

        if isinstance(date, datetime.date):
            self.__date = date
        elif date is True:  # Если указано "взять сегодня"
            self.__date = datetime.date.today()
        else:  # Если там None или что то ещё
            self.__date = None


        self.__parameters_dict = {}  # словарь с доп параметрами. Про запас

    # ------------------------------------------------------------------------------------------------
    # Закроем данные через property ------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def name(self) -> str or int:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def date(self) -> None or datetime.date:
        return self.__date

    @property  # выдаёт КОПИЮ словаря
    def parameters(self) -> dict:
        return copy.deepcopy(self.__parameters_dict)

    # ------------------------------------------------------------------------------------------------
    # Работа с параметрами ---------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_parameter(self, name: str,
                      value: object,
                      replace: bool = True) -> bool:
        '''
        Функция добавляет параметр в self.
        :param name: имя параметра
        :param value:  значение параметра
        :param replace: заменить ли параметр, если он уже был
        :return: True, если индекс name был свободным, False, если был занят
        '''
        try:
            a = self.__parameters_dict[name]
            result = True
        except KeyError:  # Если значения нет
            result = False

        if (not result) or replace:  # Если значения нет или разрешена замена
            self.__parameters_dict[name] = value  # Установим значение
        return result

    def get_parameter(self, name: str,
                      no_value: object = None) -> object:
        '''
        Функция пытается выдать параметр из словаря с параметрами.
        :param name: имя параметра
        :param no_value: значение, которое будет выдано в случае отсутствия параметра.
        :return:
        '''
        try:
            return self.__parameters_dict[name]
        except KeyError:
            return no_value


# ------------------------------------------------------------------------------------------------
# Непосредственно контейнер ----------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class SetContainer:
    '''
    Смысл контейнера - хранение наборов одинаковых однородных данных. Например: набор объектов графа, набор SERP
    объектов, наборов со статистикой директа, наборов запросов и прочее и прочее.

    Не рекомендуется использовать функцию create, лучше передовать созданные во вне объекты, т.к. функция create
    просто через try попробует создать объект с поданными параметрами. Что, в принципе, можно сделать и вне неёё.
    '''

    def __init__(self,
                 objects_type: object,
                 process_manager: ProcessesManager, launch_module_name: str = None,
                 identification_key: ContainerIdentificationKey = None,
                 ):
        '''

        :param launch_module_name: имя вызывающего модуля (объекта, содержащего контейнер)
        :param process_manager: менеджер процесса, который руководит запуском.
        :param objects_type: тип данных объектов. Именно по нему будут создаваться объекты в create.
        :param identification_key: идентификационный ключ контейнера с данными.
        '''
        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name)
        self.__to_log = self.__Logger.to_log  # Сделаем себе функцию логирования

        self.__identification_key = identification_key
        if self.__identification_key is None:
            self.__to_log(message=f'__init__: Создан контейнер данных с типом объектов  {objects_type}',
                          log_type='DEBUG')
        else:
            self.__to_log(message=(f'__init__: Для объекта {identification_key.description} создан контейнер данных с типом объектов ' +
                                   f'{objects_type}'),
                          log_type='DEBUG')

        self.__objects_type = objects_type  # Запомним тип объектов
        self.__objects_dict = {}
        self.__max_int_key = 0


    # ------------------------------------------------------------------------------------------------
    # Закроем данные через property ------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def identification_key(self) -> ContainerIdentificationKey:
        return self.__identification_key

    @property  # функция отдаёт неглубокую копию
    def objects_dict(self) -> dict:
        return copy.copy(self.__objects_dict)

    @property
    def dict_keys(self) -> list:
        return list(self.__objects_dict.keys())

    @property
    def max_int_key(self) -> int:
        return self.__max_int_key

    # ------------------------------------------------------------------------------------------------
    # Менеджмент данных ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    def check_access(self, index: object) -> bool:
        '''
        Првоерка наличия объекта на индексе
        :param index: индекс/имя в наборе
        :return: статус
        '''
        try:
            a = self.__objects_dict[index]
            return True
        except KeyError:
            return False

    def get_object(self, index: object,
                   no_value: object = None) -> object or None:
        '''
        Функция возвращает объект или None
        :param index: индекс/имя в наборе
        :param no_value: что вернуть если объекта нет?
        :return: объект или None, если объекта нет
        '''
        try:
            return self.__objects_dict[index]
        except KeyError:
            return no_value

    def add_object(self, data_object: object,
                   replace: bool = True,
                   index_name: str or int or float = 'default') -> bool or int or None:
        '''
        Функция принимает объект типа, указанного в __init__ (objects_type)
        :param data_object: объект, который надо поместить в контейнер. Тип объекта self.__objects_type
        :param replace: заменить если индекс занят?
        :param index_name: индекс словаря, на который будет добавлен объект. По умолчанию это __max_key + 1
        :return: Если индекс указан явно: был ли свободен индекс? True - свободен, False - был занят.
                 Если индекс поставлен 'default' - вернёт индекс
                 В случае ошибки - None
        '''
        if not isinstance(data_object, self.__objects_type):  # Если тип неверный
            self.__to_log(message=(f'add_object: ошибка типа данных поданного объекта. Ожидалось "{self.__objects_type}",' +
                                   f'получено {type(data_object)}'),
                          log_type='ERROR')
            return None

        # Установим индекс
        if index_name == 'default':  # Если ставим дефолтный
            # чтобы self.__max_key был всё время актуален
            self.__max_int_key += 1  # Сначала крутанём
            new_index = self.__max_int_key  # потом возьмём
        else:
            new_index = index_name
            if isinstance(new_index, int):  # Если ключ - целый индекс
                if new_index > self.__max_int_key:  # Если значение больше текущего максимального
                    self.__max_int_key = new_index  # заменим текущее на новое

        try:  # Првоерим, занят ли индекс
            a = self.__objects_dict[new_index]
            free = False
        except KeyError:
            free = True

        # Добавим в селф
        if free or replace:  # Если индекс свободен или разрешена замена
            self.__objects_dict[new_index] = data_object

        if index_name == 'default':  # если индекс определялся внутри функции
            return new_index  # вернём индекс
        else:  # Если индекс был подан заранее
            return free  # ну - вернём результат

    def del_object(self, index_name: str or int or float) -> bool:
        '''
        Функция пытается удалить объект
        :param index_name: индекс элемента, который мы удалим
        :return: True - объект был и он удалён, False - объекта не было
        '''
        try:
            self.__objects_dict.pop(index_name)
            return True  # Если объект был и успешно удалён
        except KeyError:
            return False  # Если объекта не было

    '''
    def create_object(self, replace: bool = True,
                      index_name: str or int or float = 'default',
                      **kwargs) -> bool or None:
        ''
        Использование функции КРАЙНЕ не рекомендуется. Она есть только для полноты набора. Куда более умно будет
        создать объект вне функции и передать в контейнер через add_object
        :param replace: заменить если индекс занят?
        :param index_name: индекс словаря, на который будет добавлен объект. По умолчанию это __max_key + 1
        :param kwargs: агрументы, которые будут переданы в объект.
        :return: был ли свободен индекс? True - свободен, False - был занят. В случае ошибки - None
        ''
        # Установим индекс
        if index_name == 'default':  # Если ставим дефолтный
            # чтобы self.__max_key был всё время актуален
            self.__max_key += 1  # Сначала крутанём
            index_name = self.__max_key  # потом возьмём

        # Пробуем создать обхект
        try:
            New_obj = self.__objects_type(**kwargs)  # Передадим объекты
            print('Запрошена неработающая функция создания объекта')
            self.__to_log(message=f'Запрошена неработающая функция создания объекта. Аргументы: {**kwargs}',
                          log_type='ERROR')
        except BaseException as miss:
            self.__to_log(message=f'ошибка создания объекта: {miss}. Аргументы: {**kwargs}',
                          log_type='ERROR')
            return None

        try:  # Првоерим, занят ли индекс
            a = self.__objects_dict[index_name]
            free = False
        except KeyError:
            free = True
            # Добавим в селф

        if free or replace:  # Если индекс свободен или разрешена замена
            self.add_object(data_object=New_obj, index_name=index_name)  # добавим

        return free
        #'''

