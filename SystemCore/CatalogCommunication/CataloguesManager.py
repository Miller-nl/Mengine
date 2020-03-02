
import os  # для работы с файлами
import sys
import configparser
import datetime


from SystemCore.CatalogCommunication.DefoultCatalogs import main_files_catalog, data_catalogs


# https://docs.python.org/3.5/library/os.path.html#os.path.abspath


# Объект для менеджмента процесса
class CatalogsManager:
    '''
    Модуль для работы с каталогами. Его задача: создать схему каталогов и обсепечить работу с ней.

    Структура каталогов:
    "Основной каталог" -> "Каталог процесса" (по имени процесса) -> Подкаталог сессии (session_subdirectory) ->
        Папки для данных -> Файлы  или (Подкаталоги модулей сессии -> Файлы)

    Данные хранятся в объекте "configparser", при этом дефолтное значение секции хранится на опции "__section_path_name"
    Изменение структуры папок "на лету" невозможно по причине того, что переименовывание секции или опции может и,
        скорее всего, приведёт к проблемам, связанным с доступом к данным, находящимся в каталоге или подкаталогах
        секции.

        Папки для данных - "секция"

        "Подкаталоги модулей сессии" - опция

        Добавить функцию "запросить файлы"


    Методы и свойства



        _mistakes - список ошибок, полученных при работе с каталогами (.append(sys.exc_info()))
            #


    '''

    __section_path_name = 'section_path'  # Название опции с основным каталогом секции


    def __init__(self,
                 process_name: str,
                 parent_directory: str = None,
                 session_subdirectory: str = None):
        '''

        :param process_name: имя процесса. Именно по нему будет сгенерирован "основной подкаталог".
        :param main_path: основной каталог с данными. В нём будет создан подкаталог для процесса "process_name"
            процесса, в подкаталоге которого процесс будет хранить свои данные.
            Значение 'default' значит, что будет использован main_files_catalog, указанный в файле с менеджером.
        :param session_subdirectory: подкаталог main_process_path, в котором будет разворачиватсья стандартная схема папок для
            данной сессии процесса process_name.
            Это удобно для разделения данных от разных запусков модуля и тестирования. Если не задан - берётся
            "дата + время" запуска.
        '''

        self.__mistakes = []  # свой список ошибок

        self.__process_name = process_name
        self.__parent_directory = parent_directory

        if parent_directory is None:
            parent_directory = main_files_catalog  # Берём импортнутый каталог
        parent_directory = os.path.abspath(parent_directory)  # Форматнём путь
        self.__main_path = os.path.join(parent_directory, process_name)  # Установим "основной каталог" процесса

        if session_subdirectory is None:  # если не задано
            session_subdirectory = str(datetime.datetime.now()).replace(':', ';')  # Установим по времени запуска
        self.__session_subdirectory = session_subdirectory

        # Объект для хранения секций (основных подкаталогов) и опций (подкаталогов секций)
        self.__config = configparser.ConfigParser()










        #config.sections()

        # os.path.join()



        # Создадим глвный каталог
        self.__main_path = self.__create_process_path(main_path=main_path, subdirectory=session_subdirectory)

        # Заведём файл с настроками каталогов
        self.__catalogs = configparser.ConfigParser()
        self.__catalogs.read_dict(data_catalogs)  # Скормим в конфиг каталоги из словаря
        self.__catalogs_preparation()  # Воспроизведём каталоги конфига

    def __perpare_main_catalogs(self):
        '''
        Задача функции: проверить существование основных каталогов и, если потребуется, воспроизвести их.

        :return: статус выполнения
        '''

        if not os.access(self.main_process_path, mode=os.F_OK):  # Создадим основной каталог модуля, если его нет
            os.makedirs(self.main_process_path)

        if not os.access(self.main_process_path, mode=os.F_OK):  # Создадим каталог сесси, если его нет
            os.makedirs(self.main_process_path)
        return

    # ------------------------------------------------------------------------------------------------
    # Основные доступы -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def process_name(self) -> str:
        '''
        Имя сессии запуска

        :return:
        '''
        return self.__process_name

    @property
    def parent_directory(self) -> str:
        '''
        Отдаёт "родительский каталог", внутри которого находится подкаталог для процесса "main_process_path"
        :return: строка - путь
        '''
        return self.__parent_directory

    @property
    def main_process_path(self) -> str:
        '''
        Основной каталог процесса, в котором будут развёрнуты все нужные файлы.

        :return: строка - путь
        '''
        return self.__main_path

    @property
    def session_path(self) -> str:
        '''
        Полный путь к подкаталогу, в котором хранятся данные текущей сессии: файлы и папки сессий

        :return: строка - путь
        '''
        return os.path.join(self.main_process_path, self.__session_subdirectory)

    @property
    def _mistakes(self) -> list:
        '''
        Общий параметр
        Функция отдаёт ошибки, полученные при работе логера. Ошибки извлекаются через sys.exc_info().

        :return: копия спискаошибок
        '''
        return self.__mistakes.copy()

    # ------------------------------------------------------------------------------------------------
    # Работа с каталогами ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
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
            element = os.path.join(directory, element)  # Делаем абсолютный путь
            if os.path.isfile(element):  # Если это файл
                try:
                    os.remove(element)  # Удаляем его
                except BaseException:
                    errors += 1  # Крутанём счётчик ошибок

            else:  # Если это каталог
                self.__drop_directory(directory=element)  # Запросим его зачистку
                # Тут счётчик не надо - если были ошибки в подкаталогах, то try/except завалится

        # Теперь попробуем дропнуть саму директорию
        try:
            os.rmdir(directory)  # Пробуем удалить директорию
            if errors:  # Если были ошибки
                return None
            else:  # Если количество ошибок при удалении файлов - 0
                return True  # Вернём статус успешного овыполнения

        except OSError:  # исключая ошибку
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

    def get_section_path(self, section_name: str) -> str or None:
        '''
        Функция отдаёт каталог сеции.

        :param section_name: имя секции
        :return: полный путь или None, если нет запрошенной секции.
        '''
        # Проверим наличие секции
        if not self.check_section(section_name=section_name):
            return None
        else:  # Если секция есть
            return os.path.join(self.session_path, self.__config.get(section=section_name,
                                                                     option=self.__section_path_name))

    def check_section(self, section_name: str) -> bool:
        '''
        Функция проверяет, есть ли соответствующая секция

        :param section_name: имя секции
        :return: статус наличия секции
        '''
        return self.__config.has_section(section_name)

    def add_section(self, section_name: str,
                    section_folder: str = None) -> bool or None:
        '''
        Функция добавляет секцию в набор каталогов. Если секция есть, её "переименовывание" запрещено во избежание
        ошибок. Если добавление каталога провалено, секция не добавится.

        :param section_name: имя секции
        :param section_folder: папка секции. Если не задан - выбирается имя секции по дефолту.
        :return: True - секции не было, добавлена False - секция или папка есть; None - ошибка.
        '''
        if section_folder is None:  # Если папка не задана
            section_folder = section_name  # Берём имя за каталог

        if self.check_section(section_name=section_name):  # Если секция есть
            return False  # Вернём статус
        else:  # Если секции нет
            try:
                if not os.access(self.main_process_path, mode=os.F_OK):  # Создадим каталог секции, если его нет
                    os.makedirs(self.main_process_path)

                self.__config.add_section(section_name)  # Создаём секцию в настройках
                self.__config.set(section=section_name, option=self.__section_path_name,
                                  value=section_folder)  # Ставим каталог
            except BaseException:  # если был косяк
                self.__mistakes.append(sys.exc_info())  # Логируем
                return None

    def del_section(self, section_name: str,
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
            # Делаем удаление
            result = self.__drop_directory(directory=self.get_section_path(section_name=section_name))

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
    def get_options(self, section_name: str) -> list or None:
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

    def check_option(self, section_name: str, option_name: str) -> bool or None:
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

    def get_option_path(self, section_name: str, option_name: str) -> str or None:
        '''
        Функция отдаёт каталог опции.

        :param section_name: имя секции
        :param option_name: имя опции
        :return: строка с полным путём каталога или None, если нет секции или опции.
        '''

        if self.check_option(section_name=section_name, option_name=option_name) is not True:  #Проверим опцию
            path = os.path.join(self.get_section_path(section_name=section_name),
                                self.__config.get(section=section_name, option=option_name))
            return path
        else:  # Если нет секции или опции
            return None

    def add_option(self, section_name: str, option_name: str,
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
            option_folder = option_name

        check_option = self.check_option(section_name=section_name, option_name=option_name)  # Проверим наличие секции
        if check_option is False:  # Если опция есть, а секции нет
            self.__config.set(section=section_name, option=option_name, value=option_folder)  # Создадим секцию
            return True  # Закончим, вернув статус успешности

        elif check_option is True:  # Если опция есть
            return False  # вернём статус

        else:  # если там None (нет секции)
            return None  # вернём статус

    def del_option(self, section_name: str, option_name: str,
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
    '''
    Сделать параметры "Секция" и "Опция" = None. Если опция не задана, обрабатывается секция.
    
    Это функции "для удобства"
    
    Получения подкаталогов не надо! Только файлы
    '''
    def get_files_list(self, section_name: str) -> str or None:
        '''
        Функция отдаёт каталог сеции.

        :param section_name: имя секции
        :return: полный путь или None, если нет запрошенной секции.
        '''
        return



    # ------------------------------------------------------------------------------------------------
    # Получить файлы ---------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------




















    @property
    def sub_catalogs(self) -> configparser.ConfigParser:
        '''
        Функция отдаёт ссылку на объект с настройками подкаталогов.

        :return:
        '''
        return self.__catalogs

    # ------------------------------------------------------------------------------------------------
    # Работа с каталогами ----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def get_catalog(self, name: str) -> str:
        '''
        Отдаёт "основной каталог" каталог
        :param name:
        :return:
        '''














    # ------------------------------------------------------------------------------------------------
    # "Удобный" доступ к подкаталогам ----------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def logging_catalog(self, name: str = None) -> str or None:
        '''
        Функция отдаёт каталоги логгирования.

        :param name: имя подкаталога. Если не задано, берётся "основной". Вообще это "опция".
        :return: строка с полным путём или None
        '''
        if name is None:
            name = 'main'
        return self.get_subdirectory(section='logging', option=name)

    def data_catalog(self, name: str = None) -> str or None:
        '''
        Функция отдаёт каталоги для хранения данных.

        :param name: имя подкаталога. Если не задано, берётся "основной". Вообще это "опция".
        :return: строка с полным путём или None
        '''
        if name is None:
            name = 'main'
        return self.get_subdirectory(section='data', option=name)

    def sql_catalog(self, name: str = None) -> str or None:
        '''
        Функция отдаёт каталоги для хранения данных о запросах и таблицах.

        :param name: имя подкаталога. Если не задано, берётся "основной". Вообще это "опция". Доступны:
            failed_requests - "упавшие запросы";
            saved - "сохранённые данные".
        :return: строка с полным путём или None
        '''
        if name is None:
            name = 'main'
        return self.get_subdirectory(section='sql', option=name)

    def emergency_save(self, name: str = None) -> str or None:
        '''
        Функция отдаёт каталоги для сохранения данных в виде DO в случае критических ошибок при работе с большими
            объймами.

        :param name: имя подкаталога. Если не задано, берётся "основной". Вообще это "опция".
        :return: строка с полным путём или None
        '''
        if name is None:
            name = 'main'
        return self.get_subdirectory(section='emergency_save', option=name)

    # ------------------------------------------------------------------------------------------------
    # Преднастройка ----------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def __create_catalog(self, catalog: str) -> bool or None:
        '''
        Функция "добавляет" каталог для работы. Нужна для общности и упращения правок при изменении этого
        процесса.

        :param catalog: адрес каталога
        :return: был ли создан каталог? True - да, каталог был добавлен? False - нет, каталог уже был,
            None - ошибка.
        '''
        try:
            if not os.access(catalog, mode=os.F_OK):  # Если каталога нет
                os.makedirs(catalog)  # Создадим
                return True
            else:
                return False  # Если каталог был - вернём это
        except BaseException:
            return None

    def __create_process_path(self, main_path: str,
                              subdirectory: str = None) -> str or None:
        '''
        Функция создаёт "основной" подкаталог и возвращает его для установки в self.__main_path

        :param main_path: каталог для процесса. Значение 'default' значит, что он будет получен из Catalogs
        :param subdirectory: подкаталог, в котором будет разворачиватсья стандартная схема папок.
            Например, для тестирования.
        :return: ничего
        '''
        # Установим основной каталог
        if main_path == 'default':  # Если требуется получить дефльтный каталог
            main_path = main_files_catalog  # установим дефолтный каталог

        if not main_path.endswith('/'):  # Добавим слеш в конец
            main_path += '/'

        if subdirectory is None:  # Если подкаталог не задан
            subdirectory = ''
        else:  # Если задан
            if subdirectory.startswith('/'):
                subdirectory = subdirectory[1:]
            if not subdirectory.endswith('/'):
                subdirectory += '/'

        main_path = main_path + subdirectory + self.process_name  # Установим каталог для данного процесса
        if not main_path.endswith('/'):  # Добавим "слеш"
            main_path += '/'

        add_result = self.__create_catalog(catalog=main_path)  # Добавим каталог
        if isinstance(add_result, bool):  # Если каталог есть
            return main_path  # вернём
        else:  # Если это None
            return None  # Вернём "ошибку"

    def __catalogs_preparation(self):
        '''
        Функция воспроизводит систему подкаталогов внутри self.__main_path по self.__catalogs

        :return: ничего
        '''
        sections = self.__catalogs.sections()  # Берём "секции"
        for section in sections:  # Воспроизводим каталоги секций
            options = self.__catalogs.options(section)  # Берём опции секции
            for option in options:
                sub_dir = self.__catalogs.get(section=section, option=option)  # берём подкаталог
                # Отправляем в добавление
                self.__create_catalog(catalog=self.main_process_path + sub_dir)

        return

    # ------------------------------------------------------------------------------------------------
    # Создание и получение каталогов -----------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Проверить директорию - в системе.

    # Создать директорию, если её нет


    def add_subdirectory(self, catalog: str,
                         section: str,
                         option: str,
                         replace: bool = False) -> bool or None:
        '''
        Функция добавляет каталог во внутренний объект и создаёт его. Замены нет.

        :param catalog: Полный путь подкаталога, включая все его директории, кроме основной: self. main_process_path
        :param section: "секция" подкаталога (смысловая часть), как "logging", "sql" и прочие.
        :param option: "опция" - навзание подкаталога внутри его секции.
        :param replace: заменить ли имеющееся значение опции?
        :return: True - если новое значение было установлено без проблем, False - если опция секции была уже занята.
            None - при критической ошибке.
        '''
        # Предподготовим catalog
        if not catalog.endswith('/'):  # Если нет нужной "концовки"
            catalog += '/'  # Добавим
        if catalog.startswith('/'):  # Если начинается "неверно"
            catalog = catalog[1:]  # срежем

        # Проверим наличие секции
        try:
            self.__catalogs.add_section(section)  # Пробуем добавить секцию
        except configparser.DuplicateSectionError:  # ошибка "секция есть"
            pass  # добавлять ничего не надо

        # Проверим опцию
        result = True
        try:
            a = self.__catalogs.get(section=section, option=option)  # Пробуем получить опцию
            # Если секция есть

            if a == catalog:  # Если каталоги совпали
                return True  # Вернём,что всё ок

            elif replace:  # Если замена разрешена
                result = False  # Ставим, что "опция" была уже
                self.__catalogs.remove_option(section=section, option=option)
            else:
                return False  # Если замена не разрешена, верёнм "ошибку"
            #catalogs.remove_section()
        except configparser.NoOptionError:  # Если нет опции такой
            pass  # Чилим

        # Добавим опцию
        self.__catalogs.set(section=section, option=option, value=catalog)
        # и заведём каталог
        add_result = self.__create_catalog(self.main_process_path + catalog)  # Добавим каталог
        if add_result is None:  # Если была ошибка
            return None  # Вернём ошибку
        else:  # Если каталог есть
            return result  # верёнм результат

    def get_subdirectory(self, section: str,
                         option: str,) -> str or None:
        '''
        Функция выдаёт полный путь в подкаталог по catalog_index, если он есть.
        :param section: "секция" подкаталога (смысловая часть), как "logging", "sql" и прочие.
        :param option: "опция" - навзание подкаталога внутри его секции.
        :return: подкаталог, если он есть или был создан, или None, если его нет и он не был создан.
        '''
        try:
            return self.main_process_path + self.__catalogs.get(section=section, option=option)
        except BaseException:  # Если нет секции или опции
            return None  # результат - нет подкаталога

