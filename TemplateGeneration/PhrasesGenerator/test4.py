


import pandas as pd
import numpy as np

from Managers.ProcessesManager import ProcessesManager
from CatalogCommunication.PandasSimpleReader import PandasSimpleReader

launch_module_name = 'ЗАЕБАЛО ПИЗДЕЦ БЛЯТЬ СУКА НАХУЙ'
catalog = 'E:/0_Data/Drom 3/11 Другие города/1 Генерация/Бэк'
file_name = 'Финальный набор запросов город волгоград 38 12.csv'
region = 'volgograd'
'''
#geo = {'city_id': 56, 'geo_mask_value': 'челябинск', 'geo_mask_mapping': 'chelyabinsk'}

geo = {'city_id': 51, 'geo_mask_value': 'самара', 'geo_mask_mapping': 'samara'}
'''

PrMan = ProcessesManager(process_name='Конвертация csv', subdirectory='Testing')
CSVreader = PandasSimpleReader(launch_module_name=launch_module_name, process_manager=PrMan)
File_data = CSVreader.csv_import(directory=catalog, file_name=file_name)


columns = ['Wb', 'Wf']
for el in columns:
    File_data[el] = File_data[el].fillna(-1)
    File_data[el] = File_data[el].astype(int)

# Дропнем пустые
File_data = File_data.loc[File_data['Wb'] != 0]
File_data['url'] = None

# Модель: 'model_mapping'
mapping_columns = ['condition_mapping',
                   'size3_mapping', 'size1_mapping', 'size2_mapping',
                   'property_mapping']

def count_url(phrase_id: int):

    url = f'https://baza.drom.ru/{region}/wheel/tire/'  # "страт" урла

    # Пробуем добавить "модель"
    mark = File_data.loc[phrase_id, 'model_mapping']
    if not mark is np.nan:  # Если не пустое
        if mark.startswith('query='):  # Если это поисковая фраза
            url += '?' + mark
        else:  # Если это марка/модель
            url += mark  # просто добавми

    # Теперь остальные в порядке mapping_columns
    for mask_name in mapping_columns:  # пошли по маскам
        if not File_data.loc[phrase_id, mask_name] is np.nan:  # Если не пустое
            if '?' in url:  # Если уже есть атрибуты
                url += '&' + File_data.loc[phrase_id, mask_name]  # добавим "ещё один" элемент
            else:
                url += '?' + File_data.loc[phrase_id, mask_name]  # добавим "первый" элемент

    return url

for id in File_data.index.tolist():  # пошли по данным
    File_data.at[id, 'url'] = count_url(id)
CSVreader.csv_export(file_name=file_name, directory=catalog,
                     file_data=File_data)