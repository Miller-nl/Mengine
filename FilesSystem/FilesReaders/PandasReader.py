
from ...Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger
from .StandartReader import StandartReader

import pandas as pd


class PandasReader(StandartReader):
    '''
    Класс для считывания и сохранения csv таблиц и pandas объектов.

    Методы и свойства:

        connect_path() - соединить каталог и имя файла

        shift_name() - функция модификации имени файла, если оно не является уникальным.

        Логирование
            _Logger - логгер

            _sub_module_name - "под имя", использующееся при логировании

            _to_log - функция логирования

        Настройки считывания
            save_loaded - сохранять ли считанные файлы?

            loaded - словарь сохранённых файлов

            _reset_loaded - обновить словарь сохранённых файлов

        Проверки
            check_assess() - проверка доступа

            get_encoding() - получить кодировку файла


        Чтение - запись
            write_csv() - запись

            read_csv() - чтение

            write_excel() - запись

            read_excel() - чтение
    '''

    def __init__(self, logger: CommonLoggingClient = None, parent_name: str = None,
                 save_loaded: bool = False):
        '''

        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        '''

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

        # Выполним стандартный init
        StandartReader.__init__(self, logger=self.__Logger, parent_name=self.__my_name,
                                save_loaded=save_loaded)

    # ------------------------------------------------------------------------------------------------
    # .csv Файлы -------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read_csv(self, full_path: str, save_loaded: bool = None,
                 encoding: str = None,
                 index_column_name: str = None,
                 sep: str = ';'
                 ) -> pd.core.frame.DataFrame or None:
        '''
        Функция считывания csv файла

        :param full_path: полный путь к файлу
        :param save_loaded: сохранить ли загруженный файл? True - да, False - нет, None - использовать стандартную
            настройку (save_loaded)
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param index_column_name: имя колонки с названием индекса
        :param sep: - разделитель в файле
        :return: считанный файл или None в случае ошибки
        '''

        self.__to_log(message='Запрошено чтение файла.',
                      logging_data={'full_path': full_path},
                      logging_level='DEBUG')

        if not full_path.endswith('.csv'):  # Установим расширение, если его нет
            self.__to_log(message='Расширение файла неприемлемо - не ".csv". Чтение провалено.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        if not self.check_assess(path=full_path):  # Если нет доступа к файлу
            self.__to_log(message='Доступ к файлу отсутствует. Чтение провалено.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        if encoding is None:  # Если кодировка не указана
            encoding = self.get_encoding(full_path=full_path)
            if encoding is None:  # Если получение кодировки завалено
                self.__to_log(message='Автоопределение кодировки провалено. Чтение провалено.',
                              logging_data={'full_path': full_path},
                              logging_level='ERROR')
                return None

        # Считаем
        file_data = None
        try:  # Считаем
            Main_file = open(full_path, 'r', encoding=encoding)  # Создадим "файлоподобный объект"
            # (чтобы pandas не заблокировал к нему потом доступ)
            file_data = pd.read_csv(filepath_or_buffer=Main_file,
                                    sep=sep, encoding=encoding, index_col=index_column_name,
                                    engine='python')  # считаем его

        except BaseException:  # Если не получилось считать файл
            self.__to_log(message='Считывание документа провалено. Чтение провалено.',
                          logging_data={'full_path': full_path,
                                        'encoding': encoding,
                                        'index_column_name': index_column_name,
                                        'sep': sep},
                          logging_level='ERROR')
        finally:
            try:
                Main_file.close()  # Закроем файлоподобный объект
            except BaseException:
                pass

        if file_data is not None:  # Если чтение успешно

            if save_loaded is None:
                save_loaded = self.save_loaded

            if save_loaded:  # Если требуется сохранить в память
                if not self.__ad_loaded(full_path=full_path, data=file_data):  # Если данные пришлось перезаписать
                    self.__to_log(message='При сохранении в словарь произошла перезапись.',
                                  logging_data={'full_path': full_path},
                                  logging_level='WARNING')

                self.__to_log(message='Чтение файла выполнено успешно. Данные сохранены в словарь.',
                              logging_data={'full_path': full_path},
                              logging_level='DEBUG')

            else:  # Если сохранение не требовалось
                self.__to_log(message='Чтение файла выполнено успешно. Сохранение не требовалось.',
                              logging_data={'full_path': full_path},
                              logging_level='DEBUG')

            return file_data
        else:
            return None


    def write_csv(self, file_data: pd.core.frame.DataFrame or pd.core.series.Series,
                  full_path: str, shift_name: bool or None = True,
                  sep: str = ';', with_index: bool = True,
                  encoding: str = 'utf-8') -> True or str or None:
        '''
        Фнукия записывает данные в файл ".csv".

        :param file_data: данные для экспорта в файл в виде фрейма или столбца
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :param sep: разделитель в файле
        :param with_index: экспортировать ли индекс?
        :param encoding: кодировка файла
        :return: True - успешно экспортнуто, имя уникально
            str - успешно экспортнуто, имя изменено
            None - ошибка экспорта
        '''

        self.__to_log(message='Запрошен экспорт файла.',
                      logging_data={'full_path': full_path},
                      logging_level='DEBUG')

        if not full_path.endswith('.csv'):  # валидация расширения
            self.__to_log(message='Расширение файла неприемлемо - не ".csv". Экспорт провален.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        # Проверим тип данных
        if isinstance(file_data, pd.core.frame.DataFrame):
            pass
        elif isinstance(file_data, pd.core.series.Series):  # Если подна series - конвертнём
            file_data = self.__convert_series_to_frame(series=file_data)  # Конвертнём в DataFrame

            if file_data is None:  # Если конвертация упала
                self.__to_log(message='Конвертация поданного Series во DataFrame провалена. Экспорт провален.',
                              logging_data={'full_path': full_path},
                              logging_level='ERROR')
                return None  # Верёнм ошибку

        else:  # Если тип неверный
            self.__to_log(message='Ошибка типа экспортных данных. Экспорт провален.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        # Выполним проверку и сдвиг имени файла
        name_shifted = False
        if self.check_assess(path=full_path):  # Если файл есть
            if shift_name:  # Если сдвиг разрешён
                self.__to_log(message='Имя файла не является уникальным. Сдвиг разрешен.',
                              logging_data={'full_path': full_path,
                                            'shift_name': shift_name},
                              logging_level='DEBUG')
                full_path = self.name_shifting(full_path=full_path, expansion='.csv')
                name_shifted = True  # Так как старое имя уже есть, то сдвиг точно был

            else:  # Если сдвиг запрещён
                self.__to_log(message='Имя файла не является уникальным. Сдвиг запрещён. Экспорт провален.',
                              logging_data={'full_path': full_path,
                                            'shift_name': shift_name},
                              logging_level='ERROR')
                return None

        # Выполним экспорт
        try:
            file_data.to_csv(path_or_buf=full_path, sep=sep, encoding=encoding,
                             index=with_index)

        except BaseException:
            self.__to_log(message='Экспорт файла провален.',
                          logging_data={'full_path': full_path,
                                        'sep': sep,
                                        'encoding': encoding,
                                        'with_index': with_index},
                          logging_level='ERROR')
            return None

        self.__to_log(message='Экспорт файла выполнен успешно.',
                      logging_data={'full_path': full_path},
                      logging_level='DEBUG')

        # Отдадим результат работы
        if name_shifted:  # Если имя было сдвинуто
            return full_path

        else:  # Если имя не изменилось
            return True

    def __convert_series_to_frame(self, series: pd.core.series.Series) -> pd.core.frame.DataFrame or None:
        '''
        Функция конвертирует series во frame для удобства

        :param series: series с данными
        :return: результат конвертации: DataFrame или None, если конвертация упала (хз, чё там может упасть).
        '''

        try:
            export = pd.DataFrame(data=series.tolist(), index=series.index)
            return export
        except BaseException:
            self.__to_log(message='Конвертация Series в DataFrame провалено.',
                          logging_level='ERROR')
            return None

    # ------------------------------------------------------------------------------------------------
    # excel файлы ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read_excel(self, full_path: str, save_loaded: bool = None,
                   index_column_number: int = None,
                   encoding: str = None,
                   sheets_names: int or str or list = None
                   ) -> pd.core.frame.DataFrame or dict or None:
        '''
        Функция считывания xlsx файла
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html

        :param full_path: полный путь к файлу
        :param save_loaded: сохранить ли загруженный файл? True - да, False - нет, None - использовать стандартную
            настройку (save_loaded)
        :param index_column_number: какую колонку считать индексом всех листов? Варианты:
            int - номер колонки (начиная с 0)
            None - индекс отсутствует.
        :param encoding: кодировка файла. None - pandas.read_excel выберет кодировку сам.
            Комментарий - по ощущениям, engine='xlrd' сам берёт кодировку, раскодируя файл из битного представления.
        :param sheets_names: определяет листы, которые требуется считать:
            str - имя листа;
            int - номер листа (с нулевого);
            list - список из строк или чисел ([0, "Sheet5"] - возьмёт первый лист и лист с именем "Sheet5");
            None - взять все.
        :return: считанный файл в виде pd.core.frame.DataFrame; если считывался один лист, или
            dict вида {sheet_name: DataFrame}, если считывались несколько; или None в случае ошибки.
        '''
        self.__to_log(message='Запрошено чтение файла.',
                      logging_data={'full_path': full_path},
                      logging_level='DEBUG')

        if not full_path.endswith('.xlsx') and not full_path.endswith('.xls'):  # Установим расширение, если его нет
            self.__to_log(message='Расширение файла неприемлемо - не ".xlsx"/".xls". Чтение провалено.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        if not self.check_assess(path=full_path):  # Если нет доступа к файлу
            self.__to_log(message='Доступ к файлу отсутствует. Чтение провалено.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        # Считаем
        file_data = None
        try:  # Считаем
            #Main_file = codecs.open(full_path, mode='rb', encoding=encoding)  # Создадим "файлоподобный объект"
            Main_file = open(full_path, 'rb')  # Создадим "файлоподобный объект"
            # (чтобы pandas не заблокировал к нему потом доступ)
            file_data = pd.read_excel(io=Main_file,
                                      sheet_name=sheets_names,
                                      encoding=encoding,
                                      index_col=index_column_number,
                                      engine='xlrd'
                                      )  # считаем его

        except BaseException:  # Если не получилось считать файл
            self.__to_log(message='Считывание документа провалено. Чтение провалено.',
                          logging_data={'full_path': full_path,
                                        'index_column_number': index_column_number,
                                        'encoding': encoding,
                                        'sheets_names': sheets_names},
                          logging_level='ERROR')
        finally:
            try:
                Main_file.close()  # Закроем файлоподобный объект
            except BaseException:
                pass

        if file_data is not None:  # Если чтение успешно

            if save_loaded is None:
                save_loaded = self.save_loaded

            if save_loaded:  # Если требуется сохранить в память
                if not self.__ad_loaded(full_path=full_path, data=file_data):  # Если данные пришлось перезаписать
                    self.__to_log(message='При сохранении в словарь произошла перезапись.',
                                  logging_data={'full_path': full_path},
                                  logging_level='WARNING')

                self.__to_log(message='Чтение файла выполнено успешно. Данные сохранены в словарь.',
                              logging_data={'full_path': full_path},
                              logging_level='DEBUG')

            else:  # Если сохранение не требовалось
                self.__to_log(message='Чтение файла выполнено успешно. Сохранение не требовалось.',
                              logging_data={'full_path': full_path},
                              logging_level='DEBUG')

            return file_data
        else:
            return None

    def write_excel(self, file_data:  pd.core.frame.DataFrame or pd.core.series.Series or dict,
                    full_path: str,
                    shift_name: bool or None = True,
                    with_index: bool = True,
                    one_list_name: str = 'List1',
                    encoding: str = 'utf-8') -> True or str or None:
        '''
        Фнукия записывает данные в файл ".xlsx"
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html

        :param file_data: данные для экспорта в файл: DataFrame или Series экспортнутся на лист с именем
            one_list_name; если же подан словарь, имена листов совпадут с индексами.
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :param with_index: экспортировать ли с индексом
        :param one_list_name: имя "одного" листа. Если подан DataFrame или Series, а не словарь, то лист надо
            как-то назвать. Это его имя. Если подан словарь, в качестви имён листов будет взят индекс.
        :param encoding: кодировка файла
        :return: True - успешно экспортнуто, имя уникально
            str - успешно экспортнуто, имя изменено
            None - ошибка экспорта
        '''

        self.__to_log(message='Запрошен экспорт файла.',
                      logging_data={'full_path': full_path},
                      logging_level='DEBUG')

        if not full_path.endswith('.xlsx'):  # валидация расширения
            self.__to_log(message='Расширение файла неприемлемо - не ".xlsx". Экспорт провален.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        # Проверим тип данных
        if isinstance(file_data, dict):
            for key in file_data.keys():  # Проверим, что каждый элемент является фреймом
                if isinstance(file_data[key], pd.core.frame.DataFrame):  # Если фрейм
                    pass

                elif isinstance(file_data[key], pd.core.series.Series):  # Если Series - конвертнём
                    new_data = self.__convert_series_to_frame(series=file_data[key])

                    if new_data is None:  # Если конвертация упала
                        self.__to_log(message=('Конвертация элемента словаря из Series в DataFrame провалена. ' +
                                               'Элемент удалён из словаря.'),
                                      logging_data={'full_path': full_path,
                                                    'key': key},
                                      logging_level='ERROR')
                        file_data.pop(file_data[key])
                    else:  # Если всё ок
                        file_data[key] = new_data

                else:  # Если говнотип
                    self.__to_log(message='Тип объекта в словаре является неприемлимым. Элемент удалён из словаря.',
                                  logging_data={'full_path': full_path,
                                                'key': key},
                                  logging_level='ERROR')
                    file_data.pop(file_data[key])
        elif isinstance(file_data, pd.core.frame.DataFrame):
            file_data = {one_list_name: file_data}
        elif isinstance(file_data, pd.core.series.Series):  # Если подна series - конвертнём
            file_data = self.__convert_series_to_frame(series=file_data)  # Конвертнём в DataFrame
            if file_data is None:  # Если конвертация упала
                self.__to_log(message='Конвертация поданного Series во DataFrame провалена. Экспорт провален.',
                              logging_data={'full_path': full_path},
                              logging_level='ERROR')
                return None  # Верёнм ошибку
            else:  # Если всё ок
                file_data = {one_list_name: file_data}
        else:  # Если тип неверный
            self.__to_log(message='Ошибка типа экспортных данных. Экспорт провален.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

        # Выполним проверку и сдвиг имени файла
        name_shifted = False
        if self.check_assess(path=full_path):  # Если файл есть
            if shift_name:  # Если сдвиг разрешён
                old_name = full_path
                full_path = self.name_shifting(full_path=full_path, expansion='.xlsx')
                self.__to_log(message='Имя файла не является уникальным. Сдвиг разрешен, имя изменено.',
                              logging_data={'old_name': old_name,
                                            'new_name': full_path,
                                            'shift_name': shift_name},
                              logging_level='DEBUG')
                name_shifted = True  # Так как старое имя уже есть, то сдвиг точно был

            else:  # Если сдвиг запрещён
                self.__to_log(message='Имя файла не является уникальным. Сдвиг запрещён. Экспорт провален.',
                              logging_data={'full_path': full_path,
                                            'shift_name': shift_name},
                              logging_level='ERROR')
                return None

        # Выполним экспорт
        all_fine = True
        try:
            with pd.ExcelWriter(full_path) as writer:  # Делаем "писатель файла"
                for frame_key in file_data.keys():  # Пошли по индексу в словаре
                    try:
                        file_data[frame_key].to_excel(writer, sheet_name=frame_key, encoding=encoding, index=with_index)
                    except BaseException:
                        self.__to_log(message='Экспорт файла частично провален.',
                                      logging_data={'full_path': full_path,
                                                    'encoding': encoding,
                                                    'key': frame_key,
                                                    'with_index': with_index},
                                      logging_level='ERROR')
                        all_fine = False
        except BaseException:
            self.__to_log(message='Экспорт файла провален полностью.',
                          logging_data={'full_path': full_path,
                                        'encoding': encoding,
                                        'with_index': with_index},
                          logging_level='ERROR')
            return None  # Статус ошибка

        if all_fine:
            self.__to_log(message='Экспорт файла выполнен успешно.',
                          logging_data={'full_path': full_path},
                          logging_level='DEBUG')
        else:
            self.__to_log(message='Экспорт файла выполнен с ошибками.',
                          logging_data={'full_path': full_path},
                          logging_level='WARNING')

        # Отдадим результат работы
        if name_shifted:  # Если имя было сдвинуто
            return full_path

        else:  # Если имя не изменилось
            return True

