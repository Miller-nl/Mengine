'''
# --------------------------------------------------------------------------------------------------------
# Контейнер GeneratedSet ---------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
Генератор работает над контейнером GeneratedSet. Генератор не делает НИ КАКОЙ АНАЛИТИКИ или "умных оценок".
Задача генератора: дял указанного элемента создать "детализацию" по шаблоону, проверить, разрешены ли объекты
из детализации и являются ли они новыми? Если всё в порядке - в набор GeneratedSet будет добавлен объект.

Параметры init:


Доступные методы и свойства:
    основные @property (БЕЗ setter-а!)

    # Функции генерации

    # Функции проверки элементов




Написать, что по ходу работы будут проверены родители на: факт существования, разрешение их детализации
Но родители чекаются только те, у которых есть все маски, отмеченные как основные.


Генератор только собирает, используя "разрешение" на сбор от набора GeneratedSet.  Внутри генератора нет никаких(!)
оценок или чего бы то ни было ещё.
Он просто получает команду на один или более шагов генерации и всё.






В генератор будет ПОДАВАТЬСЯ контейнер запросов.
Укажем параметры "сгенеренных комбинаций" и "токенов" - список имён, которые будут запрашиваться в функцию
    оценки. При этом будет указан маппинг параметров токенов и параметров функции.

    Вопрос в том, как передавать в функцию параметры? Словарём?

Функция может передаваться из менеджера

'''

import copy

from Managers.ProcessesManager import ProcessesManager
from TemplateGeneration.GenDataContainers import GeneratedObject, MaskValue  # Контейнеры данных
from TemplateGeneration.GeneratedSet import GeneratedSet  # Сам набор

class TemplateGenerator:
    '''
    Задача генератора: найти разрешённые комбинации значений масок и отдать в набор команду на создание соответствующих
        объектов.

    Для работы генератор получает: шаблон и GeneratedSet с имеющимися объектами.
    Для генерации в функцию object_detailing подаётся "сгенерированный объект" в качестве "стартовой" комбинации
        токенов, к которой будет добавлено +1 значение. Однако, если количество значений в объекте равно длине шаблона,
        то есть - шаблон исчерпан, будет выдана ошибка. Для удобства иожно явно указать маски, значения которых будут
        добавлены, если это не сделать, то:
            1. запросятся все "основные" маски, если хоть одна основаня маска не содержится в сгенерированном объекте,
                то генерация будет идти только по основным маскам.
            2. если все основные маски есть, то будут взяты все прочие - не освновные маски из шаблона.
    Результат - словарь с объектами, которые прошли проверку, вида: {имя_маски: [список_ссылок_на_объекты]} - для удобства.
        Все объекты из словаря будут новыми (если комбинация была, она не попадёт в словарь), но уже добавленными в
        набор, т.к. они создаются через GeneratedSet.create_object()

    '''

    def __init__(self, generated_set: GeneratedSet,
                 process_manager: ProcessesManager, launch_module_name: str = None,
                 required_masks: list = None):
        '''
        В required_masks не стоит указывать все маски шаблона. Если требуется снять только элементы максимальной длины,
        это следует делать через набор GeneratedSet, но не тут. Кроме того, оставлять список пустым тоже не желательно,
        так как это кратно увеличит количество комбинаций, которые, скорее всего, не будут нужны.
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер процесса, который руководит запуском
        :param generated_set: объект - набор сгенерированных комбинаций. Чистый или преднастроенный, но готовый.
        :param required_masks: "обязательные маски". То есть те, которые обязательно(!) должны быть в сгенерированных
            комбинациях. Эти маски не должны быть пустыми, как минимум нужно указать маску основного объекта.
        '''

        # Установим логер
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name,
                                                      log_initialization=True)
        self.__to_log = self.__Logger.to_log

        # Установим объект - набор
        self.__GeneratedSet = generated_set
        self.__masks_pattern = generated_set.masks_pattern  # снимим список для скорости доступа

        # установим данные об обязательных масках в self и определим, разрешена ли генерация?
        self._prepare_masks_pattern(required_masks=required_masks)

    # Функция забирает в self данные масок
    def _prepare_masks_pattern(self, required_masks: list or None):
        '''
        Функция загонит данные о маске объекта и обязательных масках в self.
        :param required_masks: список обязательных масок
        :return: ничего
        '''
        if required_masks is None:  # Если не подан список
            self.__required_masks = []  # Делаем список пустым
            self.__to_log(message=f'_prepare_masks_pattern: подан пустой список обязательных масок!',
                          log_type='WARNING')
        else:  # Если указаны маски
            # Проверим, что они все есть в шаблоне self.__masks_pattern и дромнем лишние
            keep_masks = []  # словарь масок, которые мы оставим
            for mask in list(set(required_masks)):  # Пошли по маскам (list, set чтобы предостеречься от дублей)
                if mask in self.__masks_pattern:  # Проверим вхождение
                    keep_masks.append(mask)  # добавим в список, чтобы был верный порядок
                else:
                    self.__to_log(message=(f'_prepare_masks_pattern: ошибка проверки маски {mask} из ' +
                                           f'required_masks: маски нет в наборе. Маска будет пропущена. ' +
                                           f'Поданный общий шаблон: {self.__masks_pattern}'),
                                  log_type='WARNING')

            if len(self.__masks_pattern) == len(required_masks):  # Если поданы все маски, которые вообще есть в шаблоне
                self.__to_log(message=(f'_prepare_masks_pattern: все маски шаблона {self.__masks_pattern} ' +
                                       f'поданы как обязательные. Это может привести к проблемам при генерации'),
                              log_type='WARNING')
            self.__required_masks = keep_masks
        return

    # ------------------------------------------------------------------------------------------------
    # Работа с пропертями ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def GeneratedSet(self) -> GeneratedSet:
        '''
        Функция для защиты внутреннего объекта-контейнера.
        :return: ссылка на внутренний контейнер
        '''
        return self.__GeneratedSet

    @property  # Делаем неглубокую копию полного списка масок, чтобы сохранить сам self список
    def masks_pattern(self) -> list:
        return copy.copy(self.__masks_pattern)

    @property  # Делаем неглубокую копию списка обязательных масок, чтобы сохранить сам self список
    def required_masks(self) -> list:
        return copy.copy(self.__required_masks)

    # ------------------------------------------------------------------------------------------------
    # Генерация --------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def object_detailing(self, parent_object: GeneratedObject,
                         masks_list: list = None) -> dict or None:
        '''
        Функция получает объект parent_object и воспроизводит для него все объекты, которые находятся на
        один уровень ниже - то есть, имеют на одну маску больше.
        В экспортный словарь НЕ поавдут элементы, которые уже имелись в контейнере (специфика __mask_generation),
        однако нужно будет проверить разрешённость комбинаций, т.к. в этом подпроцессе она НИГДЕ не проверяется и
        никакие(!) оценки не делаются.
        :param parent_object: объект для комбинации которого делается детализация.
        :param masks_list: список масок, для которых будет делаться детализация.
            None - определить через __prepare_masks_list
        :return: словарь вида {mask_name: [GeneratedObject list]} или None в случае ошибки. Исчерпывание в parent_object
            шаблона тоже считается ошибкой. Если словарь окажется пуст, вернётся None, т.к. это ошибка.
        '''
        # Подготовим маски:
        processing_masks = self.__prepare_masks_list(parent_object=parent_object, masks_list=masks_list)
        if processing_masks == []:  # Если список пуст (шаблон исчерпан), залогируем
            self.__to_log(message=(f'object_detailing: запрошена генерация для объекта {parent_object.element_id} по маскам {processing_masks}. ' +
                                   f'После проверки масок их список оказался пуст. Генерация по объекту пропущена'),
                          log_type='ERROR')
            return None  # вернём "ошибку"

        # Пойдём на генерацию
        export_dict = {}  # словарь для экспорта
        for processing_mask in processing_masks:  # Пошли по маскам
            result_list = self.__mask_generation(parent_object=parent_object,
                                                 processing_mask=processing_mask)  # делаем генерацию по маске
            if result_list is None:
                self.__to_log(message=(f'object_detailing: запрошена генерация для объекта {parent_object.element_id} по маске {processing_mask}. ' +
                                       f'Ошибка генерации'),
                              log_type='ERROR')
            elif result_list == []:
                self.__to_log(message=(f'object_detailing: запрошена генерация для объекта {parent_object.element_id} по маске {processing_mask}. ' +
                                       f'Список результатов пуст'),
                              log_type='WARNING')
            else:  # Если список не пуст - всё ок
                export_dict[processing_mask] = result_list  # занесём его в словарь

        if export_dict == {}:  # Если с ловарь пуст
            # Логируем
            self.__to_log(message=(f'object_detailing: запрошена генерация для объекта {parent_object.element_id} по маскам {processing_masks}. ' +
                                   f'Словарь списоков с результатами генерации пуст'),
                          log_type='WARNING')
            return {}  # Вернём пустой словарь, т.к. просто комбинации могли быть исчерпаны

        return export_dict

    def __prepare_masks_list(self, parent_object: GeneratedObject, masks_list: list = None) -> list:
        '''
        Функция получает маски объекта, для которого будет делаться шаг генерации. Выделяет, какие маски, не
        задействованные объектом, будут использоваться.
        Важно, что сначала воспроизводятся ТОЛЬКО обязательные маски, и, только если в родительском объекте
        заняты все обязательные маски, в генерацию пойдут прочие маски.
        Это дефолтная настройка.
        :param parent_object: ссылка на "родительский объект" (parent_object.used_masks)
        :param masks_list: список масок, для которых запрошена генерация. None - взять все маски, которые ещё не
            используются.
        :return: список масок, по которым будут добавляться значения в комбинацию. С сохранением порядка в шаблоне(!).
            Если список пуст, значит, родительский объект полностью исчерпывает шаблон.
        '''
        if masks_list is None:  # Если указаны "все маски"
            check_masks_list = self.__masks_pattern  # берём все маски шаблона
        else:
            check_masks_list = []  # заведём список
            for mask in masks_list:
                if mask in self.__masks_pattern:  # Если маска есть в шаблоне
                    check_masks_list.append(mask)
                else:  # Если нет
                    # логируем и скипаем
                    self.__to_log(message=(f'__prepare_masks_list: запрошена генерация для объекта {parent_object.element_id} по маскам {masks_list}. ' +
                                           f'Маски "{mask}" нет в шаблоне {self.__masks_pattern}. Маска пропущена'),
                                  log_type='WARNING')

        object_masks = parent_object.used_masks  # берём список масок, которые использует родитель

        processing_masks = []  # список, которые надо будет обрабоать
        # детектор того, что есть хоть одна "обязательная" маска, которой ещё нет в объекте parent_object
        any_required_mask = False  # По дефолту - ни одной
        for mask_name in check_masks_list:  # пошли по набору
            if not mask_name in object_masks:  # если маска не занята внутри объекта
                processing_masks.append(mask_name)  # добавим её в список к воспроизведению
                if mask_name in self.__required_masks:  # Если маска "обязательная", и её нет в parent_object
                    any_required_mask = True  # крутанём детектор

            elif not masks_list is None:  # Если маска занята, но она была принудительно подана в списке
                # логируем и
                self.__to_log(message=(f'object_detailing: запрошена генерация для объекта {parent_object.element_id} по маскам {processing_masks}. ' +
                                       f'Маска "{mask_name}" Уже занята в объекте. Маска пропущена'),
                              log_type='WARNING')

        if any_required_mask:  # Если есть хоть одна "обязательная маска", которая не присутствует в processing_masks
            # оставим только обязательные маски в списке
            buffer_list = []  # буферный список
            for check_mask in processing_masks:  # пошли по маскам, по которым планировалась генерация
                if check_mask in self.__required_masks:  # Если маска "обязательная"
                    buffer_list.append(check_mask)  # добавим её в список
            # по условию в buffer_list попадёт как минимум одна маска
            processing_masks = buffer_list  # работать будем только с обязательными масками

        return processing_masks

    # только воспроизведение списка объектов +1 уровня для конкретной маски
    def __mask_generation(self, parent_object: GeneratedObject,
                          processing_mask: str or int) -> list or None:
        '''
        Функция берёт комбинацию, использующуюся в конкретном GeneratedObject, и накидывает ещё одну маску (+1 уровень).
        Маска берётся из шаблона - это её название в шаблоне (строка или int - в зависимости от).
        Функция проверяет, что такой комбинации ещё нет, и что все "родители" для новой комбинации значений масок
        имеются в наборе и их детализация разрешена. Если это так, то функция создаёт/генерирует объект для комбинации и
        заносит данные в контейнер, так как это делается автоматически при создании нового объекта в наборе.
        Так как возвращается список добавленных элементов, вне функции можно запросить их удаление при необходимости.
        ВАЖНО: Установка значений шаблона в правильном порядке делается внутри GeneratedObject. Тут не надо это делать.
        "Пустое значение" маски не добавляется, т.к. такая комбинация отвечает поступившему объекту - parent_object.
        :param parent_object: объект для комбинации которого делается детализация.
        :param processing_mask: маска из self.__masks_pattern, дял которой будет делаться воспроизведение
        :return: список сгенерированных объектов GeneratedObject или None в случае ошибки. Может быть пуст, только
            если список значений маски был пуст. Обыекты, котоыре уже были в наборе в список НЕ ПОПАДУТ.
        '''
        # проверим, что значение маски является приемлемым
        if not processing_mask in self.__masks_pattern:  # Если нет
            self.__to_log(message=(f'__mask_generation: Элемент {parent_object.element_id}. ' +
                                   f'Ошибка проверки маски processing_mask = "{processing_mask}" :' +
                                   f' маски нет в шаблоне {self.__masks_pattern}. Работа закончена'),
                          log_type='ERROR')
            return None

        # Проверим, что указанная маска ещё не занята
        if processing_mask in parent_object.used_masks:  # Если маска уже занята
            self.__to_log(message=(f'__mask_generation: Элемент {parent_object.element_id}. ' +
                                   f'Ошибка проверки маски processing_mask = "{processing_mask}" :' +
                                   f' маска использована в элементе {parent_object.used_masks}. Работа закончена'),
                          log_type='ERROR')
            return None

        # Если всё ок

        parent_values = parent_object.masks_values  # Получим список значений от parent_object
        # Получим список значений маски, которая подана в проработку, для которых разрешена генерация
        mask_values_list = self.__GeneratedSet.get_mask_values(mask_name=processing_mask, generation_allowed=True)
        if mask_values_list == []:  # Если список пуст
            self.__to_log(message=(f'__mask_generation: Запрошенный по маске "{processing_mask}" ' +
                                   f'список токенов пуст'),
                          log_type='WARNING')
            return []

        # Подготовим словарь для "добавления" значения новой маски
        preparing_dict = self.__insert_mask_value(values_list=parent_values,
                                                  processing_mask=processing_mask)
        # Создадим список сгенерированных объектов с комбинациями
        export_objects_list = []  # список объектов для экспорта
        for new_mask_value in mask_values_list:  # пошли по новым маскам
            new_list = copy.copy(parent_values)  # сделаем неглубокую копию, чтобы не повлиять на parent_values
            new_list.append(new_mask_value)  # добавим в список значение для указанной новой маски
            new_list = preparing_dict['left_values'] + [new_mask_value] + preparing_dict['right_values']

            # Запросим в наборе разрешение на генерацию комбинации
            combination_check = self.ask_permission_to_generate(masks_values=new_list)

            if combination_check:  # Если генерация разрешена
                # Создадим новый объект с указанной комбинацией
                new_generated_object = self.__GeneratedSet.create_object(masks_values=new_list)
                if new_generated_object is None:  # Если добавление упало
                    # Логируем
                    self.__to_log(message=f'__mask_generation: Ошибка создания нового элемента. Элемент пропущен',
                                  log_type='ERROR')
                    continue  # скипаем
                else:  # Если всё ок
                    export_objects_list.append(new_generated_object)  # добавим ссылку на объект в список

            else:  # не разрешена
                continue  # скипаем, т.к. нас интересуют ТОЛЬКО новые объекты

        return export_objects_list  # закончим

    def __insert_mask_value(self, values_list: list,
                            processing_mask: str or int) -> dict:
        '''
        Задача функции разделить values_list на "левый список" и "правый список".
        :param values_list: список значений масок, в который мы вставим значения новых масок.
        :param processing_mask: "название" маски
        :return: словарь с индексом "left_masks", "left_values", "right_mask", 'right_values'
        '''
        # Мы обязательно найдём такое j, которое разделит шаблон на две части, т.к. processing_mask точно есть в шаблоне
        for j in range(0, len(self.__masks_pattern)):  # пошли по шаблону
            if self.__masks_pattern[j] == processing_mask:  # если номер маски найден
                # сплинтем
                left_masks = self.__masks_pattern[:j]  # левые маски
                right_mask = self.__masks_pattern[j+1:]  # правые маски
                break  # закончили

        # теперь разделим список значений.
        left_values = []  # Список может не разделиться, т.к. все маски из values_list могут быть левее новой
        right_values = []  # поэтому объявим тут
        for j in range(0, len(values_list)):  # пошли по значениям
            if values_list[j].mask in left_masks:  # если значение находится  в списке левых масок
                left_values.append(values_list[j])
            else:  # Если значение не находится в списке левых масок
                # значит оно и все правые значения должны быть из списка правых масок
                # т.к. попасть в processing_mask ни кто из них не может, т.к. processing_mask нет среди масок значений
                # по условию её определения
                right_values = values_list[j:]  # Заберём все значения от текущего включительно в правый список
                break  # закончим обход

        return {"left_masks": left_masks, "left_values": left_values,
               "right_mask": right_mask, "right_values": right_values}

    # ------------------------------------------------------------------------------------------------
    # Проверка новой комбинации ----------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def ask_permission_to_generate(self, masks_values: list) -> bool:
        '''
        Функция, которая проверяет разрешение на генерацию. Если объект уже есть или в наборе нет какой-то комбинации,
        короче данной на 1 маску, или у такой комбинации запрещена детализация - генерация запрещена. Если все
        более короткие комбинации есть и их детализация разрешена - то генерация разрешается.
        :param masks_values: комбинация токенов. Если комбинация занята, разрешение не даётся.
        :return: bool результат (ВСЕГДА bool).
        '''
        # проверим, нет ли такого объекта
        check_result = self.__GeneratedSet.fast_combination_check(masks_values=masks_values)
        if isinstance(check_result, GeneratedObject):  # Если есть
            return False  # запретим его генерацию
        if len(masks_values) > 1:  # Если есть "родители"
            # Если хоть одного из "родителей" нет в наборе или его детализация запрещена
            if not self.check_for_parents(masks_values=masks_values):
                # комбинация запрещена
                return False
        # Если всё ок
        return True

    def check_for_parents(self, masks_values: list) -> bool:
        '''
        Функция проверяет через быстрый доступ, что у комбинации masks_values есть все более короткие родители, и что
        для них разрешена генерация (GeneratedObject.detailing_allowed is True). То есть, комбинации, в которых одно
        значение из masks_values пропущено.
        Важная оговорка в том, что "пропускать" можно ТОЛЬКО НЕОБЯЗАТЕЛЬНЫЕ маски. Т.к. пропуск любой обязательной
        маски сразу приведёт к запрету.
        :param masks_values: комбинация токенов, для которой делается проверка.
        :return: статус
        '''
        for j in range(0, len(masks_values)):  # пошли по списку
            check_list = copy.copy(masks_values)  # копируем для защиты
            if check_list[j].mask in self.__required_masks:  # Если маска значения является обязательной
                continue  # скипаем пропуск этого значения (т.к. такого родителя точно нет)

            check_list = check_list[:j] + check_list[j + 1:]  # дропаем элемент из комбинации
            parent = self.__GeneratedSet.fast_combination_check(masks_values=check_list)  # чекаем родителя
            # parent это False или ссылка на GeneratedObject
            if parent is False:  # Если более короткой комбинации нет
                return False  # Вернём, что не все родители есть в наборе
            else:  # Если родитель есть
                if not parent.detailing_allowed:  # Если детализация родителя запрещена (нельзя генерить "детей")
                    return False  # Вернём запрет
        return True  # Если дошли до сюда - всё ок












