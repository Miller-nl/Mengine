from .Common import CommonMethods
from Exceptions.ExceptionTypes import ProcessingError, ValidationError

import pandas as pd


class CSV(CommonMethods):
    '''
    Класс для считывания и сохранения csv объектов.

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

            read() - чтение
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
             index_column_name: str = None,
             sep: str = ';'
             ) -> pd.core.frame.DataFrame:
        '''
        Функция считывания csv файла

        :param full_path: полный путь к файлу
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param index_column_name: имя колонки с названием индекса
        :param sep: - разделитель в файле
        :return: считанный файл
        '''
        if not full_path.endswith('.csv'):
            raise ValidationError("Incorrect file extension. Only '.csv' is available.")

        with self.mutex:
            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)


            try:  # Считаем
                with open(full_path, 'r', encoding=encoding) as file:
                    result = pd.read_csv(filepath_or_buffer=file,
                                         sep=sep, encoding=encoding, index_col=index_column_name,
                                         engine='python')  # считаем его

            except BaseException as miss:  # Если не получилось считать файл
                raise ProcessingError(f'File reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        return result

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: pd.core.frame.DataFrame or pd.core.series.Series,
              full_path: str, shift_name: bool or None = True,
              sep: str = ';', with_index: bool = True,
              encoding: str = 'utf-8') -> bool or str:
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
            False - отказ от экспорта
            str - успешно экспортнуто, имя изменено
        '''
        if not full_path.endswith('.csv'):
            raise ValidationError("Incorrect file extension. Only '.csv' is available.")


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
                if with_index:
                    if file_data.index.name is None:
                        index_label = 'index'
                    else:
                        index_label = file_data.index.name
                else:
                    index_label=None

                file_data.to_csv(path_or_buf=full_path, sep=sep, encoding=encoding,
                                 index=with_index,
                                 index_label=index_label)

            except BaseException as miss:
                raise ProcessingError(f'File export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        if name_shifted:
            return full_path
        else:
            return True
