import math


class ProxyServer:
    '''
    Класс - контейнер прокси сервера.

    Методы и свойства
        ip - адрес

        port - порт

        protocol - протокол сервера

        country - двухбуквенное обозначение страны (http://www.borovic.ru/codes.html)

        proxy_id - индекс в базе данных (детектирует занесённость сервера в БД)

        ping - задержка (округлённая в меньшую сторону)

        source - источник сервера (откуда взят). None - не известно

        user - пользователь (если есть)

        password - пароль (если есть)

    '''

    def __init__(self, ip: str, port: str or int,
                 protocol: str = None, country: str = None,
                 ping: int or float = None,
                 source: str = None,
                 user: str = None, password: str = None,
                 proxy_id: int = None):
        '''

        :param ip: адрес
        :param port: порт
        :param protocol: тип прокси: http/https
        :param country: двухбуквенное обозначение страны (http://www.borovic.ru/codes.html)
        :param source: адрес сайта, от которого был получен сервер. None - не указан режим.
        :param user: пользователь (если есть)
        :param password: пароль (если есть)
        :param proxy_id: индекс в БД (если не задан, сервер будет занесён в БД)
        '''

        self.ip = ip
        self.port = str(port)

        self.protocol = protocol
        self.country = country

        self.ping = ping

        self.source = source
        self.proxy_id = proxy_id

        self.user = user
        self.password = password

    # ------------------------------------------------------------------------------------------------
    # Обновление данных ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def ping(self) -> int or None:
        '''
        Отдаёт задержку, если она известна

        :return:
        '''
        return self.__ping

    @ping.setter
    def ping(self, value: int or float or None):
        '''
        Устанавливает значение пинга (требуется для округления)

        :param value: значение задержки (None - если неизвестна)
        :return:
        '''
        if value is None:
            self.__ping = value
        else:
            self.__ping = math.floor(value)
        return


