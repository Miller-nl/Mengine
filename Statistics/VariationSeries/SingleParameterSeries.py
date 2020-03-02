'''
Модуль получает набор данных.
Столбцы отмечаются на две категории:
    1. требующие "простой развёртки". Например - столбце с полом, работой и т.п. .
        (эти свойства являются "несовместными" событиями. То есть - мы можем так сделать, и это будет верно)
        При этом развёртка будет идти не как bool, а числом от 0 до 1 (то есть - мы используем вероятность
        того, что то или иное событие имеет указанный параметр). Это нужно для более качественного вероятностного
        "лечения" пропусков.
        (БИВР)
    2. "Числовые" столбцы: возраст, расстояние, вес, прочие параметры.
        (столбцы могут обрабатываться как БИВР или как ИВР с к к-м Стерджесса)
В качестве набора для подготовки следует отправлять ВЕСЬ тренировочный набор данных!
Важно, что "отсутсвующее" значение будет тоже включено в вариационный ряд на нулевое место.
Кроме того, вынести отдельно в модуль "генерацию сеток", которые будут предсказывать,
какое значение может быть в том или ином пропущенном случае.
ОЦЕНКА ВЫБРОСОВ ОТДЕЛЬНО В DataEstimator
Дополнительно, делать оценку корреляции параметров с результатом.
И делать оцценку "критической нехваки информации" - когда у нас пропущено слишкеом много данных.
отдельно
Подсчёт параметров для замены "недостающих значений". (чтобы сохранить распределение)
варианты - среднее, медианное, одно из них + "размытие"
случайное с каким-то законом
'''


class VariationSeries():
    MyName = "VariationSeries"

    # ----------------------------------------------------------------------------------------------------
    # Преднастройка --------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    import pandas as __pd
    import numpy as __np
    import math as __math  # для рассчётов

    Available_types = {}  # Cловарь с типами, которые указывают на тот или иной способ построения вариационных рядов
    Available_types['BRow'] = [__np.str, __np.bool, str, bool]
    Available_types['IRow'] = [__np.float64, __np.int64, int, float]

    Minimum_number_of_values = 3  # Минимальное количество различающихся значений для построения интервального ряда

    def __init__(self, identification_name):
        '''
        :param identification_name:  - имя вызывающего модуля
        '''

        self.__set_communication(identification_name=identification_name)  # Установим модуль связи

    # Функция для инициации модулей коммуникации
    def __set_communication(self, identification_name):
        '''
        :param identification_name: - имя вызывающего модуля
        :return:
        '''
        self.MyName = str(identification_name) + '.' + self.MyName  # Добавим имя вызывающего модуля
        import Communication.WithAnalyst as CWA
        self.__CM = CWA.CommunicationAPI(launch_module_name=self.MyName)
        self.__communication = self.__CM.Communication  # Фунция для коммуникации

        import Communication.ReturnModule as CRM
        self.__RM = CRM.ReturnAPI(launch_module_name=self.MyName)
        self.__ret_function = self.__RM.standart_return  # функция для return-а

    def reset_module(self):

        self.__FramesRows = {}
        '''
        Словарь, в который запоминаются вариационные ряды (если в функции подсчёта указан соответсвующий параметр).
        Для каждого DataFrame указывается "имя", по которому можно будет запрашивать его вариационные ряды

        Структура словаря:
            __FramesRows[frame_name][row_index]
                Если row_index - название колонки, то значение - словарь вида Serie
                Если row_index =='FrameRow', то значение - Многомерный вариационный ряд. Если его (ряда) нет, то None

        Словарь вида Serie имеет индекс [DATA]
        DATA имеет значения:
        'type' - тип ряда: 'BRow' - безинтервальный ряд;
                           'IRow' - интервальный ряд
                            None - ряд не был посчитан
        'row' - Frame - ряд. Или None - если ряд не был посчитан
        'less_min' - элементы, которые вышли левее минимума (у BRow это 0)
        'more_max' - элементы, которые вышли правее максимума (у BRow это 0)
        'dropped' - количество элементов, сброшенных по drop_values
        'None' - количество строк с пропущенным значением
        Суммарно имеем три уровня [имя фрейма][запрашиваемый ряд][параметры ряда]
        '''

        return

    def GetSeries(self):
        '''
        Функция возвращает self.__FramesRows
        :return: self.__FramesRows
        '''
        return self.__FramesRows

    # ----------------------------------------------------------------------------------------------------
    # Выполнение -----------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    def Prepare(self, data_frame,
                confines_dict=False,
                frame_name=False):
        '''
        Функция делает вариационыне ряды для столбцов data_frame: для каждого и "итоговый" - для всех.
        :param data_frame: таблица с данными
        :param frame_name: имя, с которым данные будут занесены во __FramesRows. Если False, то запоминания не будет.
        :param confines_dict: словарь "ограничений". False - нет словаря.
                                Иначе ожидается словарь с мультииндексом: [column_name,data]
                                Где data принимает значения:
                                'min' - минимальное значение для столбца (только для бивр)
                                'max' - максимальное значение для столбца (только для бивр)
                                'drop' - игнорировать значения (это список или одно значение)
                                'points' - количество точек для разбиения в вариационный ряд (только для бивр)
                             эти ограничения будут использоваться при построении рядов.
        :return: Frame_dict - словарь с результатом
        '''

        # Выполним проверку поступившего фрейма
        if not isinstance(data_frame, self.__pd.core.frame.DataFrame):
            if isinstance(data_frame, self.__pd.core.series.Series):
                data_frame = data_frame.to_frame()  # если это Series - конвертнём во фрейм
            else:
                # Иначе - тип не удовлетворителен
                return self.__ret_function(status='Ошибка',
                                           mistakes=[{'where': 'CSVExport',
                                                      'what': 'Тип "file_data" является недопустимым',
                                                      'mistake_data': (
                                                              'Ожидалось pandas.core.frame.DataFrame. Получено ' +
                                                              str(type(data_frame)))
                                                      }]
                                           )

        Frame_dict = {}  # Словарь для вариационных рядов фрейма
        Culumns_list = data_frame.columns.tolist()  # Получим список столбцов

        for column in Culumns_list:
            # Получим из словаря ограничения, если они есть

            column_serie = self.ColumnProcessing(serie_column=data_frame[column])
            '''
            Перевести series к просто параметрам - без имени. Имя юзать тут

            А в селф класть словарь с индексом - колонками. В селфе будет словарь с названиями фреймов.
            '''
            pass

        return

    # ----------------------------------------------------------------------------------------------------
    # Рассчёт ряда по столбцу ----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    def ColumnProcessing(self, serie_column,
                         row_type=False,
                         serie_name='No_name',
                         limiting_minimum=False,
                         limiting_maximum=False,
                         points_amount=False,
                         drop_values=False):
        '''
        Обработка колонки. Функция получает объект Series (столбец DataFrame). Функция открытая
        :param serie_column: объект Series - колонка DataFrame
        :param row_type: явное указание типа ряда, который будет построен. Значения 'IRow', 'BRow'.
                            если не указать тип, а данные имеют числовой вариант, то будет построен IRow,
                            что иногда может стать проблемой. Например, если значения были только 1 и 0.
        :param serie_name: имя столбца - для сообщений с предупреждениями и только.
        :param limiting_minimum: ограничение на минимальное значение (актуально только для ИВР)
        :param limiting_maximum: ограничение на максимальное значение (актуально только для ИВР)
        :param points_amount: количество интервалов, на которые будет выполнено разбиение (актуально только для ИВР)
        :param drop_values: значение или список значений, которые будут сброшены из набора
        :return: Serie - словарь с данными
                            Словарь вида Serie имеет [DATA]
                            DATA имеет значения:
                            'type' - тип ряда: 'BRow' - безинтервальный ряд;
                                            'IRow' - интервальный ряд
                                            False - ряд не был посчитан
                            'row' - Frame - ряд. Или False - если ряд не был посчитан
                            'less_min' - элементы, которые вышли левее минимума (у BRow это 0)
                            'more_max' - элементы, которые вышли правее максимума (у BRow это 0)
                            'step' - "шаг" интервала (у BRow это 0)
                            'dropped' - количество элементов, сброшенных по drop_values
                            'None' - количество строк с пропущенным значением
        '''

        Serie = {}  # Заведём словарь для результата
        '''

        '''
        # Выполним валидацию
        mistakes = self.__column_processing_validator(serie_column=serie_column,
                                                      row_type=row_type,
                                                      serie_name=serie_name,
                                                      limiting_minimum=limiting_minimum,
                                                      limiting_maximum=limiting_maximum,
                                                      points_amount=points_amount,
                                                      drop_values=drop_values)
        if mistakes != []:
            return self.__ret_function(status='Ошибка',
                                       mistakes=mistakes)

        # Возьмём колонку отдельно, чтобы не запороть ничего в исходном наборе
        Exam_column = serie_column.copy(deep=True)

        Serie['None'] = sum(Exam_column.isna())  # Посчитаем количество пустых значений в столбце
        Exam_column.dropna(inplace=True)  # Сбросим пустые зачения в рабочем столбце

        Serie['dropped'] = 0  # Количество сброшенных элементов по списку drop_values
        if not drop_values is False:  # Если указаны значения для сброса
            if not isinstance(drop_values, list):  # Если это одно значение
                drop_values = [drop_values]  # Сделаем список
            shape_before = Exam_column.shape[0]
            Exam_column = Exam_column.loc[~Exam_column.isin(drop_values)]  # Выполним сброс
            Serie['dropped'] = shape_before - Exam_column.shape[0]

        # Определим тип ряда, который будет построен

        if row_type == 'IRow' or row_type == 'BRow':  # Если задан явно
            Row_type = row_type  # Тип ряда, который будет построен

        else:  # Иначе - выясним, какой ряд строить
            Row_type = self.__check_row_type(Exam_column=Exam_column, serie_name=serie_name)
            if Row_type is False:
                unique_types = list(set(Exam_column.apply(type)))  # Получим уникальные типы для отчёта
                return self.__ret_function(status='Ошибка',
                                           mistakes=[{'where': 'ColumnProcessing',
                                                      'what': ('Тип данных столбца: ' + str(serie_name) +
                                                               ' является недопустимым'),
                                                      'mistake_data': ('Ожидались числа, bool или строки. ' +
                                                                       'Получено: ' + str(unique_types))
                                                      }]
                                           )
        # Установим параметры
        Serie['less_min'] = 0  # Вылеты левее
        Serie['more_max'] = 0  # Вылеты правее
        Serie['step'] = 0  # "шаг" интервала для IRow
        Serie['type'] = Row_type  # Занесём данные о типе ряда

        # Построим ряд
        if Row_type == 'IRow':
            result_dict = self.OneDimensional_IRow(values_list=Exam_column,
                                                   points_amount=points_amount,
                                                   limiting_min=limiting_minimum,
                                                   limiting_max=limiting_maximum)

            if result_dict['status'] == 'Успешно':  # Если получение данных успешно
                result_dict = result_dict['result']  # Получим данные результата
            else:  # Иначе
                return self.__ret_function(status=result_dict['status'],
                                           result=result_dict['result'],
                                           mistakes=result_dict['mistakes'])  # Выходим с ошибкой

            Serie['row'] = result_dict['IRow']
            Serie['less_min'] = result_dict['less_minimum']
            Serie['more_max'] = result_dict['more_maximum']
            Serie['step'] = result_dict['step']


        elif Row_type == 'BRow':
            Serie['row'] = self.OneDimensional_BRow(values_list=Exam_column, data_type=Exam_column.dtypes)
        else:
            self.__communication(message_type='WARNING',
                                 message=('Не опознан тип ряда столбца: ' + str(serie_name) + ' - тип ' +
                                          str(Row_type) + '. Столбец пропущен (указан тип ряда None)')
                                 )
            Serie['row'] = False

        return self.__ret_function(status='Успешно',
                                   result=Serie)

    # Валидатор
    def __column_processing_validator(self, serie_column,
                                      row_type,
                                      serie_name,
                                      limiting_minimum,
                                      limiting_maximum,
                                      points_amount,
                                      drop_values):

        mistakes = []
        if row_type not in ['IRow', 'BRow'] and not row_type is False:  # Если значение неудовлетворительное
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Значение "row_type" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ("Ожидалось 'IRow' или 'BRow' или False. Получено " +
                                              str(type(row_type)))
                             })

        if not isinstance(serie_column, self.__pd.core.series.Series):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "serie_column" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось  pd.core.series.Series. Получено ' +
                                              str(type(serie_column)))
                             })
        if serie_column.shape[0] < 2:  # Если подан слишком короткий набор
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Значение "serie_column" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось не менее 2 элементов. Получено ' +
                                              str(serie_column.shape[0]))
                             })
        if not (isinstance(serie_name, str) or serie_name == 'No_name'):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "serie_name" является недопустимым.',
                             'mistake_data': ('Ожидалось строка. Получено ' +
                                              str(type(serie_name)))
                             })
        # Если тип не является разрешённым
        if not (type(limiting_minimum) in self.Available_types['IRow'] or limiting_minimum is False):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "limiting_minimum" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось тип из ' + str(self.Available_types['IRow']) + '. Получено ' +
                                              str(type(limiting_minimum)))
                             })
        if not (type(limiting_maximum) in self.Available_types['IRow'] or limiting_maximum is False):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "limiting_maximum" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось тип из ' + str(self.Available_types['IRow']) + '. Получено ' +
                                              str(type(limiting_maximum)))
                             })

        if not (isinstance(points_amount, int) or points_amount is False):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "points_amount" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось int. Получено ' +
                                              str(type(points_amount)))
                             })
        if not (isinstance(drop_values, list) or points_amount is drop_values):
            mistakes.append({'where': '__column_processing_validator',
                             'what': 'Тип "points_amount" является недопустимым для столбца: ' +
                                     str(serie_name),
                             'mistake_data': ('Ожидалось list. Получено ' +
                                              str(type(drop_values)))
                             })

        return mistakes

    # Функция проверки вида требующегося ряда
    def __check_row_type(self, Exam_column,
                         serie_name):
        '''
        Функция определяет тип ряда для колонки (Series) Exam_column
        :param Exam_column: объект Series с данными
        :return: тип ряда: 'IRow' , 'BRow'
        '''
        data_type = Exam_column.dtypes  # Чекаем тип данных столбца
        if data_type == self.__np.object:  # Если опознали тип данных как np.object, это может быть проблемой

            unique_types = list(set(Exam_column.apply(type)))  # Получим уникальные типы
            if len(unique_types) == 1:  # Если тип один
                # Определим Row_type
                if unique_types[0] in self.Available_types['IRow']:
                    Row_type = 'IRow'
                    self.__communication(message_type='INFO',
                                         message=('Тип данных столбца: ' + str(serie_name) +
                                                  ' опознан как np.object . ' +
                                                  'Столбцу указан тип: ' + str(unique_types[0]) +
                                                  '. Ряд - интервальный.'))
                elif unique_types[0] in self.Available_types['BRow']:
                    Row_type = 'BRow'
                    self.__communication(message_type='INFO',
                                         message=('Тип данных столбца: ' + str(serie_name) +
                                                  ' опознан как np.object . ' +
                                                  'Столбцу указан тип: ' + str(unique_types[0]) +
                                                  '. Ряд - безинтервальный.'))
                else:  # Если не найден удовлетворительный вариант
                    Row_type = False

            elif unique_types == [float, int]:  # Если это циферки
                Row_type = 'IRow'
                self.__communication(message_type='INFO',
                                     message=('Тип данных столбца: ' + str(serie_name) +
                                              ' опознан как np.object . ' +
                                              'В столбце встречены тип float и int.'))
            else:  # Если там не пойми чё
                Row_type = False

        elif data_type in self.Available_types['IRow']:
            # Если коилчество уникальных значений больше чем Minimum_number_of_values
            if Exam_column.nunique() > self.Minimum_number_of_values:
                Row_type = 'IRow'  # Строим интервальный ряд
            else:  # Если меньше
                Row_type = 'BRow'  # то всё-таки безинтервальный

        elif data_type in self.Available_types['BRow']:
            Row_type = 'BRow'

        else:
            Row_type = False

        return Row_type

    # ----------------------------------------------------------------------------------------------------
    # Функции построения безинтервального ряда -----------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    # Для безинтервального ряда
    def OneDimensional_BRow(self, values_list, data_type=object):
        '''
        Функция делает безинтервальный варационный ряд
        :param values_list: список значений или series
        :param data_type: тип данных. По дефолту - object
        :return: вариационный ряд DataFrame('right_point','hits'), или False в случае ошибки
        '''

        if isinstance(values_list, list):  # Если это список
            values_list = self.__pd.Series(values_list)  # Переведём в Series
        elif not isinstance(values_list, self.__pd.core.series.Series):  # если это не список и не Series
            return self.__ret_function(status='Ошибка',
                                       mistakes=[{'where': 'OneDimensional_BRow',
                                                  'what': 'Тип "values_list" является недопустимым',
                                                  'mistake_data': ('Ожидалось list или Series. Получено ' + str(
                                                      type(values_list)))
                                                  }]
                                       )

        row = values_list.value_counts()  # получим series значений с количеством "совпадений"
        # Сделаем фрейм (первая строка - значения, вторая - количество совпадений)
        BRow = self.__pd.DataFrame(data=[row.index, row.values])
        BRow = BRow.T  # Транспонируем
        BRow.columns = ['value', 'hits']  # Заведём названия колонок
        BRow.sort_values(by=['value'])  # Отсортируем по значению для удобства
        BRow['value'] = BRow['value'].astype(data_type)
        BRow.reset_index(drop=True, inplace=True)  # Обновим индекс

        return self.__ret_function(status='Успешно', result=BRow.copy(deep=True))

    # ----------------------------------------------------------------------------------------------------
    # Функции построения интервального ряда --------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------

    # Для интервального ряда
    def OneDimensional_IRow(self, values_list,
                            points_amount=False,
                            limiting_min=False,
                            limiting_max=False
                            ):
        '''
        Функция делает интервальный варационный ряд
        :param values_list: список значений (или series)
        :param points_amount: количество интервалов. Если False, считаем по Стерджессу
        :param limiting_min: значение, которое ограничивает "снизу". Все случаи, в которых value ниже этого
                                параметра будут считаться в вариационном ряде на интервал, содержащий это ограничение.
        :param limiting_max: значение, которое ограничивает "сверху". Все случаи, в которых value выше этого
                                параметра будут считаться в вариационном ряде на интервал, содержащий это ограничение.
        :return: Стандартный ретёрн вернёт словарь с индексами: IRow, less_minimum, more_maximum.
                    IRow - вариационный ряд в виде DataFrame('middle_point','hits'),где:
                                middle_point - средняя точка интервала.
                                hits - количество "попаданий" в интервал
                    step - "шаг" интервала.
                    less_minimum, more_maximum - количество элементов за границами списка (это int числа)
                 Или "Ошибка".
        '''

        # Выполним валидацию
        mistakes = self.__one_dimensional_irow_validator(values_list=values_list,
                                                         points_amount=points_amount,
                                                         limiting_minimum=limiting_min,
                                                         limiting_maximum=limiting_max)
        if mistakes != []:
            return self.__ret_function(status='Ошибка',
                                       mistakes=mistakes)

        if isinstance(values_list, list):  # Если это список
            values_list = self.__pd.Series(values_list)  # Переведём в Series
        else:
            values_list = values_list.copy(deep=True)  # Явно передадим в values_list данные

        result = {}  # Заведём словарь результата

        split_points = self.__get_split_points(values_list=values_list,
                                               points_amount=points_amount,
                                               limiting_minimum=limiting_min,
                                               limiting_maximum=limiting_max
                                               )  # Получим список точек для разбиения
        # Получим шаг интервала
        result['step'] = (split_points[len(split_points) - 1] - split_points[0]) / len(split_points)

        result['IRow'] = self.__pd.DataFrame({'middle_point': [],
                                              'hits': []})  # Сам вариационный ряд
        result['IRow']['middle_point'] = result['IRow']['middle_point'].astype(
            float)  # Зададим тип разделяющих точек (именно float)
        result['IRow']['hits'] = result['IRow']['hits'].astype(int)  # Зададим количество "хитов"

        # Снимем значения, выходящие за рамки limiting_min и limiting_max, если надо
        if not limiting_min is False:
            result['less_minimum'] = values_list.loc[values_list < limiting_min].shape[0]
            values_list.drop(index=values_list.loc[values_list < limiting_min].index,
                             inplace=True)  # Дропнем лишнее
        else:
            result['less_minimum'] = 0

        if not limiting_max is False:
            result['more_maximum'] = values_list.loc[values_list > limiting_max].shape[0]
            values_list.drop(index=values_list.loc[values_list > limiting_max].index,
                             inplace=True)  # Дропнем лишнее
        else:
            result['more_maximum'] = 0

        values_list.sort_values(inplace=True)  # Отсортируем список значений для потимизации (после дропа лишнего)
        values_list.reset_index(inplace=True, drop=True)  # Скинем индекс

        print('Точки для интервалов ', str(split_points))  # !!!!!!!!!!!!!!!!!!!!!
        print('less_minimum:', result['less_minimum'])  # !!!!!!!!!!!!!!!!!!!!!
        print('more_maximum:', result['more_maximum'])  # !!!!!!!!!!!!!!!!!!!!!
        print('step: ', result['step'])
        print('values_list')
        print(values_list.value_counts().sort_values(axis='index').head(10))

        current_element = 0  # Счётчик "текущего" элемента списка values_list
        values_list_shape = values_list.shape[0]
        for split_point_number in range(1, len(split_points)):  # Пошли считать хиты с первой(!) точки (не нулевой!)

            # заведём строку для данных
            result['IRow'].at[split_point_number] = [split_points[split_point_number] - result['step'] / 2, 0]

            print('Секция: ', split_points[split_point_number - 1], ' - ',
                  split_points[split_point_number])  # !!!!!!!!!!!!!!!!!!!!!!!!
            print(result['IRow'].loc[split_point_number])  # !!!!!!!!!!!!!!!!!!!!!!!!

            if current_element == values_list_shape:  # Если current_element выходит за рамки values_list
                break  # принудительно закончим (чтобы в While не было ошибки)

            while values_list.loc[current_element] <= split_points[
                split_point_number]:  # Пока точки попадают слева от границы или на неё
                # Зафиксируем хит
                result['IRow'].at[split_point_number, 'hits'] = result['IRow'].loc[split_point_number, 'hits'] + 1
                current_element += 1  # Сдвинули счётчик (только если засчитали хит!)
                if current_element == values_list_shape:  # Если current_element выходит за рамки values_list
                    break  # принудительно закончим

        result['IRow']['hits'] = result['IRow']['hits'].astype(int)  # интнем хиты

        return self.__ret_function(status='Успешно', result=result)

    # Валидатор для OneDimensional_IRow
    def __one_dimensional_irow_validator(self, values_list,
                                         points_amount,
                                         limiting_minimum,
                                         limiting_maximum):

        mistakes = []
        if not (isinstance(values_list, self.__pd.core.series.Series) or isinstance(values_list, list)):
            mistakes.append({'where': '__one_dimensional_irow_validator',
                             'what': 'Тип "values_list" является недопустимым',
                             'mistake_data': ('Ожидалось list или Series. Получено ' + str(type(values_list)))
                             })

        if not (isinstance(points_amount, int) or (points_amount is False)):
            mistakes.append({'where': '__one_dimensional_irow_validator',
                             'what': 'Тип "points_amount" является недопустимым',
                             'mistake_data': ('Ожидалось int или False. Получено ' + str(type(points_amount)))
                             })
        # Available_types['IRow']
        if not limiting_minimum is False:  # Если это не False
            success = False
            for el_type in self.Available_types['IRow']:
                if isinstance(limiting_minimum, el_type):  # Если найден "разрешённый тип"
                    success = True  # Установим индикатор
                    break  # Закончим проверку
            if not success:
                mistakes.append({'where': '__one_dimensional_irow_validator',
                                 'what': 'Тип "limiting_minimum" является недопустимым',
                                 'mistake_data': ('Ожидался тип из: '
                                                  + str(self.Available_types['IRow']) +
                                                  '. Получено ' + str(type(limiting_minimum)))
                                 })
        if not limiting_maximum is False:  # Если это не False
            success = False
            for el_type in self.Available_types['IRow']:
                if isinstance(limiting_maximum, el_type):  # Если найден "разрешённый тип"
                    success = True  # Установим индикатор
                    break  # Закончим проверку
            if not success:
                mistakes.append({'where': '__one_dimensional_irow_validator',
                                 'what': 'Тип "limiting_maximum" является недопустимым',
                                 'mistake_data': ('Ожидался тип из: '
                                                  + str(self.Available_types['IRow']) +
                                                  '. Получено ' + str(type(limiting_maximum)))
                                 })

        return mistakes

    # Функция для определения "точек разделения" размаха выборки на интервалы
    def __get_split_points(self, values_list,
                           points_amount=False,
                           limiting_minimum=False,
                           limiting_maximum=False):
        '''
        Функция для получения точек разбиения интервалов для Безинтервального вариационного ряда.
        Важно, что функция даёт именно точки для разбиения интервалов
        :param values_list: список(!) Series или  значений, встречающихся в выборке
        :param points_amount: количество интервалов. Если False, считаем по Стерджессу
        :param limiting_minimum: значение, которое ограничивает "снизу".
        :param limiting_maximum: значение, которое ограничивает "сверху".
        :return: список с точками для разбиения ряда
        '''

        if isinstance(values_list, list):  # Если это список
            values_list = self.__pd.Series(values_list)  # Сделаем список

        elif not isinstance(values_list, self.__pd.core.series.Series):  # Если не series  не список
            self.__communication(message_type='CRITICAL',
                                 message=('В __get_split_points подан values_list не список и не Series.'))
            return

        # Определим размах выборки
        if limiting_minimum is False:  # Если не указана нижняя граница
            limiting_minimum = values_list.min()
        if limiting_maximum is False:  # Если не указана верхняя граница
            limiting_maximum = values_list.max()

        # Определим шаг
        if not points_amount is False:  # Если указано значение
            if not isinstance(points_amount, int):
                # Если значение не целое, но оно указано
                self.__communication(message_type='WARNING',
                                     message=('При разбиении выборки на интервалы указано неверное значение ' +
                                              ' количества интервалов: ' + str(points_amount) +
                                              ' тип - ' + str(type(points_amount)) +
                                              '. Считаем по Стерджессу.')
                                     )
                points_amount = self.__math.ceil(
                    1 + self.__math.log2(values_list.shape[0]))  # Определим количество интервалов
            # Если указано и целое - всё ок. Ничего не делаем

        else:  # Если значение не указано
            points_amount = self.__math.ceil(
                1 + self.__math.log2(values_list.shape[0]))  # Определим количество интервалов

        step = (limiting_maximum - limiting_minimum) / points_amount

        # Установим точки
        points_list = []
        x_point = limiting_minimum - step / 2  # "Нулевая" точка
        points_list.append(x_point)
        # Почему делим на 1.5 - чтобы не дать "дополнительный лишний интервал
        # но и при малых числах не получить проблему
        while x_point < (limiting_maximum):  # Пока не вышли за границы
            x_point += step
            points_list.append(x_point)  # Добавим точку в список

        return points_list  # Вернём список точек


'''
Тема такая. Вот у нас есть пол - м/ж.
Если мы делаем бинарный нейрон - то он не активируется на одном из значений. Тогда, "влияние" пола в одном
из случаев должны апроксимировать другие факторы, что непраильно.
Предложение - попробовать два нейрона: мужской и женский. Которые будут активироваться.
Проверить экспериментально. Ожидается, что два нейрона на бинарный признак будут лучше чем один.
Возможно, что с "курением" такое не прокатит. т.к. мы считаем для здорового организма, а курение "даёт дебаф".
То есть - не все признаки могут быть таким образом сделаны! Это важно!
А вот для "городской/деревенский" - верно указанное выше.
'''