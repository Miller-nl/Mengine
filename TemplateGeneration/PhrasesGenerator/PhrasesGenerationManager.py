'''
Развести менеджеров на две категории: первый - аналог текущего Gen test: для работы с одним регионом.
Второй - MultiRegions: для работы с набором регионов. Разница в том, что:
    - парсинг будет вестись не в одно задание (как сейчас), а по заданию на каждый указанный регион
    - запрсоы в парсинг будут уходить как: без региона - во все парсинг задания, с регионом - только в своё задание
    - у сгенеренных объектов появится набор статистик по регионам
    - у функции оценки изменится алгоритм работы

    Также изменятся и отчёты.

Так как "мультирегионы" будут обобщением текущео Gen test, который джёт рефа, то рефа не будет. Позже будет написан
    объект сразу для работы с набором регионов.

Вопрос ещё вот какой - какие модернизации "сгенерированных" объектов надо будет сделать для хранения данных статистики?
    Скорее всего, объект получит SetContainer, в котором будут объекты DirectParsingResult, а в качестве индекса
    выступит индекс региона. Причём это будет сделано поверх текущего словаря с параметрами - отдельно от него.
    А вот хранение "списка регионов" будет непосредственно в менеджере.

Экспорт/импорт будет в два формата:
    1. В CSV в формате: id, запрос, параметры, маски со значениями и маппингом;
    2. В pickl формат.
Предпочтительно сохранение в pickl для будущей работы. Но "в долгосрочку" надо хранить в CSV, т.к. pickle не подгрузится.









Добавить в объект параметр: набор регионов, по которым будем парсить стату. И "агрегированно"/"сепарированно" - метод
парсинга и оценки статы. Скорее всего это будет "сепарированно". И как бы генерация будет вестись "дальше и дальше",
но чекаться данные будут только по тем городам, в которых "генерация продолжается". То есть по сути это объединение
нескольких процессов в один.
(то есть - парсер надо вынести за менеджер или тпиа того. Но подготовка к парсингу будет точно отдельным процессом)
В противном случае - при агрегированной генерации, работа будет вестись как "с одним регионом".

В результате сепарированной генерации мы получим набор запросов, сопроводжённый статистикой по регионам. И нам надо будет
spliter и combiner для наборов запросов.


Тут будет "менеджер генерации", в котором будет всё происходить.

При этом именно тут будет и граф, и набор
from TemplateGeneration.DataContainers import GeneratedSet  # Контейнеры данных



Порядок:
    1. Получить шаблон
    2. Получить имеющиеся комбинации с параметрами. Создать объекты генерации и добавить их в набор

    3. Настроить генератор, указать функцию для "продолжения генерации" (ранжировщик)

    4. Выполнить шаг генерации

    5. Запросить статистику по новым объектам  (надо ли сгенеренному объекту добавить параметр "новый", а сету
        функцию: получить объекты(готовые=да/нет) ? Думаю, да)
    6. Подождать статистику
    7. Занести статистику на новые объекты с шага 4

    8. Перейти на шаг 4


Нейросети и т.п. тут же - в менеджере развернуть.



Кроме того будет дополнительно создан отдельный объект, который будет администрировать весь процесс: от импорта
    шаблона и имеющихся данных, до экспорта данных в нужном виде.

    Дополнительные комментарии:
        1. Информация о совместности/несовместности и подобных параметрах будет храниться у соответствующих
            сгенерированных комбинаций на словаре score. Этого будет достаточно.
        2. У генератора есть "маска объекта" (object_mask) -  это сам объект, к которому относится запрос: название
            и варианты названий. Маска объекта не может быть пустой(!). Кроме того, отдельно есть "обязательные"
            маски, логика использования которых такая же, как и у "маски объекта" (они не могут быть пустыми).
            Смысл в "обязательных масках" в том, чтобы генерировать кастомные части набора. Например для "шин" это
            могут быть сезонные шины или шины какой-либо марки.
            В случае, если нам нужны только полные комбинации, следует указать в качестве "обязательных масок" все
            маски GeneratedSet.masks_pattern .
        3. Лучше не ставить все маски как "обязятельные", т.к. тогда в генераторе воспроизведутся ВСЕ комбинации и
            это может забить память несмотря на организацию данных. Желательно вместо этого "забрать только объекты
            максимальной длины".
        4. Функция, разрешающая/запрещающая комбинации для генерации находится в GeneratedSet, а не тут.
            Причина такого решения проста - все данные о наборе содержатся в GeneratedSet, и сам генератор
            ничего из них не знает и, вообще говоря, не должен знать.


    У генератора будет четыре режима работы:
        1. Генерация с текущего положения до максимально разрешённого уровня.
            Для генерации потребуется "минимальный порог", который разрешит использование имеющихся комбинаций в
            генерации, и "максимальное количество использованных масок".
            Желательно сопроводить все запросы каким-то счётом, который наивно характеризовал бы количество трафика,
            которое может идти через комбинацию, чтобы понимать, какие комбинации парсить первее всего, а какие
            парсить последними. Однако исключить из парсинга комбинации при такой схеме не получится.
            Это аналог генерации, которая использовалась ранее: когда получена статистика по значениям масок, попарным
            комбинациям формата "основное слово + доп значение" и тройным комбинациям - где два доп значения.

        2. Пошаговая генерация с константой.
            Для генерации задайтся константа - минимальный порог. Разница с первым режимом в том, что генерация
            выполняется не в один заход, а циклами: шаг генерации - парсинг статистики. При этом комбинации,
            которые при парсинге получили частоту меньше константы, исключаются из дальнейшей работы.

            Это более оптимальный вариант, т.к. заведомо нулевые комбинации не будут давать более длинных вариантов
            себя, которых может быть очень и очень много.

        3. Пошаговая генерация с убывающей константой
            Так как с увеличением длины запроса частота падает преимущественно экспоненциально, то получается, что
            одна и та же константа не очень нам подойдёт при генерации длинных комбинаций. Поэтому возможно ввести
            функцию, которая будет выдавать константу "минимального порога", зависящую от длины комбинации.
            Смысл зависимости от длины комбинации (её уровня) в том, чтобы продолжать генерацию только по наиболее
            жирным запросам.

            Кроме того, константа может зависеть от "шага". То есть, чем больше выполнено шагов генерации, тем ниже
            может быть константа. Для того, чтобы добирать даже мелкий трафик - по крайне мере пытаться его добрать.

        4. Генерация с нейросетью
            Пока не определено


'''

# Генератор и GeneratedSet встречаются только(!) тут!
from Managers.ProcessesManager import ProcessesManager

# Модули для парсинга

#  Модули для обработки
from TemplateGeneration.GeneratedSet import GeneratedSet  # Сам набор

# Модули для API


clipping_constant = 12  # минимальная базовая частота продолжения генерации
Wb_min = 6  # минимальная базовая частота для парсинга фазовой частоты при финальном парсинге

class GenerationManager:



    def __init__(self,masks_pattern: list, generated_set: GeneratedSet,
                 process_manager: ProcessesManager, launch_module_name: str = None,
                 clipping_constant: int = 12,
                 ):
        '''

        + настройка работы с "уровнем"  и "шагом ненерации". И настройка, по которой можно использовать в экспорте
            только те комбинации, в которых ВСЕ маски имеют непустые значения.

        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер процесса, который руководит запуском
        :param process_manager: менеджер процесса, который руководит запуском
        :param generated_set: объект - набор сгенерированных комбинаций. Чистый или преднастроенный, но готовый.
        :param clipping_constant: минимальная базовая частота, разрешающая продолжение генерации
        '''

        # Установим логер
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name,
                                                      log_initialization=True)
        self.__to_log = self.__Logger.to_log

        self.__GeneratedSet = GeneratedSet(launch_module_name=launch_module_name, process_manager=process_manager,
                                           masks_pattern=masks_pattern)









'''
GeneratedSet(launch_module_name=launch_module_name, process_manager=process_manager,
                                           masks_pattern=masks_pattern)
'''



'''
 # Решим вопрос с графом
        if load_graph:  # Если надо подгрузить граф
            identification_key = IdentificationKey(name=graph_name, type=DirectedGraph)
            self.__DirectedGraph = DirectedGraph(launch_module_name=launch_module_name,
                                                 process_manager=process_manager,
                                                 identification_key=identification_key)  # Подгрузим
        else:
            self.__DirectedGraph = None  # Если граф подгружать не нужно, то поставим None
'''



'''

    # ------------------------------------------------------------------------------------------------
    # Функция рассчёта параметров --------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    ''
    Функция оценки:
    Подготовщие получает словарь с именами параметров, которые надо запросить у элемента. Это важно - именно словарь (или список)
    и названия в точности совпадают с названиями этих штук у параметра. После чего функция подготавливает словарь с
    нужными значениями и передаёт их в функцию оценки, откуда получает "циферку" или bool
    ''


    @staticmethod
    def _area_counter(values_list: list) -> float:
        ''
        Смысл функции - подсчёт "площади" под ломанной при нормировании на участок [0,1].
        :param values_list: список int или float значений
        :return: коэффициент "площади" под ломанной, на участке [0,1], с равномерным расположением точек. Причём
            нулевая точка лежит имеет x=0, а последняя x=1. Y = значению в списке.
        ''
        values_list.sort()  # отсортируем список
        if len(values_list) == 1:  # Если элемент один
            return values_list[0]
        else:  # Если более одного
            K = 1/(len(values_list)-1)  # "ширина" участков
            S = 0
            for j in range(1, len(values_list)):  # Пошли соберём площадь под ломанной
                S += K * (values_list[j] + (values_list[j-1] - values_list[j])/2)  # ширина * высоту участков
            return S





'''





'''
Тестирование работы шаблона



Добавить в объект параметр: набор регионов
'''

import pandas as pd

from Managers.ProcessesManager import ProcessesManager

launch_module_name = 'Main'
PrMan = ProcessesManager(process_name='Генератор запросов')

# ----------------------------------------------------------------------------------------------------
# Укажем параметры для работы ------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# Файл
catalog = 'E:/0_Data/Drom 3/11 Другие города'
requests_file = 'Шаблон запросов.csv'

# Параметры масок
value_marker = '_value'
mapping_marker = '_mapping'
required_masks = ['object']

# ЕСЛИ НАДО, СТАРЫЕ ВАРИАНТЫ В КОРЗИНЕ

# Регион и гео токен
geo = {'city_id': 66, 'geo_mask_value': 'омск', 'geo_mask_mapping': 'omsk'}
#geo = {'city_id': 54, 'geo_mask_value': 'екатеринбург', 'geo_mask_mapping': 'ekaterinburg'}
#geo = {'city_id': 56, 'geo_mask_value': 'челябинск', 'geo_mask_mapping': 'chelyabinsk'}

city_id = geo['city_id']  # id города
geo_mask_value = geo['geo_mask_value']  # название города русскими буквами
geo_mask_mapping = geo['geo_mask_mapping']  # маппинг - кусок url
geo_mask_name = 'region'


# ----------------------------------------------------------------------------------------------------
# Преднастройка --------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
from AparserModules.ParserAPI.AuthorizationFunction import authorization
server_API, passw = authorization()


# Залогируем преднастройку
Logger = PrMan.create_logger(module_name='Main',
                             log_initialization=True)
#PrMan.CatalogsManager.add_subdirectory(name='data_dir', parent_directory=PrMan.CatalogsManager.path_data, subdirectory=str(city_id))
data_dir = PrMan.CatalogsManager.path_data

Logger.to_log(message=f'Преднастройка выполнена. Город: {city_id}. Файл: {catalog + requests_file}',
              log_type='DEBUG')
Logger.to_log(message=f'Каталог для хранения данных: {data_dir}',
              log_type='DEBUG')

# ----------------------------------------------------------------------------------------------------
# Считывание данных ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# Считаем файл
from CatalogCommunication.PandasSimpleReader import PandasSimpleReader
CSVreader = PandasSimpleReader(launch_module_name=launch_module_name, process_manager=PrMan)
Pattern = CSVreader.csv_import(directory=catalog, file_name=requests_file)

# Пересохраним его в каталог с данными
CSVreader.csv_export(directory=PrMan.CatalogsManager.path_data, file_name=f'Шаблон запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
                     file_data=Pattern)
Logger.to_log(message=f'Файл с шаблоном считан и пересохранён в каталог {data_dir + "Pattern.csv"}',
              log_type='DEBUG')

# Выделим список нужных масок
masks = []
for column in Pattern.columns:
    if value_marker in column:
        masks.append(column.replace(value_marker, ''))  # добавим "чистое" название
# добавим в шаблон маску региона
masks.append(geo_mask_name)

Logger.to_log(message=f'Маски выделены',
              log_type='DEBUG')

# ----------------------------------------------------------------------------------------------------
# Преднастройка набора -------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

from TemplateGeneration.GenDataContainers import MaskValue  # Контейнеры данных
from TemplateGeneration.GeneratedSet import GeneratedSet  # Сам набор
from TemplateGeneration.Generator import TemplateGenerator  # Генератор


# Создадим "набор данных" со списком - шаблоном
DataSet = GeneratedSet(launch_module_name=launch_module_name, process_manager=PrMan,
                       masks_pattern=masks)

# Для всех уникальных значений создадим объект и отдадим в сет
for mask_name in masks:
    if mask_name == geo_mask_name:  #маска гео скипается
        continue

    unique = pd.unique(Pattern[mask_name + value_marker])  # Получим уникальные значение
    for value in unique:  # пошли по значениям
        if str(value) == 'nan':  # если нормальные значения кончились
            break  # кончаем
        mapping = Pattern.loc[Pattern[mask_name + value_marker] == value][mask_name + mapping_marker].tolist()[0]
        try:  # интнем
            value = int(value)
        except BaseException:
            pass
        new_value = MaskValue(mask=mask_name, value=value, mapping=mapping)

        # Отдадим в сет
        DataSet.add_mask_token(mask_value=new_value)

        DataSet.fast_combination_check(masks_values=[new_value]).detailing_allowed = True  # Поставим, что можно генерить

# Добавим гео токен
new_geo_value = MaskValue(mask=geo_mask_name, value=geo_mask_value, mapping=geo_mask_mapping)
DataSet.add_mask_token(mask_value=new_geo_value)
DataSet.fast_combination_check(masks_values=[new_geo_value]).detailing_allowed = True  # Поставим, что можно генерить

Logger.to_log(message=f'Токены выделены и переданы в сет. Набор готов к генерации',
              log_type='DEBUG')

# ----------------------------------------------------------------------------------------------------
# Циклическая обработка ------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
from CatalogCommunication.ObjectsReader import ObjectReader
ObReader = ObjectReader(launch_module_name=launch_module_name, process_manager=PrMan, default_directory=data_dir)
sets_name = str(city_id) + ' GeneratedSet'
# Сохраним сет
#ObReader.save_pickle_object(file_name=sets_name + ' zero', file_data=DataSet)


# ---------------------------------------------------------------------------------------------------
# Функции ------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

def generators_step(ProcessingDataSet):
    # подгрузим сет данных
    Logger.to_log(message=f'generators_step: сет считан',
                  log_type='DEBUG')

    # Создадим генератор
    Generator = TemplateGenerator(launch_module_name=launch_module_name, process_manager=PrMan,
                                  generated_set=ProcessingDataSet,
                                  required_masks=required_masks)  # Маску можно не отдавать, она дёрнется с сета
    Logger.to_log(message=f'generators_step: генератор создан',
                  log_type='DEBUG')

    # Выполним шаг генерации

    get_elements_dict = ProcessingDataSet.get_elements_dict(detailing_allowed=True)  # берём только те элементы, которые можно расшить
    gen_dict = {}  # {parent_id: {mask: list_of_elements}}
    for el_id in get_elements_dict.keys():  # Пошли по списку всех элементов
        gen_dict[el_id] = Generator.object_detailing(parent_object=get_elements_dict[el_id])

        p_phrase = ''
        for Value in get_elements_dict[el_id].masks_values:
            p_phrase += str(Value.value) + ' '
    Logger.to_log(message=f'generators_step: шаг генерации выполнен',
                  log_type='DEBUG')
    return ProcessingDataSet

# Подготовим данные к парсингу
# У ТЕХ, КТО ЖДЁТ ПАРСИНГА: name='parsing', value=True
# Нас интересует только базовая частота

from AparserModules.ParserAPI.AparserAPI import Aparser
Parser = Aparser(password=passw, server_address=server_API,
                 launch_module_name=launch_module_name, process_manager=PrMan)

from AparserModules.Parsers.YandexDirectFrequency.DirectPreparer import DirectFrequencyDTO  # Импорт предподготовщиков заданий

def add_task(ProcessingDataSet):

    parsing_phrases = ProcessingDataSet.get_elements_dict(post_processed=False)  # берём неподготовленные элементы
    # словарь вида {id: element}
    # Конвертнём в Series для общности

    Phrases_series = pd.Series()
    for phrase_id in parsing_phrases.keys():  # пошли по индексам
        values_list = parsing_phrases[phrase_id].masks_values
        phrase = ''
        for value in values_list:  # пошли по значениями
            if isinstance(value.value, float):
                add = round(value.value)
            else:
                add = value.value
            phrase += str(add) + ' '
        phrase = phrase[:len(phrase) - 1]  # дропнем последний пробел
        Phrases_series.at[phrase_id] = phrase  # отдадим данные в Series

    if Phrases_series.shape[0] == 0:  # Если фраз нет
        Logger.to_log(message=f'Нет фраз для парсинга',
                      log_type='ERROR')
        return 'all_done'

    Preparer = DirectFrequencyDTO()  # сделаем подгтовщик
    Preparer.add_phrases(queries=Phrases_series)
    task_id = Parser.add_task(task_dto=Preparer.get_dto(regional_data=city_id))
    Logger.to_log(message=f'Результат постановки в очередь парсинга базовой частоты {task_id}')

    return task_id # вернём индекс задания


def get_parsed_data(tasks_id):
    stat_dict = Parser.get_json_task_file(task_id=tasks_id)
    return stat_dict

def estimate(ProcessingDataSet: GeneratedSet, stat_list: list):
    for stat_bject in stat_list:  # пошли по списку
        try:
            # Получим id
            id_part = stat_bject['element_id']
            id_part = int(id_part)
            Wb = stat_bject['views']
            if Wb == None:  # Если базовая частота не получена
                Wb = clipping_constant
            GenObject = ProcessingDataSet.get_generated_object(element_id=id_part)
            GenObject.set_parameter(name='Wb', value=Wb)
            if Wb < clipping_constant:  # Если элемент не проходит порог
                GenObject.detailing_allowed = False
            else:  # Если проходит
                GenObject.detailing_allowed = True

            GenObject.post_processed = True  # обработали
        except BaseException as miss:
            Logger.to_log(message=f'Ошибка обработки данных от парсера "{miss}" для DTO: {stat_bject}',
                          log_type='ERROR')
    return


def save_set_data():
    # Сделаем экспорт в pandas
    export_frame = pd.DataFrame()
    # Заведём нужные колонки
    export_frame['phrase'] = None  # фраза
    export_frame['Wb'] = None  # базовая частота
    export_frame['level'] = 0  # уровень

    for column_name in masks:  # Добавим "всё для масок"
        export_frame[column_name + value_marker] = None  # значение
        export_frame[column_name + mapping_marker] = None  # маппинг

    phrases = DataSet.get_elements_dict()  # получим все объекты
    for phrase_id in phrases:
        # Соберём фразу
        values_list = phrases[phrase_id].masks_values
        phrase = ''
        for value in values_list:  # пошли по значениями
            if isinstance(value.value, float):
                add = round(value.value)
            else:
                add = value.value
            export_frame.at[phrase_id, value.mask + value_marker] = add  # добавим значение маски
            export_frame.at[phrase_id, value.mask + mapping_marker] = value.mapping  # добавим маппинг значения

            phrase += str(add) + ' '
        phrase = phrase[:len(phrase) - 1]  # дропнем последний пробел
        export_frame.at[phrase_id, 'phrase'] = phrase
        export_frame.at[phrase_id, 'level'] = phrases[phrase_id].level
        export_frame.at[phrase_id, 'Wb'] = phrases[phrase_id].get_parameter(name='Wb')

    CSVreader.csv_export(directory=PrMan.CatalogsManager.path_data, file_name=f'Набор запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
                         file_data=export_frame, with_index=True)
    return

def to_do(step):
    print('Начат шаг генерации')
    Logger.to_log(message=f'Шаг {step}: начат')
    ProcessingDataSet = generators_step(DataSet)  # Сделаем генерацию
    print('Шаг генерации сделан')
    Logger.to_log(message=f'Шаг {step}: сделан')
    #ObReader.save_pickle_object(file_name=sets_name, file_data=ProcessingDataSet)

    task_id = add_task(ProcessingDataSet)  # закинем в парсинг

    if task_id is None:
        print('Ошибка передачи данных в парсер отданых в парсер')
        Logger.to_log(message=f'Шаг {step}: Ошибка передачи данных в парсер отданых в парсер')
        return

    if task_id == 'all_done':
        print('Новых элементов не получено. Генерация закончена')
        Logger.to_log(message=f'Шаг {step}: Новых элементов не получено. Генерация закончена')
        return 'all_done'

    print('Данные отданы в парсер')
    Logger.to_log(message=f'Шаг {step}: Данные отданы в парсер. Задание {task_id}')
    stat_dict = get_parsed_data(task_id)
    print('Стата от парсера получена')
    Logger.to_log(message=f'Шаг {step}: Стата от парсера получена')
    estimate(ProcessingDataSet, stat_dict)
    print('Оценка сделана')
    Logger.to_log(message=f'Шаг {step}: Оценка сделана')
    #ObReader.save_pickle_object(file_name=sets_name, file_data=copy.deepcopy(ProcessingDataSet))

    save_set_data()
    return None

def final_parsing(ProcessingDataSet):
    # Снимем стату
    parsing_phrases = ProcessingDataSet.get_elements_dict()  # берём все элементы
    # словарь вида {id: element}
    # Конвертнём в Series для общности
    Phrases_series = pd.Series()
    for phrase_id in parsing_phrases.keys():  # пошли по индексам
        if parsing_phrases[phrase_id].get_parameter(name='Wb') < Wb_min:  # Если частота базовая слишком мала
            continue

        # Сформируем фразу
        values_list = parsing_phrases[phrase_id].masks_values
        phrase = ''
        for value in values_list:  # пошли по значениями
            if isinstance(value.value, float):
                add = round(value.value)
            else:
                add = value.value
            phrase += str(add) + ' '
        phrase = phrase[:len(phrase) - 1]  # дропнем последний пробел
        Phrases_series.at[phrase_id] = phrase  # отдадим данные в Series

    # Подготовим DTO
    Preparer = DirectFrequencyDTO()  # сделаем подгтовщик
    Preparer.add_phrases(queries=Phrases_series)
    task_id = Parser.add_task(task_dto=Preparer.get_dto(regional_data=city_id, specifier_left='"', specifier_right='"'))
    Logger.to_log(message=f'Результат постановки в очередь парсинга базовой частоты {task_id}')

    if task_id is None:
        print(f'final_parsing Ошибка - task_id is None')
        return

    # Получим результат
    stat_list = Parser.get_json_task_file(task_id=task_id)

    if stat_list is None:
        print(f'final_parsing Ошибка - stat_list is None')
        return

    # Снимем данные статы
    for stat_object in stat_list:  # пошли по списку
        try:
            # Получим id
            id_part = stat_object['element_id']
            id_part = int(id_part)
            Wf = stat_object['views']
            if Wf == None:  # Если базовая частота не получена
                Wf = -1
            GenObject = ProcessingDataSet.get_generated_object(element_id=id_part)
            GenObject.set_parameter(name='Wf', value=Wf)
        except BaseException as miss:
            Logger.to_log(message=f'Ошибка обработки данных от парсера "{miss}" для DTO: {stat_object}',
                          log_type='ERROR')


    # Отдадим всё в экспорт
    # Сделаем экспорт в pandas
    if True:  # УБЕРИ ПОТОМ
        export_frame = pd.DataFrame()
        # Заведём нужные колонки
        export_frame['phrase'] = None  # фраза
        export_frame['Wb'] = -1  # базовая частота
        export_frame['Wf'] = -1  # базовая частота
        export_frame['level'] = 0  # уровень

        for column_name in masks:  # Добавим "всё для масок"
            export_frame[column_name + value_marker] = None  # значение
            export_frame[column_name + mapping_marker] = None  # маппинг

        phrases = DataSet.get_elements_dict()  # получим все объекты
        for phrase_id in phrases:
            # Соберём фразу
            values_list = phrases[phrase_id].masks_values
            phrase = ''
            for value in values_list:  # пошли по значениями
                if isinstance(value.value, float):
                    add = round(value.value)
                else:
                    add = value.value
                export_frame.at[phrase_id, value.mask + value_marker] = add  # добавим значение маски
                export_frame.at[phrase_id, value.mask + mapping_marker] = value.mapping  # добавим маппинг значения

                phrase += str(add) + ' '
            phrase = phrase[:len(phrase) - 1]  # дропнем последний пробел
            export_frame.at[phrase_id, 'phrase'] = phrase
            export_frame.at[phrase_id, 'level'] = phrases[phrase_id].level
            export_frame.at[phrase_id, 'Wb'] = phrases[phrase_id].get_parameter(name='Wb')
            export_frame.at[phrase_id, 'Wf'] = phrases[phrase_id].get_parameter(name='Wf')

    export_frame['Wb'] = export_frame['Wb'] .astype(int)
    export_frame['Wf'] = export_frame['Wf'].astype(int)

    CSVreader.csv_export(directory=PrMan.CatalogsManager.path_data,
                            file_name=f'Финальный Набор запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
                            file_data=export_frame, with_index=True)

for j in range(1, len(masks)):
    print(f'\n\nШаг {j} начат')
    result = to_do(j)
    print(f'Шаг {j} закончен\n\n')
    if result == 'all_done':
        Logger.to_log(message=f'Шаг {j}: Генерация закончена')
        break

final_parsing(DataSet)






#'''
def show(level):
    data_set = DataSet.get_elements_dict(level=level)
    print(f'\n\n\nЭлементы длины {level}')
    for el_id in data_set.keys():
        values = data_set[el_id].masks_values
        for j in range(0, len(values)):
            values[j] = values[j].value
        print(f'{data_set[el_id].element_id}: {values}. Дальнейшая генерация: {data_set[el_id].detailing_allowed}')
    print('\n\n\n')

#show(3)
#'''
# DataSet.fast_combination_check(masks_values=DataSet.)







