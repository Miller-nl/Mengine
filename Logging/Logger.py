import queue
import threading


from Exceptions.ExceptionTypes import MethodPropertyError, ProcessingError
from Logging.AppsExamples import ExporterAppExample
from Logging.Message.Message import Message
from Logging.Message.LoggingLevels import int_logging_level


default_logging_level = 10


class Logger:

    def __init__(self,
                 app_name: str,
                 launch_key: str or int = None,
                 log_launch: bool = False,
                 logging_level: str or int = 'DEBUG',
                 emergency_worker: ExporterAppExample = None,
                 daemon: bool = True
                 ):
        '''

        :param app_name: app name
        :param launch_key: Startup session key
        :param log_launch: Log application launch?
        :param logging_level: minimal logging level
        :param emergency_worker: logger for messages with failed export
        :param daemon: daemon parameter for Thread
        :param timeout: Time to try to re-export messages in case of errors.
        '''

        self.__app_name = app_name
        self.__launch_key = launch_key

        self.__queue = queue.Queue()
        self.__daemon = daemon

        self.__mutex = threading.RLock()
        self.__workers = {}  # словарь с исполнителями
        self.__works = False
        self.__kill = False
        self.__redirect_to_queue = None
        self.__thread = None

        self.__logging_level = int_logging_level(logging_level=logging_level,
                                                 default_level=10)  # Установим уровень лога

        self.__are_we_cool_yet = True  # exceptions detector

        if (emergency_worker is not None) and (not hasattr(emergency_worker, 'export')):
            raise MethodPropertyError(f'Worker {type(emergency_worker)} have no "export" method.')
        self.__emergency_worker = emergency_worker

        self.start()

        if log_launch:
            self.log(message=f'Application started.',
                     logging_level='DEBUG')

    def start(self):
        with self.__mutex:
            self.__works = True
            self.__kill = False

            self.__thread = threading.Thread(target=self.__process_queue,
                                             args=(),
                                             daemon=self.__daemon)
            self.__thread.start()

        return

    def finish(self, redirect_to_queue: queue.Queue = None):
        '''
        Stops receiving messages on the queue and waits for the message export to complete.
        You can restart it later or redirect messages to another logger.

        :return:
        '''
        with self.__mutex:
            self.__works = False
            self.__redirect_to_queue = redirect_to_queue

        self.__queue.join()
        return

    def stop(self):
        '''
        Stops the logger immediately.
        You can restart it later.

        :return:
        '''
        with self.__mutex:
            self.__works = False
            self.__kill = True

        self.__thread.join()
        return

    def stop_redirecting(self) -> queue.Queue or None:
        '''
        Stop forwarding messages to the queue of another logger.

        :return: reference to the registrar queue to which messages were forwarded. Or None, if he was not set.
        '''
        with self.__mutex:
            self.__redirect_to_queue = None
        return

    # ------------------------------------------------------------------------------------------------
    # Processing -------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def __process_queue(self):
        '''

        :return:
        '''
        while True:
            with self.__mutex:  # Check the status
                if self.__kill:
                    break

            message = self.__queue.get()
            successful_exports = len(self.__workers)

            for worker_id in self.__workers.keys():

                try:
                    self.__workers[worker_id].export(message)
                except BaseException:
                    try:
                        self._emergency_delivery(worker_id=worker_id,
                                                 message=message)
                    except BaseException:
                        successful_exports -= 1

            self.__queue.task_done()  # any way delivery is done

            # If all workers fail export and no emergency worker is set
            if successful_exports is 0:
                pass

        return

    def _emergency_delivery(self,worker_id: int, message: Message):
        '''

        :param worker_id: unsuccessful worker id
        :param message: the message that led to the error
        :return:
        '''
        emergency_message = Message(message='Message export error.',
                                    logging_level=40,
                                    app_name=self.app_name,
                                    launch_key=self.launch_key,
                                    function_name='__process_queue',
                                    logging_data={
                                        'worker': (worker_id, str(type(self.__workers[worker_id]))),
                                        'main_message': message.main_message(),
                                        'identification': message.identification(),
                                        'trace': message.trace},
                                    exception=True)

        if self.emergency_worker is not None:
            try:
                self.emergency_worker.export(message=emergency_message)
            except BaseException as new_miss:
                new_emergency_message = Message(message='Emergency message export error.',
                                                logging_level=40,
                                                app_name=self.app_name,
                                                launch_key=self.launch_key,
                                                function_name='_emergency_delivery',
                                                logging_data={
                                                    'worker': ('emergency_worker', str(type(self.emergency_worker))),
                                                    'identification': message.identification(),
                                                    'trace': message.trace},
                                                exception=new_miss)
                self.emergency_worker.export(message=new_emergency_message)

        else:
            try:
                self.__workers[worker_id].export(emergency_message)
            except BaseException as new_miss:
                new_emergency_message = Message(message='Emergency message export error.',
                                                logging_level=40,
                                                app_name=self.app_name,
                                                launch_key=self.launch_key,
                                                function_name='_emergency_delivery',
                                                logging_data={
                                                    'worker': (worker_id, str(type(self.__workers[worker_id]))),
                                                    'identification': message.identification(),
                                                    'trace': message.trace},
                                                exception=new_miss)
                self.__workers[worker_id].export(message=new_emergency_message)
        return

    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def create_name(module: str, submodule: str = None) -> str:
        '''
        Функция создаёт "стандартную" структуру имён модулей, отвечающую их запускам.

        :param module: имя "родительского" модуля. Может быть незадано.
        :param submodule: имя "дочернего" модуля.
        :return: строка полного форматного подъимени.
        '''
        if module is None:
            return submodule
        else:
            if not submodule.startswith(module):  # Если название родителя ещё не включено
                return f'{module}.{submodule}'
            else:  # Если название родителя уже есть в начале
                return submodule  # значит, имя уже форматное

    # ------------------------------------------------------------------------------------------------
    # properties -------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def app_name(self) -> str:
        return self.__app_name

    @property
    def launch_key(self) -> str or int or None:
        return self.__launch_key

    @property
    def works(self) -> bool:
        with self.__mutex:
            return self.__works

    @property
    def default_logging_level(self) -> int:
        '''

        :return: minimum logging level
        '''
        return default_logging_level

    @property
    def logging_level(self) -> int:
        return self.__logging_level

    @property
    def are_we_cool_yet(self) -> bool:
        '''

        :return: True, if there were no exceptions, otherwise False
        '''
        with self.__mutex:
            return self.__are_we_cool_yet

    @property
    def workers(self) -> dict:
        with self.__mutex:
            return self.__workers.copy()

    @property
    def emergency_worker(self) -> ExporterAppExample or None:
        return self.__emergency_worker

    @property
    def _queue(self) -> queue.Queue:
        with self.__mutex:
            return self.__queue

    @property
    def _daemon(self) -> bool:
        return self.__daemon

    @property
    def _thread(self) -> threading.Thread:
        with self.__mutex:
            return self.__thread

    # ------------------------------------------------------------------------------------------------
    # Workers ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def add_worker(self, worker: ExporterAppExample) -> int:
        '''

        :param worker: log writer
        :return: worker index
        '''
        with self.__mutex:
            if hasattr(worker, 'export'):
                if self.__workers != {}:
                    new_id = max(self.__workers) + 1
                else:
                    new_id = 1

                self.__workers[new_id] = worker
                return new_id
            else:
                raise MethodPropertyError(f'Worker {type(worker)} have no "export" method.')

    def drop_worker(self, worker_id: int):
        '''

        :param worker_id: worker index
        :return: nothing
        '''
        with self.__mutex:
            try:
                self.__workers.pop(worker_id)
            except BaseException as miss:
                raise KeyError(f'No such worker: {worker_id}') from miss
        return

    # ------------------------------------------------------------------------------------------------
    # Логирование ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def log(self, message: str,
            function_name: str or bool = True,
            submodule_name: str = None,
            processing_key: str = None,
            logging_level: int or str = 'DEBUG',
            error_type: type or None = None,
            logging_data: object = None,
            exception: tuple or bool = True,
            trace: list or bool = False,
            **kwargs):
        '''
        Функция для отправки сообщений на сервер логирования.
        Без мьютекса, чтобы не блокировать работающие потоки на время "ожидания" добавления сообщенияв очередь.

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param processing_key: ключ запуска конкретной обработки
        :param logging_level: тип сообщения в лог. Число или:
                                DEBUG	Подробная информация, как правило, интересна только при диагностике проблем.

                                INFO	Подтверждение того, что все работает, как ожидалось.

                                WARNING	Указание на то, что произошло что-то неожиданное или указание на проблему в
                                        ближайшем будущем (например, «недостаточно места на диске»).
                                        Программное обеспечение все еще работает как ожидалось.

                                ERROR	Из-за более серьезной проблемы программное обеспечение
                                        не может выполнять какую-либо функцию.

                                CRITICAL	Серьезная ошибка, указывающая на то,
                                        что сама программа не может продолжить работу.
        :param error_type: тип ошибки, если требуется.
        :param logging_data: dto объект, который будет залогирован. Обычно содержит информацию о данных,
            обрабатывающихся в скриптах. Список/словарь - то, что можно перегнать в json
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return:
        '''
        if int_logging_level(logging_level=logging_level) < self.__logging_level:
            return

        if self.works:
            new_message = self._create_message(message=message,
                                               function_name=function_name,
                                               submodule_name=submodule_name,
                                               processing_key=processing_key,
                                               logging_level=logging_level,
                                               error_type=error_type,
                                               logging_data=logging_data,
                                               exception=exception,
                                               trace=trace,
                                               **kwargs
                                               )
            self.__queue.put(new_message)
            return

        else:
            with self.__mutex:
                if self.__redirect_to_queue is None:
                    raise ProcessingError(f'The logger is stopped. Message not received: {message}')
                else:
                    redirect_to_queue = self.__redirect_to_queue

            new_message = self._create_message(message=message,
                                               function_name=function_name,
                                               submodule_name=submodule_name,
                                               processing_key=processing_key,
                                               logging_level=logging_level,
                                               error_type=error_type,
                                               logging_data=logging_data,
                                               exception=exception,
                                               trace=trace,
                                               **kwargs
                                               )
            redirect_to_queue.put(new_message)
            return

    def _create_message(self, message: str,
                        function_name: str or bool = True,
                        submodule_name: str = None,
                        processing_key: str = None,
                        logging_level: int or str = 'DEBUG',
                        error_type: type or None = None,
                        logging_data: object = None,
                        exception: tuple or bool = True,
                        trace: list or bool = False,
                        **kwargs) -> Message:
        '''
        Функция для подготовки форматного DTO для сообщения

        :param message: сообщение для логирования
        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param processing_key: имя "запуска" обработки. Это удобно для логирвоания "задания" приложения.
        :param logging_level: тип сообщения в лог. Число или:
                                DEBUG	Подробная информация, как правило, интересна только при диагностике проблем.

                                INFO	Подтверждение того, что все работает, как ожидалось.

                                WARNING	Указание на то, что произошло что-то неожиданное или указание на проблему в
                                        ближайшем будущем (например, «недостаточно места на диске»).
                                        Программное обеспечение все еще работает как ожидалось.

                                ERROR	Из-за более серьезной проблемы программное обеспечение
                                        не может выполнять какую-либо функцию.

                                CRITICAL	Серьезная ошибка, указывающая на то,
                                        что сама программа не может продолжить работу.
        :param error_type: тип ошибки, если требуется.
        :param logging_data: dto объект, который будет залогирован. Обычно содержит информацию о данных,
            обрабатывающихся в скриптах.
        :param exception: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
            следа внутри функции. Если задан exception_mistake, то trace игнорируется.
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs
        :return: форматный контейнер сообщения - Message.
        '''

        logging_level = int_logging_level(logging_level=logging_level, default_level=self.default_logging_level)
        if logging_level >= 40:
            self.__are_we_cool_yet = False

        # Скорректируем уровень лога, если нужно
        if exception is not False or error_type is not None:  # Если переданы данные об исключении или ошибке
            if logging_level > 20:  # Если уровень логирования недостаточно высок
                logging_level = 30  # Ставим "WARNING", так как в общем случае exception_message не всегда ERROR

        # Сделаем сообщение
        export_message = Message(message=message,
                                 logging_level=logging_level,
                                 error_type=error_type,
                                 app_name=self.app_name,
                                 launch_key=self.launch_key,
                                 processing_key=processing_key,
                                 function_name=function_name,
                                 submodule_name=submodule_name,
                                 logging_data=logging_data,
                                 exception=exception,
                                 trace=trace,
                                 **kwargs)
        return export_message

    # ------------------------------------------------------------------------------------------------
    # Functions creation -----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def create_logging_function(self,
                                function_name: str or bool = True,
                                submodule_name: str = None,
                                processing_key: str = None,
                                **kwargs) -> bool or None:
        '''
        Функция для отправки сообщений на сервер логирования.
        Без мьютекса, чтобы не блокировать работающие потоки на время "ожидания" добавления сообщенияв очередь.

        :param function_name: имя вызывающей функции
        :param submodule_name: имя подмодуля
        :param processing_key: ключ запуска конкретной обработки
        :param kwargs: дополнительные параметры, который уйдeт на логирование в json. Если названия параметров
            совпадут  с индексами в data, то индексы, находившиеся в data будут перезаписаны значениями kwargs.
            Параметры не должны пересекаться названиями с параметрами функции .log() !
        :return:
        '''

        def log(message: str,
                function_name: str or bool = function_name,
                submodule_name: str = submodule_name,
                processing_key: str = processing_key,
                logging_level: int or str = 'DEBUG',
                error_type: type or None = None,
                logging_data: object = None,
                exception: tuple or bool = True,
                trace: list or bool = False,
                **kwargs_new):
            kwargs_new = {**kwargs, **kwargs_new}

            self.log(message=message,
                     function_name=function_name,
                     submodule_name=submodule_name,
                     processing_key=processing_key,
                     logging_level=logging_level,
                     error_type=error_type,
                     logging_data=logging_data,
                     exception=exception,
                     trace=trace,
                     **kwargs_new)
            return

        return log
