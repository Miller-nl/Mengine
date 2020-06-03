
class RemoteConnectionData:
    '''
    Объект, хранящий данные для удалённого подключения к базе данных: драйвер, адрес, авторизацию.
    Если объект используется для подключения к локальной БД, то у него заданы только движок и каталог.


    Методы и свойства:
        engine - название движка, на котором работает база (PostgreSQL, MySQL). Без версии

        base_name - имя базы данных

        catalog - каталог базы

        host - хост

        port - порт

        user - пользователь

        password - пароль

        server - host:port

        authorization - "пользователь:пароль"
    '''

    def __init__(self,
                 engine: str,
                 base_name: str = None,
                 catalog: str = None,
                 host: str = None, port: str or int = None,
                 user: str = None, password: str = None):
        '''

        :param engine: название движка, на котором работает база (PostgreSQL, MySQL, SQLite). Без версии
        :param base_name: имя базы
        :param catalog: каталог с файлом базы для SQLite
        :param host: адрес
        :param port: порт
        :param user: пользователь
        :param password: пароль
        '''

        self.__engine = engine
        self.__base_name = base_name
        self.__catalog = catalog
        self.__host = host
        if port is None:
            self.__port = port
        else:
            self.__port = int(port)
        self.__user = user
        self.__password = password

    # ------------------------------------------------------------------------------------------------
    # Доступы ----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    @property
    def engine(self) -> str:
        '''
        Движок, на котором работает база.

        :return: название движка без версии (PostgreSQL, MySQL)
        '''
        return self.__engine

    @property
    def base_name(self) -> str or None:
        '''
        Имя базы

        :return:
        '''
        return self.__base_name

    @property
    def catalog(self) -> str or None:
        '''
        Для SQLite это каталог базы

        :return: строка с каталогом
        '''
        return self.__catalog

    @property
    def host(self) -> str or None:
        '''
        Хост

        :return:
        '''
        return self.__host

    @property
    def port(self) -> int or None:
        '''
        Порт в виде строки

        :return:
        '''
        return self.__port

    @property
    def user(self) -> str or None:
        '''
        имя пользователя

        :return:
        '''
        return self.__user

    @property
    def password(self) -> str or None:
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


DefaultDB = RemoteConnectionData(engine='MySQL',
                                 base_name='parser',
                                 host='seo-mysql.bazadev.net', port='3306',
                                 user='parser', password='Oyoo8laeNgegho')