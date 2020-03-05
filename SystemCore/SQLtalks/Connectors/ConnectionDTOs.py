
class ConnectionData:
    '''
    Объект, хранящий данные для подключения
    '''
    def __init__(self, base_name: str,
                 host: str, port: str,
                 user: str, password: str):
        '''

        :param base_name: имя базы
        :param host: адрес
        :param port: порт
        :param user: пользователь
        :param password: пароль
        '''

        self.__base_name = base_name
        self.__host = host
        self.__port = str(port)
        self.__user = user
        self.__password = password

    # ------------------------------------------------------------------------------------------------
    # Доступы ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def base_name(self) -> str:
        '''
        Имя базы

        :return:
        '''
        return self.__base_name

    @property
    def host(self) -> str:
        '''
        Хост

        :return:
        '''
        return self.__host

    @property
    def port(self) -> str:
        '''
        Порт в виде строки

        :return:
        '''
        return self.__port

    @property
    def user(self) -> str:
        '''
        имя пользователя

        :return:
        '''
        return self.__user

    @property
    def password(self) -> str:
        '''
        пароль

        :return:
        '''
        return self.__password


    @property
    def server(self) -> str:
        '''
        Отдаёт хост и порт

        :return: "хост:порт"
        '''
        return f'{self.host}:{self.port}'

    @property
    def authorization(self) -> str:
        '''
        Отдаёт пользователя и пароль

        :return: "пользователь:пароль"
        '''
        return f'{self.user}:{self.password}'

