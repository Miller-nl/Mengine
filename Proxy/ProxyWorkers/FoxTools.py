
from SystemCore.Proxy.Proxy import ProxyServer
from Logging import CommonLoggingClient, prepare_logger

foxtools_pages = ['http://foxtools.ru/Proxy',
                  'http://foxtools.ru/Proxy?page=2',
                  'http://foxtools.ru/Proxy?page=3',
                  'http://foxtools.ru/Proxy?page=4'
                  ]

name = 'foxtools'
proxy_id = 1


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

def foxtools(page_content: str) -> list or int or None:
    '''
    Функция выделяет из контента страниц, указанных выше, данные о прокси серверах и отдаёт их в виде списка
        серверов.

    :param page_content: контент страницы
    :return: список объектов ProxyServer, полученных от страницы (Если до страниц не дозвонились, список будет пуст);
        None - в случае, если работа упала.
    '''

    proxies_list = []  # список проксис ерверов, которые мы отдадим

    for page_url in foxtools_pages:
        page_content = get_page_data(url=page_url, use_proxy=use_proxy)  # Берём страницу

        if not isinstance(page_content, str):  # Если ответила не строка
            continue

        # Выделяем таблицу с серверами
        page_content = BeautifulSoup(page_content, "html.parser")
        tbody = page_content.findAll(name={'tbody': True})[0]  # Берём контент таблицы
        strings = tbody.findAll(name={'tr': True})  # выделяем строки таблицы

        # Конвертируем в прокси
        for proxy_string in strings:
            address = proxy_string.contents[3].contents[0]
            port = proxy_string.contents[5].contents[0]

            if 'https' in proxy_string.contents[11].text.lower():
                protocol = 'https'
            else:
                protocol = 'http'

            country = proxy_string.contents[7].contents[0]['alt']

            proxy = ProxyServer(ip=address, port=port,
                                protocol=protocol,
                                country=country,
                                source=name)
            proxies_list.append(proxy)

    return proxies_list

