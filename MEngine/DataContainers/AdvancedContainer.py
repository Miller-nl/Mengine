
import multiprocessing
import threading


class no_mutex:
    def acquire(self):
        pass
        return

    def release(self):
        pass
        return


class AdvancedContainer:
    '''
    Основная задача контейнера: реализация над словарём набора методов, которые обеспечат его более удобное
        использование.

    Комментарии:
        с логгером/Без
        с мьютексом/без - True - мультипроцессный, False - многопоточный, None - Без вообще.
        с указанием типа или без
        с произвольным индексом или с фиксированным (тип индекса)
        с наличием "автонумерации" и без

        две функции добавления: как в словарь aaa[name] = object и def

        получение длины: через len и функцией
        получение списка ключей/элементов - также две функции

        добавить срезы
        и "генератор" или как там - для for el in container


    Методы и свойства:
        Логирование
            _Logger - логгер

            _sub_module_name - "под имя", использующееся при логировании

            _to_log - функция логирования

        База данных
            SQLconnector - коммуникатор с БД

        API
            one_page_data_transit() - прередаёт в базу данные одной страницы результатов поиска.

    '''

    def __init__(self,
                 multiprocess_access: bool or None = False
                 ):
        '''

        :param multiprocess_access: разрешить ли использование в нескольких процессах?
            True - mutex будет от multiprocessing, False - от threading, None - без мьютекса.
        '''

        self.__dict = {}  # словарь - контейнер

        self.__multiprocess_access = multiprocess_access
        if multiprocess_access is True:
            self.__mutex = multiprocessing.Lock()
        elif multiprocess_access is False:
            self.__mutex = threading.Lock()
        else:  # Если это None
            self.__mutex = no_mutex()

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def mutex(self) -> object or no_mutex:
        '''
        Получение мьютекса объекта.
        Если multiprocess_access True, то это мьютекс multiprocessing.synchronize.Lock, иначе - _thread.lock.

        :return: мьютекс
        '''
        return self.__mutex

    @property
    def multiprocess_access(self) -> bool or None:
        '''
        Разрешён ли "многопроцессный доступ"?

        :return:
        '''
        return self.__multiprocess_access

    # ------------------------------------------------------------------------------------------------
    # Мультидоступ -----------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def lock(self):
        '''
        Блокировка мьютекса.

        :return: ничего
        '''
        self.__mutex.acquire()
        return

    @property
    def open(self):
        '''
        Разблокировка мьютекса.

        :return:
        '''
        self.__mutex.release()
        return









def aaa():

    '''


    Комментарии:
        с логгером/Без
        с мьютексом/без - True - мультипроцессный, False - многопоточный, None - Без вообще.
        с указанием типа или без
        с произвольным индексом или с фиксированным (тип индекса)
        с наличием "автонумерации" и без

        две функции добавления: как в словарь aaa[name] = object и def

        получение длины: через len и функцией
        получение списка ключей/элементов - также две функции

        добавить срезы
        и "генератор" или как там - для for el in container
    '''




