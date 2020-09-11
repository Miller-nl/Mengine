from Exceptions.ExceptionTypes import MethodPropertyError
from FilesSystem.FilesReaders.JSONL import JSONL

from ..Message.Message import Message
from ..AppsExamples import MessagePreparerExample
from ..Message.LoggingLevels import int_logging_level

import threading


class JSONpreparer:

    def prepare(self, message: Message) -> dict:
        return message.get_dict()


# передаём путь или райтер
class JsonLogger:

    def __init__(self,
                 file_path: str,
                 logging_level: str or int = 'DEBUG',
                 preparer: MessagePreparerExample = JSONpreparer()):

        self.__preparer = preparer
        self.__file_path = file_path
        if not hasattr(preparer, 'prepare'):
            raise MethodPropertyError(f'Worker {type(preparer)} have no "prepare" method.')

        self.__writer = JSONL()

        self.__mutex = threading.RLock()

        self.__logging_level = int_logging_level(logging_level=logging_level)

    # ---------------------------------------------------------------------------------------------
    # properties ----------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    @property
    def file_path(self) -> str:
        return self.__file_path

    @property
    def logging_level(self) -> int:
        return self.__logging_level
    # ---------------------------------------------------------------------------------------------
    # Общие property ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def export(self, message: Message):
        if message.logging_level < self.logging_level:
            return

        with self.__mutex:
            export_message = self.__preparer.prepare(message)
            self.__writer.write_line(file_data=export_message,
                                     full_path=self.__file_path)
            return
