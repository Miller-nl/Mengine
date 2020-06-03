import traceback
import sys
# ---------------------------------------------------------------------------------------------
# Работа со следом и ошибками -----------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
def get_traceback() -> list:
    '''
    Фукнция возвращяет набор объектов traceback.FrameSummary. Нужна для логгирование ошибок и действий.
    Структура элемента списка:
        Для <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\pydevconsole.py, line 386 in <module>>
        .name = '<module>'
        .filename = 'C:\\Program Files\\JetBrains\\PyCharm Community Edition 2018.3.5\\helpers\\pydev\\pydevconsole.py'
        .line = 'pydevconsole.start_client(host, port)'
        .lineno = 386
        .locals = kjgahsdgf

    :return: список "пути", не учитывающего текущую функцию
    '''
    trace = traceback.extract_stack()[:-1]  # -1 нужен чтобы убрать себя (_get_traceback) из следа
    return trace


def expand_traceback(trace: list) -> list:
    '''
    Разворачивает "след" в список форматных строк, которые будет удобно обрабатывать в будущем.

    Структура объекта списка:
        Для <FrameSummary file C:\Program Files\JetBrains\PyCharm Community Edition 2018.3.5\helpers\pydev\pydevconsole.py, line 386 in <module>>
        .name = '<module>'
        .filename = 'C:\\Program Files\\JetBrains\\PyCharm Community Edition 2018.3.5\\helpers\\pydev\\pydevconsole.py'
        .line = 'pydevconsole.start_client(host, port)'
        .lineno = 386
        .locals = kjgahsdgf

    :param trace: след, полученный через traceback.extract_stack(). Если список пуст, ответ будет пустой строкой.
    :return: строка в обычном или в json формате.
    '''
    trace_str = []
    for tr in trace:  # Погнали собирать
        trace_str.append(f'File: "{tr.filename}", in {tr.name} line {tr.lineno}: {tr.line}')  # Форматная строка
    return trace_str


def expand_exception_mistake(exception_mistake: tuple = None,
                             with_traceback: bool = True) -> tuple or None:
    '''
    Функция разворачивает tuple, полученный в try/except функцией sys.exc_info() tuple, содержащий строку
        с сообщением об ошибке и след, если он требуется. Строка форматного сообщения 'ErrorType: error message'

    :param exception_mistake: ошибка, полученная при try except функцией sys.exc_info(). Если параметр None,
        данные об ошибке будут запрошены внутри функции.
        Структура tuple: (ErrorType, args, traceback)
    :param with_traceback: добавлять ли "след" в tuple?
    :return: tuple следующего содержания:("строка с ошибкой и аргументом", traceback_list). traceback_list может
        быть None, если with_traceback - False.
        None - в случае, если tuple с данными об ошибке был (None, None, None) - "нет ошибки"
    '''

    if exception_mistake is None:  # Чекнем, передана ли ошибка
        exception_mistake = sys.exc_info()  # Если не передана - чекнем, есть ли ошибка вообще?

    if exception_mistake == (None, None, None):  # Если ошибки нет
        return None

    export_string = f'{exception_mistake[0]}: {exception_mistake[1]}'  # форматная строка
    if with_traceback:
        trace = expand_traceback(trace=traceback.extract_tb(exception_mistake[2]))
    else:
        trace = None
    return (export_string, trace)


def prepare_exception(exception_mistake: tuple or bool = False) -> tuple or None:
    '''
        Функция реализует логику обработку "исключений" в логере.

        :param exception_mistake: данные об ошибке. Или это tuple, полученный от sys.exc_info(), состоящий из
            всех трёхэлементов, или указание на запрос ошибки внутри функции логирования.
            Если этот параметр не False, то trace игнорируется
        :return: или None, или tuple вида ("строка с ошибкой и аргументом", traceback_list)
        '''
    if exception_mistake is True:  # Если ошибку надо запросить тут
        exception_mistake = expand_exception_mistake()  # Получим развёрнутую ошибку или None, если её нет
    elif isinstance(exception_mistake, tuple):  # Если typle передан
        # Форматируем его
        exception_mistake = expand_exception_mistake(exception_mistake=exception_mistake)
    else:
        exception_mistake = None  # иначе укажем, что данных нет
    return exception_mistake


def prepare_trace(trace: list or bool = True,
                  drop_last: int = 0) -> list or None:
    '''
    Функция реализует логику обработки "следа"  в логере.

    :param trace: список объектов следа, полученный через traceback.extract_stack(), или указание на запрос
        следа внутри функции. Если задан exception_mistake, то trace игнорируется.
    :param drop_last: количество последних элементов следа, которые мы сбросим
    :return: Список со следом или None/
    '''
    if trace is False:  # Если след брать не нужно
        trace = None
    elif trace is True:  # Если надо получить след тут
        trace = get_traceback()[:- 1 - drop_last]  # Минус prepare_trace
    elif isinstance(trace, list):  # Если след есть
        trace = expand_traceback(trace=trace)  # форматируем

    return trace

