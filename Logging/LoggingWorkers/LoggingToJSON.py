import json
import datetime
import os
import sys

from ..CommonFunctions.LoggingLevels import int_logging_level, logging_levels
from ..CommonFunctions.ForFailedMessages import FailedMessages

class JsonLogger:
    '''
    Объект, использующийся для логирования данных в файлы "name.jsonlines".

    Уровни логирования: 10 или 'DEBUG'; 20 или 'INFO'; 30 или 'WARNING'; 40 или 'ERROR'; 50 или 'CRITICAL'.


    Свойства и методы:

        default_logging_level - уровень логирования поумолчанию

        journals - список с данными о журналах

        are_messages_cool_yet - все ли сообщения успешно записаны

        failed_messages_container - контейнер с упавшими сообщениями


        log_dto() - непосредственно функция для логирования
    '''

    __logging_levels = logging_levels

    def __init__(self,
                 journals_catalog: str, journal_file: str = None,
                 remember_failed_requests: int = 120,
                 logging_level: str or int = 'DEBUG'):
        '''

        :param journals_catalog: директория для ведения журнала. По дефолту определяется через файл с настройками
        :param journal_file: файл для логирования без расширения. Если не задан, создастся автоматически
                по времени и дате.
        :param remember_failed_requests: количество сообщений, которые будут заполнены в случае отказа воркера. 0 - все.
        :param logging_level: Уровень логирования в файл .jsonlines. Если задан "косячно", поставится "DEBUG"
        '''

        self.__default_logging_level = int_logging_level(logging_level=logging_level,
                                                         default_level=10)  # Установим уровень лога

        self.__mistakes = []  # Список ошибок логера (как лог логера)

        # Создадим файл журнала если его нет
        self.__prepare_file(journals_catalog=journals_catalog, journal_file=journal_file)

        self.__failed_messages = FailedMessages(maximum_list_length=remember_failed_requests)

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
        except FileNotFoundError:  # Если нет каталога
            self.__mistakes.append(sys.exc_info())  # Список ошибок логера (как лог логера)
            return None
        except OSError:  # Если косячное имя файла
            self.__mistakes.append(sys.exc_info())  # Список ошибок логера (как лог логера)
            return None

        return True  # Если всё ок

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
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
        if not self.failed_messages_container.fails_amount:  # Если количество упавших сообщений ноль
            return True
        else:
            return False  # Если более нуля сообщений провалены хоть одним воркером

    @property
    def failed_messages_container(self) -> FailedMessages:
        '''
        Получение контейнра првоаленных сообщений

        :return: объект со списком упавшиъх сообщений
        '''
        return self.__failed_messages

    # ---------------------------------------------------------------------------------------------
    # Функции логирования -------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def log_dto(self, dto: dict or str) -> bool:
        '''
        Функция логирует в json файл.

        :param dto: словарь-DTO, или уже готовая json строка лога.
        :return: успешность добавления сообщения
        '''
        try:
            with open(self.journals[0], 'a') as write_file:  # Делаем экспорт
                if isinstance(dto, dict):
                    json.dump(dto, write_file)
                elif isinstance(dto, str):
                    json.dump(json.loads(dto), write_file)

                write_file.write('\n')
                write_file.flush()
            return True
        except BaseException:  # При ошибке записи
            self.failed_messages_container.add_message(workers_names=self.__class__.__name__, message=dto)
            return False

