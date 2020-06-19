
import os  # для работы с файлами
import sys
import configparser

from ..Logging.CommonLoggingClient import CommonLoggingClient, prepare_logger

# Протянуть логер
# Протянуть "извлечь схему из каталога"
# Добавить статичные функции создания/удаления каталога и файлов в нём


class CatalogsManager:
    '''
    Модуль для работы с каталогами. Его задача: создать схему каталогов и обсепечить работу с ней.

    Структура каталогов:
    "Основной каталог" -> "Секции" -> файлы секкции/"Опции" -> файлы опцииы)

    Данные хранятся в объекте "configparser", при этом дефолтное значение секции хранится на опции "__section_path_name"
    Изменение структуры папок "на лету" невозможно по причине того, что переименовывание секции или опции может и,
        скорее всего, приведёт к проблемам, связанным с доступом к данным, находящимся в каталоге или подкаталогах
        секции.

        Папки для данных - "секция"

        "Подкаталоги модулей сессии" - опция

    Важно, что при добавлении каталогов для секций и опций не производится проверка существования каталогов, то есть:
        несколько процессов или запусков могут работать в одной и директории с одинаковыми папками. Это сделано для
        универсальности.

    Методы и свойства
        Логирование
            _Logger - логгер

            _sub_module_name - "под имя", использующееся при логировании

            _to_log - функция логирования

        Работа с файлами
            main_path - "основной" каталог (в котором развёрнута структура папок).

            get_files_list() - получение списка файлов в секции или опции

            get_sub_catalogs_list() - получение списка подкаталогов в секции или опции

        Секции
            sections - список названий секций

            check_section() - проверка существования секции

            get_section_path() - получение абсолютного каталога секции

            add_section() - добавление секции

            del_section() - удаление секции

        Опции
            get_options() - получение опций секции

            check_option() - проверка наличия опции

            get_option_path() - получение абсолютного каталога опции

            add_option() - добавление опции

            del_option() - удаление опции

    '''

    __section_path_name = 'section_path'  # Название опции с основным каталогом секции

    def __init__(self, main_path: str,
                 logger: CommonLoggingClient = None, parent_name: str = None):
        '''

        :param main_path: основной каталог с данными. В нём будет создан подкаталог для процесса "process_name"
            процесса, в подкаталоге которого процесс будет хранить свои данные.
        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        '''

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)

        self.__main_path = os.path.abspath(main_path)  # Форматнём путь

        # Объект для хранения секций (основных подкаталогов) и опций (подкаталогов секций)
        self.__config = configparser.ConfigParser()

        self.__prepare_main_path()  # подготовим основные каталоги

    def __prepare_main_path(self):
        '''
        Задача функции: проверить и создать при необходимости основной каталог со всеми вышестоящими каталогами.

        :return: ничего
        '''
        if not os.access(self.main_path, mode=os.F_OK):  # Создадим основной каталог модуля, если его нет
            os.makedirs(self.main_path)
        return

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
    # Работа с каталогами ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def main_path(self) -> str:
        '''
        Основной каталог процесса, в котором будут развёрнуты все нужные файлы.

        :return: строка - путь
        '''
        return self.__main_path

    def __drop_directory(self, directory: str) -> bool or None:
        '''
        Функция иттеративно удаляет все файлы в указанной директории, проверяет все её папки, выполняя удаление внутри
            них, после чего ударяет подкаталоги, а в завершении удаляет и саму директорию directory
        :param directory: директория, подлежащая удалению
        :return: статус наличия ошибок. True - нет ошибок, False - каталога нет; None - при удалении встречены ошибки.
        '''
        if not os.access(path=directory, mode=os.F_OK):  # проверим каталог
            return False  # вернём ошибку

        objects_list = os.listdir(directory)  # Полуичм список объектов в каталоге
        errors = 0
        for element in objects_list:  # Погнали по объектам
            file_name = os.path.join(directory, element)  # Делаем абсолютный путь
            if os.path.isfile(file_name):  # Если это файл
                try:
                    os.remove(file_name)  # Удаляем его
                except BaseException:
                    self.__to_log(message='Ошибка удаления файла.',
                                  logging_data={'file_name': file_name},
                                  logging_level='ERROR')

                    errors += 1  # Крутанём счётчик ошибок

            else:  # Если это каталог
                self.__drop_directory(directory=file_name)  # Запросим его зачистку
                # Тут счётчик не надо - если были ошибки в подкаталогах, то try/except завалится

        # Теперь попробуем дропнуть саму директорию
        try:
            os.rmdir(directory)  # Пробуем удалить директорию
            if errors:  # Если были ошибки
                return None
            else:  # Если количество ошибок при удалении файлов - 0
                return True  # Вернём статус успешного овыполнения

        except OSError:  # исключая ошибку
            self.__to_log(message='Ошибка удаление директории.',
                          logging_data={'directory': directory},
                          logging_level='ERROR')
            return None


        # Получим список подкаталогов

        # os.rmdir(path, *, dir_fd=None) - удаляет пустую директорию.

    # ------------------------------------------------------------------------------------------------
    # Работа с секциями ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def sections(self) -> list:
        '''
        Получение секций. Секции получаются в виде списка названий, не путей - путь запросить отдельно.

        :return: список с названиями секций
        '''
        return self.__config.sections()

    def get_section_path(self, section_name: str or int) -> str or None:
        '''
        Функция отдаёт каталог сеции.

        :param section_name: имя секции
        :return: полный путь или None, если нет запрошенной секции.
        '''
        # Проверим наличие секции
        if not self.check_section(section_name=section_name):
            return None
        else:  # Если секция есть
            return os.path.join(self.main_path, self.__config.get(section=section_name,
                                                                  option=self.__section_path_name))

    def check_section(self, section_name: str or int) -> bool:
        '''
        Функция проверяет, есть ли соответствующая секция

        :param section_name: имя секции
        :return: статус наличия секции
        '''
        return self.__config.has_section(section_name)

    def add_section(self, section_name: str or int,
                    section_folder: str = None) -> bool or None:
        '''
        Функция добавляет секцию в набор каталогов. Если секция есть, её "переименовывание" запрещено во избежание
        ошибок. Если добавление каталога провалено, секция не добавится.

        :param section_name: имя секции
        :param section_folder: папка секции. Если не задан - выбирается имя секции по дефолту.
        :return: True - секции не было, добавлена False - секция или папка есть, добавление отменено; None - ошибка.
        '''
        if section_folder is None:  # Если папка не задана
            section_folder = str(section_name)  # Берём имя за каталог

        if self.check_section(section_name=section_name):  # Если секция есть
            return False  # Вернём статус
        else:  # Если секции нет
            try:
                section_path = os.path.join(self.main_path, section_folder)

                if not os.access(section_path, mode=os.F_OK):  # Создадим каталог секции, если его нет
                    os.makedirs(section_path)

                self.__config.add_section(section_name)  # Создаём секцию в настройках
                self.__config.set(section=section_name, option=self.__section_path_name,
                                  value=section_folder)  # Ставим каталог
                return True
            except BaseException:  # если был косяк
                self.__to_log(message='Добавление секции в набор каталогов провалено.',
                              logging_data={'section_name': section_name,
                                            'section_folder': section_folder},
                              logging_level='ERROR')
                return None

    def del_section(self, section_name: str or int,
                    clear_disc: bool = False) -> bool or None:
        '''
        Функция удаляет секцию.

        :param section_name: имя секции
        :param clear_disc: очистить ли жёсткий диск?
        :return: True - если секция была и она удалена, данные с диска зачищены; False - секции не было;
            None - ошибка удаления секции или зачистки данных, если последняя запрошена.
        '''

        if not self.__config.has_section(section_name):  # Если секции нет
            return False  # Вернём статус
        elif clear_disc:  # Если секция есть и диск чистим
            section_path = self.get_section_path(section_name=section_name)
            result = self.__drop_directory(directory=section_path)  # Делаем удаление

            if result is None:  # если были ошибки
                return None
            else:  # если каталога секции не было или он удалён успешно
                self.__config.remove_section(section_name)  # Зачистим секцию
                return True
        else:  # Если секция ест, но диск не чистим
            self.__config.remove_section(section_name)  # Зачистим секцию
            return True

    # ------------------------------------------------------------------------------------------------
    # Работа с опциями -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_options(self, section_name: str or int) -> list or None:
        '''
        Функция отдаёт список опций секции. Если опций нет, то список будет пуст.
        Если указана несуществующия секция - функция сообщит об ошибке.

        :param section_name: имя секции, которая нас интересует
        :return: список с опциями (может быть пуст) или None.
        '''
        try:
            return self.__config.options(section_name)
        except configparser.NoSectionError:
            return None

    def check_option(self, section_name: str or int, option_name: str or int) -> bool or None:
        '''
        Проверка наличия опции.

        :param section_name: имя секции
        :param option_name: имя опции
        :return: True - секция есть, опция есть; False - секция есть, опции нет; None - нет секции.
        '''
        if not self.check_section(section_name=section_name):  # если нет секции
            return None
        else:  # Если она есть
            return self.__config.has_option(section=section_name, option=option_name)  # отдаём статус опции

    def get_option_path(self, section_name: str or int, option_name: str or int) -> str or None:
        '''
        Функция отдаёт каталог опции.

        :param section_name: имя секции
        :param option_name: имя опции
        :return: строка с полным путём каталога или None, если нет секции или опции.
        '''

        if self.check_option(section_name=section_name, option_name=option_name) is not True:  # Проверим опцию
            path = os.path.join(self.get_section_path(section_name=section_name),
                                self.__config.get(section=section_name, option=option_name))
            return path
        else:  # Если нет секции или опции
            return None

    def add_option(self, section_name: str or int, option_name: str or int,
                   option_folder: str = None) -> bool or None:
        '''
        Функция добавляет опцию в соответствующую секцию

        :param section_name: имя секции
        :param option_name: имя опции
        :param option_folder: подкаталог опции. Если не задан, берётся option_name
        :return: статус выполнения: True - опции не было, создана; False - опция была, действий не выполнено;
            None - ошибка (в том числе - "отсутствует секция")
        '''
        if option_folder is None:  # Если нет подкаталога
            option_folder = str(option_name)

        check_option = self.check_option(section_name=section_name, option_name=option_name)  # Проверим наличие секции
        if check_option is False:  # Если опция есть, а секции нет

            try:
                option_path = os.path.join(self.main_path, self.get_section_path(section_name=section_name),
                                           option_folder)
                if not os.access(option_path, mode=os.F_OK):  # Создадим каталог опции, если его нет
                    os.makedirs(option_path)
                self.__config.set(section=section_name, option=option_name, value=option_folder)  # Создадим опцию
                return True  # Закончим, вернув статус успешности

            except BaseException:  # если был косяк
                self.__to_log(message='Добавление секции в набор каталогов провалено.',
                              logging_data={'section_name': section_name,
                                            'main_path': self.main_path,
                                            'section_path': self.get_section_path(section_name=section_name),
                                            'option_folder': option_folder,
                                            },
                              logging_level='ERROR')
                return None

        elif check_option is True:  # Если опция есть
            return False  # вернём статус

        else:  # если там None (нет секции)
            return None  # вернём статус

    def del_option(self, section_name: str or int, option_name: str or int,
                   clear_disc: bool = False) -> bool or None:
        '''
        Удаление опции, включая все файлы в ней!

        :param section_name: имя секции
        :param option_name: имя опции
        :param clear_disc: очистить ли жёсткий диск?
        :return: True - опция есть, удалена; False - секция есть, опции нет, не удалена опция;
            None - нет секции, не удалена опция.
        '''
        check_option = self.check_option(section_name=section_name, option_name=option_name)  # Проверим наличие секции
        if check_option is False:  # Если опция есть, а секции нет
            return False  # Закончим

        elif check_option is True:  # Если опция есть
            if clear_disc:  # Если диск зачищать нужно
                # Делаем удаление
                result = self.__drop_directory(directory=self.get_option_path(section_name=section_name,
                                                                              option_name=option_name))
                if result is None:  # если были ошибки
                    return None
                else:  # если каталога секции не было или он удалён успешно
                    self.__config.remove_option(section=section_name, option=option_name)
                    return True

            else:  # Если не нужно чистить диск
                self.__config.remove_option(section=section_name, option=option_name)
                return True  # вернём статус

        else:  # если там None (нет секции)
            return None  # вернём статус

    # ------------------------------------------------------------------------------------------------
    # Получить список файлов -------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_files_list(self, section_name: str or int,
                       option_name: str or int = None,
                       full_path: bool = True) -> str or None:
        '''
        Функция отдаёт список имён файлов сеции, если не задана опция. Если опция указана, отдаются файлы из опции.

        :param section_name: имя секции
        :param option_name: имя опции. Если не задано, берутся
        :param full_path: регулирует, в каком виде имена попадут в экспорт: полный путь (true)
            или только имя файла (false)
        :return: список имён файлов; None - если нет секции/опции/не существует каталог.
        '''
        if option_name is None:
            path = self.get_section_path(section_name=section_name)
        else:
            path = self.get_option_path(section_name=section_name, option_name=option_name)

        if path is None:  # если у нас ошибка получения каталога
            return None

        export_list = []  # экспортынй лист
        for element in os.listdir(path=path):
            element_path = os.path.join(path, element)  # Делаем абсолютный путь
            if os.path.isfile(element_path):  # Если это файл
                if full_path:  # если берём полный путь
                    export_list.append(element_path)
                else: # или берём только имя
                    export_list.append(element)
        return export_list  # отдаём результат

    def get_sub_catalogs_list(self, section_name: str or int,
                              option_name: str or int = None,
                              full_path: bool = True) -> str or None:
        '''
        Функция отдаёт список имён подкаталогов сеции, если не задана опция. Если опция указана, отдаются подкаталоги
            из опции.

        :param section_name: имя секции
        :param option_name: имя опции. Если не задано, берутся
        :param full_path: регулирует, в каком виде имена попадут в экспорт: полный путь (true)
            или только имя файла (false)
        :return: список имён подкаталогов; None - если нет секции/опции/не существует каталог.
        '''
        if option_name is None:
            path = self.get_section_path(section_name=section_name)
        else:
            path = self.get_option_path(section_name=section_name, option_name=option_name)

        if path is None:  # если у нас ошибка получения каталога
            return None

        export_list = []  # экспортынй лист
        for element in os.listdir(path=path):
            element_path = os.path.join(path, element)  # Делаем абсолютный путь
            if not os.path.isfile(element_path):  # Если это не файл (папка)
                if full_path:  # если берём полный путь
                    export_list.append(element_path)
                else:  # или берём только имя
                    export_list.append(element)
        return export_list  # отдаём результат