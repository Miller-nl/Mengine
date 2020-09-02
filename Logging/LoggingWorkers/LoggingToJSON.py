import json
import datetime
import os
import multiprocessing
import threading

from ..CommonFunctions.LoggingLevels import int_logging_level, logging_levels
from ..CommonFunctions.FailedMessagesContainer import FailedMessages
from ..CommonFunctions.Message import Message

class no_mutex:
    def acquire(self):
        pass
        return

    def release(self):
        pass
        return


class JsonLogger:
    '''
    Объект, использующийся для логирования данных в файлы "name.jsonlines".

    Уровни логирования: 10 или 'DEBUG'; 20 или 'INFO'; 30 или 'WARNING'; 40 или 'ERROR'; 50 или 'CRITICAL'.


    Свойства и методы:
        mutex - мьютекс

        multiprocess_access - разрешённость доступов из разных процессов

        default_logging_level - уровень логирования поумолчанию

        journals - список с данными о журналах

        are_messages_cool_yet - все ли сообщения успешно записаны

        _FailedMessages - контейнер с упавшими сообщениями

        _LoggerErrors - ошибки логера

        log_dto() - непосредственно функция для логирования
    '''

    __logging_levels = logging_levels

    def __init__(self,
                 journals_catalog: str, journal_file: str = None,
                 remember_failed_requests: int = 120,
                 logging_level: str or int = 'DEBUG',
                 multiprocess_access: bool or None = False):
        '''

        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования без расширения. Если не задан, создастся автоматически
                по времени и дате.
        :param remember_failed_requests: количество сообщений, которые будут заполнены в случае отказа воркера. 0 - все.
        :param logging_level: Уровень логирования в файл .jsonlines. Если задан "косячно", поставится "DEBUG"
        :param multiprocess_access: разрешить ли использование в нескольких процессах?
            True - mutex будет от multiprocessing, False - от threading, None - без мьютекса.
        '''

        self.__default_logging_level = int_logging_level(logging_level=logging_level,
                                                         default_level=10)  # Установим уровень лога

        self.__LoggerErrors = FailedMessages(maximum_list_length=remember_failed_requests)
        self.__FailedMessages = FailedMessages(maximum_list_length=remember_failed_requests)

        # Создадим файл журнала если его нет
        self.__prepare_file(journals_catalog=journals_catalog, journal_file=journal_file)

        self.__multiprocess_access = multiprocess_access
        if multiprocess_access is True:
            self.__mutex = multiprocessing.Lock()
        elif multiprocess_access is False:
            self.__mutex = threading.Lock()
        else:  # Если это None
            self.__mutex = no_mutex()


    def __prepare_file(self, journals_catalog: str, journal_file: str = None) -> bool or None:
        '''
        Функция устанавливает файл для логирования

        :param journals_catalog: директория для ведения журнала
        :param journal_file: файл для логирования
        :return: статус добавления: True - Успешно; None - ошибка (нет каталога или неверное имя файла).
        '''

        # Создадим имя файлай
        journals_catalog = os.path.abspath(journals_catalog)  # отформатируем путь

        if isinstance(journal_file, str):  # Если имя файла задано
            if not journal_file.endswith('.jsonlines'):  # Проверим расширение
                journal_file += '.jsonlines'  # Установим, если нет
        else:  # Если имя не задано
            journal_file = (str(datetime.datetime.now()).replace(':', ';') + '.jsonlines')
        self.__journal_file = os.path.join(journals_catalog, journal_file)  # Забьём в полный путь

        try:
            if not os.access(self.__journal_file, os.F_OK):  # Если файла нет, создадим
                with open(self.__journal_file, "w", encoding="utf-8") as f:
                    pass
        except BaseException:  # Если нет каталога или косячное имя
            self._LoggerErrors.add_message(workers_names=self.__class__.__name__,
                                           message=Message(message='Ошибка установки файла для логирования.',
                                                           logging_level=30,
                                                           logging_data={'journal_file': self.__journal_file}
                                                           )
                                           )
            return None

        return True  # Если всё ок

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
    def multiprocess_access(self) -> bool:
        '''
        Разрешён ли "многопроцессный доступ"?

        :return:
        '''
        return self.__multiprocess_access

    @property
    def default_logging_level(self) -> int:
        '''
        Общий параметр
        Отдаёт "дефолтный" уровень логирования в файл: 10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL

        :return: число
        '''
        return self.__default_logging_level

    @property
    def journals(self) -> list:
        '''
        Отдаёт полный путь к файлу лога.

        :return: строка с путём, обёрнутая в список для общности интерфейсов
        '''
        return [self.__journal_file]

    @property
    def are_messages_cool_yet(self) -> bool:
        '''
        Получения статуса "безошибочности" отправки сообщений, которые логировались

        :return: True - не было сообщений, проваленых воркерами; False - были
        '''
        if not self._FailedMessages.fails_amount:  # Если количество упавших сообщений ноль
            return True
        else:
            return False  # Если более нуля сообщений провалены хоть одним воркером

    @property
    def _FailedMessages(self) -> FailedMessages:
        '''
        Получение контейнра првоаленных сообщений

        :return: объект со списком упавшиъх сообщений
        '''
        return self.__FailedMessages

    @property
    def _LoggerErrors(self) -> FailedMessages:
        '''
        Получение контейнра с ошибками в работе логера.

        :return: объект со списком сообщений об ошибках
        '''
        return self.__LoggerErrors

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def log_dto(self, message: dict or list or str or Message) -> bool or None:
        '''
        Функция логирует в json файл.

        :param message: словарь-DTO, или уже готовая json строка лога, или форматное сообщение Message.
        :return: успешность добавления сообщения: True - полностью успешно;
            False - "данные" были срезаны из-за ошибок отправки, но само сообщение доставлено;
            None - сообщение не залогировано.
        '''
        self.mutex.acquire()
        try:
            if not os.access(self.__journal_file, os.F_OK):  # Если файла нет
                return None  # ошибка

            try:
                with open(self.journals[0], 'a') as write_file:  # Делаем экспорт
                    if isinstance(message, dict):
                        json.dump(message, write_file)
                    if isinstance(message, Message):
                        json.dump(message.get_dict(trimmed=False), write_file)
                    elif isinstance(message, str):
                        json.dump(json.loads(message), write_file)

                    write_file.write('\n')
                    write_file.flush()
                return True
            except BaseException:  # При ошибке записи
                self._FailedMessages.add_message(workers_names=self.__class__.__name__, message=message)
                self._LoggerErrors.add_message(workers_names=self.__class__.__name__,
                                               message=Message(message='Ошибка записи полного сообщения.',
                                                               logging_level=30,
                                                               logging_data={'journal_file': self.__journal_file}
                                                               )
                                               )
                if isinstance(message, Message):  # Если это контейнер
                    try:
                        with open(self.journals[0], 'a') as write_file:  # Делаем экспорт
                            json.dump(message.get_dict(trimmed=True), write_file)

                        return False  # Вернём, что сообщение оптправлено с ошибкой
                    except BaseException:
                        self._LoggerErrors.add_message(workers_names=self.__class__.__name__,
                                                       message=Message(message='Ошибка записи укороченного сообщения.',
                                                                       logging_level=30,
                                                                       logging_data={
                                                                           'journal_file': self.__journal_file}
                                                                       )
                                                       )
                return None  # Если завален стандартный вывод и "укороченный" тоже

        except BaseException:
            self._LoggerErrors.add_message(workers_names=self.__class__.__name__,
                                           message=Message(message='Непредвиденная ошибка',
                                                           logging_level=30,
                                                           logging_data={'journal_file': self.__journal_file}
                                                           )
                                           )
            return None  # ошибка
        finally:
            self.mutex.release()

