
'''
import Parser_proxy as Pp
#Парсер прокси. Крутится по кругу
Z=Pp.AddProxy(repetitions=True)# Оставим парситься на ночь
#SQL - сегодняшние call_date=now()::date
import SystemCore.Proxy.Parser_proxy as Pp
#Парсер прокси. Крутится по кругу
Z=Pp.AddProxy(repetitions=True,
              get_from='SQL',
              get_condition=' call_date<>now()::date ')# Оставим парситься на ночь
Можно добавить "get_from='site',get_condition="all" "
Чтобы вместо "auto" вызывалась функция, которая в мультипоточном
режиме запустит по экземпляру класса на каждый источник.
http://foxtools.ru/Proxy
'''


class AddProxy:
    '''
    Как работает:
    - Берём данные с одного(!) указанного источника.
    - Чекаем их на доступность + пингуем(если стоит такая настройка - желательно)
    - Выгружаем данные в таблицу(если стоит такая настройка - желательно)
    Выполнять можно сразу много раз с помощью repetitions.
    Если надо получить набор прокси, поставьте repetitions=False, и интересующие вас данные
    будут находиться в объекте self.Proxy_list. Вы сможете взять их по концу выполнения __init__().
    Также можно добавить в будущем экспорт на API
    Важно! Что сервера дефолтно не пингуются по "основной ссылке". Дефолтная ссылка пока вообще не используется.
    Параметры запуска:
    repetitions=False - Количество повторейний.
                        Значения: False или 0 - без повторений
                                  True - бесконечно крутиться
                                  N - выполнить N раз
    need_My_proxy=False - Нужно ли использовать прокси при парсинге? (то есть, дёргать прокси через прокси)
                          Значения: False - нет, прокси не использовать
                                    True - использовать лист из 10 прокси
                           Желательно использовать.
    Defult_ping_link=False - Изменить значение "основной ссылки поумолчанию". За новое значение берётся Defult_ping_link
    defult_timeout=False - Изменить стандартное время ожидания ответа сервера? За новое значение берётся defult_timeout
    max_timeout=False - Изменить максимальный таймаут для прозвона прокси? За новое значение берётся max_timeout
    unacceptable_number_of_tests=False - изменить количество прозвонов, после которого прокси считается мёртвым.
    get_from='site' - откуда берём данные
    get_condition='Free-proxy' - условие
            Подробнее:
            Эти две переменные связаны друг с другом. Доступные варианты:
            get_from='site',get_condition='имя сайта в __Soursers_data'
            get_from='SQL',get_condition='условие на выбор "WHERE..." ' . Автоматически сервера сортируются по timeout
                    Для проверки sql таблицы ОБЯЗАТЕЛЬНАЯ ЧАСТЬ УСЛОВИЯ ' AND call_date<>now()::date '
                    чтобы не брать сервера, которые уже обновлены.
            get_from='get_frame', get_condition=df cо столбцами: 'protocol','server_ip','server_port',
                                                                 'login','password'.
                                                                 'sourse' будет поставлен "script".
                                        Все строки должны быть без "пустот". Иначе такая строка сбросится.
    do_estimate=True - делать ли оценку доступности прокси: t/f
    export_to_sql=True - Делать ли экспорт в базу. Рекомендуется делать всегда.
                         Если запускаете с повторениями, ОБЯЗАТЕЛЬНО ставить True!
    clean_exported_to_sql=True - Удалить ли экспортированные в SQL сервера. Сделать False, если они нужны!
                                 Если без повторений (), то автоматически clean_exported_to_sql=False.
                                 Если бесконечно повторять, то автоматически clean_exported_to_sql=True,
                                 Если N повторений, и clean_exported_to_sql не задан, то он True.
                                 Задавать параметр имеет смысл только при N повторений в repetitions. Иначе он ставится
                                 автоматически.
    sql_batch_size=False - Изменить дефолтный размер набора, который подгрузится из базы? (поумолчанию 300 штук)
    quiet_mod=False - Использваоть ли "Тихий режим"? t/f. (без вывода инфы, кроме случаев, когда инфа должна быть введена)
    auto=True  #Автоматически запуститься и отработать.
                В противном случае модуль НИЧЕГО не сделает, кроме автонастройки.
    Полезные функции:
    auto_work_mode(repetitions,
                   get_from,get_condition,
                   need_My_proxy,
                   export_to_sql
                   )
                   Функция "выполнения цикла автоматического прохода".
                   Если вам нужно периодически обновлять набор прокси и дёргать их в программу, запустите экземпляр
                   класса с auto=False и repetitions=False(!).
                   И для получения списка прокси запустите эту функцию с repetitions=False или N (лучше False). После
                   её выполнения обратитесь к параметру Proxy_list экземпляра класса.
                   Для "зачистки" старых прокси есть функция reset_Proxy_lists
    reset_Proxy_lists - "скинуть" список Proxy_list
    add_proxy - Добавить прокси сервер в список. Добавляется один прокси. Возвращается t - успешно или 'Ошибка - ', если нет.
    check_Proxy_list - Обновить данные о имеющихся серверах
    fill_My_proxy_from_self - завполнить список "моих прокси" (через которые скрипт парсит источники) из имеющихся прокси
    check_My_proxy - проверить доступность моих прокси и удалить недоступные
    import_from_sql(where) - заполнить список проксей с базы. (where - условие на выбор прокси)
    export_set_to_sql(clean_exported) - экспорт в базу. (clean_exported - удалить ли экспортированные. False, если они ещё нужны)
    Для каждого источника есть своя "именная" функция (named_update_function),
    которая берёт HTML-ТЕКСТ страницы источника, выделяет в нём данные о прокси-серверах и заносит их в self.Proxy_list
    !!!Чтобы добваить источник, его надо впиать в self.__Soursers_data через функцию self.__fill_sourses (прямо в ней)
    и сделать для него именную функцию (пример - __get_Free_proxy).
    После чего нужно добавить эту функцию в специальный словарь __named_functions[name]=funс.
    При этом источник должен получить своё имя, которое будет использоваться в качесвте индекса в __Soursers_data
    и в __named_functions. Пример имени - "Free-proxy".
    Тогда для инициации парсинга вы просто при запуске указываете "site"+'имя источника', и парсинг будет вестись с него.
    Парсинг идёт "тупо": дёргаем страницу по ссылке, через __named_functions[name] выделяем данные о прокси и
    добавляем их в 'self'.
    Возможно, на прокси с логином и паролем будет падать. Тогда надо переделать "req_obj.auth = (p_user, p_pass)"
    '''

    # Тут указаны браузеры, которые популярны
    # https://www.liveinternet.ru/stat/drom/browsers.html?period=month&per_page=20&ok=+OK+&report=browsers.html%3Fperiod%3Dmonth
    # http://www.useragentstring.com/pages/useragentstring.php Тут можно взять юзерагенты.
    # Это набор "браузеров", которыми мы будем представляться
    user_agent_list = [
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',

        # Firefox
        'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0',

        # Opera
        'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.14.1) Presto/2.12.388 Version/12.16',
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',
        'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
        'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
        'Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00',
        'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
        'Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00',
        'Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0',
        'Opera/9.80 (Windows NT 6.1; WOW64; U; pt) Presto/2.10.229 Version/11.62',
        'Opera/9.80 (Windows NT 6.0; U; pl) Presto/2.10.229 Version/11.62',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
        'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.9.168 Version/11.51',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; de) Opera 11.51'
    ]

    import sql_communication as sc  # Для работы с локальной базой

    import pandas as pd  # Для таблиц
    import numpy as np

    import requests  # Для выполнения запросов
    import random  # Для случайных задержек

    from bs4 import BeautifulSoup  # Для обработки страниц

    import time  # Для работы со временем
    import re  # Для чистки от лишних символов

    import threading  # Для многопоточности

    quiet_mod = False  # В тихом моде ли работать - без сообщений
    do_estimate = True  # Делать ли проверку прокси при работе

    __clean_exported_to_sql = True
    __sql_batch_size = 300  # Максимальное количество прокси, полученных из SQL, уходящих в обработку (больше не выгрузится)

    __start_time = False  # Время начала работы программы (для задержек парсинга)

    # Настройки для обращений
    defult_timeout = 4  # Секунд на таймаут запроса
    max_timeout = 21  # Таймаут после которого перестём пытаться. Должен быть В РАЗЫ больше defult_timeout

    ussepted_threads = 20  # Количество потоков, на которые можно параллелить

    unacceptable_number_of_tests = 9  # Количество неудачных попыток дозвона, после которого помечается как мёртвый
    # Переносится из Proxy_list в Dead_proxy. 1 прозвон делается по всему Links_list

    __Have_any_proxy = False  # Детектор того, что есть хоть 1 прокси в списке спарсенных
    __Have_My_proxy = False  # Прокси, через которые может ходить программа
    # должны быть БЕЗ авторизации

    # Лучше ставить "https://vk.com/", чтобы лишний раз не светить на нужном ресурсе
    Main_ping_link = "https://www.yandex.ru/"  # Основная ссылка - куда будем стучать

    # Набор ссылок, по которым будем проверять доступность прокси (топовые ресурсы Рунета)
    Links_list = ["https://vk.com/",
                  "https://mail.ru/",
                  "https://lenta.ru/",
                  "http://www.km.ru/",
                  "https://www.drom.ru/"]

    __protocols = ['HTTP', 'HTTPS', 'http', 'https']  # Разрешённые протоколы

    # Таблица сайтов - источников прокси. При изменении - поправить "add_sourse" функцию
    # Индекс - имя источника
    __Soursers_data = pd.DataFrame({'link': [],
                                    'delay': [],
                                    })
    __Soursers_data['link'] = __Soursers_data['link'].astype(str)  # ссылка
    __Soursers_data['delay'] = __Soursers_data['delay'].astype(int)  # Задержка в опрашивании

    __named_functions = {}  # Словарь с именными функциями. Индекс - имя источника
    '''
    Proxy_list - набор всех прокси, о которых есть инфа.
    Полное описание - смотри self.reset_proxy_lists()
    '''

    def __init__(self,
                 repetitions=False,  # Количество повторейний False=0
                 need_My_proxy=False,  # Нужны ли "свои прокси"?

                 Defult_ping_link=False,  # Основная ссылка
                 defult_timeout=False,  # Стандартный таймаут для запросов на сайты
                 max_timeout=False,  # Максимально допустимый таймаут для запросов на сайты

                 unacceptable_number_of_tests=False,  # Количество прозвонов, после которого прокси считается мёртвым

                 get_from='site',
                 get_condition='Free-proxy',

                 do_estimate=True,
                 ussepted_threads=True,
                 export_to_sql=True,
                 clean_exported_to_sql=True,  # Удалить ли экспортированные в SQL сервера

                 sql_batch_size=False,  # Сколько данных выгружать из SQL

                 quiet_mod=False,  # "Тихий режим" - без вывода инфы, кроме случаев, когда инфа должна быть введена
                 auto=True  # Автоматически запуститься и отработать.
                 ):
        '''
        :param need_My_proxy - надо ли использовать свой набор прокси. False - нет, или число - сколько.
        :param do_wokr - Если False, то будет выполнена только преднастройка
        :param get_from - откуда взять данные. Варианты:
                           1. 'SQL' - дёрнет с базы запросы с условием get_condition.
                           Условие вида 'WHERE ...'. Условие может быть ''
                           2. 'site' - Взять с сайта.
                              Условие - имя сайта, проверяется по в __Soursers_data. Если такой сайт не предусмотрен,
                              ничего не произойдёт.
                                  Дефлтно - 'Free-proxy'.
                           3. 'get_frame'- Команда - принять дата фрейм, отвечающий "Proxy_list".
                                 Скрипт проверит заполненность полей:
                                 'protocol','server_ip','server_port',
                                 'login','password'.
                                 'sourse' будет поставлен "script".
        :param do_estimate - Делать ли оценку доступности и пинга (t/f)
        :param export_to_sql - делать ли выгрузку в таблицу
        Добавить получение данных из программы при инициации.
        Чтобы можно было создать дохуя экземпляров, которые будут бегать и чекать SQL таблицу, получив
        какой-то сет данных из неё. Иначе обновление будет идти неделями!
         - для этого есть add_proxy. Надо только написать блок.
        Возможно, работу стоит разбить на три части:
        получить (настраивается отдельно)
        оценить (настраивается отдельно)
        экспортировать (настраивается отдельно)
        И если получаем из программы, то делаем только одно выполнение.
        Режим "парсинга" для добавления новых прокси ВЕСТИ ОТДЕЛЬНО!
        Т.к. проверка 300 прокси займёт около 5 часов. А парсить следовало бы почаще ;)
        Добавить себе на локал хост таблицу с проксями!
        СДЕЛАТЬ настройки запуска:
        1. Режим работы: спарсить с источника и занести в SQL (или куда указывает параметр экспорта)/
                         Взять с SQL, проверить, обновить даныне в SQL (или куда указывает параметр экспорта
            для каждого режима работы надо запустьть отдельный экземпляр класса.
            Для каждого конкретного источника надо тоже запустьть отдельный экземпляр класса.
        2. Количество выполнений:
        3. Куда экспортировать по ходу работы:
                    в sql
                    никуда  (имеет смысл только если repetitions=False, иначе не разрешать такой вариант и экспортить в SQL)
        4. Перенести в параметры всякие штуки типа выставление таймаутов и т.п.
        По дефолту выставить их "False".
        !! Добавить "корретировку таймаута". Типа если явно задан таймаут, то независимо от режима работы,
        он поставиться всем источникам. И будет использоваться в цикле работы с базой!
        Добавить параметр "нихуя не делать".
        :param repetitions: Количество повторений. По дефолту - ни одного
        '''

        self.__fill_sourses()  # Заполнили данные об источниках
        self.reset_Proxy_lists()  # Создадим таблицу с прокси
        self.reset_My_rpoxy()  # Создадим таблицу со "своими" прокси

        # ------------------------------------------------------------------------------------
        # Преднастроим параметры -------------------------------------------------------------

        if Defult_ping_link != False and type(Defult_ping_link) == str:
            self.Main_ping_link = Defult_ping_link
        if defult_timeout != False:
            self.defult_timeout = defult_timeout
        if max_timeout != False:
            self.max_timeout = max_timeout
        if unacceptable_number_of_tests != False:
            self.unacceptable_number_of_tests = unacceptable_number_of_tests
        if quiet_mod is True:
            self.quiet_mod = quiet_mod
        if sql_batch_size != False and type(sql_batch_size) == int:
            # Если указан размер выборки из SQL
            self.__sql_batch_size = sql_batch_size
        if do_estimate == False:
            self.do_estimate = do_estimate  # Делать ли оценку

        if not (repetitions is True) and repetitions != False:  # Если задан repetitions
            if type(repetitions) != int:  # И он не того формата
                repetitions = False
                self.communication(message='Ошибка - количество повторений не распознано. Повторений не будет.')

        if repetitions == False:  # Если повторений нет, то чистить не будем!
            self.__clean_exported_to_sql = False
        elif repetitions is True:  # Если повторяем бесконечно
            self.__clean_exported_to_sql = True  # ОБЯЗАТЕЛЬНО! ЧИСТИМ
        elif type(clean_exported_to_sql) == bool:  # Если t/f
            self.__clean_exported_to_sql = clean_exported_to_sql

        # Если надо использовать свои прокси и указано число или если не надо использовать свои прокси
        if (need_My_proxy != False and type(need_My_proxy) == int) or need_My_proxy == False:
            pass  # то всё ок
        else:  # Иначе, если число не целое или там какой-то мусор, ставим дефолтное 10
            need_My_proxy = 30

        self.communication(message='Преднастройка завершена')

        # Если делаем автоматически
        if auto is True:
            result = self.auto_work_mode(repetitions=repetitions,
                                         get_from=get_from, get_condition=get_condition,
                                         need_My_proxy=need_My_proxy,
                                         export_to_sql=export_to_sql,
                                         threads_count=ussepted_threads
                                         )
            self.communication(message='Работа выполнена, результат: ' + result)

    # ------------------------------------------------------------------------------------------------
    # Функции __init__-а -----------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # multi_threads
    def auto_work_mode(self, repetitions,
                       get_from, get_condition,
                       need_My_proxy,
                       export_to_sql,
                       threads_count=True
                       ):
        '''
        Автоматический мод. Взять с источника, выгрузить, проверить, передать в SQL
        :param repetitions:  - повторения
        :param get_from: - тип источника
        :param get_condition: - параметр для источника
        :param need_My_proxy: - использовать ли прокси
        :param export_to_sql: - выгружать ли в базу
        :return:
        '''
        while True:  # Для повторений (прерыватель в конце)

            this_moment = (str(self.time.localtime().tm_year) + '.' +
                           str(self.time.localtime().tm_mon) + '.' +
                           str(self.time.localtime().tm_mday) +
                           '  ' + str(self.time.localtime().tm_hour) + ':' + str(self.time.localtime().tm_min))

            self.communication(message=('\n' +
                                        '\n' + '============================================================' +
                                        '\n' + '============================================================'
                                        )
                               )
            self.communication(message='Начат цикл проработки ' + this_moment)

            # ------------------------------------------------------------------------------------
            # Получим список прокси --------------------------------------------------------------
            get_result = self.__get_data(get_from=get_from, get_condition=get_condition)

            if get_result == 'Успешно':  # Если всё ок
                self.communication(message='Список прокси получен')

            # Если брали с сайта, и ошибка в "источнике"
            elif get_from == 'site' and get_result == 'Ошибка - в списке источников нет указанного':  # Если нет такого источника
                return get_result

            # Если брали с сайта и ошибка не в источнике
            elif get_result != 'Успешно' and get_from == 'site':  # Если с сайта - попробуем ещё раз

                # Если мы используем прокси и список моих прокси не пуст, попробуем прозвонить весь список по очереди
                if need_My_proxy != False and self.__Have_My_proxy is True:

                    # Будем пытаться дозвониться через прокси пока они есть
                    while get_result != 'Успешно' and self.__Have_My_proxy is True:
                        # Важно, что при неудачной опытке дёрнуть страницу через сервер из My_proxy, он удаляется
                        # И, если это был последний сервер в списке, то "__Have_My_proxy" станет False автоматически

                        self.communication(message=('\nПовторная попытка через 30 секунд' +
                                                    '(время ' + str(self.time.localtime().tm_hour) + ':'
                                                    + str(self.time.localtime().tm_min) + ')'
                                                    ))
                        self.time.sleep(30)  # Ждём
                        get_result = self.__get_data(get_from=get_from, get_condition=get_condition)  # Пробуем ещё раз
                        if get_result == 'Успешно':  # Получение было успешным
                            self.communication(message='Список прокси получен')
                            break  # Закончим цикл "While".
                        else:
                            self.communication(message='Получить список прокси не удалось')

                    # Если не получили набор прокси и парсить больше не через что
                    if get_result != 'Успешно' and self.__Have_My_proxy == False:
                        # На этом проходе ничего дальше сделано не будет
                        self.communication(message='\nСписок собственных прокси опустошен. \nЗавершение круга')
                        # Без указания ошибки, т.к. она выводится в __get_data

                else:  # Если мы не используем прокси, а звоним со своего ip
                    self.communication(message=('Повторная попытка через 5 минут' +
                                                '(время ' + str(self.time.localtime().tm_hour) + ':'
                                                + str(self.time.localtime().tm_min) + ')'
                                                ))
                    self.time.sleep(300)  # Ждём 5 минут
                    get_result = self.__get_data(get_from=get_from, get_condition=get_condition)  # Пробуем ещё раз
                    if get_result == 'Успешно':  # Получение было успешным
                        self.communication(message='Список прокси получен')

                    else:  # Если была ошибка
                        self.communication(
                            message='Завершение круга')  # Без указания ошибки, т.к. она выводится в __get_data
                        # На этом проходе ничего дальше сделано не будет

            # Если брали не с сайта, и была получена ошибка, то пока завершим.
            else:
                self.communication(message='Результат: ' + get_result + '\nЗавершение круга')
                # На этом проходе ничего дальше сделано не будет

            # ------------------------------------------------------------------------------------
            # Если надо проверить прокси - проверим ----------------------------------------------
            # Если данные получены
            check_time = 0
            check_result = False  # Чтобы переменная существовала
            if self.do_estimate is True and get_result == 'Успешно':

                self.communication(message=('Начинаю проверку прокси на доступность в ' +
                                            str(self.time.localtime().tm_hour) + ':'
                                            + str(self.time.localtime().tm_min))
                                   )

                check_time = self.time.time()  # Засечём время

                # Если делаем в многопоточном режиме с дефолтной настройкой
                if threads_count is True:
                    # Берём self.ussepted_threads потоков
                    check_result = self.multi_threads_check_Proxy_list(threads_count=self.ussepted_threads)
                # Если указано количество потоков
                elif type(threads_count) == int:
                    check_result = self.multi_threads_check_Proxy_list(threads_count=threads_count)
                else:  # Если с многопоточностью не срослось
                    check_result = self.check_Proxy_list()  # Проверили прокси в однопоточном режиме

                check_time = round(self.time.time() - check_time)

                if check_result == 'Успешно':
                    self.communication(message=('Проверка прокси на доступность выполнена успешно' +
                                                '\nЗатрачено ' + str(round(check_time / 60)) + ' мин'))

                    if get_from == 'site' and need_My_proxy != False:  # Если при этом прокси тянем с сайта

                        if self.__Have_My_proxy:  # Если "мои" прокси есть
                            self.communication(message=('Выполняю проверку своих прокси (в один поток) '))
                            self.check_My_proxy()  # чекнем их

                        required_to_add = need_My_proxy - self.My_proxy.shape[
                            0]  # Определим, на сколько серверов надо пополнить
                        self.communication(
                            message=('Пытаюсь пополнить набор собственных прокси на ' + str(required_to_add) + ' штук'))

                        # Пополним
                        fill_my_pr_result = self.fill_My_proxy_from_self(N=required_to_add)
                        self.communication(
                            message=('Результат пополнения собственных прокси: ' + str(fill_my_pr_result)))



                else:  # Если по выполнению была ошибка
                    self.communication(message=('Проверка прокси на доступность выполнена с ошибкой' +
                                                '\n' + check_result +
                                                '\nЗатрачено ' + str(round(check_time / 60)) + ' мин')
                                       )

            # ------------------------------------------------------------------------------------
            # Экспортируем прокси, если требуется ------------------------------------------------
            # Если нужно экспортировать в таблицу и список прокси успешно получен и обновлён
            export_time = 0
            export_result = False  # Чтобы переменная существовала
            if export_to_sql is True and get_result == 'Успешно':
                # Условие check_result=='Успешно' - не обязательно!
                # Даже если проверка прокси завалилась или её вообще не было, то экспорт всё равно будет
                self.communication(message='Начинаю экспорт данных о серверах в базу')

                export_time = self.time.time()  # Засечём время
                export_result = self.expotr_to_sql(clean_exported=True)  # Экспортируем
                export_time = round(self.time.time() - export_time)  # Получим затраченное на экспорт время

                self.communication(message=('Выполнен экспорт в базу: ' + export_result +
                                            '\nЗатрачено ' + str(round(export_time)) + ' сек')
                                   )

            # ------------------------------------------------------------------------------------
            # Задержка ---------------------------------------------------------------------------
            # хе-хе... У цикла задержка )
            if repetitions != False:  # Если повторений будет несколько

                if get_result == 'Успешно':  # Если данные были получены

                    if get_from == 'site':  # Если тянем с сайта, возьмём его задержку
                        to_sleep = self.__Soursers_data.at[get_condition, 'delay'] * 60
                        # get_condition - имя сайта и инедекс в таблице. delay в минутах, поэтому умножаем на 60

                    else:  # Если не с сайта, то берём дефолтную
                        to_sleep = 900  # По дефолту ожидаем 15 минут

                else:  # Если при получении данных была ошибка
                    to_sleep = 300  # ожидаем 5 минут

                # Добавим "случайную погрешность"
                to_sleep += self.random.randrange(-200, 200)

                # Вычтем время на проверку и экспорт
                to_sleep = to_sleep - export_time - check_time
                if to_sleep < 0:  # Если время "вышло"
                    to_sleep = 0
                # Поспим

                if get_from == 'SQL':  # Если обновляем таблицы
                    if get_result == 'Успешно':  # И выгрузка была успешной можно не спать
                        self.communication(message=('Цикл закончен. '
                                                    '(время ' + str(self.time.localtime().tm_hour) + ':' +
                                                    str(self.time.localtime().tm_min) + ')'
                                                    )
                                           )
                    else:  # Если выгрузка была не успешной
                        self.communication(message=('Цикл закончен. Перехожу в жидание на ' + str(15) + ' мин ' +
                                                    '(время ' + str(self.time.localtime().tm_hour) + ':' +
                                                    str(self.time.localtime().tm_min) + ':' +
                                                    str(self.time.localtime().tm_sec) + ')'
                                                    )
                                           )
                        self.time.sleep(900)
                else:
                    self.communication(message=('Цикл закончен. Перехожу в жидание на ' + str(to_sleep) + ' cек ' +
                                                '(время ' + str(self.time.localtime().tm_hour) + ':' +
                                                str(self.time.localtime().tm_min) + ':' +
                                                str(self.time.localtime().tm_sec) + ')'
                                                )
                                       )
                    self.time.sleep(to_sleep)

            # ------------------------------------------------------------------------------------
            # Прерыватель повторений -------------------------------------------------------------

            # Сдвинем счётчик, если надо
            if not (repetitions is True) and type(
                    repetitions) == int:  # Если не надо крутиться бесконечно, а по счётчику
                repetitions -= 1  # Снимем единичку
                if repetitions == 0:  # Если счётчик дошёл до нуля
                    self.communication(message='\nРабота закончена.')
                    break  # Закончим повторения вайла
            elif repetitions == False:  # Если повторений вообще не надо
                self.communication(message='\nРабота закончена.')
                break  # Закончим повторения вайла

            self.communication(message='\n \n \n')

        return 'Успешно'

    # Функция получения данных из указанного источника.
    def __get_data(self, get_from, get_condition):
        '''
        :param get_from: - откуда брать
        :param get_condition - доп условие.
        :return: "успешно" если данные получены, или "Ошибка ...", в противном случае
        '''

        if type(get_from) != str:
            self.communication(message='Неверная настройка параметра "get_from"')
            return 'Ошибка - неверный тип get_from'

        # Пошли по видам источников
        # Готово - отлажено
        if get_from == 'site':  # -----------------------------------------------------------  Если получаем c сайта
            sourse_name = get_condition  # Запомним имя источника
            # Проверим, что такой источник есть
            if not (sourse_name in self.__Soursers_data.index.tolist()):
                # Если такого источника нет
                return 'Ошибка - в списке источников нет указанного'

            # Если такой источник есть - дёрнем данные со страницы и занесём в self
            result = self.__get_pr_and_fill_list(sourse_name=sourse_name,  # Берём для источника
                                                 named_update_function=self.__named_functions[sourse_name],
                                                 # Укажем функцию получения прокси со страницы
                                                 with_user_agent=True  # Используем случайный юзерагент
                                                 )

            self.communication(message=('Получение данных из ' + str(sourse_name) + ': ' + result))

            self.__start_time = self.time.time()  # Засечём время окончания парсинга сайта, для верной задержки при парсинге

            return result  # Вернём результат операции ("Успешно" или "Ошибка...")



        elif get_from == 'SQL':  # -------------------------------------------------------  Если получаем из таблицы
            # get_condition - условие "WHERE ..."
            result = self.import_from_sql(where=get_condition)
            self.communication(message=('Получение данных из ' + str(get_from) + ': ' + result))
            return result


        elif get_from == 'get_frame':  # ------------------------------------------- Если нам передаётся набор прокси
            Frame = get_condition  # Возьмём объект

            from pandas import DataFrame
            if type(Frame) != DataFrame:  # Если объект - не фрейм,
                self.communication(
                    message=('Получение данных из ' + str(get_from) + ': ' + 'Ошибка - объект не DataFrame'))
                return 'Ошибка - объект не DataFrame'

            headers_list = ['protocol', 'server_ip', 'server_port', 'login',
                            'password']  # Укажем список обязательных заголовков
            Frame_list = list(Frame)  # Заголовки фрейма (Чтобы не формировать каждый раз)

            # Проверим, что нужные столбцы есть
            for el in headers_list:  # Пошли по нужным заголовкам
                if not (el in Frame_list):  # Если нужного заголовка нет
                    self.communication(
                        message=('Получение данных из ' + str(get_from) + ': ' + 'Ошибка - отсутсвуют нужные столбцы'))
                    return 'Ошибка - отсутсвуют нужные столбцы'

            # Если есть все нужные столбцы, оставим только их
            Frame = Frame[headers_list].copy(deep=True)
            # Скинем столбцы, где нет критически важных данных
            Frame.dropna(subset=['protocol'], inplace=True)
            Frame.dropna(subset=['server_ip'], inplace=True)
            Frame.dropna(subset=['server_port'], inplace=True)
            # Заменим пустые логины и пароли на ''
            Frame['login'].replace(self.np.nan, '', inplace=True)
            Frame['password'].replace(self.np.nan, '', inplace=True)

            # Добавим прокси через self.add_proxy
            for el_id in Frame.index.tolist():  # Пошли по новому набору

                # Кроме строк, где есть или логин, или пароль (один есть, второго нет)
                if Frame.loc[el_id, 'login'] == '' or Frame.loc[el_id, 'password'] == '':  # Если кто-то пуст,
                    if Frame.loc[el_id, 'login'] != Frame.loc[el_id, 'password']:  # Но не оба
                        continue  # Скипаем

                add_result = self.add_proxy(protocol=Frame.loc[el_id, 'protocol'],
                                            server_ip=Frame.loc[el_id, 'server_ip'],
                                            server_port=Frame.loc[el_id, 'server_port'],
                                            sourse='script',
                                            login=Frame.loc[el_id, 'login'],
                                            password=Frame.loc[el_id, 'password'],
                                            )

            self.communication(message=('Получение данных из ' + str(get_from) + ': ' + 'Успешно'))
            return 'Успешно'

        else:
            self.communication(
                message=('Получение данных из ' + str(get_from) + ': ' + '\nОшибка - нет такого источника'))
            return 'Ошибка - нет такого источника'

    # ------------------------------------------------------------------------------------------------
    # Для общения с внешней средой -------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Для общения с внешней средой - готово, отлажено
    def communication(self, message,
                      retrieve=False,
                      mode='tf',
                      quiet_mod=quiet_mod
                      ):
        '''
        Функция для общения с внешним миром
        :param message: - сообщение для вывода
        :param retrieve: - вернуть ли что-либо. Если не False, то переменная будет содержать возвращаемую инфу.
        :param mode: - режим, помогающий избежать части ошибок ввода
        :return: - по настройке retrieve.
        #'''

        # Если тихий мод и не надо что-либо считывать, молчим
        if quiet_mod is True and retrieve is False:
            return

        if retrieve == False:  # Если надо только написать сообщение
            print(message)

        else:  # Если хотим что-то в обратку

            print(message)  # напишем фразу юзеру

            a = 0
            while a == 0:

                if mode == 'tf':  # да нет
                    a_in = input('    да/нет (Enter - да) ')
                    if (a_in == '') or (a_in == 'да') or (a_in == 'lf'):
                        print('    --- Принято "да"')
                        return True
                    elif (a_in == 'ytn') or (a_in == 'нет'):
                        print('--- Принято "нет"')
                        return False

                    else:
                        print('--- Ошибка ввода, повторите')


                elif mode == 'N':  # Ввод числа
                    a_in = input('')
                    if (a_in == ''):  # если ввод пустой - вернём ноль
                        print('--- Принято "0"')
                        return 0
                    elif a_in.isdigit() == True:  # если введено число
                        print('--- Принято')
                        return int(a_in)  # вернём это число
                    else:
                        print('--- Ошибка ввода, повторите')

                elif mode == 'str':  # Ввод строки
                    a_in = input('')
                    if (a_in == ''):  # если ввод пустой - вернём ноль
                        print('--- Принято "False" ')
                        return False
                    else:
                        return a_in  # вернули строку

            return  # Досюда точно не дойдёт

    # ------------------------------------------------------------------------------------------------
    # Функции создания и наполнения self.Proxy_list --------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Обновление My_rpoxy  - готово, отлажено
    def reset_My_rpoxy(self):
        My_proxy = self.pd.DataFrame({'protocol': [],
                                      'server_ip': [],
                                      'server_port': [],
                                      'user': [],  # Если нет - сделать пустым ''
                                      'pass': [],  # Если нет - сделать пустым ''
                                      'timeout': []
                                      })

        My_proxy['protocol'] = My_proxy['protocol'].astype(str)
        My_proxy['server_ip'] = My_proxy['server_ip'].astype(str)
        My_proxy['server_port'] = My_proxy['server_port'].astype(str)
        My_proxy['user'] = My_proxy['user'].astype(str)
        My_proxy['pass'] = My_proxy['pass'].astype(str)
        My_proxy['timeout'] = My_proxy['timeout'].astype(int)

        self.My_proxy = My_proxy
        self.__Have_My_proxy = False

        return

    # Функция для сброса списков всех имеющихся и доступных прокси  - готово, отлажено
    def reset_Proxy_lists(self):

        # Набор всех прокси серверов
        all_proxy = self.pd.DataFrame({'protocol': [],
                                       'server_ip': [],
                                       'server_port': [],

                                       'login': [],
                                       'password': [],

                                       'sourse': [],

                                       'checked': [],
                                       'is_available': [],
                                       'timeout': [],

                                       'unsuccessful_calls': [],
                                       'country': [],
                                       'comment': [],
                                       })

        all_proxy['protocol'] = all_proxy['protocol'].astype(str)
        all_proxy['server_ip'] = all_proxy['server_ip'].astype(str)
        all_proxy['server_port'] = all_proxy['server_port'].astype(str)

        all_proxy['login'] = all_proxy['login'].astype(str)
        all_proxy['password'] = all_proxy['password'].astype(str)

        all_proxy['sourse'] = all_proxy['sourse'].astype(str)  # Имя источника

        all_proxy['checked'] = all_proxy['checked'].astype(bool)  # Проверен ли прокси
        all_proxy['is_available'] = all_proxy['is_available'].astype(bool)  # Доступен ли
        all_proxy['timeout'] = all_proxy['timeout'].astype(int)  # Таймаут

        all_proxy['unsuccessful_calls'] = all_proxy['unsuccessful_calls'].astype(int)  # Количество попыток дозвона
        all_proxy['country'] = all_proxy['country'].astype(str)

        all_proxy['comment'] = all_proxy['comment'].astype(str)  # Коммент

        self.Proxy_list = all_proxy  # Забрали в self

        self.Dead_proxy = all_proxy  # Мёртвые прокси

        self.__Have_any_proxy = False  # Запомним, что у нас нет прокси

        return

    # Добавить прокси в self.Proxy_list Вернёт t- успешно, или вид ошибки  - готово, отлажено
    def add_proxy(self,
                  protocol,
                  server_ip,
                  server_port,
                  sourse,
                  login='',
                  password='',

                  checked=False,
                  is_available=False,
                  timeout=defult_timeout,
                  calls=0,
                  country='',
                  comment=''
                  ):

        if type(protocol) != str:  # Если протокол не строка
            return 'Ошибка - неверный протокол'

        protocol = protocol.lower()
        if not (protocol in self.__protocols):  # Если протокол не разрешён
            return 'Ошибка - неразрешённый протокол'
        # Проверим нет ли уже прокси с таким ip
        if (self.Proxy_list.loc[self.Proxy_list['server_ip'] == server_ip]).shape[0] != 0:
            return 'Ошибка - ip уже есть'

        try:
            new_id = max(self.Proxy_list.index.tolist()) + 1  # Получим id
        except ValueError:  # Если список пустой
            new_id = 0

        self.Proxy_list.at[new_id, 'protocol'] = protocol
        self.Proxy_list.at[new_id, 'server_ip'] = server_ip
        self.Proxy_list.at[new_id, 'server_port'] = str(server_port)  # м.б. строка или число
        self.Proxy_list.at[new_id, 'sourse'] = sourse

        self.Proxy_list.at[new_id, 'login'] = login
        self.Proxy_list.at[new_id, 'password'] = password

        if isinstance(checked, bool):
            self.Proxy_list.at[new_id, 'checked'] = checked
        else:
            self.Proxy_list.at[new_id, 'checked'] = False

        self.Proxy_list.at[new_id, 'is_available'] = is_available
        self.Proxy_list.at[new_id, 'timeout'] = timeout
        self.Proxy_list.at[new_id, 'unsuccessful_calls'] = calls

        self.Proxy_list.at[new_id, 'country'] = self.phrase_clear(phrase=country)
        self.Proxy_list.at[new_id, 'comment'] = self.phrase_clear(phrase=comment)

        return True

    # Чистка фразы от лищних символов
    def phrase_clear(self, phrase):
        phrase = self.re.sub(r'[^\w\s]', '', phrase)  # Зачистим лишние знаки
        phrase = (phrase.replace('  ', ' ')).replace('  ', ' ')  # Заменим двойные пробелы
        phrase = phrase.lower()  # сведём к нижнему регистру

        return phrase

    # ------------------------------------------------------------------------------------------------
    # Указание сайтов для получения данных -----------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Функция для заполнения набора источников - готово, отлажено
    def __fill_sourses(self):
        # Добавитли источник
        self.add_sourse(name='Free-proxy',
                        link='https://free-proxy-list.net/',
                        named_function=self.__get_Free_proxy,  # Именная функция
                        delay=11  # Их список обновляетс якаждые 10 минут.
                        )

        # Добавить получение от тимура

        return

    # Функция добавления источника прокси - готово, отлажено
    def add_sourse(self, name, link, named_function, delay):
        '''
        :param name: - имя
        :param link: - сылка - источник прокси
        :param delay: - задержка в минутах для обновления списка прокси
        :return: Статус выполнения "Успешно" или "Ошибка..."
        '''
        if type(name) != str and type(link) != str and type(delay) != int:
            return 'Ошибка - несовпадение типов'

        # Пинганём сервер. Если он не доступен, дадим ошибку.
        # Возможно, прям тут попробуем проверить - есть ли там прокси?
        self.__Soursers_data.at[name, 'link'] = link
        self.__Soursers_data.at[name, 'delay'] = delay

        self.__named_functions[name] = named_function  # Запомнили именную функцию

        return 'Успешно'

    # ------------------------------------------------------------------------------------------------
    # Парсинг прокси со страниц конкретных сайтов - именные функции (named_update_functions) ---------
    # ------------------------------------------------------------------------------------------------

    # Функция "взять и занести в селф"  - готово, отлажено.
    def __get_pr_and_fill_list(self,
                               sourse_name,
                               named_update_function,
                               with_user_agent=True
                               ):
        '''
        Дёргает данные о прокси со страницы сервиса. Заносит прокси в self именной функцией.
        Выполняется разово
        :param sourse_name: - имя источника из __Soursers_data
        :param named_update_function: - именная функция, которая получает данные со страницы источника
        :param repetitions: количество повторений (t-бесконечно,f-ни разу, N(int) - N раз)
        :return: ничего. Добавляет данные в таблицу
        '''

        # Проверим - есть ли доступные прокси:
        if self.__Have_My_proxy is True:  # Если есть
            proxy_index = self.random.choice(self.My_proxy.index.tolist())  # Выберем случайный доступный прокси
            proxy_type = self.My_proxy.loc[proxy_index, 'protocol']
            adress_and_port = self.My_proxy.loc[proxy_index, 'server_ip'] + ':' + self.My_proxy.loc[
                proxy_index, 'server_port']
            timeout = self.My_proxy.loc[proxy_index, 'timeout']

            # Если есть авторизация
            if self.My_proxy.loc[proxy_index, 'user'] != '' and self.My_proxy.loc[proxy_index, 'pass'] != '':
                p_user = self.My_proxy.loc[proxy_index, 'user']
                p_pass = self.My_proxy.loc[proxy_index, 'pass']
            else:  # Если авторизации нет
                p_user = False
                p_pass = False

        else:  # Если нет
            proxy_type = False
            adress_and_port = False
            p_user = False
            p_pass = False
            timeout = self.defult_timeout

        # Дёрнем страницу:
        result = self.__get_page_data(url=self.__Soursers_data.loc[sourse_name, 'link'],
                                      proxy_type=proxy_type,
                                      adress_and_port=adress_and_port,
                                      with_user_agent=with_user_agent,
                                      p_user=p_user,
                                      p_pass=p_pass,
                                      proxy_timeout=timeout
                                      )
        # Проверим успешность
        if type(result) == str:
            return ('Ошибка - ' + result)  # Если ошибка - вернём её

        else:  # Если всё путём
            # Передадим текст страницы в именную функцию
            named_update_function(Page_text=result[0].content)  # Она всё сделает

            return 'Успешно'  # Закончили

    # Для Free-proxy. Вернёт "Успешно", если все прокси взяты, или bad_proxy - набор невзятых прокси - готово, отлажено
    def __get_Free_proxy(self, Page_text):
        '''
        Для фри прокси из страницы забираются прокси. Потом они добавляются в общий набор.
        :param Page_text: Текст со страницы
        :return: ничего. Добавляет данные в таблицу
        '''

        # Набор новых "плохих" прокси серверов
        bad_proxy = self.pd.DataFrame({'protocol': [],
                                       'server_ip': [],
                                       'server_port': [],
                                       'sourse': [],
                                       'country': [],
                                       'comment': []
                                       })
        bad_proxy['protocol'] = bad_proxy['protocol'].astype(str)
        bad_proxy['server_ip'] = bad_proxy['server_ip'].astype(str)
        bad_proxy['server_port'] = bad_proxy['server_port'].astype(str)

        bad_proxy['sourse'] = bad_proxy['sourse'].astype(str)  # Имя источника
        bad_proxy['country'] = bad_proxy['country'].astype(str)
        bad_proxy['comment'] = bad_proxy['comment'].astype(str)

        content = self.BeautifulSoup(Page_text, "html.parser")  # Получиv html разметку

        tables = content.findAll(name={'tbody': True})  # Вытащит даныне по тегy tbody

        pr_table_strings = tables[0].findAll(name={'tr': True})  # Взяли таблицу проксей и разбили по строкам

        for string in pr_table_strings:  # Пошли по строкам

            string_elements = string.findAll(name={'td': True})  # разобьём строку по элементам

            # Далее отправим данные из строки в список прокси

            # Получим тип прокси
            pr_type = string_elements[6].get_text()
            if pr_type == 'yes':
                protocol = 'https'
            elif pr_type == 'no':
                protocol = 'http'

            # Добавим прокси в self.Proxy_list
            result = self.add_proxy(protocol=protocol,
                                    server_ip=string_elements[0].get_text(),  # Получим ip
                                    server_port=string_elements[1].get_text(),  # Получим порт
                                    sourse="Free-proxy",
                                    country=string_elements[3].get_text()  # Взяли страну
                                    )
            if not (result is True):  # Если не успешно
                bad_id = bad_proxy.shape[0]
                bad_proxy['protocol'] = protocol
                bad_proxy['server_ip'] = string_elements[0].get_text()
                bad_proxy['server_port'] = string_elements[1].get_text()

                bad_proxy['sourse'] = "Free-proxy"
                bad_proxy['country'] = string_elements[3].get_text()
                bad_proxy['comment'] = result  # Запомним причину отказа

        # Если в наборе есть хоть один прокси
        if self.Proxy_list.shape[0] > 0:
            self.__Have_any_proxy = True
        else:  # Если там ни одного прокси
            self.__Have_any_proxy = False

        if bad_proxy.shape[0] > 0:  # Если есть хоть один плохой прокси
            return bad_proxy

        return 'Успешно'

    # ------------------------------------------------------------------------------------------------
    # Получить данные страницы -----------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Получить данные страницы (просто парсит страницу и отдаёт response или строку с ошибкой). - готово, отлажено.
    def __get_page_data(self, url,
                        proxy_type=False,
                        adress_and_port=False,
                        proxy_timeout=defult_timeout,
                        p_user=False,
                        p_pass=False,

                        number_of_attempts=1,
                        max_attempts=3,
                        delay=15,
                        with_user_agent=True,
                        my_number=1):
        '''
        :param url: урл для обращения
        :param proxy_type: тип прокси http или  https
        :param adress_and_port: адрес и порт вида - "192.168.0.1:8090"
        :param proxy_timeout: таймаут для прокси
        :param p_user: пользователь
        :param p_pass: пароль
        :param number_of_attempts: какой по счёту будет эта попытка обращения
        :param max_attempts: максимальное количество обращений
        :param delay: задержка в секундах!
        :param with_user_agent: Использовать ли юзер агент?
        :param my_number: - уровень "глубины" функции. При вызове себя же он увеличивается на 1.
        :return: 'Ошибка - превышено количество попыток' - не смогли дёрнуть
                 "Ошибка - не удалось соединиться" - если при последней попытке подключения была ConnectionError
                  [response,with_proxy] - если успешно. response - результат запроса!
                                          with_proxy - использовался ли прокси
        Можно добавить всякий кастом пользователя типа юзер агента и т.п.
        '''

        # Рассчитаем время сна
        sec_to_sleep = (self.random.randint(delay - round(delay / 2), delay + round(delay / 2)))

        # Создадим объект для запросов
        req_obj = self.requests.Session()

        # Если есть прокси
        if proxy_type in self.__protocols and type(adress_and_port) == str:
            self.communication(message=('Парсинг источника ведётся через прокси: ' +
                                        str(proxy_type) + ' ' + str(adress_and_port) +
                                        ' попытка ' + str(my_number))
                               )
            req_obj.proxies = {proxy_type: adress_and_port}  # Дадим в настройку объекта прокси
        else:
            self.communication(message=('Парсинг источника ведётся без использования прокси, со своего ip'))

        # Если надо пользователя и пароль
        if p_user != False and p_pass != False and type(p_user) == str and type(p_pass) == str:
            req_obj.auth = (p_user, p_pass)

        # Если нужен юзер-агент
        if with_user_agent:
            user_agent = {'User-agent': self.random.choice(self.user_agent_list)}  # Возьмём случайный из списка

        # Прозвоним
        try:
            # без юзер агента
            if with_user_agent == False:
                response = req_obj.get(url, timeout=proxy_timeout)

            # с агентом
            elif with_user_agent is True:
                response = req_obj.get(url, headers=user_agent, timeout=proxy_timeout)

            # Если выполнение было неудачным
            if response.status_code != 200:
                log = "Код ответа: " + str(response.status_code)

                # Если это была последняя попытка
                if number_of_attempts >= max_attempts:
                    return log  # Вернём ошибку

                # Если ещё можно попытаться
                self.time.sleep(sec_to_sleep)

                # Ещё одна попытка
                result = self.__get_page_data(url=url,
                                              proxy_type=proxy_type,
                                              adress_and_port=adress_and_port,
                                              number_of_attempts=number_of_attempts + 1,
                                              max_attempts=max_attempts,
                                              delay=delay,
                                              with_user_agent=with_user_agent,
                                              my_number=my_number + 1
                                              )

                if type(result) == str and my_number == 1:  # Если после всех попыток результат - сообщение об ошибке
                    # Удалим этот прокси из self.My_proxy
                    ip_addres = (adress_and_port.split(':')[0])
                    self.My_proxy = self.My_proxy.loc[self.My_proxy['server_ip'] != ip_addres]
                    self.My_proxy.reset_index(drop=True, inplace=True)  # Скинем индекс, чтобы не было проблем
                    if self.My_proxy.shape[0] == 0:  # Если серверов больше нет
                        self.__Have_My_proxy = False
                    self.communication(message=('Прокси сервер удалён из набора для парсинга.'))

                # Вернём результат
                return result

            else:  # Если выполнение было удачным
                return [response]

        except BaseException as e:
            log = str(e)

            # Если это была последняя попытка
            if number_of_attempts >= max_attempts:
                return log  # Вернём ошибку

            # Если ещё можно попытаться
            self.time.sleep(sec_to_sleep)

            # Ещё одна попытка
            result = self.__get_page_data(url=url,
                                          proxy_type=proxy_type,
                                          adress_and_port=adress_and_port,
                                          number_of_attempts=number_of_attempts + 1,
                                          max_attempts=max_attempts,
                                          delay=delay,
                                          with_user_agent=with_user_agent,
                                          my_number=my_number + 1
                                          )

            if type(result) == str and my_number == 1:  # Если после всех попыток результат - сообщение об ошибке
                # Удалим этот прокси из self.My_proxy
                ip_addres = (adress_and_port.split(':')[0])
                self.My_proxy = self.My_proxy.loc[self.My_proxy['server_ip'] != ip_addres]
                self.My_proxy.reset_index(drop=True, inplace=True)  # Скинем индекс, чтобы не было проблем
                if self.My_proxy.shape[0] == 0:  # Если серверов больше нет
                    self.__Have_My_proxy = False

                self.communication(message=('Прокси сервер удалён из набора для парсинга.'))

            # Вернём результат
            return result

    # ------------------------------------------------------------------------------------------------
    # SQL - выгрузка/отгрузка ------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # Взять из базы
    def import_from_sql(self, where):
        '''
        Важно, что из подгруженных строк будет оставлено не более self.__sql_batch_size .
        :param where: - условие для выбора прокси-серверов из таблицы
        :return: "Успешно" или "Ошибка".
        '''

        # Проверим условие
        if type(where) != str:
            self.communication(message='Ошибка - Условие неверного формата. Выгрузка отменена.')
            return 'Ошибка - условие не строка'

        # Законектимся к базе
        sql_comm = self.sc.MY_base()  # подгрузим объект для коммуникации
        proxy_table = self.sc.My_base_tables.proxy_table

        # Если нет "служебного слова", но условие не пустое

        if where.find('WHERE') == -1 and where.find('where') == -1 and where != '':
            where = ' WHERE ' + where  # Добавим служебное слово
        where = ' ' + where

        # Првоерим, что для выгрузки есть хоть один запрос
        check_req = ('SELECT COUNT(*)' +
                     ' FROM ' + proxy_table.loc['таблица'][0] +
                     where)
        check_result = sql_comm.get_one(requests=[check_req])[0]
        # Если для выгрузки 0 запросов
        if check_result == 0:
            self.communication(message='Ошибка - Нет данных для выгрузки. Выгрузка отменена.')
            return 'Ошибка - Нет данных для выгрузки'

        # Сформируем запрос на получение данных
        base_req = ('SELECT ' +
                    proxy_table.loc['протокол'][0] + ',' +
                    proxy_table.loc['ip'][0] + ',' +
                    proxy_table.loc['port'][0] + ',' +

                    proxy_table.loc['логин'][0] + ',' +
                    proxy_table.loc['пароль'][0] + ',' +

                    proxy_table.loc['источник'][0] + ',' +

                    proxy_table.loc['доступен'][0] + ',' +
                    proxy_table.loc['таймаут'][0] +
                    ' FROM ' + proxy_table.loc['таблица'][0] +
                    where +
                    ' ORDER BY ' + proxy_table.loc['таймаут'][0]  # С группировкой по таймауту
                    )
        # Получим данные
        result = sql_comm.get_set(requests=base_req)[0]  # [0],т.к. запрос один
        new_data = self.pd.DataFrame(result, columns=['protocol',
                                                      'server_ip', 'server_port',
                                                      'login', 'password',
                                                      'sourse',
                                                      'is_available', 'timeout'])

        # Скинем "лишние" данные, чтобы проверка не была вечной.
        new_data = new_data.loc[new_data.index < self.__sql_batch_size]  # Оставим self.__sql_batch_size строк

        # Добавим прокси через self.add_proxy
        for el_id in new_data.index.tolist():  # Пошли по новому набору
            add_result = self.add_proxy(protocol=new_data.loc[el_id, 'protocol'],
                                        server_ip=new_data.loc[el_id, 'server_ip'],
                                        server_port=new_data.loc[el_id, 'server_port'],

                                        sourse=new_data.loc[el_id, 'sourse'],

                                        login=new_data.loc[el_id, 'login'],
                                        password=new_data.loc[el_id, 'password'],

                                        is_available=new_data.loc[el_id, 'is_available'],
                                        timeout=new_data.loc[el_id, 'timeout']
                                        )

        # Отконектимся от базы
        sql_comm.connection(act='close')

        return 'Успешно'

    # Выгрузить в базу
    def expotr_to_sql(self,
                      sourse_name="all",
                      checked=True,
                      clean_exported=__clean_exported_to_sql):
        '''
        Функция экспортирует и зачищает при необходимости список прокси
        :param sourse_name - источник, для которого экспортируем.
        :param checked - выгружать только проверенные прокси? True-да, False - все
        :param clean_exported - зачистить ли экспортированные данные?
        :return "Успешно", если всё ок.
        '''

        if sourse_name == 'all':
            export_frame = self.Proxy_list.copy(deep=True)
        else:
            export_frame = self.Proxy_list[self.Proxy_list['sourse'] == sourse_name].copy(deep=True)

        if checked is True:  # Если выгрузить только проверенные прокси
            export_frame = export_frame.loc[export_frame['checked'] == True]

        # Проверим - есть ли вообще что экспортировать?
        if export_frame.shape[0] == 0:  # Если нечего
            return 'Нет запросов на экспорт'

        index_list = export_frame.index.tolist()
        del export_frame  # Для экономии памяти

        # Законектимся к базе
        sql_comm = self.sc.MY_base()  # подгрузим объект для коммуникации
        proxy_table = self.sc.My_base_tables.proxy_table

        requests_list = []  # Создадим список запросов на апдейт
        # Заведём счётчики для месседжа
        new_servers = 0  # Добавлено серверов
        updated_servers = 0  # Обновлено серверов
        for el_id in index_list:  # Пошли по набору имеющихся прокси

            req_act = False  # Указывает, как составить запрос. False - ничего не делать
            '''
            'insert_done' - вставить обработанный запрос
            'insert_not_done' - вставить необработанный запрос
            'update' - обновить существующий запрос
            '''
            # Если запрос выгрузили из таблицы
            if self.Proxy_list.loc[el_id, 'checked'] == 'SQL':
                if self.Proxy_list.loc[el_id, 'checked'] is True:  # Если мы обновили сервер
                    req_act = 'update'  # То обновим данные в таблице

                else:  # Если сервер был из таблицы, и мы его не обновили
                    continue  # Скипаем

            elif self.Proxy_list.loc[el_id, 'checked'] != 'SQL':  # Если сервер новый
                # Провеерим - нет ли его уже в таблице
                request_ex = ('SELECT EXISTS( SELECT ' + proxy_table.loc['ip'][0] +
                              ' FROM ' + proxy_table.loc['таблица'][0] +
                              ' WHERE ' + proxy_table.loc['ip'][0] + ' = ' + "'" + self.Proxy_list.loc[
                                  el_id, 'server_ip'] + "'" +
                              ' ) '
                              )
                exist = sql_comm.get_one(requests=request_ex)[0]  # Получили t/f - есть ли уже запись с таким ip

                if exist is True:  # Если сервер уже есть в таблице
                    if self.Proxy_list.loc[el_id, 'checked'] is True:  # Если мы обновили сервер
                        req_act = 'update'  # То обновим данные в таблице
                    else:  # Если сервер был из таблицы, и мы его не обновили
                        continue  # Скипаем

                else:  # Если сервера в таблице не было
                    if self.Proxy_list.loc[el_id, 'checked'] is True:  # Если сервер новый и обновлён
                        req_act = 'insert_done'
                    else:  # Если сервер не обновлён
                        req_act = 'insert_not_done'

            # К этому моменту мы точно знаем, Какого типа запрос надо послать (знаем req_act)
            if req_act == False:  # Если никакой запрос не надо
                continue

            # Иначе - выберем вариант:
            if req_act == 'update':  # Если надо обновить существующий запрос.

                # Неудачные обращения
                if self.Proxy_list.loc[el_id, 'is_available']:  # Если сервер доступен
                    unsuccessful_calls = '0'  # Всё ок
                else:  # Если сервер есть в таблице и при проверке он был недоступен
                    unsuccessful_calls = proxy_table.loc['неудачные обращения'][0] + '+1'  # +1

                request = ('UPDATE ' + proxy_table.loc['таблица'][0] +
                           ' SET ' +
                           proxy_table.loc['таймаут'][0] + ' = ' + str(self.Proxy_list.loc[el_id, 'timeout']) + ',' +
                           proxy_table.loc['доступен'][0] + ' = ' + str(
                            self.Proxy_list.loc[el_id, 'is_available']) + ',' +
                           proxy_table.loc['неудачные обращения'][0] + ' = ' + unsuccessful_calls + ',' +
                           proxy_table.loc['дата обращения'][0] + ' = ' + 'now()::date' +  # Сегодня
                           ' WHERE ' + proxy_table.loc['ip'][0] + ' = ' + "'" + self.Proxy_list.loc[
                               el_id, 'server_ip'] + "'"
                           )
                requests_list.append(request)  # Добавили запрос в список запросов
                updated_servers += 1

            elif req_act == 'insert_done':  # Если надо вставить новый проверенный запрос
                # Неудачные обращения
                if self.Proxy_list.loc[el_id, 'is_available']:  # Если сервер доступен
                    unsuccessful_calls = '0'  # Всё ок
                else:  # Если сервер есть в таблице и при проверке он был недоступен
                    unsuccessful_calls = '1'  # +1

                request = ('INSERT INTO ' + proxy_table.loc['таблица'][0] +
                           " ( " +
                           proxy_table.loc['ip'][0] + ',' +
                           proxy_table.loc['port'][0] + ',' +
                           proxy_table.loc['протокол'][0] + ',' +

                           proxy_table.loc['логин'][0] + ',' +
                           proxy_table.loc['пароль'][0] + ',' +

                           proxy_table.loc['таймаут'][0] + ',' +
                           proxy_table.loc['источник'][0] + ',' +
                           proxy_table.loc['доступен'][0] + ',' +

                           proxy_table.loc['неудачные обращения'][0] + ',' +
                           proxy_table.loc['дата обращения'][0] + ',' +

                           proxy_table.loc['страна'][0] + ',' +

                           proxy_table.loc['комментарий'][0] +
                           " ) " +

                           ' VALUES ' +
                           " ( " +
                           "'" + str(self.Proxy_list.loc[el_id, 'server_ip']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'server_port']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'protocol']) + "'" + ',' +

                           "'" + str(self.Proxy_list.loc[el_id, 'login']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'password']) + "'" + ',' +

                           str(self.Proxy_list.loc[el_id, 'timeout']) + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'sourse']) + "'" + ',' +
                           str(self.Proxy_list.loc[el_id, 'is_available']) + ',' +

                           unsuccessful_calls + ',' +  # Неудачные обращения
                           'now()::date' + ',' +  # Дата обращения

                           "'" + str(self.Proxy_list.loc[el_id, 'country']) + "'" + ',' +

                           "'" + str(self.Proxy_list.loc[el_id, 'comment']) + "'" +
                           " ) "
                           )
                requests_list.append(request)
                new_servers += 1


            elif req_act == 'insert_not_done':  # Если надо вставить новый непроверенный запрос
                # Неудачные обращения

                request = ('INSERT INTO ' + proxy_table.loc['таблица'][0] +
                           " ( " +
                           proxy_table.loc['ip'][0] + ',' +
                           proxy_table.loc['port'][0] + ',' +
                           proxy_table.loc['протокол'][0] + ',' +

                           proxy_table.loc['логин'][0] + ',' +
                           proxy_table.loc['пароль'][0] + ',' +

                           proxy_table.loc['таймаут'][0] + ',' +
                           proxy_table.loc['источник'][0] + ',' +
                           proxy_table.loc['доступен'][0] + ',' +

                           proxy_table.loc['страна'][0] + ',' +

                           proxy_table.loc['комментарий'][0] +
                           " ) " +

                           ' VALUES ' +
                           " ( " +
                           "'" + str(self.Proxy_list.loc[el_id, 'server_ip']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'server_port']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'protocol']) + "'" + ',' +

                           "'" + str(self.Proxy_list.loc[el_id, 'login']) + "'" + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'password']) + "'" + ',' +

                           str(self.Proxy_list.loc[el_id, 'timeout']) + ',' +
                           "'" + str(self.Proxy_list.loc[el_id, 'sourse']) + "'" + ',' +
                           str(self.Proxy_list.loc[el_id, 'is_available']) + ',' +

                           "'" + str(self.Proxy_list.loc[el_id, 'country']) + "'" + ',' +

                           "'" + str(self.Proxy_list.loc[el_id, 'comment']) + "'" +
                           " ) "
                           )
                requests_list.append(request)
                new_servers += 1

        sql_comm.to_base(requests=requests_list)  # Отправили запросы в базу
        sql_comm.connection(act='close')  # Дисконектнулись

        self.communication(message=('Обновлено серверов: ' + str(updated_servers) +
                                    '\nДобавлено серверов: ' + str(new_servers))
                           )

        if clean_exported is True:  # Если надо зачистить Proxy_list от экспортированных данных
            # Оставим лишь те строки, чей индекс не был в export_frame
            self.Proxy_list = self.Proxy_list.loc[~self.Proxy_list.index.isin(index_list)]

        return 'Успешно'

    # ------------------------------------------------------------------------------------------------
    # Работа с моими прокси (My_proxy) ---------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # Делается в один поток.

    # Проверка доступности серверов из My_proxy - готово, отлажено.
    def check_My_proxy(self,
                       use_main_link=False,
                       custom_links_list=False,
                       clear=True):
        '''
        Проверяем доступность собственных прокси.
        :param use_main_link:  Использовать основную ссылку при проверке
        :param custom_links_list - использовать кастомный набор ссылок
        :param clear: - удалить ли недоступные? (ВСЕГДА УДАЛЯТЬ!)
        :return: ничего
        '''

        if self.My_proxy.shape[0] == 0:  # Если прокси нет
            self.__Have_My_proxy = False

        # Если нет своих прокси
        if self.__Have_My_proxy == False:
            return 'Нет прокси'

        self.My_proxy.reset_index(drop=True, inplace=True)  # Скинем индекс, чтобы не было проблем c 'out of bounds'

        # Пошли по набору своих прокси
        drop_index_list = []  # Чтобы при дропе в цикле не было проблем
        for p_id in self.My_proxy.index.tolist():
            # Сделаем мультичек
            # Сделаем проверку
            Availables = self.check_proxy_available(proxy_type=self.My_proxy.loc[p_id, 'protocol'],
                                                    adress_and_port=self.My_proxy.loc[p_id, 'server_ip'] + ':' +
                                                                    self.My_proxy.loc[p_id, 'server_port'],
                                                    p_user=self.My_proxy.loc[p_id, 'user'],
                                                    p_pass=self.My_proxy.loc[p_id, 'pass'],
                                                    custom_links_list=custom_links_list,
                                                    use_main_link=use_main_link,
                                                    max_timeout=self.My_proxy.loc[p_id, 'timeout']  # С учётом таймаута
                                                    )

            if Availables == False and clear is True:  # Если он недоступен и по настройке мы зачищаем
                drop_index_list.append(p_id)

        # Скинем "недоступные прокси"
        self.My_proxy.drop(self.My_proxy.index[drop_index_list], inplace=True)  # Скинем его из набора
        # Обновим индекс
        self.My_proxy.reset_index(drop=True,
                                  inplace=True)  # Скинем индекс, чтобы не было проблем (чтобы индекс шел по порядку)

        # Если в результате проверки удалились все прокси
        if self.My_proxy.shape[0] == 0:
            self.__Have_My_proxy = False  # Запомним, что их больше нет.

            # И сразу попытаемся пополнить
            self.fill_My_proxy_from_self()

        return 'Успешно'

    # Попробовать заполнить "мои прокси" с имеющихся в базе. - готово, отлажено.
    def fill_My_proxy_from_self(self,
                                N=10,
                                use_main_link=False,
                                custom_links_list=False,
                                protocol='https'):
        '''
        Добавляет в "свои прокси" (My_proxy) Данные из Proxy_list
        :param N: - Сколько дёрнуть прокси. Будет взято столько или меньше, если столько же не доступно.
        :param use_main_link: - Использовать основную ссылку при проверке
        :param custom_links_list - использовать кастомный набор ссылок
        :return - успешно ли. Сколько прокси добавлено
        '''
        if N == 0:
            return 'Пополнять не нужно'
        # Возьмём доступные прокси с нужным протоколом
        my_wariants = self.Proxy_list[
            (self.Proxy_list['is_available'] is True) & (self.Proxy_list['protocol'] == protocol)].copy(deep=True)

        if my_wariants.shape[0] == 0:
            return 'Нет доступных вариантов'

        added = 0  # Заведём счётчик добавленных прокси
        # Пошли по набору
        for pr_id in my_wariants.index.tolist():

            # Првоерим - нет ли уже этого сервера в self.My_proxy
            if (self.My_proxy.loc[self.My_proxy['server_ip'] == my_wariants.loc[pr_id, 'server_ip']]).shape[0] != 0:
                continue  # Если такой вариант есть - скипаем

            # Сделаем проверку
            Availables = self.check_proxy_available(proxy_type=my_wariants.loc[pr_id, 'protocol'],
                                                    adress_and_port=(my_wariants.loc[pr_id, 'server_ip'] +
                                                                     ':' + my_wariants.loc[pr_id, 'server_port']
                                                                     ),
                                                    p_user=my_wariants.loc[pr_id, 'login'],
                                                    p_pass=my_wariants.loc[pr_id, 'password'],
                                                    custom_links_list=custom_links_list,
                                                    use_main_link=use_main_link,
                                                    max_timeout=my_wariants.loc[pr_id, 'timeout']  # Дадим таймаут
                                                    )

            if Availables != False:  # Если доступен
                # Добавим в self.My_proxy
                try:
                    new_id = max(self.My_proxy.index.tolist()) + 1  # Сдвинем id на 1 от максимального
                except ValueError:
                    new_id = 0

                self.My_proxy.at[new_id, 'protocol'] = my_wariants.loc[pr_id, 'protocol']
                self.My_proxy.at[new_id, 'server_ip'] = my_wariants.loc[pr_id, 'server_ip']
                self.My_proxy.at[new_id, 'server_port'] = my_wariants.loc[pr_id, 'server_port']
                self.My_proxy.at[new_id, 'user'] = my_wariants.loc[pr_id, 'login']
                self.My_proxy.at[new_id, 'pass'] = my_wariants.loc[pr_id, 'password']
                self.My_proxy.at[new_id, 'timeout'] = my_wariants.loc[pr_id, 'timeout']

                # Запомним, что добавили ещё один прокси
                added += 1

            if added == N:  # Если добавили нужное количество - закончим добавление
                break

        # Если есть хоть один свой прокси,
        if self.My_proxy.shape[0] > 0:
            self.__Have_My_proxy = True  # Запомним, что сервера есть
        elif self.My_proxy.shape[0] == 0:
            self.__Have_My_proxy = False  # Запомним, что серверов нет

        if added < N:
            return 'Варианты кончились, добавлено ' + str(added)

        return 'Успешно пополнено на ' + str(N) + ' штук'

    # ------------------------------------------------------------------------------------------------
    # Дозвон на прокси в один поток ------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    # Чекает по всему Proxy_list на доступность. Ставит is_available=True, если дозвонились, и таймаут - готово, отлажено.
    def check_Proxy_list(self,
                         Use_main_link=False,
                         custom_links_list=False,
                         is_available='all',
                         only_new=True,
                         clean=unacceptable_number_of_tests
                         ):
        '''
        ПРИ КОРРЕКЦИИ АРГУМЕНТОВ ПОПРАВИТЬ check_Proxy_list_multi_threads в месте разваливания на потоки.
        Ставит is_available=True, если дозвонились,
        и is_available=False, если не дозвонились за максимально разрешённый таймаут
        :param thread_proxy_list_size - количество прокси в потоке
        :param Use_main_link - Использовать ли при проверке ссылку на основной ресурс (нет, канеш!)
        :param custom_links_list - использовать кастомный лист ссылок для проверки (передать лист)
        :param is_available - Какие чекаем. "all" - все; t/f - доступные/недоступные Поумолчанию чекаем все
        :param only_new - проверить только те, что ещё не были проверены
        :param clean - Если fals, то чистки не будет.
                       Если число - то удалятся все прокси, которые прозванивали более clean раз.
        :return:
        '''
        if self.Proxy_list.shape[0] == 0:
            return 'Нет доступных прокси'

        # Сообщим о работе
        proxy_list_size = self.Proxy_list.shape[0]
        work_time = (str(round(proxy_list_size * 3 / 60)) + '-' +
                     str(round(proxy_list_size * 10 / 60))
                     )
        self.communication(message=('Првоерка ' + str(proxy_list_size) + ' серверов будет вестись в одном потоке' +
                                    '\nОжидающееся время работы: ' + work_time + ' мин')
                           )

        # Возьмём доступные прокси
        my_list = self.Proxy_list.copy(deep=True)
        if is_available != 'all':  # Если t/f
            my_list = my_list.loc[my_list['is_available'] == is_available]

        if only_new is True:  # Если надо только новые прокси
            my_list = my_list.loc[my_list['comment'] != 'checked']

        id_list = my_list.index.tolist()  # Взяли индекс
        del my_list  # Чтобы не засорять память

        # Пошли по набоу
        for pr_id in id_list:
            Availables = self.check_proxy_available(custom_links_list=custom_links_list,  # Не кастомный сет ссылок
                                                    use_main_link=Use_main_link,
                                                    proxy_type=self.Proxy_list.loc[pr_id, 'protocol'],
                                                    adress_and_port=self.Proxy_list.loc[pr_id, 'server_ip'] + ':' +
                                                                    self.Proxy_list.loc[pr_id, 'server_port'],
                                                    p_user=self.Proxy_list.loc[pr_id, 'login'],
                                                    p_pass=self.Proxy_list.loc[pr_id, 'password']
                                                    )

            if Availables == False:  # Если превышен максимальный таймаут по всем ресурсам прозвона
                self.Proxy_list.at[pr_id, 'is_available'] = False  # Запомним, что сервер недоступен
                # Таймаут поставим стандартный. Чтобы "долго не ждать", если его где-то дёрнут.
                self.Proxy_list.at[pr_id, 'timeout'] = self.defult_timeout
                self.Proxy_list.at[pr_id, 'unsuccessful_calls'] = self.Proxy_list.loc[pr_id, 'unsuccessful_calls'] + 1

                # Запомним, что был неудачный прозвон

            else:  # Если таймаут посчитан
                self.Proxy_list.at[pr_id, 'is_available'] = True  # Запомним доступность
                self.Proxy_list.at[pr_id, 'timeout'] = Availables  # Возьмём таймаут
                self.Proxy_list.at[pr_id, 'unsuccessful_calls'] = 0  # Скинем счётчик неудачных попоыток дозвона

            # Отметим, что прокси-сервер обработан
            self.Proxy_list.at[pr_id, 'checked'] = True

        # Оповестим о результатах проверки:
        are_available = (self.Proxy_list.loc[self.Proxy_list['is_available'] == True]).shape[0]
        are_not_available = (self.Proxy_list.loc[self.Proxy_list['is_available'] == False]).shape[0]
        total = self.Proxy_list.shape[0]
        self.communication(message=('Из ' + str(total) + ' серверов ' +
                                    'доступны: ' + str(are_available) + ', ' +
                                    'недоступны: ' + str(are_not_available))
                           )
        # Если надо чистить прокси с большим количеством недозвонов
        if clean != False and type(clean) == int:
            # Добавитм "мёртвые прокси" в Dead_proxy
            self.Dead_proxy = self.pd.concat(
                [self.Dead_proxy, self.Proxy_list[self.Proxy_list['unsuccessful_calls'] >= clean]],
                axis=1, sort=False)
            self.Dead_proxy.drop_duplicates(subset=['server_ip'], keep='first')  # Зачистим дубли

            self.Proxy_list = self.Proxy_list[
                self.Proxy_list['unsuccessful_calls'] < clean]  # Удалим из исходнойго набора

            if self.Proxy_list.shape[0] == 0:  # Если по итогу прокси нет
                self.__Have_any_proxy = False  # Запоминм, что список пустой

        return 'Успешно'

    # ------------------------------------------------------------------------------------------------
    # Многопоточный дозвон на прокси -----------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------

    def multi_threads_check_Proxy_list(self,
                                       threads_count=ussepted_threads,
                                       Use_main_link=False,
                                       custom_links_list=False,
                                       is_available='all',
                                       only_new=True,
                                       clean=unacceptable_number_of_tests
                                       ):
        '''
        Вызываем проверку прокси (функция ) но в многооточном режиме
        :param threads_count - количество потоков
        :param Use_main_link - Использовать ли при проверке ссылку на основной ресурс (нет, канеш!)
        :param custom_links_list - использовать кастомный лист ссылок для проверки (передать лист)
        :param is_available - Какие чекаем. "all" - все; t/f - доступные/недоступные Поумолчанию чекаем все
        :param only_new - проверить только те, что ещё не были проверены
        :param clean - Если fals, то чистки не будет.
                       Если число - то удалятся все прокси, которые прозванивали более clean раз.
        :param start_id - id, с которого начнётся набор, который уйдёт на проверку.
        :param end_id - последний id, который будет использоваться
        :return:
        '''
        # Если вообще нет прокси серверов
        if self.Proxy_list.shape[0] == 0:
            return 'Нет доступных прокси'

        # Сообщим о работе
        proxy_list_size = self.Proxy_list.shape[0]
        work_time = (str(round(proxy_list_size * 3 / 60) / threads_count) + '-' +
                     str(round(proxy_list_size * 10 / 60) / threads_count * 2)
                     # Возьмём "побольше" верхний предел времени
                     )
        self.communication(message=('Првоерка ' + str(proxy_list_size) + ' серверов будет вестись в ' + str(
            threads_count) + ' потоков' +
                                    '\nОжидающееся время работы: ' + work_time + ' мин')
                           )

        # Разобьём список "проси серверов" в наборы по 20 штук
        import math  # Для округлений

        step = math.ceil(self.Proxy_list.shape[0] / threads_count)  # Шаг (округлили в большую сторону)
        start_id = 0  # Начало среза
        end_id = step  # Конец среза
        max_id = max(self.Proxy_list.index.tolist())  # Максимальный id

        threads_set = {}  # Создадим список с потоками
        for set_part_number in range(0, threads_count):  # Пошли по частям сета
            if start_id > max_id:  # Если стартовый прокси больше длины списка
                break
            elif end_id > max_id:  # Если конечный id больше максимального в списке
                end_id = max_id  # Установим ему максимальное значение
            # Получим набор id
            id_list = (
            self.Proxy_list.loc[(self.Proxy_list.index >= start_id) & (self.Proxy_list.index <= end_id)]).index.tolist()
            # Сделаем поток
            threads_set[set_part_number] = self.threading.Thread(target=self.mtc_Proxy_list_part,
                                                                 args=(id_list, False, False)
                                                                 )
            threads_set[set_part_number].start()

            # Сдвинем
            start_id = end_id + 1
            end_id += step

        # Подождём окончания потоков.
        for set_part_number in range(0, len(threads_set)):
            # "len", т.к. в мелких наборах может быть на 1 поток меньше
            threads_set[set_part_number].join()

        # Оповестим о результатах проверки:
        are_available = (self.Proxy_list.loc[self.Proxy_list['is_available'] == True]).shape[0]
        are_not_available = (self.Proxy_list.loc[self.Proxy_list['is_available'] == False]).shape[0]
        total = self.Proxy_list.shape[0]
        self.communication(message=('Из ' + str(total) + ' серверов ' +
                                    'доступны: ' + str(are_available) + ', ' +
                                    'недоступны: ' + str(are_not_available))
                           )
        # Если надо чистить прокси с большим количеством недозвонов
        if clean != False and type(clean) == int:
            # Добавитм "мёртвые прокси" в Dead_proxy
            self.Dead_proxy = self.pd.concat(
                [self.Dead_proxy, self.Proxy_list[self.Proxy_list['unsuccessful_calls'] >= clean]],
                axis=1, sort=False)
            self.Dead_proxy.drop_duplicates(subset=['server_ip'], keep='first')  # Зачистим дубли

            self.Proxy_list = self.Proxy_list[
                self.Proxy_list['unsuccessful_calls'] < clean]  # Удалим из исходнойго набора

            if self.Proxy_list.shape[0] == 0:  # Если по итогу прокси нет
                self.__Have_any_proxy = False  # Запоминм, что список пустой

        return 'Успешно'

    # Првоеряет доступность прокси из self.Proxy_list по списку id_list
    def mtc_Proxy_list_part(self,
                            id_list,
                            Use_main_link=False,
                            custom_links_list=False
                            ):
        '''
        ПРИ КОРРЕКЦИИ АРГУМЕНТОВ ПОПРАВИТЬ multi_threads_check_Proxy_list в месте разваливания на потоки.
        Ставит is_available=True, если дозвонились,
        и is_available=False, если не дозвонились за максимально разрешённый таймаут
        :param id_list - список с индексами прокси в  self.Proxy_list для проверки
        :param Use_main_link - Использовать ли при проверке ссылку на основной ресурс (нет, канеш!)
        :param custom_links_list - использовать кастомный лист ссылок для проверки (передать лист)
        :return:
        '''

        if id_list == []:
            return 'Ошибка - список пуст'

        # Пошли по набоу
        for pr_id in id_list:
            Availables = self.check_proxy_available(custom_links_list=custom_links_list,  # Не кастомный сет ссылок
                                                    use_main_link=Use_main_link,
                                                    proxy_type=self.Proxy_list.loc[pr_id, 'protocol'],
                                                    adress_and_port=self.Proxy_list.loc[pr_id, 'server_ip'] + ':' +
                                                                    self.Proxy_list.loc[pr_id, 'server_port'],
                                                    p_user=self.Proxy_list.loc[pr_id, 'login'],
                                                    p_pass=self.Proxy_list.loc[pr_id, 'password']
                                                    )

            if Availables == False:  # Если превышен максимальный таймаут по всем ресурсам прозвона
                self.Proxy_list.at[pr_id, 'is_available'] = False  # Запомним, что сервер недоступен
                # Таймаут поставим стандартный. Чтобы "долго не ждать", если его где-то дёрнут.
                self.Proxy_list.at[pr_id, 'timeout'] = self.defult_timeout
                self.Proxy_list.at[pr_id, 'unsuccessful_calls'] = self.Proxy_list.loc[pr_id, 'unsuccessful_calls'] + 1

                # Запомним, что был неудачный прозвон

            else:  # Если таймаут посчитан
                self.Proxy_list.at[pr_id, 'is_available'] = True  # Запомним доступность
                self.Proxy_list.at[pr_id, 'timeout'] = Availables  # Возьмём таймаут
                self.Proxy_list.at[pr_id, 'unsuccessful_calls'] = 0  # Скинем счётчик неудачных попоыток дозвона

            # Отметим, что прокси-сервер обработан
            self.Proxy_list.at[pr_id, 'checked'] = True

        return 'Успешно'

    # Проверяет "доступность" конкретного прокси.
    # вернёт время ожидание или False, если привышен макс.таймаут - готово, отлажено.
    def check_proxy_available(self,
                              proxy_type,
                              adress_and_port,
                              p_user='',
                              p_pass='',
                              custom_links_list=False,
                              use_main_link=False,
                              max_timeout=max_timeout
                              ):
        '''
        Если надо пинговать на "основной ресурс", ставим use_main_link=True. Тогда настройка custom_links_list будет
        заигнорена.
        Это основная и единственная функция првоерки прокси. Т.к. прочие признаны недостаточными или избыточными.
        Есть "конфликт" - кажется, что в use_main_link можно передать ссылку, которая будет использоваться,
        как основная ссылка для прозвона. И это так. При этом она будет приоритенее, чем ссылки заданные в custom_links_list.
        То есть, если параметр use_main_link задан, то используется он.
        :param proxy_type: - тип прокси
        :param adress_and_port: - "адрес:порт"
        :param p_user: - логин
        :param p_pass: - пароль
        :param custom_links_list: - Использовать "кастомный" набор ссылок - f - взять дефолтный.
                                    Иначе это сама ссылка или набор ссылок. Значение "T" игнорируется
        :param custom_links_list: - использовать для дозвона основную ссылку. ВАЖНЕЕ custom_links_list
        :param max_timeout: - максимальный таймаут
        :return - таймаут или False - если не дозвонился.
        '''

        # Решим, куда звонить (определим links_list)
        if use_main_link is True:  # Если звонить на основную ссылку
            links_list = [self.Main_ping_link]

        elif type(use_main_link) == str:  # Если в "основной ссылке" указана строка
            links_list = [use_main_link]  # Будем звонить на неё, как на основную

        # Иначе
        else:
            # Првоерим набор ссылок:
            if custom_links_list != False and not (custom_links_list is True):  # Если набор ссылок кастомный
                # Если t - эт ничего не значит )
                if type(custom_links_list) == str:  # Если это одна строка
                    links_list = [custom_links_list]

                elif type(custom_links_list) == list:  # Если это уже список
                    # Проверим, что все элементы списка - строки
                    for el in custom_links_list:
                        if type(el) != str:
                            return 'Ошибка - неверный тип кастомных ссылок'
                    links_list = custom_links_list  # Если всё ок, берём набор

                else:  # Иначе (если тип неверный) - ретёрн
                    return 'Ошибка - неверный тип кастомных ссылок'

            else:  # Если набор дефолтный
                links_list = self.Links_list  # Если дефотный список

        # Делается так, чтобы при дефолтной настройке выполнять 1 условие вместо 100500.
        # Да - пк быстрый, но это не повод его заебать.

        # Создадим объект для запросов
        req_obj = self.requests.Session()
        req_obj.proxies = {proxy_type: adress_and_port}  # Дадим в настройку объекта прокси

        # Если надо пользователя и пароль
        if p_user != False and p_pass != False and type(p_user) == str and type(p_pass) == str:
            req_obj.auth = (p_user, p_pass)

        user_agent = {'User-agent': self.random.choice(self.user_agent_list)}  # Возьмём случайный из списка

        Success = False  # Детектор того, что мы дозвонились.
        # Прозвоним
        for el_url in links_list:  # Пошли по списку ссылок
            # Задача - быстрее таймаута дозвониться хоть на одну ссылку.
            start_time = self.time.time()

            try:  # Звоним с максимальным таймаутом
                response = req_obj.get(el_url, headers=user_agent, timeout=max_timeout)

                # Если выполнение было удачным
                if response.status_code == 200:
                    Success = round(self.time.time() - start_time) + self.defult_timeout
                    # Прибавим defult_timeout для учёта "качек пинга".

                    if Success > self.max_timeout:  # Если значение привысило макс таймаут
                        Success = self.max_timeout  # Установим макс таймаут

                    # Так как мы дозвонились, дальше можно не пинговать
                    break  # Закончим цикл

            except BaseException:  # Если были ЛЮБЫЕ ошибки, включая таймаут
                pass  # Чилим.

        # Если прозванивалась только одна ссылка и прозвон был неудачным, попробуем ещё раз.
        if len(links_list) == 1 and Success == False:
            try:  # Звоним с максимальным таймаутом
                start_time = self.time.time()
                response = req_obj.get(links_list[0], headers=user_agent, timeout=max_timeout)

                # Если выполнение было удачным
                if response.status_code == 200:
                    Success = round(self.time.time() - start_time) + self.defult_timeout
                    # Прибавим defult_timeout для учёта "качек пинга".

                    if Success > self.max_timeout:  # Если значение привысило макс таймаут
                        Success = self.max_timeout  # Установим макс таймаут

            except BaseException:  # Если были ЛЮБЫЕ ошибки
                pass  # Чилим.

        return Success  # Вернём результат.


# ------------------------------------------------------------------------------------------------------------
# Запуск модуля ----------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------


def start_working(mode='SQL'):
    if mode == 'SQL':
        # Проверка прокси-серверов, которые обновлялись не сегодня
        Z = AddProxy(repetitions=True,
                     need_My_proxy=10,
                     ussepted_threads=50,

                     get_from='SQL',
                     get_condition=' call_date<>now()::date',
                     sql_batch_size=200
                     )  # Оставим парситься на ночь

    elif mode == 'get_new':
        # Парсинг проксей
        Z = AddProxy(repetitions=True,
                     need_My_proxy=10,
                     ussepted_threads=50)

