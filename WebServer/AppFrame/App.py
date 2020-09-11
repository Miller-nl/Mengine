
from .logging import logging_wrapper

class ApplicationFramework:
    '''
    Пример приложения для Web-сервера.
    Методы:
        Identification
            name

        Working
            do()
            stop()
    '''

    def __init__(self,
                 logging_function: logging_wrapper,
                 database_adapter: object
                 ):
        '''

        :param logging_function: function for logging.
        :param database_adapter: database adapter for your app
        '''

    # ------------------------------------------------------------------------------------------------
    # Identification ---------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def name() -> str:
        '''
        Returns app name for logging.

        :return:
        '''
        return 'ApplicationFramework'

    # ------------------------------------------------------------------------------------------------
    # Working ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------


    def setup(self):


        return

    def handle(self):
        return

    def finish(self):
        return


