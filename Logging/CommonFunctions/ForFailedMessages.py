from .MessagesPreparer import Message

# ---------------------------------------------------------------------------------------------
# Хранение упавших сообщений ------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
class FailedMessages:
    '''
    Контейнер для хранения сообщений, не обработанных воркерами.

        maximum_list_length - максимальная длина списка

        failed_requests - список вида [([workers_names], message), ...]

        fails_amount - количество проваленных сообщений

        add_message() - добавить сообщение
    '''

    def __init__(self, maximum_list_length: int = 100):
        '''

        :param maximum_list_length: максимальная длина списка сообщений логирования. 0 - все
        '''
        self.__maximum_list_length = maximum_list_length
        self._reset_list()

    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def maximum_list_length(self) -> int:
        '''
        Получение максимальной длины списка с ошибками/сообщениями. 0 - любая длина

        :return: целое число
        '''
        return self.__maximum_list_length

    @property
    def failed_requests(self) -> list:
        '''
        Отдаёт запросы, которые не были обработаны воркерами.

        :return: копия списка ошибок вида [([workers_names], message), ...]
        '''
        return self.__failed_requests.copy()

    @property
    def fails_amount(self) -> int:
        '''
        Отдаёт размер контейнера

        :return: длина списка
        '''
        return len(self.__failed_requests)

    # ---------------------------------------------------------------------------------------------
    # Запоминание сообщений -----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def _reset_list(self):
        '''
        Функция сбрасывает список с упавшими сообщениями

        :return: ничего
        '''
        self.__failed_requests = []  # Список проваленных запросов
        return

    def add_message(self, workers_names: str or int or list or tuple,
                    message: str or list or dict or Message):
        '''
        Функция добавляет в словарь
        :param workers_names: имя "воркера", который добавил сообщение.
        :param message:
        :return:
        '''
        if not isinstance(workers_names, list):
            workers_names = [workers_names]

        self.__failed_requests.append((workers_names, message))

        if self.maximum_list_length:
            list_len = len(self.__failed_requests)
            if list_len > self.maximum_list_length:  # Если есть ограничение и оно привышено
                # форматнём список
                self.__failed_requests = self.__failed_requests[list_len - self.maximum_list_length:]
        return

