

'''
Тестирование работы шаблона



Добавить в объект параметр: набор регионов
'''

import pandas as pd

from Managers.ProcessesManager import ProcessesManager
from CatalogCommunication.PandasSimpleReader import PandasSimpleReader
from CatalogCommunication.ObjectsReader import ObjectReader

from AparserModules.ParserAPI.AuthorizationFunction import authorization

from TemplateGeneration.GenDataContainers import GeneratedObject, MaskValue  # Контейнеры данных
from TemplateGeneration.GeneratedSet import GeneratedSet  # Сам набор
from TemplateGeneration.Generator import TemplateGenerator  # Генератор

launch_module_name = 'Main'
PrMan = ProcessesManager(process_name='Генератор запросов',
                         session_name='Генерация для Питина',
                         main_path='E:/0_Data/Статистика шины на авто/Генерация запросов')

# ----------------------------------------------------------------------------------------------------
# Укажем параметры для работы ------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# Файл
catalog = 'E:/0_Data/Статистика шины на авто/Генерация запросов'
requests_file = 'Шаблон запросов — копия.csv'

# Параметры масок
value_marker = '_value'
mapping_marker = '_mapping'
required_masks = ['object']

# ЕСЛИ НАДО, СТАРЫЕ ВАРИАНТЫ В КОРЗИНЕ

# Регион и гео токен
#geo = {'city_id': 66, 'geo_mask_value': 'омск', 'geo_mask_mapping': 'omsk'}
#geo = {'city_id': 54, 'geo_mask_value': 'екатеринбург', 'geo_mask_mapping': 'ekaterinburg'}
#geo = {'city_id': 56, 'geo_mask_value': 'челябинск', 'geo_mask_mapping': 'chelyabinsk'}
#geo = {'city_id': 62, 'geo_mask_value': 'красноярск', 'geo_mask_mapping': 'krasnoyarsk'}
#geo = {'city_id': 35, 'geo_mask_value': 'краснодар', 'geo_mask_mapping': 'krasnodar'}

#geo = {'city_id': 65, 'geo_mask_value': 'новосибирск', 'geo_mask_mapping': 'novosibirsk'}
#geo = {'city_id': 43, 'geo_mask_value': 'казань', 'geo_mask_mapping': 'kazan'}
#geo = {'city_id': 51, 'geo_mask_value': 'самара', 'geo_mask_mapping': 'samara'}

geo = {'city_id': 225, 'geo_mask_value': 'Россия', 'geo_mask_mapping': 'no_total_mapping'}

city_id = geo['city_id']  # id города
geo_mask_value = geo['geo_mask_value']  # название города русскими буквами
geo_mask_mapping = geo['geo_mask_mapping']  # маппинг - кусок url
geo_mask_name = 'region'

# Параметры для генерации и парсинга
priority = 7
clipping_constant = 128  # минимальная базовая частота продолжения генерации
Wb_min = 64  # минимальная базовая частота для парсинга фазовой частоты при финальном парсинге


# ----------------------------------------------------------------------------------------------------
# Маппинг на url -------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
'''
Если переделаешь шаблон, то надо переделать и функцию маппинга. Преимущественно это касается "моделей", no_value и
порядка задействования масок.
'''
no_mapping = 'no_mapping'  # Это токен "без маппинга"
url_start = f'https://baza.drom.ru/{geo["geo_mask_mapping"]}/wheel/tire/'  # "страт" урла

# Модель: 'model_mapping'
mapping_columns = ['condition_mapping',
                   'size3_mapping', 'size1_mapping', 'size2_mapping',
                   'property_mapping']

def count_url(element: GeneratedObject):

    return url_start

    url = url_start  # старт урла
    values_list = element.masks_values  # значения масок
    element_masks = element.used_masks  # список использующихся масок

    # Сначала "маска" или "поисковый запрос".
    if 'model_mapping' in element_masks:  # Если маска модели занята
        for value in values_list:  # Пошли по значениям
            if value.mask == 'model_mapping':
                mark = value.value  # берём значение
                break
        # Добавим в url
        if mark.startswith('query='):  # Если это поисковая фраза
            url += '?' + mark
        else:  # Если это марка/модель
            url += mark  # просто добавми

    # Теперь остальные в порядке mapping_columns
    for mask_name in mapping_columns:  # пошли по маскам
        # Получим значение
        proc_value = False  # Детектор отсутствия значения
        for value in values_list:  # Пошли по значениям
            if value.mask == mask_name:
                proc_value = value.value  # берём значение
                break
        if proc_value is False:  # Если нет значения для маски
            continue  # Скипаем работу с маской - идём к следующей
        else:
            if '?' in url:  # Если уже есть атрибуты
                url += '&' + proc_value  # добавим "ещё один" элемент
            else:
                url += '?' + proc_value  # добавим "первый" элемент
    return url

# ----------------------------------------------------------------------------------------------------
# Преднастройка --------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
server_API, passw = authorization()

# Залогируем преднастройку
Logger = PrMan.create_logger(module_name='Main',
                             log_initialization=True)
#PrMan.CatalogsManager.add_subdirectory(name='data_dir', parent_directory=PrMan.CatalogsManager.path_data, directory=str(city_id))
data_dir = PrMan.CatalogsManager.data_catalog()

Logger.to_log(message=f'Преднастройка выполнена. Город: {city_id}. Файл: {catalog + requests_file}',
              log_type='DEBUG')
Logger.to_log(message=f'Каталог для хранения данных: {data_dir}',
              log_type='DEBUG')

# ----------------------------------------------------------------------------------------------------
# Считывание данных ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# Считаем файл
CSVreader = PandasSimpleReader(launch_module_name=launch_module_name, process_manager=PrMan)
Pattern = CSVreader.csv_import(directory=catalog, file_name=requests_file)

# Пересохраним его в каталог с данными
CSVreader.csv_export(directory=PrMan.CatalogsManager.data_catalog(), file_name=f'Шаблон запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
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

    Preparer = DirectFrequencyDTO(priority=priority)  # сделаем подгтовщик
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

    # Сделаем промежуточный экспорт, не сбрасывая нулевые фразы
    data_export(drop_zero_base=False,
                file_name=f'Набор запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
                mapp_url=False)
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
    task_id = Parser.add_task(task_dto=Preparer.get_dto(regional_data=city_id, specifier='"$query"'))
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

    return


def data_export(drop_zero_base: bool = True,
                file_name: str = None,
                mapp_url: bool = False):
    '''
    drop_zero_base - скинуть ли строки, у которых Wb = 0
    '''

    # Отдадим всё в экспорт
    # Сделаем экспорт в pandas
    export_dict = {'id': [],
                   'phrase': [],
                   'Wb': [], 'Wf': [],
                   'level': []}

    if mapp_url:  # Если будем маппить на url
        export_dict['url'] = []

    for column_name in masks:  # Добавим пустые списки для масок и значений
        export_dict[column_name + value_marker] = []  # значение
        export_dict[column_name + mapping_marker] = []  # маппинг

    phrases = DataSet.get_elements_dict()  # получим все объекты
    for phrase_id in phrases:
        # Соберём фразу
        values_list = phrases[phrase_id].masks_values
        free_masks = list(set(masks) - set(phrases[phrase_id].used_masks))  # получим список пустых масок
        phrase = ''
        for value in values_list:  # Добавим значения на непустые маски
            if isinstance(value.value, float):
                add = round(value.value)
            else:
                add = value.value

            phrase += str(add) + ' '  # Добавим в фразу
            export_dict[value.mask + value_marker].append(add)
            export_dict[value.mask + mapping_marker].append(value.mapping)

        for free_mask in free_masks:  # Добавим на пустые маски
            export_dict[free_mask + value_marker].append(None)
            export_dict[free_mask + mapping_marker].append(None)

        phrase = phrase[:len(phrase) - 1]  # дропнем последний пробел
        export_dict['id'].append(phrase_id)
        export_dict['phrase'].append(phrase)
        export_dict['level'].append(phrases[phrase_id].level)
        export_dict['Wb'].append(phrases[phrase_id].get_parameter(name='Wb'))
        exact_w = phrases[phrase_id].get_parameter(name='Wf')
        if exact_w is None:
            exact_w = -1
        export_dict['Wf'].append(exact_w)

        # Маппинг
        if mapp_url:
            try:
                page_url = count_url(element=phrases[phrase_id])  # Получим url
            except BaseException as miss:
                page_url = 'ERROR'
                Logger.to_log(message=f'Ошибка сбора url для {phrase_id} - "{phrase}": {miss}',
                              log_type='ERROR')

            export_dict['url'].append(page_url)

    # У фрейма не будет "пустых" частот
    data_frame = pd.DataFrame(export_dict)  # Конвертнём
    data_frame['Wf'] = data_frame['Wf'].fillna(-1)  # Заменим пустоты
    data_frame['Wb'] = data_frame['Wb'].fillna(-1)  # Заменим пустоты

    if drop_zero_base:  # Если дропнуть нулевые Wf
        data_frame = data_frame.loc[data_frame['Wb'] != 0]


    if file_name is None:
        file_name = f'Финальный набор запросов город {geo_mask_value} {city_id} {clipping_constant}.csv'

    CSVreader.csv_export(directory=PrMan.CatalogsManager.data_catalog(),
                         file_name=file_name,
                         file_data=data_frame)
    return

for j in range(1, len(masks)):
    print(f'\n\nШаг {j} начат')
    result = to_do(j)
    print(f'Шаг {j} закончен\n\n')
    if result == 'all_done':
        Logger.to_log(message=f'Шаг {j}: Генерация закончена')
        break

final_parsing(DataSet)  # Парсинг
data_export(drop_zero_base=True,
            file_name=f'Финальный набор запросов город {geo_mask_value} {city_id} {clipping_constant}.csv',
            mapp_url=True)  # Экспорт

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

