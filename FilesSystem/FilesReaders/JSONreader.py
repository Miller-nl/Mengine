from ...Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger
from .StandartReader import StandartReader

import json


class JSONreader(StandartReader):
    '''
    Класс для считывания и сохранения json объектов.

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
            write() - запись

            read() - чтение

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
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read(self, full_path: str, save_loaded: bool = None,
             encoding: str = None) -> object or None:
        '''
        Функция считывания csv файла

        :param full_path: полный путь к файлу
        :param save_loaded: сохранить ли загруженный файл? True - да, False - нет, None - использовать стандартную
            настройку (save_loaded)
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :return: считанный файл или None в случае ошибки
        '''

        return

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: object, full_path: str, shift_name: bool or None = True,
              ) -> True or str or None:
        '''
        Фнукия записывает данные в файл

        :param file_data: данные для экспорта в файл
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :return: True - успешно экспортнуто, имя уникально
            str - успешно экспортнуто, имя изменено
            None - ошибка экспорта
        '''

        return



