'''готово/отлажено
# ----------------------------------------------------------------------------------------------------
# PandasSimpleReader ---------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
Задача объекта - считать/экспортнуть и, если требуется, запомнить файл. Модуль работает С ОДНИМ файлом за вызов метода.
В случае, если файл запомнен, то к нему есть доступ через функции get.

Внутренние наборы данных
    files - словарь. Индекс - имя файла, значение - DataFrame считанного файла

Параметры модуля:
    __init__
        launch_module_name - идетнификационное имя (откуда вызывают, из какого процесса)
        save_imported - сохранять ли данные считанных файлов?
        save_exported - сохранить ли экспортирующиеся файлы
        process_manager - менеджер текущего процесса

Функция импорта файла с каталога:
    csv_import(directory, file_name,encoding='default', with_index=False, sep=';')
        Считываются данные из одного указанного файла в директории.
        :param file_name: имя файла
        :param directory: директория с файлом
        :param encoding: - кодировка файла (дефолтная - или Win1251, или UTF-8. Определит сам)
        :param with_index: - считывать ли индекс из файла?
        :param sep: - разделитель в файле
        :return: status, result. bool - успешность, result - данные файла или False при заваливании операции

Функция экспорта файла в каталог:
    csv_export(directory, tokens_name, file_data, encoding='default', with_index=False, sep=';')
        Экспортится один фрейм в один csv файл.
        :param directory: директория с файлом
        :param tokens_name: имя файла
        :param file_data: непосредственно объект pandas для экспорта
        :param encoding: - кодировка файла (дефолтная - или Win1251, или UTF-8. Определит сам)
        :param with_index: - считывать ли индекс из файла?
        :param sep: - разделитель в файле
        :return: status (bool)

Функция экспорта файла в каталог:
    xlsx_export(directory, tokens_name, data_dict, encoding='default', with_index=False, sep=';')
        Экспортится фрейм в XLSX файл. Если подан словарь, то для каждого фрейма словаря в файле созадётся
        лист, имеющий название соответсвующего индекса словаря.
        :param directory: директория с файлом
        :param tokens_name: имя файла
        :param file_dict: непосредственно словарь объектов DataFrame для экспорта или объект DataFrame
        :param encoding: - кодировка файла (дефолтная - или Win1251, или UTF-8. Определит сам)
        :param with_index: - считывать ли индекс из файла?
        :return:  status (bool)


Функция обновления словаря:
    reset_dicts()
        без параметров. Просто перезаводит словарь.

Функция доступа к словарям считанных/экспортнух данных:
    get_imported(name)
    name - имя импортнуго файла, который мы хотим получить (с расширением!).
    :return status, file
            status - есть ли данные в словаре
            file - считанный файл (если данных нет - False)

    get_exported(name)
    name - имя экспортнутого файла, который мы хотим получить (с расширением!).
    :return status, file
            status - есть ли данные в словаре
            file - считанный файл (если данных нет - False)

'''

import os as os
import pandas as pd

from chardet.universaldetector import UniversalDetector as UniversalDetector  # Для автоопределения кодировки
from Managers import ProcessesManager

class PandasSimpleReader:


    def __init__(self, process_manager: ProcessesManager, launch_module_name: str = None,
                 save_imported=False,
                 save_exported=False
                 ):
        '''
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер текущего процесса
        :param save_imported: сохранять импортируемые файлы в свой словарь?
        :param save_exported: сохранять экспортирующиеся файлы в свой словарь?
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name)
        self.__to_log = self.__Logger.to_log

        if isinstance(save_imported, bool):  # Если сохранение импорта настроено
            self.__save_imported=save_imported
        else:
            self.__save_imported = False

        if isinstance(save_exported, bool):  # Если сохранение экспорта настроено
            self.__save_exported=save_exported
        else:
            self.__save_exported = False

        self.reset_dict()  # вызовем обновление словарей

    def reset_dict(self):
        self.__to_log(message=('reset_dict: словари обновлены.'),
                      log_type='DEBUG')
        #Функция для обновления словаря
        self.__imported_files = {}
        self.__exported_files = {}
        return

    def get_imported(self, name: str):
        '''
        Функция запрашивает name в словаре импортнутых файлов. После чего выдаёт данные о считанном файле,
        если даные есть в импортнутых файлах.
        :param name: имя файла (с расширением!)
        :return: result - результат, хранящиёся в словаре на индексе name. Если результата нет, то None.
        '''
        # Выдаёт данные из словаря
        if name in self.__imported_files.keys():  # Если есть такой стчитанный файл
            file = self.__imported_files[name].copy(deep=True)  # Берём файл (копию)
        else:  # Если индекса нет
            file = None

        return file

    def get_exported(self, name):
        '''
        Функция запрашивает name в словаре экспортнутых файлов. После чего выдаёт данные о считанном файле,
        если даные есть в экспортнутых файлах.
        :param name: имя файла (с расширением!)
        :return: status, result. возвращаяет status (bool) и данные файла (копию!) - False, если файл не считан.
        '''
        # Выдаёт данные из словаря
        if name in self.__exported_files.keys():  # Если есть такой экспортнутый файл
            status = True
            file = self.__exported_files[name].copy(deep=True)  # Берём файл (копию)

        else:  # Если индекса нет
            status = False
            file = None

        return status, file

    # ----------------------------------------------------------------------------------------------------
    # Импорт данных --------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    # Считываем файл из каталога - готово, отлажено.
    def csv_import(self,
                   directory: str, file_name: str,
                   encoding: str = None,
                   index_column_name: str = False,
                   sep: str = ';') -> pd.core.frame.DataFrame or None:
        '''
        Считываются данные из одного файла из директории.
        :param file_name: имя файла с расширением!
        :param directory: директория с файлом
        :param encoding: - кодировка файла. Если None - определится автоматически
        :param index_column_name: - колонка с названием индекса
        :param sep: - разделитель в файле
        :return: result - данные файла. None если не считано.
        '''

        if not file_name.endswith('.csv'):  # Установим расширение, если его нет
            file_name += '.csv'

        self.__to_log(message=('csv_import: Запрошено считывание файла directory: "' + str(directory) + '"'
                               ' file: "' + str(file_name) + '"'),
                      log_type='DEBUG')

        # Валидация переменных
        is_ok = self.__import_validator(directory=directory, file_name=file_name)
        if not is_ok:  # Если валидация завалена
            self.__to_log(message='csv_import: Валидация не пройдена.',
                          log_type='ERROR')
            return None  # результат - не считан файл


        if not directory.endswith('/'):  # если в конце директории нет слеша, поставим его
            directory = directory + '/'

        if not os.access(directory + file_name, mode=os.F_OK):  # проверим существование файла директории
            # если файла нет
            self.__to_log(message=('csv_import: Ошибка доступак файлу ' + str(directory + file_name)),
                          log_type='ERROR')
            return None  # результат - не считан файл

        # Считаем файл
        sucsess = True  # Индикатор успеха считывания
        if isinstance(encoding, str):  # Если кодировка указана
            try:
                Main_file = open(directory + file_name, 'r', encoding=encoding)  # Создадим "файлоподобный объект"
                                                                           # (чтобы pandas не заблокировал к нему потом доступ)
                file_data = pd.read_csv(filepath_or_buffer=Main_file,
                                        sep=sep, encoding=encoding, index_col=index_column_name,
                                        engine='python')  # считаем его
                Main_file.close()  # Закроем файлоподобный объект

            except BaseException as miss:
                sucsess = False  # Ошибка считывания
                self.__to_log(message=('csv_import: Выполнение считывания файла ' + str(directory + file_name) + ': ' +
                                       str(miss)),
                              log_type='ERROR')

                try:  # Закроем фай. Через try, если файл не открылся
                    Main_file.close()  # Закроем файлоподобный объект
                except BaseException:  # Если не получилось считать файл
                    pass

        else:  # Если указано автоопределение кодировки
            detector = UniversalDetector()
            with open(directory + file_name, 'rb') as fh:
                for line in fh:
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
            encoding = detector.result['encoding']  # Получили кодировку
            try:  # Считаем
                Main_file = open(directory + file_name, 'r', encoding=encoding)  # Создадим "файлоподобный объект"
                # (чтобы pandas не заблокировал к нему потом доступ)
                file_data = pd.read_csv(filepath_or_buffer=Main_file,
                                        sep=sep, encoding=encoding, index_col=index_column_name,
                                        engine='python')  # считаем его

                sucsess = True
                Main_file.close()  # Закроем файлоподобный объект

            except BaseException as miss:  # Если не получилось считать файл
                sucsess = False  # Ошибка считывания
                self.__to_log(message=('csv_import: Выполнение считывания файла ' + str(directory + file_name) + ': ' +
                                       str(miss)),
                              log_type='ERROR')

                try:  # Закроем фай. Через try, если файл не открылся
                    Main_file.close()  # Закроем файлоподобный объект
                except BaseException:
                    pass

        if sucsess:  # Если считывание успешно
            self.__to_log(message=('csv_import: Считывание файла ' + str(directory + file_name) + ' выполнено успешно'),
                          log_type='DEBUG')
            if self.__save_imported:  # Если надо запоминать данные
                self.__imported_files[file_name] = file_data.copy(deep=True) #Запомним даныне файла

            return file_data  # Без копирования, т.к. ссылка на объект будет ТОЛЬКО у вызывающего модуля

        else:  # Если считывание завалено
            self.__to_log(message='csv_import: Выполнение считывания файла провалено.',
                          log_type='ERROR')
            return None

    # Валидация переменных
    def __import_validator(self, directory, file_name):
        is_ok = True  # всё ли в порядке

        # Проверка файла
        if not isinstance(file_name, str):  # Если имя файла не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__import_validator: Значение "file_name" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(file_name))),
                          log_type='ERROR')

        if not isinstance(directory, str):  # Если директория не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__import_validator: Значение "directory" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(directory))), log_type='ERROR')


        return is_ok

    # Считываем файл из каталога - готово, отлажено.
    def xlsx_import(self,
                    directory: str, file_name: str,
                    sheet_name: int or str or list or None = 0,
                    encoding: str = None,
                    index_column_name: str = False) -> pd.core.frame.DataFrame or dict:
        '''
        Считываются данные из одного файла из директории.
        :param file_name: имя файла с расширением!
        :param directory: директория с файлом
        :param sheet_name: номер или имя листа, который нам нужен. Или список листов. None -  считать все листы.
                Дефолтно будет использоваться только нулевой лист.
        :param encoding: - кодировка файла. Если None - определится автоматически
        :param index_column_name: - колонка с названием индекса
        :return: None если не считано, DataFrame - если считан один лист, dict - если считывались несколько листов.
        '''

        if not file_name.endswith('.xlsx'):  # Установим расширение, если его нет
            file_name += '.xlsx'


        self.__to_log(message=('xlsx_import: Запрошено считывание файла directory: "' + str(directory) +
                               ' "file: "' + str(file_name) + '"'),
                      log_type='DEBUG')

        # Валидация переменных
        is_ok = self.__import_validator(directory=directory, file_name=file_name)
        if not is_ok:  # Если валидация завалена
            self.__to_log(message='xlsx_import: Валидация не пройдена.',
                          log_type='ERROR')
            return None  # результат - не считан файл

        if not directory.endswith('/'):  # если в конце директории нет слеша, поставим его
            directory = directory + '/'

        if not os.access(directory + file_name, mode=os.F_OK):  # проверим существование файла директории
            # если файла нет
            self.__to_log(message=('xlsx_import: Ошибка доступак файлу ' + str(directory + file_name)),
                          log_type='ERROR')
            return None  # результат - не считан файл

        # Считаем файл
        sucsess = True  # Индикатор успеха считывания
        if isinstance(encoding, str):  # Если кодировка указана
            try:
                Main_file = open(directory + file_name, 'rb')  # Создадим "файлоподобный объект"
                # (чтобы pandas не заблокировал к нему потом доступ)
                file_data = pd.read_excel(io=Main_file,
                                          sheet_name=sheet_name,
                                          encoding=encoding, index_col=index_column_name,
                                          engine='xlrd'
                                          )  # считаем его
                Main_file.close()  # Закроем файлоподобный объект

            except BaseException as miss:
                sucsess = False  # Ошибка считывания
                self.__to_log(message=('xlsx_import: Выполнение считывания файла ' + str(directory + file_name) + ': ' +
                                       str(miss)),
                              log_type='ERROR')

                try:  # Закроем фай. Через try, если файл не открылся
                    Main_file.close()  # Закроем файлоподобный объект
                except BaseException:  # Если не получилось считать файл
                    pass

        else:  # Если указано автоопределение кодировки
            detector = UniversalDetector()
            with open(directory + file_name, 'rb') as fh:
                for line in fh:
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
            encoding = detector.result['encoding']  # Получили кодировку
            try:  # Считаем
                Main_file = open(directory + file_name, 'rb')  # Создадим "файлоподобный объект"
                # (чтобы pandas не заблокировал к нему потом доступ)
                file_data = pd.read_excel(io=Main_file,
                                          sheet_name=sheet_name,
                                          encoding=encoding, index_col=index_column_name,
                                          engine='xlrd'
                                          )  # считаем его

                sucsess = True
                Main_file.close()  # Закроем файлоподобный объект

            except BaseException as miss:  # Если не получилось считать файл
                sucsess = False  # Ошибка считывания
                self.__to_log(message=('xlsx_import: Выполнение считывания файла ' + str(directory + file_name) + ': ' +
                                       str(miss)),
                              log_type='ERROR')

                try:  # Закроем фай. Через try, если файл не открылся
                    Main_file.close()  # Закроем файлоподобный объект
                except BaseException:
                    pass

        if sucsess:  # Если считывание успешно
            self.__to_log(message=('xlsx_import: Считывание файла ' + str(directory + file_name) + ' выполнено успешно'),
                          log_type='DEBUG')
            if self.__save_imported:  # Если надо запоминать данные
                self.__imported_files[file_name] = file_data.copy(deep=True)  # Запомним даныне файла

            return file_data  # Без копирования, т.к. ссылка на объект будет ТОЛЬКО у вызывающего модуля

        else:  # Если считывание завалено
            self.__to_log(message='xlsx_import: Выполнение считывания файла провалено.',
                          log_type='ERROR')
            return None

    # ----------------------------------------------------------------------------------------------------
    # Функция экспорта в csv -----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    def csv_export(self,
                   directory: str, file_name: str,
                   file_data: pd.core.frame.DataFrame,
                   encoding: str = 'utf-8',
                   with_index: bool = False,
                   sep: str = ';') -> bool:
        '''
        Экспортим file_data в директорию. Если имя файла занято, то имя получит "смещение" (типа '123 (1).csv')
        :param file_name: имя файла
        :param directory: директория с файлом
        :param file_data: pandas таблица на экспорт
        :param encoding: - кодировка файла
        :param with_index: - экспортировать ли индекс
        :param sep: - разделитель в файле
        :return: status (bool)
        '''

        if not file_name.endswith('.csv'):  # Установим расширение, если его нет
            file_name += '.csv'

        self.__to_log(message=('csv_export: Запрошен экспорт файла  directory: "' + str(directory) + '"'
                               ' file: "' + str(file_name) + '"'),
                      log_type='DEBUG')

        # Валидация
        is_ok = self.__csv_export_validator(directory=directory, file_name=file_name, file_data=file_data,
                                            with_index=with_index, sep=sep)
        if not is_ok:  # Если валидация завалена
            self.__to_log(message='csv_export: Валидация не пройдена.',
                          log_type='ERROR')
            return False  # Статус - false

        # Проверим существование директории
        if not os.access(directory, mode=os.F_OK):
            # Если нет директории
            self.__to_log(message=('csv_export: Проверка существования каталога провалена. ' +
                                   'Каталога нет (' + str(directory) + ')'),
                          log_type='ERROR')
            return False

        # Если каталог есть
        if not directory.endswith('/'):  # Если нет "/" - добавим
            directory += '/'

        # Срежем расширение, если оно есть
        file_name = file_name.replace('.csv', '')

        add = ''  # Добавка к имени файла, если исходное имя занято
        count = 0  # счётчик для "сдвига" имени файла
        while True:
            if os.access(directory + file_name + add + '.csv', mode=os.F_OK):  # Если имя занято
                # Сдвинем счётчик
                count += 1
                # Скорректируем добавку
                add = '(' + str(count) + ')'
            else:  # Если варианта "directory+file_name+add+'.csv'" нет
                break  # закончим подбор сдвига

        # Экспортнём
        try:
            file_data.to_csv(path_or_buf=directory + file_name + add + '.csv', sep=sep, encoding=encoding, index=with_index)
            if self.__save_exported:  # Если надо сохранять экспортированные файлы
                self.__exported_files[file_name + add + '.csv'] = file_data.copy(deep=True)

        except BaseException as miss:
            self.__to_log(message=('csv_export: Экспорт файла ' + str(directory + file_name + add + '.csv') +
                                   ' провален. Ошибка: ' + str(miss)),
                          log_type='ERROR')
            return False

        self.__to_log(message=('csv_export: Экспорт файла ' + str(directory + file_name + add + '.csv') +
                               ' выполнен успешно'),
                      log_type='DEBUG')
        return True

    # валидатор функции экспорта в csv
    def __csv_export_validator(self, directory, file_name, file_data, with_index, sep):

        is_ok = True  # Детектор валидации

        # Проверка файла
        if not isinstance(file_name, str):  # Если имя файла не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__csv_export_validator: Тип "file_name" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(file_name))), log_type='ERROR')
        else:  # Если это строка
            if not file_name.endswith('.csv'):  # если расширение файла не csv
                is_ok = False  # Валидация завалена
                self.__to_log(message=('__csv_export_validator: Расширение "file_name" является недопустимым. ' +
                                       'Ожидалось file_name.csv . Получено ' + str(file_name)), log_type='ERROR')

        if not isinstance(directory, str):  # Если директория не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__csv_export_validator: Тип "directory" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(directory))), log_type='ERROR')

        # Проверка данных файла
        if not isinstance(file_data, pd.core.frame.DataFrame):  # подан не фрейм
            is_ok = False
            self.__to_log(message=('__csv_export_validator: Тип "file_data" является недопустимым. ' +
                                   'Ожидалось pd.core.frame.DataFrame. Получено ' + str(type(file_data))),
                          log_type='ERROR')

        if not isinstance(with_index, bool):  # Если считывание индекса указано неверно
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__csv_export_validator: Тип "with_index" является недопустимым. ' +
                                   'Ожидалось bool. Получено ' + str(type(with_index))), log_type='ERROR')

        if not isinstance(sep, str):  # Если разделитель не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__csv_export_validator: Тип "sep" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(sep))), log_type='ERROR')
        return is_ok

    # ----------------------------------------------------------------------------------------------------
    # Функция экспорта в XLSX -----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    def xlsx_export(self,
                    directory: str, file_name: str,
                    file_data: dict or pd.core.frame.DataFrame,
                    encoding: str = 'utf-8',
                    with_index: bool = False) -> bool:
        '''
        Считываются данные из одного файла из директории.

        :param file_name: имя файла
        :param directory: директория с файлом
        :param file_data: Дата фрейм, который будет экспортирован на один лист, или словарь фреймов, который будет
                            экспортирован на листы с названиями, совпадающими с индексами в словаре.
        :param encoding: - кодировка файла
        :param with_index: - экспортировать ли индекс?
        :return: status (bool)
        '''

        if not file_name.endswith('.xlsx'):  # Установим расширение, если его нет
            file_name += '.xlsx'

        self.__to_log(message=('xlsx_export: Запрошен экспорт файла  directory: "' + str(directory) + '"'
                               ' file: "' + str(file_name) + '"'),
                      log_type='DEBUG')

        is_ok = self.__xlsx_export_validator(directory=directory, file_name=file_name, file_dict=file_data,
                                             encoding=encoding, with_index=with_index)
        if not is_ok:  # Если валидация завалена
            self.__to_log(message='xlsx_export: Валидация не пройдена.',
                          log_type='ERROR')
            return False  # Статус - false

        # Проверим существование директории
        if not os.access(directory, mode=os.F_OK):
            self.__to_log(message=('xlsx_export: Проверка существования каталога провалена. ' +
                                   'Каталога нет (' + str(directory) + ')'),
                          log_type='ERROR')
            return False  # Статус - false

        # Если каталог есть
        if not directory.endswith('/'):  # Если нет / - добавим
            directory += '/'

        # Срежем раcширение, если оно есть (для сдвига имени файла)
        file_name = file_name.replace('.xlsx', '')

        add = ''  # Добавка к имени файла, если исходное имя занято
        count = 0  # счётчик
        while True:
            if os.access(directory + file_name + add + '.xlsx', mode=os.F_OK):  # Если имя занято
                # Сдвинем счётчик
                count += 1
                # Скорректируем добавку
                add = '(' + str(count) + ')'
            else:  # Если варианта "directory+tokens_name+add+'.gexf'" нет
                break

        # Транзитнем фрейм в словарь
        if isinstance(file_data, pd.core.frame.DataFrame):  # если подан фрейм
            # переведём его в словарь для общности экспорта
            do_dict = {}
            do_dict['main'] = file_data.copy(deep=True)
            file_data =do_dict

        # Выполним экспорт
        try:
            with pd.ExcelWriter(directory + file_name + add + '.xlsx') as writer:
                for frame_key in file_data.keys():  # Пошли по индексу в словаре
                    file_data[frame_key].to_excel(writer, sheet_name=frame_key, encoding=encoding, index=with_index)
        except BaseException as miss:
            # В случае ошибки
            self.__to_log(message=('xlsx_export: Экспорт файла ' + str(directory + file_name + add + '.xlsx') +
                                   ' провален. Ошибка: ' + str(miss)),
                          log_type='ERROR')
            return False  # Статус - false

        # Если экспортнуто успешно
        if self.__save_exported:  # Если надо сохранять экспортированные файлы
            self.__exported_files[file_name + add + '.xlsx'] = file_data

        self.__to_log(message=('csv_export: Экспорт файла ' + str(file_name + add + '.xlsx') +
                               ' выполнен успешно'),
                      log_type='DEBUG')
        return True

    def __xlsx_export_validator(self, directory, file_name, file_dict, encoding, with_index):
        is_ok = True

        # Проверка файла
        if not isinstance(file_name, str):  # Если имя файла не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__xlsx_export_validator: Тип "file_name" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(file_name))), log_type='ERROR')

        if not isinstance(directory, str):  # Если директория не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__xlsx_export_validator: Тип "directory" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(directory))), log_type='ERROR')

        # Проверка словаря с данными
        if not isinstance(file_dict, pd.core.frame.DataFrame):  # подан не фрейм
            if not isinstance(file_dict, dict):  # И это не словарь -
                is_ok = False
                self.__to_log(message=('__xlsx_export_validator: Тип "file_dict" является недопустимым. ' +
                                       'Ожидалось pd.core.frame.DataFrame или dict. Получено ' + str(type(file_dict))),
                              log_type='ERROR')

            else:  # Если это всё-таки словарь
                # Проверим, что все его элементы - DataFrame-ы
                for key_name in file_dict.keys():  # Пошли по словарю
                    if not isinstance(file_dict[key_name], pd.core.frame.DataFrame):  # Если элемент словаря не фрейм
                        is_ok = False
                        self.__to_log(message=('__xlsx_export_validator: Тип "file_dict[' + str(key_name) + ']"' +
                                               ' является недопустимым. ' +
                                               'Ожидалось pd.core.frame.DataFrame. Получено ' + str(type(file_dict))),
                                      log_type='ERROR')

        if not isinstance(encoding, str):  # Если кодировка - не строка
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__xlsx_export_validator: Тип "encoding" является недопустимым. ' +
                                   'Ожидалось str. Получено ' + str(type(encoding))), log_type='ERROR')

        if not isinstance(with_index, bool):  # Если считывание индекса указано неверно
            is_ok = False  # Валидация завалена
            self.__to_log(message=('__xlsx_export_validator: Тип "with_index" является недопустимым. ' +
                                   'Ожидалось bool. Получено ' + str(type(with_index))), log_type='ERROR')

        return is_ok
