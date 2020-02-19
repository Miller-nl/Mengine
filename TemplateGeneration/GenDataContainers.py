'''
Объекты, хранящие данные о самих сгенерированных экземплярах и о 
# --------------------------------------------------------------------------------------------------------
# Контейнер MaskValue ------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Объект хранит в себе данные о значении маски, которая находится в шаблоне для генерации. Причём значение может
быть сопровождено набором произвольных параметров и маппингом.
Объект используется в GeneratedObject из GeneratedSet в качестве "набора значений", вокруг которого собственно
образуется GeneratedObject.

Параметры init:
    mask: str or int -  маска, для которой используется текущее значение. Используется для маппинга на маски.
    value: object - индекс значения, само значение, всё, что угодно.
    mapping: object = None - маппинг значения в любом удобном виде. Это маппинг на сайт или что-нить ещё.
    parameters_dict: dict = None - дополнительные параметры конкретного ЗНАЧЕНИЯ МАСКИ.


Доступные методы и свойства:
    основные @property (БЕЗ setter-а!)
        mask - маска значения
        value - непосредственно объект - значение
        parameters - неглубокая копия словаря с параметрами. Неглубокая, чтобы защитить внутренний словарь от изменений.
        
    @property
        mapping - маппинг. Он может меняться у токена, что важно.
        generation_allowed - разрешена ли генерация с использованием этого значения?
        
    # Функции работы с параметрами
        add_parameter(name: str, value: object, replace: bool = True) -> bool - Функция добавляет параметр в self.
            :param name: имя параметра
            :param value:  значение параметра
            :param replace: заменить ли параметр, если он уже был
            :return: True, если индекс name был свободным, False, если был занят
    
        get_parameter(name: str, no_value: object = None) -> object -  Функция пытается выдать параметр из словаря с 
            параметрами.
            :param name: имя параметра
            :param no_value: значение, которое будет выдано в случае отсутствия параметра.
            :return: параметр или no_value
    
self параметры
    __mask - маска значения
    __value - само значение
    __mapping - маппинг значения
    __parameters_dict - словарь параметров
    __generation_allowed - разрешена ли генерация

# --------------------------------------------------------------------------------------------------------
# Контейнер GeneratedObject ------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Объект хранит в себе некоторую комбинацию, которая получена по шаблону. Комбинация хранится в виде упорядоченного
списка значений масок MaskValue. Упорядочивать не надо, значения упорядочиваются автоматически при добавлении.
Кроме того, объект может быть сопровождён набором дополнительных параметров.

Параметры init:
    element_id: персональный id объекта
    masks_pattern: список, содержащий названия масок в том порядке, в котором они идут в шаблоне! Он будет
        использоватся для сортирвки self значений. Он задаётся только при инициации и не можети быть изменён позже.
        может быть списком строк (предпочтительно для понятности) или int индексов.
    parameters: список названий параметров или готовый словарь с параметрами.
        Параметр может быть любым, но предпочтительно - числовым, bool или строкой. Не стоит использовать
        сложные объекты типа словарей или других контейнеров.
    default_parameter: "дефолтный" параметр
    detailing_allowed: разрешена ли "детализация" элемента? - генерирование ещё более длинных элементов.
    logging_function: функция для логирования


Доступные методы и свойства:

    # основные @property (БЕЗ setter-а!)
        element_id - персональный индекс элемента. Подаётся при создании. Важно, что в GeneratedSet при генерации
            индекс ставится автоматически. Поэтому  должен быть добавлен  новый нужный "маппинг";
        level - "уровень" сгенерированного объекта. Это количество использованных значейни масок;
        pattern - шаблон. Это список str or int значений, порядок в котором важен;
        masks_values - список значений масок MaskValue;
        used_masks - выдаёт список использованных масок. То есть масок, на которых есть непустые значения.
        
    # @property
        post_processed - выполнена ли "пост обработка"? Под пост обработкой может пониматсья любая обработка, которая
            делается после генерации.
        detailing_allowed - разрешена ли "детализация" (дальнейшая генерация по объекту)? Параметр нужен для разрешения
            или запрета генерации по тому или иному элементу вне генератора.


    # Функции для работы со значениями
        add_masks_values(masks_values: dict or list or MaskValue, replace: bool = True) -> bool - Функция добавляет 
            значения в список значений. Она может использоваться один раз для установки списка разом или
            несколько раз для поэтапного заполнения. Однако первый вариант предпочтительнее.
            Функция имеет немного специфичный алгоритм добавления. Его суть в том, чтобы добавить только те элементы,
            которые указаны в шаблоне, в нужном порядке. Для исключения проверок и проблем.
            :param masks_values: словарь значений вида {some_name: MaskValue}, или список или одно значение.
                порядок произвольный. Функция внутри себя воспроизведёт всё, что нужно.
            :param replace: заменить ли значения, если они имеются
            :return: статус отсутствия ошибок. Уникальность масок в нём не отображается.

        def get_masks_value(self, name: str or id) -> MaskValue or None -  Функция выдаёт значение указанной маски
            или None, если его нет
            :param name: название параметра
            :return: значение или None
        
    
    # Функции для работы с параметрами
        def parameters_dict() -> dict - Функция отдаёт неглубокую копию словаря с параметрами.

        def set_parameter(name: str, value: object) - Функция устанавливает значение value на индекс name 
            в __parameters.
            :param name: имя параметра
            :param value: значение параметра. Параметр может быть любым, но педпочтительно числовым, bool или строкой.
                Не стоит использовать сложные объекты типа словарей или других контейнеров.
            :return: ничего

        def get_parameter(name: str, no_value: object = None) -> int or float or None - Функция выдаёт значение 
            параметра name или None, если такого параметра нет.
            :param name: название параметра
            :param no_value: результат в случае отсутствия параметра в словаре.
            :return: значение или None
        del_parameter(name: str) -> bool - Функция пытается удалить параметр
            :param name: имя
            :return: статус удаления

self параметры
    __element_id - персональный индекс элементов
    __to_log - функция логирования
    __masks_pattern - списо-шаблон. Он содержит в себе "правильный порядок масок"
    __masks_values - список объектов значений. Нюанс в том, что в функции добавления токенов они савтоматически
        упорядочиваются.
    __parameters - словарь с параметрами.
    __post_processed - Детектор того, что объект "постобработан" после генерации
    __detailing_allowed - детектор того, что дальнейшая генерация разрешена
'''

import copy

# ------------------------------------------------------------------------------------------------
# Значение маски ---------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class MaskValue:
    '''
    Смысл объекта - контейнер для хранения данных о значении той или иной маски/place_holder-а шаблона. При генерации
    будут использоваться ссылки на эти объекты для экономии памяти.
    В parameters_dict можно пихнуть что угодно.

    Дополнительная выгода такого решения - эти объекты будут использоваться "мозгом" генератора для рассчёта того,
    какие комбинации будут удачными, а какие нет.
    '''

    def __init__(self, mask: str or int,
                 value: object,
                 mapping: object = None,
                 parameters_dict: dict = None,
                 generation_allowed: bool = True):
        '''
        :param mask: маска, для которой используется текущее значение
        :param value: индекс значения, само значение, всё, что угодно.
        :param mapping: маппинг значения в любом удобном виде.
        :param parameters_dict: дополнительные параметры ЗНАЧЕНИЯ МАСКИ
        :param generation_allowed: разрешено ли использование маски для генерации.
        '''

        # Возьмём основные параметры
        self.__mask = mask
        self.__value = value
        self.__mapping = mapping

        # Сделать ещё словарь с параметрами
        self.__parameters_dict = {}
        if isinstance(parameters_dict, dict):  # Если подан словарь с параметрами
            for parameter_name in parameters_dict.keys():  # Пошли по индексам
                self.__parameters_dict[parameter_name] = parameters_dict[parameter_name]  # Добавим параметры

        self.__generation_allowed = generation_allowed  # разрешена ли генерация с этой маской

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def mask(self) -> str or int:
        '''
        Возвращает маску
        :return: маска токена
        '''
        return self.__mask

    @property
    def value(self) -> object:
        '''
        Возвращает объект - значение.
        :return: значение токена
        '''
        return self.__value

    @property  # выдаёт КОПИЮ словаря
    def parameters(self) -> dict:
        '''
        Выдаёт неглубокую копию словаря. Смысл копирования в защите исходгого словаря от изменений.
        :return: копия словаря параметров токена.
        '''
        return copy.deepcopy(self.__parameters_dict)

    @property
    def mapping(self) -> object:
        '''
        Отдаёт маппинг, связанный со значением токена.
        :return: объект - маппинг.
        '''
        return self.__mapping

    @mapping.setter
    def mapping(self, value: object):
        '''
        Устанавливает маппинг токена. Маппинг может быть произвольным. но использованин сложных объектов не
        рекомендуется.
        :param value: Значение маппинга, которое будет установлено
        :return: ничего
        '''
        self.__mapping = value
        return

    @property
    def generation_allowed(self):
        return self.__generation_allowed

    @generation_allowed.setter
    def generation_allowed(self, value: bool):
        self.__generation_allowed = value
        return

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
# Сгенерированный объект -------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class GeneratedObject:
    '''
    Значения знают свою маску. Так что передаваться будут только значения масок в списке.
    Сгенерированный объект на одной маске может иметь только одно значение. Это заложено в add_masks_values.
    Считаем, что если значение маски не задано, то его нет.
    '''
    def __init__(self, element_id: int,
                 masks_pattern: list,
                 masks_values: list or dict = None,
                 parameters: list or dict = None, default_parameter: object = None,
                 detailing_allowed: bool = False,
                 logging_function=None):
        '''
        Сам объект генерации будет апеллировать только индексами значений. Он не будет использовать ни сами значения,
            ни маппин ни прочее. Только их индексы.
        ОЧЕНЬ ВАЖНО - в masks_values_ids должен быть сохранён правильный порядок масок, как в шаблоне. В противном
            случае могут быть проблемы.
        Однако объект может получить свой набор различных параметров.

        :param element_id: персональный id объекта
        :param masks_pattern: список, содержащий названия масок в том порядке, в котором они идут в шаблоне! Он будет
            использоватся для сортирвки self значений. Он задаётся только при инициации и не можети быть изменён позже.
            может быть списком строк (предпочтительно для понятности) или int индексов.
        :param masks_values: список с объектами - значениями на масках : {mask_name: MaskValue} или просто список
            значений масок.
        :param parameters: список названий параметров или готовый словарь с параметрами.
            Параметр может быть любым, но предпочтительно - числовым, bool или строкой. Не стоит использовать
            сложные объекты типа словарей или других контейнеров.
        :param default_parameter: "дефолтный" параметр
        :param detailing_allowed: разрешена ли "детализация" элемента? - генерирование ещё более длинных элементов.
        :param logging_function: функция для логирования
        '''

        self.__element_id = element_id

        self.__to_log = self.__set_logger(logging_function=logging_function)  # Установим функцию логирования
        self.__masks_pattern = masks_pattern  # Список, содержащий в себе "шаблон" для самовоспроизведения.

        self.__masks_values = []  # Список объектов MaskValue
        self.add_masks_values(masks_values=masks_values)  # выполним добавление масок

        self.__parameters = {}
        if isinstance(parameters, list):  # если подан список
            for el in parameters:  # воспроизведём словарь
                self.__parameters[el] = default_parameter
        elif isinstance(parameters, dict):  # если подан словарь
            self.__parameters = copy.copy(parameters)  # берём копию, чтобы защитить от изменения

        self.__post_processed = False  # Детектор того, что объект "постобработан" после генерации
        self.__detailing_allowed = detailing_allowed  # детектор того, что дальнейшая генерация разрешена

    def __set_logger(self, logging_function):
        '''
        Функция устанавливает функцию логирования
        :param logging_function: поданная в init-е функция или None
        :return: функция для логирования или заглушка
        '''
        # Создадим функцию логирования
        if logging_function is None:  # Если не подана функция для логирования
            def stub(*args, **kwargs):  # Сделаем "заглушку"
                return
            return stub  # вернём заглушку

        else:  # Если подана функция для логирования
            add_str = f'GeneratedObject {self.__element_id}: '
            def log_func(message: str, log_type: str ='DEBUG', **kwargs):
                message = add_str + message   # Сдеалем добавку к сообщению
                logging_function(message=message, log_type=log_type, **kwargs)  # отправим сообщение в лог
                return
            return log_func  # вернём функцию логирования

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def element_id(self) -> int:
        return self.__element_id

    @property
    def level(self) -> int:
        '''
        Функция возвращаяет количество имеющихся значений масок. То есть, условную "глубину".
        Если это ноль, то значений нет.
        :return:
        '''
        return len(list(self.__masks_values))

    @property  # неглубокая копия списка с именами масок
    def pattern(self) -> list:
        '''
        Неглубокая копия для того, чтобы можно было извлечь ссылки на объекты, но сам список изменить было нельзя.
        :return:
        '''
        return copy.copy(self.__masks_pattern)

    @property  # список значений масок
    def masks_values(self) -> list:
        '''
        Неглубокая копия для того, чтобы можно было извлечь ссылки на объекты, но сам список изменить было нельзя.
        :return:
        '''
        return copy.copy(self.__masks_values)

    @property
    def used_masks(self) -> list:
        export = []
        for value in self.masks_values:  # Пошли по значениям
            export.append(value.mask)  # пополним маской значения
        return export

    @property
    def post_processed(self) -> bool:
        return self.__post_processed

    @post_processed.setter
    def post_processed(self, value: bool):
        self.__post_processed = value
        return

    @property
    def detailing_allowed(self):
        return self.__detailing_allowed

    @detailing_allowed.setter
    def detailing_allowed(self, value: bool):
        self.__detailing_allowed = value
        return

    # ------------------------------------------------------------------------------------------------
    # Работа со значениями ---------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_masks_values(self, masks_values: dict or list or MaskValue,
                         replace: bool = True) -> bool:
        '''
        Функция добавляет значения в список значений. Она может использоваться один раз для установки списка разом или
        несколько раз для поэтапного заполнения. Однако первый вариант предпочтительнее.
        Функция имеет немного специфичный алгоритм добавления. Его суть в том, чтобы добавить только те элементы,
        которые указаны в шаблоне. Для исключения проверок и проблем.
        :param masks_values: словарь значений вида {some_name: MaskValue}, или список или одно значение.
            порядок произвольный. Функция внутри себя воспроизведёт всё, что нужно.
        :param replace: заменить ли значения, если они имеются
        :return: статус отсутствия ошибок. Уникальность масок в нём не отображается.
        '''
        # Подготовим список масок, которые уже есть
        have_masks = []
        for value in self.__masks_values:  # Пошли по списку
            have_masks.append(value.mask)  # Добавим маску в список

        if isinstance(masks_values, dict):
            new_elements = []  # список новых элементов
            for mask_name in masks_values.keys():  # Пошли по значениям
                new_elements.append(masks_values[mask_name])  # добавляем в список
        elif isinstance(masks_values, list):
            new_elements = masks_values  # Берём список как есть
        elif isinstance(masks_values, MaskValue):  # Если подан один элемент
            new_elements = [masks_values]
        else:  # если подана какая-то херь
            self.__to_log(message=(f'set_masks_values: поданный список имеет неверный тип ' +
                                   f'тип: {type(masks_values)}. Список пропущен'),
                          log_type='ERROR')
            return False

        if len(new_elements) > len(self.__masks_pattern):
            self.__to_log(message=(f'set_masks_values: длина поданного списка превышает количество масок ' +
                                   f'тип: {type(masks_values)}. Список пропущен'),
                          log_type='ERROR')
            return False

        new_self_list = []  # новый список, который попадёт в self
        for mask_name in self.__masks_pattern:  # Пошли по маскам из шаблона
            transit_self = None  # занулим
            transit_new = None

            for self_el in self.__masks_values:  # Пробежим по значениям
                if self_el.mask == mask_name:  # проверим маску
                    transit_self = self_el  # Если есть селф элемент для маски, чекаем его

            for new_el in new_elements:  # Пошли по новым
                if new_el.mask == mask_name:  # проверим маску
                    transit_new = new_el  # Если есть новый элемент для маски, чекаем его

            # Пошли заполним новый список
            if transit_self != None and transit_new == None:  # Если есть только старый
                new_self_list.append(transit_self)
            elif transit_self == None and transit_new != None:  # Если есть только новый
                new_self_list.append(transit_new)
            elif transit_self != None and transit_new != None:  # Если есть старое и новое значение
                if replace:  # Если надо сделать замену
                    new_self_list.append(transit_new)
                else:  # Если не надо делать замену
                    new_self_list.append(transit_self)

        self.__masks_values = new_self_list  # Заберём в селф
        return True  # Всё ок

    def get_masks_value(self, name: str or id) -> MaskValue or None:
        '''
        Функция выдаёт значение указанной маски или None, если его нет
        :param name: название параметра
        :return: значение или None
        '''
        try:
            return self.__masks_values[name]
        except KeyError:  # Если значения нет
            return None

    # ------------------------------------------------------------------------------------------------
    # Работа с параметрами ---------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def parameters_dict(self) -> dict:
        '''
        Функция отдаёт словарь с параметрами
        :return:
        '''
        return copy.copy(self.__parameters)

    def set_parameter(self, name: str, value: object):
        '''
        Функция устанавливает значение value на индекс name в __parameters.
        :param name: имя параметра
        :param value: значение параметра. Параметр может быть любым, но педпочтительно числовым, bool или строкой.
            Не стоит использовать сложные объекты типа словарей или других контейнеров.
        :return: ничего
        '''
        self.__parameters[name] = value
        return

    def get_parameter(self, name: str,
                      no_value: object = None) -> int or float or None:
        '''
        Функция выдаёт значение параметра name или None, если такого параметра нет.
        :param name: название параметра
        :param no_value: результат в случае отсутствия параметра в словаре.
        :return: значение или None
        '''
        try:
            return self.__parameters[name]
        except KeyError:  # Если значения нет
            return no_value

    def del_parameter(self, name: str) -> bool:
        '''
        Функция пытается удалить параметр
        :param name: имя
        :return: статус удаления
        '''
        try:
            self.__parameters.pop(name)
            return True
        except KeyError:  # Если значения нет
            return False
