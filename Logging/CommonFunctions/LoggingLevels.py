import logging
# ---------------------------------------------------------------------------------------------
# Уровни логирования --------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
logging_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
logging_levels_int = {'DEBUG': 10,
                      'INFO': 20,
                      'WARNING': 30,
                      'ERROR': 40,
                      'CRITICAL': 50}
default_logging_level = 10

def int_logging_level(logging_level: str or int or  float, default_level: int = default_logging_level) -> int:
        '''
        Получение форматного целочисленного значения урвоня логирования.

        :param logging_level: уровень логирования.
        :param default_level: дефолтный уровень логирования.
        :return: строка с именем уровня логирования.
            10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL.
            Если уровень логирования не опознан, вернётся "дефолтный" - default_logging_level.
        '''
        if isinstance(logging_level, str):
            try:  # Отдадим значение из словаря
                return logging_levels_int[logging_level]
            except KeyError:  # Если его нет
                return default_level  # Отдадим дефолтное

        elif isinstance(logging_level, float):  # Если это число с точкой
            return int(logging_level)  # интнем его

        else:  # Если задано число
            return logging_level  # вернём его

def str_logging_level(logging_level: str or int) -> str:
        '''
        Получение форматного строкового значения урвоня логирования.

        :param logging_level: уровень логирования.
        :return: строка с именем уровня логирования.
            10 - DEBUG; 20 - INFO; 30 - WARNING; 40 - ERROR; 50 - CRITICAL.
            Если уровень логирования не опознан, вернётся "дефолтный" формат - 'Level 113'
        '''
        if isinstance(logging_level, str):
            if logging_level in logging_levels:  # Првоерим по списку
                return logging_level  # Если из списка - вернём как есть
            return logging.getLevelName(logging_level)  # Иначе прогоним через "получение уровня"

        else:  # Если задано число
            return logging.getLevelName(logging_level)  # вернём строковый уровень