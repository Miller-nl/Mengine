from .Common import CommonMethods
from Exceptions.ExceptionTypes import ProcessingError, ValidationError

import pandas as pd
from warnings import warn


class XLSX(CommonMethods):
    '''
    Класс для считывания и сохранения xlsx объектов.

    Методы и свойства:
        Имена и пути
            concat_path() - соединить каталог и имя файла

            extract_name() - выделить имя файла из пути

            extract_extension() - выделить расширение файла из пути

            shift_name() - функция модификации имени файла, если оно не является уникальным.

        Проверки
            check_access() - проверка доступа

            get_encoding() - получить кодировку файла

        Чтение - запись
            write() - запись

            write_sheet() - добавить лист в конец файла

            read() - чтение

            read_sheet() - считать лист
    '''

    def __init__(self):
        '''
        '''

        # Выполним стандартный init
        CommonMethods.__init__(self)

    # ------------------------------------------------------------------------------------------------
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read(self, full_path: str,
             encoding: str = 'utf-8',
             index_column_number: int = None,
             sheets_names: int or str or list = None
             ) -> pd.core.frame.DataFrame or dict:
        '''
        Функция считывания xlsx файла

        :param full_path: полный путь к файлу
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param index_column_number: имя колонки с названием индекса
        :param sheets_names: определяет листы, которые требуется считать:
            str - имя листа;
            int - номер листа (с нулевого);
            list - список из строк или чисел ([0, "Sheet5"] - возьмёт первый лист и лист с именем "Sheet5");
            None - взять все.
        :return: считанный файл в виде pd.core.frame.DataFrame; если считывался один лист, или
            dict вида {sheet_name: DataFrame}, если считывались несколько.
        '''
        if not full_path.endswith('.xlsx'):
            raise ValidationError("Incorrect file extension. Only '.xlsx' is available.")

        with self.mutex:
            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)

            try:  # Считаем
                with open(full_path, 'rb') as file:
                    result = pd.read_excel(io=file,
                                           sheet_name=sheets_names,
                                           encoding=encoding,
                                           index_col=index_column_number,
                                           engine='xlrd'
                                           )  # считаем его

            except BaseException as miss:  # Если не получилось считать файл
                raise ProcessingError(f'File reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        return result

    def read_sheet(self, full_path: str, sheet: int or str,
                   encoding: str = 'utf-8',
                   index_column_number: int = None
                   ) -> pd.core.frame.DataFrame:
        '''
        Функция считывания одного листа xlsx файла

        :param full_path: полный путь к файлу
        :param sheet: определяет листы, которые требуется считать:
            str - имя листа;
            int - номер листа (с нулевого);
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param index_column_number: имя колонки с названием индекса
        :return: считанный лист в виде pd.core.frame.DataFrame.
        '''
        if not full_path.endswith('.xlsx'):
            raise ValidationError("Incorrect file extension. Only '.xlsx' is available.")

        with self.mutex:
            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)

            try:  # Считаем
                with open(full_path, 'rb') as file:
                    result = pd.read_excel(io=file,
                                           sheet_name=sheet,
                                           encoding=encoding,
                                           index_col=index_column_number,
                                           engine='xlrd'
                                           )  # считаем его

            except BaseException as miss:  # Если не получилось считать файл
                raise ProcessingError(f'Sheet reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        return result

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data:  pd.core.frame.DataFrame or pd.core.series.Series or dict,
              full_path: str,
              shift_name: bool or None = True,
              with_index: bool = True,
              one_list_name: str = 'List1',
              encoding: str = 'utf-8') -> bool or str:
        '''
        Фнукия записывает данные в файл ".xlsx".
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html

        :param file_data: данные для экспорта в файл: DataFrame или Series экспортнутся на лист с именем,
            переданным в one_list_name; если же подан словарь, имена листов совпадут с индексами словаря.
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :param sep: разделитель в файле
        :param with_index: экспортировать ли индекс?
        :param one_list_name: имя "одного" листа. Если подан DataFrame или Series, а не словарь, то лист надо
            как-то назвать. Это его имя. Если подан словарь, в качестви имён листов будет взят индекс.
        :param encoding: кодировка файла
        :return: True - успешно экспортнуто, имя уникально
            False - отказ от экспорта
            str - успешно экспортнуто, имя изменено
        '''
        if not full_path.endswith('.xlsx'):
            raise ValidationError("Incorrect file extension. Only '.xlsx' is available.")

        if isinstance(file_data, pd.core.frame.DataFrame):
            file_data = {one_list_name: file_data}
            pass
        elif isinstance(file_data, pd.core.series.Series):  # Если подна series - конвертнём
            try:
                file_data = pd.DataFrame(data=file_data.tolist(), index=file_data.index)
                file_data = {one_list_name: file_data}
            except BaseException as miss:
                raise ProcessingError('Series to DataFrame conversion failed. File export failed.') from miss

        elif isinstance(file_data, dict):
            for key in file_data.keys():  # Проверим, что каждый элемент является фреймом

                if isinstance(file_data[key], pd.core.frame.DataFrame):  # Если фрейм
                    pass
                elif isinstance(file_data[key], pd.core.series.Series):  # Если Series - конвертнём
                    try:
                        new_data = pd.DataFrame(data=file_data[key].tolist(), index=file_data[key].index)
                        file_data[key] = new_data
                    except BaseException as miss:
                        file_data.pop(file_data[key])
                        warn(f'Element "{key}" conversion Series to DataFrame failed. Error: {miss.args[0]}\nValue excluded.',
                             DeprecationWarning)
                else:  # Если говнотип
                    warn((f'Element "{key}" have wrong type: {type(file_data[key])}. Value excluded.' +
                          'Element must be Series or DataFrame.')
                         , DeprecationWarning)
                    file_data.pop(file_data[key])

            if file_data == {}:  # если словарь опустел
                raise ProcessingError('All dictionary elements were excluded due to errors.')

        else:
            raise ValidationError(f'file_data type must be Series or DataFrame. {type(file_data)} was passed. ' +
                                  'File export failed.')

        with self.mutex:
            name_shifted = False
            if self.check_access(path=full_path):
                if shift_name is None:
                    return False
                elif shift_name is True:
                    full_path = self.name_shifting(full_path=full_path, expansion='.json')
                    name_shifted = True

            # Выполним экспорт
            try:
                with pd.ExcelWriter(full_path, mode='w') as writer:  # Делаем "писатель файла"
                    for frame_key in file_data.keys():  # Пошли по индексу в словаре
                        if with_index:
                            if file_data[frame_key].index.name is None:
                                file_data[frame_key] = file_data[
                                    frame_key].copy()  # берём ссылку, чтобы не изменить объект
                                file_data[
                                    frame_key].index.name = 'index'  # ставим имя индекса (чтобы оно не было пустым)

                        file_data[frame_key].to_excel(writer, sheet_name=frame_key, encoding=encoding, index=with_index)
                    writer.save()
                    writer.close()

            except BaseException as miss:
                raise ProcessingError(f'File export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        if name_shifted:
            return full_path
        else:
            return True

    def write_sheet(self, file_data: pd.core.frame.DataFrame or pd.core.series.Series,
                    full_path: str,
                    sheet_name: str,
                    with_index: bool = True,
                    encoding: str = 'utf-8') -> True or str or None:
        '''
        Фнукия записывает лист в файл ".xlsx". Если лист отсутствовал, он будет добавлен.
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html

        :param file_data: данные для экспорта в файл DataFrame или Series
        :param full_path: полное имя файла
        :param sheet_name: имя листа, на который будет выполнен экспорт
        :param with_index: экспортировать ли индекс?
        :param one_list_name: имя "одного" листа. Если подан DataFrame или Series, а не словарь, то лист надо
            как-то назвать. Это его имя. Если подан словарь, в качестви имён листов будет взят индекс.
        :param encoding: кодировка файла
        :return:
        '''
        if not full_path.endswith('.xlsx'):
            raise ValidationError("Incorrect file extension. Only '.xlsx' is available.")

        if isinstance(file_data, pd.core.frame.DataFrame):
            pass
        elif isinstance(file_data, pd.core.series.Series):  # Если подна series - конвертнём
            try:
                file_data = pd.DataFrame(data=file_data.tolist(), index=file_data.index)
            except BaseException as miss:
                raise ProcessingError('Series to DataFrame conversion failed. File export failed.') from miss
        else:
            raise ValidationError(f'file_data type must be Series or DataFrame. {type(file_data)} was passed. ' +
                                  'File export failed.')

        file_data = {sheet_name: file_data}

        with self.mutex:
            # Выполним экспорт
            try:
                with pd.ExcelWriter(full_path, mode='a') as writer:  # Делаем "писатель файла"
                    for frame_key in file_data.keys():  # Пошли по индексу в словаре
                        if with_index:
                            if file_data[frame_key].index.name is None:
                                file_data[frame_key] = file_data[
                                    frame_key].copy()  # берём ссылку, чтобы не изменить объект
                                file_data[
                                    frame_key].index.name = 'index'  # ставим имя индекса (чтобы оно не было пустым)

                        file_data[frame_key].to_excel(writer, sheet_name=frame_key, encoding=encoding, index=with_index)
                    writer.save()
                    writer.close()

            except BaseException as miss:
                raise ProcessingError(f'Sheet export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        return
