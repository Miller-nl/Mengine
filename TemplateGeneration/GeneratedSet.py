'''
Объекты, хранящие данные о самих сгенерированных экземплярах и о
# --------------------------------------------------------------------------------------------------------
# Контейнер GeneratedSet ---------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Объект хранит в себе набор сгенерированных элементах. Набор нужен для удобной обработки контейнера данных.
Все "оценки" на разрешение генерации будут в отдельных модулях. Тут находится только контейнер.

Параметры init:
    launch_module_name - имя вызывающего модуля
    process_manager - менеджер процесса, который руководит запуском
    masks_pattern - список из масок, которые будут использоваться


Доступные методы и свойства:
    основные @property (БЕЗ setter-а!)
        masks_pattern - шаблон с названиями масок в правильном порядке. Это копия.
        generated_objects - копия словаря со сгенерированными элементами из контейнера. Индекс в словаре - id элементов.


    # Функции для работы со значениями масок
    create_mask_token(mask_name: str or int, value: object, mapping: object = None) -> False or int - Функция создаёт
        объект - значение маски и добавляет его в словарь шаблона. Если объект со значением value для маски mask_name
        уже есть, то это считается ошибкой (т.к. маппинг нельзя заменить или скорректировать у уже созданного объекта.
        Однако, его можно указать как параметр).
        :param mask_name: имя маски, для которой создаётся значение
        :param value: непосредственно значение
        :param mapping: маппинг для объекта
        :return: int индекс значения или False в случае ошибки.

    add_mask_token(mask_value: MaskValue) -> False or int - функция добавляет "значение" для какой-либо маски
        генератора. Важно, что у маски должен быть указан параметр "id" - индекс. Т.к. он используется в работе.
        :param mask_value: значение маски в виде объекта MaskValue
        :return: int индекс значения или False в случае ошибки.

    get_mask_values(mask_name: str or int, generation_allowed: bool = None) -> list or None - Функция выдаёт копию
        (неглубокую) списка масок (с объектами MaskValue), чтобы список защитить от изменения.
        :param mask_name: имя маски
        :param generation_allowed: статус "разрешённости" генерации по маскам. None - все, вне зависимости.
        :return: список или None в случае ОШИБКИ маски. Список может быть пуст.

    get_value(value_id: int) -> MaskValue or None - Индекс содержится на value.get_parameter(name='id').
        Индекс даётся всем при добавлении в self
        :param value_id: индекс значения
        :return: ссылка на объект или ничего

    # Функция сгенерированных параметров
    create_object(masks_values: list or dict, element_id: int = None, parameters: list or dict = None,
                  default_parameter: object = None) -> GeneratedObject or None - Функция создаёт объект GeneratedObject
        и добавляет его в self. При автоматически указываются masks_pattern и logging_function, т.к. они есть в наборе.
        :param masks_values: список с объектами - значениями на масках : {mask_name: MaskValue} или просто список
            значений масок. Подать обязательно!
        :param element_id: персональный id объекта. Может быть определён автоматически через максимальный id в
            контейнере, т.к. все индексы тут int.
        :param parameters: список названий параметров или готовый словарь с параметрами.
            Параметр может быть любым, но предпочтительно - числовым, bool или строкой. Не стоит использовать
            сложные объекты типа словарей или других контейнеров.
        :param default_parameter: "дефолтный" параметр
        :return: ссылка на новый элемент, если всё ок, или None, если не ок.

    add_object(generated_object: GeneratedObject, checking_combination_elements: bool = True) -> bool or GeneratedObject -
        Функция добавляет в self сгенерированный объект.
        :param generated_object: непосредственно объект
        :param checking_combination_elements: выполнить ли проверку корректности элементов комбинации (масок и их
            значений)? False для процесса генерации. это функция для "внешних" добавлений сгенеренных объектов.
        :return: True, если объект успешно добавлен. False - при критической ошибке. GeneratedObject - если комбинация
            уже занята другим объектом. Смысл возвращения GeneratedObject в том. чтобы модифицировать его нужным
            образом - как generated_object.

    get_generated_object(element_id: int) -> GeneratedObject or None - Функция пытается извлечь из контейнера
        объект с индексом
        :param element_id: индекс элемента
        :return: GeneratedObject, если он есть, None - если нет.

    get_elements_dict(post_processed: bool = None, detailing_allowed: bool = None, level: int = None) -> dict - Функция
        выдаёт список элементов.
        :param post_processed: получить постобработанные элементы? T  - да, F - нет, None - все.
        :param detailing_allowed: разрешение на генерацию для объектов.
        :param level: уровень или "количество непустых значений масок"
        :return: словарь элементов. Словарь может быть пуст. Индекс словаря - id элемента.

    del_object(element_id: int) -> bool - Функиця удаляет объект с индексом element_id из контейнера.
        :param element_id: индекс объекта
        :return: статус удаления


    # Проверка наличия элемента
    fast_combination_check(masks_values: list) -> False or GeneratedObject - Функция проверят уникальность комбинации
        masks_values (GeneratedObject.masks_values) через self.__fast_access, возвращая отсутствие комбинации (False)
        или отвечающий ей объект.
        :param masks_values: список значений масок объекта в отвечающем шаблону порядке (GeneratedObject.masks_values)
        :return: False, если объекта нет или ссылка на объект.


self параметры
    __Logger - логер
    __to_log - функция логирования

    __masks_pattern - шаблон в виде списка, хранящиё в себе названия масок. Он нужен для сохранения порядка масок.

    __values_container - SetContainer со значениями масок в виде TemplateGeneration.GenDataContainers.MaskValue.
    __masks_values - словарь, дублирующий по своей сути __values_container. Он имеет вид: {mask_name: [values_list]}
        Где элементы values_list - ссылки на TemplateGeneration.GenDataContainers.MaskValue. Словарь нужен для того,
        чтобы быстро запрашивать все значения, имеющиеся для конкретной маски.

    __generated_objects - SetContainer, содержащий в себе сгенерированные объекты, полученные во время работы
        из генератора или из API. Вид объектов - TemplateGeneration.GenDataContainers.GeneratedObject .
    __fast_access - словарь, дублирующий __generated_objects. Он используется для быстрой проверки наличия той или иной
        комбинации значений масок. Его вид:  {id1: {id2: {id3: {}}}}
        Вложенные словари имеют два вида индекса: "числовой" - по id и индекс "GeneratedObject", который запрашивает
        GeneratedObject с комбинацией значений, повторяющих индексы. При этом порядок использования id значений
        устанавливается порядком масок в шаблоне, который обходится слева направо.
'''

import copy

from Managers.ProcessesManager import ProcessesManager
from DataContainers.SetsFunctionality import SetContainer, ContainerIdentificationKey
from TemplateGeneration.GenDataContainers import GeneratedObject, MaskValue  # Контейнеры данных


class GeneratedSet:
    '''
    Объект, хранящий в себе набор сгенерированных объектов. Смысл - это более сложный, чем обычный словарь объект,
        но всё ещё контейнер.

    Важно отметить, что внутри контейнера SetContainer может быть свой индекс, отдельный от GeneratedObject.element_id.
    Однако в данном наборе эти индексы совпадают. Т.к. при добавлении объекта в контейнер ему явно указывается индекс.

    Все "оценки" на разрешение генерации будут в отдельных модулях. Тут находится только контейнер.
    '''

    def __init__(self, masks_pattern: list,
                 process_manager: ProcessesManager, launch_module_name: str = None
                 ):
        '''
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер процесса, который руководит запуском
        :param masks_pattern: список из масок, которые будут использоваться
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name,
                                                      log_initialization=True)
        self.__to_log = self.__Logger.to_log

        self.__masks_pattern = masks_pattern  # шаблон, указывающий порядок масок

        identification_key = ContainerIdentificationKey(name='Значения масок',
                                                        data_description='Контейнер хранящий значения масок шаблона для генератора')
        self.__values_container = SetContainer(launch_module_name='GeneratedSet',
                                               process_manager=process_manager,
                                               objects_type=MaskValue,
                                               identification_key=identification_key)  # основной контейнер с масками

        # Заведём словарь с данными для генерации. Структура: {mask_name: [values_list]}
        self.__masks_values = {}
        for mask_name in self.__masks_pattern:
            self.__masks_values[mask_name] = []  # Заведём пустые списки
        '''
        __masks_values
        Словарь, дублирующий __values_container. Его смысл в том, чтобы обеспечить ускорение генерации путём добавления
        возможности запросить список значений маски как список, без обхода всего набора с проверкой масок.
        {mask_name: [values_list]} , где values_list является списком ссылок на элементы-значения (MaskValue)
        '''

        # Создадим словарь для сгенеренных объектов. Индекс в словаре - id элемента
        self.__generated_objects = SetContainer(launch_module_name='GeneratedSet',
                                                process_manager=process_manager,
                                                objects_type=GeneratedObject,
                                                identification_key=identification_key)  # основной контейнер с объектами

        self.__fast_access = {}  # Словарь с объектами, который будет использоваться во время генерации и проверок.
        '''
        При добавлении value будет присвоен некоторый уникальный id в качесвте параметра, и
        все сгенерированные объекты будут помещены в контейнер __generated_objects и задублированы в __fast_access.
        Структура словаря __fast_access : {id1: {id2: {id3: {}}}}
        Вложенные словари имеют два вида индекса: "числовой" - по id и индекс "GeneratedObject", который запрашивает
        GeneratedObject с комбинацией значений, повторяющих индексы. При этом порядок использования id значений
        устанавливается порядком масок в шаблоне, который обходится слева направо.
        '''

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property  # копируется (не глубоко) чтобы выдать данные, но защитить список от изменения
    def masks_pattern(self) -> list:
        return copy.copy(self.__masks_pattern)

    @property  # копируется (не глубоко) чтобы выдать данные, но защитить словарь от изменения
    def generated_objects(self) -> dict:
        return self.__generated_objects.objects_dict

    # ------------------------------------------------------------------------------------------------
    # Работа со значениями масок ---------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    ''' Заполнение масок из Frame делать не будем - слишком много кастомной логики будет '''
    def create_mask_token(self, mask_name: str or int,
                          value: object,
                          mapping: object = None) -> False or int:
        '''
        Функция создаёт объект - значение маски и добавляет его в словарь шаблона.
        Если объект со значением value для маски mask_name уже есть, то это считается ошибкой (т.к. маппинг нельзя
        заменить или скорректировать у уже созданного объекта. Однако, его можно указать как параметр).
        :param mask_name: имя маски, для которой создаётся значение
        :param value: непосредственно значение
        :param mapping: маппинг для объекта
        :return: int индекс значения или False в случае ошибки.
        '''
        if not mask_name in self.__masks_pattern:  # Если значения маски нет в шаблоне
            self.__to_log(message=(f'add_mask_token: указанное имя маски "{mask_name}" отсутсвтует в ' +
                                   f'шаблоне: {self.__masks_pattern}. Добавление отменено'),
                          log_type='ERROR')
            return False

        # Проверим уникальность значения value
        for self_el in self.__masks_values[mask_name]:  # Пошли по имеющимся элементам
            if self_el.value == value:  # Если значения совпали
                self.__to_log(message=(f'add_mask_token: для указанной маски "{mask_name}" уже есть значение {value}.' +
                                       f' Добавление отменено'),
                              log_type='ERROR')
                return False
        #  Если значение уникально
        new_value = MaskValue(mask=mask_name, value=value, mapping=mapping)  # Создадим значение
        new_value_id = self.add_mask_token(mask_value=new_value)  # добавим маску
        new_value.add_parameter(name='id', value=new_value_id)  # сообщим маске её индекс в наборе

        return new_value_id  # Вернём индекс

    def add_mask_token(self, mask_value: MaskValue) -> False or int:
        '''
        функция добавляет "значение" для какой-либо маски генератора. Важно, что у маски должен быть указан параметр
        "id" - индекс. Т.к. он используется в работе.
        :param mask_value: значение маски в виде объекта MaskValue
        :return: int индекс значения или False в случае ошибки.
        '''
        mask_name = mask_value.mask  # Чекаем значение маски

        if not mask_name in self.__masks_pattern:  # Если значения маски нет в шаблоне
            self.__to_log(message=(f'add_mask_token: указанное в объекте имя маски "{mask_name}" отсутсвтует в ' +
                                   f'шаблоне: {self.__masks_pattern}. Добавление отменено'),
                          log_type='ERROR')
            return False

        # Проверим, есть ли такое значение в словаре
        if mask_value in self.__masks_values[mask_name]:
            self.__to_log(message=f'add_mask_token: поданное значение маски уже имеется',
                          log_type='WARNING')
            return True
        else:  # Если нет
            self.__masks_values[mask_name].append(mask_value)  # добавим в словарь
            new_value_id = self.__values_container.add_object(data_object=mask_value)  # добавим индекс в контейнер
            # т.к. индекс не указан явно, функция вернёт индекс
            mask_value.add_parameter(name='id', value=new_value_id)  # сообщим маске её индекс в наборе

            # Добавим "сгенерированный объект" из маски. Иначе значение не будет участвовать в генерации
            self.create_object(masks_values=[mask_value])  # одна маска.

            return new_value_id  # Вернём индекс

    def get_mask_values(self, mask_name: str or int,
                        generation_allowed: bool = None) -> list or None:
        '''
        Функция выдаёт копию (неглубокую) списка масок (с объектами MaskValue), чтобы список защитить от изменения.
        :param mask_name: имя маски
        :param generation_allowed: статус "разрешённости" генерации по маскам. None - все, вне зависимости.
        :return: список или None в случае ОШИБКИ маски. Список может быть пуст.
        '''
        try:
            export_data = copy.copy(self.__masks_values[mask_name])  # если маска есть, СКОПИРУЕМ список
        except KeyError:  # Если нет маски
            return None  # вернём None

        if generation_allowed is None:  # Если статус не важен
            return export_data  # вернём экспортный список
        else:  # Если важен
            # Подготовим список на экспорт
            result = []
            for value in export_data:  # пошли по значениям
                if value.generation_allowed == generation_allowed:  # Если статус совпал
                    result.append(value)  # добавим в список

            return result  # вернём список.

    def get_value(self, value_id: int) -> MaskValue or None:
        '''
        Индекс содержится на value.get_parameter(name='id'). Индекс даётся всем при добавлении в self
        :param value_id: индекс значения
        :return: ссылка на объект или ничего
        '''
        return self.__values_container.get_object(index=value_id, no_value=None)

    # ------------------------------------------------------------------------------------------------
    # Работа над сгенерированными объектами ----------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def create_object(self, masks_values: list or dict,
                      element_id: int = None,
                      parameters: list or dict = None, default_parameter: object = None) -> GeneratedObject or None:
        '''
        Функция создаёт объект GeneratedObject и добавляет его в self.
        При автоматически указываются masks_pattern и logging_function, т.к. они есть в наборе.
        :param masks_values: список с объектами - значениями на масках : {mask_name: MaskValue} или просто список
            значений масок. Подать обязательно!
        :param element_id: персональный id объекта. Может быть определён автоматически через максимальный id в
            контейнере, т.к. все индексы тут int.
        :param parameters: список названий параметров или готовый словарь с параметрами.
            Параметр может быть любым, но предпочтительно - числовым, bool или строкой. Не стоит использовать
            сложные объекты типа словарей или других контейнеров.
        :param default_parameter: "дефолтный" параметр
        :return: ссылка на новый элемент, если всё ок, или None, если не ок.
        '''
        if element_id is None:  # Если не указан id элемента
            # чекнем его из набора контейнера. Т.к. индекс int и контейнер знает его максимальное значение
            element_id = self.__generated_objects.max_int_key + 1  # возьмём на 1 больше, т.к. max_key занят
        for new_value in masks_values:  # Проверим типы поданных значений масок
            if not isinstance(new_value, MaskValue):  # Если тип неверный
                self.__to_log(message=(f'create_object: создание объекта полностью провалено. Вместо маски ' +
                                       f'подан неверный объект: {type(new_value)} {new_value}. Параметры: ' +
                                       f'element_id={element_id}, masks_values={masks_values}, parameters={parameters}'
                                       ),
                              log_type='ERROR')
                return None  # Вернём ошибку
        # создадим объект
        new_object = GeneratedObject(element_id=element_id,
                                     masks_pattern=self.masks_pattern, masks_values=masks_values,
                                     parameters=parameters, default_parameter=default_parameter,
                                     logging_function=self.__to_log)
        # отдадим в добавление
        result = self.add_object(generated_object=new_object, checking_combination_elements=True)

        # проверим результат (залогируем, если надо)
        if result is False:
            for j in range(0, len(masks_values)):  # Заменим объекты на их значения для логирования
                masks_values[j] = masks_values[j].value
            self.__to_log(message=(f'create_object: создание объекта полностью провалено. Параметры: ' +
                                   f'element_id={element_id}, masks_values={masks_values}, parameters={parameters}'),
                          log_type='ERROR')
            return None  # Вернём ошибку
        else:
            if result is True:  # если добавление удачно и копии нет
                return new_object  #вернём ссылку на объект
            else:  # Если это дубль
                log_dist = {}  #Словарь для логирования вида {mask: el_id}
                for j in range(0, len(masks_values)):  # Заменим объекты на их значения для логирования
                    log_dist[masks_values[j].mask] = masks_values[j].get_parameter(name='id')
                self.__to_log(message=(f'add_object: При создании объекта {new_object.element_id} он оказался дублем {result.element_id}. ' +
                                       f'Использована комбинация masks_values={log_dist}'),
                              log_type='WARNING')
                return result  # вернём ссылку на имеющийся объект

    def add_object(self, generated_object: GeneratedObject,
                   checking_combination_elements: bool = True) -> bool or GeneratedObject:
        '''
        Функция добавляет в self сгенерированный объект.
        :param generated_object: непосредственно объект
        :param checking_combination_elements: выполнить ли проверку корректности элементов комбинации (масок и их
            значений)? False для процесса генерации. это функция для "внешних" добавлений сгенеренных объектов.
        :return: True, если объект успешно добавлен. False - при критической ошибке. GeneratedObject - если комбинация
            уже занята другим объектом. Смысл возвращения GeneratedObject в том. чтобы модифицировать его нужным
            образом - как generated_object.
        '''
        if not isinstance(generated_object, GeneratedObject):
            self.__to_log(message=f'add_object: тип поданного объекта неприемлем: {type(generated_object)}',
                          log_type='ERROR')
            return False

        # Выполним быструю проверку незанятости индекса
        if self.__generated_objects.check_access(index=generated_object.element_id):  # Если объект занят
            # Если id занят
            existing_facility = self.__generated_objects.get_object(index=generated_object.element_id)  # имеющийся
            if existing_facility.masks_values == generated_object.masks_values:  # Если их значения совпали
                # вернём объект, который уже есть
                self.__to_log(message=(f'add_object: индекс поданного объекта - {generated_object.element_id} ' +
                                       'уже используется. Возвращена ссылка на объект'),
                              log_type='WARNING')
                return existing_facility
            else:  # Если значения масок не совпали
                new_values = generated_object.masks_values  # список новых значений
                for j in range(0, len(new_values)):  # Заменим объекты на их значения для логирования
                    new_values[j] = new_values[j].value
                existing_values = existing_facility.masks_values  # список старых значений
                for j in range(0, len(existing_values)):  # Заменим объекты на их значения для логирования
                    existing_values[j] = existing_values[j].value

                self.__to_log(message=(f'add_object: индекс поданного объекта - {generated_object.element_id} ' +
                                       'уже используется. Но значения нового и старого элементов не совпали! ' +
                                       f'new: {new_values}, ' +
                                       f'existing: {existing_values}'),
                              log_type='ERROR')
                return False  # Вернём оишбку

        result = self.fast_combination_check(masks_values=generated_object.masks_values)  # Проверим, есть ли комбинация
        if isinstance(result, GeneratedObject):  # Если возвращена ссылка на объект, а не False
            return result  # Вернём ссылку на объект

        if checking_combination_elements:  # Если надо првоерить корректность объекта
            # Проверим, что маски принадлежат шаблону генератора
            for mask_value in generated_object.masks_values:
                try:
                    # Если у двух значений один id, они должны совпасть.
                    # id, которого нет в наборе или значения, которого нет в наборе быть не может - это ошибка

                    # Запросим из контейнера значение маски с таким же id, что у сгенеренного объекта
                    current_value = self.__values_container.get_object(index=mask_value.get_parameter(name='id'))
                    if current_value != mask_value:  # проверим равенство значений
                        self.__to_log(message=(f'add_object: маски с индексом {mask_value.get_parameter(name="id")} ' +
                                               f'не совпадают. Добавление объекта {generated_object.element_id} прервано'),
                                      log_type='ERROR')
                        return False  # Вернём ошибку

                except KeyError:  # Если была ошибка доступа в словарь
                    self.__to_log(message=(f'add_object: маска с индексом {mask_value.get_parameter(name="id")} ' +
                                           f'отсутсвтует в словаре. Добавление объекта {generated_object.element_id} прервано'),
                                  log_type='ERROR')
                    return False  # Вернём ошибку

                except BaseException as miss:  # Если было нечто иное
                    self.__to_log(message=(f'add_object: для маски "{mask_value.mask}" значения "{mask_value.value}"' +
                                           f' получена критическая ошибка проверки: {miss}. ' +
                                           f'Добавление объекта {generated_object.element_id} прервано'),
                                  log_type='ERROR')
                    return False  # Вернём ошибку

        # Если дошли до сюда, то проверка или не запрашивалась, или выполнена успешно

        self.__add_generated_object(generated_object=generated_object)  # выполним добавление
        return True  # Вернём успешность выполнения

    def __add_generated_object(self, generated_object: GeneratedObject):
        '''
        Функция добавляет generated_object в self словари: self.__fast_access и self.__generated_objects.
        Она строго внутренняя, так как не делает никаких проверок.
        :param generated_object: сгенерированный объект
        :return: ничего
        '''
        # Добавим объект в контейнер __generated_objects
        self.__generated_objects.add_object(data_object=generated_object, index_name=generated_object.element_id)

        # Добавим ссылку в словарь быстрого доступа __fast_access:

        # получим список id масок объекта
        masks_ids = []
        for mask in generated_object.masks_values:  # пошли по маскам
            masks_ids.append(mask.get_parameter(name="id"))  # чекаем параметр "id" в масках
            # (он даётся при добавлении маски в шаблон в генераторе)

        add_to = self.__fast_access  # Берём ссылку на словарь быстрого доступа
        for mask_id in masks_ids:
            try:
                add_to = add_to[mask_id]  # пробуем получить словарь с mask_id
            except KeyError:  # Если его нет
                add_to[mask_id] = {}  # создадим
                add_to = add_to[mask_id]  # берём ссылку
        # на выходе имеем ссылку на "последний словарь"
        add_to["GeneratedObject"] = generated_object  # Добавим объект на индекс "GeneratedObject"
        return

    def get_generated_object(self, element_id: int) -> GeneratedObject or None:
        '''
        Функция пытается извлечь из контейнера объект с индексом
        :param element_id: индекс элемента
        :return: GeneratedObject, если он есть, None - если нет.
        '''
        return self.__generated_objects.get_object(index=element_id, no_value=None)

    def get_elements_dict(self, post_processed: bool = None,
                          detailing_allowed: bool = None,
                          level: int = None) -> dict:
        '''
        Функция выдаёт список элементов.
        :param post_processed: получить постобработанные элементы? T  - да, F - нет, None - все.
        :param detailing_allowed: разрешение на генерацию для объектов.
        :param level: уровень или "количество непустых значений масок"
        :return: словарь элементов. Словарь может быть пуст. Индекс словаря - id элемента.
        '''
        elements_dict = self.__generated_objects.objects_dict  # снимем копию словаря элементов из контейнера
        if isinstance(post_processed, bool):  # Если состояние важно
            for element_id in list(elements_dict.keys()):  # Пошли по элементам
                # Если элемент не удовлетворяет условию обработки
                if elements_dict[element_id].post_processed != post_processed:
                    elements_dict.pop(element_id)  # дропнем со словаря

        if isinstance(level, int):  # Если указан уровень
            for element_id in list(elements_dict.keys()):  # Пошли по элементам
                # Если элемент не удовлетворяет условию на уровень
                if elements_dict[element_id].level != level:
                    elements_dict.pop(element_id)  # дропнем со словаря

        if isinstance(detailing_allowed, bool):  # Если указано разрешение на генерацию
            for element_id in list(elements_dict.keys()):  # Пошли по элементам
                # Если элемент не удовлетворяет условию на разрешение
                if elements_dict[element_id].detailing_allowed != detailing_allowed:
                    elements_dict.pop(element_id)  # дропнем со словаря

        return elements_dict

    def del_object(self, element_id: int) -> bool:
        '''
        Функиця удаляет объект с индексом element_id из контейнера.
        :param element_id: индекс объекта
        :return: статус удаления
        '''
        return self.__generated_objects.del_object(index_name=element_id)  # вернём результат

    # ------------------------------------------------------------------------------------------------
    # Функции проверки наличия элемента --------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def fast_combination_check(self, masks_values: list) -> False or GeneratedObject:
        '''
        Функция проверят уникальность комбинации masks_values (GeneratedObject.masks_values) через self.__fast_access,
        возвращая отсутствие комбинации (False) или отвечающий ей объект.
        :param masks_values: список значений масок объекта в отвечающем шаблону порядке (GeneratedObject.masks_values)
        :return: False, если объекта нет или ссылка на объект.
        '''
        object_check = self.__fast_access  # Берём ссылку на словарь быстрого доступа
        for mask_value in masks_values:  # попробуем получить ссылку на объект
            try:
                object_check = object_check[mask_value.get_parameter(name='id')]
            except KeyError:  # Если нет такой комбинации
                return False  # Значит, и объекта нет
        # Если комбинация есть в словаре
        try:  # Проверим индекс "GeneratedObject" с объектом
            object_check = object_check['GeneratedObject']
            return object_check  # Вернём ссылку на него
        except KeyError:  # Если ошибка доступа
            return False  # Вернём, что объекта нет