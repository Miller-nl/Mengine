from Exceptions.ExceptionTypes import ProcessingError
from .Common import CommonMethods

class StandartReader(CommonMethods):
    '''
    Класс, реализующий каркас для объектов чтения/записи.

    Методы и свойства:

        concat_path() - соединить каталог и имя файла

        extract_name() - выделить имя файла из пути

        extract_extension() - выделить расширение файла из пути

        shift_name() - функция модификации имени файла, если оно не является уникальным.

        Проверки
            check_access() - проверка доступа

            get_encoding() - получить кодировку файла

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
             encoding: str = None) -> object:
        '''
        Функция считывания файла

        :param full_path: полный путь к файлу
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :return: контент файла
        '''
        if not self.check_access(path=full_path):
            raise ProcessingError('No access to file')

        with self.mutex:
            # определим кодировку файла
            if encoding is None:
                encoding = self.get_encoding(full_path=full_path)

            # читаем
            try:
                with open(full_path, mode='r', encoding=encoding) as file:
                    result = file.read()
            except BaseException as miss:
                raise ProcessingError(f'File reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss
        return result

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: object, full_path: str, shift_name: bool or None = True,
              encoding: str = 'utf-8') -> bool or str:
        '''
        Фнукия записывает данные в файл

        :param file_data: данные для экспорта в файл
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :param encoding: кодировка
        :return: True - успешно экспортнуто, имя уникально
            False - отказ от экспорта
            str - успешно экспортнуто, имя изменено
        '''
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
                    file.write(file_data)
                    file.flush()

            except BaseException as miss:
                raise ProcessingError(f'File export failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        if name_shifted:
            return full_path
        else:
            return True
