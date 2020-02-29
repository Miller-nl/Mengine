
import os  # для работы с файлами
import configparser


from SystemCore.CatalogCommunication.DefoultCatalogs import main_files_catalog, data_catalogs


# https://docs.python.org/3.5/library/os.path.html#os.path.abspath


# Объект для менеджмента процесса
class CatalogsManager:
    '''
    Модуль для работы с каталогами. Его задача: создать схему каталогов и обсепечить работу с ней.

    Структура каталогов:
    "Основной каталог" -> "Каталог процесса" (по имени процесса) -> Подкаталог сессии (session_subdirectory) ->
        Папки для данных -> Файлы  или (Подкаталоги модулей сессии -> Файлы)

        Папки для данных - "секция"

        "Подкаталоги модулей сессии" - опция

        Добавить функцию "запросить файлы"


    Методы и свойства



        _manager_mistakes - список ошибок, полученных при работе с каталогами
            # .append(sys.exc_info())


    '''

    def __init__(self,
                 process_name: str,
                 main_path: str = None,
                 program_catalog: str = None,
                 session_subdirectory: str = None):
        '''

        :param process_name: имя процесса.
        :param main_path: основной каталог, в подкаталоге которого процесс будет хранить свои данные.
            Значение 'default' значит, что будет использован main_files_catalog, указанный в файле с менеджером.
        :param program_catalog: каталог, в котором лежит скрипт. Дефолтно - неизвестен
        :param session_subdirectory: подкаталог, в котором будет разворачиватсья стандартная схема папок для данной
            сессии. Это удобно для разделения данных от разных запусков модуля и тестирования.
        '''

        self.__process_name = process_name

        if main_path is None:
            main_path = main_files_catalog  # Берём импортнутый каталог
        self.__main_path = main_path

        self.__session_subdirectory = session_subdirectory









        self.__program_catalog = program_catalog  # Каталог скрипта



        # Создадим глвный каталог
        self.__main_path = self.__create_process_path(main_path=main_path, subdirectory=session_subdirectory)

        # Заведём файл с настроками каталогов
        self.__catalogs = configparser.ConfigParser()
        self.__catalogs.read_dict(data_catalogs)  # Скормим в конфиг каталоги из словаря
        self.__catalogs_preparation()  # Воспроизведём каталоги конфига

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
    def program_catalog(self) -> str:
        '''
        Функция отдаёт каталог всей программы.

        :return:
        '''
        return self.__program_catalog

    @property
    def process_catalog(self) -> str:
        '''
        Основной каталог, которым аперирует запущенный процес

        :return: строка с каталогом
        '''
        return self.__process_catalog

    @property
    def session_catalog(self) -> str:
        '''
        Каталог, в который логируется текущая сессия
        :return:
        '''
        return self.__session_catalog

    # ------------------------------------------------------------------------------------------------
    # Работа с секциями ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def sections(self) -> list:
        '''
        Получение секций. Секции получаются в виде списка названий, не путей - путь запросить отдельно.

        :return:
        '''


        return

    def get_section(self, section_name: str) -> str:
        '''
        Функция отдаёт каталог сеции.

        :param section: имя секции
        :return: полный путь или None.
        '''


        return

    def add_section(self, section_name: str, section_folder: str = None) -> bool or None:
        '''
        Функция добавляет секцию в набор каталогов.

        :param section_name: имя секции
        :param section_folder: папка секции. Если не задан - выбирается имя секции по дефолту.
        :return: True - секции не было, добавлена False - секция или папка есть; None - ошибка.
        '''

        return


    # ------------------------------------------------------------------------------------------------
    # Работа с опциями -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------------
    # Получить подкаталоги ---------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------


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
                self.__create_catalog(catalog=self.main_path + sub_dir)

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

        :param catalog: Полный путь подкаталога, включая все его директории, кроме основной: self. main_path
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
        add_result = self.__create_catalog(self.main_path + catalog)  # Добавим каталог
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
            return self.main_path + self.__catalogs.get(section=section, option=option)
        except BaseException:  # Если нет секции или опции
            return None  # результат - нет подкаталога

