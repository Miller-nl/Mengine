from .Common import CommonMethods
from Exceptions.ExceptionTypes import ProcessingError, ValidationError

import pickle


class PICKLE(CommonMethods):
    '''
    Класс для считывания и сохранения pickle объектов.

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

    def __init__(self):
        '''
        '''

        # Выполним стандартный init
        CommonMethods.__init__(self, save_loaded=False)

    # ------------------------------------------------------------------------------------------------
    # Чтение -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def read(self, full_path: str) -> object:
        '''
        Функция считывания json файла

        :param full_path: полный путь к файлу
        :return: считанный файл в виде JSON объекта
        '''
        if not full_path.endswith('.pickle'):
            raise ValidationError("Incorrect file extension. Only '.pickle' is available.")

        if not self.check_access(path=full_path):
            raise ProcessingError('No access to file')

        # читаем
        with open(full_path, mode='rb') as file:
            result = pickle.load(file)

        return result

    # ------------------------------------------------------------------------------------------------
    # Запись -----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    def write(self, file_data: object, full_path: str, shift_name: bool or None = True) -> bool or str:
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
        if not full_path.endswith('.pickle'):
            raise ValidationError("Incorrect file extension. Only '.pickle' is available.")

        name_shifted = False
        if self.check_access(path=full_path):
            if shift_name is None:
                return False
            elif shift_name is True:
                full_path = self.name_shifting(full_path=full_path, expansion='.json')
                name_shifted = True

        # пишем
        with open(full_path, mode='wb') as file:
            pickle.dump(file_data, file, pickle.HIGHEST_PROTOCOL)
            file.flush()

        if name_shifted:
            return full_path
        else:
            return True
