

from Logging.CommonLoggingClient import CommonLoggingClient
from Logging.LoggingWorkers.LoggingToJSON import JsonLogger

JL = JsonLogger('D:\Projects\Tests')
CLC = CommonLoggingClient('Тест 1')
CLC.add_writer(JL, 'JL')
CLC.to_log('Mes 1')