import pandas as pd

from SQLCommunication.SQLconnector import PostgreSQLconnector, ConnectionData
from Managers import ProcessesManager


class SQLcommunicator:
    '''
    Это обёртка над Postgres или MySQL, которая будет использоваться в работе.
    Цель - исключить проблемы при смене базы.
    '''

    def __init__(self, process_manager: ProcessesManager, launch_module_name: str = None,
                 retry_attempts: int = 3, downtime: float = 0.01,
                 worker: str = 'PostgreSQL'):
        '''
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер текущего процесса
        :param retry_attempts: количество попыток переподключения
        :param downtime: время простоя в случае получения ошибки
        :param worker: "MySQL" или "PostgreSQL". Выбирает исполнителя запросов.
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name)
        self.__to_log = self.__Logger.to_log

        # Установим параметры модуля
        self.__base_connect = None  # Данные для подключения к базе
        self.__Allowed = False  # разрешение на работу с запросами

        self.__retry_attempts = retry_attempts  # Количество попыток переподключения
        self.__downtime = downtime  # Простой при получении ошибки

        # Получим данные для авторизации
        self.__take_authorization_data()

        if worker == 'PostgreSQL':  # Делаем MySQL конект
            # Создадим логер

            self.__SQL_connection = PostgreSQLconnector(connection_data=self.__connection_data,
                                                        logging_function=self.__to_log,
                                                        retry_attempts=retry_attempts, downtime=downtime)

    # ------------------------------------------------------------------------------------------------
    # Сохранение данных ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------



    # ------------------------------------------------------------------------------------------------
    # Функции подключения к базе ---------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # Получить данные для авторизации в базе
    def __take_authorization_data(self) -> bool:
        '''
        Задача функции - получить данные для подключения к базе. Функция сразу забирает данные в селф на
        self.__connection_data. Функция может быть изменена: добавлено запрашивание данных откуда нить.
        :return: статус получения.
        '''
        self.__connection_data = self.__get_default()
        return True

    # Получение дефолтных настроек
    @staticmethod
    def __get_default() -> ConnectionData:
        '''
        Устанавливаем прописанные в коде настройки.
        :return:
        '''
        ConData = ConnectionData(base_name='AutoSEO',
                                 host='localhost', port='1234',
                                 user='postgres', password='catalog')
        return ConData

    # Функция для работы с подключением к базе
    def connection(self, act: str,
                   retry_attempts: int = None) -> bool:  # подключение, переподключение
        '''
        Функция для подключения, отключения, переподключения к базе.
        :param act: действие, которое надо выполнить:
                        close - закрыть соединение
                        open - открыть соединение
                        reopen - переоткрыть соединение
        :param retry_attempts: количество попыток переподключения.
        :return: статус успешности выполнения операции
        '''
        result = self.__SQL_connection.connection(act=act, retry_attempts=retry_attempts)
        return result

    # ------------------------------------------------------------------------------------------------
    # "Чистые" запросы к базе ------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # отправка данных в базу
    def to_base(self, requests: str or list,
                retry_attempts: int = None) -> bool or list:
        '''
        Функция для отправки запросов в базу.

        :param requests: Запрос или список запросов.
        :param retry_attempts: количество попыток повтора запроса к базе. Если это None, то будет использовано
                дефолтное количество self.__retry_attempts
        :return: True, если все запросы выполнены успешно. False, если всё упало.
                Список упавших запросов, если упала часть.
        '''
        self.__to_log(message=f'to_base: Запрошена отправка запрсоов в базу',
                      log_type='DEBUG')
        # Если запрос пустой
        if requests == [] or requests == '':
            self.__to_log(message='to_base: Ошибка передачи запросов в базу: переменная requests пуста',
                          log_type='ERROR')
            return False  # Всё упало

        # Проверим разрешение на ведения запросов
        close_after = False  # Закрыть ли соединение после работы (дефолтно - нет)?
        if not self.__SQL_connection.allowed:
            open_result = self.connection(act='open')  # Делаем подключение
            if open_result:  # Если соединение открыто
                close_after = True  # Закрыть ли соединение после работы?
            else:  # Если не открылось соединение
                self.__to_log(message=('to_base: Ошибка передачи запросов в базу: отправка не разрешена. ' +
                                       'открыть соединение не удалось'),
                              log_type='ERROR')
                return False  # Всё упало

        # После того, как курсор получен
        if isinstance(requests, str):  # Если запрос один
            requests = [requests]  # Делаем список для общности
        failed_requests = []  # Список "упавших" запросов

        # Пойдём отправлять запросы в базу
        for request in requests:
            sending_result = self.__SQL_connection.to_base(request=request, retry_attempts=retry_attempts,
                                                           try_to_allow=False)  # Попытка подключения запрещена
            if not sending_result:  # Если запрос упал
                failed_requests.append(request)  # Заберём его в упавшие запросы

        if close_after:
            self.connection(act='close', retry_attempts=1)  # Закроем конект, если он был установлен внутри функции

        if len(failed_requests) == 0:  # Если нет упавших запросов
            self.__to_log(message=f'to_base: Все запрсоы отправлены успешно',
                          log_type='DEBUG')
            return True  # Вернём, что закончили успешно
        else:  # Если есть ошибки
            self.__to_log(message=(f'to_base: Отправка запросов в базу выполнена с ошибками: ' +
                                   f'{len(failed_requests)} из {len(requests)} провалены'),
                          log_type='ERROR')
            return failed_requests  # вернём список упавших запросов

    # Функция для получения информации из базы
    def from_base(self, requests: str or list,
                  retry_attempts: int = None,
                  errors_placeholder: object = None) -> list or bool:
        '''
        Функция для получения информации из базы

        :param requests: Запрос или список запросов.
        :param retry_attempts: количество попыток повтора запроса к базе. Если это None, то будет использовано
                дефолтное количество self.__retry_attempts
        :param errors_placeholder: объект, который будет заполнять упавшие запросы в списке элементов, который будет
            экспортирован. Если значение None - то заполнения не будет.
        :return: False в случае критической ошибки, которая делает невозможным импорт любых данных.
            Список с результатами для каждого поданного запроса в виде tuple, list или errors_placeholder (в зависимости от того, была ли
            найдена одна строка (tuple) или набор строк (список из tuple) по запросу, или запрос упал - errors_placeholder).
            Причём, даже если все запросы упали, но сам импорт возможен данных возможен, то вернётся именно список, в котором
            данные упавших запросов будут заменены на errors_placeholder.
        '''

        self.__to_log(message=f'from_base: Запрошена отправка запрсоов в базу',
                      log_type='DEBUG')
        # Если запрос пустой
        if requests == [] or requests == '':
            self.__to_log(message='from_base: Ошибка передачи запросов в базу: переменная requests пуста',
                          log_type='ERROR')
            return False  # Всё упало

        # Проверим разрешение на ведения запросов
        close_after = False  # Закрыть ли соединение после работы (дефолтно - нет)?
        if not self.__SQL_connection.allowed:
            open_result = self.connection(act='open')  # Делаем подключение
            if open_result:  # Если соединение открыто
                close_after = True  # Закрыть ли соединение после работы?
            else:  # Если не открылось соединение
                self.__to_log(message=('from_base: Ошибка передачи запросов в базу: отправка не разрешена. ' +
                                       'открыть соединение не удалось'),
                              log_type='ERROR')
                return False  # Всё упало

        # После того, как курсор получен
        if isinstance(requests, str):  # Если запрос один
            requests = [requests]  # Делаем список для общности
        requests_results = []  # Список "упавших" запросов

        # Пойдём отправлять запросы в базу
        for request in requests:
            sending_result = self.__SQL_connection.from_base(request=request, retry_attempts=retry_attempts,
                                                             errors_placeholder=errors_placeholder,
                                                             try_to_allow=False)  # Попытка подключения запрещена
            requests_results.append(sending_result)  # Заберём его в упавшие запросы
            # Результат будет в любом случае добавлен в список, т.к. в случае ошибки функция вернёт errors_placeholder

        if close_after:
            self.connection(act='close', retry_attempts=1)  # Закроем конект, если он был установлен внутри функции

        if errors_placeholder in requests_results:  # Если есть упавшие запросы
            failed = 0
            for el in requests_results:
                if el == errors_placeholder:  #  Если это ошибка
                    failed += 1

            self.__to_log(message=(f'from_base: Отправка запросов в базу выполнена с ошибками: ' +
                                   f'{failed} из {len(requests)} провалены'),
                          log_type='ERROR')

        else:  # всё отлично
            self.__to_log(message=f'from_base: Все запрсоы отправлены успешно',
                          log_type='DEBUG')

        return requests_results  # Вернём результат

    # ------------------------------------------------------------------------------------------------
    # Select с постобработкой ------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def one_requests(self, request: str,
                     retry_attempts: int = None,
                     errors_placeholder: object = None) -> tuple or object:
        '''
        Функция для получения данных по одному запросу. Смысл в том, чтобы не ставить везде пост обработку.

        :param request: Запрос или список запросов.
        :param retry_attempts: количество попыток повтора запроса к базе. Если это None, то будет использовано
                дефолтное количество self.__retry_attempts
        :param errors_placeholder: объект, который будет заполнять упавшие запросы в списке элементов, который будет
            экспортирован. Если значение None - то заполнения не будет.
        :return: errors_placeholder (None) в случае критической ошибки или значение курсора (tuple).
        '''

        # Выполним запрос
        feedback = self.from_base(requests=request, retry_attempts=retry_attempts,
                                  errors_placeholder=errors_placeholder)  # Берём нулевой элемент списка
        # Возьмём нулевой элемент
        try:
            return feedback[0]  # Пробуем вернуть нулевое значение списка - tuple объект
        except BaseException:  # Если ошибка
            self.__to_log(message=(f'one_requests: Обработка запроса провалена. ' +
                                   f'Получен ответ errors_placeholder={errors_placeholder}'),
                          log_type='ERROR')
            return errors_placeholder  # Вернём errors_placeholder

    # ------------------------------------------------------------------------------------------------
    # Запросы к временным таблицам базы --------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    '''
    Сделать как отдельную функцию вообще.
    '''
    # ------------------------------------------------------------------------------------------------
    # Функции миграции -------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

