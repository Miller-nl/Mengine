from ..AppFrame.App import ApplicationFramework
from SQLAdapters.CommomAdapter import CommonAdapterInterface
import socket
import sys
import time
import socketserver
import queue


import threading
import multiprocessing

class Server:


    def __init__(self,
                 port: int,
                 sql_adapter: CommonAdapterInterface,
                 host: str = 'locallhost',
                 app: type = ApplicationFramework,

                 ):

        self.__host = host
        self.__port = port

        self._App = app

        self.__sql_adapter = sql_adapter

        # очередь. Ограничения на потоки

        # В постановщик в очередьт добавить логирование и таймаут. Если очередь занята, то логируем и заканчиваем.
        # + как ответить на сообщение?


        pass

