from .Common import CommonMethods, FileIterator
from Exceptions.ExceptionTypes import ProcessingError, ValidationError

import json


class JSONL(CommonMethods):
    '''
    Класс для считывания и сохранения jsonlines объектов.

    Методы и свойства:
        Имена и пути
            concat_path() - соединить каталог и имя файла

            extract_name() - выделить имя файла из пути

            extract_extension() - выделить расширение файла из пути

            shift_name() - функция модификации имени файла, если оно не является уникальным.

        Проверки
            check_access() - проверка доступа

            get_encoding() - получить кодировку файла

        Настройки считывания
            save_loaded - сохранять ли считанные файлы?

            loaded - словарь сохранённых файлов

            _reset_loaded - обновить словарь сохранённых файлов

        Чтение - запись
            read() - чтение

            read_by_lines() - возвращает итерратор для чтения по строкам

            write() - запись

            write_line() - добавить строку
    '''

    def __init__(self, save_loaded: bool = False):
        '''

        :param save_loaded: сохоанять ли считанные файлы?
        '''

        # Выполним стандартный init
        CommonMethods.__init__(self, save_loaded=save_loaded)

    # ------------------------------------------------------------------------------------------------
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read(self, full_path: str, save_loaded: bool = None,
             encoding: str = 'utf-8') -> object:
        '''
        Функция считывания jsonl файла

        :param full_path: полный путь к файлу
        :param save_loaded: сохранить ли загруженный файл? True - да, False - нет, None - использовать стандартную
            настройку (save_loaded)
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :return: считанный файл в виде JSON объекта
        '''
        if not full_path.endswith('.jsonl'):
            raise ValidationError("Incorrect file extension. Only '.jsonl' is available.")

        with self.mutex:
            if not self.check_access(path=full_path):
                raise ProcessingError('No access to file')

            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)

            # читаем
            try:
                with open(full_path, mode='r', encoding=encoding) as file:
                    result = []
                    for data_string in file:
                        result.append(json.loads(data_string))
            except BaseException as miss:  # Если не получилось считать файл
                raise ProcessingError(f'File reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        if (save_loaded is None and self.save_loaded) or save_loaded is True:
            self._ad_loaded(full_path=full_path,
                            data=result)

        return result

    def read_by_lines(self, full_path: str,
                      encoding: str = 'utf-8',
                      start: int = 0, stop: int = None) -> FileIterator:
        '''
        Функция отдаёт иттератор для чтения по строкам.

        :param full_path: полный путь к файлу
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param start: первая строка
        :param stop: последняя строка. None - читать до конца.
        :return: итератор по строкам FileIterator
        '''
        if not full_path.endswith('.jsonl'):
            raise ValidationError("Incorrect file extension. Only '.jsonl' is available.")

        with self.mutex:
            if not self.check_access(path=full_path):
                raise ProcessingError('No access to file')

            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)

            return FileIterator(full_path=full_path, encoding=encoding,
                                start=start, stop=stop,
                                post_process_function=json.loads)

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: object, full_path: str, shift_name: bool or None = True,
              encoding: str = 'utf-8') -> bool or str:
        '''
        Фнукия записывает данные в файл jsonl

        :param file_data: данные для экспорта в файл
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :param encoding: кодировка
        :return: True - успешно экспортнуто, имя уникально
            False - отказ от экспорта
            str - успешно экспортнуто, имя изменено
        '''
        if not full_path.endswith('.jsonl'):
            raise ValidationError("Incorrect file extension. Only '.jsonl' is available.")

        with self.mutex:
            name_shifted = False
            if self.check_access(path=full_path):  # если есть файл и мы не дописываем в конец
                if shift_name is None:
                    return False
                elif shift_name is True:
                    full_path = self.name_shifting(full_path=full_path, expansion='.json')
                    name_shifted = True

            # пишем
            try:
                with open(full_path, mode='w', encoding=encoding) as file:
                    json.dump(file_data, file)
                    file.write('\n')
                    file.flush()

            except BaseException as miss:
                raise ProcessingError(f'File export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        if name_shifted:
            return full_path
        else:
            return True

    def write_line(self, file_data: object, full_path: str,
                   encoding: str = 'utf-8'):
        '''
        Фнукия записывает строку в файл. Если файл отсутствовал, он будет создан.

        :param file_data: данные для экспорта в файл
        :param full_path: полное имя файла
        :param encoding: кодировка
        :return:
        '''
        if not full_path.endswith('.jsonl'):
            raise ValidationError("Incorrect file extension. Only '.jsonl' is available.")

        with self.mutex:
            # пишем
            try:
                with open(full_path, mode='a', encoding=encoding) as file:  # Делаем экспорт
                    json.dump(file_data, file)
                    file.write('\n')
                    file.flush()

            except BaseException as miss:
                raise ProcessingError(f'Line export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        return