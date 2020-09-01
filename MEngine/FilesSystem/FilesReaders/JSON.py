from .Common import CommonMethods
from MEngine.Exceptions.ExceptionTypes import ProcessingError, ValidationError

import json


class JSON(CommonMethods):
    '''
    Класс для считывания и сохранения json объектов.

    Методы и свойства:
        Имена и пути
            concat_path() - соединить каталог и имя файла

            extract_name() - выделить имя файла из пути

            extract_extension() - выделить расширение файла из пути

            shift_name() - функция модификации имени файла, если оно не является уникальным.

        Проверки
            check_access() - проверка доступа

            get_encoding() - получить кодировку файла

        Настройки считывания
            save_loaded - сохранять ли считанные файлы?

            loaded - словарь сохранённых файлов

            _reset_loaded - обновить словарь сохранённых файлов

        Чтение - запись
            write() - запись

            read() - чтение
    '''


    def __init__(self, save_loaded: bool = False):
        '''

        :param save_loaded: сохоанять ли считанные файлы?
        '''

        # Выполним стандартный init
        CommonMethods.__init__(self, save_loaded=save_loaded)

    # ------------------------------------------------------------------------------------------------
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read(self, full_path: str, save_loaded: bool = None,
             encoding: str = None) -> object:
        '''
        Функция считывания json файла

        :param full_path: полный путь к файлу
        :param save_loaded: сохранить ли загруженный файл? True - да, False - нет, None - использовать стандартную
            настройку (save_loaded)
        :param encoding: строка, явно указывающая кодировку или None для её автоопределения
        :return: считанный файл в виде JSON объекта
        '''
        if not full_path.endswith('.json'):
            raise ValidationError("Incorrect file extension. Only '.json' is available.")

        if not self.check_access(path=full_path):
            raise ProcessingError('No access to file')

        # определим кодировку файла
        if encoding is None:
            encoding = self.get_encoding(full_path=full_path)

        # читаем
        with open(full_path, mode='r', encoding=encoding) as file:
            result = json.load(file)

        if (save_loaded is None and self.save_loaded) or save_loaded is True:
            self._ad_loaded(full_path=full_path,
                            data=result)

        return result

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: object, full_path: str, shift_name: bool or None = True,
              encoding: str = 'utf-8') -> bool or str:
        '''
        Фнукия записывает данные в json файл

        :param file_data: данные для экспорта в файл
        :param full_path: полное имя файла
        :param shift_name: разрешена ди замена имени: True - сдвинуть имя при совпадении на "(N)",
            False - заменить файл, None - отказаться от экспорта в случае совпадения имён.
        :return: True - успешно экспортнуто, имя уникально
            False - отказ от экспорта
            str - успешно экспортнуто, имя изменено
        '''
        if not full_path.endswith('.json'):
            raise ValidationError("Incorrect file extension. Only '.json' is available.")

        name_shifted = False
        if self.check_access(path=full_path):
            if shift_name is None:
                return False
            elif shift_name is True:
                full_path = self.name_shifting(full_path=full_path, expansion='.json')
                name_shifted = True

        # пишем
        with open(full_path, mode='w', encoding=encoding) as file:
            file.write(json.dumps(file_data))
            file.flush()

        if name_shifted:
            return full_path
        else:
            return True



