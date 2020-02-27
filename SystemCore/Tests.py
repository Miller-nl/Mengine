from SystemCore.Logging.Loggers.LoggingToJSON import JsonLogger
Logger = JsonLogger(module_name='тест', journals_catalog='D:\Projects\Журналы', journal_file='тест 3')
Logger.to_log('HELLO!')
Logger.to_log('here is a trace', trace=True)

q = []
try:
    a = q[10]
except BaseException:
    Logger.to_log('except??', exception_mistake=True)


