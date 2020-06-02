from SystemCore.Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger

import os
from chardet.universaldetector import UniversalDetector

class StandartReader:
    '''
    Класс, реализующий каркас для объектов чтения/записи.

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

    '''

    def __init__(self, logger: CommonLoggingClient = None, parent_name: str = None,
                 save_loaded: bool = False):
        '''

        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        '''

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

        self.__save_loaded = save_loaded
        self._reset_loaded()  # "сбрасываем" словарь загруженных файлов.

    def connect_path(self, directory: str, file_name: str) -> str or None:
        '''

        :param directory:
        :param file_name:
        :return: строка полного пути или None при критической ошибке
        '''
        try:
            return os.path.join(directory, file_name)
        except BaseException:
            self.__to_log(message='Соединение полного пути файла провалено.',
                          logging_data={'directory': directory,
                                        'file_name': file_name},
                          logging_level='WARNING')
            return None

    def shift_name(self, file_name: str,
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
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def _Logger(self) -> CommonLoggingClient:
        '''
        Логер, использующийся в объекте

        :return: логер
        '''
        return self.__Logger

    @property
    def _to_log(self) -> object:
        '''
        Отдаёт функцию логирования, которая используется в работе

        :return: функция
        '''
        return self.__to_log

    @property
    def _my_name(self) -> str:
        '''
        Отдаёт строку с полным структурным навзванием модуля

        :return: строку
        '''
        return self.__my_name

    # ------------------------------------------------------------------------------------------------
    # Настройки чтения -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def save_loaded(self) -> bool:
        '''
        Сохраняются ли считываемые файлы?

        :return: bool статус
        '''
        return self.__save_loaded

    @save_loaded.setter
    def save_loaded(self, value: bool):
        '''
        Устанавливает детектор необходимости сохранения считанных файлов

        :param value: bool значение
        :return: ничего
        '''
        self.__save_loaded = value
        return

    @property
    def loaded(self) -> dict:
        '''
        Отдаёт копию словаря с загруженными файлами

        :return:
        '''
        return self.__loaded.copy()

    def _reset_loaded(self):
        '''
        Сбрасывает словарь "загруженных" файлов.

        :return:
        '''
        self.__loaded = {}
        return

    def get_loaded(self, full_path: str) -> object or None:
        '''
        Функция отдаёт объект по полному имени файла.

        :param full_path: полный путь к файлу
        :return: объект из файла или None, если таковой отсутствует
        '''
        # не стоит делать отдачу по "относительному пути", т.к. в разных каталогах это могут быть разные файлы
        try:
            return self.__loaded[full_path]
        except KeyError:
            self.__to_log(message='Запрошенный файл отсутствует среди сохранённых.',
                          logging_data={'full_path': full_path},
                          logging_level='WARNING')
            return None

    def __ad_loaded(self, full_path: str, data: object) -> bool:
        '''
        Добавление считанных данных в словарь

        :param full_path: полный путь к файлу
        :param data: данные
        :return: True - имя было уникально, добавлено (или данные совпали); False - имя было занято (данные не совпали),
            объект заменён.
        '''
        try:
            a = self.__loaded[full_path]

            if a == data:  # проверим идентичность
                return True  # Если данные идентичны, замена не делается!

            else:  # если данные отличаются
                self.__loaded[full_path] = data  # установим данные
                return False

        except KeyError:  # Если данных нет
            self.__loaded[full_path] = data
            return True

    # ------------------------------------------------------------------------------------------------
    # Проверки ---------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def check_assess(self, path: str) -> bool or None:
        '''
        Функция проверяет наличие файла или каталога на указанном пути

        :param path: полный путь каталога или файла
        :return: статус или None при критической ошибке
        '''
        try:
            return os.access(path, mode=os.F_OK)
        except BaseException:
            return None

    def get_encoding(self, full_path: str) -> str or None:
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
        except BaseException:
            self.__to_log(message='Определение кодировки файла провалено.',
                          logging_data={'full_path': full_path},
                          logging_level='ERROR')
            return None

    def __shift_name(self, full_path: str, expansion: str, number: int) -> str:
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

        while self.check_assess(path=self.__shift_name(full_path=full_path,
                                                       expansion=expansion,
                                                       number=retries)
                                ):  # Делаем цикл, который прервётся на уникальном имени файла
            retries += 1

        # Цикл закончится, когда имя файла не будет найдено
        export_name = self.__shift_name(full_path=full_path,
                                        expansion=expansion,
                                        number=retries)

        if retries:  # Если сдвиг был
            self.__to_log(message='Сдвиг имени файла выполнен.',
                          logging_data={'full_path': full_path,
                                        'new_name': export_name,
                                        'retries': retries},
                          logging_level='DEBUG')
        else:
            self.__to_log(message='Сдвиг имени файла не потребовался.',
                          logging_data={'full_path': full_path},
                          logging_level='DEBUG')

        return export_name  # Вернём имя "после сдвига"

    # ------------------------------------------------------------------------------------------------
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
