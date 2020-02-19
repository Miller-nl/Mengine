'''
Описать как выглядит "обычный модуль"
'''


class Module:

    def __init__(self, process_manager: ProcessesManager,
                 launch_module_name: str = None):
        '''
        :param launch_module_name: имя вызывающего модуля
        :param process_manager: менеджер текущего процесса
        '''

        # Модуль для логирования (будет один и тот же у всех объектов сессии)
        self.__my_name = process_manager.get_module_name(my_name=self.__class__.__name__,
                                                         launch_module_name=launch_module_name)
        self.__Logger = process_manager.create_logger(module_name=self.__my_name)
        self.__to_log = self.__Logger.to_log