import os
import threading


from chardet.universaldetector import UniversalDetector
from Exceptions.ExceptionTypes import ProcessingError, ValidationError

def count_lines(full_path: str) -> int:
    '''
    Функция проверяет количество строк в файле.

    :param full_path: имя файла
    :return: количество строк
    '''
    with open(full_path) as file:
        lines = 0
        for line in file:
            lines += 1
    return lines


class FileIterator:
    '''
    Иттератор для чтения файла по строкам.
    Лучше использовать "next", чтобы файл закрылся после работы.
    '''

    def __iter__(self, ):
        return self

    def __init__(self, full_path: str,
                 encoding: str = 'utf-8',
                 start: int = 0, stop: int = None,
                 post_process_function: object = None):
        '''
        Функция отдаёт иттератор для чтения по строкам.

        :param full_path: полный путь к файлу
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :param start: первая строка
        :param stop: последняя строка
        :param post_process_function: функция для "пост обрботки" строки. Функция виде func(str)->str.
        :return: итератор по строкам itertools.islice
        '''
        self.__full_path = full_path
        self.__encoding = encoding

        try:
            self.__file = open(full_path, mode='r', encoding=encoding)
        except BaseException as miss:  # Если не получилось считать файл
            raise ProcessingError(f'File reading failed.\nfull_path: {full_path}\nencoding: {encoding}') from miss

        self.__post_process_function = post_process_function

        self.__counter = start
        if stop is None:
            stop = count_lines(full_path=full_path)
        self.__stop = stop

    def __next__(self):
        if self.__counter < self.__stop:
            self.__counter += 1
            try:
                line = self.__file.readline()
            except BaseException as miss:  # Если не получилось считать файл
                raise ProcessingError(f'Reading the next line failed.\nfull_path: {self.__full_path}\nencoding: {self.__encoding}') from miss

            if self.__post_process_function is not None:
                line = self.__post_process_function(line)
            return line
        else:
            self.__file.close()
            raise StopIteration


class CommonMethods:
    '''
    Класс, реализующий каркас для объектов чтения/записи.

    Методы и свойства:
        Имена и пути
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
        self.__mutex = threading.RLock()

    @property
    def mutex(self) -> threading.RLock:
        return self.__mutex

    @staticmethod
    def concat_path(directory: str, file_name: str) -> str or None:
        '''

        :param directory: каталог
        :param file_name: имя файла
        :return: строка полного пути или None при критической ошибке
        '''
        try:
            return os.path.join(directory, file_name)
        except BaseException as miss:
            raise ValueError('Path concatenation failed') from miss

    @staticmethod
    def extract_name(full_path: str) -> str:
        '''
        Функция извлекает имя файла из пути

        :param full_path: путь
        :return: имя файла
        '''
        return os.path.basename(full_path)

    @staticmethod
    def extract_extension(full_path: str) -> str:
        '''
        Функция извлекает расширение файла из пути

        :param full_path: путь
        :return: имя файла
        '''
        return os.path.splitext(full_path)[1]

    @staticmethod
    def shift_name(file_name: str,
                   number: int = 0) -> str:
        '''
        Функция модификации/уникализации имени файла. Нужна для единообразия форматирования

        :param file_name: исходное, не модифицированное имя файла.
        :param number: номер сдвига (на случай, если сдвиг надо делать более одного раза, т.к. варианты, соответствующие
            первым сдвигам, уже заняты).
        :return:
        '''
        name = file_name[:file_name.rfind('.')]
        expansion = file_name[file_name.rfind('.') + 1:]
        export_name = f'{name}({number}).{expansion}'

        return export_name

    # ------------------------------------------------------------------------------------------------
    # Проверки ---------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def check_access(path: str) -> bool or None:
        '''
        Функция проверяет наличие файла или каталога на указанном пути

        :param path: полный путь каталога или файла
        :return: статус или None при критической ошибке
        '''
        return os.access(path, mode=os.F_OK)

    @staticmethod
    def get_encoding(full_path: str) -> str:
        '''
        Проверка кодировки файла

        :param full_path: полный путь к файлу
        :return: кодировка или None в случае ошибки
        '''
        try:
            detector = UniversalDetector()
            with open(full_path, 'rb') as fh:
                for line in fh:
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
            encoding = detector.result['encoding']  # Получили кодировку
            return encoding
        except BaseException as miss:
            raise ProcessingError('Encoding detection error') from miss

    @staticmethod
    def __shift_name(full_path: str, expansion: str, number: int) -> str:
        '''
        Функция для коррекции имени файла (для единообразия).

        :param full_path: полный путь файла
        :param expansion: расширение файла
        :param number: номер "попытки". При number=0 модификация не происходит.
        :return:
        '''
        if number:
            export_name = full_path.replace(expansion, f' ({number})' + expansion)
            return export_name
        else:
            return full_path

    def name_shifting(self, full_path: str, expansion: str) -> str:
        '''
        Функция, позволяющая сдвинуть имя файла на уникальное. Если имя заведомо является уникальным, сдвига не
            произойдёт.

        :param full_path: полное имя файла
        :param expansion: расширение файла
        :return: новое имя файла
        '''
        retries = 0  # счётчик
        if not expansion.startswith('.'):  # Если расширение без точки
            expansion = '.' + expansion  # добавим её

        while self.check_access(path=self.__shift_name(full_path=full_path,
                                                       expansion=expansion,
                                                       number=retries)
                                ):  # Делаем цикл, который прервётся на уникальном имени файла
            retries += 1

        # Цикл закончится, когда имя файла не будет найдено
        export_name = self.__shift_name(full_path=full_path,
                                        expansion=expansion,
                                        number=retries)

        return export_name  # Вернём имя "после сдвига"
