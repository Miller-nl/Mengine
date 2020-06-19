'''
Воркеры, задача которых, получив HTML код страницы, выдать список объектов формата "ProxyServer"

http://www.borovic.ru/codes.html - коды стран
'''

import requests
import random
from bs4 import BeautifulSoup

from .UserAgents import ProxyServer, user_agent_list

protocols = ['http', 'https']
default_timeout = 25


#protocol.lower()


def get_page_data(url: str,
                  use_proxy: ProxyServer = None,
                  time_to_sleep: int = 15,
                  with_user_agent: str or bool = True,
                  timeout: int = 10) -> str or None or int:
    '''
    Функция получает контент страницы и отдаёт его в виде HTML кода

    :param url: урл для обращения
    :param use_proxy: прокси сервер, через который будем обращаться (None - Обращаемся от себя)
    :param time_to_sleep: время задержек между обращениями (случайно выбирается +/- половина)
    :param with_user_agent: Использовать ли юзер агент? str - задан явно, False - нет, True - выбрать случайно.
    :param timeout: таймаут для ответа страницы. Если задан прокси сервер, имеющий высокий пинг,
        мы будем брать от прокси.
    :return: HTML текст страницы; None - упал запрос на получение страницы; int - код ответа, если он не 200.
    '''
    sec_to_sleep = random.randint(time_to_sleep - round(time_to_sleep / 2),
                                  time_to_sleep + round(time_to_sleep / 2))  # Рассчитаем время сна

    session = requests.Session()  # создадим сессию

    if use_proxy is not None:  # Если указана прокся
        # Дадим в настройку объекта прокси
        session.proxies = {use_proxy.protocol: f'{use_proxy.protocol}://{use_proxy.ip}:{use_proxy.port}'}

        if use_proxy.user is not None:  # Если есть юзер
            session.auth = (use_proxy.user, use_proxy.password)

        if use_proxy.ping is not None:  # Берём таймаут от прокси
            if use_proxy.ping > 5:
                timeout = use_proxy.ping * 3

    if with_user_agent is True:  # Если взять рандомный
        with_user_agent = {'User-agent': random.choice(user_agent_list)}
    elif isinstance(with_user_agent, str):  # если указан агент
        with_user_agent = {'User-agent': with_user_agent}

    try:  # Прозвоним
        if with_user_agent is False:  # без юзер агента
            response = session.get(url, timeout=timeout)
        else:  # с агентом
            response = session.get(url, headers=with_user_agent, timeout=timeout)

    except BaseException:  # Если упало
        return None  # Вернём ошибку

    if response.status_code == 200:  # Если всё ок
        return response.text

    else:  # Если код ответа неприемлимый
        return response.status_code


# --------------------------------------------------------------------------------------------------------
# foxtools -----------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------
# proxy-sale ---------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
proxy_sale_pages = ['https://free.proxy-sale.com/',
              ]
proxy_sale_name = 'proxy-sale'

def proxy_sale():

    return


# --------------------------------------------------------------------------------------------------------
# spys ---------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
# http://spys.one/proxies/


# http://free-proxy.cz/ru/
# https://advanced.name/ru/freeproxy
# https://htmlweb.ru/analiz/proxy_list.php  (?p=2)


