'''
"Дефолтные" каталоги для менеджера каталогов

'''

main_files_catalog = 'E:/0_Data/0 Main catalog/'  # Каталог для данных

data_catalogs = {'logging': {'main': 'Logging/'  # Журналы логирования
                             },
                 'data': {'main': 'Data/'  # Сохранение данных. Будет по папке каждому модулю
                          },
                 'sql': {'main': 'SQL/',  # Для баз данных
                         'failed': 'SQL/failed_requests/',  # логирование упавших запросов
                         'saved': 'SQL/saved_data/'  # логирование удаляющихся/корректирующихся данных
                         },
                 'emergency_save': {'main': 'Emergency_save/'}  # каталог для экстренного сохранения
                 }