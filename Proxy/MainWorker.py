'''
Задача:
1. Получать новые прокси с сайтов
2. Держать актуальным "контрольный пул быстрых прокси" в базе
3. Проверять переобходя список базы, "живы ли его элементы"


https://olegon.ru/UserAgents.txt - список юзер агентов
'''



import requests
import random
from bs4 import BeautifulSoup
import time
import re
import threading
import pandas as pd




class FoxTools:



    def __init__(self,
                 logger: CommonLoggingClient = None, parent_name: str = None,
                 ):
        '''

        :param logger: логер. Если логер не указан, будет добавлен собственный
        :param parent_name: имя родительского модуля.
        '''

        self.__Logger, self.__to_log, self.__my_name = prepare_logger(class_name=self.__class__.__name__,
                                                                      logger=logger, parent_name=parent_name)