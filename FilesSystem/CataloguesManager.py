import os  # для работы с файлами
import configparser

from Exceptions.ExceptionTypes import ProcessingError, ValidationError

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
        Работа с файлами
            main_path - "основной" каталог (в котором развёрнута структура папок).

            get_files_list() - получение списка файлов в секции или опции

            get_sub_catalogs_list() - получение списка подкаталогов в секции или опции

            move_file() - перенос файла

            check_access() - проверка доступа

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

        Имена и пути
            concat_path() - соединить каталог и имя файла

            extract_name() - выделить имя файла из пути

            extract_extension() - выделить расширение файла из пути

            shift_name() - функция модификации имени файла, если оно не является уникальным.

    '''

    __section_path_name = 'section_path'  # Название опции с основным каталогом секции

    def __init__(self, main_path: str):
        '''

        :param main_path: основной каталог с данными. В нём будет создан подкаталог для процесса "process_name"
            процесса, в подкаталоге которого процесс будет хранить свои данные.
        '''
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
    # Работа с каталогами ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def main_path(self) -> str:
        '''
        Основной каталог процесса, в котором будут развёрнуты все нужные файлы.

        :return: строка - путь
        '''
        return self.__main_path

    def __drop_directory(self, directory: str):
        '''
        Функция иттеративно удаляет все файлы в указанной директории, проверяет все её папки, выполняя удаление внутри
            них, после чего ударяет подкаталоги, а в завершении удаляет и саму директорию directory
        :param directory: директория, подлежащая удалению
        :return:
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
                except BaseException as miss:
                    raise ProcessingError('Directory deletion failed. File deletion error.') from miss

            else:  # Если это каталог
                self.__drop_directory(directory=file_name)  # Запросим его зачистку

        # Теперь попробуем дропнуть саму директорию
        try:
            os.rmdir(directory)  # Пробуем удалить директорию
        except OSError as miss:  # исключая ошибку
            raise ProcessingError('Directory deletion failed.') from miss

        return

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

    def get_section_path(self, section_name: str) -> str:
        '''
        Функция отдаёт каталог сеции.

        :param section_name: имя секции
        :return: полный путь или None, если нет запрошенной секции.
        '''
        # Проверим наличие секции
        if not self.check_section(section_name=section_name):
            raise configparser.NoSectionError(f'"{section_name}". Getting the path failed.')
        else:  # Если секция есть
            return os.path.join(self.main_path, self.__config.get(section=section_name,
                                                                  option=self.__section_path_name))

    def check_section(self, section_name: str) -> bool:
        '''
        Функция проверяет, есть ли соответствующая секция

        :param section_name: имя секции
        :return: статус наличия секции
        '''
        return self.__config.has_section(section_name)

    def add_section(self, section_name: str,
                    section_folder: str = None) -> bool:
        '''
        Функция добавляет секцию в набор каталогов. Если секция есть, её "переименовывание" запрещено во избежание
        ошибок. Если добавление каталога провалено, секция не добавится.

        :param section_name: имя секции
        :param section_folder: папка секции. Если не задан - выбирается имя секции по дефолту.
        :return: True - секции не было, добавлена; False - секция уже есть, добавление отменено.
        '''
        if section_folder is None:  # Если папка не задана
            section_folder = section_name  # Берём имя за каталог

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

            except BaseException as miss:  # если был косяк
                raise ProcessingError((f'Section adding error.\nsection_name: {section_name}' +
                                       f'\nsection_folder: {section_folder}')) from miss
        return True

    def del_section(self, section_name: str,
                    clear_disc: bool = False) -> bool:
        '''
        Функция удаляет секцию.

        :param section_name: имя секции
        :param clear_disc: очистить ли жёсткий диск?
        :return: True - если секция была и она удалена, данные с диска зачищены; False - секции не было.
        '''

        if not self.__config.has_section(section_name):  # Если секции нет
            return False  # Вернём статус

        elif clear_disc:  # Если секция есть и диск чистим
            section_path = self.get_section_path(section_name=section_name)
            self.__drop_directory(directory=section_path)  # Делаем удаление
            self.__config.remove_section(section_name)  # Зачистим секцию

            return True

        else:  # Если секция ест, но диск не чистим
            self.__config.remove_section(section_name)  # Зачистим секцию
            return True

    # ------------------------------------------------------------------------------------------------
    # Работа с опциями -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_options(self, section_name: str) -> list:
        '''
        Функция отдаёт список опций секции. Если опций нет, то список будет пуст.
        Если указана несуществующия секция - функция сообщит об ошибке.

        :param section_name: имя секции, которая нас интересует
        :return: список с опциями (может быть пуст).
        '''
        try:
            options_list = self.__config.options(section_name)
            options_list.pop(0)  # дропаем "__section_path_name" - это "нулевая опция"
            return options_list
        except BaseException as miss:
            raise ProcessingError(f'Retrieving a list of options for section "{section_name}" failed.') from miss

    def check_option(self, section_name: str, option_name: str) -> bool:
        '''
        Проверка наличия опции.

        :param section_name: имя секции
        :param option_name: имя опции
        :return: True - секция есть, опция есть; False - секция есть, опции нет;.
        '''
        if not self.check_section(section_name=section_name):  # если нет секции
            raise configparser.NoSectionError(f'"{section_name}". Check failed.')
        else:  # Если она есть
            return self.__config.has_option(section=section_name, option=option_name)  # отдаём статус опции

    def get_option_path(self, section_name: str, option_name: str) -> str:
        '''
        Функция отдаёт каталог опции.

        :param section_name: имя секции
        :param option_name: имя опции
        :return: строка с полным путём каталога или None, если нет секции или опции.
        '''
        check_result = self.check_option(section_name=section_name, option_name=option_name)
        if check_result is True:  # Проверим опцию
            path = os.path.join(self.get_section_path(section_name=section_name),
                                self.__config.get(section=section_name, option=option_name))
            return path
        else:  # Если он False
            raise configparser.NoOptionError(f'{option_name}',
                                             section=section_name)

    def add_option(self, section_name: str, option_name: str,
                   option_folder: str = None):
        '''
        Функция добавляет опцию в соответствующую секцию

        :param section_name: имя секции
        :param option_name: имя опции
        :param option_folder: подкаталог опции. Если не задан, берётся option_name
        :return:
        '''
        if option_folder is None:  # Если нет подкаталога
            option_folder = option_name

        check_option = self.check_option(section_name=section_name, option_name=option_name)  # Проверим наличие опции
        if check_option is False:  # Если секция есть, а опции нет

            try:
                option_path = os.path.join(self.main_path, self.get_section_path(section_name=section_name),
                                           option_folder)
                if not os.access(option_path, mode=os.F_OK):  # Создадим каталог опции, если его нет
                    os.makedirs(option_path)
                self.__config.set(section=section_name, option=option_name, value=option_folder)  # Создадим опцию

            except BaseException as miss:  # если был косяк
                raise ProcessingError('Failed to add "option" to directory set.\n' +
                                       f'section_name: {section_name}\nmain_path: {self.main_path}\n' +
                                       f'section_path: {self.get_section_path(section_name=section_name)}\n' +
                                      'option_folder: {option_folder}') from miss
        return

    def del_option(self, section_name: str, option_name: str,
                   clear_disc: bool = False):
        '''
        Удаление опции, включая все файлы в ней!

        :param section_name: имя секции
        :param option_name: имя опции
        :param clear_disc: очистить ли жёсткий диск?
        :return:
        '''
        check_option = self.check_option(section_name=section_name, option_name=option_name)  # Проверим наличие секции
        if check_option is False:  # Если опция есть, а секции нет
            raise configparser.NoOptionError(f'{option_name}',
                                             section=section_name)

        elif check_option is True:  # Если опция есть
            if clear_disc:  # Если диск зачищать нужно
                # Делаем удаление
                self.__drop_directory(directory=self.get_option_path(section_name=section_name,
                                                                     option_name=option_name))
                # если каталога секции не было или он удалён успешно
                self.__config.remove_option(section=section_name, option=option_name)

            else:  # Если не нужно чистить диск
                self.__config.remove_option(section=section_name, option=option_name)

        return

    # ------------------------------------------------------------------------------------------------
    # Имена и пути -----------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def concat_path(directory: str, file_name: str) -> str or None:
        '''
        Соединяет путь и имя файла

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
    # Работа с файлами -------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def check_access(path: str) -> bool:
        '''
        Функция проверяет наличие файла или каталога на указанном пути

        :param path: полный путь каталога или файла
        :return: статус наличия
        '''
        return os.access(path, mode=os.F_OK)

    def move_file(self,
                  file_name: str,
                  location: str,
                  new_location: str,
                  create_new_location: bool = False):
        '''
        Функция переносит файл из старого расположения в новое.

        :param file_name: имя файла
        :param location: старое расположение
        :param new_location: новое
        :param create_new_location: создать ли новый каталог, если его нет?
        :return:
        '''
        try:
            old_name = self.concat_path(directory=location, file_name=file_name)
            if self.check_access(self.concat_path(directory=location, file_name=file_name)):
                if not self.check_access(new_location):
                    if create_new_location:
                        os.makedirs(new_location, mode=0o777, exist_ok=False)
                    else:
                        raise ValueError(f'File moving error. Folder "{new_location}" does not exist.')
                if self.check_access(self.concat_path(directory=new_location, file_name=file_name)):
                    raise ValueError(f'File moving error.' +
                                     f'A file with name "{file_name}" already exists in the directory "{new_location}".')

                # делаем перенос
                os.rename(old_name,
                          self.concat_path(directory=new_location, file_name=file_name))

            else:
                raise ValueError(f'File moving error. No access to file "{old_name}".')

        except BaseException as miss:
            raise ProcessingError(f'File moving from "{location}" to "{new_location}" failed.') from miss
        return

    def get_files_list(self, section_name: str or int,
                       option_name: str or int = None,
                       extension: str = None,
                       full_path: bool = True) -> list:
        '''
        Функция отдаёт список имён файлов сеции, если не задана опция. Если опция указана, отдаются файлы из опции.

        :param section_name: имя секции
        :param option_name: имя опции. Если не задано, берутся
        :param extension: расширение файлов. Если не задано - берутся все.
        :param full_path: регулирует, в каком виде имена попадут в экспорт: полный путь (true)
            или только имя файла (false)
        :return: список имён файлов.
        '''

        if option_name is None:
            path = self.get_section_path(section_name=section_name)
        else:
            path = self.get_option_path(section_name=section_name, option_name=option_name)

        export_list = []  # экспортынй лист
        for element in os.listdir(path=path):
            element_path = os.path.join(path, element)  # Делаем абсолютный путь
            if os.path.isfile(element_path):  # Если это файл

                if extension is not None:  # если учитываем расширение
                    if self.extract_extension(element_path) != extension:
                        continue

                if full_path:  # если берём полный путь
                    export_list.append(element_path)
                else: # или берём только имя
                    export_list.append(element)

        return export_list  # отдаём результат

    def get_sub_catalogs_list(self, section_name: str,
                              option_name: str = None,
                              full_path: bool = True) -> list:
        '''
        Функция отдаёт список имён подкаталогов сеции, если не задана опция. Если опция указана, отдаются подкаталоги
            из опции.

        :param section_name: имя секции
        :param option_name: имя опции. Если не задана, берётся сама секция.
        :param full_path: регулирует, в каком виде имена попадут в экспорт: полный путь (true)
            или только имя файла (false)
        :return: список имён подкаталогов.
        '''
        if option_name is None:
            path = self.get_section_path(section_name=section_name)
        else:
            path = self.get_option_path(section_name=section_name, option_name=option_name)

        export_list = []  # экспортынй лист
        for element in os.listdir(path=path):
            element_path = os.path.join(path, element)  # Делаем абсолютный путь
            if not os.path.isfile(element_path):  # Если это не файл (папка)
                if full_path:  # если берём полный путь
                    export_list.append(element_path)
                else:  # или берём только имя
                    export_list.append(element)

        return export_list  # отдаём результат