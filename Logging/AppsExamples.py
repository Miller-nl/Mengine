from Exceptions.ExceptionTypes import MethodPropertyError
from .Message.LoggingLevels import int_logging_level
from .Message.Message import Message

import threading

class MessagePreparerExample:
    '''
    An application that prepares a message for transmission to the writer.
    '''

    def prepare(self, message: Message,
                **kwargs) -> str:
        export_message = f"time: {message.time} {message.logging_level} message: {message.message}"
        return export_message


class ExporterAppExample:
    '''
    Application exporting the message.
    '''
    def __init__(self, preparer: MessagePreparerExample = MessagePreparerExample(),
                 logging_level: str or int = 'DEBUG',
                 **kwargs):

        if not hasattr(type(preparer), 'prepare'):
            raise MethodPropertyError(f'Worker {type(preparer)} have no "prepare" method.')

        self.__preparer = preparer
        self.__mutex = threading.RLock()

        self.__logging_level = int_logging_level(logging_level=logging_level)

    @property
    def logging_level(self) -> int:
        return self.__logging_level

    def export(self, message: Message,
               **kwargs):
        if message.logging_level < self.logging_level:
            return

        with self.__mutex:
            export_message = self.__preparer.prepare(message)
            print(export_message)
            return