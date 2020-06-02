'''
Задача:
1. Получать новые прокси с сайтов
2. Держать актуальным "контрольный пул быстрых прокси" в базе
3. Проверять переобходя список базы, "живы ли его элементы"


https://olegon.ru/user_agents.txt - список юзер агентов
'''



import requests
import random
from bs4 import BeautifulSoup
import time
import re
import threading
import pandas as pd




