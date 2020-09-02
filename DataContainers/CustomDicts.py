import multiprocessing
import threading


class RestrictedTypeDict(dict):
    '''
    Основная задача контейнера: реализация над словарём набора методов, которые обеспечат более удобное его
        использование. Важный комментарий состоит в том, что контейнер не предназначен для хранения элементов типа
        None.

    Методы и свойства:
        Все стандартные методы словаря

        fixed_index_type - фиксированный тип индекса. False - не фиксирован

        fixed_object_type - фиксированный тип объекта. False - не фиксирован

        check_access() - проверка доступа
    '''

    def __init__(self,
                 fixed_index_type: object or False = False,
                 fixed_object_type: object or False = False,
                 counter: object = None
                 ):
        '''

        :param fixed_index_type: фиксировать ли тип индекса? False - нет, иначе передаётся явно тип.
        :param fixed_object_type: Фиксировать ли тип объектов контейнера? False - нет, иначе передаётся явно тип.
        :param counter: объект-счётчик. Для индексации объектов, например.
        '''

        dict.__init__(self)

        self.__control_types(fixed_index_type=fixed_index_type, fixed_object_type=fixed_object_type)

        self.counter = counter

    # ---------------------------------------------------------------------------------------------
    # Преднастройка объекта -----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def __control_types(self, fixed_index_type, fixed_object_type):
        '''
        Настраивает "контроль типов данных" для объекта. Устанавливает: self.__fixed_index_type,
            self.__fixed_object_type.

        :param fixed_index_type: фиксировать ли тип индекса? False - нет, иначе передаётся явно тип.
        :param fixed_object_type: Фиксировать ли тип объектов контейнера? False - нет, иначе передаётся явно тип.
        :return: ничего
        '''
        if isinstance(fixed_index_type, type) or fixed_index_type is False:
            self.__fixed_index_type = fixed_index_type
        else:
            raise TypeError(f'fixed_index_type type must be "type". {type(fixed_index_type)} was passed.')

        if isinstance(fixed_object_type, type) or fixed_object_type is False:
            self.__fixed_object_type = fixed_object_type
        else:

            raise TypeError(f'fixed_object_type type must be "type". {type(fixed_object_type)} was passed.')

        if fixed_object_type is False and fixed_index_type is False:
            pass
        elif fixed_object_type is not False and fixed_index_type is not False:
            self.__setitem__ = self.__check_both
        elif fixed_index_type is not False:
            self.__setitem__ = self.__check_index
        elif fixed_object_type is not False:
            self.__setitem__ = self.__check_value

        return

    def __check_both(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_index_type is not False:
            if not isinstance(self.fixed_index_type, key):
                raise TypeError(f'key type must be {self.fixed_index_type}. {type(key)} was passed.')

        if self.fixed_object_type is not False:
            if not isinstance(self.fixed_object_type, value):
                raise TypeError(f'value type must be {self.fixed_object_type}. {type(value)} was passed.')

        self[key] = value
        return

    def __check_index(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_index_type is not False:
            if not isinstance(self.fixed_index_type, key):
                raise TypeError(f'key type must be {self.fixed_index_type}. {type(key)} was passed.')

        self[key] = value
        return

    def __check_value(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_object_type is not False:
            if not isinstance(self.fixed_object_type, value):
                raise TypeError(f'value type must be {self.fixed_object_type}. {type(value)} was passed.')

        self[key] = value
        return

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def fixed_index_type(self) -> type or False:
        '''

        :return: фиксированный тип индекса или False
        '''
        return self.__fixed_index_type

    @property
    def fixed_object_type(self) -> type or False:
        '''

        :return:  фиксированный тип объекта или False
        '''
        return self.__fixed_object_type

    def check_access(self, key) -> bool:
        '''
        Быстрая проверка доступа

        :param key: ключ
        :return: статус наличия объекта в контейнере
        '''
        try:
            a = self[key]
            return True
        except KeyError:
            return False


class MultiAssesDict(dict):
    '''
    Основная задача контейнера: реализация над словарём набора методов, которые обеспечат более удобное его
        использование. Важный комментарий состоит в том, что контейнер не предназначен для хранения элементов типа
        None.

    Методы и свойства:
        Все стандартные методы словаря

        fixed_index_type - фиксированный тип индекса. False - не фиксирован

        fixed_object_type - фиксированный тип объекта. False - не фиксирован

        check_access() - проверка доступа

        _mutex - мьютекс

        multiprocess_access - True: multiprocessing mutex; False - threading mutex

        acquire() - mutex.acquire()

        release() - mutex.release()

    '''

    def __init__(self,
                 fixed_index_type: object or False = False,
                 fixed_object_type: object or False = False,
                 multiprocess_access: bool = False,
                 counter: object = None
                 ):
        '''

        :param fixed_index_type: фиксировать ли тип индекса? False - нет, иначе передаётся явно тип.
        :param fixed_object_type: Фиксировать ли тип объектов контейнера? False - нет, иначе передаётся явно тип.
        :param counter: объект-счётчик. Для индексации объектов, например.
        :param multiprocess_access: разрешить ли использование в нескольких процессах?
            True - mutex будет от multiprocessing, False - от threading.
        '''

        dict.__init__(self)

        self.__control_multiprocess_access(multiprocess_access=multiprocess_access)

        self.__control_types(fixed_index_type=fixed_index_type, fixed_object_type=fixed_object_type)

        self.counter = counter

    # ---------------------------------------------------------------------------------------------
    # Преднастройка объекта -----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def __control_multiprocess_access(self, multiprocess_access: bool):
        '''
        Функция валидируте параметр multiprocess_access, устанавливая его в self. и настраивая __mutex

        :param multiprocess_access: переменная - индикатор контроля доступа
        :return: ничего
        '''
        self.__multiprocess_access = multiprocess_access

        if multiprocess_access is True:
            self.__mutex = multiprocessing.Lock()
        elif multiprocess_access is False:
            self.__mutex = threading.Lock()
        else:
            raise ValueError(f'multiprocess_access value must be True or False. {multiprocess_access} was passed.')

        return

    def __control_types(self, fixed_index_type, fixed_object_type):
        '''
        Настраивает "контроль типов данных" для объекта. Устанавливает: self.__fixed_index_type,
            self.__fixed_object_type.

        :param fixed_index_type: фиксировать ли тип индекса? False - нет, иначе передаётся явно тип.
        :param fixed_object_type: Фиксировать ли тип объектов контейнера? False - нет, иначе передаётся явно тип.
        :return: ничего
        '''
        if isinstance(fixed_index_type, type) or fixed_index_type is False:
            self.__fixed_index_type = fixed_index_type
        else:
            raise TypeError(f'fixed_index_type type must be "type". {type(fixed_index_type)} was passed.')

        if isinstance(fixed_object_type, type) or fixed_object_type is False:
            self.__fixed_object_type = fixed_object_type
        else:

            raise TypeError(f'fixed_object_type type must be "type". {type(fixed_object_type)} was passed.')

        if fixed_object_type is False and fixed_index_type is False:
            pass
        elif fixed_object_type is not False and fixed_index_type is not False:
            self.__setitem__ = self.__check_both
        elif fixed_index_type is not False:
            self.__setitem__ = self.__check_index
        elif fixed_object_type is not False:
            self.__setitem__ = self.__check_value

        return

    def __check_both(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_index_type is not False:
            if not isinstance(self.fixed_index_type, key):
                raise TypeError(f'key type must be {self.fixed_index_type}. {type(key)} was passed.')

        if self.fixed_object_type is not False:
            if not isinstance(self.fixed_object_type, value):
                raise TypeError(f'value type must be {self.fixed_object_type}. {type(value)} was passed.')

        self[key] = value
        return

    def __check_index(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_index_type is not False:
            if not isinstance(self.fixed_index_type, key):
                raise TypeError(f'key type must be {self.fixed_index_type}. {type(key)} was passed.')

        self[key] = value
        return

    def __check_value(self, key, value):
        '''
        Функция устанавливает элемент в словарь

        :param key: ключ
        :param value: объект
        :return:
        '''
        if self.fixed_object_type is not False:
            if not isinstance(self.fixed_object_type, value):
                raise TypeError(f'value type must be {self.fixed_object_type}. {type(value)} was passed.')

        self[key] = value
        return

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def fixed_index_type(self) -> type or False:
        '''

        :return: фиксированный тип индекса или False
        '''
        return self.__fixed_index_type

    @property
    def fixed_object_type(self) -> type or False:
        '''

        :return:  фиксированный тип объекта или False
        '''
        return self.__fixed_object_type

    def check_access(self, key) -> bool:
        '''
        Быстрая проверка доступа

        :param key: ключ
        :return: статус наличия объекта в контейнере
        '''
        try:
            a = self[key]
            return True
        except KeyError:
            return False

    # ------------------------------------------------------------------------------------------------
    # Мультидоступ -----------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def _mutex(self) -> object:
        '''
        Получение мьютекса объекта.
        Если multiprocess_access True, то это мьютекс multiprocessing.synchronize.Lock, иначе - _thread.lock.
        Лучше использовать функции: lock, open.

        :return: мьютекс
        '''
        return self.__mutex

    @property
    def multiprocess_access(self) -> bool:
        '''
        Разрешён ли "многопроцессный доступ"? True - да, False - используется многопоточный.

        :return:
        '''
        return self.__multiprocess_access

    def acquire(self):
        '''
        Блокировка мьютекса.

        :return: ничего
        '''
        self.__mutex.acquire()
        return

    def release(self):
        '''
        Разблокировка мьютекса.

        :return:
        '''
        self.__mutex.release()
        return
