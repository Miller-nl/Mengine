''' готово/отлажено
# ----------------------------------------------------------------------------------------------------
# ObjectsReader --------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
Задача объекта - загружать и сохранять файлы в каталог. Делаться это будет с помощью модуля pickle.

Параметры init
    launch_module_name: str - имя вызывающего модуля - для логирования.
    process_manager: ProcessesManager - менеджер текущего процесса
    default_directory: str - дефолтный каталог, с которым будет взаимодействовать модуль в случае, если в функциях
        не будет явно указана директория.

Доступные методы:
    # Сохранение и подгрузка произвольных объектов
        save_pickle_object(directory: str, file_name: str, file_data: object, name_shift: bool = True) -> bool. Функция сохраняет
            объект в каталог и возвращает статус сохранения.

        load_pickle_object(directory: str, file_name: str) -> object. Функция загружает объект. Если успешно - возвращает объект,
            иначе вернёт None (ни кто ж не будет сохрнять None в файл).

    # Сохранение и подгрузка объектов JSON
        save_json_object(file_data: str or list or dict, file_name: str, directory: str = None, name_shift: bool = True) -> bool
            Функция сохраняет данные в указанный файл формата json. Возвращает успешность сохранения.
        load_json_object(self, file_name: str, directory: str = None, encoding: str = 'utf-8') -> dict or list or None - функция
            пытается загрузить json файл по указанном упути. В случае успеха вохвращает словарь или список,
            в случае провала - None.

self параметры
    __Logger - логер
    __to_log - функция логирования
    __default_directory - дефолтный каталог

Добавить потом:
    функцию экстренного сохранения объектов процесса.
'''

import os as os  # Для работы с каталогом
import pickle  # Для сохранения/подгрузки
import json

from Managers import ProcessesManager

# объект для чтения/сохранения
class ObjectReader:

    def __init__(self, process_manager: ProcessesManager, launch_module_name: str = None,
                 default_directory: str = None):
        '''
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер текущего процесса
        :param default_directory: каталог "по умолчанию"
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name)
        self.__to_log = self.__Logger.to_log

        self.__default_directory = default_directory


    # ----------------------------------------------------------------------------------------------------
    # Сохранение и подгрузка произвольных объектов -------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------
    # сохранение объекта в директорию
    def save_pickle_object(self,
                           file_data: object,
                           file_name: str, directory: str = None,
                           name_shift: bool = True) -> bool:
        '''
        Функция сохраняет объект в каталог
        :param directory: каталог.
        :param file_name: имя интересующего файла.
        :param file_data: данные, которые должны быть сохранены
        :param name_shift: разрешено ли изменение имени в случае, если искомое занято.
        :return: status - bool.
        '''

        if directory is None:  # Если директория не указана
            if not self.__default_directory is None:  # Если указан дефолтный каталог
                directory = self.__default_directory  # Берём дефолтное значение
            else:  # Если не указан каталог и дефолтного значения нет
                self.__to_log(message=(f'save_pickle_object: Экспорт файла {file_name} провален. ' +
                                       'Не указана директория для экспорта'),
                              log_type='ERROR')
                return False  # Иначе - вернём ошибку

        # Првоерим директорию
        if not os.access(directory, mode=os.F_OK):  # Если директории нет
            os.makedirs(directory)  # Создадим
        directory += "/"

        # Срежем расширение, если оно есть
        file_name = file_name.replace('.pickle', '')

        add = ''  # Добавка к имени файла, если исходное имя занято
        count = 0  # счётчик для "сдвига" имени файла
        while True:
            if os.access(directory + file_name + add + '.pickle', mode=os.F_OK):  # Если имя занято
                # Сдвинем счётчик
                count += 1
                # Скорректируем добавку
                add = '(' + str(count) + ')'
            else:  # Если варианта "directory+file_name+add+'.pickle'" нет
                break  # закончим подбор сдвига

        if not name_shift and count != 0:  # Если имя было занято, а сдвиг не разрешён
            self.__to_log(message=('save_pickle_object: Экспорт файла ' + directory + file_name + '.pickle' +
                                   ' будет выполнен в существующий файл! Имя занято, коррекция имени запрещена.'),
                          log_type='WARNING')
            add = ''  # Скорректируем добавку (будем писать в искомый файл)

        try:  # Экспортнём
            with open(directory + file_name + '.pickle', 'wb') as f:
                pickle.dump(file_data, f, pickle.HIGHEST_PROTOCOL)
            self.__to_log(message=('save_pickle_object: Экспорт файла ' + directory + file_name + add + '.pickle' +
                                   ' выполнен успешно'),
                          log_type='DEBUG')
            return True
        except BaseException as miss:
            self.__to_log(message=('save_pickle_object: Экспорт файла ' + directory + file_name + add + '.pickle' +
                                   ' провален. Ошибка: ' + str(miss)),
                          log_type='ERROR')
            return False

    # загрузка объекта из директории
    def load_pickle_object(self,
                           file_name: str, directory: str = None) -> object:
        '''
        Функция сохраняет переданный объект в каталог.
        :param directory: каталог.
        :param file_name: имя файла.
        :return: считанный объект или None, если считывание провалено
        '''

        self.__to_log(message=(f'load_pickle_object: Запрошено считывание файла directory: {directory}, ' +
                               f'file_name: {file_name}'),
                      log_type='DEBUG')

        if directory is None:  # Если директория не указана
            if not self.__default_directory is None:  # Если указан дефолтный каталог
                directory = self.__default_directory  # Берём дефолтное значение
            else:  # Если не указан каталог и дефолтного значения нет
                self.__to_log(message=(f'load_pickle_object: Импорт файла {file_name} провален. ' +
                                       'Не указана директория для экспорта'),
                              log_type='ERROR')
                return False  # Иначе - вернём ошибку

        if not directory.endswith('/'):  # если в конце директории нет слеша, поставим его
            directory = directory + '/'

        # Срежем расширение, если оно есть
        file_name = file_name.replace('.pickle', '')

        if not os.access(directory + file_name + '.pickle', mode=os.F_OK):  # проверим существование файла директории
            # если файла нет
            self.__to_log(message=('load_pickle_object: Ошибка доступак файлу ' + directory + file_name + '.pickle'),
                          log_type='ERROR')
            return None  # результат - не считан файл

        # Пробуем считать файл
        try:
            with open(directory + file_name + '.pickle', 'rb') as f:
                result = pickle.load(f)
            self.__to_log(message=('load_pickle_object: Импорт файла ' + directory + file_name + '.pickle' +
                                   ' выполнен успешно'),
                          log_type='DEBUG')
            return result  # Если считали у спешно

        except BaseException as miss:
            self.__to_log(message=('load_pickle_object: Ошибка считывания файла ' + directory + file_name + '.pickle' +
                                   ': ' + str(miss)),
                          log_type='ERROR')
            return None  # Результат считывания - None

    # ----------------------------------------------------------------------------------------------------
    # Сохранение и подгрузка объектов JSON ---------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    def save_json_object(self,
                         file_data: str or dict or list,
                         file_name: str, directory: str = None,
                         name_shift: bool = True) -> bool:
        '''
        Функция сохраняет объект в каталог
        :param directory: каталог.
        :param file_name: имя интересующего файла.
        :param file_data: данные, которые должны быть сохранены
        :param name_shift: разрешено ли изменение имени в случае, если искомое занято.
        :return: status - bool.
        '''

        if directory is None:  # Если директория не указана
            if not self.__default_directory is None:  # Если указан дефолтный каталог
                directory = self.__default_directory  # Берём дефолтное значение
            else:  # Если не указан каталог и дефолтного значения нет
                self.__to_log(message=(f'save_json_object: Экспорт файла {file_name} '
                                       ' провален. Не указана директория для экспорта'),
                              log_type='ERROR')
                return False  # Иначе - вернём ошибку

        # Првоерим директорию
        if not os.access(directory, mode=os.F_OK):  # Если директории нет
            os.makedirs(directory)  # Создадим
        directory += "/"

        # Срежем расширение, если оно есть
        file_name = file_name.replace('.json', '')

        add = ''  # Добавка к имени файла, если исходное имя занято
        count = 0  # счётчик для "сдвига" имени файла
        while True:
            if os.access(directory + file_name + add + '.json', mode=os.F_OK):  # Если имя занято
                # Сдвинем счётчик
                count += 1
                # Скорректируем добавку
                add = '(' + str(count) + ')'
            else:  # Если варианта "directory+file_name+add+'.pickle'" нет
                break  # закончим подбор сдвига

        if not name_shift and count != 0:  # Если имя было занято, а сдвиг не разрешён
            self.__to_log(message=('save_json_object: Экспорт файла ' + directory + file_name + '.json' +
                                   ' будет выполнен в существующий файл! Имя занято, коррекция имени запрещена.'),
                          log_type='WARNING')
            add = ''  # Скорректируем добавку (будем писать в искомый файл)

        try:  # Экспортнём
            with open(directory + file_name + '.json', 'w', encoding='utf-8') as f:
                if isinstance(file_data, str):  # Если подана строка
                    json.dump(json.loads(file_data), f)  # Сделаем из строки json
                elif isinstance(file_data, dict) or isinstance(file_data, list):  # Если подан объект
                    json.dump(file_data, f)

                self.__to_log(message=(f'save_json_object: Экспорт файла {directory + file_name + add}.pickle ' +
                                       'выполнен успешно'),
                              log_type='DEBUG')
                return True

        except BaseException as miss:
            self.__to_log(message=(f'save_json_object: Экспорт файла {directory + file_name + add}.pickle '
                                   f' провален. Ошибка: {miss}'),
                          log_type='ERROR')
            return False

    # загрузка объекта из директории
    def load_json_object(self, file_name: str, directory: str = None,
                         encoding: str = 'utf-8') -> dict or list or None:
        '''
        Функция сохраняет переданный объект в каталог.
        :param directory: каталог.
        :param file_name: имя файла.
        :param encoding: кодировка
        :return: считанный объект или None, если считывание провалено
        '''

        self.__to_log(message=(f'load_json_object: Запрошено считывание файла directory: {directory}, ' +
                               f'file_name: {file_name}'),
                      log_type='DEBUG')

        if directory is None:  # Если директория не указана
            if not self.__default_directory is None:  # Если указан дефолтный каталог
                directory = self.__default_directory  # Берём дефолтное значение
            else:  # Если не указан каталог и дефолтного значения нет
                self.__to_log(message=(f'load_json_object: Импорт файла {file_name} '
                                       ' провален. Не указана директория для экспорта'),
                              log_type='ERROR')
                return None  # Иначе - вернём ошибку

        if not directory.endswith('/'):  # если в конце директории нет слеша, поставим его
            directory = directory + '/'

        # Срежем расширение, если оно есть
        file_name = file_name.replace('.json', '')

        if not os.access(directory + file_name + '.json', mode=os.F_OK):  # проверим существование файла директории
            # если файла нет
            self.__to_log(message=('load_json_object: Ошибка доступак файлу ' + directory + file_name + '.json'),
                          log_type='ERROR')
            return None  # результат - не считан файл

        # Пробуем считать файл
        try:
            with open(directory + file_name + '.json', 'r', encoding=encoding) as f:
                result = json.load(f)
            self.__to_log(message=('load_json_object: Импорт файла ' + directory + file_name + '.json' +
                                   ' выполнен успешно'),
                          log_type='DEBUG')
            return result  # Если считали у спешно

        except BaseException as miss:
            self.__to_log(message=('load_json_object: Ошибка считывания файла ' + directory + file_name + '.json' +
                                   ': ' + str(miss)),
                          log_type='ERROR')
            return None  # Результат считывания - None

